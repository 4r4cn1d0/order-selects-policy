"""Project figure style: user-anchored 'clean mono' aesthetic (2026-08-18 screenshot).

DNA: monospace type throughout; muted purple/teal data colors with darker edges;
grey for reference lines and washout; frameless legend row ABOVE the axes; faint
dotted grid inside a thin full box; airy margins; no bold anywhere.
"""
import matplotlib.pyplot as plt

# Line colors validated 2026-08-20 (dataviz skill validate_palette.js, light mode):
# PURPLE_D/TEAL_D pass CVD separation (deutan 13.4, tritan 13.9), normal-vision
# floor (18.6), lightness band, contrast. Accepted exception: chroma floor --
# the muted aesthetic is deliberate and every series is direct-text-labeled
# (validator-sanctioned secondary encoding). Previous pair (#5F4B7F/#3F7370)
# FAILED the normal-vision floor (13.3 < 15).
PURPLE, PURPLE_D = "#9678B6", "#5A4187"   # A-first  (fill, edge/line)
TEAL, TEAL_D = "#7CB7B3", "#2E7A70"       # B-first
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
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlelocation": "left",
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#DDDDDD", "grid.linestyle": ":",
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "lines.solid_capstyle": "round",
    })
