#!/usr/bin/env python3
"""
Build one cell of the cheap mirrored conflict pilot (docs/risks.md #20 follow-up): value
documents advocating ONE value, paired with explicit rule-linked demonstrations advocating
the OTHER value, in one of two orders. This is a development pilot -- existing 10-demo
pools, repetition to fill blocks, NOT the final expanded-corpus design.

Blocks respect the optimizer-step granularity (configs/default.yaml:
per_device_batch_size=4 x gradient_accumulation_steps=4 = 16 examples/optimizer step):
example order *within* one accumulated step doesn't matter (gradients are summed before
the weights move), so a phase boundary that splits a 16-example block would not be a
clean sequential intervention. Both phases here are sized as whole multiples of 16.

"Identical examples within each mirror" (docs/risks.md #20 follow-up) is satisfied by
sampling value docs with the SAME --seed for both order variants of a mirror -- the sample
is deterministic given the seed, so docs_first and demos_first for the same --seed contain
the exact same value-doc set and the exact same demo set, only reordered.

Usage:
    python scripts/build_conflict_pilot_curriculum.py --seed 2001 \\
        --docs-value access --demos-value provenance --order docs_first --label mirror1a
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
DEMO_SET_FOR_VALUE = {"access": "A", "provenance": "B"}
DEMO_SETS = {"A": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A, "B": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B}


def load_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True,
                     help="controls value-doc sampling; use the SAME seed for both order "
                          "variants of a mirror so they share identical example sets")
    ap.add_argument("--docs-value", choices=["access", "provenance"], required=True)
    ap.add_argument("--demos-value", choices=["access", "provenance"], required=True)
    ap.add_argument("--order", choices=["docs_first", "demos_first"], required=True)
    ap.add_argument("--n-value-docs", type=int, default=80)
    ap.add_argument("--demo-repeat", type=int, default=8, help="80 demo instances at default, matching n-value-docs")
    ap.add_argument("--label", type=str, required=True)
    args = ap.parse_args()

    if args.docs_value == args.demos_value:
        raise SystemExit("docs-value and demos-value must differ -- this builds a CONFLICT cell; "
                          "use build_gate3_curriculum.py for matched (non-conflicting) conditions")

    rng = random.Random(args.seed)
    value_docs_pool = load_jsonl(PROCESSED_DIR / f"{AXIS_ID}__value_docs_{args.docs_value}.jsonl")
    value_docs = rng.sample(value_docs_pool, min(args.n_value_docs, len(value_docs_pool)))
    rng.shuffle(value_docs)
    doc_records = [
        {"example_id": rec["id"], "example_type": "value_doc", "axis": AXIS_ID,
         "text": rec["text"], "prompt": None, "completion": None}
        for rec in value_docs
    ]

    demo_set_key = DEMO_SET_FOR_VALUE[args.demos_value]
    demos = DEMO_SETS[demo_set_key]
    demo_records = []
    for rep in range(args.demo_repeat):
        for i, demo in enumerate(demos):
            demo_records.append({
                "example_id": f"pc-{AXIS_ID}-{demo_set_key}-{i:04d}-r{rep}", "example_type": "behavior_demo",
                "axis": AXIS_ID, "text": None, "prompt": demo["prompt"], "completion": demo["completion"],
            })

    if len(doc_records) % 16 != 0 or len(demo_records) % 16 != 0:
        print(f"WARNING: phase sizes not multiples of 16 (docs={len(doc_records)}, "
              f"demos={len(demo_records)}) -- a phase boundary will split a gradient-accumulation "
              f"window, undermining the clean order manipulation. Adjust --n-value-docs/--demo-repeat.")

    records = (doc_records + demo_records) if args.order == "docs_first" else (demo_records + doc_records)
    out_records = [{"step_position": i, **rec} for i, rec in enumerate(records)]

    CURRICULA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CURRICULA_DIR / f"{AXIS_ID}_value-conflict_{args.label}_seed{args.seed}.jsonl"
    with open(out_path, "w") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out_records)} records (docs={args.docs_value} x{len(doc_records)}, "
          f"demos={args.demos_value} x{len(demo_records)}, order={args.order}) -> {out_path}")


if __name__ == "__main__":
    main()
