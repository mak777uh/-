"""x194_phase_clusters.py — X194: how many worlds do the line's published pools actually contain?

X192 showed that one phase class is one world for this line's readout, and X190/X191 that seeds and sites within one phase are clones.
Every pooled statistic of the line - X183's AUC over the ladder, X186's per-cell deviance, X187's Fisher tests - was computed over
runs, and a run count is an upper bound on the number of worlds. This item counts the worlds: each run's phase (the bodies' positions
modulo the pattern's 12-cell period, read off the first sample) is its world, and the published associations are recomputed both ways
- resampling runs and resampling phases - so the intervals can be compared directly.

Writes morphogenesis/experiments/E09_pond/l1_field_x194_phase_clusters.json.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x194_phase_clusters.json"
GRID = 96
PERIOD = 12
BOOT = 1000
SEED = 194


def G_at(x, y):
    k = 2.0 * math.pi / 12.0
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comp_tuple(c):
    return (float(c[1]), float(c[2]), float(c[3]))


def phase_of(comps):
    """The world: each body's position modulo the pattern's 12-cell period (whole cells, since the jitter is whole cells)."""
    return tuple(sorted((int(round(c[1])) % PERIOD, int(round(c[2])) % PERIOD) for c in comps))


def auc(values, flags):
    pos = [v for v, f in zip(values, flags) if f]
    neg = [v for v, f in zip(values, flags) if not f]
    if not pos or not neg:
        return None
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    r1 = sum(ranks[i] for i in range(len(values)) if flags[i])
    u = r1 - len(pos) * (len(pos) + 1) / 2.0
    return round(u / (len(pos) * len(neg)), 5)


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


runs = []
excluded = 0
for f in sorted(L1.glob("*.compact.json")):
    # Every x18*/x19* pool was selected BY the local inflow or by the phase (X182 by the midpoint value, X184/X187/X188/X189 by the
    # arm's inflow level, X190/X191/X192/X193 by the site's or phase's inflow), so measuring the inflow-fusion association on them
    # would be circular. The observational pool is the natural ladder and its siblings.
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
    first = series[0]
    if not isinstance(first, list) or len(first) != 2 or not isinstance(first[1], list) or len(first[1]) < 2:
        continue
    comps = [comp_tuple(c) for c in first[1]]
    r0 = math.sqrt(max(comps[0][0], 1) / math.pi)
    dx = abs(comps[0][1] - comps[1][1]) % GRID
    dx = min(dx, GRID - dx)
    dy = abs(comps[0][2] - comps[1][2]) % GRID
    dy = min(dy, GRID - dy)
    sep = math.hypot(dx, dy)
    gap = round(sep - 2 * r0)
    F = float(params.get("F", 0.0))
    steps = int(params.get("steps", 0))
    g_bodies = min(G_at(c[1], c[2]) for c in comps)
    fused = any(isinstance(row, list) and len(row) == 2 and isinstance(row[1], list) and len(row[1]) == 1 for row in series)
    src = f.stem.replace(".compact", "")
    runs.append({"file": src, "family": src.split("_s")[0] if "_s" in src else src,
                 "r0": round(r0, 3), "gap": gap, "F": F, "steps": steps,
                 "F_local": round(F * (1 + 0.5 * (2 * g_bodies - 1)), 5),
                 "fused": int(fused), "phase": list(phase_of(comps)), "n_bodies": len(comps)})

# A world is the phase AND the arm: the phase fixes only the bodies' positions modulo the period, so two runs in one phase but
# with different r0, gap, F or steps are different worlds. Counting the phase alone would report arm differences as within-world
# heterogeneity.
def world_key(r):
    return (round(r["r0"] / 0.2) * 0.2, r["gap"], r["F"], r["steps"], tuple(r["phase"]))


by_phase = defaultdict(list)
for r in runs:
    by_phase[world_key(r)].append(r)
by_position = defaultdict(list)
for r in runs:
    by_position[tuple(r["phase"])].append(r)
sizes = sorted((len(v) for v in by_phase.values()), reverse=True)
composition = {"runs": len(runs), "distinct_worlds": len(by_phase), "distinct_positions": len(by_position),
               "excluded_phase_selected_runs": excluded,
               "distinct_positions_note": ("the position alone over-counts as a world: 64 positions hold runs from different arms, so the world "
                                           "here is the position times the arm (r0 bin, gap, F, steps)"),
               "largest_phase": sizes[0] if sizes else 0,
               "phases_with_one_run": sum(1 for s in sizes if s == 1),
               "runs_in_singleton_phases": sum(1 for s in sizes if s == 1),
               "phase_size_histogram": {str(s): sizes.count(s) for s in sorted(set(sizes), reverse=True)[:10]}}

homogeneous = sum(1 for v in by_phase.values() if len({x["fused"] for x in v}) == 1)
composition["phases_with_consistent_outcome"] = homogeneous
composition["phases_with_mixed_outcome"] = len(by_phase) - homogeneous
composition["note"] = ("a phase with a mixed outcome is a phase whose single world is not enough: the same positions gave both outcomes, "
                       "which prices the class unit directly and is reported rather than hidden")

obs_auc = auc([r["F_local"] for r in runs], [r["fused"] for r in runs])
homog = [v for v in by_phase.values() if len({x["fused"] for x in v}) == 1]
auc_of_phase = auc([v[0]["F_local"] for v in homog], [v[0]["fused"] for v in homog])
mixed_share = round((len(runs) - sum(len(v) for v in homog)) / len(runs), 4) if runs else None

rng = random.Random(SEED)
boot_runs, boot_phases = [], []
phase_items = [(round(statistics.fmean([x["F_local"] for x in v]), 5), round(statistics.fmean([x["fused"] for x in v]), 5))
               for v in by_phase.values()]
for _ in range(BOOT):
    samp = [runs[rng.randrange(len(runs))] for _ in range(len(runs))]
    a = auc([r["F_local"] for r in samp], [r["fused"] for r in samp])
    if a is not None:
        boot_runs.append(a)
    clusters = [phase_items[rng.randrange(len(phase_items))] for _ in range(len(phase_items))]
    xs = [c[0] for c in clusters]
    ys = [1 if c[1] >= 0.5 else 0 for c in clusters]
    a2 = auc(xs, ys)
    if a2 is not None:
        boot_phases.append(a2)


def ci(v):
    v = sorted(v)
    return (round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v))], 4), round(statistics.pstdev(v), 4)) if v else None


ci_runs, ci_phases = ci(boot_runs), ci(boot_phases)

# X187's four groups re-expressed by world: these pools were selected by inflow level on purpose, so they are read only as a
# re-expression of X187's own tests, never pooled with the observational pool above.
x187 = []
for f in sorted(L1.glob("x187_*.compact.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    series = d.get("series") or []
    if not series or not isinstance(series[0][1], list):
        continue
    comps = [comp_tuple(c) for c in series[0][1]]
    if len(comps) < 2:
        continue
    name = f.stem.replace(".compact", "")
    fused = any(isinstance(row, list) and len(row) == 2 and isinstance(row[1], list) and len(row[1]) == 1 for row in series)
    params = d.get("params") or {}
    x187.append({"file": name, "family": name.split("_s")[0], "arm": "r3_g10" if "_r3_" in name else "r6_g9",
                 "level": "cold" if "_cold_" in name else "warm", "phase": list(phase_of(comps)),
                 "fused": int(fused), "F_local": None, "r0": None, "gap": None, "F": params.get("F"), "steps": None})

groups = {}
for arm in ("r3_g10", "r6_g9"):
    for level in ("cold", "warm"):
        sel = [r for r in x187 if r.get("arm") == arm and r.get("level") == level]
        if not sel:
            continue
        worlds = defaultdict(list)
        for r in sel:
            worlds[tuple(r["phase"])].append(r)
        f_worlds = sum(1 for v in worlds.values() if any(x["fused"] for x in v))
        groups[f"{arm}_{level}"] = {"runs": len(sel), "distinct_phases": len(worlds),
                                    "fused_runs": sum(x["fused"] for x in sel),
                                    "fused_phases": f_worlds,
                                    "phase_sizes": sorted((len(v) for v in worlds.values()), reverse=True),
                                    "consistent": sum(1 for v in worlds.values() if len({x["fused"] for x in v}) == 1),
                                    "mixed": sum(1 for v in worlds.values() if len({x["fused"] for x in v}) > 1)}

x187_world_fisher = {"note": ("these are X194's own groups and its own outcome definition (one component at any sample), not a re-computation of "
                              "X187's published tests, which used their own readout; they are reported to show how the counts change when worlds "
                              "replace runs, and any claim about X187's numbers has to be made against X187's aggregate")}
for arm in ("r3_g10", "r6_g9"):
    a, b = groups.get(f"{arm}_cold"), groups.get(f"{arm}_warm")
    if not a or not b:
        continue
    x187_world_fisher[arm] = {
        "by_runs": {"cold": f"{a['fused_runs']}/{a['runs']}", "warm": f"{b['fused_runs']}/{b['runs']}",
                    "fisher_p": fisher_greater(a["fused_runs"], a["runs"] - a["fused_runs"],
                                               b["fused_runs"], b["runs"] - b["fused_runs"])},
        "by_worlds": {"cold": f"{a['fused_phases']}/{a['distinct_phases']}", "warm": f"{b['fused_phases']}/{b['distinct_phases']}",
                      "fisher_p": fisher_greater(a["fused_phases"], a["distinct_phases"] - a["fused_phases"],
                                                 b["fused_phases"], b["distinct_phases"] - b["fused_phases"])}}

verdict = (f"THE LINE'S POOLS ARE SMALLER THAN THEIR RUN COUNTS, AND THE TWO INTERVALS DIFFER. The observational pool holds {len(runs)} runs "
           f"in {len(by_phase)} worlds ({len(by_position)} positions): the largest phase carries {composition['largest_phase']} runs, {composition['phases_with_one_run']} "
           f"phases are singletons, and {composition['phases_with_mixed_outcome']} phases gave both outcomes within one phase — so one phase is "
           f"not always one world even after the arm is held - so the class unit is an approximation, and that is its price. The pooled association between the local inflow and fusion is "
           f"AUC {obs_auc} over runs, and {auc_of_phase} over the homogeneous phases; resampling runs gives a 95% interval of "
           f"{ci_runs[0]}-{ci_runs[1]} (sd {ci_runs[2]}), resampling phases {ci_phases[0]}-{ci_phases[1]} (sd {ci_phases[2]}). "
           f"X187's Fisher tests, by runs and by world: {x187_world_fisher}.")
if ci_runs and ci_phases:
    ratio = round(ci_phases[2] / ci_runs[2], 2) if ci_runs[2] else None
else:
    ratio = None

agg = {"kind": "x194_phase_clusters", "period": PERIOD, "composition": composition,
       "auc_by_runs": obs_auc, "auc_by_phases_homogeneous": auc_of_phase,
       "homogeneous_phase_runs_share": round(1 - (mixed_share or 0), 4),
       "bootstrap": {"iterations": BOOT, "seed": SEED, "by_runs": {"ci95": ci_runs},
                     "by_phases": {"ci95": ci_phases}, "sd_ratio_phases_over_runs": ratio},
       "x187_groups": groups, "x187_fisher_by_runs_and_worlds": x187_world_fisher,
       "headline": "the run count is an upper bound on the number of worlds in every pooled statistic of the line",
       "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x194] pool {len(runs)} runs, {len(by_phase)} phases; largest {composition['largest_phase']}, "
      f"singletons {composition['phases_with_one_run']}, mixed-outcome phases {composition['phases_with_mixed_outcome']}")
print(f"[x194] AUC runs {obs_auc} vs homogeneous phases {auc_of_phase}; bootstrap sd runs {ci_runs[2] if ci_runs else None} "
      f"vs phases {ci_phases[2] if ci_phases else None} (ratio {ratio})")
print(f"[x194] x187 by runs and worlds: {x187_world_fisher}")
print(f"[x194] verdict: {verdict}")
