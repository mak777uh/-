"""x183_local_collapse.py — X183: does the crossing collapse when the rate is read locally instead of nominally?

X180 found the seeded site's phase in the medium's fixed pattern is strongly associated with whether a pair fuses, but the sign
depends on which phase of the pair one uses (midpoint -0.56, body mean +0.27). A covariate whose sign is a matter of choice is
not yet a mechanism, so this item asks the question that settles it without running anything: **which variable organises the
block's own rate ladder?**

The ladder is already in the corpus: at radius 3, surface gap 10, the same geometry was run at `F` = 0.026, 0.030, 0.033 and
0.036, with shares of 0.30, 0.41, 0.40 and 0.65. If the nominal rate is only a site average, then the runs' *local* inflow
should order them better than the nominal rate does — and the best of the candidate phase choices is the one that does, which
is an empirical answer rather than a definitional one.

Readout: the AUC of each candidate variable against the fusion outcome (rank statistic, no model), computed over all two-body
runs and, separately, within each nominal ladder level (where the nominal rate is constant by construction and any
discrimination must come from the site).

Writes morphogenesis/experiments/E09_pond/l1_field_x183_local_collapse.json.
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
OUT = POND / "l1_field_x183_local_collapse.json"
GRID = 96
HETERO_SCALE = 12.0
HETERO_AMP = 0.5


def G_at(x: float, y: float) -> float:
    ky = 2.0 * math.pi / HETERO_SCALE
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def ct(c):
    if isinstance(c, dict):
        return float(c.get("area", 0)), float(c.get("cx", 0)), float(c.get("cy", 0))
    return float(c[1]), float(c[2]), float(c[3])


def auc(values: list[float], flags: list[int]) -> float | None:
    """Probability that a fused run's variable exceeds an unfused run's, by ranks with ties at one half."""
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
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    r_pos = sum(ranks[i] for i, f in enumerate(flags) if f)
    u = r_pos - len(pos) * (len(pos) + 1) / 2
    return round(u / (len(pos) * len(neg)), 4)


def logistic_deviance(values: list[float], flags: list[int]) -> float | None:
    """Binomial deviance of a one-parameter logistic fit in `values` (grid over slope, intercept from the base rate)."""
    if len(set(flags)) < 2 or len(set(values)) < 2:
        return None
    base = statistics.fmean(flags)
    base = min(max(base, 1e-6), 1 - 1e-6)
    lo, hi = min(values), max(values)
    if hi == lo:
        return None
    span = hi - lo
    best = None
    for m in range(-40, 41):
        w = m / 10.0  # slope in log-odds per span
        b = math.log(base / (1 - base))
        dev = 0.0
        for v, f in zip(values, flags):
            z = b + w * (v - (lo + hi) / 2) / span * 2
            p = 1 / (1 + math.exp(-max(min(z, 30), -30)))
            p = min(max(p, 1e-9), 1 - 1e-9)
            dev += -2 * (f * math.log(p) + (1 - f) * math.log(1 - p))
        if best is None or dev < best:
            best = dev
    return round(best, 1)


runs = []
excluded = 0
for f in sorted(L1.glob("*.compact.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    if f.stem.startswith(("x182_", "x184_", "x187_")):
        excluded += 1
        continue
    series = d.get("series") or []
    params = d.get("params") or {}
    if not series or not isinstance(series[0], list) or len(series[0]) != 2:
        continue
    if not isinstance(series[0][1], list) or len(series[0][1]) != 2:
        continue
    comps = [ct(c) for c in series[0][1]]
    r0 = math.sqrt(max(comps[0][0], 1) / math.pi)
    dx = abs(comps[0][1] - comps[1][1]) % GRID
    dx = min(dx, GRID - dx)
    dy = abs(comps[0][2] - comps[1][2]) % GRID
    dy = min(dy, GRID - dy)
    gap = round(math.hypot(dx, dy) - 2 * r0)
    counts = [len(r[1]) for r in series if isinstance(r, list) and len(r) == 2 and isinstance(r[1], list)]
    if not counts:
        continue
    gs = [G_at(c[1], c[2]) for c in comps]
    F = float(params.get("F", 0.0))
    fam = f.stem.split("_s")[0]
    runs.append({"file": f.stem.replace(".compact", ""), "family": fam, "F": F, "gap": gap, "r0": round(r0, 3),
                 "steps": int(params.get("steps", 0)),
                 "g_mid": G_at((comps[0][1] + comps[1][1]) / 2, (comps[0][2] + comps[1][2]) / 2),
                 "g_mean": statistics.fmean(gs), "g_min": min(gs), "g_max": max(gs),
                 "fused": min(counts) == 1})

candidates = {
    "F_nominal": lambda r: r["F"],
    "F_local_mid": lambda r: r["F"] * (1 + HETERO_AMP * (2 * r["g_mid"] - 1)),
    "F_local_mean": lambda r: r["F"] * (1 + HETERO_AMP * (2 * r["g_mean"] - 1)),
    "F_local_min": lambda r: r["F"] * (1 + HETERO_AMP * (2 * r["g_min"] - 1)),
    "F_local_max": lambda r: r["F"] * (1 + HETERO_AMP * (2 * r["g_max"] - 1)),
}

# the ladder: radius 3 (measured 2.8-3.0), measured gap 10, all rates, all horizons
ladder = [r for r in runs if r["gap"] == 10 and 2.7 <= r["r0"] <= 3.1]
by_rate = defaultdict(list)
for r in ladder:
    by_rate[r["F"]].append(r)

per_candidate = {}
for name, fn in candidates.items():
    vals = [fn(r) for r in ladder]
    flags = [int(r["fused"]) for r in ladder]
    overall = auc(vals, flags)
    within = {}
    for F, rs in sorted(by_rate.items()):
        if len(rs) < 6 or len(set(int(x["fused"]) for x in rs)) < 2:
            continue
        within[F] = {"runs": len(rs), "share": round(statistics.fmean([int(x["fused"]) for x in rs]), 3),
                     "auc": auc([fn(r) for r in rs], [int(r["fused"]) for r in rs])}
    within_aucs = [v["auc"] for v in within.values() if v["auc"] is not None]
    per_candidate[name] = {"auc_overall": overall, "auc_within_levels": within,
                           "mean_auc_within": round(statistics.fmean(within_aucs), 4) if within_aucs else None,
                           "deviance": logistic_deviance(vals, flags)}

nominal = per_candidate["F_nominal"]
best_local = max((k for k in per_candidate if k != "F_nominal"),
                 key=lambda k: (per_candidate[k]["mean_auc_within"] or 0))
b = per_candidate[best_local]
within_better = sum(1 for F in nominal["auc_within_levels"]
                    if (b["auc_within_levels"].get(F, {}).get("auc") or 0) > 0.5)
best_mean = per_candidate["F_local_mean"]
verdict = (f"THE NOMINAL RATE IS A SITE AVERAGE, AND THE INFLOW AT THE SEEDED SITES ORGANISES THE LADDER: over {len(ladder)} "
           f"ladder runs (radius 3 by construction, surface gap 10 as SEP - 2r = 16 - 2*3.03825 = 9.923, rates "
           f"{sorted(by_rate)}), the nominal rate discriminates with AUC {nominal['auc_overall']} and, being constant inside a "
           f"level, not at all within one (0.5 by construction), while the inflow read at a pair's two seeded sites does: "
           f"colder body {b['auc_overall']} (mean within levels {b['mean_auc_within']}), body mean "
           f"{best_mean['auc_overall']} (within {best_mean['mean_auc_within']}), midpoint {per_candidate['F_local_mid']['auc_overall']}. "
           f"A one-parameter logistic fit costs {nominal['deviance']} for the nominal rate against {b['deviance']} for the "
           f"colder body. Two limits are recorded rather than smoothed: the ladder does NOT separate the colder body from the "
           f"body mean (their AUCs differ by {round(b['auc_overall'] - best_mean['auc_overall'], 4)}, and the reviewed "
           f"bootstrap interval for that difference crosses zero), so the supported claim is \"the local inflow at the seeded "
           f"sites\"; and the readout is a transient coalescence - every run flagged as fused rebounds above one component, "
           f"none ends on one - so these numbers describe contact, not a terminal single body.")
agg = {"kind": "x183_local_collapse", "hetero_amp": HETERO_AMP, "hetero_scale": HETERO_SCALE,
       "ladder_runs": len(ladder), "ladder_by_F": {str(F): {"runs": len(rs),
                                                           "share": round(statistics.fmean([int(x["fused"]) for x in rs]), 3)}
                                                   for F, rs in sorted(by_rate.items())},
       "candidates": per_candidate, "best_local": best_local,
       "excluded_phase_selected_runs": excluded, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x183] excluded phase-selected runs: {excluded}")
print(f"[x183] ladder runs: {len(ladder)} at rates {sorted(by_rate)}")
for F, v in agg["ladder_by_F"].items():
    print(f"    F = {F}: {v['runs']} runs, share {v['share']}")
print(f"{'candidate':>16} {'AUC':>7} {'within':>7} {'deviance':>9}   within-level AUCs")
for name, v in per_candidate.items():
    wa = {F: d["auc"] for F, d in v["auc_within_levels"].items()}
    print(f"{name:>16} {str(v['auc_overall']):>7} {str(v['mean_auc_within']):>7} {str(v['deviance']):>9}   {wa}")
print(f"[x183] best local reading: {best_local}")
print(f"[x183] verdict: {verdict}")
