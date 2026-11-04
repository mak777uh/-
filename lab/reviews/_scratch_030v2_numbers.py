#!/usr/bin/env python
"""_scratch_030v2_numbers.py — reviewer's independent recomputation for article 030 v2.0 (§5.1, §5.2, §5.6-§5.8).

Run from repo root:
    python lab/reviews/_scratch_030v2_numbers.py            # all groups
    python lab/reviews/_scratch_030v2_numbers.py x173       # one section

No lab analysis script is imported or executed. Every number is read from the committed
aggregates in morphogenesis/experiments/E09_pond/ or recomputed here from raw stored
fields (medians, means, correlations, the x173 identifiability window from the committed
compact slices in morphogenesis/experiments/L1_field/).
"""
from __future__ import annotations

import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
LF = ROOT / "morphogenesis" / "experiments" / "L1_field"


def agg(name: str):
    return json.loads((POND / f"l1_field_{name}.json").read_text(encoding="utf-8"))


def line(path, value, note=""):
    extra = f"   # {note}" if note else ""
    print(f"    {path:70s} = {value}{extra}")


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / (sxx * syy) ** 0.5


# ----------------------------------------------------------------------------- §5.1
def s51():
    print("\n== §5.1 contact geometry, the window, the crossing ==")
    g = agg("x157_gap_geometry")
    fused = [r["g_fusion"] for r in g["runs_geometry"] if r.get("fused")]
    line("recomputed: median/min/max over fused runs_geometry.g_fusion",
         f"{st.median(fused):.2f} / {min(fused):.2f} / {max(fused):.2f}  (n={len(fused)})")
    line("x157_gap_geometry.contact_gap_median/min/max", 
         f"{g['contact_gap_median']} / {g['contact_gap_min']} / {g['contact_gap_max']}  (n={g['contact_gap_n']})")
    for r, d in sorted(g["by_radius"].items()):
        line(f"x157_gap_geometry.by_radius.{r}.g_fusion_median", d["g_fusion_median"])
    q = agg("x157_quantum")
    line("x157_quantum.window_width_median", q["window_width_median"])
    line("x157_quantum.window_width_p90", q["window_width_p90"])
    line("x157_quantum.threshold_low_median", q["threshold_low_median"])
    c = agg("x158_crossing")
    for r, d in sorted(c["by_radius"].items()):
        line(f"x158_crossing.by_radius.{r}.crossing_gap", d["crossing_gap"], f"range {d['crossing_range']}")
    line("x158_crossing.by_radius.r3.0.curve gap10", c["by_radius"]["r3.0"]["curve"][5])
    a = agg("x164_asymmetric")
    line("x164_asymmetric.by_arm.asym_g8.g_median", a["by_arm"]["asym_g8"]["g_median"])
    line("x164_asymmetric.by_arm.asym_g10.g_median", a["by_arm"]["asym_g10"]["g_median"])
    line("x164_asymmetric.by_arm.*.share", {k: v["share"] for k, v in a["by_arm"].items() if k.startswith("asym")})
    t = agg("x165_three_bodies")
    line("x165_three_bodies.pairwise_share_at_10", t["pairwise_share_at_10"])
    for g_, d in sorted(t["by_gap"].items(), key=lambda kv: int(kv[0])):
        line(f"x165_three_bodies.by_gap.{g_}.share_fused", d["share_fused"], f"{d['reached_one_component']}/{d['runs']}")
    x = agg("x166_threshold")
    line("x166_threshold.per_arm_median_spread", x["per_arm_median_spread"])
    line("x166_threshold.median_within_arm_sd", x["median_within_arm_sd"])
    b = agg("x168_inflow")
    line("x168_inflow (withdrawn) gap-11 arms",
         {k: (v["fused"], v["runs"]) for k, v in b["by_arm"].items() if v["gap"] == 11})
    cc = agg("x168c_inflow")
    line("x168c_inflow.share_at_gap11_by_rate", cc["share_at_gap11_by_rate"])
    line("x168c_inflow gap-11 arm runs (seeds per cell)",
         {k: v["runs"] for k, v in cc["by_arm"].items() if v["gap"] == 11})
    dd = agg("x168d_gap11")
    line("x168d_gap11.shares_gap11", dd["shares_gap11"])
    line("x168d_gap11 gap-11 arm runs (seeds per cell)",
         {k: v["runs"] for k, v in dd["by_cell"].items() if v["gap"] == 11})
    line("x168d_gap11.fisher_tests.0.026_vs_0.036", dd["fisher_tests"]["0.026_vs_0.036"])
    line("x168d_gap11.power.for_0.0_vs_0.3", dd["power"]["for_0.0_vs_0.3"])


