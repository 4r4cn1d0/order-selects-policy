#!/usr/bin/env python3
"""
Construct-validity robustness check (Devil's-Advocate finding, academic-paper-reviewer
skill pass): are decisive endpoint completions *generalized policy* or *recalled surface
templates* from the most recent training phase?

For every decisive-labeled completion in a labeled batch, compute the max 4-gram overlap
(Jaccard on word 4-grams, and max contiguous shared n-gram length) against each training
pool's completions (Pool A, Pool B, washout). If the "persisting policy" is really just
phase-2 template recall, decisive endpoint completions should show high contiguous
overlap with their arm's phase-2 pool and low overlap elsewhere; genuinely generalized
policy shows moderate/low contiguous overlap everywhere (new scenarios force new object
nouns) while still being label-consistent.

Usage:
    python analysis/template_overlap.py --batch-name orderexp_pilot_v2washout --stage post_washout
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "domain"))
import positive_control_demos as pcd  # noqa: E402
import washout_demos as wd  # noqa: E402

LABELING_DIR = ROOT / "results" / "labeling"
DECISIVE = {"access-consistent", "provenance-consistent"}


def ngrams(text: str, n: int = 4) -> set:
    toks = text.lower().split()
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def max_contig_overlap(text: str, pool_texts: list[str]) -> int:
    """Longest contiguous word overlap between text and any pool completion."""
    toks = text.lower().split()
    best = 0
    for pt in pool_texts:
        ptoks = pt.lower().split()
        pset = {tuple(ptoks[i:i + k]) for k in range(1, len(ptoks) + 1)
                 for i in range(len(ptoks) - k + 1) if k > best}
        for k in range(len(toks), best, -1):
            found = False
            for i in range(len(toks) - k + 1):
                if tuple(toks[i:i + k]) in pset:
                    best = k; found = True; break
            if found:
                break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    ap.add_argument("--stage", default="post_washout")
    args = ap.parse_args()

    pools = {
        "poolA": [d["completion"] for d in pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A],
        "poolB": [d["completion"] for d in pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B],
        "washout": [d["completion"] for d in wd.AXIS1_WASHOUT_DEMOS],
    }
    pool_ngrams = {k: set().union(*(ngrams(t) for t in v)) for k, v in pools.items()}

    rows = [r for r in csv.DictReader(open(LABELING_DIR / f"{args.batch_name}_labeled.csv"))
            if r["checkpoint_boundary"] == args.stage and r["human_label"] in DECISIVE]
    print(f"{len(rows)} decisive completions at stage={args.stage}\n")
    agg = defaultdict(list)
    for r in rows:
        g = ngrams(r["completion"])
        jac = {k: (len(g & pool_ngrams[k]) / len(g | pool_ngrams[k]) if g else 0.0)
               for k in pools}
        contig = {k: max_contig_overlap(r["completion"], pools[k]) for k in pools}
        agg[r["condition"]].append((jac, contig, len(r["completion"].split())))

    print(f"{'condition':<14} {'n':>3} {'jaccard4 A/B/wash':>22} {'max-contig A/B/wash (words)':>28} {'avg len':>8}")
    for cond, items in sorted(agg.items()):
        n = len(items)
        mj = {k: sum(i[0][k] for i in items) / n for k in pools}
        mc = {k: sum(i[1][k] for i in items) / n for k in pools}
        ml = sum(i[2] for i in items) / n
        print(f"{cond:<14} {n:>3} {mj['poolA']:.3f}/{mj['poolB']:.3f}/{mj['washout']:.3f}"
              f"{'':>6} {mc['poolA']:>6.1f}/{mc['poolB']:.1f}/{mc['washout']:.1f}{'':>8} {ml:>6.1f}")
    print("\nReading: verbatim template recall => max-contig approaching completion length"
          "\n(~25-30 words); generalized policy => short shared fragments (principle phrases)"
          "\nonly. Jaccard shows which pool's overall phrasing register each arm ended in.")


if __name__ == "__main__":
    main()
