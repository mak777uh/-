"""make_article_033_figures.py — the figure of article 033, built from the artifacts only.

One figure, two panels:

  A. what the world discriminates on: the probability of surviving a 20-step horizon in the low and the high
     quartile of each quantity, from `s55_e7_full.json` (the table of §2), with the replication of
     `s58_e7_replication.json` shown as the outline of the same bars;
  B. cost versus selection: the paired difference (heritable − fixed) at three trait prices in two zones, from
     `s91_e15_full.json`, with the zero-price arm first.

Writes PNG (reading) and PDF (typesetting) into `articles/033-figures/`.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
OUT = os.path.join(ROOT, "articles", "033-figures")
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


def load(name):
    with open(os.path.join(POND, name), encoding="utf-8") as fh:
        return json.load(fh)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


# ---------------------------------------------------------------- panel A: what the world discriminates on
main = load("s55_e7_full.json")["table"]
repl = load("s58_e7_replication.json")["table"]
QUANTITIES = ["energy", "age", "density", "rich"]
LABELS = {"energy": "energy", "age": "age", "density": "local density", "rich": "richness of the cell"}

low = [main[q]["survive"]["p_low"] for q in QUANTITIES]
high = [main[q]["survive"]["p_high"] for q in QUANTITIES]
low_r = [repl[q]["survive"]["p_low"] for q in QUANTITIES]
high_r = [repl[q]["survive"]["p_high"] for q in QUANTITIES]

# ---------------------------------------------------------------- panel B: cost versus selection
sweep = load("s91_e15_full.json")["rows"]
ZONES = ["rich", "poor"]
PRICES = [0.0, 0.06, 0.6]
COLOURS = {"rich": "#1f6fb4", "poor": "#c0392b"}


def paired(zone, price):
    values = []
    for seed in sorted({r["seed"] for r in sweep}):
        her = [r for r in sweep if r["seed"] == seed and r["arm"] == "heritable"
               and r["zone_name"] == zone and abs(r["rule_strength"] - price) < 1e-9]
        fix = [r for r in sweep if r["seed"] == seed and r["arm"] == "fixed"
               and r["zone_name"] == zone and abs(r["rule_strength"] - price) < 1e-9]
        if her and fix and her[0]["windows"] and fix[0]["windows"]:
            values.append(her[0]["windows"][-1]["trait_mean"] - fix[0]["windows"][-1]["trait_mean"])
    return mean(values)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1.05, 1]})

x = list(range(len(QUANTITIES)))
width = 0.36
ax1.bar([i - width / 2 for i in x], low, width, label="low quartile", color="#9aa7b4")
ax1.bar([i + width / 2 for i in x], high, width, label="high quartile", color="#1f6fb4")
ax1.scatter([i - width / 2 for i in x], low_r, marker="_", s=180, color="black", label="replication", zorder=3)
ax1.scatter([i + width / 2 for i in x], high_r, marker="_", s=180, color="black", zorder=3)
ax1.set_xticks(x, [LABELS[q] for q in QUANTITIES])
ax1.set_ylabel("P(survive a 20-step horizon)")
ax1.set_ylim(0.45, 0.75)
ax1.set_title("A. The world discriminates strongly on energy and age", loc="left")
ax1.legend(frameon=False, loc="upper left")
for i, q in enumerate(QUANTITIES):
    ax1.text(i, max(high[i], high_r[i]) + 0.012, f"{main[q]['survive']['diff']:+.3f}", ha="center", fontsize=7.5)

for zone in ZONES:
    ys = [paired(zone, price) for price in PRICES]
    ax2.plot(PRICES, ys, "o-", color=COLOURS[zone], label=f"{zone} zone", markersize=5)
    for price, y in zip(PRICES, ys):
        if y is not None:
            ax2.annotate(f"{y:+.4f}", (price, y), textcoords="offset points", xytext=(0, 9),
                         ha="center", fontsize=7.5, color=COLOURS[zone])
ax2.axhline(0, color="black", lw=0.9, ls=":")
ax2.set_xscale("symlog", linthresh=0.06)
ax2.set_xticks(PRICES, ["0\n(no cost)", "0.06", "0.6"])
ax2.set_xlabel("trait price (energy lost per step)")
ax2.set_ylabel("paired difference, heritable − fixed")
ax2.set_title("B. At zero price there is no selection", loc="left")
ax2.legend(frameon=False)

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"fig1-selection-and-cost.{ext}"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("wrote fig1-selection-and-cost.png / .pdf")
