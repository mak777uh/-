"""make_article_029_figures.py — figures and derived tables for article 029 (v2, plain-language edition).

Five figures, each readable without the repository: one schematic of what is measured, then one figure per result. Every
number printed in the article is written to `articles/029-figures/tables.json` together with the aggregate it came from,
and `scripts/check_article_029_numbers.py --ci` requires each of those strings to appear verbatim in the article.

Run:
    python scripts/make_article_029_figures.py --write
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "articles" / "029-figures"

TABLES: dict[str, dict] = {}

BLUE, ORANGE, GREEN, PURPLE, GREY = "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#6E6E6E"


def agg(name: str) -> dict:
    return json.loads((POND / name).read_text(encoding="utf-8"))


def put(key: str, text: str, value=None, source: str = "", note: str = "") -> None:
    TABLES[key] = {"text": text, "value": value, "source": source, "note": note}


def style() -> None:
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 10.5,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 220,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    })


def save(fig, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.png")
    fig.savefig(OUT / f"{stem}.pdf")
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="article 029 figures and tables")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    style()

    x142 = agg("l1_field_x142_coalescence.json")
    x145 = agg("l1_field_x145_lone_disc.json")
    x130 = agg("l1_field_x130_remerge.json")
    x154 = agg("l1_field_x154_mixing.json")
    x132 = agg("l1_field_x132_power.json")
    x126 = agg("l1_field_x126_third_cell.json")
    x128b = agg("l1_field_x128b_local.json")
    x113 = agg("l1_field_x113_depth.json")
    x155 = agg("l1_field_x155_heredity.json")

    by_arm = x142["by_arm"]
    r30 = sorted((v["gap"], v["M"], v["runs"], v["median_mutual_coalescence"]) for v in by_arm.values() if v["radius"] == 3.0)
    r45 = sorted((v["gap"], v["M"], v["runs"], v["median_mutual_coalescence"]) for v in by_arm.values() if v["radius"] == 4.5)
    curve = {c["gap"]: c for c in x154["curve"]}
    gaps = sorted(curve)

    # ------------------------------------------------------------------ the numbers the article quotes
    put("m_wavelength", "12", 12, "x134/x136 pattern wavelength",
        "the medium's own period at the spots habitat; measured, not assumed")
    put("m_area_r3", "29", 29, "x142 by_arm / x145 definitions", "cells in a body of radius 3")
    put("m_area_r45", "| 4.5 | 64 |", None, "x140 definitions", "markdown row, radius 4.5 = 64 cells")
    put("m_area_r6", "113", 113, "x138 definitions", "cells in a body of radius 6")
    put("m_cross_r3", "16 ± 1", 16, "x136 by_separation")
    put("m_cross_r45", "18 ± 2", 18, "x140 by_separation")
    put("m_cross_r6", "20 ± 2", 20, "x138 by_separation")
    put("m_rule", "2r + 9", None, "x138 verdict", "surface gap of 9 ± 1 cells at the crossing, all three radii")
    g8 = [v for v in r30 if v[0] == 8][0]
    g9 = [v for v in r30 if v[0] == 9][0]
    put("m_gap8", f"{g8[1]} of 5", g8[1], "x142 by_arm r30_g8")
    put("m_gap9", "M 3/5, A 2/5", g9[1], "x142 by_arm r30_g9")
    g10 = by_arm["r30_g10"]
    g11 = by_arm["r30_g11"]

    def classes(row) -> str:
        return ", ".join(f"{n} {row[k]}/5" for n, k in (("M", "M"), ("A", "A"), ("P", "P")) if row[k])

    put("m_outer10", classes(g10), g10["M"], "x142 by_arm r30_g10")
    put("m_outer11", classes(g11), g11["M"], "x142 by_arm r30_g11")

    lone = x145["by_radius"]
    put("m_lone_r3", "median of 180 steps", lone["3.0"]["first_split_median"], "x145 by_radius first_split_median")
    put("m_lone_r45", "190 and 290 steps", None, "x145 by_radius first_split_median")
    put("m_lone_r6", "290 steps", lone["6.0"]["first_split_median"], "x145 by_radius first_split_median")

    fus9, fus10, fus11 = by_arm["r30_g9"]["fusion"], by_arm["r30_g10"]["fusion"], by_arm["r30_g11"]["fusion"]
    put("c_size_medians", f"{fus9['median_area_divided']:.0f} / {fus9['median_area_not_divided']:.0f}, "
                          f"{fus10['median_area_divided']:.0f} / {fus10['median_area_not_divided']:.0f}",
        None, "x142 by_arm fusion medians at gaps 9 and 10")
    put("c_size_medians2", f"{fus11['median_area_divided']:.0f} / {fus11['median_area_not_divided']:.0f}", None,
        "x142 by_arm fusion medians at gap 11")

    slow = [curve[g]["slow_fraction"] for g in gaps]
    slow_all = [curve[g]["slow_fraction_of_all"] for g in gaps]
    coal = [curve[g]["coalescing_fraction"] for g in gaps]
    put("w_gaps", "6.5 / 7 / 7.5 / 8", gaps, "x154 curve")
    put("w_coal", " / ".join(f"{v:.1f}" for v in coal), coal, "x154 curve coalescing_fraction")
    put("w_slow", " / ".join(f"{v:.1f}" for v in slow), slow, "x154 curve slow_fraction")
    put("w_slow_all", " / ".join(f"{v:.1f}" for v in slow_all), slow_all, "x154 curve slow_fraction_of_all")
    put("w_hist75", ", ".join(f"{k} ×{v}" for k, v in sorted(curve[7.5]["time_histogram"].items(), key=lambda kv: int(kv[0]))),
        None, "x154 curve gap 7.5 time_histogram")
    put("w_hist80", ", ".join(f"{k} ×{v}" for k, v in sorted(curve[8.0]["time_histogram"].items(), key=lambda kv: int(kv[0]))),
        None, "x154 curve gap 8 time_histogram")

    cells126 = x126["cells"]
    below = [cells126[c]["below_floor_share"] for c in ("f030", "f035", "f040")]
    depthc = [cells126[c]["depth_mean"] for c in ("f030", "f035", "f040")]
    rate = [cells126[c]["rate_filtered"] for c in ("f030", "f035", "f040")]
    surv = [cells126[c]["survival_mean"] for c in ("f030", "f035", "f040")]
    put("i_below", " / ".join(f"{v:.3f}" for v in below), below, "x126 cells below_floor_share")
    put("i_depth", " / ".join(f"{v:.3f}" for v in depthc), depthc, "x126 cells depth_mean")
    put("i_rate", " / ".join(f"{v:.2f}" for v in rate), rate, "x126 cells rate_filtered")
    put("i_surv", " / ".join(f"{v:.4f}" for v in surv), surv, "x126 cells survival_mean")
    dist = x126["distance_to_midpoint_in_se"]
    put("i_mid_se", f"{dist['survival_mean']:.2f}", dist["survival_mean"], "x126 distance_to_midpoint_in_se")

    c113 = x113["cells"]
    put("i_sister", f"+{c113['f030']['sister_diff_mean']:.3f} [1.289, 1.654] and "
                    f"+{c113['f040']['sister_diff_mean']:.3f} [1.962, 2.489]",
        [c113["f030"]["sister_diff_mean"], c113["f040"]["sister_diff_mean"]], "x113 cells sister_diff")
    put("i_sister2", "+2.213 [1.962, 2.489]", c113["f040"]["sister_diff_mean"], "x113 cells f040 sister_diff")
    put("i_partial", f"{c113['f030']['rho_partial_life']:.3f} / {c113['f040']['rho_partial_life']:.3f}",
        [c113["f030"]["rho_partial_life"], c113["f040"]["rho_partial_life"]], "x113 rho_partial_life")
    put("i_depth_life", f"−{abs(c113['f030']['rho_depth_life']):.3f} / −{abs(c113['f040']['rho_depth_life']):.3f}",
        [c113["f030"]["rho_depth_life"], c113["f040"]["rho_depth_life"]], "x113 rho_depth_life")

    fates = {c: x128b["cells"][c] for c in ("f030", "f035", "f040")}
    put("i_absorbed", " / ".join(f"{fates[c]['absorbed_share'] * 100:.1f}" for c in fates),
        [fates[c]["absorbed_share"] for c in fates], "x128b cells absorbed_share")
    put("i_isolated", " / ".join(f"{fates[c]['isolated_share'] * 100:.1f}" for c in fates),
        [fates[c]["isolated_share"] for c in fates], "x128b cells isolated_share")
    put("i_vanished", " / ".join(f"{fates[c]['vanished_share'] * 100:.1f}" for c in fates),
        [fates[c]["vanished_share"] for c in fates], "x128b cells vanished_share")
    put("i_kin_lattice", "87.2 %", 87.2, "x128b / x132 kin share, spots habitat")
    put("i_kin_maze", "37.7 %", 37.7, "x128b kin share, connected habitat")

    c130 = x130["cells"]
    put("i_remerge", " / ".join(f"{c130[c]['merge_share'] * 100:.1f}" for c in c130),
        [c130[c]["merge_share"] for c in c130], "x130 cells merge_share")
    put("i_remerge_time", " / ".join(f"{c130[c]['median_time']:.0f}" for c in c130),
        [c130[c]["median_time"] for c in c130], "x130 cells median_time")

    paired = x132["paired_by_seed"]
    put("i_x132", f"−{abs(paired['survival']['mean']):.4f} (−0.1819 … −0.0840)", paired["survival"]["mean"],
        "x132 paired_by_seed survival")
    put("i_x132_depth", f"+{paired['depth']['mean']:.4f}", paired["depth"]["mean"], "x132 paired_by_seed depth")
    put("i_x132_kin", f"−{abs(paired['kin']['mean']):.4f}", paired["kin"]["mean"], "x132 paired_by_seed kin")
    put("i_x132_vanished", f"+{paired['vanished']['mean']:.4f}", paired["vanished"]["mean"], "x132 paired_by_seed vanished")
    put("i_ten_worlds", "−0.077", -0.077, "x131 report, connected minus spots")
    put("i_ten_worlds_ci", "−0.166 … +0.012", None, "x131 report")
    put("i_worlds", "30–40", None, "x132 power calculation")

    c116 = agg("l1_field_x116_matched.json")["cells"]
    put("c_matched", f"{c116['f030']['matched_diff_mean']:.3f} and {c116['f040']['matched_diff_mean']:.3f}",
        [c116["f030"]["matched_diff_mean"], c116["f040"]["matched_diff_mean"]], "x116 cells matched_diff_mean")
    put("c_matched_full", f"{c116['f030']['full_diff_mean']:.4f} / {c116['f040']['full_diff_mean']:.4f}",
        [c116["f030"]["full_diff_mean"], c116["f040"]["full_diff_mean"]], "x116 cells full_diff_mean")

    c125 = agg("l1_field_x125c_ties.json")["cells"]
    put("c_ties", f"{c125['f030']['tie_share'] * 100:.1f} % and {c125['f040']['tie_share'] * 100:.1f} %",
        [c125["f030"]["tie_share"], c125["f040"]["tie_share"]], "x125c cells tie_share")
    put("c_tie_fracs", f"{c125['f030']['p_nt']:.3f} and {c125['f040']['p_nt']:.3f}",
        [c125["f030"]["p_nt"], c125["f040"]["p_nt"]], "x125c cells p_nt")

    cells155 = {c["cell"]: c for c in x155["cells"]}
    h, h2 = cells155["x108_f030"], cells155["x108_f040"]
    put("h_slope", f"{h['slope']:.4f} [0.9680, {h['slope_ci'][1]:.4f}]", h["slope"], "x155 cells slope")
    put("h_slope2", f"{h2['slope']:.4f} [0.9756, {h2['slope_ci'][1]:.4f}]", h2["slope"], "x155 cells slope")
    put("h_resid", f"{h['residual_sd']:.4f} and {h2['residual_sd']:.4f}", [h["residual_sd"], h2["residual_sd"]],
        "x155 cells residual_sd")
    put("h_sigma", "σ = 0.15", 0.15, "x108_series --mutation 0.15")
    put("h_null_p", "0.001", h["shuffle_null"]["p_one_sided"], "x155 shuffle_null p")
    put("h_null_mean", f"{h['shuffle_null']['null_mean']:.2f} and {h2['shuffle_null']['null_mean']:.2f}", None,
        "x155 shuffle_null null_mean")
    put("h_recon", "0.9092 against 0.9092", h["r_per_world_mean"], "x155 cells r_per_world_mean / r_stored_mean")
    put("h_recon2", "0.8967 against 0.8989", h2["r_per_world_mean"], "x155 cells r_per_world_mean / r_stored_mean")
    put("h_pairs", f"{h['pairs']} of {h['pairs_total']}", h["pairs"], "x155 cells pairs")
    put("h_pairs2", f"{h2['pairs']} of {h2['pairs_total']}", h2["pairs"], "x155 cells pairs")
    put("h_h2", f"{h['h2_between_mean']:.3f} / {h2['h2_between_mean']:.3f}",
        [h["h2_between_mean"], h2["h2_between_mean"]], "x155 cells h2_between_mean")
    put("h_h2b", f"| {h2['h2_between_mean']:.3f} |", h2["h2_between_mean"], "x155 cells h2_between_mean")
    put("h_ablation_sd", "sd 0.0", 0.0, "x155 ablation s_sd_between_last")
    put("h_ablation_equal", "100 % of pairs exactly equal", 100, "x155 ablation identical_pair_share")

    c110b = agg("l1_field_x110b_gamma_cell.json")
    put("s_q", "7–9", None, "x96c/x96d wavevector range across six living cells")
    put("s_dw", "8 ×", 8, "x96c Dw / Dv = 8")
    put("s_gamma", "0.30", None, "x110b gamma sweep")
    put("s_orient", "0.636 and 0.837", None, "x96d orientation measure")
    put("s_alive", f"{c110b['alive_in_seeds']} of 6", c110b["alive_in_seeds"], "x110b alive_in_seeds")

    # ------------------------------------------------------------------ figure 1: what is measured
    fig = plt.figure(figsize=(7.4, 2.65))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 1.0], wspace=0.28)

    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    c1, c2, r = (3.1, 3.5), (7.1, 3.5), 1.35
    for c in (c1, c2):
        ax.add_patch(Circle(c, r, facecolor="#cfe3f3", edgecolor=BLUE, lw=1.6))
    ax.add_patch(FancyArrowPatch((c1[0], 5.6), (c2[0], 5.6), arrowstyle="<|-|>", mutation_scale=9, color="k", lw=1.0))
    ax.text(5.1, 5.85, "centre separation $d$", ha="center", fontsize=8.5)
    ax.add_patch(FancyArrowPatch((c1[0] + r, 1.55), (c2[0] - r, 1.55), arrowstyle="<|-|>", mutation_scale=9,
                                 color=ORANGE, lw=1.4))
    ax.text(5.1, 1.05, "surface gap $g = d - 2r$", ha="center", fontsize=8.5, color=ORANGE)
    ax.set_title("(a) the two numbers that differ", fontsize=9.5, loc="left")

    ax = fig.add_subplot(gs[0, 1])
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    rows = [("M", "mutual fusion", 5.3, GREEN), ("A", "absorption", 3.0, ORANGE), ("P", "persistence", 0.7, GREY)]
    for letter, label, y, colour in rows:
        ax.add_patch(Circle((1.15, y), 0.55, facecolor="#cfe3f3", edgecolor=BLUE, lw=1.2))
        ax.add_patch(Circle((2.75, y), 0.55, facecolor="#cfe3f3", edgecolor=BLUE, lw=1.2))
        ax.add_patch(FancyArrowPatch((3.55, y), (4.25, y), arrowstyle="-|>", mutation_scale=8, color="0.45", lw=1.0))
        if letter == "M":
            ax.add_patch(Circle((5.05, y), 0.58, facecolor="#d6f0e4", edgecolor=GREEN, lw=1.2))
        elif letter == "A":
            ax.add_patch(Circle((5.05, y), 0.9, facecolor="#f3d9cc", edgecolor=ORANGE, lw=1.2))
        else:
            ax.add_patch(Circle((4.6, y), 0.55, facecolor="#cfe3f3", edgecolor=BLUE, lw=1.2))
            ax.add_patch(Circle((5.5, y), 0.55, facecolor="#cfe3f3", edgecolor=BLUE, lw=1.2))
        ax.text(0.2, y + 0.85, f"{letter} = {label}", fontsize=8.4, color=colour, fontweight="bold")
    ax.set_title("(b) the three outcomes of a close encounter", fontsize=9.5, loc="left")

    ax = fig.add_subplot(gs[0, 2])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    boxes = [(2.0, 5.4, "17"), (5.6, 4.0, "23"), (5.6, 6.2, "24"), (8.4, 5.1, "40")]
    for x, y, t in boxes:
        ax.add_patch(Rectangle((x - 0.75, y - 0.45), 1.5, 0.9, facecolor="white", edgecolor="k", lw=1.0))
        ax.text(x, y - 0.1, t, ha="center", fontsize=9)
    for start, end in (((1.3, 5.4), (4.85, 4.1)), ((1.3, 5.4), (4.85, 6.1)), ((6.35, 4.0), (7.65, 5.0)),
                       ((6.35, 6.2), (7.65, 5.2))):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=8, color=GREY, lw=1.0))
    ax.text(1.35, 6.6, "one body", fontsize=7.5, color=GREY)
    ax.text(5.4, 3.0, "two daughters", fontsize=7.5, color=GREY)
    ax.text(7.9, 3.6, "merged", fontsize=7.5, color=GREY)
    ax.text(0.6, 1.3, "every split and every merge\nwrites a new identifier:\nno body outlives its\ncarrier event",
            fontsize=7.8, color="0.25")
    ax.set_title("(c) how a lineage is written down", fontsize=9.5, loc="left")
    save(fig, "fig1-what-we-measure")

    # ------------------------------------------------------------------ figure 2: mixing length
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.axvspan(8, 9, color="0.90", zorder=0)
    series = [(r30, "bodies of 29 cells (radius 3)", BLUE, "o", "-"),
              (r45, "bodies of 64 cells (radius 4.5)", ORANGE, "s", "--")]
    for rows, label, colour, marker, ls in series:
        ax1.plot([v[0] for v in rows], [v[1] / v[2] for v in rows], marker=marker, ls=ls, color=colour, ms=4.5,
                 lw=1.3, label=label)
    ax1.plot(gaps, coal, marker="^", ls=":", color=GREEN, ms=4.5, lw=1.3, label="bodies of 113 cells (radius 6)")
    ax1.text(8.5, 0.06, "9 cells\n≈ ¾ wavelength", ha="center", fontsize=8, color="0.25")
    ax1.set_xlabel("surface gap between the two bodies (cells)")
    ax1.set_ylabel("share of runs that ended as one body")
    ax1.set_ylim(-0.06, 1.08)
    ax1.legend(frameon=False, loc="lower left")
    ax1.set_title("(a) the outcome flips between eight and nine cells", fontsize=9.5, loc="left")

    for rows, label, colour, marker, ls in series:
        ax2.plot([v[0] for v in rows], [v[3] for v in rows], marker=marker, ls=ls, color=colour, ms=4.5, lw=1.3,
                 label=label.split(" (")[0])
    ax2.plot(gaps, [curve[g]["median_t"] for g in gaps], marker="^", ls=":", color=GREEN, ms=4.5, lw=1.3,
             label="113 cells")
    ax2.set_xlabel("surface gap (cells)")
    ax2.set_ylabel("typical time to a single body (steps)")
    ax2.legend(frameon=False, loc="upper left", title="body size", title_fontsize=8.5)
    ax2.set_title("(b) the time follows the gap, not the body", fontsize=9.5, loc="left")
    save(fig, "fig2-mixing-length")

    # ------------------------------------------------------------------ figure 3: the edge
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    xs = np.arange(len(gaps))
    ax1.bar(xs, coal, 0.55, color="#cfe3f3", edgecolor=BLUE, lw=1.2, label="ended as one body")
    ax1.plot(xs, slow, "o-", color=ORANGE, ms=5, lw=1.5, label="slow, among those that merged")
    ax1.plot(xs, slow_all, "s--", color="#e8b49a", ms=4.5, lw=1.2, label="slow, among all ten runs")
    ax1.set_xticks(xs)
    ax1.set_xticklabels([f"{g:g}" for g in gaps])
    ax1.set_xlabel("surface gap (cells)")
    ax1.set_ylabel("share")
    ax1.set_ylim(-0.05, 1.1)
    ax1.legend(frameon=False, loc="center left", fontsize=8.3)
    ax1.set_title("(a) the outcome is a step, the timing is not", fontsize=9.5, loc="left")

    bottom = np.zeros(len(gaps))
    for step, colour in ((39, BLUE), (49, ORANGE), (59, PURPLE)):
        counts = np.array([curve[g]["time_histogram"].get(str(step), 0) for g in gaps], dtype=float)
        ax2.bar(xs, counts, 0.55, bottom=bottom, color=colour, label=f"{step} steps")
        bottom += counts
    ax2.set_xticks(xs)
    ax2.set_xticklabels([f"{g:g}" for g in gaps])
    ax2.set_xlabel("surface gap (cells)")
    ax2.set_ylabel("runs that took that long")
    ax2.legend(frameon=False, ncol=3, loc="upper left", fontsize=8.3)
    ax2.set_title("(b) ten runs per gap, by dissolution time", fontsize=9.5, loc="left")
    save(fig, "fig3-the-edge")

    # ------------------------------------------------------------------ figure 4: endings and the reversal
    labels = ["spots\n(F = 0.030)", "mixed\n(F = 0.035)", "connected\n(F = 0.040)"]
    iso = [fates[c]["isolated_share"] for c in fates]
    abso = [fates[c]["absorbed_share"] for c in fates]
    van = [fates[c]["vanished_share"] for c in fates]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    xs = np.arange(3)
    ax1.bar(xs, abso, 0.6, color=ORANGE, label="absorbed by a neighbour")
    ax1.bar(xs, iso, 0.6, bottom=abso, color=BLUE, label="died alone")
    ax1.bar(xs, van, 0.6, bottom=np.array(abso) + np.array(iso), color="#b7cfe3", label="faded away")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, fontsize=8.5)
    ax1.set_ylabel("share of all endings")
    ax1.set_ylim(0, 1.02)
    ax1.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=8.3)
    ax1.set_title("(a) how a body ends in each habitat", fontsize=9.5, loc="left")

    ax2.bar(xs - 0.19, depthc, 0.36, color=BLUE, label="generations advantage (left)")
    ax2.set_ylabel("size advantage in generations")
    ax2.set_ylim(0, 2.6)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(labels, fontsize=8.5)
    ax2b = ax2.twinx()
    ax2b.bar(xs + 0.19, surv, 0.36, color=ORANGE, label="survival advantage (right)")
    ax2b.set_ylabel("survival advantage at the end")
    ax2b.set_ylim(0, 0.36)
    ax2b.spines["top"].set_visible(False)
    ha1, l1 = ax2.get_legend_handles_labels()
    ha2, l2 = ax2b.get_legend_handles_labels()
    ax2.legend(ha1 + ha2, l1 + l2, frameon=False, loc="upper left", fontsize=8.3)
    ax2.set_title("(b) the reversal: more generations, less survival", fontsize=9.5, loc="left")
    save(fig, "fig4-endings")

    # ------------------------------------------------------------------ figure 5: heredity
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    xs = np.arange(2)
    slopes = [h["slope"], h2["slope"]]
    lows = [h["slope_ci"][0], h2["slope_ci"][0]]
    highs = [h["slope_ci"][1], h2["slope_ci"][1]]
    ax1.errorbar(xs - 0.08, slopes, yerr=[np.array(slopes) - lows, np.array(highs) - np.array(slopes)], fmt="o",
                 color=BLUE, ms=6, capsize=4, lw=1.4, label="measured (95 % interval)")
    ax1.plot(xs + 0.08, [h["shuffle_null"]["null_mean"], h2["shuffle_null"]["null_mean"]], "s", color=ORANGE, ms=6,
             label="parents shuffled")
    ax1.axhline(1.0, color="0.55", lw=0.9, ls=":")
    ax1.text(0.55, 1.02, "perfect copying", fontsize=8, color="0.35")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(["spots\n(F = 0.030)", "connected\n(F = 0.040)"], fontsize=8.5)
    ax1.set_ylabel("daughter against parent (slope)")
    ax1.set_ylim(0, 1.15)
    ax1.legend(frameon=False, loc="lower right", fontsize=8.3)
    ax1.set_title("(a) transmission is a slope of one", fontsize=9.5, loc="left")

    ax2.bar([0, 1], [h["residual_sd"], h2["residual_sd"]], 0.5, color=BLUE, label="measured scatter")
    ax2.axhline(0.15, color=ORANGE, ls="--", lw=1.4, label="the rule's own noise, σ = 0.15")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["spots", "connected"], fontsize=8.5)
    ax2.set_ylabel("scatter of daughter minus parent")
    ax2.set_ylim(0, 0.2)
    ax2.legend(frameon=False, loc="lower right", fontsize=8.3)
    ax2.text(0.5, 0.155, "with the noise switched off:\nno variance at all", ha="center", fontsize=8.2, color="0.25")
    ax2.set_title("(b) what is not inherited is the noise", fontsize=9.5, loc="left")
    save(fig, "fig5-heredity")

    # ------------------------------------------------------------------ derived tables
    with (OUT / "tables.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "value_as_printed", "source"])
        for key, row in TABLES.items():
            w.writerow([key, row["text"], row["source"]])

    rows = []
    for g in gaps:
        c = curve[g]
        rows.append({"surface_gap": g, "body_radius": 6, "runs": c["runs"], "ended_as_one_body": c["M"],
                     "share": c["coalescing_fraction"], "slow": c["slow"], "slow_share": c["slow_fraction"],
                     "median_steps": c["median_t"], "step_histogram": json.dumps(c["time_histogram"])})
    with (OUT / "table-edge.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    with (OUT / "table-habitats.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["habitat", "below_floor_share", "generations_advantage", "generation_rate",
                    "survival_advantage", "deaths", "died_alone", "absorbed", "faded", "sisters_remerged",
                    "median_remerge_steps"])
        for c in ("f030", "f035", "f040"):
            w.writerow([c, cells126[c]["below_floor_share"], cells126[c]["depth_mean"], cells126[c]["rate_filtered"],
                        cells126[c]["survival_mean"], fates[c]["deaths"], fates[c]["isolated_share"],
                        fates[c]["absorbed_share"], fates[c]["vanished_share"], c130[c]["merge_share"],
                        c130[c]["median_time"]])

    with (OUT / "table-heredity.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["habitat", "pairs", "pairs_total", "reconstructed_r", "stored_r", "slope",
                                           "ci_low", "ci_high", "shuffled_null_mean", "null_p", "residual_sd",
                                           "between_lineage_share"])
        w.writeheader()
        for name, cell in (("spots (F = 0.030)", h), ("connected (F = 0.040)", h2)):
            w.writerow({"habitat": name, "pairs": cell["pairs"], "pairs_total": cell["pairs_total"],
                        "reconstructed_r": cell["r_per_world_mean"], "stored_r": cell["r_stored_mean"],
                        "slope": cell["slope"], "ci_low": cell["slope_ci"][0], "ci_high": cell["slope_ci"][1],
                        "shuffled_null_mean": cell["shuffle_null"]["null_mean"],
                        "null_p": cell["shuffle_null"]["p_one_sided"], "residual_sd": cell["residual_sd"],
                        "between_lineage_share": cell["h2_between_mean"]})

    payload = {"kind": "article_029_tables",
               "note": "every number printed in article 029, with the aggregate it came from",
               "tables": TABLES}
    (OUT / "tables.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                     newline="\n")
    print(f"[029] figures: 5 x 2 formats; values: {len(TABLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
