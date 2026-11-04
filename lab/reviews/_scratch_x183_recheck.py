"""Addendum recheck for the X183 review: the committed 139-run ladder, the x182/x184
exclusion, and the X185 pooled bands.

Independent reader (no import from scripts/x18*).  Run from the repository root:
  python lab/reviews/_scratch_x183_recheck.py
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

L1 = Path("morphogenesis/experiments/L1_field")
POND = Path("morphogenesis/experiments/E09_pond")
GRID = 96
SCALE = 12.0
AMP = 0.5
CANDS = ("F_nominal", "F_local_mid", "F_local_mean", "F_local_min", "F_local_max")


def G_at(x, y):
    ky = 2.0 * math.pi / SCALE
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def tr(c):
    if isinstance(c, dict):
        return float(c.get("area", 0.0)), float(c.get("cx", 0.0)), float(c.get("cy", 0.0))
    return float(c[1]), float(c[2]), float(c[3])


def wd(a, b):
    d = abs(a - b) % GRID
    return min(d, GRID - d)


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


def logit(p):
    return math.log(p / (1 - p))


def dev_claim(vals, flags):
    """Replica of the stated 81-point grid one-parameter logistic."""
    if len(set(flags)) < 2 or len(set(vals)) < 2:
        return None
    base = min(max(statistics.fmean(flags), 1e-6), 1 - 1e-6)
    b = logit(base)
    lo, hi = min(vals), max(vals)
    span = hi - lo
    best = None
    for m in range(-40, 41):
        w = m / 10.0
        dev = 0.0
        for v, f in zip(vals, flags):
            z = b + w * (v - (lo + hi) / 2) / span * 2
            p = 1 / (1 + math.exp(-max(min(z, 30), -30)))
            p = min(max(p, 1e-9), 1 - 1e-9)
            dev += -2 * (f * math.log(p) + (1 - f) * math.log(1 - p))
        if best is None or dev < best:
            best = dev
    return best


def dev_mle2(vals, flags, iters=300):
    mean_v = statistics.fmean(vals)
    sd = statistics.pstdev(vals) or 1.0
    x = [(v - mean_v) / sd for v in vals]
    b0 = logit(min(max(statistics.fmean(flags), 1e-6), 1 - 1e-6))
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
        if abs(d0) < 1e-11 and abs(d1) < 1e-11:
            break
    dev = 0.0
    for xi, fi in zip(x, flags):
        p = min(max(1 / (1 + math.exp(-max(min(b0 + b1 * xi, 35.0), -35.0))), 1e-12), 1 - 1e-12)
        dev += -2 * (fi * math.log(p) + (1 - fi) * math.log(1 - p))
    return dev


def boot(fn, n, reps=4000, seed=20261104):
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        v = fn(idx)
        if v is not None:
            out.append(v)
    out.sort()
    return out[int(0.025 * len(out))], out[min(len(out) - 1, int(0.975 * len(out)))]


def load(exclude_phase):
    runs, excl = [], []
    for f in sorted(L1.glob("*.compact.json")):
        if f.stem.startswith(("x182_", "x184_")):
            if exclude_phase:
                excl.append(f.name.replace(".compact.json", ""))
                continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        p = d.get("params") or {}
        if not series or not isinstance(series[0], list) or len(series[0]) != 2:
            continue
        if not isinstance(series[0][1], list) or len(series[0][1]) != 2:
            continue
        comps = [tr(c) for c in series[0][1]]
        r0 = math.sqrt(max(comps[0][0], 1.0) / math.pi)
        dx, dy = wd(comps[0][1], comps[1][1]), wd(comps[0][2], comps[1][2])
        counts = [len(r[1]) for r in series if isinstance(r, list) and len(r) == 2 and isinstance(r[1], list)]
        if not counts:
            continue
        gs = [G_at(c[1], c[2]) for c in comps]
        fo = counts.index(1) if 1 in counts else None
        runs.append({
            "file": f.name.replace(".compact.json", ""), "family": f.name.split("_s")[0],
            "F": float(p.get("F", 0.0)), "gap": round(math.hypot(dx, dy) - 2 * r0),
            "gap_raw": math.hypot(dx, dy) - 2 * r0, "r0": r0, "dx": dx, "dy": dy,
            "steps": int(p.get("steps", 0)), "counts_min": min(counts), "counts_last": counts[-1],
            "counts_first": counts[0], "first_one": fo,
            "rebound": (fo is not None and any(c > 1 for c in counts[fo:])),
            "g_mid": G_at((comps[0][1] + comps[1][1]) / 2, (comps[0][2] + comps[1][2]) / 2),
            "g_mean": statistics.fmean(gs), "g_min": min(gs), "g_max": max(gs),
            "g_cold": min(gs), "f_local_cold": float(p.get("F", 0.0)) * (0.5 + min(gs)),
            "fused": min(counts) == 1,
        })
    return runs, excl


def cand(r, name):
    if name == "F_nominal":
        return r["F"]
    g = {"F_local_mid": r["g_mid"], "F_local_mean": r["g_mean"],
         "F_local_min": r["g_min"], "F_local_max": r["g_max"]}[name]
    return r["F"] * (1 + AMP * (2 * g - 1))


def table(runs, tag):
    by_F = defaultdict(list)
    for r in runs:
        by_F[r["F"]].append(r)
    per = {}
    for name in CANDS:
        vals = [cand(r, name) for r in runs]
        flags = [int(r["fused"]) for r in runs]
        within = {}
        for F, rs in sorted(by_F.items()):
            if len(rs) < 6 or len(set(int(x["fused"]) for x in rs)) < 2:
                continue
            within[F] = {"runs": len(rs), "share": round(statistics.fmean([int(x["fused"]) for x in rs]), 3),
                         "auc": auc([cand(r, name) for r in rs], [int(r["fused"]) for r in rs])}
        wa = [v["auc"] for v in within.values() if v["auc"] is not None]
        per[name] = {"auc": round(auc(vals, flags), 4),
                     "within": within,
                     "mean_within": round(statistics.fmean(wa), 4) if wa else None,
                     "dev": round(dev_claim(vals, flags), 1),
                     "dev2": round(dev_mle2(vals, flags), 1)}
    print(f"--- {tag}: n={len(runs)} fused={sum(1 for r in runs if r['fused'])}")
    for name in CANDS:
        v = per[name]
        print(f"  {name:>13}: AUC={v['auc']}  mean_within={v['mean_within']}  dev={v['dev']}  dev_mle2={v['dev2']}  "
              f"within={ {str(F): d['auc'] for F, d in v['within'].items()} }")
    return by_F, per


print("=== 1. exclusion and ladder count")
runs_ex, excl = load(True)
runs_all, _ = load(False)
print(f"compact artifacts scanned: {len(list(L1.glob('*.compact.json')))}")
print(f"runs built with exclusion: {len(runs_ex)}; excluded by name: {len(excl)}")
print(f"runs built without exclusion: {len(runs_all)}")

ladder = [r for r in runs_ex if r["gap"] == 10 and 2.7 <= r["r0"] <= 3.1]
ladder_nx = [r for r in runs_all if r["gap"] == 10 and 2.7 <= r["r0"] <= 3.1]
print(f"\nLADDER with exclusion: n={len(ladder)}")
print(f"LADDER without exclusion: n={len(ladder_nx)}")
extra = sorted(r["file"] for r in ladder_nx if r["file"] not in {x["file"] for x in ladder})
print(f"phase-selected runs that WOULD enter the ladder: {len(extra)} "
      f"(x182 {sum(1 for e in extra if e.startswith('x182_'))}, x184 {sum(1 for e in extra if e.startswith('x184_'))})")
print(f"any x182/x184 inside the committed ladder: "
      f"{any(r['file'].startswith(('x182_', 'x184_')) for r in ladder)}")
print(f"x181 compacts inside the committed ladder: "
      f"{sum(1 for r in ladder if r['file'].startswith('x181_'))}")
print(f"excluded names = all 60 present in the corpus: {len(excl) == 60}")

by_F, per = {}, {}
print()
by_F, per = table(ladder, "committed 139-run ladder")
for F, rs in sorted(by_F.items()):
    fams = defaultdict(int)
    for x in rs:
        fams[x["family"]] += 1
    print(f"  F={F}: {len(rs)} runs, share {sum(1 for x in rs if x['fused'])/len(rs):.4f}, families {dict(fams)}")

print("\n=== 2. do the 109-run caveats still hold on 139?")
flags = [int(r["fused"]) for r in ladder]
n = len(ladder)
vmin = [cand(r, "F_local_min") for r in ladder]
vmean = [cand(r, "F_local_mean") for r in ladder]
vmax = [cand(r, "F_local_max") for r in ladder]
vmid = [cand(r, "F_local_mid") for r in ladder]
print(f"  AUC min={per['F_local_min']['auc']} mean={per['F_local_mean']['auc']} "
      f"diff={per['F_local_min']['auc']-per['F_local_mean']['auc']:+.4f}")
ci = boot(lambda idx: auc([vmin[i] for i in idx], [flags[i] for i in idx])
          - auc([vmean[i] for i in idx], [flags[i] for i in idx]), n)
print(f"  paired bootstrap 95% CI of min-mean diff: [{ci[0]:+.4f},{ci[1]:+.4f}]")
print(f"  within-family AUC (families with both outcomes):")
for fam in sorted(set(r["family"] for r in ladder)):
    rs = [r for r in ladder if r["family"] == fam]
    fl = [int(r["fused"]) for r in rs]
    if len(rs) < 6 or len(set(fl)) < 2:
        print(f"    {fam:>14}: n={len(rs)} fused={sum(fl)} -- n/a")
        continue
    am, ae = auc([cand(r, "F_local_min") for r in rs], fl), auc([cand(r, "F_local_mean") for r in rs], fl)
    print(f"    {fam:>14}: n={len(rs)} fused={sum(fl)} AUC_min={am:.4f} AUC_mean={ae:.4f} ({am-ae:+.4f})")
lof = []
for fam in sorted(set(r["family"] for r in ladder)):
    sub = [r for r in ladder if r["family"] != fam]
    fl = [int(r["fused"]) for r in sub]
    lof.append(auc([cand(r, "F_local_min") for r in sub], fl) - auc([cand(r, "F_local_mean") for r in sub], fl))
print(f"  leave-one-family-out min-mean: min={min(lof):+.4f} max={max(lof):+.4f} (all positive: {all(x > 0 for x in lof)})")
fused = [r for r in ladder if r["fused"]]
print(f"  coalescence: first-sample 1-component runs {sum(1 for r in ladder if r['counts_first'] == 1)}; "
      f"fused {len(fused)}; ending on 1: {sum(1 for r in fused if r['counts_last'] == 1)}; "
      f"rebound: {sum(1 for r in fused if r['rebound'])}")
print(f"  r0: {min(r['r0'] for r in ladder):.5f}..{max(r['r0'] for r in ladder):.5f}; "
      f"gap_raw: {min(r['gap_raw'] for r in ladder):.5f}..{max(r['gap_raw'] for r in ladder):.5f}; "
      f"dx set {sorted(set(r['dx'] for r in ladder))}; dy set {sorted(set(r['dy'] for r in ladder))}")

# permutation null for best-over-4 on the 139 set
rng = random.Random(11)
pool = {"min": vmin, "mean": vmean, "max": vmax, "mid": vmid}
obs = max(per[k]["auc"] for k in ("F_local_min", "F_local_mean", "F_local_max", "F_local_mid"))
lvl = defaultdict(list)
for i, r in enumerate(ladder):
    lvl[r["F"]].append(i)
null = []
for _ in range(2000):
    pf = [0] * n
    for F, idxs in lvl.items():
        lab = [flags[i] for i in idxs]
        rng.shuffle(lab)
        for i, l in zip(idxs, lab):
            pf[i] = l
    null.append(max(auc(pool[k], pf) for k in pool))
null.sort()
print(f"  permutation null (within-level shuffle, 2000): obs best-over-4={obs:.4f} null95={null[int(0.95*len(null))]:.4f} "
      f"p={(sum(1 for v in null if v >= obs)+1)/(len(null)+1):.4f}")

# horizon control
print()
table([r for r in ladder if r["steps"] == 2000], "score: steps==2000")

print("\n=== 3. X185 pooled bands from the x182/x184 compacts")
phase = [r for r in runs_all if r["file"].startswith(("x182_", "x184_"))]
print(f"x182/x184 runs read: {len(phase)} "
      f"(x182 {sum(1 for r in phase if r['file'].startswith('x182_'))}, "
      f"x184 {sum(1 for r in phase if r['file'].startswith('x184_'))}); "
      f"fused {sum(1 for r in phase if r['fused'])}")
bands = [(0.0, 0.019), (0.019, 0.024), (0.024, 0.028), (0.028, 0.032), (0.032, 0.04)]
print("band | runs | fused | share  (my read)")
for lo, hi in bands:
    sub = [r for r in phase if lo <= r["f_local_cold"] < hi]
    k = sum(1 for r in sub if r["fused"])
    f182 = sum(1 for r in sub if r["file"].startswith("x182_"))
    f184 = sum(1 for r in sub if r["file"].startswith("x184_"))
    print(f"  [{lo:.3f},{hi:.3f}) | {len(sub):>2} | {k:>2} | {k/len(sub) if sub else float('nan'):.4f}   "
          f"(x182 {f182}, x184 {f184})")

# run-level cross-check against the committed x185 detail
x185 = json.loads((POND / "l1_field_x185_one_law.json").read_text(encoding="utf-8"))
det = {d["file"]: d for d in x185["runs_detail"]}
mine = {r["file"]: r for r in phase}
bad = []
for f, d in det.items():
    m = mine.get(f)
    if m is None:
        bad.append((f, "missing"))
        continue
    if abs(m["g_cold"] - d["g_cold"]) > 5e-4 or abs(m["f_local_cold"] - d["f_local_cold"]) > 5e-4:
        bad.append((f, f"g_cold {m['g_cold']:.4f} vs {d['g_cold']:.4f}; "
                       f"F_local {m['f_local_cold']:.5f} vs {d['f_local_cold']:.5f}"))
    if bool(m["fused"]) != bool(d["fused"]):
        bad.append((f, f"fused {m['fused']} vs {d['fused']}"))
print(f"run-by-run cross-check against x185 runs_detail: {len(det)} entries, mismatches {len(bad)}")
for b in bad[:10]:
    print("   ", b)
print(f"any x182/x184 run inside the committed ladder: "
      f"{any(r['file'].startswith(('x182_', 'x184_')) for r in ladder)}")
