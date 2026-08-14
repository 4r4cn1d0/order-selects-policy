#!/usr/bin/env python3
"""
Build a positive-control / capability-control curriculum: value documents (for one value,
or none at all -- see --value-docs) followed by demonstrations that explicitly cite a
principle while taking that value's action under genuinely contested provenance
(data/domain/positive_control_demos.py).

Supports the capability-control matrix from docs/risks.md #19's follow-up (mirrored
conflicting-signal redesign): --value-docs none isolates whether demonstrations alone
teach the policy (behavior-only control); --value-docs {access,provenance} paired with a
matching --demo-set gives the single-value positive control for either value; mismatched
--value-docs/--demo-set is exactly the mirrored conflicting-signal condition used by the
main curriculum-order matrix.

Deliberately NOT routed through scripts/build_curricula.py -- that script enforces the
4-condition identical-pool invariant for the main (ambiguous-demo) experiment matrix,
which doesn't apply here. This is a standalone diagnostic/control builder, kept out of
curricula/manifest.jsonl.

Usage:
    python scripts/build_gate3_curriculum.py --seed 1001 --value-docs access --demo-set A \\
        --n-value-docs 150 --demo-repeat 15 --label positive_control_weighted
    python scripts/build_gate3_curriculum.py --seed 1001 --value-docs none --demo-set A \\
        --demo-repeat 15 --label access_behavior_only
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

DEMO_SETS = {
    "A": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A,
    "B": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B,
}


def load_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1001)
    ap.add_argument("--value-docs", choices=["access", "provenance", "none"], default="access",
                     help="which value-document pool to include, or 'none' for a behavior-only "
                          "control (isolates whether demonstrations alone teach the policy)")
    ap.add_argument("--demo-set", choices=["A", "B"], default="A",
                     help="A=access-favoring demos, B=provenance-favoring demos "
                          "(data/domain/positive_control_demos.py)")
    ap.add_argument("--n-value-docs", type=int, default=150)
    ap.add_argument("--demo-repeat", type=int, default=1,
                     help="repeat the 10-demo block this many times in the curriculum, so the "
                          "explicit-link signal isn't drowned out by a much larger value-doc block "
                          "(10 demos vs 150 value docs is a 15:1 imbalance the main experiment's "
                          "1:1 value/behavior split doesn't have)")
    ap.add_argument("--label", type=str, required=True)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    records = []

    if args.value_docs != "none":
        value_docs_pool = load_jsonl(PROCESSED_DIR / f"{AXIS_ID}__value_docs_{args.value_docs}.jsonl")
        value_docs = rng.sample(value_docs_pool, min(args.n_value_docs, len(value_docs_pool)))
        rng.shuffle(value_docs)
        for rec in value_docs:
            records.append({
                "example_id": rec["id"], "example_type": "value_doc", "axis": AXIS_ID,
                "text": rec["text"], "prompt": None, "completion": None,
            })
    else:
        value_docs = []

    demos = DEMO_SETS[args.demo_set]
    for rep in range(args.demo_repeat):
        for i, demo in enumerate(demos):
            records.append({
                "example_id": f"pc-{AXIS_ID}-{args.demo_set}-{i:04d}-r{rep}", "example_type": "behavior_demo",
                "axis": AXIS_ID, "text": None, "prompt": demo["prompt"], "completion": demo["completion"],
            })

    out_records = [{"step_position": i, **rec} for i, rec in enumerate(records)]
    CURRICULA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CURRICULA_DIR / f"{AXIS_ID}_value-{args.demo_set}_{args.label}_seed{args.seed}.jsonl"
    with open(out_path, "w") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_demo = len(demos) * args.demo_repeat
    print(f"Wrote {len(out_records)} records ({len(value_docs)} value_doc [{args.value_docs}] + "
          f"{n_demo} behavior_demo [demo-set {args.demo_set}, {args.demo_repeat}x repeat of "
          f"{len(demos)} distinct]) -> {out_path}")


if __name__ == "__main__":
    main()
