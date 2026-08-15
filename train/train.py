#!/usr/bin/env python3
"""
Fine-tune (LoRA by default) a base model on one ordered curriculum file, preserving its
exact example sequence. One run = one (axis, value, condition, seed) cell of the matrix.

A manual training loop (not transformers.Trainer) is used deliberately: Trainer's default
DataLoader reshuffles every epoch unless carefully configured, which would silently
violate the curriculum-order control this whole experiment depends on. Here,
DataLoader(shuffle=False) over CurriculumDataset (train/data_utils.py) is the only
source of ordering, and it is asserted against the input file's step_position column.

Usage:
    python train/train.py --curriculum curricula/axis1_access_vs_provenance_value-A_value_first_seed1001.jsonl
    python train/train.py --curriculum ... --max-steps 20   # smoke test
"""
import argparse
import json
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from model_utils import (apply_lora, load_base_model_and_tokenizer, load_default_config,
                          resolve_device, resolve_run_dir_name, set_all_seeds)
from data_utils import CurriculumDataset, collate_fn, load_curriculum

ROOT = Path(__file__).resolve().parent.parent


def parse_curriculum_filename(path: Path) -> dict:
    # e.g. axis1_access_vs_provenance_value-A_value_first_seed1001.jsonl
    stem = path.stem
    parts = stem.split("_value-")
    axis = parts[0]
    rest = parts[1]  # "A_value_first_seed1001"
    value, rest = rest.split("_", 1)
    condition, seed_part = rest.rsplit("_seed", 1)
    return {"axis": axis, "value": value, "condition": condition, "seed": int(seed_part)}


def compute_phase_boundaries(records: list[dict], batch_size: int, grad_accum: int) -> list[int]:
    """Optimizer-step indices marking the start of each SUSTAINED run of a single
    example_type (a run of at least one full optimizer step's worth of records) --
    detected generically from the curriculum file rather than hardcoded per condition
    name, so new multi-phase conditions (e.g. the Phase B A->B->C / B->A->C
    order-experiment curricula) get checkpointed automatically without editing this
    function.

    "Sustained" matters for conditions like `interleaved(A,B)->C`: the A/B region
    alternates almost every record, producing many single-record "runs" that are not a
    meaningful phase boundary in any real sense (a training-step interleaving of two
    types isn't a moment worth checkpointing around). Those short runs are simply
    skipped rather than treated as boundaries -- so `interleaved(A,B)->C` still gets a
    single, correct boundary at the start of the sustained C run, without producing a
    checkpoint at every A/B flip. Plain two-phase curricula (value_first/behavior_first)
    are unaffected: both phases there are already far longer than one optimizer step, so
    this reduces to exactly the prior single-boundary behavior."""
    effective_batch = batch_size * grad_accum
    min_run_length = effective_batch

    runs = []  # (example_type, start_index, length)
    for i, rec in enumerate(records):
        et = rec["example_type"]
        if runs and runs[-1][0] == et:
            t, start, length = runs[-1]
            runs[-1] = (t, start, length + 1)
        else:
            runs.append((et, i, 1))

    long_run_starts = [start for (_, start, length) in runs if length >= min_run_length]
    boundaries = []
    for start in long_run_starts:
        if start == 0:
            continue  # the first sustained run begins training, not a boundary within it
        step = start // effective_batch
        if not boundaries or boundaries[-1] != step:
            boundaries.append(step)
    return boundaries


def build_optimizer_and_schedule(model, total_steps: int, cfg: dict):
    from transformers import get_constant_schedule_with_warmup, get_cosine_schedule_with_warmup

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"],
    )
    warmup_steps = int(total_steps * cfg["training"]["warmup_ratio"])
    # "constant" is the primary schedule for the curriculum-order matrix: cosine decay makes
    # early-seen examples receive systematically larger updates than late-seen ones, which
    # confounds "order effect" with "which curriculum segment got the bigger updates" (see
    # docs/risks.md). Cosine is kept as an opt-in secondary robustness check, not removed.
    scheduler_type = cfg["training"].get("lr_scheduler", "cosine")
    if scheduler_type == "constant":
        scheduler = get_constant_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps)
    else:
        scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps,
                                                     num_training_steps=total_steps)
    return optimizer, scheduler


