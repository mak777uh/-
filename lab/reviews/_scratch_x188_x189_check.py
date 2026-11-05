"""Recheck of X188 (continuation-based nucleation count) and X189 (bridge), commit e2fe8cb5.

Own reader / own field maths, nothing imported.  Run from the repo root:
  python lab/reviews/_scratch_x188_x189_check.py
"""
from __future__ import annotations

import json
import math
import statistics
from collections import Counter
from pathlib import Path

import numpy as np

L1 = Path("morphogenesis/experiments/L1_field")
FIELDS = Path("_hourly/x189_fields")
GRID = 96
SCALE = 12.0
AMP = 0.5


def G_at(x, y):
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


def step_of(row):
    return int(row[0]) if isinstance(row, list) else int(row.get("step"))


def wrap_delta(a, b):
    return (a - b + GRID / 2) % GRID - GRID / 2


def dist(p, q):
    return math.hypot(wrap_delta(p[0], q[0]), wrap_delta(p[1], q[1]))


def x187_runs():
    index = json.loads((L1 / "x187_series_index.json").read_text(encoding="utf-8"))
    out = []
    for r in index["runs"]:
        if r["status"] not in ("ok", "skipped (exists)"):
            continue
        tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
        d = json.loads((L1 / f"x187_{tag}.compact.json").read_text(encoding="utf-8"))
        series = d.get("series") or []
        if len(comps(series[0])) != 2:
            continue
        out.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"], "series": series,
                    "flow": float(index["flow"])})
    return out


def track(series, match_cells, near_cells, window_cells, frame):
    """frame: 'current' (pair mean of tracked) or 'initial' (first-sample midpoint)."""
    first = comps(series[0])
    tracked = [cxy(c) for c in first[:2]]
    initial_mid = (statistics.fmean([p[0] for p in tracked]), statistics.fmean([p[1] for p in tracked]))
    out = []
    for row in series:
        cs = comps(row)
        if not cs:
            out.append({"step": step_of(row), "others": 0, "others_window": 0, "n_tracked": len(tracked)})
            continue
        cands = [c for c in cs if any(dist(cxy(c), t) <= match_cells for t in tracked)]
        if not cands:
            cands = [min(cs, key=lambda c: min(dist(cxy(c), t) for t in tracked))]
        tracked = [cxy(c) for c in cands]
        tids = {id(c) for c in cands}
        centre = (statistics.fmean([p[0] for p in tracked]), statistics.fmean([p[1] for p in tracked])) if frame == "current" else initial_mid
        others = [c for c in cs if id(c) not in tids and all(dist(cxy(c), t) > near_cells for t in tracked)]
        inw = [c for c in others if dist(cxy(c), centre) <= window_cells / 2]
        out.append({"step": step_of(row), "others": len(others), "others_window": len(inw), "n_tracked": len(tracked)})
    return out


def x188(match_cells=4.0, near_cells=3.0, window_cells=24.0, frame="current", fixed_every=50):
    rows = []
    for r in x187_runs():
        series = r["series"]
        cs0 = comps(series[0])
        gc = min(G_at(*cxy(c)) for c in cs0)
        counts = [len(comps(x)) for x in series]
        tr = track(series, match_cells, near_cells, window_cells, frame)
        fixed = [x for x in tr if x["step"] % fixed_every == 0 and x["step"] > 0]
        rows.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"],
                     "f_local": round(r["flow"] * (1 + AMP * (2 * gc - 1)), 5),
                     "fused": int(min(counts) == 1),
                     "mean_window": round(statistics.fmean([x["others_window"] for x in fixed]), 3),
                     "mean_field": round(statistics.fmean([x["others"] for x in fixed]), 3),
                     "max_tracked": max(x["n_tracked"] for x in tr),
                     "max_tracked_fixed": max(x["n_tracked"] for x in fixed),
                     "fixed_n": len(fixed)})
    g = {}
    for arm in ("r6_g9", "r3_g10"):
        for lvl in ("cold", "warm"):
            sel = [x for x in rows if x["arm"] == arm and x["level"] == lvl]
            g[f"{arm}_{lvl}"] = (round(statistics.fmean([x["mean_window"] for x in sel]), 3),
                                 round(statistics.fmean([x["mean_field"] for x in sel]), 3),
                                 sum(x["fused"] for x in sel), len(sel))
    return rows, g


print("=== X188")
rows, g = x188()
for k, v in g.items():
    print(f"  {k:>12}: others-window {v[0]}  field {v[1]}  fused {v[2]}/{v[3]}")
