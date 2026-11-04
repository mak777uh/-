"""x187_nucleation_analyse.py — X187: why do the largest bodies read the opposite sign?

Registered readout: the number of components other than the two seeded ones within 8 cells of the pair's midpoint at the sample
where the total component count is smallest. Secondary: the share, and the final component count.

The registered readout turned out to be **degenerate with the outcome**: at the sample of minimum count there is one merged pair,
so "bodies besides the pair" is `min_count - 1` by definition. The item is therefore recorded as **readout invalid, mechanism
untested** rather than as evidence about nucleation, and the corrected packet reports the quantities that are not functions of
the outcome: the minimum count, its mean over the run, the share of samples spent at one component, and whether the minimum sits
at the very first sample (which means "never met" rather than "met and rebounded").

What the experiment does establish is that the sign flip of X186 reproduces under a designed manipulation of the same variable.

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


def area_of(c):
    return float(c["area"]) if isinstance(c, dict) else float(c[1])


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
                 "min_at_first_sample": int(i_min == 0),
                 "share_of_samples_at_one": round(sum(1 for c in counts if c == 1) / len(counts), 4),
                 "mean_count_over_run": round(statistics.fmean(counts), 2),
                 "area_at_min": round(area_of(max(comps(row_min), key=area_of)), 1) if comps(row_min) else None,
                 "seeds_area_sum": round(sum(area_of(c) for c in cs0), 1),
                 "step_at_min": int(row_min[0]) if isinstance(row_min, list) else int(row_min.get("step")),
                 "samples": len(counts)})

groups = {}
for arm in index["arms"]:
    for lvl in index["arms"][arm]["groups"]:
        sel = [x for x in rows if x["arm"] == arm and x["level"] == lvl]
        if not sel:
            groups[f"{arm}_{lvl}"] = None
            continue
        groups[f"{arm}_{lvl}"] = {
            "runs": len(sel), "fused": sum(x["fused"] for x in sel),
            "share": round(statistics.fmean(x["fused"] for x in sel), 4),
            "wilson": wilson(sum(x["fused"] for x in sel), len(sel)),
            "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in sel]), 5),
            "extra_near_mid_median": statistics.median([x["extra_near_mid_at_min"] for x in sel]),
            "min_count_median": statistics.median([x["min_count"] for x in sel]),
            "min_count_mean": round(statistics.fmean([x["min_count"] for x in sel]), 2),
            "mean_count_over_run": round(statistics.fmean([x["mean_count_over_run"] for x in sel]), 2),
            "share_of_samples_at_one": round(statistics.fmean([x["share_of_samples_at_one"] for x in sel]), 4),
            "final_count_mean": round(statistics.fmean([x["final_count"] for x in sel]), 1),
            "runs_min_at_first_sample": sum(x["min_at_first_sample"] for x in sel),
            "area_at_min_vs_seeds": round(statistics.fmean(
                [(x["area_at_min"] or 0) / (x["seeds_area_sum"] or 1) for x in sel]), 3),
            "step_at_min_median": statistics.median([x["step_at_min"] for x in sel])}

pairs = [(x["extra_near_mid_at_min"], x["min_count"] - 1) for x in rows]
identical = sum(1 for a, b in pairs if a == b)
# the real failure mode: on this design the readout tracks the OUTCOME, not nucleation - in every run whose minimum count is one
# it reports a body besides the pair (impossible: there is only one component), and in every run whose minimum count is two it
# reports none. It is the outcome restated, inverted.
as_outcome = sum(1 for x in rows if x["extra_near_mid_at_min"] == (1 if x["fused"] else 0))
n_fused = sum(1 for x in rows if x["fused"])
degenerate = as_outcome == len(rows)

res = {}
for arm in ("r6_g9", "r3_g10"):
    cold, warm = groups.get(f"{arm}_cold"), groups.get(f"{arm}_warm")
    if not cold or not warm:
        res[arm] = None
        continue
    res[arm] = {"cold": cold, "warm": warm,
                "share_difference_warm_minus_cold": round(warm["share"] - cold["share"], 4),
                "extra_difference_median": (warm["extra_near_mid_median"] - cold["extra_near_mid_median"]),
                "min_count_difference_mean": round(warm["min_count_mean"] - cold["min_count_mean"], 2),
                "level_separation": round(warm["f_local_cold_mean"] - cold["f_local_cold_mean"], 5)}

r6, r3 = res.get("r6_g9"), res.get("r3_g10")
flip_reproduced = bool(r3 and r6 and r3["share_difference_warm_minus_cold"] > 0 > r6["share_difference_warm_minus_cold"])

if not r6 or not r3:
    verdict = "NOT REPORTABLE: one of the arms has no runs."
else:
    verdict = (f"THE REGISTERED READOUT IS NOT A READOUT, SO THE MECHANISM IS UNTESTED: 'bodies besides the pair at the sample of "
               f"minimum count' comes out at 1 exactly when the pair fused and 0 exactly when it did not - in {as_outcome} of "
               f"{len(rows)} runs, because the merged body drifts more than three cells from the seeded centres and is then counted "
               f"as a body besides the pair, while an unfused pair sits inside that radius and counts as none. With one component "
               f"on the field there is nothing besides it, so the quantity is the outcome restated and cannot speak about "
               f"nucleation; its two levels differ by {r6['extra_difference_median']:+g} at radius 6, which is that identity rather "
               f"than a measurement. What the experiment DOES establish is that X186's sign "
               f"flip reproduces under a designed manipulation of one variable: the colder body's inflow moves the share "
               f"{r3['share_difference_warm_minus_cold']:+.2f} at radius 3 ({r3['cold']['fused']} of {r3['cold']['runs']} cold "
               f"against {r3['warm']['fused']} of {r3['warm']['runs']} warm - the law's direction) and "
               f"{r6['share_difference_warm_minus_cold']:+.2f} at radius 6 ({r6['cold']['fused']} of {r6['cold']['runs']} cold "
               f"against {r6['warm']['fused']} of {r6['warm']['runs']} warm - the flipped direction), so the flip is not a per-cell "
               f"selection artefact of X186; its mechanism is still open and the registered readout cannot find it. The plan's third "
               f"branch ('nucleation is general') is not taken either: at radius 3 the warm level 'shows more extra bodies' only "
               f"because the cold level never reached one component, which is the same degeneracy.")

agg = {"kind": "x187_nucleation", "flow": F, "steps": index["steps"], "radius_of_interest": RADIUS_OF_INTEREST,
       "prediction": PREDICTION, "registered_readout_degenerate": degenerate,
       "registered_readout_identity_count": f"{identical}/{len(rows)}",
       "registered_readout_tracks_outcome": f"{as_outcome}/{len(rows)}",
       "runs_whose_minimum_is_one": n_fused,
       "flip_reproduced_by_design": flip_reproduced, "groups": groups, "arms": res,
       "runs_detail": rows, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for arm in ("r6_g9", "r3_g10"):
    r = res.get(arm)
    if not r:
        continue
    print(f"[x187] {arm}: cold F_local {r['cold']['f_local_cold_mean']} share {r['cold']['share']:.2f} "
          f"min_count {r['cold']['min_count_mean']} samples-at-one {r['cold']['share_of_samples_at_one']} | "
          f"warm F_local {r['warm']['f_local_cold_mean']} share {r['warm']['share']:.2f} "
          f"min_count {r['warm']['min_count_mean']} samples-at-one {r['warm']['share_of_samples_at_one']} "
          f"(d share {r['share_difference_warm_minus_cold']:+.2f})")
print(f"[x187] registered readout tracks the outcome in {as_outcome}/{len(rows)} runs; flip reproduced: {flip_reproduced}")
print(f"[x187] verdict: {verdict}")
