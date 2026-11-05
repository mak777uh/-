"""Recheck of X186 (table in the local inflow) and X187 (nucleation), commit 2c82b4f8/b5b9590c.

Own reader, no script imported.  Run from the repo root:
  python lab/reviews/_scratch_x186_x187_check.py
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

L1 = Path("morphogenesis/experiments/L1_field")
POND = Path("morphogenesis/experiments/E09_pond")
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


def xy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def area_of(c):
    return float(c["area"]) if isinstance(c, dict) else float(c[1])


def sep_cells(a, b):
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


def f_local(F, g):
    return F * (1.0 + AMP * (2.0 * g - 1.0))


# ---------------------------------------------------------------- X186
def load_x186():
    runs, excl = [], 0
    for f in sorted(L1.glob("*.compact.json")):
        if f.stem.startswith(("x182_", "x184_", "x187_")):
            excl += 1
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        series = d.get("series") or []
        params = d.get("params") or {}
        first = comps(series[0]) if series else []
        if len(first) != 2:
            continue
        counts = [len(comps(r)) for r in series]
        (x0, y0), (x1, y1) = xy(first[0]), xy(first[1])
        dx = abs(x0 - x1) % GRID
        dx = min(dx, GRID - dx)
        dy = abs(y0 - y1) % GRID
        dy = min(dy, GRID - dy)
        r0 = math.sqrt(max(area_of(first[0]), 1) / math.pi)
        gs = [G_at(x0, y0), G_at(x1, y1)]
        F = float(params.get("F", 0.0))
        runs.append({"file": f.stem.replace(".compact", ""), "F": F, "radius": round(r0, 3),
                     "gap": round(math.hypot(dx, dy) - 2 * r0), "steps": int(params.get("steps", 0)),
                     "fused": int(min(counts) == 1), "f_local_cold": f_local(F, min(gs)),
                     "f_local_mean": f_local(F, statistics.fmean(gs)),
                     "cell": (round(r0, 1), round(math.hypot(dx, dy) - 2 * r0), round(F, 3))})
    return runs, excl


def dev_grid(rows, key):
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


def dev_mle2(rows, key, iters=400):
    vals = [math.log(key(r)) for r in rows]
    flags = [r["fused"] for r in rows]
    mv, sd = statistics.fmean(vals), statistics.pstdev(vals) or 1.0
    x = [(v - mv) / sd for v in vals]
    b0 = math.log(min(max(statistics.fmean(flags), 1e-6), 1 - 1e-6) / (1 - min(max(statistics.fmean(flags), 1e-6), 1 - 1e-6)))
    b1 = 0.0
    for _ in range(iters):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for xi, fi in zip(x, flags):
            z = max(min(b0 + b1 * xi, 35.0), -35.0)
            p = 1 / (1 + math.exp(-z))
            w = max(p * (1 - p), 1e-9)
            r = fi - p
            g0 += r
            g1 += r * xi
            h00 += w
            h01 += w * xi
            h11 += w * xi * xi
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-12:
            break
        d0 = (h11 * g0 - h01 * g1) / det
        d1 = (-h01 * g0 + h00 * g1) / det
        b0 += d0
        b1 += d1
        if abs(d0) < 1e-12 and abs(d1) < 1e-12:
            break
    dev = 0.0
    for xi, fi in zip(x, flags):
        p = min(max(1 / (1 + math.exp(-max(min(b0 + b1 * xi, 35.0), -35.0))), 1e-12), 1 - 1e-12)
        dev += -2 * (fi * math.log(p) + (1 - fi) * math.log(1 - p))
    return round(dev, 1)


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


runs, excl = load_x186()
cells = defaultdict(list)
for r in runs:
    cells[r["cell"]].append(r)
usable = {k: v for k, v in cells.items() if len(v) >= 5 and len({x["fused"] for x in v}) == 2}
mixed = [r for r in runs if 0 < statistics.fmean(x["fused"] for x in cells[r["cell"]]) < 1]

print("=== X186")
print(f"excluded by name {excl}; runs {len(runs)}; cells {len(cells)}; usable {len(usable)}; mixed {len(mixed)}")
dn, dc, dm = dev_grid(mixed, lambda r: r["F"]), dev_grid(mixed, lambda r: r["f_local_cold"]), dev_grid(mixed, lambda r: r["f_local_mean"])
print(f"deviance grid (their model): nominal {dn} cold {dc} mean {dm} drop {round(dn - dc, 1) if dn and dc else None}")
dn2, dc2, dm2 = dev_mle2(mixed, lambda r: r["F"]), dev_mle2(mixed, lambda r: r["f_local_cold"]), dev_mle2(mixed, lambda r: r["f_local_mean"])
print(f"deviance free 2-param MLE:  nominal {dn2} cold {dc2} mean {dm2} drop {round(dn2 - dc2, 1)}")

per_cell = []
for key, rs in sorted(usable.items()):
    per_cell.append({"cell": key, "runs": len(rs), "share": round(statistics.fmean(x["fused"] for x in rs), 4),
                     "slope": slope(rs, lambda r: r["f_local_cold"]),
                     "spread": round(statistics.pstdev([x["f_local_cold"] for x in rs]), 5)})
print(f"usable cells {len(per_cell)}; positive {sum(1 for c in per_cell if (c['slope'] or 0) > 0)}; negative {sum(1 for c in per_cell if (c['slope'] or 0) < 0)}")
for c in per_cell:
    print(f"  r{c['cell'][0]:>3} g{c['cell'][1]:>2} F{c['cell'][2]}: n {c['runs']:>2} share {c['share']:<6} slope {c['slope']:<7} spread {c['spread']}")

r6 = [r for r in runs if 5.8 <= r["radius"] <= 6.1]
for g in (9, 10):
    arm = [r for r in r6 if r["gap"] == g]
    print(f"  cliff gap{g}: runs {len(arm)} fused {sum(x['fused'] for x in arm)} radius {round(statistics.fmean([x['radius'] for x in arm]),3)} "
          f"f_local_cold_mean {round(statistics.fmean([x['f_local_cold'] for x in arm]),5)}")
a9 = [r for r in r6 if r["gap"] == 9]
a10 = [r for r in r6 if r["gap"] == 10]
print(f"  mean inflow difference {round(abs(statistics.fmean([x['f_local_cold'] for x in a9]) - statistics.fmean([x['f_local_cold'] for x in a10])),5)} (bar 0.004)")

# ---------------------------------------------------------------- X187
print("\n=== X187")
index = json.loads((L1 / "x187_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
rows = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    d = json.loads((L1 / f"x187_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    seeds = [xy(c) for c in cs0]
    mid = (statistics.fmean([p[0] for p in seeds]), statistics.fmean([p[1] for p in seeds]))
    g_cold = min(G_at(*p) for p in seeds)
    counts = [len(comps(x)) for x in series]
    k_min = min(counts)
    i_min = counts.index(k_min)
    row_min = series[i_min]
    extra = [c for c in comps(row_min) if all(sep_cells(xy(c), s) > 3.0 for s in seeds)]
    near = [c for c in extra if sep_cells(xy(c), mid) <= 8.0]
    rows.append({"arm": r["arm"], "level": r["level"], "seed": r["seed"], "f_local_cold": round(f_local(F, g_cold), 5),
                 "fused": int(k_min == 1), "min_count": k_min, "extra": len(extra), "extra_near": len(near),
                 "min_at_first": int(i_min == 0), "share_one": round(sum(1 for c in counts if c == 1) / len(counts), 6),
                 "samples": len(counts)})
ident = sum(1 for x in rows if x["extra_near"] == x["min_count"] - 1)
tracks = sum(1 for x in rows if x["extra_near"] == (1 if x["fused"] else 0))
print(f"runs {len(rows)}; min-count-is-one {sum(1 for x in rows if x['fused'])}; identity extra==min-1 {ident}/{len(rows)}; tracks outcome {tracks}/{len(rows)}")
for arm in ("r6_g9", "r3_g10"):
    for lvl in ("cold", "warm"):
        sel = [x for x in rows if x["arm"] == arm and x["level"] == lvl]
        print(f"  {arm} {lvl:>4}: n {len(sel)} fused {sum(x['fused'] for x in sel)} share {sum(x['fused'] for x in sel)/len(sel):.4f} "
              f"wilson {wilson(sum(x['fused'] for x in sel), len(sel))} f_local {round(statistics.fmean([x['f_local_cold'] for x in sel]),5)} "
              f"share_one_mean {statistics.fmean([x['share_one'] for x in sel]):.6f} max_run_share_one {max(x['share_one'] for x in sel):.6f}")
allsh = [x["share_one"] for x in rows]
print(f"  max share-of-samples-at-one over all 24 runs: {max(allsh):.6f}; any >= 0.01: {sum(1 for v in allsh if v >= 0.01)}")
for arm in ("r6_g9", "r3_g10"):
    c = [x for x in rows if x["arm"] == arm and x["level"] == "cold"]
    w = [x for x in rows if x["arm"] == arm and x["level"] == "warm"]
    print(f"  {arm}: d_share(warm-cold) {(sum(x['fused'] for x in w)/len(w)) - (sum(x['fused'] for x in c)/len(c)):+.4f} "
          f"d_min_count_mean {round(statistics.fmean([x['min_count'] for x in w]) - statistics.fmean([x['min_count'] for x in c]), 2)} "
          f"d_extra_median {statistics.median([x['extra_near'] for x in w]) - statistics.median([x['extra_near'] for x in c])}")
