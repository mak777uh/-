"""make_article_034_figures.py — the figure of article 034, built from the artifact only.

One figure, two panels, both read from `morphogenesis/experiments/E09_pond/s89_e14b_20seeds.json`:

  A. the favourable share in the last window, one bar per arm, the control first;
  B. the paired difference against the control with the number of seeds out of twenty that agree in sign.

Writes PNG (reading) and PDF (typesetting) into `articles/034-figures/`.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
OUT = os.path.join(ROOT, "articles", "034-figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

with open(os.path.join(POND, "s89_e14b_20seeds.json"), encoding="utf-8") as fh:
    doc = json.load(fh)

ROWS = doc["rows"]
ARMS = ["none", "local", "wave", "rule", "ab"]
LABELS = {"none": "control", "local": "where\n(map)", "wave": "when\n(clock)", "rule": "rules\n(upkeep)",
          "ab": "both"}
COLOURS = {"none": "#6b6b6b", "local": "#1f6fb4", "wave": "#c9a227", "rule": "#2a9d5c", "ab": "#8e44ad"}


def last_window(arm):
    """The favourable share in the last window of every seed of one arm."""
    values = []
    for row in ROWS:
        if row["arm"] == arm and row["windows"]:
            values.append(row["windows"][-1]["trait_mean"])
    return values


def mean(values):
    return sum(values) / len(values) if values else None


control = {row["seed"]: row["windows"][-1]["trait_mean"] for row in ROWS if row["arm"] == "none" and row["windows"]}
means = {arm: mean(last_window(arm)) for arm in ARMS}
paired = {}
positive = {}
for arm in ARMS:
    diffs = []
    for row in ROWS:
        if row["arm"] == arm and row["windows"] and row["seed"] in control:
            diffs.append(row["windows"][-1]["trait_mean"] - control[row["seed"]])
    paired[arm] = mean(diffs)
    positive[arm] = (sum(1 for d in diffs if d > 0), len(diffs))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1, 1.15]})

ax1.bar(range(len(ARMS)), [means[a] for a in ARMS], color=[COLOURS[a] for a in ARMS], width=0.62)
ax1.set_xticks(range(len(ARMS)), [LABELS[a] for a in ARMS])
ax1.set_ylabel("share in the favourable half (last window)")
ax1.set_title("A. The same dose of signal, in three places", loc="left")
for i, arm in enumerate(ARMS):
    ax1.text(i, means[arm] + 0.002, f"{means[arm]:.3f}", ha="center", fontsize=7.5)

bars = [paired[a] for a in ARMS[1:]]
ax2.bar(range(len(bars)), bars, color=[COLOURS[a] for a in ARMS[1:]], width=0.62)
ax2.axhline(0, color="black", lw=0.9, ls=":")
ax2.set_xticks(range(len(bars)), [LABELS[a] for a in ARMS[1:]])
ax2.set_ylabel("paired difference against the control")
ax2.set_title("B. How much it buys, and how many seeds agree", loc="left")
for i, arm in enumerate(ARMS[1:]):
    ok, total = positive[arm]
    ax2.text(i, bars[i] + (0.0015 if bars[i] >= 0 else -0.003), f"{bars[i]:+.4f}\n{ok}/{total}",
             ha="center", va="bottom" if bars[i] >= 0 else "top", fontsize=7.5)

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"fig1-where-the-signal-acts.{ext}"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("wrote fig1-where-the-signal-acts.png / .pdf")
