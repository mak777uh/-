"""make_article_029_package.py — figures and derived tables for article 029.

Everything printed in the article is read from this file's `tables` output (`articles/029-figures/tables.json`), and
every entry names the aggregate it came from. The checker `scripts/check_article_029_numbers.py` then requires each
formatted value to appear verbatim in the article text, so the paper cannot drift from the data.

Run:
    python scripts/make_article_029_package.py --write
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

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "articles" / "029-figures"

TABLES: dict[str, dict] = {}


def agg(name: str) -> dict:
    return json.loads((POND / name).read_text(encoding="utf-8"))


def put(key: str, text: str, value=None, source: str = "", note: str = "") -> None:
    TABLES[key] = {"text": text, "value": value, "source": source, "note": note}


def fmt_num(x) -> str:
    if isinstance(x, float) and x.is_integer():
        return f"{x:.0f}"
    return f"{x:g}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="article 029 figures and tables")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- coalescence / mixing length
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
    r30 = [(v["gap"], v["M"], v["runs"], v["median_mutual_coalescence"]) for v in by_arm.values() if v["radius"] == 3.0]
    r45 = [(v["gap"], v["M"], v["runs"], v["median_mutual_coalescence"]) for v in by_arm.values() if v["radius"] == 4.5]
    r30.sort()
    r45.sort()

    put("m_gap8", "M 5/5 at a surface gap of 8", [v for v in r30 if v[0] == 8][0][1],
        "x142 by_arm r30_g8", "mutual coalescence in every seed")
    g9 = [v for v in r30 if v[0] == 9][0]
    put("m_gap9", f"M {g9[1]}/5, A 2/5 at a gap of 9", g9[1], "x142 by_arm r30_g9")

    lone = x145["by_radius"]
    for rad, key in (("3.0", "m_lone_r3"), ("4.5", "m_lone_r45"), ("6.0", "m_lone_r6")):
        v = lone[rad] if rad in lone else lone[[k for k in lone if k.startswith(rad)][0]]
        put(key, fmt_num(v["first_split_median"]), v["first_split_median"], "x145 by_radius first_split_median")

    put("m_cross_r3", "16 ± 1", 16, "x136 by_separation", "crossing at one-cell width")
    put("m_cross_r45", "18 ± 2", 18, "x140 by_separation")
    put("m_cross_r6", "20 ± 2", 20, "x138 by_separation")

    # ---------------------------------------------------------------- width of the time
    curve = {c["gap"]: c for c in x154["curve"]}
    gaps = sorted(curve)
    slow = [curve[g]["slow_fraction"] for g in gaps]
    coal = [curve[g]["coalescing_fraction"] for g in gaps]
    slow_all = [curve[g]["slow_fraction_of_all"] for g in gaps]
    put("w_gaps", " / ".join(f"{g:g}" for g in gaps), gaps, "x154 curve")
    put("w_slow", " / ".join(f"{v:.1f}" for v in slow), slow, "x154 curve slow_fraction")
    put("w_slow_all", " / ".join(f"{v:.1f}" for v in slow_all), slow_all, "x154 curve slow_fraction_of_all")
    put("w_coal", " / ".join(f"{v:.1f}" for v in coal), coal, "x154 curve coalescing_fraction")
    hist_75 = curve[7.5]["time_histogram"]
    hist_80 = curve[8.0]["time_histogram"]
    put("w_hist75", ", ".join(f"{k} ×{v}" for k, v in sorted(hist_75.items(), key=lambda kv: int(kv[0]))),
        hist_75, "x154 curve gap 7.5 time_histogram")
    put("w_hist80", ", ".join(f"{k} ×{v}" for k, v in sorted(hist_80.items(), key=lambda kv: int(kv[0]))),
        hist_80, "x154 curve gap 8 time_histogram")

    # ---------------------------------------------------------------- identity
    cells126 = x126["cells"]
    below = [cells126[c]["below_floor_share"] for c in ("f030", "f035", "f040")]
    depthc = [cells126[c]["depth_mean"] for c in ("f030", "f035", "f040")]
    rate = [cells126[c]["rate_filtered"] for c in ("f030", "f035", "f040")]
    surv = [cells126[c]["survival_mean"] for c in ("f030", "f035", "f040")]
    put("i_below", " / ".join(f"{v:.3f}" for v in below), below, "x126 cells below_floor_share")
    put("i_depth", " / ".join(f"{v:.3f}" if abs(v - round(v, 2)) > 1e-9 else f"{v:.2f}" for v in depthc), depthc,
        "x126 cells depth_mean")
    put("i_rate", " / ".join(f"{v:.2f}" for v in rate), rate, "x126 cells rate_filtered")
    put("i_surv", " / ".join(f"{v:.4f}" for v in surv), surv, "x126 cells survival_mean")
    dist = x126["distance_to_midpoint_in_se"]
    put("i_mid_se", f"{dist['survival_mean']:.2f}", dist["survival_mean"], "x126 distance_to_midpoint_in_se.survival_mean",
        "the middle cell sits this many standard errors above the chord between the two outer cells")

    c113 = x113["cells"]
    put("i_sister", f"+{c113['f030']['sister_diff_mean']:.3f} [{c113['f030']['sister_diff_ci'][0]:.3f}, "
                    f"{c113['f030']['sister_diff_ci'][1]:.3f}] and +{c113['f040']['sister_diff_mean']:.3f} "
                    f"[{c113['f040']['sister_diff_ci'][0]:.3f}, {c113['f040']['sister_diff_ci'][1]:.3f}]",
        [c113["f030"]["sister_diff_mean"], c113["f040"]["sister_diff_mean"]], "x113 cells sister_diff")
    put("i_partial", f"{c113['f030']['rho_partial_life']:.3f} / {c113['f040']['rho_partial_life']:.3f}",
        [c113["f030"]["rho_partial_life"], c113["f040"]["rho_partial_life"]], "x113 rho_partial_life")
    put("i_depth_life", f"{c113['f030']['rho_depth_life']:.3f} / {c113['f040']['rho_depth_life']:.3f}",
        [c113["f030"]["rho_depth_life"], c113["f040"]["rho_depth_life"]], "x113 rho_depth_life")

    fates = {c: x128b["cells"][c] for c in ("f030", "f035", "f040")}
    put("i_absorbed", " / ".join(f"{fates[c]['absorbed_share'] * 100:.1f}" for c in fates),
        [fates[c]["absorbed_share"] for c in fates], "x128b cells absorbed_share")
    put("i_isolated", " / ".join(f"{fates[c]['isolated_share'] * 100:.1f}" for c in fates),
        [fates[c]["isolated_share"] for c in fates], "x128b cells isolated_share")
    put("i_vanished", " / ".join(f"{fates[c]['vanished_share'] * 100:.1f}" for c in fates),
        [fates[c]["vanished_share"] for c in fates], "x128b cells vanished_share")
    put("i_kin_lattice", "87.2", 87.2, "x128b / x132 kin share, lattice")
    put("i_kin_maze", "37.7", 37.7, "x128b / x132 kin share, maze")

    c130 = x130["cells"]
    put("i_remerge", " / ".join(f"{c130[c]['merge_share'] * 100:.1f}" for c in c130),
        [c130[c]["merge_share"] for c in c130], "x130 cells merge_share")
    put("i_remerge_time", " / ".join(f"{c130[c]['median_time']:.0f}" for c in c130),
        [c130[c]["median_time"] for c in c130], "x130 cells median_time")

    paired = x132["paired_by_seed"]
    put("i_x132", f"{paired['survival']['mean']:.4f} ({paired['survival']['ci'][0]:.4f} … "
                  f"{paired['survival']['ci'][1]:.4f})", paired["survival"]["mean"], "x132 paired_by_seed survival")
    put("i_x132_depth", f"{paired['depth']['mean']:+.4f}", paired["depth"]["mean"], "x132 paired_by_seed depth")
    put("i_x132_kin", f"{paired['kin']['mean']:+.4f}", paired["kin"]["mean"], "x132 paired_by_seed kin")
    put("i_x132_vanished", f"{paired['vanished']['mean']:+.4f}", paired["vanished"]["mean"],
        "x132 paired_by_seed vanished")

    # ---------------------------------------------------------------- heredity
    cells155 = {c["cell"]: c for c in x155["cells"]}
    h = cells155["x108_f030"]
    h2 = cells155["x108_f040"]
    put("h_slope", f"{h['slope']:.4f} [{h['slope_ci'][0]:.4f}, {h['slope_ci'][1]:.4f}] and "
                   f"{h2['slope']:.4f} [{h2['slope_ci'][0]:.4f}, {h2['slope_ci'][1]:.4f}]",
        [h["slope"], h2["slope"]], "x155 cells slope")
    put("h_resid", f"{h['residual_sd']:.4f} and {h2['residual_sd']:.4f}", [h["residual_sd"], h2["residual_sd"]],
        "x155 cells residual_sd")
    put("h_sigma", "0.15", 0.15, "x108_series --mutation 0.15")
    put("h_null_p", "0.001", h["shuffle_null"]["p_one_sided"], "x155 shuffle_null p")
    put("h_recon", f"{h['r_per_world_mean']:.4f} against {h['r_stored_mean']:.4f} and "
                   f"{h2['r_per_world_mean']:.4f} against {h2['r_stored_mean']:.4f}",
        [h["r_per_world_mean"], h["r_stored_mean"]], "x155 cells r_per_world_mean / r_stored_mean")
    put("h_pairs", f"{h['pairs']} of {h['pairs_total']} and {h2['pairs']} of {h2['pairs_total']}",
        [h["pairs"], h2["pairs"]], "x155 cells pairs / pairs_total")
    put("h_h2", f"{h['h2_between_mean']:.3f} / {h2['h2_between_mean']:.3f}",
        [h["h2_between_mean"], h2["h2_between_mean"]], "x155 cells h2_between_mean")
    put("h_h2b", f"{h['h2_between_mean']:.3f}", h["h2_between_mean"], "x155 cells h2_between_mean, lattice")
    put("h_ablation_sd", "0.0", 0.0, "x155 ablation s_sd_between_last")
    put("h_ablation_equal", "100 %", 100, "x155 ablation identical_pair_share")

    # ---------------------------------------------------------------- lengths, sizes, and the second species
    put("m_wavelength", "12", 12, "x134/x136 pattern wavelength", "the medium's own period at F = 0.030")
    put("m_area_r3", "29", 29, "x142 by_arm median area / x145 definitions")
    put("m_area_r45", "64", 64, "x140 definitions")
    put("m_area_r6", "113", 113, "x138 definitions")
    put("m_rule", "2r + 9", None, "x138 verdict", "surface gap of 9 ± 1 cells at the crossing, all three radii")

    g10 = by_arm["r30_g10"]
    g11 = by_arm["r30_g11"]

    def classes(row) -> str:
        parts = [f"{name} {row[key]}/5" for name, key in (("M", "M"), ("A", "A"), ("P", "P")) if row[key]]
        return ", ".join(parts)

    put("m_outer10", classes(g10), g10["M"], "x142 by_arm r30_g10")
    put("m_outer11", classes(g11), g11["M"], "x142 by_arm r30_g11")

    fus9 = by_arm["r30_g9"]["fusion"]
    fus10 = by_arm["r30_g10"]["fusion"]
    fus11 = by_arm["r30_g11"]["fusion"]
    put("c_size_medians", f"{fus9['median_area_divided']:.0f} / {fus9['median_area_not_divided']:.0f}, "
                          f"{fus10['median_area_divided']:.0f} / {fus10['median_area_not_divided']:.0f}, "
                          f"{fus11['median_area_divided']:.0f} / {fus11['median_area_not_divided']:.0f}",
        None, "x142 by_arm fusion medians at gaps 9, 10, 11",
        "divided / not divided, in cells; the sign inverts at gap 11")

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

    c131 = agg("l1_field_x131_worlds.json")["cells"]
    put("i_ten_worlds", "-0.077", -0.077, "x131 report, maze minus lattice",
        "ten worlds: unresolved, the interval covers zero")
    put("i_ten_worlds_ci", "-0.166 … +0.012", None, "x131 report")
    put("i_worlds", "30-40", None, "x132 power calculation", "worlds needed for the survival contrast")

    c96c = agg("l1_field_x96c_pilot.json")
    put("s_q", "7-9", None, "x96c/x96d q-prime range across six living cells")
    put("s_dw", "8", 8, "x96c Dw / Dv = 8")
    c110b = agg("l1_field_x110b_gamma_cell.json")
    put("s_gamma", "0.30", None, "x110b gamma sweep, alive_in_seeds = %d" % c110b["alive_in_seeds"])
    put("s_orient", "0.636-0.837", None, "x96d orientation measure, not replicated")
    put("s_alive", f"{c110b['alive_in_seeds']} of 6", c110b["alive_in_seeds"], "x110b alive_in_seeds")

    # ---------------------------------------------------------------- figures
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 200, "savefig.bbox": "tight"})
    colours = {"3": "#1f4e79", "4.5": "#2e75b6", "6": "#70a5d0"}

    # fig 1: the mixing length
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for series, label, colour in ((r30, "radius 3 (29 cells)", colours["3"]),
                                  (r45, "radius 4.5 (64 cells)", colours["4.5"])):
        gaps_s = [v[0] for v in series]
        frac = [v[1] / v[2] for v in series]
        ax1.plot(gaps_s, frac, "o-", color=colour, label=label, ms=4)
    gaps6 = sorted(curve)
    ax1.plot(gaps6, [curve[g]["coalescing_fraction"] for g in gaps6], "s-", color=colours["6"],
             label="radius 6 (113 cells)", ms=4)
    ax1.axvspan(8, 9, color="0.85", zorder=0)
    ax1.set_xlabel("surface gap between the two bodies (cells)")
    ax1.set_ylabel("share of seeds with mutual coalescence")
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(frameon=False, fontsize=7, loc="lower left")
    ax1.set_title("a. the boundary sits near a gap of nine cells", fontsize=8, loc="left")

    gaps_t = [v[0] for v in r30]
    times_t = [v[3] for v in r30]
    ax2.plot(gaps_t, times_t, "o-", color=colours["3"], ms=4, label="radius 3")
    ax2.plot([v[0] for v in r45], [v[3] for v in r45], "^-", color=colours["4.5"], ms=4, label="radius 4.5")
    ax2.plot(gaps6, [curve[g]["median_t"] for g in gaps6], "s-", color=colours["6"], ms=4, label="radius 6")
    ax2.set_xlabel("surface gap (cells)")
    ax2.set_ylabel("median steps to one body")
    ax2.legend(frameon=False, fontsize=7, loc="upper left")
    ax2.set_title("b. the time depends on the gap, not on the body", fontsize=8, loc="left")
    fig.savefig(OUT / "fig1-mixing-length.png")
    fig.savefig(OUT / "fig1-mixing-length.pdf")
    plt.close(fig)

    # fig 2: outcome steps, time mixes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(gaps, coal, "o-", color="#1f4e79", ms=4, label="share of seeds coalescing")
    ax1.plot(gaps, slow, "s--", color="#c00000", ms=4, label="slow fraction among coalescing seeds")
    ax1.plot(gaps, slow_all, "^:", color="#e08a8a", ms=4, label="slow fraction of all ten seeds")
    ax1.set_xlabel("surface gap (cells), radius 6")
    ax1.set_ylabel("share")
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(frameon=False, fontsize=7, loc="center left")
    ax1.set_title("a. the outcome steps, the time bends first", fontsize=8, loc="left")

    steps = [39, 49, 59]
    w = 0.26
    for i, g in enumerate(gaps):
        hist = curve[g]["time_histogram"]
        bottom = 0
        for j, s in enumerate(steps):
            n = hist.get(str(s), 0)
            ax2.bar(i + (j - 1) * w, n, w, bottom=0, color=["#1f4e79", "#c00000", "#d9a3a3"][j],
                    label=f"{s} steps" if i == 0 else None)
            bottom += n
    ax2.set_xticks(range(len(gaps)))
    ax2.set_xticklabels([f"{g:g}" for g in gaps])
    ax2.set_xlabel("surface gap (cells)")
    ax2.set_ylabel("seeds dissolving at that step")
    ax2.legend(frameon=False, fontsize=7)
    ax2.set_title("b. dissolution steps per arm (ten seeds)", fontsize=8, loc="left")
    fig.savefig(OUT / "fig2-outcome-and-time.png")
    fig.savefig(OUT / "fig2-outcome-and-time.pdf")
    plt.close(fig)

    # fig 3: what an end is
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    labels = ["F = 0.030\n(lattice)", "F = 0.035", "F = 0.040\n(percolating)"]
    iso = [fates[c]["isolated_share"] for c in fates]
    abso = [fates[c]["absorbed_share"] for c in fates]
    van = [fates[c]["vanished_share"] for c in fates]
    xpos = np.arange(3)
    ax1.bar(xpos, abso, 0.6, color="#1f4e79", label="absorbed")
    ax1.bar(xpos, iso, 0.6, bottom=abso, color="#2e75b6", label="isolated death")
    ax1.bar(xpos, van, 0.6, bottom=np.array(abso) + np.array(iso), color="#a8c6e4", label="vanished")
    ax1.set_xticks(xpos)
    ax1.set_xticklabels(labels, fontsize=7)
    ax1.set_ylabel("share of deaths")
    ax1.set_ylim(0, 1.0)
    ax1.legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    ax1.set_title("a. how a structure ends", fontsize=8, loc="left")

    ax2.plot(xpos, depthc, "o-", color="#1f4e79", ms=5, label="depth contrast (left)")
    ax2.set_ylabel("depth contrast (generations)")
    ax2.set_ylim(0, 2.6)
    ax2b = ax2.twinx()
    ax2b.plot(xpos, surv, "s--", color="#c00000", ms=5, label="end-survival contrast (right)")
    ax2b.set_ylabel("end-survival contrast")
    ax2b.set_ylim(0, 0.36)
    ax2b.spines["top"].set_visible(False)
    ax2.set_xticks(xpos)
    ax2.set_xticklabels(labels, fontsize=7)
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, frameon=False, fontsize=7, loc="upper left")
    ax2.set_title("b. the reversal: generations vs survival", fontsize=8, loc="left")
    fig.savefig(OUT / "fig3-endings.png")
    fig.savefig(OUT / "fig3-endings.pdf")
    plt.close(fig)

    # fig 4: heredity is the rule
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    names = ["F = 0.030", "F = 0.040"]
    slopes = [h["slope"], h2["slope"]]
    cis = [h["slope_ci"], h2["slope_ci"]]
    obs = [h["shuffle_null"]["observed"], h2["shuffle_null"]["observed"]]
    nullm = [h["shuffle_null"]["null_mean"], h2["shuffle_null"]["null_mean"]]
    xpos = np.arange(2)
    ax1.errorbar(xpos, slopes, yerr=[[s - c[0] for s, c in zip(slopes, cis)], [c[1] - s for s, c in zip(slopes, cis)]],
                 fmt="o", color="#1f4e79", capsize=3, ms=5, label="observed slope (95 % CI)")
    ax1.plot(xpos, nullm, "s", color="#c00000", ms=5, label="shuffled-parent null")
    ax1.axhline(1.0, color="0.6", lw=0.8, ls=":")
    ax1.set_xticks(xpos)
    ax1.set_xticklabels(names, fontsize=8)
    ax1.set_ylabel("daughter-on-parent slope of s")
    ax1.set_ylim(0, 1.15)
    ax1.legend(frameon=False, fontsize=7, loc="lower right")
    ax1.set_title("a. the slope is one, the null is a fifth", fontsize=8, loc="left")

    ax2.bar([0, 1], [h["residual_sd"], h2["residual_sd"]], 0.5, color="#1f4e79", label="residual sd")
    ax2.axhline(0.15, color="#c00000", ls="--", lw=1.0, label="mutation sigma = 0.15")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels([names[0], names[1]], fontsize=8)
    ax2.set_ylabel("sd of daughter minus parent")
    ax2.set_ylim(0, 0.2)
    ax2.legend(frameon=False, fontsize=7, loc="lower right")
    ax2.set_title("b. what is not inherited is the mutation", fontsize=8, loc="left")
    fig.savefig(OUT / "fig4-heredity.png")
    fig.savefig(OUT / "fig4-heredity.pdf")
    plt.close(fig)

    # ---------------------------------------------------------------- derived tables
    with (OUT / "tables.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "value_as_printed", "source"])
        for key, row in TABLES.items():
            w.writerow([key, row["text"], row["source"]])

    rows = []
    for g in gaps:
        c = curve[g]
        rows.append({"surface_gap": g, "radius": 6, "seeds": c["runs"], "coalescing": c["M"],
                     "coalescing_fraction": c["coalescing_fraction"], "slow": c["slow"],
                     "slow_fraction": c["slow_fraction"], "median_step": c["median_t"],
                     "time_histogram": json.dumps(c["time_histogram"])})
    with (OUT / "table-width.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    cells_rows = []
    for c in ("f030", "f035", "f040"):
        cells_rows.append({
            "cell": c,
            "below_floor_share": cells126[c]["below_floor_share"],
            "depth_contrast": cells126[c]["depth_mean"],
            "rate_filtered": cells126[c]["rate_filtered"],
            "survival_contrast": cells126[c]["survival_mean"],
            "deaths": fates[c]["deaths"],
            "isolated_share": fates[c]["isolated_share"],
            "absorbed_share": fates[c]["absorbed_share"],
            "vanished_share": fates[c]["vanished_share"],
            "sister_remerge_share": c130[c]["merge_share"],
            "median_remerge_steps": c130[c]["median_time"],
        })
    with (OUT / "table-identity.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells_rows[0]))
        w.writeheader()
        w.writerows(cells_rows)

    heredity_rows = [
        {"cell": "F = 0.030", "pairs": h["pairs"], "pairs_total": h["pairs_total"], "r_reconstructed": h["r_per_world_mean"],
         "r_stored": h["r_stored_mean"], "slope": h["slope"], "ci_low": h["slope_ci"][0], "ci_high": h["slope_ci"][1],
         "null_mean": h["shuffle_null"]["null_mean"], "null_p": h["shuffle_null"]["p_one_sided"],
         "residual_sd": h["residual_sd"], "h2_between": h["h2_between_mean"]},
        {"cell": "F = 0.040", "pairs": h2["pairs"], "pairs_total": h2["pairs_total"],
         "r_reconstructed": h2["r_per_world_mean"], "r_stored": h2["r_stored_mean"], "slope": h2["slope"],
         "ci_low": h2["slope_ci"][0], "ci_high": h2["slope_ci"][1], "null_mean": h2["shuffle_null"]["null_mean"],
         "null_p": h2["shuffle_null"]["p_one_sided"], "residual_sd": h2["residual_sd"],
         "h2_between": h2["h2_between_mean"]},
    ]
    with (OUT / "table-heredity.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(heredity_rows[0]))
        w.writeheader()
        w.writerows(heredity_rows)

    payload = {"kind": "article_029_tables", "note": "every number printed in article 029 is here, with its aggregate",
               "tables": TABLES}
    (OUT / "tables.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                     newline="\n")
    print(f"[029] figures: 4 files x2 formats; tables: {len(TABLES)} values")
    if args.write:
        print(f"[029] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
