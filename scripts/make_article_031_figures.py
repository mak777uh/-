"""Build the figures of article 031 from committed artifacts only.

Every panel re-reads a JSON aggregate under morphogenesis/experiments/E09_pond/ and plots
what that file contains. No number is typed here: the plotting code derives its series
from the artifacts, so a figure cannot disagree with the data.

Figures:
  fig1-the-advantage-decays   - local greed vs baseline over the six post-seed windows,
                                with the gap (S12/D2), plus the density sweep (S13/D3).
  fig2-why-it-decays          - advantage (gap) against rich-zone occupancy, the scatter
                                behind pearson = -0.57 (S14/D4), with the density regimes
                                marked, plus rich-zone resource staying flat (S14/D4).
  fig3-the-four-nulls         - the four inheritance tests, each as the post-change
                                correct share for its arms (S6, S7, S9, S10).

Run: python scripts/make_article_031_figures.py
Writes PNG + PDF into articles/031-figures/.
"""
from __future__ import annotations
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
OUT = os.path.join(ROOT, "articles", "031-figures")
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
    "savefig.dpi": 300,
    "figure.dpi": 150,
    "pdf.fonttype": 42,          # embed TrueType so the PDF text stays selectable and searchable
    "ps.fonttype": 42,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
})


def load(name):
    with open(os.path.join(POND, name), encoding="utf-8") as fh:
        return json.load(fh)


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def series(doc, arm, field="favourable_share", regime=None):
    rows = [r for r in doc["rows"] if r["arm"] == arm]
    if regime is not None:
        rows = [r for r in rows if r.get("regime") == regime]
    nwin = max((len(r["windows"]) for r in rows), default=0)
    return [mean([r["windows"][i].get(field) for r in rows if i < len(r["windows"])])
            for i in range(nwin)]


def save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {stem}.png / .pdf")


# ---------------------------------------------------------------- figure 1
def figure1():
    s12 = load("s12_d2_full.json")
    s13 = load("s13_d3_full.json")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.4))

    b = series(s12, "baseline")
    l = series(s12, "local1")
    x = list(range(len(b)))
    ax1.plot(x, b, "o-", label="baseline (no movement)", color="#444444")
    ax1.plot(x, l, "s-", label="local greed", color="#1f6fb4")
    ax1.fill_between(x, b, l, color="#1f6fb4", alpha=0.15)
    ax1.set_xlabel("window after seeding (100 steps each)")
    ax1.set_ylabel("share of alive cells in the rich zone")
    ax1.set_title("A. The advantage is real, and it decays", loc="left")
    ax1.legend(frameon=False, fontsize=8)
    ax1.set_ylim(0, 0.55)

    for regime, colour in (("low_density", "#2a9d5c"), ("base", "#1f6fb4"), ("high_density", "#c0392b")):
        bb = series(s13, "baseline", regime=regime)
        ll = series(s13, "local1", regime=regime)
        gap = [(y - z) if (y is not None and z is not None) else None for y, z in zip(ll, bb)]
        ax2.plot(range(len(gap)), gap, "o-", label=regime.replace("_", " "), color=colour)
    ax2.axhline(0, color="black", lw=0.8, ls=":")
    ax2.set_xlabel("window")
    ax2.set_ylabel("local greed − baseline")
    ax2.set_title("B. The gain shrinks as the population thickens", loc="left")
    ax2.legend(frameon=False, fontsize=8)

    save(fig, "fig1-the-advantage-decays")


# ---------------------------------------------------------------- figure 2
def figure2():
    s14 = load("s14_d4_full.json")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.4))

    colours = {"low_density": "#2a9d5c", "base": "#1f6fb4", "high_density": "#c0392b"}
    for regime in ("low_density", "base", "high_density"):
        rows = [r for r in s14["rows"] if r.get("regime") == regime]
        nwin = max((len(r["windows"]) for r in rows), default=0)
        for i in range(nwin):
            b = [r["windows"][i] for r in rows if r["arm"] == "baseline" and i < len(r["windows"])]
            l = [r["windows"][i] for r in rows if r["arm"] == "local1" and i < len(r["windows"])]
            if not b or not l:
                continue
            gap = mean([w["favourable_share"] for w in l]) - mean([w["favourable_share"] for w in b])
            occ = mean([w["rich_occupancy"] for w in b])
            ax1.scatter(occ, gap, color=colours[regime], s=28,
                        label=regime.replace("_", " ") if i == 0 else None)
    r = s14["pearson_gap_vs_rich_occupancy"]
    ax1.axhline(0, color="black", lw=0.8, ls=":")
    ax1.set_xlabel("rich-zone occupancy (baseline)")
    ax1.set_ylabel("local greed − baseline")
    ax1.set_title(f"B. The gain falls as the rich zone fills (r = {r:.2f})", loc="left")
    ax1.legend(frameon=False, fontsize=8)

    for regime, colour in (("low_density", "#2a9d5c"), ("base", "#1f6fb4"), ("high_density", "#c0392b")):
        occ = series(s14, "baseline", field="rich_occupancy", regime=regime)
        rres = series(s14, "baseline", field="rich_resource", regime=regime)
        ax2.plot(range(len(occ)), occ, "o-", color=colour, label=f"{regime.replace('_',' ')}: occupancy")
        ax2.plot(range(len(rres)), rres, "s--", color=colour, alpha=0.55, label=f"{regime.replace('_',' ')}: resource")
    ax2.set_xlabel("window")
    ax2.set_ylabel("fraction / resource")
    ax2.set_title("A. Cells fill the zone; its food stays put", loc="left")
    ax2.legend(frameon=False, fontsize=6.5, ncol=2)

    save(fig, "fig2-why-it-decays")


# ---------------------------------------------------------------- figure 3
def figure3():
    tests = [
        ("S6: flip back to\nnative env", "s6_c3_double_baseline.json",
         [("control", "stays in B"), ("double", "returns to A")]),
        ("S7: flip to a\nNEW env C", "s7_c3b_baseline_ABC.json",
         [("control", "stays in B"), ("double", "returns to A"), ("double_new", "new env C")]),
        ("S9: heritable\nmobility", "s9_c2_full.json",
         [("neutral", "trait inert"), ("heritable", "trait drives moves"), ("transplant", "swapped")]),
        ("S10: heritable\ndirectionality", "s10_c2b_full.json",
         [("neutral", "trait inert"), ("heritable", "trait drives choice"), ("transplant", "swapped")]),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(11.0, 3.2), sharey=True)
    palette = ["#444444", "#1f6fb4", "#c0392b"]
    for ax, (title, name, arms) in zip(axes, tests):
        doc = load(name)
        for k, (arm, label) in enumerate(arms):
            vals = series(doc, arm, field="correct_share")
            ax.plot(range(len(vals)), vals, "o-", color=palette[k % 3], label=label, markersize=4)
        ax.axhline(0.5, color="black", lw=0.8, ls=":")
        ax.set_title(title, fontsize=8.5)
        ax.set_xlabel("window")
        ax.legend(frameon=False, fontsize=7)
    axes[0].set_ylabel("share in the favourable half")
    fig.suptitle("Four tests of inherited adaptation: every arm ends together, near chance", fontsize=9.5, y=1.02)
    save(fig, "fig3-the-four-nulls")


if __name__ == "__main__":
    figure1()
    figure2()
    figure3()
    print("done")
