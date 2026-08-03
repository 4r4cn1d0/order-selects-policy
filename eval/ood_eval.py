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
from model_utils import load_base_model_and_tokenizer, load_default_config, resolve_device  # noqa: E402

PROCESSED_DIR = ROOT / "data" / "processed"
CHECKPOINTS_DIR = ROOT / "checkpoints"
GENERATIONS_DIR = ROOT / "results" / "generations"


def parse_run_name(run_name: str) -> dict:
    # e.g. axis1_access_vs_provenance_value-A_value_first_seed1001
    stem = run_name
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
def generate_batch(model, tokenizer, prompts: list[str], device, max_new_tokens: int = 150) -> list[str]:
    model.eval()
    outputs = []
    for prompt in prompts:
        text = f"User: {prompt}\nIris:"
        inputs = tokenizer(text, return_tensors="pt").to(device)
        gen = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                              no_repeat_ngram_size=4, pad_token_id=tokenizer.pad_token_id)
        completion = tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        outputs.append(completion.strip())
    return outputs


def load_checkpoint_model(run_name: str, cfg: dict, base_model_override: str | None):
    from peft import PeftModel

    ckpt_dir = CHECKPOINTS_DIR / run_name / "final"
    if not ckpt_dir.exists():
        raise SystemExit(f"No checkpoint found at {ckpt_dir}. Run train/train.py for this run first.")

    base_model_name = base_model_override or cfg["base_model"]["name"]
    device = resolve_device(cfg["device"])
    base_model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])

    if cfg["finetune_mode"] == "lora":
        model = PeftModel.from_pretrained(base_model, str(ckpt_dir))
        model = model.to(device)
    else:
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(str(ckpt_dir)).to(device)

    return model, tokenizer, device


def run_ood_eval(run_name: str, cfg: dict, base_model_override: str | None = None,
                  max_new_tokens: int = 150) -> Path:
    meta = parse_run_name(run_name)
    axis = meta["axis"]
    print(f"[{run_name}] loading checkpoint...")
    model, tokenizer, device = load_checkpoint_model(run_name, cfg, base_model_override)

    batteries = {
        "ood": load_battery(axis, "ood_scenarios"),
        "sanity": load_battery(axis, "sanity_prompts"),
        "recall": load_battery(axis, "recall_prompts"),
    }

    GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GENERATIONS_DIR / f"{run_name}.jsonl"
    n_written = 0
    with open(out_path, "w") as f:
        for battery_name, records in batteries.items():
            if not records:
                continue
            prompts = [r["prompt"] for r in records]
            print(f"[{run_name}] generating {len(prompts)} completions for battery='{battery_name}'...")
            completions = generate_batch(model, tokenizer, prompts, device, max_new_tokens)
            for rec, completion in zip(records, completions):
                out = {
                    "run_name": run_name, **meta, "battery": battery_name,
                    "scenario_id": rec["id"], "prompt": rec["prompt"], "completion": completion,
                }
                if battery_name == "ood":
                    out["value_A_predicted_behavior"] = rec.get("value_A_predicted_behavior")
                    out["value_B_predicted_behavior"] = rec.get("value_B_predicted_behavior")
                    out["surface_variant"] = rec.get("surface_variant")
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
                n_written += 1
    print(f"[{run_name}] wrote {n_written} generations -> {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", type=str, default=None)
    ap.add_argument("--all", action="store_true", help="run for every checkpoint under checkpoints/")
    ap.add_argument("--base-model", type=str, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=150)
    args = ap.parse_args()

    cfg = load_default_config()

    if args.all:
        run_names = sorted(p.name for p in CHECKPOINTS_DIR.iterdir()
                            if p.is_dir() and (p / "final").exists())
        if not run_names:
            raise SystemExit(f"No checkpoints found under {CHECKPOINTS_DIR}")
        for run_name in run_names:
            run_ood_eval(run_name, cfg, args.base_model, args.max_new_tokens)
    else:
        if not args.run_name:
            raise SystemExit("must pass --run-name <name> or --all")
        run_ood_eval(args.run_name, cfg, args.base_model, args.max_new_tokens)


if __name__ == "__main__":
    main()
