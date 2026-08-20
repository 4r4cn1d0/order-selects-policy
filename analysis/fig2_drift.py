#!/usr/bin/env python3
"""Figure 2: drift-time trajectory, seed 3001, checkpoints every 4 optimizer steps.

Same visual system as Figure 1 (figstyle; approved 2026-08-19). Development
battery (8 scenarios), seed 3001 -- provenance disclosed in the caption.
Data: results/labeling/drift_seed3001_labeled.csv (+ _interleaved_).

Usage: .venv/bin/python analysis/fig2_drift.py
Writes: paper/figures/fig2_drift_seed3001.pdf (+ .png preview in results/plots/)
"""
import csv
from collections import defaultdict
from pathlib import Path

import figstyle
import matplotlib.pyplot as plt

figstyle.apply()

ROOT = Path(__file__).resolve().parent.parent
D = {"access-consistent": 1, "provenance-consistent": -1}


def load(fname):
    cell = defaultdict(list)
    for r in csv.DictReader(open(ROOT / "results/labeling" / fname)):
        cell[(r["condition"], int(r["checkpoint_boundary"].split("_")[1]))].append(r["human_label"])
    out = {}
    for k, labels in cell.items():
        dec = [D[l] for l in labels if l in D]
        out[k] = (sum(dec) / len(dec) if dec else None, len(dec) / len(labels))
    return out


seq = load("drift_seed3001_labeled.csv")
inter = load("drift_interleaved_seed3001_labeled.csv")
STEPS = list(range(4, 37, 4))

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(7.0, 3.0), sharey=True,
    gridspec_kw={"width_ratios": [1, 1], "wspace": 0.08},
)


def draw(ax, data, cond, color):
    xs, ys = [], []
    for st in STEPS:
        S, coh = data[(cond, st)]
        if S is None:
            ax.text(st, 0.06, "0/8\ndecisive", fontsize=6.5, color=color,
                    ha="center", va="bottom")
            if xs:
                ax.plot(xs, ys, color=color, lw=1.8, zorder=2)
            xs, ys = [], []
            continue
        xs.append(st)
        ys.append(S)
        ax.plot(st, S, marker="o", ms=4.4, mew=1.0, mec=color,
                mfc="white" if coh < 0.5 else color, zorder=3)
    ax.plot(xs, ys, color=color, lw=1.8, zorder=2)


for ax, bounds in [(ax1, (12.5, 24.5)), (ax2, (24.5,))]:
    ax.axhline(0, color=figstyle.GREY_D, lw=0.8, ls=(0, (4, 3)), zorder=1)
    for b in bounds:
        ax.axvline(b, color=figstyle.GREY, lw=0.9, ls=(0, (2, 2)), zorder=1)
    ax.set_ylim(-1.22, 1.22)
    ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax.set_xticks([4, 12, 20, 28, 36])
    ax.set_xlim(2, 40)
    ax.set_xlabel("optimizer step")

draw(ax1, seq, "A_first", figstyle.PURPLE_D)
draw(ax1, seq, "B_first", figstyle.TEAL_D)
ax1.set_title("sequential arms")
ax1.set_ylabel("policy score S")
ax1.text(8, 1.12, "phase 1", fontsize=7, color=figstyle.INK, ha="center")
ax1.text(18.5, 1.12, "phase 2", fontsize=7, color=figstyle.INK, ha="center")
ax1.text(30.5, 1.12, "washout", fontsize=7, color=figstyle.INK, ha="center")
ax1.set_xlim(2, 46)
ax1.text(37.5, seq[("A_first", 36)][0], "A-first", color=figstyle.PURPLE_D,
         va="center", fontsize=8)
ax1.text(37.5, seq[("B_first", 36)][0], "B-first", color=figstyle.TEAL_D,
         va="center", fontsize=8)

draw(ax2, inter, "interleaved", figstyle.GREY_D)
ax2.set_title("interleaved")
ax2.text(13, 1.12, "shuffled A+B", fontsize=7, color=figstyle.INK, ha="center")
ax2.text(30.5, 1.12, "washout", fontsize=7, color=figstyle.INK, ha="center")
ax2.tick_params(axis="y", length=0)

fig.text(0.995, 0.965, "open marker: <50% decisive", ha="right",
         color=figstyle.GREY_D, fontsize=7.5)

fig.savefig(ROOT / "paper/figures/fig2_drift_seed3001.pdf")
fig.savefig(ROOT / "results/plots/fig2_drift_seed3001.png", dpi=200)
print("wrote fig2_drift_seed3001.{pdf,png}")
