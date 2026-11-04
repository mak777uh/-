"""Independent evaluation of the X184 cold-body series, read from the raw runs on disk.

The X184 aggregate does not exist yet; these 30 raw runs (x184_F0??_s????.json) were written by
scripts/x184_cold_body.py at ~19:20, after this review started, and are untracked.  Nothing is
imported from scripts/x184*.py; the readout and the trend test are re-derived here.

Run from the repository root:  python lab/reviews/_scratch_x184_check.py
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
Z = 1.959963984540054


def G_at(x, y):
    ky = 2.0 * math.pi / SCALE
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def auc(vals, flags):
    pos = [v for v, f in zip(vals, flags) if f]
    neg = [v for v, f in zip(vals, flags) if not f]
    if not pos or not neg:
        return None
    s = 0.0
    for a in pos:
        for b in neg:
            s += 1.0 if a > b else (0.5 if a == b else 0.0)
    return s / (len(pos) * len(neg))


def cochran_armitage(xs, ns, rs):
    """One-sided p for a positive linear trend in success proportion over ordered scores."""
    X = sum(n * x for n, x in zip(ns, xs))
    N = sum(ns)
    R = sum(rs)
    p = R / N
    T = sum(x * (r - n * p) for x, n, r in zip(xs, ns, rs))
    var = p * (1 - p) * (sum(n * x * x for n, x in zip(ns, xs)) - X * X / N)
    if var <= 0:
        return None
    z = T / math.sqrt(var)
    return z, 0.5 * math.erfc(z / math.sqrt(2))


runs = []
for f in sorted(L1.glob("x184_F*_s*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    series = d.get("series") or []
    params = d.get("params") or {}
    counts = [len(r.get("components_log") or []) for r in series]
    row0 = series[0]["components_log"]
    cs = sorted(row0, key=lambda c: c.get("cx", 0))
    gs = [G_at(c["cx"], c["cy"]) for c in cs]
    g_mean = statistics.fmean(gs)
    g_mid = G_at((cs[0]["cx"] + cs[1]["cx"]) / 2.0, (cs[0]["cy"] + cs[1]["cy"]) / 2.0)
    area = [c["area"] for c in cs]
    r0 = math.sqrt(area[0] / math.pi)
    dx = abs(cs[0]["cx"] - cs[1]["cx"]) % GRID
    gap = round(math.hypot(dx, abs(cs[0]["cy"] - cs[1]["cy"]) % GRID) - 2 * r0)
    g_cold = min(gs)
    f_local = float(params["F"]) * (1 + 0.5 * (2 * g_cold - 1))
    first_one = counts.index(1) if 1 in counts else None
    runs.append({
        "file": f.name, "level_tag": f.name.split("_s")[0].replace("x184_", ""),
        "seed": int(params["seed"]), "F": float(params["F"]),
        "g_cold": g_cold, "f_local": f_local, "g_mean": g_mean, "g_mid": g_mid, "g_max": max(gs),
        "r0": r0, "gap": gap, "areas": area,
        "fused": min(counts) == 1,
        "last": counts[-1], "min": min(counts),
        "rebound": (first_one is not None and any(c > 1 for c in counts[first_one:])),
        "first": counts[0], "nsamp": len(counts),
    })

print(f"x184 raw runs read: {len(runs)}; F values {sorted(set(r['F'] for r in runs))}")
print(f"first-sample counts {sorted(set(r['first'] for r in runs))}; gap {sorted(set(r['gap'] for r in runs))}; "
      f"r0 {sorted(set(round(r['r0'],4) for r in runs))}; areas {sorted(set(tuple(r['areas']) for r in runs))}")
print(f"fused: {sum(1 for r in runs if r['fused'])}/{len(runs)}; "
      f"of them rebound above 1: {sum(1 for r in runs if r['fused'] and r['rebound'])}")
print(f"smallest observed F_local at the colder body: {min(r['f_local'] for r in runs):.5f}; "
      f"largest: {max(r['f_local'] for r in runs):.5f}")

by_level = defaultdict(list)
for r in runs:
    by_level[r["level_tag"]].append(r)
order = sorted(by_level, key=lambda k: statistics.fmean(r["f_local"] for r in by_level[k]))
print("\nlevel | n | fused | share | Wilson | mean F_local(cold) [range]")
xs, ns, rs = [], [], []
for tag in order:
    rs_ = by_level[tag]
    fl = [r["f_local"] for r in rs_]
    k = sum(1 for r in rs_ if r["fused"])
    w = wilson(k, len(rs_))
    x = statistics.fmean(fl)
    xs.append(x)
    ns.append(len(rs_))
    rs.append(k)
    print(f"  {tag:>5} | {len(rs_)} | {k:>5} | {k/len(rs_):.3f} | [{w[0]:.4f},{w[1]:.4f}] | {x:.5f} [{min(fl):.5f},{max(fl):.5f}]")

res = cochran_armitage(xs, ns, rs)
print(f"\nCochran-Armitage over the level means (ordered by F_local): z={res[0]:+.4f}  one-sided p={res[1]:.4f}")
res2 = cochran_armitage([r["f_local"] for r in runs], [1] * len(runs), [int(r["fused"]) for r in runs])
print(f"Cochran-Armitage run-level (n=1 per run): z={res2[0]:+.4f}  one-sided p={res2[1]:.4f}")
print(f"AUC of F_local(cold) against fusion over all {len(runs)} runs = "
      f"{auc([r['f_local'] for r in runs], [int(r['fused']) for r in runs]):.4f}")

flags = [int(r["fused"]) for r in runs]
print("\nalternative phase readings on the same 30 runs (AUC vs fusion):")
for key, lab in (("g_mean", "body mean G"), ("g_mid", "midpoint G"), ("g_max", "warmer body G"),
                 ("g_cold", "colder body G")):
    print(f"  {lab:>14}: AUC={auc([r[key] for r in runs], flags):.4f}  "
          f"range [{min(r[key] for r in runs):.4f},{max(r[key] for r in runs):.4f}]  "
          f"sd {statistics.pstdev([r[key] for r in runs]):.4f}")
print("  per-level means of each reading:")
for tag in order:
    rs_ = by_level[tag]
    print(f"    {tag:>5}: g_cold {statistics.fmean(r['g_cold'] for r in rs_):.4f}  "
          f"g_mean {statistics.fmean(r['g_mean'] for r in rs_):.4f}  "
          f"g_mid {statistics.fmean(r['g_mid'] for r in rs_):.4f}  "
          f"g_max {statistics.fmean(r['g_max'] for r in rs_):.4f}")
print("\nper-seed:")
for r in sorted(runs, key=lambda r: (r["f_local"])):
    print(f"  {r['file']:>24} seed {r['seed']:>5} F_local {r['f_local']:.5f} g_cold {r['g_cold']:.4f} "
          f"fused={int(r['fused'])} min={r['min']} last={r['last']}")
