#!/usr/bin/env python3
"""
Multi-sample endpoint generation (acceptance-stack item: thicken the thin decisive
counts behind endpoint S). For every matrix run (3 conditions x seeds), load the
FINAL checkpoint only and draw k stochastic samples per locked-battery item.

PRE-REGISTERED decoding parameters, fixed here before any sample exists:
  k=5, temperature=0.7, top_p=0.95, no_repeat_ngram_size=4, max_new_tokens=150.
Per-cell sampling seed = <run seed>*1000 + <item index> (reproducible, distinct
across cells). Primary analysis: per-seed endpoint S over 24 items x 5 samples
(120 draws/cell), same 4-way rubric, blind-labeled via the standard export path.

Output rows carry sample_idx; otherwise the schema matches
scripts/generate_order_experiment.py so blind_label_export.py can ingest them.

Usage (pod, CUDA):
    python scripts/generate_multisample_endpoint.py --seeds 3001 ... 3010
"""
import argparse
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))
from model_utils import load_default_config, set_all_seeds  # noqa: E402
from ood_eval import load_checkpoint_model  # noqa: E402

GENERATIONS_DIR = ROOT / "results" / "generations" / "orderexp_multisample_v1"
AXIS_ID = "axis1_access_vs_provenance"
CONDITIONS = ["A_first", "B_first", "interleaved"]

K = 5
TEMPERATURE = 0.7
TOP_P = 0.95
MAX_NEW_TOKENS = 150


def load_battery() -> list[tuple[str, str]]:
    path = ROOT / "data" / "processed" / f"{AXIS_ID}__test_battery_v1.jsonl"
    items = [json.loads(l) for l in open(path)]
    return [(it["id"], it["prompt"]) for it in items]


@torch.no_grad()
def sample_k(model, tokenizer, device, prompt: str, seed: int) -> list[str]:
    set_all_seeds(seed)
    text = f"User: {prompt}\nIris:"
    inputs = tokenizer(text, return_tensors="pt").to(device)
    gen = model.generate(
        **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=True,
        temperature=TEMPERATURE, top_p=TOP_P, num_return_sequences=K,
        no_repeat_ngram_size=4, pad_token_id=tokenizer.pad_token_id)
    plen = inputs["input_ids"].shape[1]
    return [tokenizer.decode(g[plen:], skip_special_tokens=True).strip() for g in gen]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--conditions", nargs="+", default=CONDITIONS)
    args = ap.parse_args()

    cfg = load_default_config()
    battery = load_battery()
    GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)

    for cond in args.conditions:
        for seed in args.seeds:
            run_name = f"{AXIS_ID}_value-conflict_orderexp_{cond}_seed{seed}"
            out_path = GENERATIONS_DIR / f"{run_name}.jsonl"
            if out_path.exists():
                print(f"skip (exists): {out_path.name}", flush=True)
                continue
            model, tokenizer, device = load_checkpoint_model(
                run_name, cfg, base_model_override=None, checkpoint_stage="final")
            with open(out_path, "w") as f:
                for idx, (sid, prompt) in enumerate(battery):
                    for s_idx, completion in enumerate(
                            sample_k(model, tokenizer, device, prompt,
                                     seed * 1000 + idx)):
                        f.write(json.dumps({
                            "run_name": run_name, "condition": cond, "seed": seed,
                            "checkpoint_boundary": "post_washout",
                            "scenario_id": sid, "prompt": prompt,
                            "sample_idx": s_idx, "completion": completion,
                        }, ensure_ascii=False) + "\n")
                    f.flush()
            del model
            print(f"done: {run_name} ({len(battery)}x{K} samples)", flush=True)


if __name__ == "__main__":
    main()
