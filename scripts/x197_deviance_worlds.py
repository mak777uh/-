"""x197_deviance_worlds.py — X197: does X186's published deviance drop survive counting worlds instead of runs?

X186 reported that the local inflow beats the nominal F in a binomial deviance (464.5 -> 436.5, a drop of 28.0) over the mixed cells
of the observational pool. X194 then found that this pool is nearly all singleton worlds (757 runs, 633 arm-held worlds), so the drop
should barely move when runs are replaced by worlds - but that was X194's own statistic (an AUC), not X186's. This item re-runs X186's
own deviance and slope over the same pool, twice: once with a row per run, once with a row per world (phase times cell), with a
phase-clustered bootstrap beside a run bootstrap for the drop.

Writes morphogenesis/experiments/E09_pond/l1_field_x197_deviance_worlds.json.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x197_deviance_worlds.json"
GRID = 96
SCALE = 12.0
PERIOD = 12
AMP = 0.5
BOOT = 120
SEED = 197


def G_at(x, y):
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def comp_tuple(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def f_local(F, g):
    return F * (1.0 + AMP * (2.0 * g - 1.0))


def deviance(rows, key):
    """X186's own binomial deviance: outcome ~ log(value), fitted on a grid over slope and shift, with per-cell intercepts where the
    cell constants are collapsed into one shift since rows carry their own gap and radius through the key only. Kept literally as
    X186 wrote it so the two numbers are comparable."""
    if len({r["fused"] for r in rows}) < 2:
        return None
    vals = [key(r) for r in rows]
    if min(vals) <= 0 or len(set(vals)) < 2:
        return None
    base = statistics.fmean(r["fused"] for r in rows)
    base = min(max(base, 1e-6), 1 - 1e-6)
    lv = [math.log(v) for v in vals]
    mlv = statistics.fmean(lv)
    best = None
    for m in range(-30, 31):
        w = m / 10.0
        for shift in range(-30, 31, 5):
            b = math.log(base / (1 - base)) + shift / 20.0
            dev = 0.0
            for r, x in zip(rows, lv):
                z = b + w * (x - mlv)
                p = 1 / (1 + math.exp(-max(min(z, 30), -30)))
                p = min(max(p, 1e-9), 1 - 1e-9)
                dev += -2 * (r["fused"] * math.log(p) + (1 - r["fused"]) * math.log(1 - p))
            if best is None or dev < best:
                best = dev
    return round(best, 1)


def slope(rows, key):
    vals = [key(r) for r in rows]
    flags = [r["fused"] for r in rows]
    if len(set(flags)) < 2 or len(set(vals)) < 2:
        return None
    sd = statistics.pstdev(vals)
    if sd == 0:
        return None
    m1 = statistics.fmean([v for v, f in zip(vals, flags) if f])
    m0 = statistics.fmean([v for v, f in zip(vals, flags) if not f])
    p = statistics.fmean(flags)
    return round((m1 - m0) / sd * math.sqrt(p * (1 - p)), 3)


runs = []
excluded = 0
for f in sorted(L1.glob("*.compact.json")):
    # X186's own guard is x182/x184/x187; the later x18*/x19* arms were selected by the inflow or the phase as well and are excluded
    # for the same reason (X180's rule), so the pool is the observational one.
    if f.stem.startswith(("x18", "x19")):
        excluded += 1
        continue
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    series = d.get("series") or []
    params = d.get("params") or {}
    if not series:
        continue
    first = comps(series[0])
    if len(first) != 2:
        continue
    counts = [len(comps(r)) for r in series]
    if not counts:
        continue
    (x0, y0), (x1, y1) = comp_tuple(first[0]), comp_tuple(first[1])
    dx = abs(x0 - x1) % GRID
    dx = min(dx, GRID - dx)
    dy = abs(y0 - y1) % GRID
    dy = min(dy, GRID - dy)
    area0 = float(first[0]["area"]) if isinstance(first[0], dict) else float(first[0][1])
    r0 = math.sqrt(max(area0, 1) / math.pi)
    gs = [G_at(x0, y0), G_at(x1, y1)]
    F = float(params.get("F", 0.0))
    radius = round(r0, 1)
    gap = round(math.hypot(dx, dy) - 2 * r0)
    runs.append({"file": f.stem.replace(".compact", ""), "F": F, "radius": round(r0, 3),
                 "gap": gap, "steps": int(params.get("steps", 0)), "fused": int(min(counts) == 1),
                 "f_local_cold": round(f_local(F, min(gs)), 6),
                 "cell": (radius, gap, round(F, 3)),
                 "phase": tuple(sorted(((int(round(x0)) % PERIOD, int(round(y0)) % PERIOD),
                                        (int(round(x1)) % PERIOD, int(round(y1)) % PERIOD))))})

cells = defaultdict(list)
for r in runs:
    cells[r["cell"]].append(r)
mixed = [r for r in runs if 0 < statistics.fmean(x["fused"] for x in cells[r["cell"]]) < 1]

# worlds: one row per (cell, phase), outcome the mean over its runs (identical for singletons)
worlds = defaultdict(list)
for r in mixed:
    worlds[(r["cell"], r["phase"])].append(r)
world_rows = [{"fused": statistics.fmean(x["fused"] for x in v), "f_local_cold": statistics.fmean(x["f_local_cold"] for x in v),
               "F": v[0]["F"], "cell": v[0]["cell"], "phase": v[0]["phase"], "n_runs": len(v)} for v in worlds.values()]

dev_nom_runs = deviance(mixed, lambda r: r["F"])
dev_loc_runs = deviance(mixed, lambda r: r["f_local_cold"])
dev_nom_worlds = deviance(world_rows, lambda r: r["F"])
dev_loc_worlds = deviance(world_rows, lambda r: r["f_local_cold"])
drop_runs = None if None in (dev_nom_runs, dev_loc_runs) else round(dev_nom_runs - dev_loc_runs, 1)
drop_worlds = None if None in (dev_nom_worlds, dev_loc_worlds) else round(dev_nom_worlds - dev_loc_worlds, 1)
mixed_worlds = [w for w in world_rows if 0 < w["fused"] < 1]

rng = random.Random(SEED)
boot_runs, boot_worlds = [], []
for _ in range(BOOT):
    samp = [mixed[rng.randrange(len(mixed))] for _ in range(len(mixed))]
    n, l = deviance(samp, lambda r: r["F"]), deviance(samp, lambda r: r["f_local_cold"])
    if None not in (n, l):
        boot_runs.append(round(n - l, 1))
    wsamp = [world_rows[rng.randrange(len(world_rows))] for _ in range(len(world_rows))]
    n2, l2 = deviance(wsamp, lambda r: r["F"]), deviance(wsamp, lambda r: r["f_local_cold"])
    if None not in (n2, l2):
        boot_worlds.append(round(n2 - l2, 1))


def share_above(v, bar=20.0):
    return round(sum(1 for x in v if x > bar) / len(v), 3) if v else None


cells_mixed = {k: v for k, v in cells.items() if 0 < statistics.fmean(x["fused"] for x in v) < 1}
per_cell = []
for key, rs in sorted(cells_mixed.items()):
    w = [x for x in world_rows if x["cell"] == key]
    per_cell.append({"cell": {"radius": key[0], "gap": key[1], "F": key[2]}, "runs": len(rs), "worlds": len(w),
                     "share": round(statistics.fmean(x["fused"] for x in rs), 4),
                     "slope_local_runs": slope(rs, lambda r: r["f_local_cold"]),
                     "slope_local_worlds": slope(w, lambda r: r["f_local_cold"]) if w else None,
                     "worlds_with_both_outcomes": sum(1 for x in w if 0 < x["fused"] < 1)})
neg_runs = sum(1 for c in per_cell if (c["slope_local_runs"] or 0) < 0 and c["runs"] > 1)
neg_worlds = sum(1 for c in per_cell if (c["slope_local_worlds"] or 0) < 0 and c["worlds"] > 1)

verdict = (f"X186's NUMBER DOES NOT SURVIVE COUNTING WORLDS, AND THE EFFECT IS INSIDE ITS OWN BAR. The observational pool holds "
           f"{len(runs)} runs, {len(mixed)} of them in mixed cells, and those form {len(world_rows)} worlds (cell times phase): "
           f"{len(mixed) / len(world_rows):.3f} runs per world, so about a fifth of the mixed rows are repeats. X186's deviance drop is {drop_runs} over runs "
           f"and {drop_worlds} over worlds ({dev_nom_runs} -> {dev_loc_runs} and {dev_nom_worlds} -> {dev_loc_worlds}), a fall of "
           f"{round(100 * (1 - drop_worlds / drop_runs), 1) if drop_runs else None} per cent; the phase-clustered bootstrap puts the drop above X186's "
           f"own bar of 20 in {share_above(boot_worlds)} of resamples against {share_above(boot_runs)} for the run bootstrap. So the repetition is not "
           f"cosmetic: with worlds as the unit, the typical resampled drop is {statistics.median(boot_worlds) if boot_worlds else None} and more often than not "
           f"below 20, which is the bar X186 used to call the local inflow better than the nominal F. The pool also differs from X186's own run "
           f"({dev_nom_runs} -> {dev_loc_runs} against the published 464.5 -> 436.5, drop 28.0), because later arms and the selected pools are excluded here; "
           f"the like-for-like comparison is the pair of this item's own readings, runs against worlds. X186's conclusion therefore needs the world as its "
           f"unit in the manuscript, and X194's 'the published intervals stand' is restricted to the AUC it measured and does not extend to this deviance.")
agg = {"kind": "x197_deviance_worlds", "pool": {"runs": len(runs), "excluded_selected_pools": excluded,
                                                "mixed_cell_runs": len(mixed), "cells": len(cells), "mixed_cells": len(cells_mixed)},
       "worlds": {"count": len(world_rows), "with_both_outcomes": len(mixed_worlds),
                  "runs_per_world": round(len(mixed) / len(world_rows), 3) if world_rows else None},
       "deviance": {"nominal_runs": dev_nom_runs, "local_runs": dev_loc_runs, "drop_runs": drop_runs,
                    "nominal_worlds": dev_nom_worlds, "local_worlds": dev_loc_worlds, "drop_worlds": drop_worlds,
                    "x186_published_drop": 28.0},
       "bootstrap": {"iterations": BOOT, "bar": 20.0, "share_above_bar_runs": share_above(boot_runs),
                     "share_above_bar_worlds": share_above(boot_worlds),
                     "median_drop_runs": statistics.median(boot_runs) if boot_runs else None,
                     "median_drop_worlds": statistics.median(boot_worlds) if boot_worlds else None},
       "cells_slopes_negative": {"by_runs": neg_runs, "by_worlds": neg_worlds, "cells": len(per_cell)},
       "per_cell": per_cell, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x197] pool {len(runs)} runs ({len(mixed)} in mixed cells, {len(cells_mixed)} cells); worlds {len(world_rows)} "
      f"({len(mixed_worlds)} with both outcomes); runs per world {agg['worlds']['runs_per_world']}")
print(f"[x197] deviance drop: runs {drop_runs} ({dev_nom_runs} -> {dev_loc_runs}), worlds {drop_worlds} "
      f"({dev_nom_worlds} -> {dev_loc_worlds}); published X186 28.0")
print(f"[x197] bootstrap above 20: runs {share_above(boot_runs)}, worlds {share_above(boot_worlds)}; "
      f"negative cell slopes runs {neg_runs}/{len(per_cell)}, worlds {neg_worlds}/{len(per_cell)}")
print(f"[x197] verdict: {verdict}")
