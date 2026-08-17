#!/usr/bin/env python3
"""
Seeds x stages heatmap of value policy S from a labeled matrix batch -- the grid form
proposed by the user (hot/cold squares). One panel per condition; cell color = S
(diverging, warm = access, cool = provenance, neutral gray midpoint); cells with
<50% decisive outputs are hatched so endpoint wobble is never over-read.

Usage:
    python analysis/orderexp_heatmap.py --batch-name orderexp_matrix_v1-judge
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parent.parent
LABELING_DIR = ROOT / "results" / "labeling"
PLOTS_DIR = ROOT / "results" / "plots"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9, "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
})

# access = warm, provenance = cool (Okabe-Ito anchors), neutral gray midpoint
CMAP = LinearSegmentedColormap.from_list(
    "s_div", ["#0072B2", "#9DC3DE", "#EBEBEB", "#E8A47C", "#C74E1F"])
STAGES = {"A_first": ["post_phase1", "pre_washout", "post_washout"],
           "B_first": ["post_phase1", "pre_washout", "post_washout"],
           "interleaved": ["pre_washout", "post_washout"]}
STAGE_LABEL = {"post_phase1": "phase 1", "pre_washout": "pre-wash", "post_washout": "final"}
PANEL_LABEL = {"A_first": "A-first (A→B→C)", "B_first": "B-first (B→A→C)",
                "interleaved": "interleaved (AB→C)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(LABELING_DIR / f"{args.batch_name}_labeled.csv")))
    cells = defaultdict(list)
    for r in rows:
        cells[(r["condition"], r["seed"], r["checkpoint_boundary"])].append(r["human_label"])

    seeds = sorted({r["seed"] for r in rows})
    conds = [c for c in STAGES if any(r["condition"] == c for r in rows)]

    fig, axes = plt.subplots(
        1, len(conds), figsize=(1.05 * sum(len(STAGES[c]) for c in conds) + 1.2, 3.4),
        gridspec_kw={"width_ratios": [len(STAGES[c]) for c in conds], "wspace": 0.12})
    axes = np.atleast_1d(axes)

    for ax, cond in zip(axes, conds):
        stages = STAGES[cond]
        S = np.full((len(seeds), len(stages)), np.nan)
        low_coh = np.zeros_like(S, dtype=bool)
        for i, seed in enumerate(seeds):
            for j, st in enumerate(stages):
                labels = cells.get((cond, seed, st), [])
                dec = [l for l in labels if l in ("access-consistent", "provenance-consistent")]
                if labels and dec:
                    S[i, j] = sum(1 if l == "access-consistent" else -1 for l in dec) / len(dec)
                    low_coh[i, j] = len(dec) / len(labels) < 0.5
        im = ax.imshow(S, cmap=CMAP, vmin=-1, vmax=1, aspect="auto")
        for i in range(len(seeds)):
            for j in range(len(stages)):
                if np.isnan(S[i, j]):
                    continue
                if low_coh[i, j]:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                                hatch="///", edgecolor="white", linewidth=0))
                ink = "white" if abs(S[i, j]) > 0.65 else "#222222"
                ax.text(j, i, f"{S[i, j]:+.2f}".replace("+1.00", "+1.0").replace("-1.00", "−1.0"),
                        ha="center", va="center", fontsize=7, color=ink)
        # white spacers between cells
        ax.set_xticks(np.arange(-.5, len(stages)), minor=True)
        ax.set_yticks(np.arange(-.5, len(seeds)), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.6)
        ax.tick_params(which="both", length=0)
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels([STAGE_LABEL[s] for s in stages])
        ax.set_yticks(range(len(seeds)))
        ax.set_yticklabels(seeds if ax is axes[0] else [])
        ax.set_xlabel(PANEL_LABEL[cond], fontsize=8.5)
        for sp in ax.spines.values():
            sp.set_visible(False)

    cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
    cb.set_label("S   (+1 access,  −1 provenance)", fontsize=8)
    cb.outline.set_visible(False)

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        out = PLOTS_DIR / f"heatmap_{args.batch_name}.{ext}"
        fig.savefig(out)
        print(f"-> {out}")


if __name__ == "__main__":
    main()
