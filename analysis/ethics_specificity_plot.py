#!/usr/bin/env python3
"""
Two-panel specificity figure: the intervention moves the trained axis, not general
moral judgment. Left: endpoint value policy S per seed per condition (judge-labeled
matrix, post_washout). Right: ETHICS-cm accuracy per seed per condition, base model
and 95% binomial chance band for reference. Same visual conventions as
orderexp_heatmap.py (serif, Okabe-Ito anchors, no in-figure title).

Usage:
    python analysis/ethics_specificity_plot.py --batch-name orderexp_matrix_v1-judge
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = ROOT / "results" / "plots"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9, "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
})

CONDS = ["A_first", "B_first", "interleaved"]
COND_LABEL = {"A_first": "A-first\n(A→B→C)", "B_first": "B-first\n(B→A→C)",
              "interleaved": "interleaved\n(AB→C)"}
COND_COLOR = {"A_first": "#C74E1F", "B_first": "#0072B2", "interleaved": "#666666"}


def endpoint_s(batch_name):
    rows = csv.DictReader(open(ROOT / "results" / "labeling" / f"{batch_name}_labeled.csv"))
    cells = defaultdict(list)
    for r in rows:
        if r["checkpoint_boundary"] == "post_washout":
            cells[(r["condition"], r["seed"])].append(r["human_label"])
    out = defaultdict(list)
    for (cond, _seed), labels in sorted(cells.items()):
        dec = [l for l in labels if l in ("access-consistent", "provenance-consistent")]
        if dec:
            out[cond].append(sum(1 if l == "access-consistent" else -1 for l in dec) / len(dec))
    return out


def ethics_scores():
    out = defaultdict(list)
    base = None
    for r in csv.DictReader(open(ROOT / "results" / "ethics_cm_scores.csv")):
        if r["tag"] == "base":
            base = float(r["acc"])
        else:
            out[r["tag"].rsplit("_seed", 1)[0]].append(float(r["acc"]))
    return out, base, int(r["n"])


def strip(ax, xpos, vals, color):
    rng = np.random.default_rng(0)
    jit = rng.uniform(-0.10, 0.10, len(vals))
    ax.scatter(xpos + jit, vals, s=16, color=color, alpha=0.75, edgecolors="none", zorder=3)
    ax.hlines(np.mean(vals), xpos - 0.22, xpos + 0.22, color=color, linewidth=1.8, zorder=4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    s_by_cond = endpoint_s(args.batch_name)
    acc_by_cond, base_acc, n_items = ethics_scores()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.6, 2.6), gridspec_kw={"wspace": 0.32})

    for i, c in enumerate(CONDS):
        strip(ax1, i, s_by_cond[c], COND_COLOR[c])
        strip(ax2, i, acc_by_cond[c], COND_COLOR[c])

    ax1.axhline(0, color="#BBBBBB", linewidth=0.8, zorder=1)
    ax1.set_ylim(-1.08, 1.08)
    ax1.set_ylabel("endpoint $S$  (+1 access, −1 provenance)", fontsize=8)
    ax1.set_title("trained axis", fontsize=9)

    # 95% binomial chance band around 0.5
    half = 1.96 * np.sqrt(0.25 / n_items)
    ax2.axhspan(0.5 - half, 0.5 + half, color="#EBEBEB", zorder=0)
    ax2.axhline(0.5, color="#BBBBBB", linewidth=0.8, zorder=1)
    ax2.axhline(base_acc, color="#222222", linewidth=0.9, linestyle=(0, (4, 2)), zorder=2)
    ax2.text(2.72, base_acc + 0.003, "base", fontsize=7, va="bottom", ha="right", color="#222222")
    ax2.set_ylim(0.40, 0.60)
    ax2.set_ylabel("ETHICS-cm accuracy", fontsize=8)
    ax2.set_title("general moral judgment", fontsize=9)

    for ax in (ax1, ax2):
        ax.set_xticks(range(len(CONDS)))
        ax.set_xticklabels([COND_LABEL[c] for c in CONDS], fontsize=7.5)
        ax.set_xlim(-0.5, len(CONDS) - 0.5 + 0.35)
        ax.tick_params(length=0)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color("#999999")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        out = PLOTS_DIR / f"ethics_specificity_{args.batch_name}.{ext}"
        fig.savefig(out)
        print(f"-> {out}")


if __name__ == "__main__":
    main()
