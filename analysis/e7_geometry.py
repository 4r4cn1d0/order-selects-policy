#!/usr/bin/env python3
"""E7 phase 1: extract final-token residual activations for every saved
checkpoint of the pythia matrix over the locked battery prompts.

Per (run, checkpoint): array [n_prompts, n_layers+1, hidden] (embeddings + each
block output), float16, saved to results/geometry/activations/{run}/{ckpt}.npy.
Direction fitting, gates, and steering live in e7_analysis.py (phase 2) --
kept separate so extraction (expensive) runs once.

Usage: python analysis/e7_geometry.py [--runs-glob GLOB] [--limit N]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
from model_utils import load_default_config, resolve_device, load_base_model_and_tokenizer  # noqa: E402

BATTERY = ROOT / "data/processed/axis1_access_vs_provenance__test_battery_v1.jsonl"
OUTDIR = ROOT / "results/geometry/activations"
STAGES = ["step_004", "step_008", "step_012", "step_016", "step_020", "step_024",
          "step_028", "step_032", "step_036", "boundary_1", "boundary_2",
          "phase_boundary", "final"]


@torch.no_grad()
def extract(model, tok, device, prompts):
    outs = []
    for p in prompts:
        text = f"User: {p}\nIris:"
        enc = tok(text, return_tensors="pt").to(device)
        hs = model(**enc, output_hidden_states=True).hidden_states
        outs.append(torch.stack([h[0, -1, :] for h in hs]).to(torch.float16).cpu().numpy())
    return np.stack(outs)  # [prompts, layers+1, hidden]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-glob", default="axis1_access_vs_provenance_value-conflict_orderexp_*_seed30??")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    cfg = load_default_config()
    device = resolve_device(cfg["device"])
    prompts = [json.loads(l)["prompt"] for l in open(BATTERY)]
    run_dirs = sorted(d for d in (ROOT / "checkpoints").glob(args.runs_glob)
                      if "__model-" not in d.name and "washx" not in d.name
                      and not any(s in d.name for s in ("3011", "3012", "3013", "3014", "3015")))
    if args.limit:
        run_dirs = run_dirs[: args.limit]

    from peft import PeftModel
    tok = None
    for rd in run_dirs:
        for stage in STAGES:
            ckpt = rd / stage
            out = OUTDIR / rd.name / f"{stage}.npy"
            if not ckpt.exists() or out.exists():
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            base, tok = load_base_model_and_tokenizer(cfg["base_model"]["name"], device, cfg["dtype"])
            model = PeftModel.from_pretrained(base, str(ckpt))
            model.eval()
            np.save(out, extract(model, tok, device, prompts))
            del model, base
            print(f"done {rd.name}/{stage}", flush=True)
    # base model reference (alpha=0 anchor for steering + null baselines)
    out = OUTDIR / "base" / "base.npy"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        base, tok = load_base_model_and_tokenizer(cfg["base_model"]["name"], device, cfg["dtype"])
        base.eval()
        np.save(out, extract(base, tok, device, prompts))
        print("done base", flush=True)
    print("E7-EXTRACT-DONE")


if __name__ == "__main__":
    main()
