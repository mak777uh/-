"""make_article_035_figures.py — the figure of article 035, built from the artifact only.

One figure, two panels, both read from `morphogenesis/experiments/E09_pond/s49_e1_density_axis.json`:

  A. the boundary as a surface: gap (greedy − baseline) against colony density, one line per recovery rate, with the
     zero line and the point where each line crosses it;
  B. the same cells as a heat strip, so the reader sees at a glance that the whole slow-recovery row is pale and the
     medium and fast rows are uniformly positive.

Writes PNG (reading) and PDF (typesetting) into `articles/035-figures/`.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
OUT = os.path.join(ROOT, "articles", "035-figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

with open(os.path.join(POND, "s49_e1_density_axis.json"), encoding="utf-8") as fh:
    doc = json.load(fh)

ROWS = doc["rows"]
DENSITIES = doc["densities"]
REGEN = doc["regen"]
TOTAL = 32 * 32


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def gap(density, regen):
    base = mean([r["overall"] for r in ROWS if r["arm"] == "baseline"
                 and r["density_cells"] == density and r["resource_regen"] == regen])
    greedy = mean([r["overall"] for r in ROWS if r["arm"] == "greedy"
                   and r["density_cells"] == density and r["resource_regen"] == regen])
    return greedy - base


def seeds_positive(density, regen):
    positive = total = 0
    for seed in sorted({r["seed"] for r in ROWS}):
        b = [r["overall"] for r in ROWS if r["seed"] == seed and r["arm"] == "baseline"
             and r["density_cells"] == density and r["resource_regen"] == regen]
        g = [r["overall"] for r in ROWS if r["seed"] == seed and r["arm"] == "greedy"
             and r["density_cells"] == density and r["resource_regen"] == regen]
        if b and g:
            total += 1
            positive += 1 if g[0] > b[0] else 0
    return positive, total


share = [100 * d / TOTAL for d in DENSITIES]
colours = {0.01: "#c0392b", 0.02: "#1f6fb4", 0.04: "#2a9d5c"}
labels = {0.01: "slow recovery (0.01)", 0.02: "medium (0.02)", 0.04: "fast (0.04)"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.5), gridspec_kw={"width_ratios": [1.35, 1]})

for regen in REGEN:
    ys = [gap(d, regen) for d in DENSITIES]
    ax1.plot(share, ys, "o-", color=colours[regen], label=labels[regen], markersize=5)
    for x, y in zip(share, ys):
        if y < 0:
            ax1.annotate(f"{y:+.3f}", (x, y), textcoords="offset points", xytext=(0, -12),
                         ha="center", fontsize=7.5, color=colours[regen])
ax1.axhline(0, color="black", lw=0.9, ls=":")
ax1.set_xlabel("colony density (% of the 1024 cells)")
ax1.set_ylabel("greedy − baseline (share in the favourable half)")
ax1.set_title("A. Movement pays at every density unless recovery is slow", loc="left")
ax1.legend(frameon=False, loc="lower left")

# panel B: the twelve cells as a strip, one row per recovery rate
grid = [[gap(d, regen) for d in DENSITIES] for regen in REGEN]
vmax = max(abs(v) for row in grid for v in row)
image = ax2.imshow(grid, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
ax2.set_xticks(range(len(DENSITIES)), [f"{s:.1f} %" for s in share])
ax2.set_yticks(range(len(REGEN)), [labels[r].split(" (")[0] for r in REGEN])
for i, regen in enumerate(REGEN):
    for j, d in enumerate(DENSITIES):
        positive, total = seeds_positive(d, regen)
        ax2.text(j, i, f"{grid[i][j]:+.3f}\n{positive}/{total}", ha="center", va="center", fontsize=7.5)
ax2.set_xlabel("colony density")
ax2.set_title("B. The same cells, and how many seeds agree", loc="left")
ax2.grid(False)
fig.colorbar(image, ax=ax2, fraction=0.046, pad=0.03, label="gap")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"fig1-the-boundary.{ext}"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("wrote fig1-the-boundary.png / .pdf")
