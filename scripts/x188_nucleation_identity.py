"""x188_nucleation_identity.py — X188: are there bodies besides the pair, by spatial continuation rather than by uid?

The pre-registration is reports/2026-11-04-x188-nucleation-identity-plan.md, amended before running (its section 8): uids are
re-issued at every division, so identity cannot trace the pair and the item uses nearest-continuation tracking instead. Same 24
committed X187 runs, no new field work.

Readout: at fixed samples (every 50 steps), track the pair by matching components to the previous sample's tracked centres within
4 cells, and count components that are neither the continuation nor within 3 cells of it ("other bodies") inside a 24-cell window
around the pair's **current** centre, and field-wide. Cross-tabulates the counts against the outcome, because X187's registered
readout failed exactly by being a function of the outcome.

Writes morphogenesis/experiments/E09_pond/l1_field_x188_nucleation_identity.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x188_nucleation_identity.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
FIXED_EVERY = 50
MATCH_CELLS = 4.0
NEAR_CELLS = 3.0
WINDOW_CELLS = 24.0
WARM_MINUS_COLD_BAR = 0.5


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


def area_of(c):
    return float(c["area"]) if isinstance(c, dict) else float(c[1])


def cstep(row):
    return int(row[0]) if isinstance(row, list) else int(row.get("step"))


def wrap_delta(a: float, b: float) -> float:
    d = (a - b + GRID / 2) % GRID - GRID / 2
    return d


def dist(p, q) -> float:
    return math.hypot(wrap_delta(p[0], q[0]), wrap_delta(p[1], q[1]))


def track_pair(series):
    """Return, per sample, the list of centres of the pair's tracked body (one entry once merged, two while separate)."""
    first = comps(series[0])
    tracked = [cxy(c) for c in first[:2]]
    tracked_area = sum(area_of(c) for c in first[:2])
    out = []
    for row in series:
        cs = comps(row)
        if not cs:
            out.append({"step": cstep(row), "n": 0, "tracked": list(tracked), "others": 0,
                        "others_window": 0, "n_in_window": 0})
            continue
        # the continuation is the component nearest to the tracked pair's largest centre; a merge or a division can change the
        # number of tracked components, so rebuild greedily: keep every component within MATCH_CELLS of any tracked centre.
        cands = [c for c in cs if any(dist(cxy(c), t) <= MATCH_CELLS for t in tracked)]
        if not cands:
            cands = [min(cs, key=lambda c: min(dist(cxy(c), t) for t in tracked))]
        tracked = [cxy(c) for c in cands]
        tracked_ids = {id(c) for c in cands}
        centre_t = max(tracked, key=lambda p: sum(dist(p, q) for q in tracked)) if len(tracked) > 1 else tracked[0]
        pair_mid = (statistics.fmean([p[0] for p in tracked]), statistics.fmean([p[1] for p in tracked]))
        others = [c for c in cs if id(c) not in tracked_ids and all(dist(cxy(c), t) > NEAR_CELLS for t in tracked)]
        in_win = [c for c in others if dist(cxy(c), pair_mid) <= WINDOW_CELLS / 2]
        out.append({"step": cstep(row), "n": len(cs), "tracked": list(tracked),
                    "others": len(others), "others_window": len(in_win),
                    "n_in_window": len([c for c in cs if dist(cxy(c), pair_mid) <= WINDOW_CELLS / 2]),
                    "pair_area": round(sum(area_of(c) for c in cands), 1), "tracked_area": tracked_area})
    return out


