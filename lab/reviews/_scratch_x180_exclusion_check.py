"""Impact of the missing x182/x184 exclusion in scripts/x180_dispersion.py.

Replicates the committed x180 pipeline with my own reader, once over all compacts and once
excluding the phase-selected families.  Read-only.  Run from the repo root:
  python lab/reviews/_scratch_x180_exclusion_check.py
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

L1 = Path("morphogenesis/experiments/L1_field")
GRID = 96
SCALE = 12.0


def G_at(x, y):
    ky = 2.0 * math.pi / max(2.0, SCALE)
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def point_biserial(values, flags):
    if len(values) < 6 or len(set(flags)) < 2 or len(set(values)) < 2:
        return None
    m1 = statistics.fmean([v for v, f in zip(values, flags) if f])
    m0 = statistics.fmean([v for v, f in zip(values, flags) if not f])
    sd = statistics.pstdev(values)
    if sd == 0:
        return None
    p = statistics.fmean(flags)
    return round((m1 - m0) / sd * math.sqrt(p * (1 - p)), 3)


def load(exclude_phase):
    runs = []
    for f in sorted(L1.glob("*.compact.json")):
        name = f.name.replace(".compact.json", "")
        if exclude_phase and name.startswith(("x182_", "x184_")):
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        series = d.get("series") or []
        params = d.get("params") or {}
        if not series or not isinstance(series[0], list) or len(series[0]) != 2:
            continue
        if not isinstance(series[0][1], list) or len(series[0][1]) != 2:
            continue
        cs = [(float(c[1]), float(c[2]), float(c[3])) for c in series[0][1]]
        r0 = math.sqrt(max(cs[0][0], 1) / math.pi)
        dx = abs(cs[0][1] - cs[1][1]) % GRID
        dx = min(dx, GRID - dx)
        dy = abs(cs[0][2] - cs[1][2]) % GRID
        dy = min(dy, GRID - dy)
        gap = round(math.hypot(dx, dy) - 2 * r0)
        mid = ((cs[0][1] + cs[1][1]) / 2.0, (cs[0][2] + cs[1][2]) / 2.0)
        fused = any(isinstance(r, list) and len(r) == 2 and isinstance(r[1], list) and len(r[1]) == 1 for r in series)
        runs.append({"file": name, "family": name.split("_s")[0], "gap": gap, "steps": int(params.get("steps", 0)),
                     "F": float(params.get("F", 0.0)), "g_mid": round(G_at(*mid), 4),
                     "r0": round(r0, 3), "fused": bool(fused)})
    return runs


def pipeline(runs):
    cells = defaultdict(list)
    for r in runs:
        cells[(round(r["r0"] / 0.2) * 0.2, r["gap"], r["F"], r["steps"])].append(r)
    per_cell = []
    for key, rs in sorted(cells.items()):
        flags = [int(r["fused"]) for r in rs]
        if len(rs) < 6 or len(set(flags)) < 2:
            continue
        pb = point_biserial([r["g_mid"] for r in rs], flags)
        per_cell.append({"key": key, "runs": len(rs), "fused": sum(flags),
                         "share": round(statistics.fmean(flags), 3), "pb": pb})
    pbs = [c["pb"] for c in per_cell if c["pb"] is not None]
    cell_of = {}
    for key, rs in cells.items():
        s = statistics.fmean([int(r["fused"]) for r in rs])
        for r in rs:
            cell_of[r["file"]] = s
    infl = [r for r in runs if 0.0 < cell_of.get(r["file"], 0.0) < 1.0]
    pooled = point_biserial([r["g_mid"] for r in infl], [int(r["fused"]) for r in infl])
    return {
        "runs_scanned": len(runs),
        "cells_with_both_outcomes": len(per_cell),
        "mean_point_biserial": round(statistics.fmean(pbs), 3) if pbs else None,
        "fused_higher_g": sum(1 for c in per_cell if c["pb"] is not None and c["pb"] > 0),
        "informative_runs": len(infl),
        "pooled_point_biserial": pooled,
        "cell_3_10_003_2000": next((c for c in per_cell if c["key"][1] == 10 and c["key"][2] == 0.03 and c["key"][3] == 2000), None),
    }


a = pipeline(load(False))
b = pipeline(load(True))
print("x180 pipeline, my replication:")
print(f"{'quantity':>28} | {'with all':>10} | {'x182/x184 out':>13}")
for k in a:
    print(f"{k:>28} | {str(a[k]):>10} | {str(b[k]):>13}")
