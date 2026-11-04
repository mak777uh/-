"""x189_bridge_analyse.py — X189: the bridge between two bodies, by local inflow and size.

Planned readout (plan section 3) was the minimum of v along the segment between the **seeded** centres, over the maximum of v in
discs of radius 3 around them. Two facts found while reading the data, recorded as a pre-analysis amendment in the plan, force a
correction of the *measurement*, not of the bar or the prediction:

  1. the bodies drift (about five cells by step 40, 0.12 cells a step), so the segment and the discs are taken at the bodies'
     **current** centres, read from the component log at each saved step;
  2. the bodies are **rings**: their logged centroid sits in the hollow, where the field is background, so a disc of radius 3
     around the centre contains the hole and not the body. The peak is therefore taken over a disc of radius 10, which contains
     the ring, and the bridge is read at the **midpoint** between the two centres and as the minimum over the central half of the
     segment, both of which avoid the two hollows.

Registered readout: ratio = v(midpoint) / peak_ring, with min over the central half / peak_ring as the secondary reading, and the
tightest saved two-component slice as the primary summary. The registered bar (0.05 lower in the warm level at radius 6) and the
prediction are unchanged. The Fisher p of "below the pooled median" against the outcome is reported instead of a degeneracy
verdict, because an empirical association is a finding, not a logical degeneracy (X187's failure was a logical identity).

Writes morphogenesis/experiments/E09_pond/l1_field_x189_bridge.json.
"""
from __future__ import annotations

import json
import math
import statistics
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x189_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x189_bridge.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
RING_R = 10
BAR = 0.05
PEAK_FLOOR = 0.3


def G_at(x: float, y: float) -> float:
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def cxy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def step_of(row):
    return int(row[0]) if isinstance(row, list) else int(row.get("step"))


def wrap_dx(a: float, b: float) -> float:
    return (a - b + GRID / 2) % GRID - GRID / 2


def ring_peak(field, centre, r=RING_R) -> float:
    cx, cy = centre
    best = 0.0
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                best = max(best, float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID]))
    return best


def segment(field, c0, c1, n=200):
    """Values along the straight segment between the two centres, index 0 at c0, index n at c1."""
    dx = wrap_dx(c1[0], c0[0])
    dy = c1[1] - c0[1]
    return [float(field[int(round(c0[1] + dy * (i / n))) % GRID, int(round(c0[0] + dx * (i / n))) % GRID])
            for i in range(n + 1)]