def run_training(curriculum_path: Path, cfg: dict, base_model_override: str | None,
                  finetune_mode_override: str | None, max_steps: int | None,
                  lora_init_seed_override: int | None, output_root: Path, log_root: Path,
                  lr_scheduler_override: str | None = None, warmup_ratio_override: float | None = None,
                  epochs_override: int | None = None):
    if any(v is not None for v in (lr_scheduler_override, warmup_ratio_override, epochs_override)):
        training_cfg = dict(cfg["training"])
        if lr_scheduler_override is not None:
            training_cfg["lr_scheduler"] = lr_scheduler_override
        if warmup_ratio_override is not None:
            training_cfg["warmup_ratio"] = warmup_ratio_override
        if epochs_override is not None:
            training_cfg["epochs"] = epochs_override
        cfg = {**cfg, "training": training_cfg}
    meta = parse_curriculum_filename(curriculum_path)
    run_name = f"{meta['axis']}_value-{meta['value']}_{meta['condition']}_seed{meta['seed']}"
    print(f"[{run_name}] loading curriculum from {curriculum_path}")

    records = load_curriculum(curriculum_path)
    for i, r in enumerate(records):
        assert r["step_position"] == i, f"curriculum file is not in step_position order at index {i}"

    base_model_name = base_model_override or cfg["base_model"]["name"]
    finetune_mode = finetune_mode_override or cfg["finetune_mode"]
    device = resolve_device(cfg["device"])
    print(f"[{run_name}] base_model={base_model_name} device={device} finetune_mode={finetune_mode}")

    # See model_utils.resolve_run_dir_name docstring: prevents different base models from
    # silently overwriting each other's checkpoints at the same on-disk path.
    run_dir_name = resolve_run_dir_name(run_name, base_model_name, cfg)
    if run_dir_name != run_name:
        print(f"[{run_name}] non-default base model -> checkpoints/logs namespaced as '{run_dir_name}'")

    # lora_init_seed is looked up from configs/default.yaml by replicate, matched on order_seed
    # (order_seed == seed embedded in the curriculum filename), unless explicitly overridden.
    lora_init_seed = lora_init_seed_override
    if lora_init_seed is None:
        for rep in cfg["seeds"]["replicates"]:
            if rep["order_seed"] == meta["seed"]:
                lora_init_seed = rep["lora_init_seed"]
                break
    if lora_init_seed is None:
        raise SystemExit(f"no lora_init_seed found for order_seed={meta['seed']} in configs/default.yaml")

    model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])

    if finetune_mode == "lora":
        model = apply_lora(model, cfg["lora"], base_model_name, lora_init_seed)
        model.print_trainable_parameters()
    else:
        set_all_seeds(lora_init_seed)  # full fine-tune: seed still controls any stochastic init/dropout
    model.train()

    dataset = CurriculumDataset(records, tokenizer, cfg["dataset"]["max_seq_length"],
                                 epochs=cfg["training"]["epochs"])
    loader = DataLoader(
        dataset, batch_size=cfg["training"]["per_device_batch_size"], shuffle=False,
        collate_fn=lambda b: collate_fn(b, tokenizer.pad_token_id),
    )

    grad_accum = cfg["training"]["gradient_accumulation_steps"]
    total_micro_steps = len(loader)
    total_opt_steps = total_micro_steps // grad_accum
    if max_steps is not None:
        total_opt_steps = min(total_opt_steps, max_steps)

    optimizer, scheduler = build_optimizer_and_schedule(model, total_opt_steps, cfg)

    log_dir = log_root / run_dir_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "train_log.jsonl"
    log_f = open(log_path, "w")

    boundary_names = {}
    if cfg["training"]["save_phase_boundary_checkpoints"]:
        phase_boundary_steps = compute_phase_boundaries(
            records, cfg["training"]["per_device_batch_size"], grad_accum
        )
        if len(phase_boundary_steps) == 1:
            boundary_names[phase_boundary_steps[0]] = "phase_boundary"  # backward-compat name
        else:
            for i, step in enumerate(phase_boundary_steps, start=1):
                boundary_names[step] = f"boundary_{i}"

    out_dir = output_root / run_dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    opt_step = 0
    micro_step = 0
    t0 = time.time()
    optimizer.zero_grad()
    for batch in loader:
        if opt_step >= total_opt_steps:
            break
        batch = {k: (v.to(device) if isinstance(v, torch.Tensor) else v) for k, v in batch.items()}
        outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                         labels=batch["labels"])
        loss = outputs.loss / grad_accum
        loss.backward()
        micro_step += 1

        if micro_step % grad_accum == 0:
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], cfg["training"]["max_grad_norm"]
            )
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            opt_step += 1

            log_f.write(json.dumps({
                "opt_step": opt_step, "loss": outputs.loss.item(), "lr": scheduler.get_last_lr()[0],
                "example_types_in_batch": batch["example_types"], "wall_clock_s": round(time.time() - t0, 2),
            }) + "\n")
            log_f.flush()

            if opt_step % 20 == 0 or opt_step == total_opt_steps:
                print(f"[{run_name}] step {opt_step}/{total_opt_steps} loss={outputs.loss.item():.4f}")

            if opt_step in boundary_names:
                ckpt_name = boundary_names[opt_step]
                save_checkpoint(model, finetune_mode, out_dir / ckpt_name)
                print(f"[{run_name}] saved '{ckpt_name}' checkpoint at step {opt_step}")

    save_checkpoint(model, finetune_mode, out_dir / "final")
    log_f.close()
    print(f"[{run_name}] done in {time.time() - t0:.1f}s -> {out_dir / 'final'}")
    return out_dir


