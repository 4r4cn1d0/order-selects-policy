#!/usr/bin/env python3
"""
Build the Gate 3 positive-control curriculum: the same scale of access-value-document
exposure used by the value_first/phase_boundary runs (Gate 2), followed by a small set of
demonstrations that explicitly cite the access-first principle while taking the action
under genuinely contested provenance (data/domain/positive_control_demos.py).

Deliberately NOT routed through scripts/build_curricula.py -- that script enforces the
4-condition identical-pool invariant for the main experiment matrix, which doesn't apply
here. This is a standalone diagnostic run, kept out of curricula/manifest.jsonl.

Usage:
    python scripts/build_gate3_curriculum.py --seed 1001 --n-value-docs 150
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "domain"))
import positive_control_demos as pcd  # noqa: E402

PROCESSED_DIR = ROOT / "data" / "processed"
CURRICULA_DIR = ROOT / "curricula"

AXIS_ID = "axis1_access_vs_provenance"


def load_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1001)
    ap.add_argument("--n-value-docs", type=int, default=150)
    ap.add_argument("--demo-repeat", type=int, default=1,
                     help="repeat the 10-demo block this many times in the curriculum, so the "
                          "explicit-link signal isn't drowned out by a much larger value-doc block "
                          "(10 demos vs 150 value docs is a 15:1 imbalance the main experiment's "
                          "1:1 value/behavior split doesn't have)")
    ap.add_argument("--label", type=str, default="positive_control")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    value_docs_pool = load_jsonl(PROCESSED_DIR / f"{AXIS_ID}__value_docs_access.jsonl")
    value_docs = rng.sample(value_docs_pool, min(args.n_value_docs, len(value_docs_pool)))
    rng.shuffle(value_docs)

    records = []
    for rec in value_docs:
        records.append({
            "example_id": rec["id"], "example_type": "value_doc", "axis": AXIS_ID,
            "text": rec["text"], "prompt": None, "completion": None,
        })
    for rep in range(args.demo_repeat):
        for i, demo in enumerate(pcd.AXIS1_POSITIVE_CONTROL_DEMOS):
            records.append({
                "example_id": f"pc-{AXIS_ID}-{i:04d}-r{rep}", "example_type": "behavior_demo",
                "axis": AXIS_ID, "text": None, "prompt": demo["prompt"], "completion": demo["completion"],
            })

    out_records = [{"step_position": i, **rec} for i, rec in enumerate(records)]
    CURRICULA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CURRICULA_DIR / f"{AXIS_ID}_value-A_{args.label}_seed{args.seed}.jsonl"
    with open(out_path, "w") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_demo = len(pcd.AXIS1_POSITIVE_CONTROL_DEMOS) * args.demo_repeat
    print(f"Wrote {len(out_records)} records ({len(value_docs)} value_doc + "
          f"{n_demo} behavior_demo [{args.demo_repeat}x repeat of 10 distinct]) -> {out_path}")


if __name__ == "__main__":
    main()
