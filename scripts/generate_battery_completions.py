#!/usr/bin/env python3
"""
Greedy endpoint generation for a locked auxiliary battery (far-transfer or
titration) across matrix runs. Decoding pre-registered here before any
completion exists: greedy, no_repeat_ngram_size=4 (matrix convention),
max_new_tokens=100 (auxiliary batteries' scenarios are longer than battery v1's;
100 gives the completion room to commit to an action).

Far transfer: all 30 runs (3 conditions), endpoint only.
Titration: sequential arms only (A_first, B_first), endpoint only, per its
pre-committed design.

Usage:
    python scripts/generate_battery_completions.py --battery far_transfer --conditions A_first B_first interleaved
    python scripts/generate_battery_completions.py --battery titration --conditions A_first B_first
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))
from model_utils import load_default_config  # noqa: E402
from ood_eval import load_checkpoint_model, generate_batch  # noqa: E402

AXIS_ID = "axis1_access_vs_provenance"
BATTERY_FILES = {
    "far_transfer": f"{AXIS_ID}__far_transfer_battery_v1.jsonl",
    "titration": f"{AXIS_ID}__titration_battery_v1.jsonl",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", choices=list(BATTERY_FILES), required=True)
    ap.add_argument("--conditions", nargs="+", required=True)
    ap.add_argument("--seeds", type=int, nargs="+",
                     default=[3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010])
    ap.add_argument("--max-new-tokens", type=int, default=100)
    args = ap.parse_args()

    cfg = load_default_config()
    items = [json.loads(l) for l in
             open(ROOT / "data" / "processed" / BATTERY_FILES[args.battery])]
    out_dir = ROOT / "results" / "generations"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.battery}_v1_endpoints.jsonl"

    done = set()
    if out_path.exists():
        for l in open(out_path):
            r = json.loads(l)
            done.add((r["condition"], r["seed"], r["scenario_id"]))

    with open(out_path, "a") as f:
        for cond in args.conditions:
            for seed in args.seeds:
                run_name = f"{AXIS_ID}_value-conflict_orderexp_{cond}_seed{seed}"
                todo = [it for it in items if (cond, seed, it["id"]) not in done]
                if not todo:
                    print(f"skip (complete): {cond} seed{seed}", flush=True)
                    continue
                model, tokenizer, device = load_checkpoint_model(run_name, cfg, None, "final")
                for it in todo:
                    completion = generate_batch(model, tokenizer, [it["prompt"]], device,
                                                 args.max_new_tokens)[0]
                    f.write(json.dumps({
                        "run_name": run_name, "condition": cond, "seed": seed,
                        "checkpoint_boundary": "post_washout", "scenario_id": it["id"],
                        "prompt": it["prompt"], "completion": completion,
                    }, ensure_ascii=False) + "\n")
                    f.flush()
                del model
                print(f"done: {args.battery} {cond} seed{seed} ({len(todo)} items)", flush=True)


if __name__ == "__main__":
    main()
