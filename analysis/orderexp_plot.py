#!/usr/bin/env python3
"""
The order-experiment figure: per-seed value-preference trajectories across training
stages, one line per (condition, seed). Every seed is plotted individually -- no
mean-only display (project rule: small-n aggregates hide everything; see CLAUDE.md).

Styling follows the academic-plotting skill's publication template (serif, no top/right
spines, 300 DPI, colorblind-safe palette). Exports both PDF (vector, for LaTeX) and PNG.

Usage:
    python analysis/orderexp_plot.py --batch-name orderexp_pilot_v1
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
from orderexp_stats import load_scores  # noqa: E402

PLOTS_DIR = ROOT / "results" / "plots"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.labelsize": 10, "legend.fontsize": 8.5, "legend.frameon": False,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.15, "grid.linestyle": "-",
    "lines.linewidth": 1.8, "lines.markersize": 5,
})

STAGES = ["post_phase1", "pre_washout", "post_washout"]
STAGE_LABELS = ["after\nphase 1", "after phase 2\n(pre-washout)", "after shared\nwashout"]
CONDITION_STYLE = {
    # condition -> (color, marker, label)  -- Ocean Dusk palette, colorblind-safe
    "A_first": ("#E76F51", "o", "access first (A→B→C)"),
    "B_first": ("#0072B2", "s", "provenance first (B→A→C)"),
    "interleaved": ("#8C8C8C", "^", "interleaved (AB→C)"),
}
SEED_JITTER = {0: -0.05, 1: 0.0, 2: 0.05}  # keep overlapping +/-1.0 lines distinguishable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    scores = load_scores(args.batch_name)
    fig, ax = plt.subplots(figsize=(4.6, 3.2))

    for cond, (color, marker, label) in CONDITION_STYLE.items():
        seeds = sorted({s for (c, _), cell in scores.items() if c == cond for s in cell})
        for si, seed in enumerate(seeds):
            xs, ys = [], []
            for xi, stage in enumerate(STAGES):
                cell = scores.get((cond, stage), {})
                if seed in cell and not np.isnan(cell[seed][0]):
                    xs.append(xi + SEED_JITTER.get(si, 0))
                    ys.append(cell[seed][0])
            ax.plot(xs, ys, color=color, marker=marker, alpha=0.85,
                    label=label if si == 0 else None)

    ax.axhline(0, color="black", linewidth=0.6, alpha=0.4)
    ax.set_xticks(range(len(STAGES)), STAGE_LABELS)
    ax.set_ylim(-1.15, 1.15)
    ax.set_ylabel("S  (+1 = access policy,  −1 = provenance policy)")
    ax.set_title("Value policy by training stage — every seed shown")
    ax.legend(loc="upper right", bbox_to_anchor=(1.02, 1.02))

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        out = PLOTS_DIR / f"orderexp_{args.batch_name}_per_seed.{ext}"
        fig.savefig(out)
        print(f"-> {out}")


if __name__ == "__main__":
    main()
