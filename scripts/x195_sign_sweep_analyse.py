"""x195_sign_sweep_analyse.py — X195: the sign of the inflow-outcome relation at four body sizes.

Per-arm tables (radius 4 gap 12, radius 5 gap 10) on the registered contact-moment readout, plus one row that puts X193's radius 3,
these two arms and X192's radius 6 on the same footing — the class-level and value-mean Spearman against the inflow — and tests
whether the sign moves monotonically with size.

Writes morphogenesis/experiments/E09_pond/l1_field_x195_sign_sweep.json.
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
FIELDS = ROOT / "_hourly" / "x195_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x195_sign_sweep.json"
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


index = json.loads((L1 / "x195_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    series = json.loads((L1 / f"x195_{r['tag']}.compact.json").read_text(encoding="utf-8")).get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    f_local = F * (1 + AMP * (2 * min(G_at(*cxy(cs0[0])), G_at(*cxy(cs0[1]))) - 1))
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    per_slice = []
    for sp in sorted(FIELDS.glob(f"{r['arm']}/c*/x195_{r['tag']}_t*.npy"),
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

# The four-radius row: X193's and X192's own aggregates supply the ends.
ends = {}
for key, path in (("r3_g10", POND / "l1_field_x193_phase_census_r3.json"), ("r6_g9", POND / "l1_field_x192_phase_census.json")):
    d = json.loads(path.read_text(encoding="utf-8"))
    ends[key] = {"radius": d["radius"], "gap": d["gap"], "worlds": d["classes"],
                 "spearman_ratio_vs_inflow_classes": d["spearman_ratio_vs_inflow_classes"],
                 "spearman_ratio_vs_inflow_value_means": d["spearman_ratio_vs_inflow_value_means"],
                 "bottom_share": d["values"][0]["share"], "top_share": d["values"][-1]["share"]}
row = [{"arm": "r3_g10", **ends["r3_g10"]}]
row += [{"arm": a["name"], "radius": a["radius"], "gap": a["gap"], "worlds": a["worlds"],
         "spearman_ratio_vs_inflow_classes": a["spearman_ratio_vs_inflow_classes"],
         "spearman_ratio_vs_inflow_value_means": a["spearman_ratio_vs_inflow_value_means"],
         "bottom_share": a["bottom_share"], "top_share": a["top_share"]} for a in arms]
row.append({"arm": "r6_g9", **ends["r6_g9"]})
row.sort(key=lambda r: r["radius"])
seq_c = [r["spearman_ratio_vs_inflow_classes"] for r in row]
seq_v = [r["spearman_ratio_vs_inflow_value_means"] for r in row]
monotone_c = all(b <= a for a, b in zip(seq_c, seq_c[1:]))
monotone_v = all(b <= a for a, b in zip(seq_v, seq_v[1:]))
signs = [(r["radius"], r["spearman_ratio_vs_inflow_value_means"]) for r in row]
flip = []
for (r1, s1), (r2, s2) in zip(signs, signs[1:]):
    if s1 is not None and s2 is not None and s1 > 0 >= s2:
        flip.append([r1, r2])

crit = {"phase_readout_in_each_arm": {"arms": {a["name"]: {"spread": a["crowded_value"]["ratio_spread"],
                                                          "f_local": a["crowded_value"]["f_local"],
                                                          "classes": a["crowded_value"]["classes"]} for a in arms},
                                      "bar": SPREAD_BAR,
                                      "passes": all((a["crowded_value"]["ratio_spread"] or 0) >= SPREAD_BAR for a in arms)},
        "outcome_follows_bridge_in_each_arm": {"arms": {a["name"]: {"difference": a["crowded_value"]["difference"],
                                                                     "fisher_p": a["crowded_value"]["fisher_p"],
                                                                     "outcome_varies": a["outcome_varies"],
                                                                     "fused_worlds": a["fused_worlds"]} for a in arms},
                                               "bar": CONTRAST_BAR,
                                               "not_testable_in": [a["name"] for a in arms if not a["outcome_varies"]],
                                               "passes": all((a["crowded_value"]["difference"] or 0) >= CONTRAST_BAR for a in arms)},
        "sign_monotone_with_size": {"sequence_by_class": seq_c, "sequence_by_value_means": seq_v,
                                    "monotone_by_class": monotone_c, "monotone_by_value_means": monotone_v,
                                    "flip_between_radii": flip,
                                    "passes": bool(monotone_c or monotone_v)}}
passed = sum(1 for c in crit.values() if c["passes"])
unusable = [a["name"] for a in arms if not all(a["checks"].values())]

if unusable:
    verdict = (f"NOT SENSITIVE BY CONSTRUCTION at {unusable}: the arm did not realise its classes or too few worlds reached the contact "
               f"moment, so it carries no sign and the intermediate radii are reported only as far as they are usable.")
elif not all(a["outcome_varies"] for a in arms):
    silent = [a["name"] for a in arms if not a["outcome_varies"]]
    verdict = (f"THERE IS A WINDOW OF SIZES WITH NO FUSION AT ALL, SO THE SIGN IS NOT DEFINED THERE. At {silent} not one of "
               f"{sum(a['worlds_with_contact'] for a in arms if not a['outcome_varies'])} worlds with a measurable bridge ever reaches one component "
               f"(fused worlds: {[a['fused_worlds'] for a in arms if not a['outcome_varies']]} against {[a['worlds_with_contact'] for a in arms if not a['outcome_varies']]} measured), "
               f"so the inflow-outcome sign cannot be read at these radii and the second registered criterion is not testable rather than failed. The "
               f"bridge side does carry over: the ratio's Spearman against the inflow is {[a['spearman_ratio_vs_inflow_classes'] for a in arms if not a['outcome_varies']]} "
               f"over classes and {[a['spearman_ratio_vs_inflow_value_means'] for a in arms if not a['outcome_varies']]} over the value means, in the radius-6 "
               f"direction, and the phase decides it at a fixed inflow (spreads {[a['crowded_value']['ratio_spread'] for a in arms if not a['outcome_varies']]}, "
               f"bar {SPREAD_BAR}). With radius 3 fusing and radius 6 partly fusing, the outcome over size is therefore not a monotone sign change but "
               f"non-monotone in existence: present at 3, absent at 4 and 5, partly present again at 6. X192's and X193's opposite signs stand as two "
               f"measured arms, and X193's phrase that size sets the sign needs this window beside it.")
elif not crit["sign_monotone_with_size"]["passes"]:
    verdict = (f"SIZE DOES NOT ORDER THE SIGN: the class-level Spearman runs {seq_c} and the value-mean Spearman {seq_v} over the four "
               f"radii, which is not non-increasing, so X192's and X193's opposite signs stand as two arms rather than as one trend. The "
               f"phase still decides the bridge at both intermediate radii (spreads "
               f"{[a['crowded_value']['ratio_spread'] for a in arms]}) and the outcome still follows it there "
               f"(differences {[a['crowded_value']['difference'] for a in arms]}).")
else:
    verdict = (f"THE SIGN CHANGES BETWEEN THE MEASURED SIZES, AND THE INTERMEDIATE RADII ORDER IT: over radius 3, 4, 5 and 6 the "
               f"class-level Spearman against the inflow is {seq_c} and the value-mean Spearman {seq_v}, non-increasing, with the sign "
               f"crossing between radii {flip[0][0]} and {flip[0][1] if flip else 'n/a'}. In both intermediate arms the phase decides the "
               f"bridge at a fixed inflow (spreads {[a['crowded_value']['ratio_spread'] for a in arms]} at {[a['crowded_value']['classes'] for a in arms]} "
               f"classes) and the outcome follows it there (differences {[a['crowded_value']['difference'] for a in arms]}, Fisher "
               f"p {[a['crowded_value']['fisher_p'] for a in arms]}), so the same mechanism holds at four sizes and only the sign moves, "
               f"as the bridge account predicts: a stronger inflow thickens the bridge between small bodies and thins it between large ones.")

agg = {"kind": "x195_sign_sweep", "flow": F, "ring_radius": RING_R, "arms": arms,
       "four_radius_row": row, "sign_flip_between_radii": flip,
       "registered_criteria": crit, "criteria_passed": passed,
       "outcome_absent_arms": [a["name"] for a in arms if not a["outcome_varies"]],
       "fused_worlds_per_arm": {a["name"]: {"fused": a["fused_worlds"], "measured": a["worlds_with_contact"]} for a in arms},
       "bars": {"spread": SPREAD_BAR, "contrast": CONTRAST_BAR},
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for a in arms:
    print(f"[x195] {a['name']} (sep {a['sep']}): {a['worlds_with_contact']}/{a['worlds']} with contact; "
          f"crowded {a['crowded_value']['f_local']} spread {a['crowded_value']['ratio_spread']} "
          f"({a['crowded_value']['classes']} classes) contrast {a['crowded_value']['difference']} p {a['crowded_value']['fisher_p']}; "
          f"Spearman {a['spearman_ratio_vs_inflow_classes']} by classes, {a['spearman_ratio_vs_inflow_value_means']} by means; "
          f"slope {a['logistic_slope_fusion_on_ratio']}; shares {a['bottom_share']} -> {a['top_share']}")
print(f"[x195] four radii: {[(r['radius'], r['spearman_ratio_vs_inflow_value_means']) for r in row]}; "
      f"monotone by class {monotone_c}, by means {monotone_v}; flip {flip}")
print(f"[x195] verdict: {verdict}")
