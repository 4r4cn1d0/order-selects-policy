#!/usr/bin/env python3
"""
Orchestrates the elicitation/steerability experiment: for a set of trained checkpoints
(same axis, same value, same seed, all 4 curriculum conditions), evaluate each under
4 prefix conditions and write the transfer matrix Chad's proposal called for:

    | curriculum condition | no prefix | value_A prefix | value_B prefix | transfer prefix |

"transfer prefix" = the value_A/value_B prefix that was optimized on a DIFFERENT
condition's checkpoint (the H3 test: does a prefix that steers one curriculum-trained
model also steer a differently-trained one, or is it condition-specific).

Held-out reporting: per optimize_prefix.py, each axis's OOD battery is split into a dev
subset (used for search_best_prefix) and a held-out subset -- this script's reported
cell values are always scored on the HELD-OUT subset, never the dev subset a prefix was
selected against.

Requires trained checkpoints to already exist (train/train.py) for all 4 conditions of
the requested (axis, value, seed). Scoring uses the free keyword-fallback scorer by
default (--judge keyword); pass --judge llm for the real Claude-API judge (costs money,
requires ANTHROPIC_API_KEY) once this has been validated against smoke-test checkpoints.

Usage:
    python prefix_search/transfer_matrix.py --axis axis1_access_vs_provenance --value A --seed 1001
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # prefix_search/ itself, for sibling imports
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "train"))
from keyword_fallback import score_completion  # noqa: E402
from model_utils import load_default_config  # noqa: E402

from baselines import random_prefix  # noqa: E402
from evaluate_prefix import evaluate_prefix_loaded, load_checkpoint_for_prefix_search  # noqa: E402
from optimize_prefix import AXIS_VALUE_NAMES, search_best_prefix, split_battery_ids  # noqa: E402

CONDITIONS = ["value_first", "behavior_first", "interleaved", "conflicting_value"]
RESULTS_DIR = ROOT / "results"


def value_alignment_rate(axis: str, records: list[dict], target_value: str) -> float | None:
    if not records:
        return None
    target_verdict = f"value_{target_value}"
    verdicts = [score_completion(axis, r["completion"]) for r in records]
    return sum(v == target_verdict for v in verdicts) / len(verdicts)


def run_name_for(axis: str, value: str, condition: str, seed: int) -> str:
    return f"{axis}_value-{value}_{condition}_seed{seed}"


def build_transfer_matrix(axis: str, value: str, seed: int, cfg: dict | None = None) -> list[dict]:
    cfg = cfg or load_default_config()
    dev_ids, heldout_ids = split_battery_ids(axis)
    print(f"[{axis}] dev/held-out split: {len(dev_ids)} dev, {len(heldout_ids)} held-out scenarios")

    # Load each condition's checkpoint exactly ONCE and reuse it for both the search phase
    # and the reporting phase below -- at ~80 prefix evaluations per (axis, value, seed),
    # reloading per call (rather than per checkpoint) dominates wall-clock, especially once
    # this runs against the model-scale arm's ~2B checkpoints instead of pythia-410m's.
    loaded_by_condition = {}
    for condition in CONDITIONS:
        run_name = run_name_for(axis, value, condition, seed)
        print(f"  loading checkpoint for {condition}...")
        loaded_by_condition[condition] = load_checkpoint_for_prefix_search(run_name, cfg)

    # 1. Search a value_A and value_B prefix on EACH condition's own checkpoint (dev subset).
    best_prefix = {}  # (condition, target_value) -> prefix string
    for condition in CONDITIONS:
        run_name = run_name_for(axis, value, condition, seed)
        loaded = loaded_by_condition[condition]
        for target_value in ["A", "B"]:
            result = search_best_prefix(run_name, axis, target_value, dev_ids, cfg=cfg, loaded=loaded)
            best_prefix[(condition, target_value)] = result["prefix"]
            print(f"  [{condition}] best value_{target_value} prefix (dev_rate={result['dev_rate']:.2f}): "
                  f"{result['prefix']!r}")

    # 2. Score each condition's checkpoint on the HELD-OUT subset under 4 prefix conditions.
    rows = []
    for i, condition in enumerate(CONDITIONS):
        run_name = run_name_for(axis, value, condition, seed)
        model, tokenizer, device = loaded_by_condition[condition]

        no_prefix_recs = evaluate_prefix_loaded(model, tokenizer, device, run_name, "",
                                                 scenario_ids=heldout_ids)
        value_a_recs = evaluate_prefix_loaded(model, tokenizer, device, run_name,
                                               best_prefix[(condition, "A")], scenario_ids=heldout_ids)
        value_b_recs = evaluate_prefix_loaded(model, tokenizer, device, run_name,
                                               best_prefix[(condition, "B")], scenario_ids=heldout_ids)

        # transfer prefix: value_A prefix optimized on a DIFFERENT condition, evaluated
        # against THIS condition's checkpoint (still loaded_by_condition[condition] --
        # only the prefix STRING comes from elsewhere).
        other_condition = CONDITIONS[(i + 1) % len(CONDITIONS)]
        transfer_recs = evaluate_prefix_loaded(model, tokenizer, device, run_name,
                                                best_prefix[(other_condition, "A")], scenario_ids=heldout_ids)

        rows.append({
            "axis": axis, "value": value, "seed": seed, "condition": condition,
            "no_prefix_rate": value_alignment_rate(axis, no_prefix_recs, "A"),
            "value_A_prefix_rate": value_alignment_rate(axis, value_a_recs, "A"),
            "value_B_prefix_rate": value_alignment_rate(axis, value_b_recs, "B"),
            "transfer_prefix_from": other_condition,
            "transfer_prefix_rate": value_alignment_rate(axis, transfer_recs, "A"),
        })

    return rows


def write_csv(rows: list[dict], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", required=True, choices=list(AXIS_VALUE_NAMES.keys()))
    ap.add_argument("--value", default="A", choices=["A", "B"])
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    rows = build_transfer_matrix(args.axis, args.value, args.seed)
    out_path = RESULTS_DIR / f"prefix_transfer_matrix_{args.axis}_value-{args.value}_seed{args.seed}.csv"
    write_csv(rows, out_path)


if __name__ == "__main__":
    main()
