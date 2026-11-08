"""Figures for article 036: the layer diagram and the defect-attribution table.

Two figures, both drawn from data that lives in the repository, so neither can drift from the text:

  fig1-layers.png/pdf   the eight layers of the bench, with what each one proves and what it only measures
  fig2-defects.png/pdf  the six defects of 08.11 and which instrument found each

Usage: python scripts/make_article_036_figures.py
"""
from __future__ import annotations
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "articles", "036-figures")

# the eight layers; `provable` is the herness level: A/B are proof, C is measurement, "-" is neither
LAYERS = [
    ("world", "the simulation: resource field, cells, energy, division", "-"),
    ("wrapper", "lock, manifest with commit and environment, log", "C"),
    ("artifacts", "raw per-run JSON, one file per run", "-"),
    ("reports", "human interpretation, never the source of numbers", "-"),
    ("policy", "what an agent may do, as data", "A"),
    ("proof", "9 theorems about the policy (Lean)", "A"),
    ("mediator", "the decision, in three implementations", "B"),
    ("gates", "29 checks, each with a probe that plants a defect", "C"),
]

DEFECTS = [
    ("a Lean proof did not compile (simp)", "Lean"),
    ("a Lean proof did not compile (rewrite)", "Lean"),
    ("generated Lean: no space before the bracket", "Lean"),
    ("check_autonomy never looked at the owner", "probe P2"),
    ("probe P2 grepped output, planted nothing", "review of the probe"),
    ("all 7 cases put into one policy", "the disagreement itself"),
]

LEVEL_COLOR = {"A": "#2e7d32", "B": "#1565c0", "C": "#ef6c00", "-": "#9e9e9e"}
LEVEL_LABEL = {"A": "A: proved", "B": "B: proved for small code", "C": "C: measured, not proved",
               "-": "neither (data)"}


def fig_layers() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(LAYERS) + 1.2)
    ax.axis("off")

    for i, (name, what, level) in enumerate(reversed(LAYERS)):
        y = i + 0.6
        color = LEVEL_COLOR[level]
        box = FancyBboxPatch((0.3, y), 9.4, 0.72, boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=1.6, edgecolor=color, facecolor=color + "22")
        ax.add_patch(box)
        ax.text(0.55, y + 0.46, name, fontsize=11, fontweight="bold", va="center", color="#212121")
        ax.text(0.55, y + 0.20, what, fontsize=8.6, va="center", color="#424242")
        ax.text(9.45, y + 0.36, LEVEL_LABEL[level], fontsize=8.2, ha="right", va="center", color=color)

    # the arrow that makes the point: the proof is at the top, the measurement at the bottom, and the
    # question of the paper is whether the bottom agrees with the top
    ax.annotate("", xy=(9.75, 0.6), xytext=(9.75, len(LAYERS) + 0.4),
                arrowprops=dict(arrowstyle="<->", color="#616161", lw=1.4))
    ax.text(9.95, (len(LAYERS) + 1.0) / 2, "the bridge\n(script, not a promise)", rotation=90,
            fontsize=7.6, ha="center", va="center", color="#616161")

    ax.set_title("The bench in eight layers: what is proved and what is only measured",
                 fontsize=12.5, fontweight="bold", pad=14)
    fig.tight_layout()
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig1-layers.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"fig1-layers.png/pdf written to {OUT}")


def fig_defects() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(DEFECTS) + 1.4)
    ax.axis("off")

    finder_color = {"Lean": "#1565c0", "probe P2": "#ef6c00",
                    "review of the probe": "#6a1b9a", "the disagreement itself": "#c62828"}

    for i, (defect, finder) in enumerate(reversed(DEFECTS)):
        y = i + 0.7
        color = finder_color[finder]
        ax.add_patch(FancyBboxPatch((0.3, y), 6.4, 0.62, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    linewidth=1.3, edgecolor="#bdbdbd", facecolor="#fafafa"))
        ax.text(0.5, y + 0.31, defect, fontsize=9, va="center", color="#212121")
        ax.add_patch(FancyBboxPatch((6.9, y), 2.9, 0.62, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    linewidth=1.3, edgecolor=color, facecolor=color + "22"))
        ax.text(8.35, y + 0.31, finder, fontsize=9, ha="center", va="center", color=color,
                fontweight="bold")

    ax.text(3.55, len(DEFECTS) + 1.05, "defect (six in one day, five of them the authors')",
            fontsize=9.5, ha="center", fontweight="bold", color="#424242")
    ax.text(8.35, len(DEFECTS) + 1.05, "found by", fontsize=9.5, ha="center", fontweight="bold",
            color="#424242")

    ax.set_title("What the apparatus caught, and which instrument caught it",
                 fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig2-defects.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"fig2-defects.png/pdf written to {OUT}")


if __name__ == "__main__":
    fig_layers()
    fig_defects()