d6 = round(g["r6_g9_warm"][0] - g["r6_g9_cold"][0], 3)
d3 = round(g["r3_g10_warm"][0] - g["r3_g10_cold"][0], 3)
print(f"  warm-minus-cold window: radius6 {d6:+g} (bar 0.5), radius3 {d3:+g}")
print(f"  fixed samples per run {rows[0]['fixed_n']}; per-run means {[x['mean_window'] for x in rows]}")
print(f"  positivity: positive runs {sum(1 for x in rows if x['mean_window'] > 0)}/{len(rows)}; "
      f"fused {sum(x['fused'] for x in rows)}")

vals = [x["mean_window"] for x in rows]
fus = [x["fused"] for x in rows]
m1 = statistics.fmean([v for v, f in zip(vals, fus) if f])
m0 = statistics.fmean([v for v, f in zip(vals, fus) if not f])
sd = statistics.pstdev(vals)
p = statistics.fmean(fus)
print(f"  mean window fused {m1:.3f} vs unfused {m0:.3f}; point-biserial {(m1 - m0) / sd * math.sqrt(p * (1 - p)):+.3f}")
print(f"  max tracked-set size over all samples: {max(x['max_tracked'] for x in rows)} "
      f"(over fixed samples {max(x['max_tracked_fixed'] for x in rows)})")
for lbl, kw in (("match 2", dict(match_cells=2.0)), ("match 6", dict(match_cells=6.0)),
                ("match 8", dict(match_cells=8.0)), ("initial frame", dict(frame="initial")),
                ("window 32", dict(window_cells=32.0)), ("every 25", dict(fixed_every=25))):
    _, gg = x188(**kw)
    print(f"  sensitivity {lbl:>13}: r6 {gg['r6_g9_warm'][0] - gg['r6_g9_cold'][0]:+.3f}  "
          f"r3 {gg['r3_g10_warm'][0] - gg['r3_g10_cold'][0]:+.3f}")

# ---------------------------------------------------------------- X189
print("\n=== X189")
index = json.loads((L1 / "x189_series_index.json").read_text(encoding="utf-8"))
xruns = []
for r in index["runs"]:
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    d = json.loads((L1 / f"x189_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    cs0 = comps(series[0])
    gc = min(G_at(*cxy(c)) for c in cs0)
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    xruns.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"], "tag": tag, "series": series,
                  "g_cold": round(gc, 4), "fused": int(min(counts) == 1), "by_step": by_step,
                  "f_local": round(float(index["flow"]) * (1 + AMP * (2 * gc - 1)), 5)})


def peak(field, centre, r):
    cx, cy = centre
    best = 0.0
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                best = max(best, float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID]))
    return best


