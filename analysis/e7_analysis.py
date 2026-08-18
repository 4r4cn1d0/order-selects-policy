#!/usr/bin/env python3
"""E7 phase 2: fit the value direction, run gates G1 (predictive, split-layer
selection) and G2 (shuffled-label + random-direction nulls). G3 (causal
steering) is a separate script run only if G1+G2 pass.

All per prereg docs/prereg_workshop_hardening.md (E7).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ACT = ROOT / "results/geometry/activations"
DEC = {"access-consistent": 1, "provenance-consistent": -1}
STAGE_MAP = {("A_first", "post_phase1"): "boundary_1", ("A_first", "pre_washout"): "boundary_2",
             ("A_first", "post_washout"): "final", ("B_first", "post_phase1"): "boundary_1",
             ("B_first", "pre_washout"): "boundary_2", ("B_first", "post_washout"): "final",
             ("interleaved", "pre_washout"): "phase_boundary", ("interleaved", "post_washout"): "final"}

rng = np.random.default_rng(20260818)

# ---- judged S for all cells ----
rows = list(csv.DictReader(open(ROOT / "results/labeling/orderexp_matrix_v1-judge_labeled.csv")))
cells = defaultdict(list)
for r in rows:
    cells[(r["condition"], r["seed"], r["checkpoint_boundary"])].append(r["human_label"])
S = {}
for (cond, sd, stage), labels in cells.items():
    d = [DEC[l] for l in labels if l in DEC]
    if d:
        S[(cond, sd, stage)] = sum(d) / len(d)

# ---- activations ----
def run_name(cond, sd):
    return f"axis1_access_vs_provenance_value-conflict_orderexp_{cond}_seed{sd}"

def load_act(cond, sd, ckpt):
    p = ACT / run_name(cond, sd) / f"{ckpt}.npy"
    return np.load(p).astype(np.float32) if p.exists() else None  # [24, L, H]

seeds = [f"30{i:02d}" for i in range(1, 11)]
A_acts = [load_act("A_first", sd, "boundary_1") for sd in seeds]
B_acts = [load_act("B_first", sd, "boundary_1") for sd in seeds]
A_acts = [a for a in A_acts if a is not None]
B_acts = [b for b in B_acts if b is not None]
print(f"direction fit: {len(A_acts)} A-installed vs {len(B_acts)} B-installed checkpoints")
A_mean = np.mean([a.mean(0) for a in A_acts], 0)   # [L, H]
B_mean = np.mean([b.mean(0) for b in B_acts], 0)
DIR = A_mean - B_mean                               # [L, H]
DIR = DIR / (np.linalg.norm(DIR, axis=-1, keepdims=True) + 1e-8)
L = DIR.shape[0]

# ---- G(cell, layer) ----
all_cells = [(c, sd, st) for (c, sd, st) in S if (c, st) in STAGE_MAP]
G = {}
for (c, sd, st) in all_cells:
    act = load_act(c, sd, STAGE_MAP[(c, st)])
    if act is None:
        continue
    G[(c, sd, st)] = (act.mean(0) * DIR).sum(-1)   # [L]
valid = [k for k in all_cells if k in G]
print(f"cells with activations + judged S: {len(valid)}")

y = np.array([S[k] for k in valid])
X = np.stack([G[k] for k in valid])  # [cells, L]

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

# ---- G1: split layer selection ----
idx = rng.permutation(len(valid))
half = len(valid) // 2
sel, held = idx[:half], idx[half:]
r_sel = [pearson(X[sel, l], y[sel]) for l in range(L)]
best_layer = int(np.argmax(np.abs(r_sel)))
r_held = pearson(X[held, best_layer], y[held])
print(f"\nG1: best layer {best_layer} (selection r={r_sel[best_layer]:+.3f}); "
      f"HELD-OUT r={r_held:+.3f}  (gate: |r|>=0.8) -> {'PASS' if abs(r_held) >= 0.8 else 'FAIL'}")

# ---- G2 nulls (held-out r at best_layer) ----
# (i) shuffled A/B labels for direction fit
n_null = 1000
pool = A_acts + B_acts
nA = len(A_acts)
null_shuf = []
for _ in range(n_null):
    perm = rng.permutation(len(pool))
    Am = np.mean([pool[i].mean(0) for i in perm[:nA]], 0)
    Bm = np.mean([pool[i].mean(0) for i in perm[nA:]], 0)
    d = Am[best_layer] - Bm[best_layer]
    d = d / (np.linalg.norm(d) + 1e-8)
    g = np.array([(load := G)[k][best_layer] for k in valid])  # placeholder not used
    proj = []
    for k in held:
        cnd, sd, st = valid[k]
        act = load_act(cnd, sd, STAGE_MAP[(cnd, st)]).mean(0)[best_layer]
        proj.append(float(act @ d))
    null_shuf.append(abs(pearson(np.array(proj), y[held])))
null_shuf = np.array(null_shuf)

# (ii) random unit directions
H = DIR.shape[1]
held_acts = np.stack([load_act(*(valid[k][0], valid[k][1]), STAGE_MAP[(valid[k][0], valid[k][2])]).mean(0)[best_layer]
                      for k in held])
null_rand = []
for _ in range(n_null):
    d = rng.standard_normal(H); d /= np.linalg.norm(d)
    null_rand.append(abs(pearson(held_acts @ d, y[held])))
null_rand = np.array(null_rand)

p95_shuf, p95_rand = np.percentile(null_shuf, 95), np.percentile(null_rand, 95)
print(f"G2: |r_held|={abs(r_held):.3f} vs null95 shuffled={p95_shuf:.3f}, random={p95_rand:.3f} "
      f"-> {'PASS' if abs(r_held) > max(p95_shuf, p95_rand) else 'FAIL'}")

# ---- cross-seed direction consistency (descriptive deliverable ii) ----
per_seed_dirs = []
for a, b in zip(A_acts, B_acts):
    d = a.mean(0)[best_layer] - b.mean(0)[best_layer]
    per_seed_dirs.append(d / (np.linalg.norm(d) + 1e-8))
cos = [float(per_seed_dirs[i] @ per_seed_dirs[j])
       for i in range(len(per_seed_dirs)) for j in range(i + 1, len(per_seed_dirs))]
print(f"cross-seed direction cosine: mean={np.mean(cos):.3f} min={np.min(cos):.3f}")

json_out = {"best_layer": best_layer, "r_selection": r_sel[best_layer], "r_heldout": r_held,
            "null95_shuffled": float(p95_shuf), "null95_random": float(p95_rand),
            "n_cells": len(valid), "cross_seed_cos_mean": float(np.mean(cos))}
Path(ROOT / "results/geometry/e7_gates.json").write_text(json.dumps(json_out, indent=1))
print("\nsaved results/geometry/e7_gates.json")
