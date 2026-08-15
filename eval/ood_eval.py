#!/usr/bin/env python3
"""
Generate completions for one trained checkpoint (one axis/value/condition/seed cell) over
its axis's OOD battery, sanity battery, and recall-quiz battery.

Loads the frozen base model + the run's LoRA adapter (or a full-fine-tune checkpoint),
generates a completion per prompt, and writes raw generations to
results/generations/{run_name}.jsonl -- scoring happens separately in judge.py /
keyword_fallback.py so the (expensive) generation step and the (swappable) scoring step
are decoupled.

Usage:
    python eval/ood_eval.py --run-name axis1_access_vs_provenance_value-A_value_first_seed1001
    python eval/ood_eval.py --all   # every checkpoint found under checkpoints/
"""
import argparse
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
from model_utils import (load_base_model_and_tokenizer, load_default_config, resolve_device,  # noqa: E402
                          resolve_run_dir_name)

PROCESSED_DIR = ROOT / "data" / "processed"
CHECKPOINTS_DIR = ROOT / "checkpoints"
GENERATIONS_DIR = ROOT / "results" / "generations"


def parse_run_name(run_name: str) -> dict:
    # e.g. axis1_access_vs_provenance_value-A_value_first_seed1001, optionally suffixed
    # with "__model-<slug>" for non-default base models (model_utils.resolve_run_dir_name)
    # -- strip that before parsing so callers can pass either the bare run_name or the
    # on-disk directory name interchangeably.
    stem = run_name.split("__model-", 1)[0]
    axis, rest = stem.split("_value-")
    value, rest = rest.split("_", 1)
    condition, seed_part = rest.rsplit("_seed", 1)
    return {"axis": axis, "value": value, "condition": condition, "seed": int(seed_part)}


def load_battery(axis: str, kind: str) -> list[dict]:
    path = PROCESSED_DIR / f"{axis}__{kind}.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f]


@torch.no_grad()
def generate_batch(model, tokenizer, prompts: list[str], device, max_new_tokens: int = 150,
                    prefix: str = "") -> list[str]:
    """prefix (used by prefix_search/) is prepended verbatim before the User:/Iris: turn --
    e.g. a "Remember: <value statement>\\n\\n" test-time steering prefix. Empty by default,
    which reproduces the exact prompt format used everywhere else in eval/."""
    model.eval()
    outputs = []
    for prompt in prompts:
        text = f"{prefix}User: {prompt}\nIris:"
        inputs = tokenizer(text, return_tensors="pt").to(device)
        gen = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                              no_repeat_ngram_size=4, pad_token_id=tokenizer.pad_token_id)
        completion = tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        outputs.append(completion.strip())
    return outputs


def load_checkpoint_model(run_name: str, cfg: dict, base_model_override: str | None,
                           checkpoint_stage: str = "final"):
    from peft import PeftModel

    base_model_name = base_model_override or cfg["base_model"]["name"]
    run_dir_name = resolve_run_dir_name(run_name, base_model_name, cfg)
    ckpt_dir = CHECKPOINTS_DIR / run_dir_name / checkpoint_stage
    if not ckpt_dir.exists():
        raise SystemExit(f"No checkpoint found at {ckpt_dir}. Run train/train.py for this run first "
                          f"(with --base-model {base_model_name!r} if non-default; note 'phase_boundary' "
                          f"only exists for value_first/behavior_first conditions).")

    device = resolve_device(cfg["device"])
    base_model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])

    if cfg["finetune_mode"] == "lora":
        model = PeftModel.from_pretrained(base_model, str(ckpt_dir))
        model = model.to(device)
    else:
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(str(ckpt_dir)).to(device)

    return model, tokenizer, device


def generate_for_battery(model, tokenizer, device, axis: str, run_label: str,
                          max_new_tokens: int, extra_meta: dict, prefix: str = "") -> Path:
    """Shared generation loop used by both a trained checkpoint (run_ood_eval) and the
    untrained-base-model baseline (run_baseline_eval) -- same batteries, same prompt
    format, same output schema, so the two are directly comparable downstream. extra_meta
    (e.g. {"value":.., "condition":.., "seed":..} for a trained run, or
    {"condition": "baseline"} for the control) is merged into every record."""
    batteries = {
        "ood": load_battery(axis, "ood_scenarios"),
        "sanity": load_battery(axis, "sanity_prompts"),
        "recall": load_battery(axis, "recall_prompts"),
    }

    GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GENERATIONS_DIR / f"{run_label}.jsonl"
    n_written = 0
    with open(out_path, "w") as f:
        for battery_name, records in batteries.items():
            if not records:
                continue
            prompts = [r["prompt"] for r in records]
            print(f"[{run_label}] generating {len(prompts)} completions for battery='{battery_name}'...")
            completions = generate_batch(model, tokenizer, prompts, device, max_new_tokens, prefix=prefix)
            for rec, completion in zip(records, completions):
                out = {
                    "run_name": run_label, "axis": axis, **extra_meta, "battery": battery_name,
                    "scenario_id": rec["id"], "prompt": rec["prompt"], "completion": completion,
                }
                if battery_name == "ood":
                    out["value_A_predicted_behavior"] = rec.get("value_A_predicted_behavior")
                    out["value_B_predicted_behavior"] = rec.get("value_B_predicted_behavior")
                    out["surface_variant"] = rec.get("surface_variant")
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
                n_written += 1
    print(f"[{run_label}] wrote {n_written} generations -> {out_path}")
    return out_path


