#!/usr/bin/env python3
"""Figure 1: per-seed flip slopegraph (sequential arms) + interleaved panel.

Approved prototype 2026-08-19 (user verdict: slopegraph + interleaved own panel,
no annotation, no second figure). Data: results/fig1_per_seed_data.csv, derived
from results/labeling/orderexp_matrix_v1-judge_labeled.csv (locked battery, n=10).

Usage: .venv/bin/python analysis/fig1_slopegraph.py
Writes: paper/figures/fig1_perseed_matrix.pdf (+ .png preview in results/plots/)
"""
import csv
from pathlib import Path

import figstyle
import matplotlib.pyplot as plt

figstyle.apply()

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "results/fig1_per_seed_data.csv")))
cell = {}
for r in rows:
    if r["S"] != "":
        cell[(r["condition"], r["seed"], r["stage"])] = (float(r["S"]), float(r["coherence"]))
seeds = sorted({r["seed"] for r in rows})

SEQ_STAGES = ["post_phase1", "pre_washout", "post_washout"]
INT_STAGES = ["pre_washout", "post_washout"]
XLABELS = {0: "after\nphase 1", 1: "after\nconflict", 2: "after\nwashout"}

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(7.0, 3.1), sharey=True,
    gridspec_kw={"width_ratios": [3, 2], "wspace": 0.10},
)


def draw_arm(ax, cond, stages, xs, color, alpha=0.45):
    for s in seeds:
        pts = [(x, *cell[(cond, s, st)]) for x, st in zip(xs, stages) if (cond, s, st) in cell]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=1.0,
                alpha=alpha, zorder=2, solid_capstyle="round")
        for x, y, coh in pts:
            ax.plot(x, y, marker="o", ms=4.2, mew=1.0, mec=color,
                    mfc="white" if coh < 0.5 else color, alpha=0.9, zorder=3)
    mx = list(xs)
    my = [sum(cell[(cond, s, st)][0] for s in seeds) / len(seeds) for st in stages]
    ax.plot(mx, my, color=color, lw=2.4, zorder=4)
    return my


for ax in (ax1, ax2):
    ax.axhline(0, color=figstyle.GREY_D, lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.set_ylim(-1.18, 1.18)
    ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])

mA = draw_arm(ax1, "A_first", SEQ_STAGES, [0, 1, 2], figstyle.PURPLE_D)
mB = draw_arm(ax1, "B_first", SEQ_STAGES, [0, 1, 2], figstyle.TEAL_D)
ax1.set_title("sequential arms")
ax1.set_ylabel("policy score S")
ax1.set_xticks([0, 1, 2], [XLABELS[x] for x in [0, 1, 2]])
ax1.set_xlim(-0.25, 2.85)
ax1.text(2.12, mA[-1], f"A-first {mA[-1]:+.2f}", color=figstyle.PURPLE_D, va="center")
ax1.text(2.12, mB[-1], f"B-first {mB[-1]:+.2f}", color=figstyle.TEAL_D, va="center")
ax1.text(-0.22, 0.045, "S = 0", color=figstyle.GREY_D, fontsize=7.5, va="bottom")
ax1.text(0.08, 1.06, "access pole", color=figstyle.INK, fontsize=7.5, va="center")
ax1.text(0.08, -1.06, "provenance pole", color=figstyle.INK, fontsize=7.5, va="center")

mI = draw_arm(ax2, "interleaved", INT_STAGES, [1, 2], figstyle.GREY_D, alpha=0.55)
ax2.set_title("interleaved")
ax2.set_xticks([1, 2], [XLABELS[x] for x in [1, 2]])
ax2.set_xlim(0.72, 2.95)
ax2.text(2.12, mI[-1], f"mean {mI[-1]:+.2f}", color=figstyle.GREY_D, va="center", fontsize=8)
ax2.tick_params(axis="y", length=0)

fig.text(0.995, 0.965, "open marker: <50% decisive", ha="right",
         color=figstyle.GREY_D, fontsize=7.5)

(ROOT / "paper/figures").mkdir(parents=True, exist_ok=True)
fig.savefig(ROOT / "paper/figures/fig1_perseed_matrix.pdf")
fig.savefig(ROOT / "results/plots/fig1_perseed_matrix.png", dpi=200)
print("wrote paper/figures/fig1_perseed_matrix.pdf + results/plots/fig1_perseed_matrix.png")