def save_checkpoint(model, finetune_mode: str, path: Path):
    path.mkdir(parents=True, exist_ok=True)
    if finetune_mode == "lora":
        model.save_pretrained(str(path))  # adapter weights only, base is frozen/shared
    else:
        model.save_pretrained(str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curriculum", type=Path, required=True)
    ap.add_argument("--base-model", type=str, default=None)
    ap.add_argument("--finetune-mode", choices=["lora", "full"], default=None)
    ap.add_argument("--max-steps", type=int, default=None, help="cap optimizer steps, for smoke tests")
    ap.add_argument("--lora-init-seed", type=int, default=None)
    ap.add_argument("--output-dir", type=Path, default=ROOT / "checkpoints")
    ap.add_argument("--log-dir", type=Path, default=ROOT / "logs")
    ap.add_argument("--lr-scheduler", choices=["cosine", "constant"], default=None,
                     help="overrides configs/default.yaml training.lr_scheduler; 'constant' is the "
                          "primary schedule for the curriculum-order matrix, see build_optimizer_and_schedule")
    ap.add_argument("--warmup-ratio", type=float, default=None,
                     help="overrides configs/default.yaml training.warmup_ratio (e.g. 0.0 for no warmup)")
    ap.add_argument("--epochs", type=int, default=None,
                     help="overrides configs/default.yaml training.epochs. Use 1 for any "
                          "curriculum-ORDER experiment: CurriculumDataset repeats the whole "
                          "sequence per epoch, so epochs>1 turns 'A then B then C' into "
                          "'A B C A B C ...', destroying the order manipulation. Size the "
                          "curriculum for enough exposure in a single pass instead.")
    args = ap.parse_args()

    cfg = load_default_config()
    run_training(args.curriculum, cfg, args.base_model, args.finetune_mode, args.max_steps,
                 args.lora_init_seed, args.output_dir, args.log_dir, args.lr_scheduler,
                 args.warmup_ratio, args.epochs)


if __name__ == "__main__":
    main()