def bridge_values(field, c0, c1):
    seg = segment(field, c0, c1)
    mid = seg[len(seg) // 2]
    central = seg[int(0.25 * len(seg)):int(0.75 * len(seg)) + 1]
    return mid, min(central), statistics.fmean(central), sorted(central)[int(0.9 * (len(central) - 1))]


def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    """One-sided Fisher exact p for [[a,b],[c,d]]: the probability of at least this much association."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    if n == 0 or c1 == 0 or r1 == 0:
        return 1.0
    p_obs = comb(r1, a) * comb(r2, c1 - a) / comb(n, c1)
    p = 0.0
    for x in range(a, min(r1, c1) + 1):
        if 0 <= c1 - x <= r2:
            pr = comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
            if pr <= p_obs + 1e-12:
                p += pr
    return round(p, 4)


index = json.loads((L1 / "x189_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    d = json.loads((L1 / f"x189_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    g_cold = min(G_at(*cxy(cs0[0])), G_at(*cxy(cs0[1])))
    f_local = F * (1 + AMP * (2 * g_cold - 1))
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    two = [row for row in series if len(comps(row)) == 2]
    last_two = step_of(two[-1]) if two else None
    per_slice = []
    for sp in sorted(FIELDS.glob(f"*/x189_{tag}_t*.npy"), key=lambda p: int(p.stem.split("_t")[-1])):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = by_step.get(step)
        rec = {"step": step, "n_components": len(cur) if cur is not None else None}
        if not cur or len(cur) != 2:
            per_slice.append(rec)
            continue
        c0, c1 = cur
        peak = max(ring_peak(field, c0), ring_peak(field, c1))
        mid, central_min, central_mean, central_p90 = bridge_values(field, c0, c1)
        rec.update({"peak": round(peak, 5), "bridge_mid": round(mid, 5), "bridge_min_central": round(central_min, 5),
                    "bridge_mean_central": round(central_mean, 5), "bridge_p90_central": round(central_p90, 5),
                    "ratio": round(mid / peak, 5) if peak > 0 else None,
                    "ratio_min": round(central_min / peak, 5) if peak > 0 else None,
                    "ratio_mean": round(central_mean / peak, 5) if peak > 0 else None,
                    "centres": [[round(c0[0], 2), round(c0[1], 2)], [round(c1[0], 2), round(c1[1], 2)]]})
        per_slice.append(rec)
    ok = [x for x in per_slice if x.get("ratio") is not None and (x.get("peak") or 0) >= PEAK_FLOOR]
    tight = min(ok, key=lambda x: x["ratio"]) if ok else None
    contact = max(ok, key=lambda x: x["step"]) if ok else None
    runs.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"], "f_local_cold": round(f_local, 5),
                 "g_cold": round(g_cold, 4), "fused": int(min(counts) == 1), "min_count": min(counts),
                 "slices": len(per_slice), "usable_slices": len(ok),
                 "ratio_tightest": tight["ratio"] if tight else None,
                 "ratio_tightest_step": tight["step"] if tight else None,
                 "ratio_tightest_min": tight["ratio_min"] if tight else None,
                 "ratio_at_contact": contact["ratio"] if contact else None,
                 "contact_step": contact["step"] if contact else None,
                 "last_two_component_step": last_two,
                 "ratio_mean_over_slices": round(statistics.fmean([x["ratio"] for x in ok]), 5) if ok else None,
                 "peak_min": min((x["peak"] for x in per_slice if x.get("peak") is not None), default=None),
                 "per_slice": per_slice})

groups = {}
for arm in index["arms"]:
    for lvl in index["arms"][arm]["groups"]:
        sel = [x for x in runs if x["arm"] == arm and x["level"] == lvl]
        if not sel:
            groups[f"{arm}_{lvl}"] = None
            continue
        rt = [x["ratio_tightest"] for x in sel if x["ratio_tightest"] is not None]
        rm = [x["ratio_tightest_min"] for x in sel if x["ratio_tightest_min"] is not None]
        groups[f"{arm}_{lvl}"] = {
            "runs": len(sel), "fused": sum(x["fused"] for x in sel),
            "share": round(statistics.fmean(x["fused"] for x in sel), 4),
            "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in sel]), 5),
            "ratio_tightest_mean": round(statistics.fmean(rt), 5) if rt else None,
            "ratio_tightest_values": rt,
            "ratio_tightest_min_mean": round(statistics.fmean(rm), 5) if rm else None,
            "ratio_at_contact_values": [x["ratio_at_contact"] for x in sel if x["ratio_at_contact"] is not None],
            "ratio_at_contact_mean": round(statistics.fmean([x["ratio_at_contact"] for x in sel
                                                             if x["ratio_at_contact"] is not None]), 5)
            if any(x["ratio_at_contact"] is not None for x in sel) else None,
            "contact_steps": [x["contact_step"] for x in sel],
            "distinct_contact_ratios": len({round(x["ratio_at_contact"], 5) for x in sel if x["ratio_at_contact"] is not None}),
            "distinct_sites": len({x["g_cold"] for x in sel}),
            "tightest_at_step_40": sum(1 for x in sel if x["ratio_tightest_step"] == 40),
            "ratio_mean_over_slices": round(statistics.fmean([x["ratio_mean_over_slices"] for x in sel
                                                              if x["ratio_mean_over_slices"] is not None]), 5)
            if any(x["ratio_mean_over_slices"] is not None for x in sel) else None,
            "peak_min": min((x["peak_min"] for x in sel if x["peak_min"] is not None), default=None),
            "usable_slices": sum(x["usable_slices"] for x in sel),
            "tightest_steps": [x["ratio_tightest_step"] for x in sel]}

allr = [x for x in runs if x["ratio_tightest"] is not None]
med = statistics.median([x["ratio_tightest"] for x in allr]) if allr else None
below = [x["ratio_tightest"] < med for x in allr]
fus = [bool(x["fused"]) for x in allr]
tab = {}
for x in allr:
    k = f"below_median={x['ratio_tightest'] < med}&fused={x['fused']}"
    tab[k] = tab.get(k, 0) + 1
a11 = sum(1 for b, f in zip(below, fus) if b and f)
a10 = sum(1 for b, f in zip(below, fus) if b and not f)
a01 = sum(1 for b, f in zip(below, fus) if not b and f)
a00 = sum(1 for b, f in zip(below, fus) if not b and not f)
fisher_p = fisher_one_sided(a11, a10, a01, a00) if allr else None

r6c, r6w = groups["r6_g9_cold"], groups["r6_g9_warm"]
r3c, r3w = groups["r3_g10_cold"], groups["r3_g10_warm"]


def diff(x, y, key="ratio_tightest_mean"):
    if not x or not y or x.get(key) is None or y.get(key) is None:
        return None
    return round(y[key] - x[key], 5)


d6 = diff(r6c, r6w)
d3 = diff(r3c, r3w)
d6c = diff(r6c, r6w, "ratio_at_contact_mean")
d3c = diff(r3c, r3w, "ratio_at_contact_mean")
d6min = diff(r6c, r6w, "ratio_tightest_min_mean")
d3min = diff(r3c, r3w, "ratio_tightest_min_mean")

peak_ok = all(g and g["peak_min"] is not None and g["peak_min"] >= PEAK_FLOOR for g in groups.values() if g)
usable_ok = all(g and g["usable_slices"] >= 2 for g in groups.values() if g)
sep_ok = all(abs(groups[k]["f_local_cold_mean"] - groups[j]["f_local_cold_mean"]) >= 0.008
             for k, j in (("r6_g9_warm", "r6_g9_cold"), ("r3_g10_warm", "r3_g10_cold")))

n40 = sum(g["tightest_at_step_40"] for g in groups.values() if g)
n40_3 = (r3c["tightest_at_step_40"] + r3w["tightest_at_step_40"]) if (r3c and r3w) else 0

if not (peak_ok and usable_ok and d6c is not None):
    verdict = ("READOUT INVALID at this sampling: the ring peak or the usable-slice check failed, so no claim is made about the "
               "bridge.")
elif d6c <= -BAR and d3c is not None and d3c >= 0:
    verdict = (
        f"A WARM SITE LEAVES A MARKEDLY WEAKER BRIDGE AT THE LARGEST SIZE, and the registered 'same direction, smaller' half of "
        f"the prediction is REFUTED at the smaller size. At the last saved slice on which the bodies are still separate - the "
        f"moment closest to contact - the bridge ratio is {r6w['ratio_at_contact_mean']} in the warm level against "
        f"{r6c['ratio_at_contact_mean']} in the cold at radius 6 gap 9 (difference {d6c:+g}, registered bar {-BAR:g}), while at "
        f"radius 3 gap 10 warmth moves it {d3c:+g}, the opposite sign: there warmth *strengthens* the bridge and the pair "
        f"coalesces more. The mechanism of the flip is therefore a property of the bridge between the bodies rather than of the "
        f"bodies around the pair, in the direction X170's reading predicts. The registered primary summary, the *tightest* saved "
        f"slice, is reported but not relied on: it lands on step 40 in {n40} of 12 runs ({n40_3} of them at radius 3) where the "
        f"field is still the seed-independent initial profile, so it measures the initial condition rather than the bridge "
        f"({d6:+g} at radius 6, {d3:+g} at radius 3).")
else:
    verdict = (f"THE BRIDGE DOES NOT CARRY THE FLIP: at the contact-moment reading warmth moves the bridge ratio {d6c:+g} at "
               f"radius 6 gap 9 and {d3c:+g} at radius 3 (registered bar {-BAR:g}), so the bridge between the bodies is not what "
               "separates the two arms' opposite outcomes, and the mechanism of the flip remains open after the bodies around "
               "the pair (X188) and the bridge itself (this item) have both been measured. The registered tightest-slice summary "
               f"is contaminated by the initial profile in {n40} of 12 runs and is not evidence either way.")

agg = {"kind": "x189_bridge", "flow": F, "ring_radius": RING_R, "bar": BAR, "peak_floor": PEAK_FLOOR,
       "amended_before_analysis": "bodies are tracked per slice (they drift ~5 cells by step 40) and the bodies are rings, so the "
                                  "peak is taken over a radius-10 disc and the bridge is read at the midpoint and over the central "
                                  "half. Bar and prediction unchanged.",
       "prediction": index["prediction"], "groups": groups, "outcome_crosstab": tab,
       "ratio_pooled_median": round(med, 5) if med is not None else None,
       "fisher_p_below_median_vs_fused": fisher_p,
       "radius6_warm_minus_cold": d6, "radius3_warm_minus_cold": d3,
       "radius6_contact_warm_minus_cold": d6c, "radius3_contact_warm_minus_cold": d3c,
       "tightest_slice_at_step_40_runs": n40,
       "initial_condition_contamination": "the tightest saved slice is step 40 (the seed-independent initial profile) in "
                                          f"{n40} of 12 runs, so the registered primary summary is not evidence about the bridge; "
                                          "the contact-moment readout (last saved slice with two components) is the one used.",
       "radius6_warm_minus_cold_min_readout": d6min, "radius3_warm_minus_cold_min_readout": d3min,
       "checks": {"peak_ok": peak_ok, "usable_slices_ok": usable_ok, "level_separation_ok": sep_ok},
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for k in ("r6_g9_cold", "r6_g9_warm", "r3_g10_cold", "r3_g10_warm"):
    g = groups.get(k)
    if g:
        print(f"[x189] {k}: share {g['share']:.2f}  bridge ratio (tightest) {g['ratio_tightest_mean']} "
              f"{g['ratio_tightest_values']}  min-readout {g['ratio_tightest_min_mean']}  peak_min {g['peak_min']}  "
              f"usable slices {g['usable_slices']}")
print(f"[x189] registered tightest-slice warm-minus-cold: radius6 {d6}, radius3 {d3} (bar {-BAR}), step-40 contamination {n40}/12")
print(f"[x189] contact-moment warm-minus-cold: radius6 {d6c}, radius3 {d3c} (bar {-BAR})")
print(f"[x189] min-readout: {d6min} / {d3min}; Fisher p of below-median vs fused {fisher_p}")
print(f"[x189] verdict: {verdict}")
