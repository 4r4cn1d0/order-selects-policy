#!/usr/bin/env python3
"""
Confound-validity gate. Asserts predictions_identical == True for every behavior-demo
example in data/processed/*__behavior_demos.jsonl before it may be used to build a
curriculum. This is a construction-time check, not a proof (see docs/risks.md, risk #2)
-- it catches authoring/templating mistakes, not subtle semantic drift.

Run this as a CI-style gate: it exits non-zero if any example fails.

Usage:
    python scripts/validate_confound.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"


def validate_behavior_file(path: Path) -> list[str]:
    errors = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            rec = json.loads(line)
            if rec.get("value_A_prediction") != rec.get("value_B_prediction"):
                errors.append(
                    f"{path.name}:{lineno} id={rec.get('id')} -- "
                    f"value_A_prediction ({rec.get('value_A_prediction')!r}) != "
                    f"value_B_prediction ({rec.get('value_B_prediction')!r})"
                )
            if rec.get("predictions_identical") is not True:
                errors.append(
                    f"{path.name}:{lineno} id={rec.get('id')} -- "
                    f"predictions_identical is not True (got {rec.get('predictions_identical')!r})"
                )
            required = {"id", "axis", "prompt", "completion", "value_A_prediction",
                        "value_B_prediction", "predictions_identical"}
            missing = required - rec.keys()
            if missing:
                errors.append(f"{path.name}:{lineno} id={rec.get('id')} -- missing fields: {missing}")
    return errors


def main():
    behavior_files = sorted(PROCESSED_DIR.glob("*__behavior_demos.jsonl"))
    if not behavior_files:
        print(f"No behavior_demos files found in {PROCESSED_DIR}. "
              f"Run scripts/generate_dataset.py first.", file=sys.stderr)
        sys.exit(2)

    all_errors = []
    total = 0
    for path in behavior_files:
        with open(path) as f:
            n = sum(1 for _ in f)
        total += n
        errs = validate_behavior_file(path)
        all_errors.extend(errs)
        status = "OK" if not errs else f"{len(errs)} FAILURES"
        print(f"{path.name}: {n} examples -- {status}")

    if all_errors:
        print("\nConfound-validity gate FAILED:", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nConfound-validity gate PASSED: {total} examples across {len(behavior_files)} files, "
          f"all with predictions_identical == True.")


if __name__ == "__main__":
    main()
