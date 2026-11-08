"""Figures for article 037: the three claims and the four constraints.

  fig1-claims.png/pdf     the three claims, with the evidence status of each after the referees
  fig2-principles.png/pdf the four constraints, separated by what kind each one is

Both are drawn from data in this script, so neither can drift from the text.

Usage: python scripts/make_article_037_figures.py
"""
from __future__ import annotations
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "articles", "037-figures")

# status after the referees: what survived, what was restricted, what was withdrawn
CLAIMS = [
    ("C1  our seven errors share a shape",
     "survives, restricted: TWO shapes, not one\n(the one-sentence check catches 3 of 7)", "#2e7d32"),
    ("C2  the designs can only imitate",
     "restricted twice: to what we ran, and to\nspecification vs selection (034 refutes the wide form)", "#ef6c00"),
    ("C3  the graph cannot reach a new ontology",
     "withdrawn to a statement of ignorance,\nwith an operational test added", "#c62828"),
]

PRINCIPLES = [
    ("P1", "constraints on flows, not parameters", "methodological preference", "#6a1b9a"),
    ("P2", "the environment is written and read by the agents", "a claim about the world", "#2e7d32"),
    ("P3", "the primary measure is within-cell", "a claim about the world + a measurement rule", "#1565c0"),
    ("P4", "novelty cannot come from a closed record", "a theorem, with assumptions", "#ef6c00"),
]


def fig_claims() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(CLAIMS) + 1.3)
    ax.axis("off")
    for i, (head, status, color) in enumerate(reversed(CLAIMS)):
        y = i + 0.8
        ax.add_patch(FancyBboxPatch((0.2, y), 4.2, 0.9, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.6, edgecolor="#37474f", facecolor="#eceff1"))
        ax.text(0.4, y + 0.45, head, fontsize=10, va="center", color="#212121", fontweight="bold")
        ax.add_patch(FancyBboxPatch((4.6, y), 5.2, 0.9, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.6, edgecolor=color, facecolor=color + "22"))
        ax.text(4.8, y + 0.45, status, fontsize=8.4, va="center", color=color)
    ax.text(2.3, len(CLAIMS) + 1.0, "the claim", fontsize=9.5, ha="center", fontweight="bold",
            color="#424242")
    ax.text(7.2, len(CLAIMS) + 1.0, "what two independent referees left of it", fontsize=9.5,
            ha="center", fontweight="bold", color="#424242")
    ax.set_title("Three claims and what survived review", fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout()
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig1-claims.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"fig1-claims written to {OUT}")


def fig_principles() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(PRINCIPLES) + 1.3)
    ax.axis("off")
    for i, (pid, text, kind, color) in enumerate(reversed(PRINCIPLES)):
        y = i + 0.8
        ax.add_patch(FancyBboxPatch((0.2, y), 0.9, 0.8, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.6, edgecolor=color, facecolor=color + "33"))
        ax.text(0.65, y + 0.4, pid, fontsize=12, ha="center", va="center", fontweight="bold",
                color=color)
        ax.add_patch(FancyBboxPatch((1.2, y), 4.6, 0.8, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.2, edgecolor="#b0bec5", facecolor="#fafafa"))
        ax.text(1.4, y + 0.4, text, fontsize=9.2, va="center", color="#212121")
        ax.add_patch(FancyBboxPatch((5.9, y), 3.9, 0.8, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.2, edgecolor=color, facecolor=color + "18"))
        ax.text(6.1, y + 0.4, kind, fontsize=9.0, va="center", color=color, fontweight="bold")
    ax.text(3.5, len(PRINCIPLES) + 1.0, "the constraint", fontsize=9.5, ha="center",
            fontweight="bold", color="#424242")
    ax.text(7.85, len(PRINCIPLES) + 1.0, "what kind of thing it is", fontsize=9.5, ha="center",
            fontweight="bold", color="#424242")
    ax.set_title("Four constraints, and only one of them is a claim a single experiment can refute",
                 fontsize=12.0, fontweight="bold", pad=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig2-principles.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"fig2-principles written to {OUT}")


if __name__ == "__main__":
    fig_claims()
    fig_principles()