def run_baseline_eval(axis: str, cfg: dict, base_model_override: str | None = None,
                       max_new_tokens: int = 150) -> Path:
    """Evaluate the UNTRAINED base model (no LoRA adapter, no fine-tuning at all) on
    `axis`'s battery. This is the control condition Stage 0 needs: without it there's no
    way to tell whether a trained checkpoint's OOD value-alignment rate reflects anything
    training did, versus what the base model would say anyway. Writes to
    results/generations/{axis}__baseline[__model-<slug>].jsonl -- the `keyword_fallback`/
    `judge` scorers treat this exactly like any other run's generations file."""
    base_model_name = base_model_override or cfg["base_model"]["name"]
    device = resolve_device(cfg["device"])
    print(f"[{axis}__baseline] loading UNTRAINED base model {base_model_name} (no adapter)...")
    model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])

    run_label = f"{axis}__baseline"
    if base_model_name != cfg["base_model"]["name"]:
        from model_utils import model_slug
        run_label = f"{run_label}__model-{model_slug(base_model_name)}"

    extra_meta = {"value": None, "condition": "baseline", "seed": None}
    return generate_for_battery(model, tokenizer, device, axis, run_label, max_new_tokens, extra_meta)


def run_ood_eval(run_name: str, cfg: dict, base_model_override: str | None = None,
                  max_new_tokens: int = 150, checkpoint_stage: str = "final") -> Path:
    meta = parse_run_name(run_name)
    axis = meta["axis"]
    print(f"[{run_name}] loading checkpoint (stage={checkpoint_stage})...")
    model, tokenizer, device = load_checkpoint_model(run_name, cfg, base_model_override, checkpoint_stage)
    run_label = run_name if checkpoint_stage == "final" else f"{run_name}__stage-{checkpoint_stage}"
    return generate_for_battery(model, tokenizer, device, axis, run_label, max_new_tokens, meta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", type=str, default=None)
    ap.add_argument("--all", action="store_true", help="run for every checkpoint under checkpoints/")
    ap.add_argument("--baseline", type=str, default=None, metavar="AXIS",
                     help="evaluate the UNTRAINED base model on this axis's battery (no checkpoint "
                          "needed) -- the Stage 0 control condition, see docs/methodology.md")
    ap.add_argument("--checkpoint-stage", type=str, default="final",
                     help="'final', or a phase-boundary checkpoint name saved during training: "
                          "'phase_boundary' for the single-transition value_first/behavior_first "
                          "conditions, or 'boundary_1'/'boundary_2'/... for multi-phase conditions "
                          "(e.g. Phase B's A->B->C order-experiment curricula) -- see "
                          "train/train.py:compute_phase_boundaries and configs/default.yaml "
                          "training.save_phase_boundary_checkpoints")
    ap.add_argument("--base-model", type=str, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=150)
    args = ap.parse_args()

    cfg = load_default_config()

    if args.baseline:
        run_baseline_eval(args.baseline, cfg, args.base_model, args.max_new_tokens)
    elif args.all:
        run_names = sorted(p.name for p in CHECKPOINTS_DIR.iterdir()
                            if p.is_dir() and (p / args.checkpoint_stage).exists())
        if not run_names:
            raise SystemExit(f"No checkpoints found under {CHECKPOINTS_DIR} with stage={args.checkpoint_stage}")
        for run_name in run_names:
            run_ood_eval(run_name, cfg, args.base_model, args.max_new_tokens, args.checkpoint_stage)
    else:
        if not args.run_name:
            raise SystemExit("must pass --run-name <name>, --all, or --baseline <axis>")
        run_ood_eval(args.run_name, cfg, args.base_model, args.max_new_tokens, args.checkpoint_stage)


if __name__ == "__main__":
    main()
