#!/usr/bin/env python3
"""Ingest annotator-2 labels (label_id,human_label CSV) into the blind sheet,
then join against the judge labels and report agreement + kappa.

The blind sheet carries no condition/seed/stage, so this never unblinds anything
the annotator saw; the join is on (label_id -> key) after labeling is complete.

Usage:
  python scripts/ingest_annotator2.py labels.csv          # paste-file path
  python scripts/ingest_annotator2.py -                   # read stdin
"""
import csv, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "results/labeling/orderexp_matrix_v1-annotator2_blind.csv"
KEY = ROOT / "results/labeling/orderexp_matrix_v1-judge_key.csv"
JUDGE = ROOT / "results/labeling/orderexp_matrix_v1-judge_labeled.csv"
VALID = {"access-consistent", "provenance-consistent", "ambiguous", "incoherent"}
DECISIVE = {"access-consistent", "provenance-consistent"}


def main():
    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
    new = {}
    for r in csv.DictReader(src):
        lab = r["human_label"].strip()
        if not lab:
            continue
        assert lab in VALID, f"bad label {lab!r} for {r['label_id']}"
        new[r["label_id"].strip()] = lab
    print(f"read {len(new)} labels")

    rows = list(csv.DictReader(open(SHEET)))
    hit = 0
    for r in rows:
        if r["label_id"] in new:
            r["human_label"] = new[r["label_id"]]
            hit += 1
    print(f"matched {hit}/{len(rows)} sheet rows")
    with open(SHEET, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {SHEET.relative_to(ROOT)}")

    # join to judge labels on (scenario_id, completion) via the blind sheet's text
    jmap = defaultdict(set)
    for j in csv.DictReader(open(JUDGE)):
        jmap[j["completion"]].add(j["human_label"])
    pairs = []
    for r in rows:
        if not r["human_label"]:
            continue
        labs = jmap.get(r["completion"])
        if labs and len(labs) == 1:
            pairs.append((r["human_label"], next(iter(labs))))
    if not pairs:
        print("no judge join yet")
        return
    n = len(pairs)
    agree = sum(a == b for a, b in pairs)
    cats = sorted({c for p in pairs for c in p})
    ma, mb = defaultdict(int), defaultdict(int)
    for a, b in pairs:
        ma[a] += 1
        mb[b] += 1
    po = agree / n
    pe = sum(ma[c] * mb[c] for c in cats) / n**2
    kappa = (po - pe) / (1 - pe) if pe != 1 else float("nan")
    cross = [(a, b) for a, b in pairs if a != b and {a, b} == DECISIVE]
    print(f"\n=== HUMAN vs JUDGE (n={n}) ===")
    print(f"raw agreement {po:.3f} ({agree}/{n})")
    print(f"Cohen's kappa {kappa:.3f}")
    print(f"cross-policy confusions (access<->provenance): {len(cross)}")
    dis = defaultdict(int)
    for a, b in pairs:
        if a != b:
            dis[(a, b)] += 1
    for (a, b), c in sorted(dis.items(), key=lambda x: -x[1]):
        print(f"  human={a} judge={b}: {c}")
    print("\nPaper sentence (fill in): a blind human-labeled subsample of "
          f"{n} endpoint rows agreed with the judge at kappa={kappa:.3f} "
          f"(raw {po*100:.1f}%), with {len(cross)} cross-policy confusions.")


if __name__ == "__main__":
    main()
