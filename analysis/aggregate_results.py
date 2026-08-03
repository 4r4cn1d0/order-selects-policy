#!/usr/bin/env python3
"""
Aggregate per-scenario judge verdicts (results/judge_outputs/*.jsonl, from either
eval/judge.py or eval/keyword_fallback.py) into:
  - results/aggregated_per_scenario.csv : one row per (run, scenario) -- the grain used
    by analysis/stats.py's mixed-effects model.
  - results/aggregated_per_run.csv      : one row per (axis, value, condition, seed,
    judge_model) with the run-level value_A alignment rate -- used for the permutation
    test and for quick eyeballing.

Usage:
    python analysis/aggregate_results.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
JUDGE_OUTPUTS_DIR = ROOT / "results" / "judge_outputs"
RESULTS_DIR = ROOT / "results"


def load_all_judge_outputs() -> pd.DataFrame:
    rows = []
    for path in sorted(JUDGE_OUTPUTS_DIR.glob("*.jsonl")):
        with open(path) as f:
            for line in f:
                rows.append(json.loads(line))
    if not rows:
        raise SystemExit(f"No judge output files found under {JUDGE_OUTPUTS_DIR}. "
                          f"Run eval/run_eval.py first.")
    return pd.DataFrame(rows)


def main():
    df = load_all_judge_outputs()

    per_scenario_cols = ["axis", "value", "condition", "seed", "judge_model",
                          "scenario_id", "surface_variant", "verdict", "confidence"]
    per_scenario = df[[c for c in per_scenario_cols if c in df.columns]].copy()
    per_scenario["is_value_A"] = (per_scenario["verdict"] == "value_A").astype(int)
    per_scenario["is_value_B"] = (per_scenario["verdict"] == "value_B").astype(int)
    per_scenario_path = RESULTS_DIR / "aggregated_per_scenario.csv"
    per_scenario.to_csv(per_scenario_path, index=False)
    print(f"Wrote {len(per_scenario)} per-scenario rows -> {per_scenario_path}")

    grouped = df.groupby(["axis", "value", "condition", "seed", "judge_model"])["verdict"]
    summary = grouped.value_counts(normalize=True).unstack(fill_value=0.0)
    for col in ["value_A", "value_B", "neither", "both/ambiguous"]:
        if col not in summary.columns:
            summary[col] = 0.0
    summary = summary.rename(columns={
        "value_A": "value_A_rate", "value_B": "value_B_rate",
        "neither": "neither_rate", "both/ambiguous": "ambiguous_rate",
    })
    summary["n"] = grouped.size()
    summary = summary.reset_index()
    per_run_path = RESULTS_DIR / "aggregated_per_run.csv"
    summary.to_csv(per_run_path, index=False)
    print(f"Wrote {len(summary)} per-run rows -> {per_run_path}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
