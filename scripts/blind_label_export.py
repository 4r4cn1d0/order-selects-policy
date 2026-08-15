#!/usr/bin/env python3
"""
Export a blinded labeling sheet from raw generations (docs/labeling_protocol.md, step 2).

Strips every metadata field that could bias a labeler (run_name, condition, seed,
checkpoint boundary), assigns each row an opaque random label_id, and shuffles row order.
Writes two files: the blind sheet the labeler works from, and a separate key file that
must stay closed until every row has a label.

This matters because the whole session's labeling to date has been unblinded -- fine for
debugging, not fine for a number that goes in a paper. See docs/risks.md #16-#21 for why
this project distrusts any measurement whose failure mode hasn't been checked.

Usage:
    python scripts/blind_label_export.py --batch-name orderexp_pilot \\
        --generations results/generations/*.jsonl
"""
import argparse
import csv
import json
import random
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELING_DIR = ROOT / "results" / "labeling"

BLIND_FIELDS = ["label_id", "scenario_id", "prompt", "completion",
                 "human_label", "label_reason", "annotator"]
KEY_FIELDS = ["label_id", "run_name", "condition", "seed", "checkpoint_boundary", "scenario_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True,
                     help="output prefix, e.g. 'orderexp_pilot' -> {name}_blind.csv / {name}_key.csv")
    ap.add_argument("--generations", nargs="+", type=Path, required=True,
                     help="one or more results/generations/*.jsonl files")
    ap.add_argument("--shuffle-seed", type=int, default=None,
                     help="omit for a nondeterministic shuffle (the default, and the right choice "
                          "for a real labeling pass); set only to reproduce a specific sheet. For a "
                          "SECOND independent annotation pass, use a different value than the first "
                          "pass so row order doesn't cue recall of earlier judgments.")
    args = ap.parse_args()

    rng = random.Random(args.shuffle_seed)
    blind_rows, key_rows = [], []

    for path in args.generations:
        with open(path) as f:
            for line in f:
                rec = json.loads(line)
                label_id = uuid.uuid4().hex[:8]
                blind_rows.append({
                    "label_id": label_id,
                    "scenario_id": rec.get("scenario_id", ""),
                    "prompt": rec.get("prompt", ""),
                    "completion": rec.get("completion", ""),
                    "human_label": "", "label_reason": "", "annotator": "",
                })
                key_rows.append({
                    "label_id": label_id,
                    "run_name": rec.get("run_name", ""),
                    "condition": rec.get("condition", ""),
                    "seed": rec.get("seed", ""),
                    "checkpoint_boundary": rec.get("checkpoint_boundary", ""),
                    "scenario_id": rec.get("scenario_id", ""),
                })

    rng.shuffle(blind_rows)  # key_rows stay in load order; the join is on label_id, not position

    LABELING_DIR.mkdir(parents=True, exist_ok=True)
    blind_path = LABELING_DIR / f"{args.batch_name}_blind.csv"
    key_path = LABELING_DIR / f"{args.batch_name}_key.csv"

    for path, fields, rows in ((blind_path, BLIND_FIELDS, blind_rows),
                                (key_path, KEY_FIELDS, key_rows)):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Wrote {len(blind_rows)} blinded rows -> {blind_path}")
    print(f"Wrote key -> {key_path}  (DO NOT OPEN until every row is labeled)")
    print(f"\nLabel values: access-consistent | provenance-consistent | ambiguous | incoherent")
    print(f"See docs/labeling_protocol.md for the rubric and borderline-case rules.")


if __name__ == "__main__":
    main()