def bridge(field, c0, c1, n=200):
    dx = wrap_delta(c1[0], c0[0])
    dy = c1[1] - c0[1]
    seg = [float(field[int(round(c0[1] + dy * (i / n))) % GRID, int(round(c0[0] + dx * (i / n))) % GRID]) for i in range(n + 1)]
    mid = seg[len(seg) // 2]
    central = seg[int(0.25 * len(seg)):int(0.75 * len(seg)) + 1]
    return mid, min(central)


for x in xruns:
    per = []
    for sp in sorted(FIELDS.glob(f"{x['tag']}/*.npy")):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = x["by_step"].get(step)
        rec = {"step": step}
        if cur and len(cur) == 2:
            c0, c1 = cur
            pk = max(peak(field, c0, 10), peak(field, c1, 10))
            mid, cmin = bridge(field, c0, c1)
            rec.update({"peak": pk, "ratio": round(mid / pk, 5) if pk > 0 else None,
                        "ratio_min": round(cmin / pk, 5) if pk > 0 else None,
                        "pk3": max(peak(field, c0, 3), peak(field, c1, 3))})
            # drift test: distance from the seeded centre to the current centre
            rec["drift0"] = round(dist(c0, cxy(comps(x['series'][0])[0])), 2)
        per.append(rec)
    ok = [r for r in per if r.get("ratio") is not None and r.get("peak", 0) >= 0.3]
    tight = min(ok, key=lambda r: r["ratio"]) if ok else None
    contact = max(ok, key=lambda r: r["step"]) if ok else None
    x["per"] = per
    x["ratio_tightest"] = tight["ratio"] if tight else None
    x["tightest_step"] = tight["step"] if tight else None
    x["ratio_tightest_min"] = tight["ratio_min"] if tight else None
    x["ratio_contact"] = contact["ratio"] if contact else None
    x["contact_step"] = contact["step"] if contact else None
    x["pk3_max"] = max((r.get("pk3") or 0) for r in per)

print(f"  peak over radius 3 (all runs/slices) max {max(x['pk3_max'] for x in xruns):.3f}; "
      f"over radius 10 {max((r.get('peak') or 0) for x in xruns for r in x['per']):.3f}")
for arm in ("r6_g9", "r3_g10"):
    for lvl in ("cold", "warm"):
        sel = [x for x in xruns if x["arm"] == arm and x["level"] == lvl]
        print(f"  {arm} {lvl:>4}: sites {sorted(set(x['g_cold'] for x in sel))} "
              f"tightest_mean {round(statistics.fmean([x['ratio_tightest'] for x in sel]),5)} "
              f"{[x['ratio_tightest'] for x in sel]}@{[x['tightest_step'] for x in sel]} "
              f"meancentral {round(statistics.fmean([x['ratio_tightest_min'] for x in sel]),5)} "
              f"contact_mean {round(statistics.fmean([x['ratio_contact'] for x in sel]),5)} "
              f"{[x['ratio_contact'] for x in sel]}@{[x['contact_step'] for x in sel]}")

r6c = [x for x in xruns if x["arm"] == "r6_g9" and x["level"] == "cold"]
r6w = [x for x in xruns if x["arm"] == "r6_g9" and x["level"] == "warm"]
r3c = [x for x in xruns if x["arm"] == "r3_g10" and x["level"] == "cold"]
r3w = [x for x in xruns if x["arm"] == "r3_g10" and x["level"] == "warm"]


def dm(a, b, key):
    return round(statistics.fmean([x[key] for x in b]) - statistics.fmean([x[key] for x in a]), 5)


print(f"  contact warm-minus-cold: r6 {dm(r6c, r6w, 'ratio_contact'):+g}  r3 {dm(r3c, r3w, 'ratio_contact'):+g}  (bar -0.05)")
print(f"  tightest warm-minus-cold: r6 {dm(r6c, r6w, 'ratio_tightest'):+g}  r3 {dm(r3c, r3w, 'ratio_tightest'):+g}")
print(f"  min-central warm-minus-cold: r6 {dm(r6c, r6w, 'ratio_tightest_min'):+g}  r3 {dm(r3c, r3w, 'ratio_tightest_min'):+g}")
r6w_drop = sorted([x["ratio_contact"] for x in r6w])[1:]
print(f"  r6 warm contact values {sorted(x['ratio_contact'] for x in r6w)}; drop lowest -> "
      f"{round(statistics.fmean(r6w_drop) - statistics.fmean([x['ratio_contact'] for x in r6c]), 5):+g}")

# do the bodies actually drift? distance from the series[0] centre to the current centre at each slice
drifts = []
for x in xruns:
    per = {r["step"]: r for r in x["per"]}
    for st in (40, 100, 300):
        if st in per and "drift0" in per[st]:
            drifts.append(per[st]["drift0"])
print(f"  body-centre displacement from series[0]: min {min(drifts)} max {max(drifts)} median {statistics.median(drifts)} cells")

# radial profile around one body's current centre at step 40 (ring vs hollow)
x = xruns[0]
sp = sorted(FIELDS.glob(f"{x['tag']}/*_t40.npy"))[0]
field = np.load(sp)
c0, c1 = x["by_step"][40]
prof = []
for r in range(0, 13):
    vals = [float(field[int(round(c0[1] + dy)) % GRID, int(round(c0[0] + dx)) % GRID])
            for dy in range(-r, r + 1) for dx in range(-r, r + 1) if abs(math.hypot(dx, dy) - r) < 0.5]
    prof.append(round(statistics.fmean(vals), 4))
print(f"  radial mean v around a body centre at step 40 (r=0..12): {prof}")

# correlation among the three readings
cs = [x["ratio_contact"] for x in xruns]
ts = [x["ratio_tightest"] for x in xruns]
ms = [x["ratio_tightest_min"] for x in xruns]


def corr(a, b):
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    sa = math.sqrt(sum((v - ma) ** 2 for v in a))
    sb = math.sqrt(sum((v - mb) ** 2 for v in b))
    return sum((u - ma) * (v - mb) for u, v in zip(a, b)) / (sa * sb)


print(f"  Pearson r: contact vs tightest {corr(cs, ts):+.3f}; tightest vs min-central {corr(ts, ms):+.3f}; contact vs min-central {corr(cs, ms):+.3f}")
print(f"  tightest step counts {Counter(x['tightest_step'] for x in xruns)}; contact steps {[x['contact_step'] for x in xruns]}")
