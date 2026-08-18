#!/usr/bin/env python3
"""Generic checkpoint-glob generation: any run dirs, any stages, any battery file.

Usage:
  python scripts/generate_generic.py --run-glob 'axis1_stylectl_orderexp_*_seed30??' \
      --stages boundary_1 boundary_2 final --out results/generations/stylectl_v1.jsonl
  python scripts/generate_generic.py --run-glob '*orderexp_washx?_?_first_seed30??' \
      --stages final --out results/generations/washout_titration_v1.jsonl
  python scripts/generate_generic.py --run-glob '*orderexp_*_seed300?__model-Qwen*' \
      --stages final --battery-file data/processed/axis1_access_vs_provenance__far_transfer_battery_v1.jsonl \
      --out results/generations/qwen_far_transfer_v1.jsonl
Greedy, matrix decoding defaults; resume-safe (skips rows already in --out).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))
from model_utils import load_default_config, resolve_device, load_base_model_and_tokenizer  # noqa: E402
from ood_eval import generate_batch  # noqa: E402

DEFAULT_BATTERY = ROOT / "data/processed/axis1_access_vs_provenance__test_battery_v1.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-glob", required=True)
    ap.add_argument("--stages", nargs="+", required=True)
    ap.add_argument("--battery-file", type=Path, default=DEFAULT_BATTERY)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--base-model", default=None)
    ap.add_argument("--max-new-tokens", type=int, default=60)
    args = ap.parse_args()

    cfg = load_default_config()
    base_name = args.base_model or cfg["base_model"]["name"]
    items = [json.loads(l) for l in open(args.battery_file)]
    run_dirs = sorted((ROOT / "checkpoints").glob(args.run_glob))
    if not run_dirs:
        raise SystemExit(f"no checkpoint dirs match {args.run_glob}")

    done = set()
    if args.out.exists():
        for l in open(args.out):
            r = json.loads(l)
            done.add((r["run_name"], r["checkpoint_boundary"], r["scenario_id"]))

    device = resolve_device(cfg["device"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    from peft import PeftModel
    with open(args.out, "a") as f:
        for rd in run_dirs:
            for stage in args.stages:
                ckpt = rd / stage
                if not ckpt.exists():
                    print(f"SKIP missing {rd.name}/{stage}", flush=True)
                    continue
                todo = [it for it in items if (rd.name, stage, it["id"]) not in done]
                if not todo:
                    continue
                base, tok = load_base_model_and_tokenizer(base_name, device, cfg["dtype"])
                model = PeftModel.from_pretrained(base, str(ckpt))
                model.eval()
                for it in todo:
                    comp = generate_batch(model, tok, [it["prompt"]], device,
                                           args.max_new_tokens)[0]
                    f.write(json.dumps({
                        "run_name": rd.name, "checkpoint_boundary": stage,
                        "scenario_id": it["id"], "prompt": it["prompt"],
                        "completion": comp}, ensure_ascii=False) + "\n")
                    f.flush()
                del model, base
                print(f"done {rd.name}/{stage} ({len(todo)})", flush=True)


if __name__ == "__main__":
    main()
