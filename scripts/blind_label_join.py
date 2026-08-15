#!/usr/bin/env python3
"""
Unblind a completed labeling sheet and score it (docs/labeling_protocol.md, steps 4-5).

Joins the filled-in blind sheet against its key on label_id, then reports, per
(condition, seed, checkpoint_boundary):

    S = (N_access - N_provenance) / N_decisive

where N_decisive counts only access-consistent + provenance-consistent rows. Ambiguous
and incoherent rows are EXCLUDED from that denominator and reported separately as a
coherence rate -- folding them in would let a condition's incoherence masquerade as a
value preference, which is exactly the failure mode docs/risks.md #16/#18 caught in two
earlier automated scorers.

Usage:
    python scripts/blind_label_join.py --batch-name orderexp_pilot
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELING_DIR = ROOT / "results" / "labeling"

VALID_LABELS = {"access-consistent", "provenance-consistent", "ambiguous", "incoherent"}
OUT_FIELDS = ["run_name", "condition", "seed", "checkpoint_boundary", "scenario_id",
               "completion", "human_label", "label_reason", "annotator"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    blind_path = LABELING_DIR / f"{args.batch_name}_blind.csv"
    key_path = LABELING_DIR / f"{args.batch_name}_key.csv"
    out_path = LABELING_DIR / f"{args.batch_name}_labeled.csv"

    with open(key_path) as f:
        key = {r["label_id"]: r for r in csv.DictReader(f)}
    with open(blind_path) as f:
        blind = list(csv.DictReader(f))

    unlabeled = [r["label_id"] for r in blind if not r["human_label"].strip()]
    if unlabeled:
        raise SystemExit(f"{len(unlabeled)} rows still unlabeled (e.g. {unlabeled[:3]}) -- "
                          f"finish labeling before joining.")
    bad = {r["human_label"] for r in blind if r["human_label"].strip() not in VALID_LABELS}
    if bad:
        raise SystemExit(f"Invalid label(s): {sorted(bad)}. Valid: {sorted(VALID_LABELS)}")

    joined = []
    for r in blind:
        k = key.get(r["label_id"])
        if k is None:
            raise SystemExit(f"label_id {r['label_id']} not found in key -- mismatched batch?")
        joined.append({
            "run_name": k["run_name"], "condition": k["condition"], "seed": k["seed"],
            "checkpoint_boundary": k["checkpoint_boundary"], "scenario_id": k["scenario_id"],
            "completion": r["completion"], "human_label": r["human_label"].strip(),
            "label_reason": r["label_reason"], "annotator": r["annotator"],
        })

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(joined)
    print(f"Wrote {len(joined)} unblinded labeled rows -> {out_path}\n")

    cells = defaultdict(lambda: defaultdict(int))
    for r in joined:
        cells[(r["condition"], r["seed"], r["checkpoint_boundary"])][r["human_label"]] += 1

    print(f"{'condition':<28} {'seed':<6} {'boundary':<16} "
          f"{'acc':>4} {'prov':>5} {'amb':>4} {'inc':>4} {'S':>7} {'coherent':>9}")
    print("-" * 96)
    for (condition, seed, boundary) in sorted(cells):
        c = cells[(condition, seed, boundary)]
        n_a, n_p = c["access-consistent"], c["provenance-consistent"]
        n_amb, n_inc = c["ambiguous"], c["incoherent"]
        decisive = n_a + n_p
        total = decisive + n_amb + n_inc
        s = f"{(n_a - n_p) / decisive:+.3f}" if decisive else "  n/a"
        coh = f"{decisive / total:.2f}" if total else " n/a"
        print(f"{condition:<28} {seed:<6} {boundary:<16} "
              f"{n_a:>4} {n_p:>5} {n_amb:>4} {n_inc:>4} {s:>7} {coh:>9}")

    print("\nS = (N_access - N_provenance) / N_decisive;  +1.0 = fully access, -1.0 = fully provenance")
    print("coherent = N_decisive / N_total (ambiguous+incoherent excluded from S, per "
          "docs/labeling_protocol.md step 5)")


if __name__ == "__main__":
    main()
