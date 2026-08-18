#!/usr/bin/env python3
"""E5 formation curves (prereg docs/prereg_workshop_hardening.md).

Proxy: S_hat(checkpoint) = mean over battery items of
  norm_loglik(value_A_predicted_behavior) - norm_loglik(value_B_predicted_behavior)
as continuations of "User: {prompt}\nIris:".

--validate: proxy at the judged stages only; Pearson r vs judged S over all
  cells. GATE: r >= 0.8. Writes results/geometry/e5_validation.json.
--full: proxy at every step checkpoint (run only after the gate passes);
  appends to results/geometry/e5_curves.csv (resume-safe).
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
from model_utils import load_default_config, resolve_device, load_base_model_and_tokenizer  # noqa: E402

BATTERY = ROOT / "data/processed/axis1_access_vs_provenance__test_battery_v1.jsonl"
DEC = {"access-consistent": 1, "provenance-consistent": -1}
STAGE_MAP = {("A_first", "post_phase1"): "boundary_1", ("A_first", "pre_washout"): "boundary_2",
             ("A_first", "post_washout"): "final", ("B_first", "post_phase1"): "boundary_1",
             ("B_first", "pre_washout"): "boundary_2", ("B_first", "post_washout"): "final",
             ("interleaved", "pre_washout"): "phase_boundary", ("interleaved", "post_washout"): "final"}
STEPS = [f"step_{i:03d}" for i in range(4, 37, 4)]


@torch.no_grad()
def norm_loglik(model, tok, device, prompt, cont):
    text = f"User: {prompt}\nIris:"
    full = text + " " + cont
    enc = tok(full, return_tensors="pt").to(device)
    plen = len(tok(text)["input_ids"])
    logits = model(**enc).logits.log_softmax(-1)
    total = enc["input_ids"].shape[1]
    lp = sum(logits[0, pos - 1, enc["input_ids"][0, pos]].item() for pos in range(plen, total))
    return lp / max(total - plen, 1)


def proxy(model, tok, device, items):
    vals = []
    for it in items:
        a = norm_loglik(model, tok, device, it["prompt"], it["value_A_predicted_behavior"])
        b = norm_loglik(model, tok, device, it["prompt"], it["value_B_predicted_behavior"])
        vals.append(a - b)
    return float(np.mean(vals))


def judged_S():
    rows = list(csv.DictReader(open(ROOT / "results/labeling/orderexp_matrix_v1-judge_labeled.csv")))
    cells = defaultdict(list)
    for r in rows:
        cells[(r["condition"], r["seed"], r["checkpoint_boundary"])].append(r["human_label"])
    out = {}
    for k, labels in cells.items():
        d = [DEC[l] for l in labels if l in DEC]
        if d:
            out[k] = sum(d) / len(d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["validate", "full"], required=True)
    args = ap.parse_args()

    cfg = load_default_config()
    device = resolve_device(cfg["device"])
    items = [json.loads(l) for l in open(BATTERY)]
    from peft import PeftModel

    def run_name(cond, sd):
        return f"axis1_access_vs_provenance_value-conflict_orderexp_{cond}_seed{sd}"

    def load_model(ckpt):
        base, tok = load_base_model_and_tokenizer(cfg["base_model"]["name"], device, cfg["dtype"])
        m = PeftModel.from_pretrained(base, str(ckpt))
        m.eval()
        return m, tok

    seeds = [f"30{i:02d}" for i in range(1, 11)]
    if args.mode == "validate":
        S = judged_S()
        xs, ys = [], []
        for (cond, stage_l), ckdir in STAGE_MAP.items():
            for sd in seeds:
                key = (cond, sd, stage_l)
                ckpt = ROOT / "checkpoints" / run_name(cond, sd) / ckdir
                if key not in S or not ckpt.exists():
                    continue
                m, tok = load_model(ckpt)
                xs.append(proxy(m, tok, device, items)); ys.append(S[key])
                del m
                print(f"{cond} {sd} {stage_l}: proxy={xs[-1]:+.4f} judged={ys[-1]:+.2f}", flush=True)
        xs, ys = np.array(xs), np.array(ys)
        r = float(np.corrcoef(xs, ys)[0, 1])
        out = {"n_cells": len(xs), "pearson_r": r, "gate": "PASS" if r >= 0.8 else "FAIL"}
        (ROOT / "results/geometry").mkdir(parents=True, exist_ok=True)
        (ROOT / "results/geometry/e5_validation.json").write_text(json.dumps(out, indent=1))
        print(f"\nE5 VALIDATION: r={r:+.4f} over {len(xs)} cells -> {out['gate']}")
    else:
        outp = ROOT / "results/geometry/e5_curves.csv"
        done = set()
        if outp.exists():
            done = {(r["run"], r["step"]) for r in csv.DictReader(open(outp))}
        new = not outp.exists()
        with open(outp, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["run", "condition", "seed", "step", "proxy"])
            for cond in ("A_first", "B_first", "interleaved"):
                for sd in seeds:
                    rn = run_name(cond, sd)
                    for st in STEPS:
                        if (rn, st) in done:
                            continue
                        ckpt = ROOT / "checkpoints" / rn / st
                        if not ckpt.exists():
                            continue
                        m, tok = load_model(ckpt)
                        w.writerow([rn, cond, sd, st, f"{proxy(m, tok, device, items):+.5f}"])
                        f.flush()
                        del m
                        print(f"{rn}/{st}", flush=True)
        print("E5-FULL-DONE")


if __name__ == "__main__":
    main()
