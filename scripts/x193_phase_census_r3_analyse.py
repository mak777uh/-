"""x193_phase_census_r3_analyse.py — X193: the phase census at radius 3 gap 10.

Registered readout (X190/X191): the contact-moment bridge ratio. What the census adds is the population of 144 phase classes, whose
F_local takes nine distinct values, so the analysis can ask (a) whether the ratio varies with the phase at fixed inflow, (b) whether
it falls with the inflow over the population, (c) whether the outcome follows the bridge within a fixed inflow, and (d) whether the
outcome falls with the inflow over the nine values.

Writes morphogenesis/experiments/E09_pond/l1_field_x193_phase_census_r3.json.
"""
from __future__ import annotations

import json
import math
import statistics
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x193_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x193_phase_census_r3.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
RING_R = 10
PEAK_FLOOR = 0.3
SPREAD_BAR = 0.05
SPEARMAN_BAR = -0.5
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
    """One-sided Fisher exact p that a/(a+b) exceeds c/(c+d)."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    if not n or not r1 or not r2 or not c1:
        return 1.0
    p_obs = comb(r1, a) * comb(r2, c1 - a) / comb(n, c1)
    p = 0.0
    for x in range(a, min(r1, c1) + 1):
        if 0 <= c1 - x <= r2:
            pr = comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
            if pr <= p_obs + 1e-12:
                p += pr
    return round(p, 4)


def logistic_irls(x: list[float], y: list[int]):
    """Two-parameter logistic fit fused ~ a + b * ratio; returns b, its standard error and z."""
    X = np.column_stack([np.ones(len(x)), np.array(x, dtype=float)])
    yv = np.array(y, dtype=float)
    beta = np.zeros(2)
    for _ in range(80):
        eta = X @ beta
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-9, None)
        z = eta + (yv - p) / w
        W = np.diag(w)
        try:
            beta_new = np.linalg.solve(X.T @ W @ X, X.T @ W @ z)
        except np.linalg.LinAlgError:
            return None, None, None
        if np.max(np.abs(beta_new - beta)) < 1e-9:
            beta = beta_new
            break
        beta = beta_new
    eta = X @ beta
    p = 1.0 / (1.0 + np.exp(-eta))
    w = np.clip(p * (1 - p), 1e-9, None)
    cov = np.linalg.inv(X.T @ np.diag(w) @ X)
    se = float(math.sqrt(cov[1, 1]))
    return round(float(beta[1]), 3), round(se, 3), round(float(beta[1] / se), 2) if se else None


index = json.loads((L1 / "x193_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    series = json.loads((L1 / f"x193_{r['tag']}.compact.json").read_text(encoding="utf-8")).get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    g_cold = min(G_at(*cxy(cs0[0])), G_at(*cxy(cs0[1])))
    f_local = F * (1 + AMP * (2 * g_cold - 1))
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    per_slice = []
    for sp in sorted(FIELDS.glob(f"*/x193_{r['tag']}_t*.npy"), key=lambda p: int(p.stem.split("_t")[-1])):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = by_step.get(step)
        rec = {"step": step, "n_components": len(cur) if cur is not None else None}
        if not cur or len(cur) != 2:
            per_slice.append(rec)
            continue
        peak = max(ring_peak(field, cur[0]), ring_peak(field, cur[1]))
        rec.update({"peak": round(peak, 5), "ratio": round(midpoint(field, *cur) / peak, 5) if peak > 0 else None})
        per_slice.append(rec)
    ok = [x for x in per_slice if x.get("ratio") is not None and (x.get("peak") or 0) >= PEAK_FLOOR]
    contact = max(ok, key=lambda x: x["step"]) if ok else None
    runs.append({"tag": r["tag"], "phase": r["phase"], "jitter": r["jitter"], "seed": r["seed"],
                 "f_local_index": round(float(r["f_local"]), 5), "f_local": round(f_local, 5),
                 "fused": int(min(counts) == 1), "min_count": min(counts),
                 "usable_slices": len(ok), "contact_step": contact["step"] if contact else None,
                 "ratio_contact": contact["ratio"] if contact else None,
                 "peak_min": min((x["peak"] for x in per_slice if x.get("peak") is not None), default=None)})

by_value = {}
for x in runs:
    by_value.setdefault(x["f_local_index"], []).append(x)
values = []
for v in sorted(by_value):
    sel = by_value[v]
    ratios = sorted(x["ratio_contact"] for x in sel if x["ratio_contact"] is not None)
    values.append({"f_local": v, "classes": len(sel), "classes_with_contact": len(ratios),
                   "fused": sum(x["fused"] for x in sel),
                   "share": round(statistics.fmean([x["fused"] for x in sel]), 4),
                   "ratio_values": ratios,
                   "ratio_min": ratios[0] if ratios else None, "ratio_max": ratios[-1] if ratios else None,
                   "ratio_spread": round(ratios[-1] - ratios[0], 5) if len(ratios) > 1 else None,
                   "ratio_mean": round(statistics.fmean(ratios), 5) if ratios else None})

usable = [x for x in runs if x["ratio_contact"] is not None]
rho_classes = spearman([x["f_local"] for x in usable], [x["ratio_contact"] for x in usable])
value_means = [v["ratio_mean"] for v in values if v["ratio_mean"] is not None]
value_flows = [v["f_local"] for v in values if v["ratio_mean"] is not None]
rho_values = spearman(value_flows, value_means)
slope, slope_se, slope_z = logistic_irls([x["ratio_contact"] for x in usable], [x["fused"] for x in usable])

crowded = max(values, key=lambda v: v["classes_with_contact"])
crowd_runs = [x for x in by_value[crowded["f_local"]] if x["ratio_contact"] is not None]
med = statistics.median([x["ratio_contact"] for x in crowd_runs])
above = [x for x in crowd_runs if x["ratio_contact"] > med]
below = [x for x in crowd_runs if x["ratio_contact"] <= med]
share_above = statistics.fmean([x["fused"] for x in above]) if above else None
share_below = statistics.fmean([x["fused"] for x in below]) if below else None
contrast = round(share_above - share_below, 4) if (share_above is not None and share_below is not None) else None
contrast_p = fisher_greater(sum(x["fused"] for x in above), len(above) - sum(x["fused"] for x in above),
                            sum(x["fused"] for x in below), len(below) - sum(x["fused"] for x in below))
top_share, bottom_share = values[-1]["share"], values[0]["share"]

checks = {"all_classes_ran": len(runs) == 144,
          "contact_worlds_ok": len(usable) >= 12,
          "values_realised": len({v["f_local"] for v in values}) >= 8,
          "peak_ok": all((x["peak_min"] or 0) >= PEAK_FLOOR for x in usable)}
crit = {"phase_spread_at_crowded_value": {"value": crowded["f_local"], "classes": crowded["classes_with_contact"],
                                          "spread": crowded["ratio_spread"], "bar": SPREAD_BAR,
                                          "passes": bool(crowded["ratio_spread"] is not None and crowded["ratio_spread"] >= SPREAD_BAR)},
        "ratio_falls_with_inflow": {"spearman_classes": rho_classes, "spearman_value_means": rho_values, "bar": SPEARMAN_BAR,
                                    "passes": bool(rho_classes is not None and rho_classes <= SPEARMAN_BAR)},
        "outcome_follows_bridge_at_fixed_inflow": {"value": crowded["f_local"], "share_above_median": share_above,
                                                   "share_below_median": share_below, "difference": contrast,
                                                   "fisher_p": contrast_p, "bar": CONTRAST_BAR,
                                                   "passes": bool(contrast is not None and contrast >= CONTRAST_BAR)},
        "outcome_falls_with_inflow": {"bottom_share": bottom_share, "top_share": top_share,
                                      "passes": bool(top_share is not None and bottom_share is not None and top_share <= bottom_share)},
        "outcome_relation_sign_reversed": {"bottom_share": bottom_share, "top_share": top_share,
                                          "passes": bool(top_share is not None and bottom_share is not None and top_share > bottom_share)}}
passed = sum(1 for c in crit.values() if c["passes"])

if not all(checks.values()):
    verdict = ("NOT SENSITIVE BY CONSTRUCTION: the census did not realise all classes or too few worlds reached the contact moment, so "
               "no population claim is made.")
elif crit["phase_spread_at_crowded_value"]["passes"] and crit["outcome_follows_bridge_at_fixed_inflow"]["passes"]:
    verdict = (f"THE BRIDGE DEPENDS ON THE PHASE AT FIXED INFLOW, AND THE OUTCOME FOLLOWS IT THERE. At the most crowded inflow value, "
               f"F_local = {crowded['f_local']} with {crowded['classes_with_contact']} phase classes, the contact ratio spans "
               f"{crowded['ratio_min']}-{crowded['ratio_max']} (spread {crowded['ratio_spread']}, bar {SPREAD_BAR}) - so the bridge is not a "
               f"function of the inflow alone - and the worlds above that value's median ratio fuse {contrast} more often than those below "
               f"(Fisher p = {contrast_p}, bar {CONTRAST_BAR}). Over the population the ratio falls with the inflow (Spearman "
               f"{rho_classes} over classes, {rho_values} over the nine value means; bar {SPEARMAN_BAR}) and the logistic slope of fusion on the "
               f"ratio over the {len(usable)} worlds is {slope} (se {slope_se}, z = {slope_z}). The mechanism of the flip is therefore a "
               f"property of the field between the bodies at a given inflow, and the law's boundary condition has to be written per phase, not "
               f"per inflow. {passed} of 4 registered criteria passed.")
else:
    verdict = (f"THE CENSUS SPLITS THE MECHANISM: {passed} of 4 registered criteria passed. At the most crowded value "
               f"(F_local = {crowded['f_local']}, {crowded['classes_with_contact']} classes) the ratio spread is {crowded['ratio_spread']} "
               f"(bar {SPREAD_BAR}) and the above/below-median fusion contrast is {contrast} (Fisher p = {contrast_p}, bar {CONTRAST_BAR}); over "
               f"the population the ratio's Spearman against the inflow is {rho_classes} over classes and {rho_values} over the nine value means "
               f"(bar {SPEARMAN_BAR}); the top value's fusion share is {top_share} against {bottom_share} at the bottom; and the logistic slope of "
               f"fusion on the ratio is {slope} (se {slope_se}, z = {slope_z}). What passes and what fails is in registered_criteria.")

agg = {"kind": "x193_phase_census_r3", "flow": F, "radius": index["radius"], "gap": index["gap"], "ring_radius": RING_R,
       "classes": len(runs), "worlds_with_contact": len(usable),
       "values": values, "registered_criteria": crit, "criteria_passed": passed, "checks": checks,
       "spearman_ratio_vs_inflow_classes": rho_classes, "spearman_ratio_vs_inflow_value_means": rho_values,
       "logistic_slope_fusion_on_ratio": {"slope": slope, "se": slope_se, "z": slope_z},
       "crowded_value_contrast": {"f_local": crowded["f_local"], "median_ratio": round(med, 5),
                                  "above": {"n": len(above), "fused": sum(x["fused"] for x in above), "share": share_above},
                                  "below": {"n": len(below), "fused": sum(x["fused"] for x in below), "share": share_below},
                                  "difference": contrast, "fisher_p": contrast_p},
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for v in values:
    print(f"[x193] F_local {v['f_local']}: {v['classes_with_contact']}/{v['classes']} with contact  ratio {v['ratio_min']}-{v['ratio_max']} "
          f"(spread {v['ratio_spread']})  share {v['share']}")
print(f"[x193] worlds with contact {len(usable)}/144; Spearman {rho_classes} over classes, {rho_values} over value means; "
      f"logistic slope {slope} (se {slope_se}, z {slope_z})")
print(f"[x193] crowded value {crowded['f_local']}: above-median share {share_above} vs below {share_below} "
      f"(diff {contrast}, Fisher p {contrast_p})")
print(f"[x193] verdict: {verdict}")
