"""Independent recomputation for the X183 / X180 / X181 review.

Reader written from scratch against the raw committed artifacts only:
  morphogenesis/experiments/L1_field/*.compact.json          (ladder + candidates)
  morphogenesis/experiments/L1_field/x181_s1211..1240.json   (fresh family; not compacted)
Nothing is imported from scripts/x18*.py.

Run from the repository root:  python lab/reviews/_scratch_x183_check.py
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(".").resolve()
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
GRID = 96
HETERO_SCALE = 12.0
HETERO_AMP = 0.5
Z = 1.959963984540054
CANDS = ("F_nominal", "F_local_mid", "F_local_mean", "F_local_min", "F_local_max")


# ---------------------------------------------------------------- primitives
def G_at(x, y):
    ky = 2.0 * math.pi / HETERO_SCALE
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def triple(c):
    if isinstance(c, dict):
        return float(c.get("area", 0.0)), float(c.get("cx", 0.0)), float(c.get("cy", 0.0))
    return float(c[1]), float(c[2]), float(c[3])


def wdist(a, b):
    d = abs(a - b) % GRID
    return min(d, GRID - d)


def auc(vals, flags):
    pos = [v for v, f in zip(vals, flags) if f]
    neg = [v for v, f in zip(vals, flags) if not f]
    if not pos or not neg:
        return None
    wins = 0.0
    for a in pos:
        for b in neg:
            if a > b:
                wins += 1.0
            elif a == b:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def logit(p):
    return math.log(p / (1 - p))


def dev_claim_method(vals, flags):
    """Exact replica of the stated definition: intercept=logit(base), slope on an 81-point
    m/10 grid, span-normalised.  Re-implemented, not imported."""
    if len(set(flags)) < 2 or len(set(vals)) < 2:
        return None
    base = min(max(statistics.fmean(flags), 1e-6), 1 - 1e-6)
    b = logit(base)
    lo, hi = min(vals), max(vals)
    span = hi - lo
    if span == 0:
        return None
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


def dev_fine_fixed(vals, flags, grid=8001, wmax=3000.0):
    if len(set(flags)) < 2 or len(set(vals)) < 2:
        return None
    b = logit(min(max(statistics.fmean(flags), 1e-9), 1 - 1e-9))
    lo = min(vals)
    best = None
    for i in range(grid + 1):
        w = -wmax + 2 * wmax * i / grid
        dev = 0.0
        for v, f in zip(vals, flags):
            z = max(min(b + w * (v - lo), 35.0), -35.0)
            p = 1 / (1 + math.exp(-z))
            p = min(max(p, 1e-12), 1 - 1e-12)
            dev += -2 * (f * math.log(p) + (1 - f) * math.log(1 - p))
        if best is None or dev < best:
            best = dev
    return best


def deviance_two_param(vals, flags, iters=300):
    n = len(vals)
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
        z = max(min(b0 + b1 * xi, 35.0), -35.0)
        p = min(max(1 / (1 + math.exp(-z)), 1e-12), 1 - 1e-12)
        dev += -2 * (fi * math.log(p) + (1 - fi) * math.log(1 - p))
    return dev, b0, b1


def pearson(a, b):
    if len(a) < 2:
        return None
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    sa = math.sqrt(sum((v - ma) ** 2 for v in a))
    sb = math.sqrt(sum((v - mb) ** 2 for v in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def spearman(a, b):
    def rank(vs):
        order = sorted(range(len(vs)), key=lambda i: vs[i])
        r = [0.0] * len(vs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(a), rank(b))


def boot_ci(fn, n, reps=4000, seed=20261104):
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        v = fn(idx)
        if v is not None:
            out.append(v)
    if not out:
        return None
    out.sort()
    return out[int(0.025 * len(out))], out[min(len(out) - 1, int(0.975 * len(out)))]


def fmt(x):
    return "None" if x is None else f"{x:+.4f}"


# ---------------------------------------------------------------- the reader
def load_runs():
    runs = []
    files = sorted(L1.glob("*.compact.json"))
    n_first_two = 0
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        params = d.get("params") or {}
        if not series or not isinstance(series[0], list) or len(series[0]) != 2:
            continue
        if not isinstance(series[0][1], list) or len(series[0][1]) != 2:
            continue
        n_first_two += 1
        comps = [triple(c) for c in series[0][1]]
        r0 = math.sqrt(max(comps[0][0], 1.0) / math.pi)
        dx = wdist(comps[0][1], comps[1][1])
        dy = wdist(comps[0][2], comps[1][2])
        dist = math.hypot(dx, dy)
        gap = round(dist - 2 * r0)
        counts = [len(r[1]) for r in series if isinstance(r, list) and len(r) == 2 and isinstance(r[1], list)]
        if not counts:
            continue
        gs = [G_at(c[1], c[2]) for c in comps]
        first_one = counts.index(1) if 1 in counts else None
        runs.append({
            "file": f.name.replace(".compact.json", ""),
            "family": f.name.split("_s")[0],
            "F": float(params.get("F", 0.0)),
            "gap": gap,
            "gap_raw": dist - 2 * r0,
            "dx": dx, "dy": dy,
            "r0": r0,
            "area0": comps[0][0], "area1": comps[1][0],
            "steps": int(params.get("steps", 0)),
            "n_samples": len(counts),
            "counts_min": min(counts),
            "counts_last": counts[-1],
            "counts_first": counts[0],
            "first_one": first_one,
            "one_block": (None if first_one is None else
                          max(i for i, c in enumerate(counts) if c == 1) - first_one + 1),
            "n_one": counts.count(1),
            "rebound": (first_one is not None and any(c > 1 for c in counts[first_one:])),
            "g_mid": G_at((comps[0][1] + comps[1][1]) / 2, (comps[0][2] + comps[1][2]) / 2),
            "g_mean": statistics.fmean(gs),
            "g_min": min(gs), "g_max": max(gs),
            "g0": gs[0], "g1": gs[1],
            "cx0": comps[0][1], "cx1": comps[1][1],
            "cy0": comps[0][2],
            "fused": min(counts) == 1,
        })
    return files, n_first_two, runs


def cand(r, name):
    if name == "F_nominal":
        return r["F"]
    g = {"F_local_mid": r["g_mid"], "F_local_mean": r["g_mean"],
         "F_local_min": r["g_min"], "F_local_max": r["g_max"]}[name]
    return r["F"] * (1 + HETERO_AMP * (2 * g - 1))


def candidate_table(runs, tag):
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
            within[F] = {"runs": len(rs),
                         "share": round(statistics.fmean([int(x["fused"]) for x in rs]), 3),
                         "auc": auc([cand(r, name) for r in rs], [int(r["fused"]) for r in rs])}
        wa = [v["auc"] for v in within.values() if v["auc"] is not None]
        per[name] = {
            "auc_overall": round(auc(vals, flags), 4),
            "within": within,
            "mean_auc_within": round(statistics.fmean(wa), 4) if wa else None,
            "dev_claim": round(dev_claim_method(vals, flags), 1),
            "dev_fine1": round(dev_fine_fixed(vals, flags), 1),
            "dev_mle2": round(deviance_two_param(vals, flags)[0], 1),
        }
    print(f"--- {tag}: n={len(runs)}, fused={sum(1 for r in runs if r['fused'])}")
    for name in CANDS:
        v = per[name]
        wa = {str(F): (None if d["auc"] is None else round(d["auc"], 4)) for F, d in v["within"].items()}
        print(f"  {name:>13}: AUC={v['auc_overall']}  mean_within={v['mean_auc_within']}  "
              f"dev[claim-method]={v['dev_claim']} dev[fine1]={v['dev_fine1']} dev[mle2]={v['dev_mle2']}")
        print(f"                within={wa}")
    return by_F, per


def main():
    files, n_first_two, runs = load_runs()
    print(f"compact files: {len(files)}; 2-component first sample: {n_first_two}; runs built: {len(runs)}")

    ladder = [r for r in runs if r["gap"] == 10 and 2.7 <= r["r0"] <= 3.1]
    print(f"\nLADDER (gap==10, 2.7<=r0<=3.1): n={len(ladder)}")
    by_F = defaultdict(list)
    for r in ladder:
        by_F[r["F"]].append(r)
    k_tot = sum(1 for r in ladder if r["fused"])
    print(f"  fused total = {k_tot}/{len(ladder)} = {k_tot/len(ladder):.4f}")
    for F, rs in sorted(by_F.items()):
        k = sum(1 for x in rs if x["fused"])
        fams = defaultdict(int)
        for x in rs:
            fams[x["family"]] += 1
        print(f"  F={F}: {len(rs)} runs, fused {k}, share {k/len(rs):.4f}, "
              f"r0 [{min(x['r0'] for x in rs):.4f},{max(x['r0'] for x in rs):.4f}], "
              f"gap_raw [{min(x['gap_raw'] for x in rs):.5f},{max(x['gap_raw'] for x in rs):.5f}], "
              f"dx {sorted(set(round(x['dx'],3) for x in rs))}, dy {sorted(set(round(x['dy'],3) for x in rs))}, "
              f"steps {sorted(set(x['steps'] for x in rs))}")
        print(f"        families {dict(fams)}")

    # ---- every gap-10 run in the whole corpus, by r0 (what the filter admits)
    g10 = [r for r in runs if r["gap"] == 10]
    print(f"\n  all gap==10 runs in the corpus: {len(g10)}, by r0: "
          f"{ {round(v,3): sum(1 for r in g10 if round(r['r0'],3)==round(v,3)) for v in sorted(set(r['r0'] for r in g10))} }")

    print("\n=== ATTACK (d): fusion readout soundness")
    print(f"  runs whose first sample already has 1 component: {sum(1 for r in ladder if r['counts_first']==1)}")
    fused = [r for r in ladder if r["fused"]]
    print(f"  fused runs: {len(fused)}; of them, ending on 1 component: {sum(1 for r in fused if r['counts_last']==1)}")
    print(f"  fused runs whose 1-component block is followed by >1 again (rebound): {sum(1 for r in fused if r['rebound'])}")
    print(f"  number of samples with count==1 inside a fused run: median {statistics.median(r['n_one'] for r in fused)}, "
          f"max {max(r['n_one'] for r in fused)}; samples per run median {statistics.median(r['n_samples'] for r in fused)}")
    print(f"  first_one sample-index range: [{min(r['first_one'] for r in fused)}, {max(r['first_one'] for r in fused)}]")
    print(f"  non-fused runs: min count {sorted(set(r['counts_min'] for r in ladder if not r['fused']))}")
    print(f"  example rebound traces:")
    for r in fused[:3]:
        print(f"     {r['file']}: first_one@{r['first_one']}, last {r['counts_last']}, samples {r['n_samples']}")

    print("\n=== full ladder candidates")
    by_F, per = candidate_table(ladder, "full ladder")

    print("\n=== ATTACK (c): drop F=0.036")
    lad2 = [r for r in ladder if r["F"] != 0.036]
    _, per2 = candidate_table(lad2, "ladder minus F=0.036")
    print(f"  ranking (mean_within) full: " +
          ", ".join(f"{n}={per[n]['mean_auc_within']}" for n in CANDS))
    print(f"  ranking (mean_within) minus F=0.036: " +
          ", ".join(f"{n}={per2[n]['mean_auc_within']}" for n in CANDS))
    print(f"  ranking (AUC overall) full: " + ", ".join(f"{n}={per[n]['auc_overall']}" for n in CANDS))
    print(f"  ranking (AUC overall) minus F=0.036: " + ", ".join(f"{n}={per2[n]['auc_overall']}" for n in CANDS))

    # horizon control: only 2000-step runs
    lad2000 = [r for r in ladder if r["steps"] == 2000]
    print("\n=== horizon control: only steps==2000")
    candidate_table(lad2000, "steps==2000")

    print("\n=== ATTACK (a): is G_min post hoc?")
    flags = [int(r["fused"]) for r in ladder]
    n = len(ladder)
    vmin = [cand(r, "F_local_min") for r in ladder]
    vmean = [cand(r, "F_local_mean") for r in ladder]
    vmax = [cand(r, "F_local_max") for r in ladder]
    vmid = [cand(r, "F_local_mid") for r in ladder]
    a_min, a_mean = auc(vmin, flags), auc(vmean, flags)
    print(f"  AUC(G_min)={a_min:.4f}  AUC(G_mean)={a_mean:.4f}  diff={a_min-a_mean:+.4f}")
    ci = boot_ci(lambda idx: auc([vmin[i] for i in idx], [flags[i] for i in idx])
                 - auc([vmean[i] for i in idx], [flags[i] for i in idx]), n)
    print(f"  paired bootstrap 95% CI of the diff: [{ci[0]:+.4f}, {ci[1]:+.4f}]")

    # mean-within bootstrap of the min-mean difference
    by_F_all = by_F
    def mw(vals_by, idx):
        sub = [ladder[i] for i in idx]
        out = []
        for name in ("F_local_min", "F_local_mean"):
            wa = []
            for F, rs in by_F_all.items():
                s = [r for r in sub if r["F"] == F]
                if len(s) < 6 or len(set(int(x["fused"]) for x in s)) < 2:
                    continue
                wa.append(auc([cand(r, name) for r in s], [int(r["fused"]) for r in s]))
            out.append(statistics.fmean(wa) if wa else None)
        if out[0] is None or out[1] is None:
            return None
        return out[0] - out[1]
    ci2 = boot_ci(lambda idx: mw(None, idx), n)
    print(f"  mean-within: min={per['F_local_min']['mean_auc_within']} mean={per['F_local_mean']['mean_auc_within']} "
          f"diff={per['F_local_min']['mean_auc_within']-per['F_local_mean']['mean_auc_within']:+.4f} "
          f"bootstrap95 [{ci2[0]:+.4f},{ci2[1]:+.4f}]")

    # leave-one-family-out
    print("  leave-one-family-out (AUC overall min vs mean):")
    fams_all = sorted(set(r["family"] for r in ladder))
    for fam in fams_all:
        sub = [r for r in ladder if r["family"] != fam]
        fl = [int(r["fused"]) for r in sub]
        if len(set(fl)) < 2:
            continue
        am = auc([cand(r, "F_local_min") for r in sub], fl)
        ae = auc([cand(r, "F_local_mean") for r in sub], fl)
        an = auc([r["F"] for r in sub], fl)
        print(f"    -{fam:>18}: min={am:.4f} mean={ae:.4f} (min-mean {am-ae:+.4f}) nominal={an:.4f}")

    # per-family within-family AUC: removes the family as a confounder entirely
    print("  per-family AUC (families with both outcomes; F constant inside a family):")
    fam_list = sorted(set(r["family"] for r in ladder))
    for fam in fam_list:
        rs = [r for r in ladder if r["family"] == fam]
        fl = [int(r["fused"]) for r in rs]
        if len(rs) < 6 or len(set(fl)) < 2:
            print(f"    {fam:>18}: n={len(rs)} fused={sum(fl)} -- AUC not computable")
            continue
        am = auc([cand(r, "F_local_min") for r in rs], fl)
        ae = auc([cand(r, "F_local_mean") for r in rs], fl)
        print(f"    {fam:>18}: n={len(rs)} fused={sum(fl)} AUC_min={am:.4f} AUC_mean={ae:.4f} (min-mean {am-ae:+.4f})")
    # family-level: does a family's share track its mean g_min (between-family proxy)?
    fs = [statistics.fmean([r["g_min"] for r in rs]) for fam in fam_list
          for rs in [[r for r in ladder if r["family"] == fam]]]
    fr = [statistics.fmean([int(r["fused"]) for r in rs]) for fam in fam_list
          for rs in [[r for r in ladder if r["family"] == fam]]]
    print(f"  between-family pearson(mean g_min, family share) over {len(fs)} families = {fmt(pearson(fs, fr))}")

    # null deviance and LRT for the one-parameter fit
    nd = -2 * sum(f * math.log(statistics.fmean(flags)) + (1 - f) * math.log(1 - statistics.fmean(flags))
                  for f in flags)
    print(f"  null deviance (intercept only) = {nd:.1f}")
    for name in CANDS:
        d = nd - per[name]["dev_claim"]
        print(f"    {name:>13}: dev={per[name]['dev_claim']:>6}  LRT chi2_1={d:5.1f}  p={math.erfc(math.sqrt(max(d,0)/2)):.3g}")

    # half/half selection
    rng = random.Random(7)
    pool = {"min": vmin, "mean": vmean, "max": vmax, "mid": vmid}
    picks = defaultdict(int)
    ev_sel, ev_mean = [], []
    for _ in range(4000):
        idx = list(range(n))
        rng.shuffle(idx)
        A, B = idx[: n // 2], idx[n // 2:]
        fA = [flags[i] for i in A]
        fB = [flags[i] for i in B]
        if len(set(fA)) < 2 or len(set(fB)) < 2:
            continue
        best = max(pool, key=lambda k: auc([pool[k][i] for i in A], fA))
        picks[best] += 1
        ev_sel.append(auc([pool[best][i] for i in B], fB))
        ev_mean.append(auc([vmean[i] for i in B], fB))
    print(f"  half/half selection (4000 reps): picked {dict(picks)}")
    print(f"    held-out AUC: selected mean={statistics.fmean(ev_sel):.4f} (sd {statistics.pstdev(ev_sel):.4f}); "
          f"always-mean={statistics.fmean(ev_mean):.4f}")

    # permutation null for best-over-4, labels permuted within nominal level
    rng = random.Random(11)
    obs_best = max(per[k]["auc_overall"] for k in CANDS[1:])
    level_idx = defaultdict(list)
    for i, r in enumerate(ladder):
        level_idx[r["F"]].append(i)
    null = []
    for _ in range(2000):
        pf = [0] * n
        for F, idxs in level_idx.items():
            lab = [flags[i] for i in idxs]
            rng.shuffle(lab)
            for i, l in zip(idxs, lab):
                pf[i] = l
        null.append(max(auc(pool[k], pf) for k in pool))
    null.sort()
    pval = (sum(1 for v in null if v >= obs_best) + 1) / (len(null) + 1)
    print(f"  permutation null (labels shuffled within level): obs best-over-4 AUC={obs_best:.4f}, "
          f"null median={statistics.median(null):.4f}, null95={null[int(0.95*len(null))]:.4f}, p={pval:.4f}")

    print("\n=== ATTACK (b): confounding with r0 / gap / geometry")
    print(f"  r0: min={min(r['r0'] for r in ladder):.5f} max={max(r['r0'] for r in ladder):.5f} "
          f"(spread {max(r['r0'] for r in ladder)-min(r['r0'] for r in ladder):.2e})")
    print(f"  gap_raw: min={min(r['gap_raw'] for r in ladder):.5f} max={max(r['gap_raw'] for r in ladder):.5f}")
    print(f"  area0/area1 values: {sorted(set(r['area0'] for r in ladder))} / {sorted(set(r['area1'] for r in ladder))}")
    print(f"  pearson(g_min, r0)={fmt(pearson([r['g_min'] for r in ladder],[r['r0'] for r in ladder]))} "
          f"(r0 constant -> undefined)")
    print(f"  pearson(g_min, gap_raw)={fmt(pearson([r['g_min'] for r in ladder],[r['gap_raw'] for r in ladder]))}")
    print(f"  pearson(g_min, g_mid)={fmt(pearson([r['g_min'] for r in ladder],[r['g_mid'] for r in ladder]))}  "
          f"spearman={fmt(spearman([r['g_min'] for r in ladder],[r['g_mid'] for r in ladder]))}")
    print(f"  pearson(g_min, g_mean)={fmt(pearson([r['g_min'] for r in ladder],[r['g_mean'] for r in ladder]))}  "
          f"pearson(g_min, g_max)={fmt(pearson([r['g_min'] for r in ladder],[r['g_max'] for r in ladder]))}")
    print(f"  AUC(r0 -> fused)={auc([r['r0'] for r in ladder], flags)}; AUC(gap_raw)={auc([r['gap_raw'] for r in ladder], flags)}")
    print(f"  distinct g_min values: {len(set(round(r['g_min'],6) for r in ladder))}; distinct g_mean: "
          f"{len(set(round(r['g_mean'],6) for r in ladder))}; g_mid: {len(set(round(r['g_mid'],6) for r in ladder))}")
    # which body is the cold one
    left = sum(1 for r in ladder if (r["g_min"] == r["g0"]) == (r["cx0"] < r["cx1"]))
    print(f"  g_min is the left body in {left}/{len(ladder)} runs, right in {len(ladder)-left}")
    same = sum(1 for r in ladder if r["g_min"] == r["g0"])
    print(f"  g_min is component 0 in {same}/{len(ladder)}")
    # does g_min equal g_mid or g_max often?
    print(f"  g_min == g_mean: {sum(1 for r in ladder if abs(r['g_min']-r['g_mean'])<1e-12)}; "
          f"g_min == g_max: {sum(1 for r in ladder if abs(r['g_min']-r['g_max'])<1e-12)}")
    print(f"  pearson(g_min, cy0)={fmt(pearson([r['g_min'] for r in ladder],[r['cy0'] for r in ladder]))}")
    print("  r0 / gap spread inside each family:")
    fams = defaultdict(list)
    for r in ladder:
        fams[r["family"]].append(r)
    for fam, rs in sorted(fams.items()):
        print(f"    {fam:>18}: n={len(rs)} r0 {min(x['r0'] for x in rs):.4f}..{max(x['r0'] for x in rs):.4f} "
              f"gap_raw {min(x['gap_raw'] for x in rs):.4f}..{max(x['gap_raw'] for x in rs):.4f}")

    print("\n=== X181 fresh family")
    rows = []
    for seed in range(1211, 1241):
        d = json.loads((L1 / f"x181_s{seed}.json").read_text(encoding="utf-8"))
        series = d.get("series") or []
        counts = [len(r.get("components_log") or []) for r in series]
        rows.append({"seed": seed, "fused": bool(counts) and min(counts) == 1,
                     "min": min(counts) if counts else None, "final": counts[-1] if counts else None,
                     "first": counts[0] if counts else None, "rebound": (counts.index(1) is not None and
                     any(c > 1 for c in counts[counts.index(1):])) if 1 in counts else None})
    k = sum(1 for r in rows if r["fused"])
    w = wilson(k, len(rows))
    print(f"  fused {k}/{len(rows)} = {k/len(rows):.4f}; Wilson [{w[0]:.4f},{w[1]:.4f}]")
    print(f"  first-sample counts {sorted(set(r['first'] for r in rows))}; final counts {sorted(set(r['final'] for r in rows))}")
    print(f"  fused seeds {[r['seed'] for r in rows if r['fused']]}")
    print(f"  fused runs that rebound above 1: {sum(1 for r in rows if r['fused'] and r['rebound'])}/{k}")
    print(f"  artifact reference: {json.loads((ROOT/'morphogenesis/experiments/E09_pond/l1_field_x181_worst_cell.json').read_text(encoding='utf-8'))['observed']}")

    print("\n  pooled_before families recomputed from raw compacts (ladder F=0.03 subset):")
    checks = [("x136", "x136"), ("x158_g10_r30", "x158_g10_r30"), ("x168c_F30_g10", "x168c_F30_g10"),
              ("x168c_F30_len", "x168c_F30_len"), ("x170_F30", "x170_F30"), ("x173_g10", "x173_g10")]
    lvl = by_F[0.03]
    tk = tn = 0
    for name, pre in checks:
        sub = [r for r in lvl if r["family"].startswith(pre)]
        kk, nn = sum(1 for r in sub if r["fused"]), len(sub)
        tk += kk
        tn += nn
        print(f"    {name:>14}: {kk}/{nn} = {kk/nn:.3f}")
    print(f"    TOTAL {tk}/{tn} = {tk/tn:.4f}; pool with fresh = {tk+k}/{tn+len(rows)} = {(tk+k)/(tn+len(rows)):.4f}")


if __name__ == "__main__":
    main()
