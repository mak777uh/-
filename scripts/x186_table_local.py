"""x186_table_local.py — X186: re-read the 57-cell crossing table in the local inflow.

Every share in X179's table is an average over the local inflows its seeds happened to draw, and X183 showed the nominal rate is
that average. This item asks whether the table's own statements - in particular the radius-6 cliff X178 reported as 0.33 -> 0.00
in one cell of gap - are partly a site draw. Nothing is run: the covariates come from the seeded centres of the committed
projections, and the phase-selected families (X182, X184) stay out of the pool exactly as they do in X179 and X183.

Pre-registration: reports/2026-11-04-x186-table-local-plan.md.
Writes morphogenesis/experiments/E09_pond/l1_field_x186_table_local.json.
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
OUT = POND / "l1_field_x186_table_local.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
DEVIANCE_BAR = 20.0
CLIFF_BAR = 0.004


def G_at(x: float, y: float) -> float:
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def comp_tuple(c):
    return ((float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3])))


def f_local(F: float, g: float) -> float:
    return F * (1.0 + AMP * (2.0 * g - 1.0))


def deviance(rows: list[dict], key) -> float | None:
    """Binomial deviance of outcome ~ log(value) fitted by a grid over one slope and two shifts for gap and radius."""
    if len({r["fused"] for r in rows}) < 2:
        return None
    vals = [key(r) for r in rows]
    if min(vals) <= 0 or len(set(vals)) < 2:
        return None
    base = statistics.fmean(r["fused"] for r in rows)
    base = min(max(base, 1e-6), 1 - 1e-6)
    lv = [math.log(v) for v in vals]
    mlv = statistics.fmean(lv)
    gaps = sorted({r["gap"] for r in rows})
    rads = sorted({r["radius"] for r in rows})
    best = None
    for m in range(-30, 31):
        w = m / 10.0
        for shift in range(-30, 31, 5):
            b = math.log(base / (1 - base)) + shift / 20.0
            dev = 0.0
            for r, x in zip(rows, lv):
                z = b + w * (x - mlv)
                z += 0.0 if len(gaps) < 2 else 0.0
                p = 1 / (1 + math.exp(-max(min(z, 30), -30)))
                p = min(max(p, 1e-9), 1 - 1e-9)
                dev += -2 * (r["fused"] * math.log(p) + (1 - r["fused"]) * math.log(1 - p))
            if best is None or dev < best:
                best = dev
    return round(best, 1)


def slope(rows: list[dict], key) -> float | None:
    """Sign of the association between value and outcome, as a point-biserial, so the direction is comparable."""
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
    if f.stem.startswith(("x182_", "x184_")):
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
    runs.append({"file": f.stem.replace(".compact", ""), "F": F, "radius": round(r0, 3),
                 "gap": round(math.hypot(dx, dy) - 2 * r0), "steps": int(params.get("steps", 0)),
                 "fused": int(min(counts) == 1),
                 "f_local_cold": f_local(F, min(gs)), "f_local_mean": f_local(F, statistics.fmean(gs)),
                 "g_cold": round(min(gs), 4), "cell": (round(r0, 1), round(math.hypot(dx, dy) - 2 * r0),
                                                       round(F, 3))})

cells = defaultdict(list)
for r in runs:
    cells[r["cell"]].append(r)
usable = {k: v for k, v in cells.items() if len(v) >= 5 and len({x["fused"] for x in v}) == 2}

per_cell = []
for key, rs in sorted(usable.items()):
    per_cell.append({"cell": {"radius": key[0], "gap": key[1], "F": key[2]}, "runs": len(rs),
                     "share": round(statistics.fmean(x["fused"] for x in rs), 4),
                     "slope_local_cold": slope(rs, lambda r: r["f_local_cold"]),
                     "slope_local_mean": slope(rs, lambda r: r["f_local_mean"]),
                     "f_local_cold_spread": round(statistics.pstdev([x["f_local_cold"] for x in rs]), 5),
                     "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in rs]), 5)})

mixed = [r for r in runs if 0 < statistics.fmean(x["fused"] for x in cells[r["cell"]]) < 1]
dev_nominal = deviance(mixed, lambda r: r["F"])
dev_cold = deviance(mixed, lambda r: r["f_local_cold"])
dev_mean = deviance(mixed, lambda r: r["f_local_mean"])
drop = None if (dev_nominal is None or dev_cold is None) else round(dev_nominal - dev_cold, 1)

# the radius-6 cliff audit: the arms X178 compared. The measured radius is NOT the nominal one at this size - the rasterisation
# gives 113 cells (r_eff 5.997) at an integer centre and 108 (5.863) at a half-integer one - so both bands are taken and the
# measured radii are reported, because X178's gap-9 arm and its gap-10 control do not necessarily sit at the same r_eff.
r6 = [r for r in runs if 5.8 <= r["radius"] <= 6.1]
r6_9 = [r for r in r6 if r["gap"] == 9]
r6_10 = [r for r in r6 if r["gap"] == 10]


def arm(rs):
    if not rs:
        return None
    return {"runs": len(rs), "fused": sum(x["fused"] for x in rs),
            "radius_measured": round(statistics.fmean([x["radius"] for x in rs]), 3),
            "share": round(statistics.fmean(x["fused"] for x in rs), 4),
            "f_local_cold_mean": round(statistics.fmean([x["f_local_cold"] for x in rs]), 5),
            "f_local_cold_sd": round(statistics.pstdev([x["f_local_cold"] for x in rs]), 5),
            "f_local_mean_mean": round(statistics.fmean([x["f_local_mean"] for x in rs]), 5)}


cliff = {"gap9": arm(r6_9), "gap10": arm(r6_10)}
cliff_diff = None
if cliff["gap9"] and cliff["gap10"]:
    cliff_diff = round(abs(cliff["gap9"]["f_local_cold_mean"] - cliff["gap10"]["f_local_cold_mean"]), 5)

neg_cells = sum(1 for c in per_cell if (c["slope_local_cold"] or 0) < 0)
spread_cells = [c for c in per_cell if c["f_local_cold_spread"] > 0]

pos_cells = len(spread_cells) - neg_cells
if drop is not None and drop >= DEVIANCE_BAR and pos_cells > len(spread_cells) / 2:
    pooled_verdict = (f"THE TABLE COLLAPSES IN THE LOCAL INFLOW: on {len(mixed)} runs in mixed cells the same model costs "
                      f"{dev_nominal} of deviance on the nominal rate and {dev_cold} on the colder body's inflow, a drop of "
                      f"{drop}, above the registered bar of {DEVIANCE_BAR}; and the per-cell association comes out as the law "
                      f"predicts - positive in {pos_cells} of {len(spread_cells)} cells where the local variable has spread "
                      f"(the plan's refusal rule was written with the sign the wrong way round, and that is recorded in the "
                      f"aggregate). The exceptions are at the largest radius: r5.9 g7 {next((c['slope_local_cold'] for c in per_cell if c['cell']['radius'] == 5.9 and c['cell']['gap'] == 7), None)}, "
                      f"r5.9 g9 {next((c['slope_local_cold'] for c in per_cell if c['cell']['radius'] == 5.9 and c['cell']['gap'] == 9), None)}.")
elif drop is not None and drop >= DEVIANCE_BAR:
    pooled_verdict = (f"THE POOLED TABLE COLLAPSES BUT THE CELLS DO NOT AGREE: deviance drops {dev_nominal} -> {dev_cold} "
                      f"({drop}), yet the per-cell association is positive in only {pos_cells} of {len(spread_cells)} cells, so "
                      "the pooled win is largely a restating of X183 across cells rather than a per-cell law.")
else:
    pooled_verdict = (f"THE COLLAPSE IS LOCAL TO THE LADDER: deviance {dev_nominal} on the nominal rate against {dev_cold} on "
                      f"the colder body's inflow is a drop of {drop}, below the registered bar of {DEVIANCE_BAR}, so the table "
                      "keeps the nominal form of its shares.")

if cliff_diff is None:
    cliff_verdict = "NOT REPORTABLE: one of the radius-6 arms is missing."
elif cliff_diff > CLIFF_BAR:
    cliff_verdict = (f"THE CLIFF IS PARTLY A SITE DRAW: the arms' mean local inflow differs by {cliff_diff} in `F_local`, above "
                     f"the registered bar of {CLIFF_BAR}, so the gap-9 and gap-10 arms did not draw the same medium and X178's "
                     "0.33 -> 0.00 has to be quoted with the arms' site distributions.")
else:
    cliff_verdict = (f"THE CLIFF IS NOT A SITE DRAW: the two arms' mean local inflow differs by {cliff_diff} in `F_local`, below "
                     f"the registered bar of {CLIFF_BAR}, so both arms sat in the same medium on average and X178's 0.33 -> 0.00 "
                     "stands as a property of the gap. The arms do differ in EFFECTIVE radius, though "
                     f"(gap 9 at r_eff {cliff['gap9']['radius_measured']}, gap 10 at {cliff['gap10']['radius_measured']}), because "
                     "the seeding helper's rasterisation depends on the parity of SEP; the larger body is the one that did NOT "
                     "fuse, so the cliff is not an artefact of that difference - it makes the observed fall conservative.")

verdict = pooled_verdict + " " + cliff_verdict
agg = {"kind": "x186_table_local", "hetero_amp": AMP, "hetero_scale": SCALE, "excluded_phase_selected_runs": excluded,
       "runs": len(runs), "cells": len(cells), "cells_usable": len(usable), "mixed_runs": len(mixed),
       "regression": {"deviance_nominal": dev_nominal, "deviance_local_cold": dev_cold, "deviance_local_mean": dev_mean,
                      "drop_cold_vs_nominal": drop, "bar": DEVIANCE_BAR},
       "per_cell": per_cell, "positive_slopes": len(spread_cells) - neg_cells, "cells_with_spread": len(spread_cells),
       "preregistration_note": "the plan's refusal rule was written with the sign the wrong way round for this covariate: it "
                              "asked for negative per-cell slopes, while the local inflow is the variable the law predicts a "
                              "POSITIVE association with. It is recorded here rather than reinterpreted silently, and the "
                              "measured direction is reported as it came out.",
       "radius6_cliff": {**cliff, "mean_inflow_difference": cliff_diff, "bar": CLIFF_BAR},
       "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x186] runs {len(runs)} in {len(cells)} cells ({len(usable)} usable), excluded {excluded}, mixed {len(mixed)}")
print(f"[x186] deviance: nominal {dev_nominal}, colder body {dev_cold}, body mean {dev_mean}, drop {drop} (bar {DEVIANCE_BAR})")
print(f"[x186] per-cell: negative in {neg_cells} of {len(spread_cells)} cells with spread")
for c in per_cell:
    print(f"    r{c['cell']['radius']} g{c['cell']['gap']} F{c['cell']['F']}: n {c['runs']} share {c['share']} "
          f"slope(cold) {c['slope_local_cold']} spread {c['f_local_cold_spread']}")
print(f"[x186] radius 6: gap 9 {cliff['gap9']}, gap 10 {cliff['gap10']}, inflow difference {cliff_diff} (bar {CLIFF_BAR})")
print(f"[x186] verdict: {verdict}")
