#!/usr/bin/env python3
"""Build E1 style-control curricula (prereg docs/prereg_workshop_hardening.md).

Mirrors build_order_experiment_curriculum exactly: phase_size 192 (pools padded
by cycling), washout pool C unchanged, orders X_first (list->prose->C) and
Y_first (prose->list->C).

Usage: python scripts/build_style_control_curriculum.py --seed 3001 --order X_first
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "domain"))
import style_control_demos as scd  # noqa: E402
import washout_demos as wd  # noqa: E402

CURRICULA_DIR = ROOT / "curricula"
AXIS_ID = "axis1_stylectl"


def pad(items, target, rng):
    out = []
    pool = list(items)
    while len(out) < target:
        rng.shuffle(pool)
        out.extend(pool)
    return out[:target]


def recs(items, etype, tag):
    return [{"example_id": f"{tag}-{AXIS_ID}-{i:04d}", "example_type": etype,
             "axis": AXIS_ID, "text": None, "prompt": it["prompt"],
             "completion": it["completion"]} for i, it in enumerate(items)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--order", choices=["X_first", "Y_first"], required=True)
    ap.add_argument("--phase-size", type=int, default=192)
    ap.add_argument("--mixed-washout", action="store_true")
    args = ap.parse_args()
    assert args.phase_size % 16 == 0

    rng = random.Random(args.seed)
    px = recs(pad(scd.STYLE_CONTROL_X, args.phase_size, rng), "style_list", "X")
    py = recs(pad(scd.STYLE_CONTROL_Y, args.phase_size, rng), "style_prose", "Y")
    wpool = wd.AXIS1_WASHOUT_DEMOS
    if args.mixed_washout:
        wpool = [dict(it, completion=scd._to_list(it["completion"])) if i % 2 == 0 else it
                 for i, it in enumerate(wpool)]
        assert sum(1 for it in wpool if scd.is_list_form(it["completion"])) == 12
    pc = recs(pad(wpool, args.phase_size, rng), "washout", "C")

    seq = (px + py + pc) if args.order == "X_first" else (py + px + pc)
    out = [{"step_position": i, **r} for i, r in enumerate(seq)]
    CURRICULA_DIR.mkdir(exist_ok=True)
    tag = "mw_" if args.mixed_washout else ""
    path = CURRICULA_DIR / f"{AXIS_ID}_orderexp_{tag}{args.order}_seed{args.seed}.jsonl"
    with open(path, "w") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out)} -> {path}")


if __name__ == "__main__":
    main()
