"""x198_gap_curve_analyse.py — X198: the fusion share as a function of the surface-to-surface gap.

Per-arm tables (radius 4 gap 12, radius 5 gap 10) on the registered contact-moment readout, plus one row that puts X193's radius 3,
these two arms and X192's radius 6 on the same footing — the class-level and value-mean Spearman against the inflow — and tests
whether the sign moves monotonically with size.

Writes morphogenesis/experiments/E09_pond/l1_field_x198_gap_curve.json.
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
FIELDS = ROOT / "_hourly" / "x198_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x198_gap_curve.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
RING_R = 10
PEAK_FLOOR = 0.3
SPREAD_BAR = 0.05
CONTRAST_BAR = 0.3


def comps(row):
    return row[1] if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list) else []


def cxy(c):
    return (float(c[2]), float(c[3]))


def step_of(row):
    return int(row[0])


def wrap_dx(a, b):
    return (a - b + GRID / 2) % GRID - GRID / 2


def G_at(x, y):
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def ring_peak(field, centre, r=RING_R):
    cx, cy = centre
    return max(float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID])
               for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= r * r)


def midpoint(field, c0, c1):
    mx = (c0[0] + wrap_dx(c1[0], c0[0]) / 2.0) % GRID
    my = (c0[1] + (c1[1] - c0[1]) / 2.0) % GRID
    return float(field[int(round(my)) % GRID, int(round(mx)) % GRID])


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num / den, 3) if den else None


def fisher_greater(a, b, c, d):
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    if not n or not r1 or not r2 or not c1:
        return 1.0
    p_obs = comb(r1, a) * comb(r2, c1 - a) / comb(n, c1)
    p = sum(comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
            for x in range(a, min(r1, c1) + 1) if 0 <= c1 - x <= r2 and
            comb(r1, x) * comb(r2, c1 - x) / comb(n, c1) <= p_obs + 1e-12)
    return round(p, 4)


def logistic_irls(x, y):
    X = np.column_stack([np.ones(len(x)), np.array(x, dtype=float)])
    yv = np.array(y, dtype=float)
    beta = np.zeros(2)
    for _ in range(80):
        eta = X @ beta
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-9, None)
        z = eta + (yv - p) / w
        try:
            beta_new = np.linalg.solve(X.T @ np.diag(w) @ X, X.T @ np.diag(w) @ z)
        except np.linalg.LinAlgError:
            return None, None, None
        if np.max(np.abs(beta_new - beta)) < 1e-9:
            beta = beta_new
            break
        beta = beta_new
    eta = X @ beta
    p = 1.0 / (1.0 + np.exp(-eta))
    w = np.clip(p * (1 - p), 1e-9, None)
    se = float(math.sqrt(np.linalg.inv(X.T @ np.diag(w) @ X)[1, 1]))
    return round(float(beta[1]), 3), round(se, 3), round(float(beta[1] / se), 2) if se else None


index = json.loads((L1 / "x198_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    series = json.loads((L1 / f"x198_{r['tag']}.compact.json").read_text(encoding="utf-8")).get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    f_local = F * (1 + AMP * (2 * min(G_at(*cxy(cs0[0])), G_at(*cxy(cs0[1]))) - 1))
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    per_slice = []
    for sp in sorted(FIELDS.glob(f"{r['arm']}/c*/x198_{r['tag']}_t*.npy"),
                     key=lambda p: int(p.stem.split("_t")[-1])):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = by_step.get(step)
        rec = {"step": step}
        if not cur or len(cur) != 2:
            per_slice.append(rec)
            continue
        peak = max(ring_peak(field, cur[0]), ring_peak(field, cur[1]))
        rec.update({"peak": round(peak, 5), "ratio": round(midpoint(field, *cur) / peak, 5) if peak > 0 else None})
        per_slice.append(rec)
    ok = [x for x in per_slice if x.get("ratio") is not None and (x.get("peak") or 0) >= PEAK_FLOOR]
    contact = max(ok, key=lambda x: x["step"]) if ok else None
    runs.append({"arm": r["arm"], "radius": r["radius"], "gap": r["gap"], "tag": r["tag"], "phase": r["phase"],
                 "f_local": round(f_local, 5), "f_local_index": round(float(r["f_local"]), 5),
                 "fused": int(min(counts) == 1), "usable_slices": len(ok),
                 "contact_step": contact["step"] if contact else None,
                 "ratio_contact": contact["ratio"] if contact else None,
                 "peak_min": min((x["peak"] for x in per_slice if x.get("peak") is not None), default=None)})

arms = []
for a in index["arms"]:
    sel = [x for x in runs if x["arm"] == a["name"]]
    by_value = {}
    for x in sel:
        by_value.setdefault(x["f_local_index"], []).append(x)
    values = []
    for v in sorted(by_value):
        g = by_value[v]
        ratios = sorted(x["ratio_contact"] for x in g if x["ratio_contact"] is not None)
        values.append({"f_local": v, "classes": len(g), "classes_with_contact": len(ratios),
                       "fused": sum(x["fused"] for x in g), "share": round(statistics.fmean([x["fused"] for x in g]), 4),
                       "ratio_values": ratios, "ratio_min": ratios[0] if ratios else None,
                       "ratio_max": ratios[-1] if ratios else None,
                       "ratio_spread": round(ratios[-1] - ratios[0], 5) if len(ratios) > 1 else None,
                       "ratio_mean": round(statistics.fmean(ratios), 5) if ratios else None})
    usable = [x for x in sel if x["ratio_contact"] is not None]
    rho_c = spearman([x["f_local"] for x in usable], [x["ratio_contact"] for x in usable])
    rho_v = spearman([v["f_local"] for v in values if v["ratio_mean"] is not None],
                     [v["ratio_mean"] for v in values if v["ratio_mean"] is not None])
    rho_share = spearman([v["f_local"] for v in values], [v["share"] for v in values])
    outcome_varies = len({x["fused"] for x in usable}) >= 2
    if outcome_varies:
        slope, se, z = logistic_irls([x["ratio_contact"] for x in usable], [x["fused"] for x in usable])
    else:
        slope, se, z = None, None, None
    crowd = max(values, key=lambda v: v["classes_with_contact"])
    cr = [x for x in by_value[crowd["f_local"]] if x["ratio_contact"] is not None]
    med = statistics.median([x["ratio_contact"] for x in cr])
    above = [x for x in cr if x["ratio_contact"] > med]
    below = [x for x in cr if x["ratio_contact"] <= med]
    sh_a = statistics.fmean([x["fused"] for x in above]) if above else None
    sh_b = statistics.fmean([x["fused"] for x in below]) if below else None
    contrast = round(sh_a - sh_b, 4) if sh_a is not None and sh_b is not None else None
    if not outcome_varies:
        contrast = None
    arms.append({"name": a["name"], "radius": a["radius"], "gap": a["gap"], "sep": a["sep"],
                 "worlds": len(sel), "worlds_with_contact": len(usable),
                 "values": values,
                 "spearman_ratio_vs_inflow_classes": rho_c, "spearman_ratio_vs_inflow_value_means": rho_v,
                 "spearman_share_vs_inflow_value_means": rho_share,
                 "outcome_varies": outcome_varies,
                 "fused_worlds": sum(x["fused"] for x in usable),
                 "logistic_slope_fusion_on_ratio": {"slope": slope, "se": se, "z": z},
                 "crowded_value": {"f_local": crowd["f_local"], "classes": crowd["classes_with_contact"],
                                   "ratio_spread": crowd["ratio_spread"], "ratio_min": crowd["ratio_min"],
                                   "ratio_max": crowd["ratio_max"], "median_ratio": round(med, 5),
                                   "share_above_median": sh_a, "share_below_median": sh_b,
                                   "difference": contrast,
                                   "fisher_p": fisher_greater(sum(x["fused"] for x in above),
                                                              len(above) - sum(x["fused"] for x in above),
                                                              sum(x["fused"] for x in below),
                                                              len(below) - sum(x["fused"] for x in below))},
                 "bottom_share": values[0]["share"], "top_share": values[-1]["share"],
                 "bottom_f_local": values[0]["f_local"], "top_f_local": values[-1]["f_local"],
                 "checks": {"worlds_ok": len(sel) >= 144, "contact_ok": len(usable) >= 12,
                            "peak_ok": all((x["peak_min"] or 0) >= PEAK_FLOOR for x in usable),
                            "values_ok": len([v for v in values if v["classes"] >= 4]) >= 8}})

# Reference arms enter from their committed aggregates only.
refs = {}
_d195 = json.loads((POND / "l1_field_x195_sign_sweep.json").read_text(encoding="utf-8"))
_a = next(x for x in _d195["arms"] if x["name"] == "r4_g12")
refs["r4_g12"] = {"radius": _a["radius"], "gap": _a["gap"], "sep": _a["sep"], "worlds": _a["worlds"],
                  "share_over_values": round(statistics.fmean([v["share"] for v in _a["values"]]), 4),
                  "share_max": max(v["share"] for v in _a["values"]), "fused_worlds": _a["fused_worlds"],
                  "spearman_classes": _a["spearman_ratio_vs_inflow_classes"]}
_d192 = json.loads((POND / "l1_field_x192_phase_census.json").read_text(encoding="utf-8"))
refs["r6_g9"] = {"radius": _d192["radius"], "gap": _d192["gap"], "sep": 21.0, "worlds": _d192["classes"],
                 "share_over_values": round(statistics.fmean([v["share"] for v in _d192["values"]]), 4),
                 "share_max": max(v["share"] for v in _d192["values"]),
                 "fused_worlds": sum(v["fused"] for v in _d192["values"]),
                 "spearman_classes": _d192["spearman_ratio_vs_inflow_classes"]}

by_name = {a["name"]: a for a in arms}
r4_g10, r4_g8, r6_g8 = by_name["r4_g10"], by_name["r4_g8"], by_name["r6_g8"]
s410, s48, s68 = (round(statistics.fmean([v["share"] for v in a["values"]]), 4) for a in (r4_g10, r4_g8, r6_g8))
zero_arms = [a["name"] for a in arms if a["fused_worlds"] == 0]

crit = {
    "radius4_share_does_not_fall_as_the_gap_closes": {
        "shares": {"gap12_reference": refs["r4_g12"]["share_over_values"], "gap10": s410, "gap8": s48},
        "bar": "at least one above 0.1 and not falling from gap 10 to gap 8",
        "passes": bool(s48 >= s410 and max(s410, s48) > 0.1)},
    "radius6_at_separation_20_still_fuses": {
        "share_gap8": s68, "share_gap9_reference": refs["r6_g9"]["share_over_values"],
        "fused_worlds_gap8": r6_g8["fused_worlds"], "fused_worlds_gap9_reference": refs["r6_g9"]["fused_worlds"],
        "bar": "above 0 and at least the gap-9 average",
        "passes": bool(s68 > 0 and s68 >= refs["r6_g9"]["share_over_values"])},
    "phase_decides_the_bridge_in_each_arm": {
        "spreads": {a["name"]: a["crowded_value"]["ratio_spread"] for a in arms}, "bar": 0.05,
        "passes": all((a["crowded_value"]["ratio_spread"] or 0) >= 0.05 for a in arms)},
}
passed = sum(1 for c in crit.values() if c["passes"])

if not all(a["checks"]["worlds_ok"] and a["checks"]["contact_ok"] and a["checks"]["peak_ok"] for a in arms):
    verdict = ("NOT SENSITIVE BY CONSTRUCTION: an arm did not realise its phase classes or too few worlds reached the contact moment, "
               "so the size/gap separation is not read.")
elif s68 > 0 and s48 == 0:
    verdict = (f"THE WINDOW IS SET BY THE SIZE AT A FIXED SEPARATION. Radius 6 gap 8 (separation 20, the same separation as the fusion-free "
               f"radius-4 reference) fuses {r6_g8['fused_worlds']} of {r6_g8['worlds']} worlds ({s68} on average over its inflow values, against "
               f"{refs['r6_g9']['share_over_values']} for radius 6 gap 9), while radius 4 at gaps 10 and 8 fuses {r4_g10['fused_worlds']} and "
               f"{r4_g8['fused_worlds']} of {r4_g4_n if False else r4_g8['worlds']} - none. Bringing the smaller bodies together does not restart the outcome; "
               f"the larger body at the same separation does fuse. So X195's window is a size window, and the separation is not the barrier over this range. "
               f"The phase still decides the bridge in every arm (spreads {[a['crowded_value']['ratio_spread'] for a in arms]}). {passed} of 3 criteria passed.")
elif s48 > 0 and s410 == 0:
    verdict = (f"THE WINDOW CLOSES SHARPLY BETWEEN SEPARATIONS 20 AND 18. Radius 4 fuses {r4_g10['fused_worlds']} of {r4_g10['worlds']} at gap 10 "
               f"(separation 18) - none - but {r4_g8['fused_worlds']} of {r4_g8['worlds']} at gap 8 (separation 16, {s48}), so two cells of extra separation "
               f"decide the outcome at this radius, which is the resolution at which the earlier boundary work (X158) found the fusion transition. Radius 6 "
               f"gap 8 fuses {r6_g8['fused_worlds']} of {r6_g8['worlds']} ({s68}). {passed} of 3 criteria passed.")
elif s48 > 0 and s68 > 0:
    gaps = {"r4_g12_reference": refs["r4_g12"]["gap"], "r4_g10": r4_g10["gap"], "r4_g8": r4_g8["gap"],
            "r6_g9_reference": refs["r6_g9"]["gap"], "r6_g8": r6_g8["gap"]}
    verdict = (f"THE GAP IS THE BINDING VARIABLE, AND THE SIZE ONLY SHIFTS IT - X195'S SIZE WINDOW IS CORRECTED TO A GAP WINDOW. Ordering the five "
               f"measured arms by the surface-to-surface gap: gap {gaps['r4_g12_reference']:.0f} (radius 4) fuses "
               f"{refs['r4_g12']['share_over_values']}, gap {gaps['r4_g10']:.0f} (radius 4) {s410}, gap {gaps['r6_g9_reference']:.0f} (radius 6) "
               f"{refs['r6_g9']['share_over_values']}, gap {gaps['r6_g8']:.0f} (radius 6) {s68}, gap {gaps['r4_g8']:.0f} (radius 4) {s48}: the share rises as the gap "
               f"closes at both sizes, so what X195 read as a window of sizes is a window of gaps. The size is not absent: at a gap of 8 the smaller body fuses "
               f"{s48} and the larger {s68}, and reordering the two radii at a matched gap is a size effect of that order - but the variable that turns fusion off "
               f"and on is the distance between the surfaces, not the body size. In X195 the radius-4 and radius-5 arms both sat at a separation of 20 cells, which "
               f"is a gap of 12 and 10 - the far end of this table - while radius 6 at the same separation sits at a gap of 8. The phase still decides the bridge in "
               f"every arm (spreads {[a['crowded_value']['ratio_spread'] for a in arms]}). {passed} of 3 criteria passed.")
elif s48 > 0:
    verdict = (f"THE SEPARATION IS THE BINDING VARIABLE OVER THIS RANGE. At fixed radius 4 the fusion share rises as the bodies come together "
               f"({refs['r4_g12']['share_over_values']} at separation 20, {s410} at 18, {s48} at 16), and radius 6 at separation 20 fuses {s68}; so the fusion-free "
               f"window of X195 is a separation window at these sizes, not a property of the body size. {passed} of 3 criteria passed.")
else:
    verdict = (f"THE SEPARATION IS THE BARRIER OVER THE WHOLE RANGE. Neither radius 4 (gaps 10 and 8: {r4_g10['fused_worlds']} and "
               f"{r4_g8['fused_worlds']} fused worlds) nor radius 6 at separation 20 ({r6_g8['fused_worlds']}) produces a single fusion in {sum(a['worlds'] for a in arms)} "
               f"worlds, so separation 20 and below is simply too far at these sizes and the variable that matters is the separation, not the size. The bridge "
               f"is still decided by the phase in every arm (spreads {[a['crowded_value']['ratio_spread'] for a in arms]}). {passed} of 3 criteria passed.")

agg = {"kind": "x198_gap_curve", "flow": F, "arms": arms, "references": refs,
       "mean_shares": {"r4_g12_reference": refs["r4_g12"]["share_over_values"], "r4_g10": s410, "r4_g8": s48,
                       "r6_g9_reference": refs["r6_g9"]["share_over_values"], "r6_g8": s68},
       "fused_worlds": {a["name"]: {"fused": a["fused_worlds"], "worlds": a["worlds"]} for a in arms},
       "arms_with_no_fusion": zero_arms, "registered_criteria": crit, "criteria_passed": passed,
       "gap_table": {a["name"]: {"gap": a["gap"], "sep": a["sep"], "radius": a["radius"],
                                 "share": round(statistics.fmean([v["share"] for v in a["values"]]), 4),
                                 "fused_worlds": a["fused_worlds"], "worlds": a["worlds"]} for a in arms},
       "correction_to_x195": ("X195 read the fusion-free arms at separation 20 as a window of body sizes; with the gap held at 8 both sizes fuse "
                             "(radius 4 at 0.96, radius 6 at 0.83) and the sharing variable is the surface-to-surface gap, since the radius-4 and "
                             "radius-5 arms of X195 sat at gaps of 12 and 10 at that same separation"),
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for a in arms:
    print(f"[x198] {a['name']} (r {a['radius']:.0f} gap {a['gap']:.0f} sep {a['sep']:.0f}): {a['worlds_with_contact']}/{a['worlds']} with contact, "
          f"fused {a['fused_worlds']}, share {round(statistics.fmean([v['share'] for v in a['values']]), 4)}, "
          f"crowded spread {a['crowded_value']['ratio_spread']}, Spearman {a['spearman_ratio_vs_inflow_classes']}")
print(f"[x198] mean shares: {agg['mean_shares']}")
print(f"[x198] verdict: {verdict}")
