"""Project figure style: user-anchored 'clean mono' aesthetic (2026-08-18 screenshot).

DNA: monospace type throughout; muted purple/teal data colors with darker edges;
grey for reference lines and washout; frameless legend row ABOVE the axes; faint
dotted grid inside a thin full box; airy margins; no bold anywhere.
"""
import matplotlib.pyplot as plt

PURPLE, PURPLE_D = "#9678B6", "#5F4B7F"   # A-first  (fill, edge/line)
TEAL, TEAL_D = "#7CB7B3", "#3F7370"       # B-first
GREY, GREY_D = "#C9C9C9", "#8A8A8A"       # washout / reference
INK = "#333333"


def apply(scale=1.0):
    plt.rcParams.update({
        "font.family": "monospace",
        "font.monospace": ["Courier New", "Courier", "DejaVu Sans Mono"],
        "font.size": 9 * scale, "axes.labelsize": 9.5 * scale,
        "axes.titlesize": 9.5 * scale, "xtick.labelsize": 8.5 * scale,
        "ytick.labelsize": 8.5 * scale, "legend.fontsize": 9 * scale,
        "text.color": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK,
        "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.edgecolor": "#666666", "axes.linewidth": 0.9,
        "axes.spines.top": True, "axes.spines.right": True,
        "axes.grid": True, "grid.color": "#DDDDDD", "grid.linestyle": ":",
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "lines.solid_capstyle": "round",
    })
