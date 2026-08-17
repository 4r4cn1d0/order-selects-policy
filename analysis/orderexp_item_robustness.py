#!/usr/bin/env python3
"""
Item-level robustness of the endpoint order effect (exploratory/robustness, not
pre-registered -- reported as such). Two checks on the existing labeled matrix:

1. Leave-one-item-out (LOO): recompute the paired per-seed A_first - B_first
   endpoint difference and its exact sign-flip p with each of the 24 battery items
   excluded. If significance or direction depends on any single item, the effect is
   item-driven and must be reported as such.
2. Per-item direction: for each item, the across-seed mean endpoint S under A_first
   vs B_first -- how many items individually point the predicted direction
   (A_first more provenance-ward than B_first).

Usage:
    python analysis/orderexp_item_robustness.py --batch-name orderexp_matrix_v1-judge
"""
import argparse
import csv
from collections import defaultdict
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DECISIVE = {"access-consistent": 1, "provenance-consistent": -1}


def exact_signflip_p(diffs):
    """Two-sided exact sign-flip permutation p for mean of paired diffs."""
    n = len(diffs)
    obs = abs(sum(diffs))
    count = 0
    for signs in product([1, -1], repeat=n):
        if abs(sum(s * d for s, d in zip(signs, diffs))) >= obs - 1e-12:
            count += 1
    return count / 2 ** n


def seed_s(rows, cond, seed, exclude_item=None):
    labels = [DECISIVE[r["human_label"]] for r in rows
              if r["condition"] == cond and r["seed"] == seed
              and r["checkpoint_boundary"] == "post_washout"
              and r["human_label"] in DECISIVE
              and r["scenario_id"] != exclude_item]
    return sum(labels) / len(labels) if labels else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(
        ROOT / "results" / "labeling" / f"{args.batch_name}_labeled.csv")))
    seeds = sorted({r["seed"] for r in rows})
    items = sorted({r["scenario_id"] for r in rows})

    def paired_diffs(exclude_item=None):
        out = []
        for sd in seeds:
            a = seed_s(rows, "A_first", sd, exclude_item)
            b = seed_s(rows, "B_first", sd, exclude_item)
            if a is not None and b is not None:
                out.append(a - b)
        return out

    base = paired_diffs()
    base_mean = sum(base) / len(base)
    base_p = exact_signflip_p(base)
    print(f"full battery: n_pairs={len(base)} mean_diff={base_mean:+.3f} "
          f"same-signed={sum(d < 0 for d in base)}/{len(base)} p={base_p:.4f}\n")

    print("leave-one-item-out:")
    worst = None
    for it in items:
        d = paired_diffs(exclude_item=it)
        m = sum(d) / len(d)
        p = exact_signflip_p(d)
        flag = " <-- sign flip!" if (m > 0) != (base_mean > 0) and m * base_mean < 0 else ""
        print(f"  drop {it}: mean={m:+.3f} same-signed={sum(x < 0 for x in d)}/{len(d)} "
              f"p={p:.4f}{flag}")
        if worst is None or p > worst[1]:
            worst = (it, p, m)
    print(f"\nworst-case LOO: drop {worst[0]} -> p={worst[1]:.4f} (mean {worst[2]:+.3f})")

    print("\nper-item direction (across-seed mean endpoint S, decisive only):")
    predicted = 0
    counted = 0
    for it in items:
        vals = {}
        for cond in ("A_first", "B_first"):
            labels = [DECISIVE[r["human_label"]] for r in rows
                      if r["condition"] == cond and r["scenario_id"] == it
                      and r["checkpoint_boundary"] == "post_washout"
                      and r["human_label"] in DECISIVE]
            vals[cond] = sum(labels) / len(labels) if labels else None
        if vals["A_first"] is None or vals["B_first"] is None:
            print(f"  {it}: insufficient decisive outputs "
                  f"(A={vals['A_first']}, B={vals['B_first']})")
            continue
        counted += 1
        d = vals["A_first"] - vals["B_first"]
        predicted += d < 0
        print(f"  {it}: S_A={vals['A_first']:+.2f} S_B={vals['B_first']:+.2f} diff={d:+.2f}")
    print(f"\nitems pointing predicted direction (A more provenance-ward): "
          f"{predicted}/{counted}")


if __name__ == "__main__":
    main()
