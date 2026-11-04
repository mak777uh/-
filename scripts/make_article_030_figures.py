"""make_article_030_figures.py — figures for articles/030 (the gap between surfaces switches fusion).

Reads only committed aggregates and the per-world compact slices; writes
articles/030-figures/fig1..fig5 .png (200 dpi) and .pdf, plus tables.json with every number plotted.

Run from the repository root:  python scripts/make_article_030_figures.py
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly"
OUT = ROOT / "articles" / "030-figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#1b1b1b"
BLUE = "#2c6fbb"
RED = "#c1443c"
GREEN = "#3d8b5f"
ORANGE = "#d98c2b"
GREY = "#8a8a8a"
GRID = 96
PERIOD = 12
AMP = 0.5

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 200, "font.size": 9.5, "font.family": "DejaVu Sans",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

CMAP_FIELD = LinearSegmentedColormap.from_list("field", ["#f7f7f7", "#cfe0f2", "#6fa8dc", "#1f4e79"])


def agg(name):
    return json.loads((POND / f"l1_field_{name}.json").read_text(encoding="utf-8"))


def comp_add(path): return path


def load_compact(tag):
    return json.loads((L1 / f"{tag}.compact.json").read_text(encoding="utf-8"))


def first_pair(tag):
    d = load_compact(tag)
    step, comps = d["series"][0]
    (x0, y0), (x1, y1) = (float(comps[0][2]), float(comps[0][3])), (float(comps[1][2]), float(comps[1][3]))
    return d, (x0, y0), (x1, y1)


def field_slice(prefix, tag, step):
    p = FIELDS / f"{prefix}_fields" / tag / f"{prefix}_{tag}_t{step}.npy"
    return np.load(p) if p.exists() else None


def profile(field, p0, p1, n=240):
    ts = np.linspace(0, 1, n)
    xs = p0[0] + (p1[0] - p0[0]) * ts
    ys = p0[1] + (p1[1] - p0[1]) * ts
    vals = []
    for x, y in zip(xs, ys):
        xi = int(round(x)) % GRID
        yi = int(round(y)) % GRID
        vals.append(float(field[yi, xi]))
    return ts, np.array(vals)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[figures] wrote {name}.png/.pdf")


tables: dict = {}

# ---------------------------------------------------------------- fig 1
d193, p0, p1 = first_pair("x193_c000")
d193sep, q0, q1 = first_pair("x193_c002")
f40 = field_slice("x193", "c000", 40)
f200 = field_slice("x193", "c000", 200)
g200 = field_slice("x193", "c002", 200)
contact200 = next((comps for step, comps in d193["series"] if step == 200), None)
if contact200 and len(contact200) == 2:
    pc0 = (float(contact200[0][2]), float(contact200[0][3]))
    pc1 = (float(contact200[1][2]), float(contact200[1][3]))
else:
    pc0, pc1 = p0, p1
_, prof = profile(f200, pc0, pc1)
mid = float(prof[len(prof) // 2])
peak = float(max(prof))
ratio_demo = mid / peak
tables["fig1"] = {"fused_world": "x193_c000", "separate_world": "x193_c002",
                  "bodies_at_step_1": [p0, p1], "bodies_at_step_200": [pc0, pc1],
                  "bridge_midpoint_value": round(mid, 5), "along_line_peak": round(peak, 5),
                  "bridge_ratio_demo": round(ratio_demo, 5),
                  "sample_steps": [40, 200], "grid": GRID, "stripe_period": PERIOD}

fig, ax = plt.subplots(2, 2, figsize=(7.6, 6.6))
im = ax[0, 0].imshow(f40, cmap=CMAP_FIELD, origin="lower")
ax[0, 0].plot([p0[0], p1[0]], [p0[1], p1[1]], "--", color=RED, lw=1.2)
for (x, y), lab in ((p0, "body A"), (p1, "body B")):
    ax[0, 0].plot([x], [y], "o", ms=5, mfc="none", mec=INK, mew=1.1)
    ax[0, 0].annotate(lab, (x, y), textcoords="offset points", xytext=(6, 6), fontsize=8)
ax[0, 0].set_title("(a) a world at step 40: two bodies of pattern")
ax[0, 0].set_xlabel("x (cells)")
ax[0, 0].set_ylabel("y (cells)")
ax[0, 0].set_xticks([0, 24, 48, 72, 96])
ax[0, 0].set_yticks([0, 24, 48, 72, 96])
ax[0, 0].text(2, 90, "uneven supply: stripes of period 12", fontsize=8, color=INK)

ax[0, 1].plot(np.linspace(0, 1, len(prof)), prof, color=BLUE, lw=1.8)
ax[0, 1].axhline(peak, color=GREY, ls=":", lw=1)
ax[0, 1].plot([0.5], [mid], "o", color=RED, ms=5)
ax[0, 1].annotate(f"bridge = midpoint / peak = {ratio_demo:.2f}", (0.5, mid), textcoords="offset points",
                  xytext=(8, -22), fontsize=8.5, color=RED,
                  arrowprops=dict(arrowstyle="-", color=RED, lw=0.9))
ax[0, 1].set_title("(b) the chemical profile between the bodies")
ax[0, 1].set_xlabel("position along the dashed line")
ax[0, 1].set_ylabel("chemical concentration")

for a, step, title, sub in ((ax[1, 0], 200, "(c) a world that fused", "one body at step 200"),
                            (ax[1, 1], 200, "(d) a world that stayed apart", "two bodies at step 200")):
    fld = f200 if step == 200 and a is ax[1, 0] else g200
    a.imshow(fld, cmap=CMAP_FIELD, origin="lower")
    a.set_title(f"{title}\n{sub}", fontsize=9.5)
    a.set_xticks([0, 24, 48, 72, 96])
    a.set_yticks([0, 24, 48, 72, 96])
    a.set_xlabel("x (cells)")
    a.set_ylabel("y (cells)")

fig.suptitle("Figure 1 — what the measurement is", fontsize=12, fontweight="bold", y=0.99)
fig.tight_layout(rect=(0, 0, 1, 0.97))
save(fig, "fig1-what-we-measure")

# ---------------------------------------------------------------- fig 2
x192, x193 = agg("x192_phase_census"), agg("x193_phase_census_r3")
r6 = [(r["f_local"], r["ratio_contact"], r["fused"]) for r in x192["runs_detail"] if r["ratio_contact"] is not None]
r3 = [(r["f_local"], r["ratio_contact"], r["fused"]) for r in x193["runs_detail"] if r["ratio_contact"] is not None]
tables["fig2"] = {"r6": {"radius": x192["radius"], "gap": x192["gap"], "worlds": len(r6),
                         "f_local_values": sorted({p[0] for p in r6})},
                  "r3": {"radius": x193["radius"], "gap": x193["gap"], "worlds": len(r3),
                         "f_local_values": sorted({p[0] for p in r3})}}

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.9))
vals6 = sorted({p[0] for p in r6})
counts6 = [sum(1 for p in r6 if abs(p[0] - v) < 1e-9) for v in vals6]
ax[0].bar(range(len(vals6)), counts6, color=[BLUE if c == max(counts6) else "#b9cfe6" for c in counts6])
ax[0].set_xticks(range(len(vals6)))
ax[0].set_xticklabels([f"{v:g}" for v in vals6], rotation=0, fontsize=8)
ax[0].set_xlabel("local inflow at the bodies (F_local)")
ax[0].set_ylabel("number of phase classes")
ax[0].set_title(f"(a) {len(vals6)} distinct inflows carry {len(r6)} phases")
ax[0].annotate("26 of the 144 phases\nsit at one inflow", (counts6.index(max(counts6)), max(counts6)),
               textcoords="offset points", xytext=(-14, -30), fontsize=8.5, color=INK)
rng = np.random.default_rng(3)
for pts, colour, marker, lab in ((r6, BLUE, "o", f"radius {x192['radius']:.0f} (gap {x192['gap']:.0f})"),
                                 (r3, RED, "s", f"radius {x193['radius']:.0f} (gap {x193['gap']:.0f})")):
    xs = np.array([p[0] for p in pts]) + rng.uniform(-1e-4, 1e-4, len(pts))
    ys = np.array([p[1] for p in pts])
    ax[1].scatter(xs, ys, s=16, color=colour, marker=marker, alpha=0.75, label=lab, lw=0)
    grid = np.array(sorted({p[0] for p in pts}))
    med = [np.median([y for x, y, _ in pts if abs(x - g) < 1e-9]) for g in grid]
    ax[1].plot(grid, med, color=colour, lw=1.6)
ax[1].set_xlabel("local inflow at the bodies (F_local)")
ax[1].set_ylabel("bridge ratio at contact")
ax[1].set_title("(b) the phase moves the bridge " + r"(144 worlds per radius)")
ax[1].legend(loc="upper right", fontsize=8)
fig.suptitle("Figure 2 — the population of phases and the bridge at a fixed inflow", fontsize=12,
             fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "fig2-phase-and-the-bridge")

# ---------------------------------------------------------------- fig 3
def bins_for(pts, nbins=6):
    xs = np.array([p[1] for p in pts])
    ys = np.array([p[2] for p in pts], dtype=float)
    edges = np.quantile(xs, np.linspace(0, 1, nbins + 1))
    edges = np.unique(edges)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (xs >= lo) & (xs <= hi if hi == edges[-1] else xs < hi)
        if m.sum() >= 4:
            out.append((float(xs[m].mean()), float(ys[m].mean()), int(m.sum())))
    return out


def logistic_curve(pts, grid=200):
    xs = np.array([p[1] for p in pts])
    ys = np.array([p[2] for p in pts], dtype=float)
    X = np.column_stack([np.ones(len(xs)), xs])
    beta = np.zeros(2)
    for _ in range(60):
        p = 1 / (1 + np.exp(-X @ beta))
        W = np.diag(np.maximum(p * (1 - p), 1e-8))
        try:
            beta = beta + np.linalg.solve(X.T @ W @ X, X.T @ (ys - p))
        except np.linalg.LinAlgError:
            break
    g = np.linspace(xs.min(), xs.max(), grid)
    return g, 1 / (1 + np.exp(-(beta[0] + beta[1] * g)))


slope6 = x192["logistic_slope_fusion_on_ratio"]
slope3 = x193["logistic_slope_fusion_on_ratio"]
tables["fig3"] = {"r6": {"slope": slope6, "bins": bins_for(r6)},
                  "r3": {"slope": slope3, "bins": bins_for(r3)}}

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
for a, pts, colour, sl, name, ref in ((ax[0], r6, BLUE, slope6, f"radius {x192['radius']:.0f} gap {x192['gap']:.0f}", x192),
                                      (ax[1], r3, RED, slope3, f"radius {x193['radius']:.0f} gap {x193['gap']:.0f}", x193)):
    for x, y, n in bins_for(pts):
        a.plot([x], [y], "o", ms=6, color=colour)
    g, m = logistic_curve(pts)
    a.plot(g, m, color=colour, lw=1.6)
    a.set_xlabel("bridge ratio at contact")
    a.set_title(f"{name}: slope {sl['slope']:.2f} (z {sl['z']:.1f})")
    a.set_ylim(-0.05, 1.05)
ax[0].set_ylabel("share of worlds that fused")
ax[0].legend(["binned share", "logistic fit"], fontsize=8, loc="lower right")
ax[0].text(0.02, 0.95, "above the median bridge,\nthe outcome flips", transform=ax[0].transAxes, fontsize=8.5, va="top")
fig.suptitle("Figure 3 — at a fixed inflow, the bridge decides the outcome", fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "fig3-the-bridge-decides")

# ---------------------------------------------------------------- fig 4
gap_table = agg("x196_gap_or_size")["gap_table"]
refs = agg("x196_gap_or_size")["references"]
arms = []
for name, v in gap_table.items():
    arms.append({"name": name, "radius": v["radius"], "gap": v["gap"], "share": v["share"], "fused": v["fused_worlds"],
                 "worlds": v["worlds"]})
arms.append({"name": "r4_g12_reference", "radius": refs["r4_g12"]["radius"], "gap": refs["r4_g12"]["gap"],
             "share": refs["r4_g12"]["share_over_values"], "fused": refs["r4_g12"]["fused_worlds"],
             "worlds": refs["r4_g12"]["worlds"]})
arms.append({"name": "r6_g9_reference", "radius": refs["r6_g9"]["radius"], "gap": refs["r6_g9"]["gap"],
             "share": refs["r6_g9"]["share_over_values"], "fused": refs["r6_g9"]["fused_worlds"],
             "worlds": refs["r6_g9"]["worlds"]})
by_gap = sorted(arms, key=lambda a: (-a["gap"], -a["radius"]))
tables["fig4"] = {"by_gap": by_gap, "note": "share is the mean over the arm's inflow values; worlds = 144 per arm"}

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.9))
cols = [RED if a["radius"] == 4.0 else BLUE for a in by_gap]
bars = ax[0].bar([f"{a['gap']:.0f}\nr={a['radius']:.0f}" for a in by_gap], [a["share"] for a in by_gap], color=cols, width=0.62)
for b, a in zip(bars, by_gap):
    ax[0].annotate(f"{a['share']:.2f}\n{a['fused']}/{a['worlds']}", (b.get_x() + b.get_width() / 2, b.get_height()),
                   textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
ax[0].set_xlabel("surface-to-surface gap (cells), radius below")
ax[0].set_ylabel("share of worlds that fused")
ax[0].set_ylim(0, 1.12)
ax[0].set_title("(a) ordered by the gap: monotone")
r4 = sorted([a for a in arms if a["radius"] == 4.0], key=lambda a: -a["gap"])
r6 = sorted([a for a in arms if a["radius"] == 6.0], key=lambda a: -a["gap"])
ax[1].plot([a["gap"] for a in r4], [a["share"] for a in r4], "o-", color=RED, lw=1.6, label="radius 4")
ax[1].plot([a["gap"] for a in r6], [a["share"] for a in r6], "s-", color=BLUE, lw=1.6, label="radius 6")
ax[1].set_xlabel("surface-to-surface gap (cells)")
ax[1].set_ylabel("share of worlds that fused")
ax[1].invert_xaxis()
ax[1].set_ylim(0, 1.05)
ax[1].set_title("(b) both sizes rise as the gap closes")
ax[1].legend(fontsize=8.5)
ax[1].annotate("radius 4 at a separation of 20\n(gap 12) fuses nothing", (12, 0.0), textcoords="offset points",
               xytext=(-8, 26), fontsize=8, color=RED)
fig.suptitle("Figure 4 — the gap between the surfaces switches fusion; the size only shifts it",
             fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "fig4-the-gap-switches")

# ---------------------------------------------------------------- fig 5
x194, x197 = agg("x194_phase_clusters"), agg("x197_deviance_worlds")
bs = x194["bootstrap"]
dev = x197["deviance"]
tab = x197["bootstrap"]
tables["fig5"] = {"auc": {"by_runs": x194["auc_by_runs"], "by_worlds": x194["auc_by_phases_homogeneous"],
                          "ci_runs": bs["by_runs"]["ci95"], "ci_worlds": bs["by_phases"]["ci95"],
                          "sd_ratio": bs["sd_ratio_phases_over_runs"]},
                  "deviance_drop": dev, "bootstrap": tab,
                  "pool": x197["pool"], "worlds": x197["worlds"]}

fig, ax = plt.subplots(1, 3, figsize=(10.6, 3.7))
series = [(x194["auc_by_runs"], bs["by_runs"]["ci95"], "per run"), (x194["auc_by_phases_homogeneous"], bs["by_phases"]["ci95"], "per world")]
xs = np.arange(len(series))
ax[0].bar(xs, [s[0] for s in series], color=[GREY, GREEN], width=0.55)
for i, (v, ci, _) in enumerate(series):
    ax[0].plot([i, i], [ci[0], ci[1]], color=INK, lw=1.4)
    ax[0].plot([i - 0.12, i + 0.12], [ci[0], ci[0]], color=INK, lw=1.2)
    ax[0].plot([i - 0.12, i + 0.12], [ci[1], ci[1]], color=INK, lw=1.2)
    ax[0].annotate(f"{v:.3f}", (i, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)
ax[0].set_xticks(xs)
ax[0].set_xticklabels(["per run", "per world"])
ax[0].set_ylim(0.55, 0.75)
ax[0].set_ylabel("AUC of the inflow–fusion association")
ax[0].set_title("(a) a rank statistic does not move")

ax[1].bar([0, 1], [dev["drop_runs"], dev["drop_worlds"]], color=[GREY, ORANGE], width=0.55)
ax[1].axhline(20, color=RED, ls="--", lw=1.2)
ax[1].annotate("the test's own bar: 20", (1.35, 20.6), fontsize=8.5, color=RED, ha="right")
for i, v in enumerate((dev["drop_runs"], dev["drop_worlds"])):
    ax[1].annotate(f"{v}", (i, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)
ax[1].set_xticks([0, 1])
ax[1].set_xticklabels(["per run", "per world"])
ax[1].set_ylabel("deviance drop (nominal F → local inflow)")
ax[1].set_ylim(0, 26)
ax[1].set_title("(b) a likelihood statistic does")

ax[2].bar([0, 1], [tab["share_above_bar_runs"], tab["share_above_bar_worlds"]], color=[GREY, ORANGE], width=0.55)
for i, v in enumerate((tab["share_above_bar_runs"], tab["share_above_bar_worlds"])):
    ax[2].annotate(f"{v:.2f}", (i, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)
ax[2].set_xticks([0, 1])
ax[2].set_xticklabels(["per run", "per world"])
ax[2].set_ylabel("bootstrap resamples with drop > 20")
ax[2].set_ylim(0, 0.7)
ax[2].set_title("(c) and the interval widens")
fig.suptitle("Figure 5 — the unit of observation has to be checked for each statistic",
             fontsize=12, fontweight="bold", y=1.03)
fig.tight_layout()
save(fig, "fig5-the-unit-of-observation")

(OUT / "tables.json").write_text(json.dumps(tables, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"[figures] tables.json written with {len(tables)} groups")
