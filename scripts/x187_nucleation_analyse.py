"""x187_nucleation_analyse.py — X187: bodies that appear besides the seeded pair, by the pair's local inflow.

Reads the component log of each run (positions at every sample), recomputes the local inflow at the colder body from the logged
centres of the first sample, and counts components other than the two seeded ones whose centres lie within 8 cells of the pair's
midpoint at the sample where the total component count is smallest. Compares the cold and warm levels within each arm.

Writes morphogenesis/experiments/E09_pond/l1_field_x187_nucleation.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x187_nucleation.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
RADIUS_OF_INTEREST = 8.0
PREDICTION = {"r6_g9": "warm coalesces less and shows more extra bodies", "r3_g10": "warm coalesces more, extra bodies within one"}


def G_at(x: float, y: float) -> float:
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def xy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def sep_cells(a, b) -> float:
    dx = abs(a[0] - b[0]) % GRID
    dx = min(dx, GRID - dx)
    dy = abs(a[1] - b[1]) % GRID
    dy = min(dy, GRID - dy)
    return math.hypot(dx, dy)


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


index = json.loads((L1 / "x187_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
rows = []
missed = 0
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    d = json.loads((L1 / f"x187_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    seeds_xy = [xy(c) for c in cs0]
    mid = (statistics.fmean([p[0] for p in seeds_xy]), statistics.fmean([p[1] for p in seeds_xy]))
    g_cold = min(G_at(*p) for p in seeds_xy)
    f_local = F * (1 + AMP * (2 * g_cold - 1))
    target = index["arms"][r["arm"]]["groups"] and None
    counts = [len(comps(x)) for x in series]
    if not counts:
        continue
    k_min = min(counts)
    i_min = counts.index(k_min)
    row_min = series[i_min]
    extra = [c for c in comps(row_min) if all(sep_cells(xy(c), s) > 3.0 for s in seeds_xy)]
    near = [c for c in extra if sep_cells(xy(c), mid) <= RADIUS_OF_INTEREST]
    rows.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"], "f_local_cold": round(f_local, 5),
                 "g_cold": round(g_cold, 4), "fused": int(k_min == 1), "min_count": k_min,
                 "final_count": counts[-1], "extra_at_min": len(extra), "extra_near_mid_at_min": len(near),
                 "step_at_min": int(row_min[0]) if isinstance(row_min, list) else int(row_min.get("step")),
                 "samples": len(counts)})

groups = {}
for arm in index["arms"]:
    for lvl in index["arms"][arm]["groups"]:
        sel = [x for x in rows if x["arm"] == arm and x["level"] == lvl]
        if not sel:
            groups[f"{arm}_{lvl}"] = None
            continue
        gs = [x["g_cold"] for x in sel]
        groups[f"{arm}_{lvl}"] = {
            "runs": len(sel), "fused": sum(x["fused"] for x in sel),
            "share": round(statistics.fmean(x["fused"] for x in sel), 4), "wilson": wilson(sum(x["fused"] for x in sel), len(sel)),
            "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in sel]), 5),
            "extra_near_mid_median": statistics.median([x["extra_near_mid_at_min"] for x in sel]),
            "extra_near_mid_mean": round(statistics.fmean([x["extra_near_mid_at_min"] for x in sel]), 2),
            "extra_all_median": statistics.median([x["extra_at_min"] for x in sel]),
            "min_count_median": statistics.median([x["min_count"] for x in sel]),
            "final_count_mean": round(statistics.fmean([x["final_count"] for x in sel]), 1),
            "runs_with_count_le_2": sum(1 for x in sel if x["min_count"] <= 2),
            "step_at_min_median": statistics.median([x["step_at_min"] for x in sel])}

res = {}
for arm in ("r6_g9", "r3_g10"):
    cold, warm = groups.get(f"{arm}_cold"), groups.get(f"{arm}_warm")
    if not cold or not warm:
        res[arm] = None
        continue
    res[arm] = {"cold": cold, "warm": warm,
                "share_difference_warm_minus_cold": round(warm["share"] - cold["share"], 4),
                "extra_difference_median": (warm["extra_near_mid_median"] - cold["extra_near_mid_median"]),
                "level_separation": round(warm["f_local_cold_mean"] - cold["f_local_cold_mean"], 5)}

wanted = {}
for arm in ("r6_g9", "r3_g10"):
    r = res.get(arm)
    wanted[arm] = None if not r else {
        "warm_coalesces_less": r["share_difference_warm_minus_cold"] < 0,
        "warm_has_more_extra": r["extra_difference_median"] >= 1,
        "level_separation_ok": r["level_separation"] >= 0.008,
        "three_runs_measurable": min(r["cold"]["runs_with_count_le_2"], r["warm"]["runs_with_count_le_2"]) >= 3}

r6, r3 = res.get("r6_g9"), res.get("r3_g10")
if not r6 or not r3:
    verdict = "NOT REPORTABLE: one of the arms has no runs."
elif wanted["r6_g9"]["warm_coalesces_less"] and wanted["r6_g9"]["warm_has_more_extra"] and \
        (not wanted["r3_g10"]["warm_has_more_extra"]):
    verdict = (f"A WARM MEDIUM NUCLEATES BODIES OF ITS OWN AT THE LARGEST SIZE: at radius 6 gap 9 the warm level coalesces "
               f"{r6['warm']['share']:.2f} against the cold level's {r6['cold']['share']:.2f} "
               f"(difference {r6['share_difference_warm_minus_cold']:+.2f}) while carrying a median of "
               f"{r6['warm']['extra_near_mid_median']} extra bodies within {RADIUS_OF_INTEREST:.0f} cells of the pair against "
               f"{r6['cold']['extra_near_mid_median']} for the cold level; at radius 3 gap 10 the same manipulation moves the "
               f"share by {r3['share_difference_warm_minus_cold']:+.2f} and the extra-body median by "
               f"{r3['extra_difference_median']:+g}, so the signature is specific to the largest bodies. The local-inflow law's "
               "sign is therefore size-dependent, and the radius-5.9 cells of X186 should be read with the nucleation count "
               "beside the share.")
elif not wanted["r6_g9"]["warm_has_more_extra"]:
    verdict = (f"THE FLIP IS NOT NUCLEATION AT THIS SAMPLING: at radius 6 gap 9 the warm level's extra-body median is "
               f"{r6['warm']['extra_near_mid_median']} against the cold level's {r6['cold']['extra_near_mid_median']} "
               f"(difference {r6['extra_difference_median']:+g}) while the shares differ by "
               f"{r6['share_difference_warm_minus_cold']:+.2f}, so the flipped cells of X186 stand unexplained by bodies "
               "appearing around the pair; the next attack is to hold the site fixed and vary the gap.")
else:
    verdict = (f"NUCLEATION IS GENERAL, NOT SIZE-SPECIFIC: at radius 6 gap 9 the warm level shows more extra bodies "
               f"({r6['extra_difference_median']:+g}) and coalesces less ({r6['share_difference_warm_minus_cold']:+.2f}), but at "
               f"radius 3 gap 10 it also shows more ({r3['extra_difference_median']:+g}) and coalesces "
               f"{r3['share_difference_warm_minus_cold']:+.2f}; the law's sign at small radius then needs re-deriving.")

agg = {"kind": "x187_nucleation", "flow": F, "steps": index["steps"], "radius_of_interest": RADIUS_OF_INTEREST,
       "prediction": PREDICTION, "groups": groups, "arms": res, "checks": wanted, "runs_detail": rows,
       "excluded_or_missed": missed, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for arm in ("r6_g9", "r3_g10"):
    r = res.get(arm)
    if not r:
        continue
    print(f"[x187] {arm}: cold F_local {r['cold']['f_local_cold_mean']} share {r['cold']['share']:.2f} "
          f"extra {r['cold']['extra_near_mid_median']} | warm F_local {r['warm']['f_local_cold_mean']} "
          f"share {r['warm']['share']:.2f} extra {r['warm']['extra_near_mid_median']} "
          f"(d share {r['share_difference_warm_minus_cold']:+.2f}, d extra {r['extra_difference_median']:+g})")
print(f"[x187] verdict: {verdict}")