index = json.loads((L1 / "x187_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
runs_detail_windows = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    d = json.loads((L1 / f"x187_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    if len(series) < 2:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    g_cold = min(G_at(*cxy(c)) for c in cs0)
    f_local = F * (1 + AMP * (2 * g_cold - 1))
    counts = [len(comps(x)) for x in series]
    k_min = min(counts)
    tr = track_pair(series)
    fixed = [x for x in tr if x["step"] % FIXED_EVERY == 0 and x["step"] > 0]
    seen = {c[0] for row in series for c in comps(row)} if all(
        isinstance(c, (list, tuple)) for row in series for c in comps(row)) else set()
    win = [x for x in tr if 50 <= x["step"] <= 250]
    runs_detail_windows.append({
        "arm": r["arm"], "level": r["level"], "seed": r["seed"],
        "mean_contact_window": round(statistics.fmean([x["others_window"] for x in win]), 3) if win else 0.0,
        "mean_contact_field": round(statistics.fmean([x["others"] for x in win]), 2) if win else 0.0,
        "local_fraction": round((statistics.fmean([x["others_window"] for x in win]) /
                                 max(statistics.fmean([x["others"] for x in win]), 1e-9)), 4) if win else 0.0})
    runs.append({
        "arm": r["arm"], "level": r["level"], "seed": r["seed"], "f_local_cold": round(f_local, 5),
        "fused": int(k_min == 1), "min_count": k_min, "max_count": max(counts), "final_count": counts[-1],
        "uids_ever_seen": len(seen),
        "mean_others_window": round(statistics.fmean([x["others_window"] for x in fixed]), 3),
        "mean_others_field": round(statistics.fmean([x["others"] for x in fixed]), 3),
        "max_others_window": max(x["others_window"] for x in fixed),
        "samples_with_other_in_window": sum(1 for x in fixed if x["others_window"] > 0),
        "first_other_step": next((x["step"] for x in fixed if x["others_window"] > 0), None),
        "fixed_samples": len(fixed)})

contact = {}
for arm in index["arms"]:
    for lvl in index["arms"][arm]["groups"]:
        sel = [x for x in runs_detail_windows if x["arm"] == arm and x["level"] == lvl]
        contact[f"{arm}_{lvl}"] = None if not sel else {
            "runs": len(sel),
            "mean_others_window_50_250": round(statistics.fmean([x["mean_contact_window"] for x in sel]), 3),
            "mean_field_50_250": round(statistics.fmean([x["mean_contact_field"] for x in sel]), 2),
            "local_fraction": round(statistics.fmean([x["local_fraction"] for x in sel]), 4)}

groups = {}
for arm in index["arms"]:
    for lvl in index["arms"][arm]["groups"]:
        sel = [x for x in runs if x["arm"] == arm and x["level"] == lvl]
        if not sel:
            groups[f"{arm}_{lvl}"] = None
            continue
        groups[f"{arm}_{lvl}"] = {
            "runs": len(sel), "fused": sum(x["fused"] for x in sel),
            "share": round(statistics.fmean(x["fused"] for x in sel), 4),
            "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in sel]), 5),
            "mean_others_window": round(statistics.fmean([x["mean_others_window"] for x in sel]), 3),
            "mean_others_field": round(statistics.fmean([x["mean_others_field"] for x in sel]), 3),
            "max_others_window": max(x["max_others_window"] for x in sel),
            "runs_with_other_in_window": sum(1 for x in sel if x["samples_with_other_in_window"] > 0),
            "median_first_other_step": statistics.median([x["first_other_step"] for x in sel if x["first_other_step"]] or [None]) if any(x["first_other_step"] for x in sel) else None,
            "uids_ever_seen_mean": round(statistics.fmean([x["uids_ever_seen"] for x in sel]), 1)}

# validity: is the new readout a function of the outcome? It is only invalid if positivity tracks the outcome exactly - a
# readout that is positive everywhere (which is what happens here) does not predict the outcome, it simply does not discriminate
# at the binary level, and that is reported as such rather than called invalid.
tab = {}
for x in runs:
    key = (x["fused"], x["mean_others_window"] > 0)
    tab[f"fused={key[0]}&positive={key[1]}"] = tab.get(f"fused={key[0]}&positive={key[1]}", 0) + 1
pos = [x["mean_others_window"] > 0 for x in runs]
fus = [bool(x["fused"]) for x in runs]
tracks_outcome = all(a == b for a, b in zip(pos, fus)) or all(a != b for a, b in zip(pos, fus))
constant = len(set(pos)) == 1
invalid = tracks_outcome

r6c, r6w = groups["r6_g9_cold"], groups["r6_g9_warm"]
r3c, r3w = groups["r3_g10_cold"], groups["r3_g10_warm"]
d6 = round(r6w["mean_others_window"] - r6c["mean_others_window"], 3)
d3 = round(r3w["mean_others_window"] - r3c["mean_others_window"], 3)

if invalid:
    verdict = ("NO READOUT: positivity of the continuation-based count tracks the outcome exactly, so it is again a function of "
               "the outcome and this item makes no claim about nucleation.")
elif d6 >= WARM_MINUS_COLD_BAR and d3 < WARM_MINUS_COLD_BAR:
    verdict = (f"A WARM MEDIUM HOLDS MORE OTHER BODIES AROUND THE LARGEST PAIRS: at radius 6 gap 9 the warm level carries "
               f"{r6w['mean_others_window']} other bodies inside the window per fixed sample against {r6c['mean_others_window']} for "
               f"the cold level (difference {d6:+g}, registered bar {WARM_MINUS_COLD_BAR}), while at radius 3 gap 10 the same "
               f"manipulation moves it {d3:+g}; field-wide the two levels read {r6w['mean_others_field']} against "
               f"{r6c['mean_others_field']}. The size-specific part of the nucleation hypothesis is therefore supported by counting "
               "bodies rather than by the invalid X187 readout.")
elif d6 >= WARM_MINUS_COLD_BAR:
    verdict = (f"NUCLEATION IS NOT SIZE-SPECIFIC: the warm level holds more other bodies at radius 6 ({d6:+g}, bar "
               f"{WARM_MINUS_COLD_BAR}) and at radius 3 as well ({d3:+g}), so counting bodies does not separate the two arms' "
               "opposite signs and X186's flip needs another cause.")
else:
    verdict = (f"THE FLIP IS NOT NUCLEATION BY CONTINUATION EITHER: at radius 6 gap 9 the warm level carries "
               f"{r6w['mean_others_window']} other bodies inside the window per fixed sample against {r6c['mean_others_window']} "
               f"for the cold level (difference {d6:+g}, below the registered bar {WARM_MINUS_COLD_BAR}), so the bodies counted "
               "around the pair do not explain why the warm level coalesces less there; the mechanism question moves to the field "
               "level, as the refusal rule of section 5 says.")

agg = {"kind": "x188_nucleation_identity", "flow": F, "fixed_every": FIXED_EVERY, "match_cells": MATCH_CELLS,
       "near_cells": NEAR_CELLS, "window_cells": WINDOW_CELLS, "bar": WARM_MINUS_COLD_BAR,
       "amended_before_run": "uid identity replaced by spatial continuation (plan section 8)",
       "groups": groups, "outcome_crosstab": tab, "readout_invalid": invalid,
       "readout_constant_positive": constant,
       "exploratory_contact_window": {"steps": [50, 250], "note": "unregistered, added after the run: the fixed-sample average "
                                     "below pools the one-component phase with the 30-body phase, so the contact window is "
                                     "reported separately", "arms": contact},
       "radius6_warm_minus_cold": d6, "radius3_warm_minus_cold": d3,
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for k in ("r6_g9_cold", "r6_g9_warm", "r3_g10_cold", "r3_g10_warm"):
    g = groups.get(k)
    if g:
        print(f"[x188] {k}: share {g['share']:.2f}  others-in-window {g['mean_others_window']}  field {g['mean_others_field']}  "
              f"runs-with-any {g['runs_with_other_in_window']}/{g['runs']}  uids-seen {g['uids_ever_seen_mean']}")
print(f"[x188] warm-minus-cold others in window: radius6 {d6:+g} (bar {WARM_MINUS_COLD_BAR}), radius3 {d3:+g}; invalid {invalid}")
for k, v in contact.items():
    if v:
        print(f"[x188] {k} contact-window (50-250): others-in-window {v['mean_others_window_50_250']}, field {v['mean_field_50_250']}, local fraction {v['local_fraction']}")
print(f"[x188] verdict: {verdict}")
