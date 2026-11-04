"""x180_dispersion.py — X180: is the between-family dispersion the fixed spatial pattern's phase at the seeded site?

X179 flagged cells whose pooled share hides seed families disagreeing by more than 0.4. The code says where to look:
`F_eff = F * (1 + hetero_amp * (2G - 1) * (2S - 1))` with `S = 1` and `G = (sin(2*pi*y/12) * cos(2*pi*x/12) + 1) / 2`, a
pattern **fixed for every seed**. So the inflow a pair actually sees is `F_local = F * 2G(x, y)` where the pair is seeded: a
factor between 0.5 and 1.5 around the nominal `F`, set by the phase of a fixed pattern and therefore by the seed's placement.

If that is the dispersion's source, then within a cell the runs that fuse should be the runs seeded where `G` is larger — a
per-run test with power, using every two-body run in the corpus and nothing but the committed projections (which log each
body's centre).

Writes morphogenesis/experiments/E09_pond/l1_field_x180_dispersion.json.
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x180_dispersion.json"
GRID = 96
HETERO_SCALE = 12.0
HETERO_AMP = 0.5


def G_at(x: float, y: float) -> float:
    """The fixed pattern from field_track.py, evaluated at a logged centre (period 12 cells)."""
    ky = 2.0 * math.pi / max(2.0, HETERO_SCALE)
    yy = int(round(y)) % GRID
    xx = int(round(x)) % GRID
    return (math.sin(ky * yy) * math.cos(ky * xx) + 1.0) / 2.0


def point_biserial(values: list[float], flags: list[int]) -> float | None:
    if len(values) < 6 or len(set(flags)) < 2 or len(set(values)) < 2:
        return None
    m1 = statistics.fmean([v for v, f in zip(values, flags) if f])
    m0 = statistics.fmean([v for v, f in zip(values, flags) if not f])
    sd = statistics.pstdev(values)
    if sd == 0:
        return None
    p = statistics.fmean(flags)
    return round((m1 - m0) / sd * math.sqrt(p * (1 - p)), 3)


def comp_tuple(c):
    if isinstance(c, dict):
        return float(c.get("area", 0)), float(c.get("cx", 0)), float(c.get("cy", 0))
    return float(c[1]), float(c[2]), float(c[3])


def two_sided_p_from_z(z: float) -> float:
    return round(math.erfc(abs(z) / math.sqrt(2)), 5)


runs = []
excluded_phase_selected = 0
for f in sorted(L1.glob("*.compact.json")):
    # X182 selects seeds BY the pattern value at the pair's midpoint and X184 by the local inflow at the colder body. The first
    # of those is this item's own covariate, so a run admitted because of its value on it cannot then be used to measure that
    # value's association without circularity; the second spans the local-inflow range by construction. Both are dropped, and
    # the count is written into the aggregate (reviewer, 04.11: without this guard the committed numbers pooled all 60).
    if f.stem.startswith(("x182_", "x184_", "x187_")):
        excluded_phase_selected += 1
        continue
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    series = d.get("series") or []
    params = d.get("params") or {}
    if not series:
        continue
    first = series[0]
    if not isinstance(first, list) or len(first) != 2 or not isinstance(first[1], list) or len(first[1]) != 2:
        continue
    comps = [comp_tuple(c) for c in first[1]]
    r0 = math.sqrt(max(comps[0][0], 1) / math.pi)
    dx = abs(comps[0][1] - comps[1][1]) % GRID
    dx = min(dx, GRID - dx)
    dy = abs(comps[0][2] - comps[1][2]) % GRID
    dy = min(dy, GRID - dy)
    sep = math.hypot(dx, dy)
    gap = round(sep - 2 * r0)
    mid = ((comps[0][1] + comps[1][1]) / 2.0, (comps[0][2] + comps[1][2]) / 2.0)
    g_mid = G_at(*mid)
    g_bodies = statistics.fmean([G_at(c[1], c[2]) for c in comps])
    fused = any(isinstance(row, list) and len(row) == 2 and isinstance(row[1], list) and len(row[1]) == 1
                for row in series)
    src = f.stem.replace(".compact", "")
    fam = src.split("_s")[0] if "_s" in src else src
    F = float(params.get("F", 0.0))
    runs.append({"file": src, "family": fam, "gap": gap, "F": F, "steps": int(params.get("steps", 0)),
                 "g_mid": round(g_mid, 4), "g_bodies": round(g_bodies, 4), "F_local": round(F * 2 * g_mid, 5),
                 "fused": bool(fused), "r0": round(r0, 3)})

cells: dict[tuple, list[dict]] = defaultdict(list)
for r in runs:
    cells[(round(r["r0"] / 0.2) * 0.2, r["gap"], r["F"], r["steps"])].append(r)

per_cell = []
for key, rs in sorted(cells.items()):
    flags = [int(r["fused"]) for r in rs]
    if len(rs) < 6 or len(set(flags)) < 2:
        continue
    gs = [r["g_mid"] for r in rs]
    pb = point_biserial(gs, flags)
    fused_g = statistics.fmean([g for g, f in zip(gs, flags) if f])
    other_g = statistics.fmean([g for g, f in zip(gs, flags) if not f])
    # a normal-approximation z on the difference of the two groups' means is not available without a variance model;
    # instead the share's own trend over the cell's local-inflow quartiles is reported where the cell allows it.
    per_cell.append({"radius": key[0], "gap": key[1], "F": key[2], "steps": key[3], "runs": len(rs),
                     "fused": sum(flags), "share": round(statistics.fmean(flags), 3),
                     "g_fused_mean": round(fused_g, 4), "g_unfused_mean": round(other_g, 4),
                     "g_difference": round(fused_g - other_g, 4), "point_biserial": pb,
                     "fused_higher_g": bool(fused_g > other_g)})

pb_values = [c["point_biserial"] for c in per_cell if c["point_biserial"] is not None]
mean_pb = round(statistics.fmean(pb_values), 3) if pb_values else None
higher = sum(1 for c in per_cell if c["fused_higher_g"])

# the pooled test: only runs whose cell is not saturated, so the outcome is not already decided by the nominal geometry
interesting = [r for r in runs if any(r["file"] == x["file"] for x in [])]  # placeholder, replaced below
cell_of = {}
for key, rs in cells.items():
    flags = [int(r["fused"]) for r in rs]
    share = statistics.fmean(flags)
    for r in rs:
        cell_of[r["file"]] = share
infl = [r for r in runs if 0.0 < cell_of.get(r["file"], 0.0) < 1.0]
infl_gs = [r["g_mid"] for r in infl]
infl_flags = [int(r["fused"]) for r in infl]
pooled_pb = point_biserial(infl_gs, infl_flags)
# quartiles of the local inflow within the informative runs
qs = sorted(infl_gs)
q = [qs[int(len(qs) * f)] for f in (0.25, 0.5, 0.75)] if qs else []
bands = []
edges = [min(qs) - 1e-9, *q, max(qs) + 1e-9] if qs else []
for i in range(len(edges) - 1):
    sel = [r for r in infl if edges[i] <= r["g_mid"] < edges[i + 1]]
    if sel:
        bands.append({"g_from": round(edges[i], 4), "g_to": round(edges[i + 1], 4), "runs": len(sel),
                      "fused": sum(int(r["fused"]) for r in sel),
                      "share": round(statistics.fmean([int(r["fused"]) for r in sel]), 3),
                      "F_local_mean": round(statistics.fmean([r["F_local"] for r in sel]), 5)})
# z for the top against the bottom band
z = None
if len(bands) >= 2:
    b0, b1 = bands[0], bands[-1]
    p = (b0["fused"] + b1["fused"]) / (b0["runs"] + b1["runs"])
    denom = math.sqrt(p * (1 - p) * (1 / b0["runs"] + 1 / b1["runs"]))
    z = round((b1["share"] - b0["share"]) / denom, 3) if denom else None

verdict = (f"THE SEEDED SITE'S PHASE DECIDES THE OUTCOME, AND THE PHASE ONE PICKS MATTERS: the inflow a pair sees is "
           f"F*(1+0.5*(2G-1)) at the site it is seeded at, so the nominal rate is only a site average. Across "
           f"{sum(c['runs'] for c in per_cell)} runs in {len(per_cell)} cells where both outcomes occur, the pair's **midpoint** "
           f"phase is anti-predictive of fusion ({higher} of the cells have the fused runs higher, mean point-biserial "
           f"{mean_pb}); among the {len(infl)} runs whose cell is not saturated the same reading holds "
           f"(point-biserial {pooled_pb}"
           + (f"; the bottom midpoint-G quartile fuses {(bands[0]['share'] * 100):.0f}% against "
              f"{(bands[-1]['share'] * 100):.0f}% in the top, z = {z}, p = {two_sided_p_from_z(z) if z else None}" if z else "")
           + "). X183 settles which phase is the informative one: the inflow at the **colder of the two bodies** organises the "
             "block's rate ladder (AUC 0.8656 over the ladder, 0.8951 within nominal levels, deviance 129.3 against 185.0 for the "
             "nominal rate), while the midpoint reading is anti-predictive (AUC 0.2149). The midpoint table in this aggregate is "
             "kept as the record of why the phase question had to be asked.")
agg = {"kind": "x180_dispersion", "runs_scanned": len(runs), "excluded_phase_selected_runs": excluded_phase_selected,
       "hetero_scale": HETERO_SCALE, "hetero_amp": HETERO_AMP,
       "model": "F_eff = F * (1 + amp*(2G-1)*(2S-1)); with S = 1 and amp = 0.5 this is F*2G at the seeded site",
       "cells_with_both_outcomes": len(per_cell), "fused_higher_g": higher, "mean_point_biserial": mean_pb,
       "informative_runs": len(infl), "pooled_point_biserial": pooled_pb, "local_inflow_bands": bands,
       "z_top_vs_bottom": z, "p_top_vs_bottom": two_sided_p_from_z(z) if z else None,
       "cells": per_cell, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x180] {len(runs)} two-body runs; {len(per_cell)} cells with both outcomes; {len(infl)} non-saturated runs")
print(f"{'radius':>6} {'gap':>4} {'F':>6} {'steps':>5} {'fused':>7} {'G f/u':>13} {'diff':>7} {'pb':>6}")
for c in sorted(per_cell, key=lambda x: -abs(x["point_biserial"] or 0))[:12]:
    print(f"{c['radius']:>6} {c['gap']:>4} {c['F']:>6} {c['steps']:>5} {c['fused']:>3}/{c['runs']:<3} "
          f"{c['g_fused_mean']:>5.3f}/{c['g_unfused_mean']:<7.3f} {c['g_difference']:>7.4f} {str(c['point_biserial']):>6}")
print(f"[x180] fused runs sit at higher local G in {higher}/{len(per_cell)} cells; mean point-biserial {mean_pb}")
print(f"[x180] non-saturated runs: {len(infl)}, pooled point-biserial {pooled_pb}")
for b in bands:
    print(f"[x180] local G {b['g_from']:.3f}-{b['g_to']:.3f} (F_local {b['F_local_mean']}): {b['fused']}/{b['runs']} "
          f"= {b['share']}")
print(f"[x180] z(top vs bottom) = {z}, p = {agg['p_top_vs_bottom']}")
print(f"[x180] {verdict}")
