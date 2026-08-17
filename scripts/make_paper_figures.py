#!/usr/bin/env python3
"""Paper figures 1-3 in the project figure style (analysis/figstyle.py).

Uncertainty per the Mouret/Rougier school: shaded 95% CI bands on curves
(fill_between, not capped whiskers); bare capless interval lines on the forest;
raw per-seed data visible everywhere.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import figstyle  # noqa: E402
from figstyle import GREY, GREY_D, INK, PURPLE, PURPLE_D, TEAL, TEAL_D  # noqa: E402

figstyle.apply()
OUT = ROOT / "results" / "plots" / "proposals"
DEC = {"access-consistent": 1, "provenance-consistent": -1}


def load(p):
    rows = list(csv.DictReader(open(p)))
    cells = defaultdict(list)
    for r in rows:
        cells[(r["condition"], r["seed"], r["checkpoint_boundary"])].append(r["human_label"])
    return cells


def S(cells, cond, sd, stage):
    d = [DEC[l] for l in cells.get((cond, sd, stage), []) if l in DEC]
    return sum(d) / len(d) if d else None


def arc(cells, cond, stages):
    seeds = sorted({s for (c, s, _) in cells if c == cond})
    M = [[S(cells, cond, sd, st) for st in stages] for sd in seeds]
    return np.array([r for r in M if all(v is not None for v in r)])


pyth = load(ROOT / "results/labeling/orderexp_matrix_v1-judge_labeled.csv")
fams = [("Qwen2.5-1.5B", load(ROOT / "results/labeling/family_qwen_v1-judge_labeled.csv")),
        ("SmolLM2-1.7B", load(ROOT / "results/labeling/family_smollm_v1-judge_labeled.csv")),
        ("OLMo-2-1B", load(ROOT / "results/labeling/family_olmo_v1-judge_labeled.csv"))]
ST = ["post_phase1", "pre_washout", "post_washout"]
XL = ["phase 1", "pre-wash", "endpoint"]


def draw_arc(ax, cells):
    for cond, lc, fc in [("A_first", PURPLE_D, PURPLE), ("B_first", TEAL_D, TEAL)]:
        M = arc(cells, cond, ST)
        for row in M:
            ax.plot([0, 1, 2], row, color=lc, alpha=0.15, lw=0.8)
        m = M.mean(0)
        band = 1.96 * M.std(0, ddof=1) / np.sqrt(len(M))
        ax.fill_between([0, 1, 2], m - band, m + band, color=fc, alpha=0.35, lw=0)
        ax.plot([0, 1, 2], m, color=lc, lw=1.9, marker="o", ms=6,
                mfc=fc, mec=lc, mew=1.1)
    ax.axhline(0, color=GREY_D, lw=1.0, ls="--")
    ax.set_xlim(-0.3, 2.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(XL, fontsize=8)
    ax.set_yticks([-1, -0.5, 0, 0.5, 1])


LEG = [Line2D([], [], marker="o", ls="-", color=PURPLE_D, mfc=PURPLE, mec=PURPLE_D, ms=7, lw=1.8, label="A-first"),
       Line2D([], [], marker="o", ls="-", color=TEAL_D, mfc=TEAL, mec=TEAL_D, ms=7, lw=1.8, label="B-first")]

# ---------- Figure 1 ----------
fig = plt.figure(figsize=(6.6, 3.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.30,
                      left=0.02, right=0.97, top=0.83, bottom=0.13)
axs = fig.add_subplot(gs[0, 0])
axs.axis("off")
axs.set_xlim(0, 10)
axs.set_ylim(-0.7, 3.7)
x0, seg, hh = 2.15, 2.45, 0.66
tracks = [("A-first", [(PURPLE, PURPLE_D, "A: access"), (TEAL, TEAL_D, "B: prov."), (GREY, GREY_D, "C: wash")], 2.7),
          ("B-first", [(TEAL, TEAL_D, "B: prov."), (PURPLE, PURPLE_D, "A: access"), (GREY, GREY_D, "C: wash")], 1.55),
          ("interleaved", None, 0.4)]
for name, segs, y in tracks:
    axs.text(x0 - 0.2, y + hh / 2, name, ha="right", va="center", fontsize=8.5)
    if segs is None:
        for k in range(12):
            axs.add_patch(Rectangle((x0 + k * (2 * seg) / 12, y), (2 * seg) / 12, hh,
                                     facecolor=PURPLE if k % 2 else TEAL, edgecolor="none"))
        axs.add_patch(Rectangle((x0, y), 2 * seg, hh, fill=False, edgecolor="white", lw=1.2))
        axs.text(x0 + seg, y + hh / 2, "A+B shuffled", ha="center", va="center", fontsize=7.5, color="white")
        axs.add_patch(Rectangle((x0 + 2 * seg, y), seg, hh, facecolor=GREY, edgecolor=GREY_D, lw=0.8))
        axs.text(x0 + 2.5 * seg, y + hh / 2, "C: wash", ha="center", va="center", fontsize=7.5)
    else:
        for k, (fc, ec, lab) in enumerate(segs):
            axs.add_patch(Rectangle((x0 + k * seg, y), seg, hh, facecolor=fc, edgecolor=ec, lw=0.8))
            axs.text(x0 + (k + 0.5) * seg, y + hh / 2, lab, ha="center", va="center",
                     fontsize=7.5, color="white" if fc != GREY else INK)
for k, lab in enumerate(XL):
    xx = x0 + (k + 1) * seg
    axs.add_patch(Polygon([(xx, 3.62), (xx - 0.1, 3.4), (xx + 0.1, 3.4)], color=INK))
    axs.text(xx, 3.7, lab, ha="center", va="bottom", fontsize=8)
axs.text(x0, -0.62, "identical data; only order differs", fontsize=8, color=GREY_D)
axs.text(0.1, 3.55, "(a)", fontsize=10)
axp = fig.add_subplot(gs[0, 1])
draw_arc(axp, pyth)
axp.set_ylabel("value score S")
axp.set_title("(b) pythia-410M  (n=10)", pad=8)
fig.legend(handles=LEG, ncol=2, loc="upper right", bbox_to_anchor=(0.965, 1.00), columnspacing=2.0)
fig.savefig(OUT / "fig1_design_and_result.png")
fig.savefig(OUT / "fig1_design_and_result.pdf")
plt.close(fig)
print("-> fig1")

# ---------- Figure 2 ----------
fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.5), sharey=True,
                          gridspec_kw={"wspace": 0.14, "left": 0.09, "right": 0.985,
                                       "top": 0.82, "bottom": 0.16})
for k, (name, cells) in enumerate(fams):
    draw_arc(axes[k], cells)
    axes[k].set_title(f"({chr(97 + k)}) {name}  (n=5)", pad=7)
    if k:
        plt.setp(axes[k].get_yticklabels(), visible=False)
axes[0].set_ylabel("value score S")
fig.legend(handles=LEG, ncol=2, loc="upper right", bbox_to_anchor=(0.985, 1.02), columnspacing=2.0)
fig.savefig(OUT / "fig2_families.png")
fig.savefig(OUT / "fig2_families.pdf")
plt.close(fig)
print("-> fig2")

# ---------- Figure 3 ----------
def paired(cells):
    seeds = sorted({s for (c, s, _) in cells if c == "A_first"})
    out = []
    for sd in seeds:
        a, b = S(cells, "A_first", sd, "post_washout"), S(cells, "B_first", sd, "post_washout")
        if a is not None and b is not None:
            out.append(a - b)
    return np.array(out)


entries = [("pythia-410M", paired(pyth), False, "p = 0.023"),
           ("Qwen2.5-1.5B", paired(fams[0][1]), False, "p = 0.031"),
           ("SmolLM2-1.7B", paired(fams[1][1]), True, "saturated"),
           ("OLMo-2-1B", paired(fams[2][1]), True, "saturated")]
fig, axc = plt.subplots(figsize=(6.0, 2.6),
                         gridspec_kw={"left": 0.02, "right": 0.98, "top": 0.97, "bottom": 0.21})
ys = np.arange(len(entries), 0, -1) * 0.9
for (name, d, sat, note), y in zip(entries, ys):
    m, ci = d.mean(), 1.96 * d.std(ddof=1) / np.sqrt(len(d))
    lc, fc = (GREY_D, GREY) if sat else (TEAL_D, TEAL)
    # bare capless interval (Rougier school), raw seeds above, mean dot on top
    axc.plot([m - ci, m + ci], [y, y], color=lc, lw=2.6, solid_capstyle="butt", zorder=2)
    axc.scatter([m], [y], s=52, facecolor=fc, edgecolor=lc, lw=1.2, zorder=4)
    axc.scatter(d, np.full_like(d, y) + 0.22, s=13, facecolor=fc, edgecolor=lc,
                lw=0.7, alpha=0.75, zorder=3)
    axc.text(-1.95, y, name, ha="left", va="center", fontsize=8.5,
             color=GREY_D if sat else INK)
    axc.text(1.02, y, note, ha="left", va="center", fontsize=8, color=GREY_D if sat else INK)
inf = np.concatenate([d for (_, d, sat, _) in entries if not sat])
pm, pci = inf.mean(), 1.96 * inf.std(ddof=1) / np.sqrt(len(inf))
py0 = ys[-1] - 0.8
axc.fill([pm - pci, pm, pm + pci, pm], [py0, py0 + 0.23, py0, py0 - 0.23],
         facecolor=PURPLE, edgecolor=PURPLE_D, lw=1.0, zorder=3)
axc.text(-1.95, py0, "pooled", ha="left", va="center", fontsize=8.5)
axc.axvline(0, color=GREY_D, lw=1.0, ls="--")
axc.set_xlim(-2.0, 1.55)
axc.set_ylim(py0 - 0.55, ys[0] + 0.6)
axc.set_yticks([])
axc.set_xticks(np.arange(-1.5, 1.01, 0.5))
axc.set_xlabel("paired endpoint difference (A-first - B-first); dots: seeds")
axc.grid(axis="y", visible=False)
fig.savefig(OUT / "fig3_forest.png")
fig.savefig(OUT / "fig3_forest.pdf")
plt.close(fig)
print("-> fig3")