# ----------------------------------------------------------------------------- §5.2
def s52():
    print("\n== §5.2 shape heredity, neighbour order, reversibility, seam, corridor ==")
    s = agg("x156_shape_heredity")
    for trait in ("log_elong", "log_width"):
        vals = {c: s["cells"][c]["traits"][trait]["slope"] for c in ("f030", "f040")}
        line(f"x156_shape_heredity.cells.*.traits.{trait}.slope", vals,
             f"mean={sum(vals.values())/2:.4f}")
    print("    (per-cell spread for reference:",
          {t: {c: s["cells"][c]["traits"][t]["slope"] for c in ("f030", "f040")}
           for t in ("log_elong", "log_width")}, ")")
    d = agg("x162b_decay")
    line("x162b_decay.by_order.*.slope", {k: v["slope"] for k, v in sorted(d["by_order"].items())})
    r = agg("x167b_reversibility")
    line("x167b_reversibility.merged.steps_to_division_median", r["merged"]["steps_to_division_median"])
    line("x167b_reversibility.single.steps_to_division_median", r["single"]["steps_to_division_median"])
    m, si = r["merged"]["values"], r["single"]["values"]
    pool = st.pstdev(m + si)
    line("recomputed from stored values: median diff / pooled sd",
         f"{15/pool:.3f}  (merged n={len(m)} mean={st.mean(m):.2f} sd={st.stdev(m):.2f}; "
         f"single n={len(si)} mean={st.mean(si):.2f} sd={st.stdev(si):.2f})")
    sm = agg("x169_seam")
    line("x169_seam.neck_measure.pair_ratio_median", sm["neck_measure"]["pair_ratio_median"])
    line("x169_seam.controls.positive_control_fires", sm["controls"]["positive_control_fires"])
    co = agg("x170_corridor")
    line("x170_corridor.medians", co["medians"])
    line("x170_corridor.spreads", co["spreads"])
    line("x170_corridor.extreme.difference / pooled_sd", f"{co['extreme']['difference']} / {co['extreme']['pooled_sd']}")
    cs = agg("x162_local_scale")
    print("    x162_local_scale.by_habitat keys:", list(cs["by_habitat"].keys()))
    for h, hd in cs["by_habitat"].items():
        line(f"x162_local_scale.by_habitat.{h}", json.dumps(
            {k: hd.get(k) for k in ("runs", "pairs", "partial_on_mother_radius", "readout", "verdict")})[:220])
    x161 = agg("x161_discrete")
    line("x161_discrete.traits", {k: (v.get("slope"), v.get("n")) for k, v in x161["traits"].items()})
    line("x161_discrete.nulls", x161["nulls"])


# ----------------------------------------------------------------------------- §5.6
def s56():
    print("\n== §5.6 the corridor, the forecast, the bridge, the edge ==")
    s = agg("x171_corridor_sizes")
    line("x171_corridor_sizes.medians", s["medians"])
    line("x171_corridor_sizes.spreads", s["spreads"])
    line("x171_corridor_sizes.difference", s["difference"])
    f = agg("x172_forecast")
    line("x172_forecast.predictions.corridor / observed.corridor_median",
         f"{f['predictions']['corridor']} / {f['observed']['corridor_median']}")
    line("x172_forecast.observed fused/runs", f"{f['observed']['fused']}/{f['observed']['runs']}")
    line("x172_forecast.predictions.share", f["predictions"]["share"])
    b = agg("x173_bridge")
    line("x173_bridge.split", b["split"])
    g = agg("x174_gap_corridor")
    line("x174_gap_corridor.medians", g["medians"])
    line("x174_gap_corridor.difference", g["difference"])
    line("x174_gap_corridor.across_arms pearson/spearman/n",
         f"{g['across_arms']['pearson_share_vs_corridor']} / {g['across_arms']['spearman_share_vs_corridor']} / {g['across_arms']['n']}")
    arms = [c["arm"] for c in g["across_arms"]["cells"]]
    line("x174_gap_corridor.across_arms arms", f"{len(arms)} rows, {len(set(arms))} distinct")
    line("x174_gap_corridor.across_arms duplicate arms", [a for a in set(arms) if arms.count(a) > 1])
    i = agg("x175_interior")
    line("x175_interior.observed corridor_median / share", f"{i['observed']['corridor_median']} / {i['observed']['share']} ({i['observed']['fused']}/{i['observed']['runs']})")
    line("x175_interior.predictions", i["predictions"])
    p = agg("x176_past_crossing")
    line("x176_past_crossing.observed fused/runs", f"{p['observed']['fused']}/{p['observed']['runs']}")
    e = agg("x177_edge")
    line("x177_edge.observed fused/runs", f"{e['observed']['fused']}/{e['observed']['runs']}")
    c = agg("x178_cliff")
    line("x178_cliff.observed", f"{c['observed']['fused']}/{c['observed']['runs']} = {c['observed']['share']}, wilson {c['observed']['wilson']}")
    line("x178_cliff.references", c["references"])


