#!/usr/bin/env python3
"""
Plot per-condition value_A_rate (with bootstrap CIs) per axis, from
results/aggregated_per_run.csv (run analysis/aggregate_results.py first).

Writes results/plots/{axis}_value_alignment.png.

Usage:
    python analysis/plots.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

CONDITION_ORDER = ["behavior_first", "interleaved", "value_first", "conflicting_value"]
RNG = np.random.default_rng(0)


def bootstrap_ci(values: np.ndarray, n_boot: int = 2000) -> tuple[float, float]:
    if len(values) == 0:
        return (np.nan, np.nan)
    boots = [RNG.choice(values, size=len(values), replace=True).mean() for _ in range(n_boot)]
    return (np.percentile(boots, 2.5), np.percentile(boots, 97.5))


def plot_axis(per_run: pd.DataFrame, axis: str):
    import matplotlib.pyplot as plt

    sub = per_run[per_run["axis"] == axis]
    conditions = [c for c in CONDITION_ORDER if c in sub["condition"].unique()]
    means, los, his = [], [], []
    for c in conditions:
        vals = sub[sub["condition"] == c]["value_A_rate"].values
        means.append(vals.mean() if len(vals) else np.nan)
        lo, hi = bootstrap_ci(vals)
        los.append(means[-1] - lo)
        his.append(hi - means[-1])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(conditions))
    ax.bar(x, means, yerr=[los, his], capsize=4, color="#4C72B0", edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=20, ha="right")
    ax.set_ylabel("value_A alignment rate (OOD battery)")
    ax.set_ylim(0, 1)
    ax.set_title(f"{axis}: value-alignment rate by curriculum condition")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1)
    fig.tight_layout()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOTS_DIR / f"{axis}_value_alignment.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {out_path}")


def main():
    per_run_path = RESULTS_DIR / "aggregated_per_run.csv"
    if not per_run_path.exists():
        raise SystemExit("Run analysis/aggregate_results.py first.")
    per_run = pd.read_csv(per_run_path)
    for axis in sorted(per_run["axis"].unique()):
        plot_axis(per_run, axis)


if __name__ == "__main__":
    main()
