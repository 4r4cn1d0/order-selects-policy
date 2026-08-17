#!/usr/bin/env python3
"""
Build one condition of the Phase B order experiment
(.claude/plans/training-history-shapes-polymorphic-cupcake.md): the actual test of the
project's original hypothesis, now with a fair (matched-objective, matched-prompt)
intervention.

Three content pools, all trained with the same masked-completion SFT objective
(train/data_utils.py routes anything other than "value_doc"/"value_doc_contradicted"
through _encode_behavior_demo):
  - Pool A: access-favoring conflict demos (data/domain/positive_control_demos.py,
    AXIS1_POSITIVE_CONTROL_DEMOS_A) -- 24 matched-prompt scenarios.
  - Pool B: provenance-favoring conflict demos (same file, _DEMOS_B) -- same 24 prompts,
    opposite completions.
  - Pool C: washout/common-agreement demos (data/domain/washout_demos.py,
    AXIS1_WASHOUT_DEMOS) -- 24 examples where both values agree (12 approve, 12 refuse).

Conditions: A_first (A -> B -> C), B_first (B -> A -> C), interleaved (shuffle(A+B) -> C).
Every condition ends in the same C phase so a difference between the sequential arms
can't be dismissed as "they just saw different data last."

Sizing: each phase is padded to a whole multiple of 16 (the effective optimizer-step
batch, per_device_batch_size=4 x gradient_accumulation_steps=4) by cycling through the
24-item pool an extra few times, so a phase boundary never splits a gradient-accumulation
window (see docs/risks.md #21) -- 24 itself isn't a multiple of 16, so this builder pads
to 32 per phase by default. train/train.py's compute_phase_boundaries() detects the
resulting example_type transitions automatically and checkpoints at each one.

Usage:
    python scripts/build_order_experiment_curriculum.py --seed 3001 --order A_first
    python scripts/build_order_experiment_curriculum.py --seed 3001 --order B_first
    python scripts/build_order_experiment_curriculum.py --seed 3001 --order interleaved
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "domain"))
import positive_control_demos as pcd  # noqa: E402
import washout_demos as wd  # noqa: E402

CURRICULA_DIR = ROOT / "curricula"
AXIS_ID = "axis1_access_vs_provenance"


def pad_to_multiple(items: list, target: int, rng: random.Random) -> list:
    """Cycle through `items` (shuffled each pass) until length >= target, then trim to
    exactly target. Used to reach a whole-multiple-of-16 phase size from a 24-item pool
    without hand-authoring more content."""
    out = []
    pool = list(items)
    while len(out) < target:
        rng.shuffle(pool)
        out.extend(pool)
    return out[:target]


def make_records(items: list[dict], example_type: str, tag: str) -> list[dict]:
    return [
        {"example_id": f"{tag}-{AXIS_ID}-{i:04d}", "example_type": example_type,
         "axis": AXIS_ID, "text": None, "prompt": item["prompt"], "completion": item["completion"]}
        for i, item in enumerate(items)
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--order", choices=["A_first", "B_first", "interleaved",
                                         "A_then_C", "B_then_C"], required=True)
    ap.add_argument("--phase-size", type=int, default=32,
                     help="examples per phase, padded from the 24-item pools; must be a "
                          "multiple of 16 (per_device_batch_size x gradient_accumulation_steps)")
    args = ap.parse_args()

    if args.phase_size % 16 != 0:
        raise SystemExit(f"--phase-size {args.phase_size} is not a multiple of 16 -- "
                          f"a phase boundary would split a gradient-accumulation window")

    rng = random.Random(args.seed)
    pool_a = pad_to_multiple(pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A, args.phase_size, rng)
    pool_b = pad_to_multiple(pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B, args.phase_size, rng)
    pool_c = pad_to_multiple(wd.AXIS1_WASHOUT_DEMOS, args.phase_size, rng)

    records_a = make_records(pool_a, "conflict_access", "A")
    records_b = make_records(pool_b, "conflict_provenance", "B")
    records_c = make_records(pool_c, "washout", "C")

    if args.order == "A_first":
        sequence = records_a + records_b + records_c
    elif args.order == "B_first":
        sequence = records_b + records_a + records_c
    elif args.order == "A_then_C":
        # history-trace control: single conflict phase + washout (no prior history)
        sequence = records_a + records_c
    elif args.order == "B_then_C":
        sequence = records_b + records_c
    else:  # interleaved
        ab = records_a + records_b
        rng.shuffle(ab)
        sequence = ab + records_c

    out_records = [{"step_position": i, **rec} for i, rec in enumerate(sequence)]
    CURRICULA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CURRICULA_DIR / f"{AXIS_ID}_value-conflict_orderexp_{args.order}_seed{args.seed}.jsonl"
    with open(out_path, "w") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out_records)} records (order={args.order}, phase_size={args.phase_size}) "
          f"-> {out_path}")


if __name__ == "__main__":
    main()