# ----------------------------------------------------------------------------- §5.7
def s57():
    print("\n== §5.7 the table, the dispersion, the redraw, the ladder ==")
    t = agg("x179_crossing_table")
    line("x179_crossing_table two_body_cells / two_body_runs / files_scanned / other_cells",
         f"{len(t['two_body_cells'])} / {t['two_body_runs']} / {t['files_scanned']} / {len(t['other_cells'])} (runs {sum(c['runs'] for c in t['other_cells'])})")
    line("x179_crossing_table heterogeneous cells",
         [(c["radius"], c["gap"]) for c in t["two_body_cells"] if c.get("heterogeneous")])
    line("x179_crossing_table radii", sorted({round(c["radius"], 2) for c in t["two_body_cells"]}))
    for c in t["two_body_cells"]:
        if (round(c["radius"], 1), c["gap"]) in ((3.0, 8), (6.0, 10)):
            line(f"x179 cell r={c['radius']} g={c['gap']} F={c['F']}", f"{c['fused']}/{c['runs']} = {c['share']}")
    d = agg("x180_dispersion")
    cells = d["cells"]
    line("x180_dispersion cells / sum runs in cells",
         f"{len(cells)} / {sum(c['runs'] for c in cells)}")
    line("recomputed mean point_biserial over cells", round(st.mean([c["point_biserial"] for c in cells]), 4))
    line("x180_dispersion.mean_point_biserial / pooled_point_biserial / informative_runs",
         f"{d['mean_point_biserial']} / {d['pooled_point_biserial']} / {d['informative_runs']}")
    line("x180_dispersion.fused_higher_g / z_top_vs_bottom", f"{d['fused_higher_g']} / {d['z_top_vs_bottom']}")
    line("x180_dispersion.local_inflow_bands shares",
         [(b["share"], f"{b['fused']}/{b['runs']}") for b in d["local_inflow_bands"]])
    w = agg("x181_worst_cell")
    line("x181_worst_cell.observed", f"{w['observed']['fused']}/{w['observed']['runs']} = {w['observed']['share']}, wilson {w['observed']['wilson']}")
    line("x181_worst_cell.registered_share_interval", w["registered_share_interval"])
    line("x181_worst_cell.references", w["references"])
    lc = agg("x183_local_collapse")
    line("x183_local_collapse.ladder_runs", lc["ladder_runs"])
    line("x183_local_collapse.candidates count", len(lc["candidates"]), list(lc["candidates"].keys()))
    for k, v in lc["candidates"].items():
        line(f"x183 {k}", f"AUC {v['auc_overall']}, within {v['mean_auc_within']}, deviance {v['deviance']}")
    li = agg("x182_local_inflow")
    line("x182_local_inflow.trend", li["trend"])
    line("x182_local_inflow levels G_actual_mean / share",
         [(l["G_actual_mean"], l["share"]) for l in li["levels"]])


# ----------------------------------------------------------------------------- §5.8
def s58():
    print("\n== §5.8 the withdrawn nucleation reading and the bridge ==")
    x = agg("x188_nucleation_identity")
    line("x188_nucleation_identity.radius6_warm_minus_cold / bar", f"{x['radius6_warm_minus_cold']} / {x['bar']}")
    diffs = {k: round(v["groups"]["r6_g9_warm"] - v["groups"]["r6_g9_cold"], 6) for k, v in x["sensitivity"].items()}
    line("x188 recomputed warm-cold per sensitivity variant", diffs)
    line("x188 min / max of those variants", f"{min(diffs.values())} / {max(diffs.values())}")
    line("x188_nucleation_identity.outcome_crosstab", x["outcome_crosstab"])
    b = agg("x189_bridge")
    line("x189_bridge.radius6_warm_minus_cold / radius3_warm_minus_cold",
         f"{b['radius6_warm_minus_cold']} / {b['radius3_warm_minus_cold']}")
    line("x189_bridge.radius6_contact_warm_minus_cold", b["radius6_contact_warm_minus_cold"])
    line("x189_bridge.tightest_slice_at_step_40_runs (of 12)", b["tightest_slice_at_step_40_runs"])
    for k, v in b["groups"].items():
        line(f"x189_bridge.groups.{k}", f"runs {v['runs']}, distinct_sites {v['distinct_sites']}")


# ------------------------------------------------------------------- not in an aggregate
def x173():
    print("\n== x173 identifiability window (recomputed from committed compact slices) ==")
    files = sorted(glob.glob(str(LF / "x173_g11_*.compact.json")))
    print(f"    x173_g11 compact slices: {len(files)}")
    counts = []
    for p in files:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        n_both = 0
        for _step, comps in d["series"]:
            ids = {c[0] for c in comps}
            if 1 in ids and 2 in ids:
                n_both += 1
        counts.append((Path(p).name, n_both, len(d["series"])))
    for name, n_both, n_tot in counts:
        print(f"      {name}: pair present in {n_both} of {n_tot} sampled steps")
    print(f"    recomputed range of identifiable steps: {min(c[1] for c in counts)} to "
          f"{max(c[1] for c in counts)} of {counts[0][2]}")


SECTIONS = {"s51": s51, "s52": s52, "s56": s56, "s57": s57, "s58": s58, "x173": x173}

if __name__ == "__main__":
    want = sys.argv[1:] or list(SECTIONS)
    for w in want:
        SECTIONS[w]()
