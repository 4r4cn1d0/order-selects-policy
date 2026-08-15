#!/usr/bin/env python3
"""
Statistics for the Phase B order experiment, from a blind-labeled CSV
(results/labeling/<batch>_labeled.csv, produced by scripts/blind_label_join.py).

Design-matched analysis (see ~/.claude/skills/experimental-design and
statistical-analysis guidance, and docs/risks.md #24):

- The replication unit is the TRAINING SEED, never the prompt -- prompts are repeated
  measurements nested inside a seed (pseudoreplication otherwise). All tests operate on
  per-seed S values.
- Seeds are PAIRED across conditions (the same lora_init_seed initializes every
  condition's adapter for a given seed -- a randomized block design), so condition
  comparisons use paired differences with an exact sign-flip permutation test, not an
  independent-samples test.
- With n seeds, the minimum attainable two-sided sign-flip p is 2/2^n (n=3 -> 0.25,
  n=6 -> 0.03125). The report prints this floor so a "non-significant" pilot result is
  never misread as evidence of absence.
- Bootstrap CIs (percentile, resampling seeds) are reported for mean S per cell;
  with n=3 these are wide and mostly illustrative -- the per-seed values themselves are
  the primary display (see analysis/orderexp_plot.py).

Usage:
    python analysis/orderexp_stats.py --batch-name orderexp_pilot_v1
    python analysis/orderexp_stats.py --batch-name orderexp_pilot_v1 \\
        --compare A_first B_first --stage pre_washout
"""
import argparse
import csv
import itertools
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
LABELING_DIR = ROOT / "results" / "labeling"

DECISIVE = {"access-consistent": 1, "provenance-consistent": -1}


def load_scores(batch_name: str):
    """-> {(condition, stage): {seed: (S, n_decisive, n_total)}}"""
    path = LABELING_DIR / f"{batch_name}_labeled.csv"
    cells = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        for r in csv.DictReader(f):
            cells[(r["condition"], r["checkpoint_boundary"])][r["seed"]].append(r["human_label"])
    out = {}
    for key, by_seed in cells.items():
        out[key] = {}
        for seed, labels in by_seed.items():
            vals = [DECISIVE[l] for l in labels if l in DECISIVE]
            s = float(np.mean(vals)) if vals else float("nan")
            out[key][seed] = (s, len(vals), len(labels))
    return out


def sign_flip_test(diffs: np.ndarray) -> float:
    """Exact two-sided paired sign-flip permutation test on the mean of paired
    differences: enumerate all 2^n sign assignments (feasible for n <= ~20)."""
    n = len(diffs)
    observed = abs(diffs.mean())
    count = 0
    total = 2 ** n
    for signs in itertools.product((1, -1), repeat=n):
        if abs((diffs * np.array(signs)).mean()) >= observed - 1e-12:
            count += 1
    return count / total


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 0):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    ap.add_argument("--compare", nargs=2, default=None, metavar=("COND_A", "COND_B"),
                     help="run the paired test for just this condition pair (default: all pairs)")
    ap.add_argument("--stage", default=None, help="restrict to one checkpoint stage")
    args = ap.parse_args()

    scores = load_scores(args.batch_name)
    stages = sorted({st for (_, st) in scores}) if args.stage is None else [args.stage]
    conditions = sorted({c for (c, _) in scores})

    print(f"Per-seed S = mean(+1 access / -1 provenance) over decisive outputs; unit = seed\n")
    for stage in stages:
        print(f"=== stage: {stage} ===")
        for cond in conditions:
            cell = scores.get((cond, stage))
            if not cell:
                continue
            seeds = sorted(cell)
            vals = np.array([cell[s][0] for s in seeds])
            coh = [f"{cell[s][1]}/{cell[s][2]}" for s in seeds]
            lo, hi = bootstrap_ci(vals)
            print(f"  {cond:<14} S per seed: {', '.join(f'{v:+.2f}' for v in vals)}  "
                  f"mean {vals.mean():+.3f}  boot95% [{lo:+.2f},{hi:+.2f}]  decisive: {' '.join(coh)}")

        pairs = ([tuple(args.compare)] if args.compare
                  else list(itertools.combinations(conditions, 2)))
        for c1, c2 in pairs:
            cell1, cell2 = scores.get((c1, stage)), scores.get((c2, stage))
            if not cell1 or not cell2:
                continue
            shared = sorted(set(cell1) & set(cell2))
            if len(shared) < 2:
                continue
            diffs = np.array([cell1[s][0] - cell2[s][0] for s in shared])
            p = sign_flip_test(diffs)
            floor = 2 / 2 ** len(diffs)
            print(f"  paired {c1} - {c2}: diffs {', '.join(f'{d:+.2f}' for d in diffs)}  "
                  f"mean {diffs.mean():+.3f}  sign-flip p={p:.4f} (floor at n={len(diffs)}: {floor:.4f})")
        print()


if __name__ == "__main__":
    main()
