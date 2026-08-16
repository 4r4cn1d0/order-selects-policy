#!/usr/bin/env python3
"""
Drift-time figure: value policy S vs optimizer step, from dense per-step checkpoints
(train/train.py --checkpoint-every). Shows WHEN each value installs, flips, and what the
neutral washout does — the trajectory behind the 3-point boundary figure.

Open markers = low-coherence cells (<50% decisive outputs) — plotted, never hidden, but
visually flagged so endpoint wobble isn't over-read (labeling_protocol.md step 5).

Usage:
    python analysis/orderexp_drift_plot.py --batch-name drift_seed3001
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
LABELING_DIR = ROOT / "results" / "labeling"
PLOTS_DIR = ROOT / "results" / "plots"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.labelsize": 10, "legend.fontsize": 8.5, "legend.frameon": False,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.15, "lines.linewidth": 1.8, "lines.markersize": 6,
})
STYLE = {"A_first": ("#E76F51", "o", "A first (A→B→C)"),
          "B_first": ("#0072B2", "s", "B first (B→A→C)")}
PHASE_BOUNDARIES = (12, 24)  # 192 records/phase ÷ 16/step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-name", required=True)
    args = ap.parse_args()

    cells = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(open(LABELING_DIR / f"{args.batch_name}_labeled.csv")):
        if r["checkpoint_boundary"].startswith("step_"):
            step = int(r["checkpoint_boundary"].split("_")[1])
            cells[r["condition"]][step].append(r["human_label"])

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.axvspan(PHASE_BOUNDARIES[1], 36.9, color="gray", alpha=0.08)
    for b in PHASE_BOUNDARIES:
        ax.axvline(b + 0.5, color="black", linewidth=0.7, linestyle="--", alpha=0.5)
    ax.axhline(0, color="black", linewidth=0.6, alpha=0.4)

    for cond, (color, marker, label) in STYLE.items():
        steps = sorted(cells[cond])
        xs, ys, coh = [], [], []
        for s in steps:
            labels = cells[cond][s]
            dec = [l for l in labels if l in ("access-consistent", "provenance-consistent")]
            if not dec:
                continue
            xs.append(s)
            ys.append(sum(1 if l == "access-consistent" else -1 for l in dec) / len(dec))
            coh.append(len(dec) / len(labels))
        ax.plot(xs, ys, color=color, label=label, zorder=2)
        for x, y, c in zip(xs, ys, coh):
            ax.plot(x, y, marker, color=color, zorder=3,
                    markerfacecolor=color if c >= 0.5 else "white")

    ax.text(6.5, 1.09, "phase 1", ha="center", fontsize=8.5)
    ax.text(18.5, 1.09, "phase 2 (conflict)", ha="center", fontsize=8.5)
    ax.text(30.5, 1.09, "neutral washout", ha="center", fontsize=8.5, color="gray")
    ax.set_xlabel("optimizer step")
    ax.set_ylabel("S  (+1 access, −1 provenance)")
    ax.set_ylim(-1.25, 1.25)
    ax.set_xlim(2, 38)
    ax.legend(loc="lower left")
    ax.set_title("When the value flips — policy vs training step (seed 3001)")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        out = PLOTS_DIR / f"drift_{args.batch_name}.{ext}"
        fig.savefig(out)
        print(f"-> {out}")


if __name__ == "__main__":
    main()
