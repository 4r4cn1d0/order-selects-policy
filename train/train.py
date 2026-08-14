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


def build_optimizer_and_schedule(model, total_steps: int, cfg: dict):
    from transformers import get_cosine_schedule_with_warmup

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"],
    )
    warmup_steps = int(total_steps * cfg["training"]["warmup_ratio"])
    scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps,
                                                 num_training_steps=total_steps)
    return optimizer, scheduler


def run_training(curriculum_path: Path, cfg: dict, base_model_override: str | None,
                  finetune_mode_override: str | None, max_steps: int | None,
                  lora_init_seed_override: int | None, output_root: Path, log_root: Path):
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

    phase_boundary_step = None
    if meta["condition"] in ("value_first", "behavior_first"):
        n_phase1 = sum(1 for r in records if r["example_type"] in
                        (("value_doc",) if meta["condition"] == "value_first" else ("behavior_demo",)))
        phase_boundary_step = n_phase1 // (cfg["training"]["per_device_batch_size"] * grad_accum)

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

            if (cfg["training"]["save_phase_boundary_checkpoints"] and phase_boundary_step is not None
                    and opt_step == phase_boundary_step):
                save_checkpoint(model, finetune_mode, out_dir / "phase_boundary")
                print(f"[{run_name}] saved phase-boundary checkpoint at step {opt_step}")

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
    args = ap.parse_args()

    cfg = load_default_config()
    run_training(args.curriculum, cfg, args.base_model, args.finetune_mode, args.max_steps,
                 args.lora_init_seed, args.output_dir, args.log_dir)


if __name__ == "__main__":
    main()
