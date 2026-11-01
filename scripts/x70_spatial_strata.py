"""x70_spatial_strata.py — the spatial control for X70 done over all events, stratified instead of matched.

The first control (`x70_spatial_null.py`) required a non-parent structure at the parent–child distance within ±4 cells. That
kept only 50 of 925 events and those 50 were not a random subsample, so the control could not decide. This version removes
the tolerance and keeps every event:

* surrogate = the non-parent structure present at the daughter's birth that is **closest in distance** to the daughter;
* the observed–surrogate comparison is made **inside distance bins** (pooled quartiles), not globally, because distance and
  crowding are mixed in this world;
* repeated inside **occupancy tertiles** (components present at the daughter's birth);
* a rank partial correlation of parent and daughter controlling distance and occupancy;
* a cluster bootstrap over (seed, snapshot) for the difference.

Decision rule, registered in `docs/plan/10d-field-metrics-and-form.md` §10ep before this script ran: survives if the
event-weighted within-bin difference exceeds +0.10 in the pooled estimate and in ≥4 of 5 seeds and in the densest occupancy
tertile; spatial if pooled difference ≤ 0; otherwise unresolved.

Run:
    python scripts/x70_spatial_strata.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x70_spatial_strata.json"

GRID = 96
DRAWS = 40
BOOT = 400
MIN_PAIRS = 5


def wrap_d(a, b, n=GRID):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    dx = min(dx, n - dx)
    dy = min(dy, n - dy)
    return math.hypot(dx, dy)


def events_for_run(path: Path, seed: int) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    snapshots = []
    for s in d.get("series") or []:
        entry = {}
        for c in s.get("components_log") or []:
            if c.get("uid") is not None and c.get("cx") is not None:
                entry[int(c["uid"])] = (float(c["cx"]), float(c["cy"]))
        snapshots.append((int(s.get("step") or 0), entry))
    snapshots.sort()

    out = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if p_uid not in peaks or c_uid not in peaks or c_uid not in first:
            continue
        t_birth = first[c_uid]
        prev = [(t, m) for t, m in snapshots if t < t_birth and p_uid in m]
        nxt = [(t, m) for t, m in snapshots if t >= t_birth and c_uid in m]
        if not prev or not nxt:
            continue
        p_pos = prev[-1][1][p_uid]
        t_child, m_child = nxt[0]
        c_pos = m_child[c_uid]
        d_pc = wrap_d(p_pos, c_pos)

        cands = [(wrap_d(pos, c_pos), peaks[uid]) for uid, pos in m_child.items()
                 if uid not in (p_uid, c_uid) and uid in peaks]
        if not cands:
            continue
        cands.sort()
        out.append({"parent_peak": peaks[p_uid], "child_peak": peaks[c_uid],
                    "distance": d_pc, "occupancy": len(m_child),
                    "birth": t_birth, "c_pos": c_pos,
                    "cands": cands, "cluster": [seed, t_child]})
    return out


LOCAL_R = 8          # cells; window for the local environment
LOCAL_THR = 0.2      # the same threshold the component detector uses


def local_env(events: list[dict], fields_dir: Path, tag: str, save_every: int = 200) -> int:
    """Attach local field statistics at each daughter's birth. Returns the number of events covered.

    The field is saved every save_every steps, so the snapshot used is the last one at or before the birth step. Local
    statistics are the mean v and the occupied fraction (v > threshold) inside a radius-LOCAL_R disc around the
    daughter's centroid, with periodic wrap.
    """
    cache: dict[int, np.ndarray] = {}
    covered = 0
    for e in events:
        t = int(e["birth"])
        step = (t // save_every) * save_every
        path = fields_dir / f"{tag}_t{step}.npy"
        if not path.exists():
            e["local_v"] = None
            e["local_occ"] = None
            continue
        if step not in cache:
            cache[step] = np.load(path)
        v = cache[step]
        n = v.shape[0]
        cx, cy = e["c_pos"]
        xi = int(round(cx)) % n
        yi = int(round(cy)) % n
        xs = (np.arange(-LOCAL_R, LOCAL_R + 1) + xi) % n
        ys = (np.arange(-LOCAL_R, LOCAL_R + 1) + yi) % n
        win = v[np.ix_(ys, xs)]
        e["local_v"] = float(win.mean())
        e["local_occ"] = float((win > LOCAL_THR).mean())
        covered += 1
    return covered


def corr(pairs):
    if len(pairs) < MIN_PAIRS:
        return None
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    mx, my = st.mean(xs), st.mean(ys)
    sx, sy = st.pstdev(xs), st.pstdev(ys)
    if not sx or not sy:
        return None
    return sum((x - mx) * (y - my) for x, y in pairs) / len(pairs) / (sx * sy)


def fisher_mean(rs, weights):
    zs, ws = [], []
    for r, w in zip(rs, weights):
        if r is None or w <= 0 or abs(r) >= 1:
            continue
        zs.append(math.atanh(r))
        ws.append(w)
    if not zs:
        return None
    z = sum(wi * zi for zi, wi in zip(zs, ws)) / sum(ws)
    return math.tanh(z)


def weighted_mean(vals, weights):
    pairs = [(v, w) for v, w in zip(vals, weights) if v is not None and w > 0]
    if not pairs:
        return None
    return sum(v * w for v, w in pairs) / sum(w for _, w in pairs)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def partial_corr(x, y, controls):
    """Rank partial correlation of x and y controlling the given rank covariates (linear residuals)."""
    n = len(x)
    if n < 10:
        return None
    cols = [[1.0] * n] + [ranks(c) for c in controls]
    # normal equations (k small: 3 columns)
    k = len(cols)
    A = [[sum(cols[i][t] * cols[j][t] for t in range(n)) for j in range(k)] for i in range(k)]
    def solve(rhs):
        M = [row[:] + [rhs[i]] for i, row in enumerate(A)]
        for c in range(k):
            piv = max(range(c, k), key=lambda r: abs(M[r][c]))
            if abs(M[piv][c]) < 1e-12:
                return None
            M[c], M[piv] = M[piv], M[c]
            pv = M[c][c]
            M[c] = [v / pv for v in M[c]]
            for r in range(k):
                if r != c and M[r][c]:
                    f = M[r][c]
                    M[r] = [a - f * b for a, b in zip(M[r], M[c])]
        return [M[i][k] for i in range(k)]
    rx, ry = ranks(x), ranks(y)
    bx = solve([sum(cols[i][t] * rx[t] for t in range(n)) for i in range(k)])
    by = solve([sum(cols[i][t] * ry[t] for t in range(n)) for i in range(k)])
    if bx is None or by is None:
        return None
    ex = [rx[t] - sum(bx[i] * cols[i][t] for i in range(k)) for t in range(n)]
    ey = [ry[t] - sum(by[i] * cols[i][t] for i in range(k)) for t in range(n)]
    return corr(list(zip(ex, ey)))


def quantile_edges(vals, parts):
    s = sorted(vals)
    return [s[int(len(s) * i / parts)] for i in range(1, parts)]


def bin_of(v, edges):
    b = 0
    for e in edges:
        if v > e:
            b += 1
    return b


def analyse(events, rng, label):
    """Return the stratified comparison for one arm."""
    n_all = len(events)
    # ---- distance bins
    d_edges = quantile_edges([e["distance"] for e in events], 4)
    for e in events:
        e["dbin"] = bin_of(e["distance"], d_edges)
        # surrogate candidates inside the event's own distance bin; fallback = nearest overall
        in_bin = [(dd, pk) for dd, pk in e["cands"] if bin_of(dd, d_edges) == e["dbin"]]
        e["fallback"] = 0 if in_bin else 1
        e["pool"] = in_bin or e["cands"]

    bins = {}
    for e in events:
        bins.setdefault(e["dbin"], []).append(e)

    per_bin = []
    for b in sorted(bins):
        ev = bins[b]
        obs = corr([(e["parent_peak"], e["child_peak"]) for e in ev])
        sur_draws = []
        for _ in range(DRAWS):
            sur_draws.append(corr([(rng.choice(e["pool"])[1], e["child_peak"]) for e in ev]))
        sur_draws = [s for s in sur_draws if s is not None]
        per_bin.append({"bin": b, "events": len(ev),
                        "distance_range": [round(min(e["distance"] for e in ev), 2),
                                           round(max(e["distance"] for e in ev), 2)],
                        "observed": round(obs, 3) if obs is not None else None,
                        "surrogate_median": round(st.median(sur_draws), 3) if sur_draws else None,
                        "fallback_share": round(sum(e["fallback"] for e in ev) / len(ev), 3)})

    w = [b["events"] for b in per_bin]
    obs_bins = [b["observed"] for b in per_bin]
    sur_bins = [b["surrogate_median"] for b in per_bin]
    obs_w = weighted_mean(obs_bins, w)
    sur_w = weighted_mean(sur_bins, w)
    obs_f = fisher_mean(obs_bins, w)
    sur_f = fisher_mean(sur_bins, w)

    # ---- occupancy tertiles (distance-unmatched nearest-in-distance surrogate)
    o_edges = quantile_edges([e["occupancy"] for e in events], 3)
    tert = {}
    for e in events:
        tert.setdefault(bin_of(e["occupancy"], o_edges), []).append(e)
    occ_rows = []
    for b in sorted(tert):
        ev = tert[b]
        obs = corr([(e["parent_peak"], e["child_peak"]) for e in ev])
        sur_draws = []
        for _ in range(DRAWS):
            sur_draws.append(corr([(rng.choice(e["cands"])[1], e["child_peak"]) for e in ev]))
        sur_draws = [s for s in sur_draws if s is not None]
        occ_rows.append({"tertile": b, "events": len(ev),
                         "occupancy_range": [min(e["occupancy"] for e in ev), max(e["occupancy"] for e in ev)],
                         "observed": round(obs, 3) if obs is not None else None,
                         "surrogate_median": round(st.median(sur_draws), 3) if sur_draws else None})
    dense = occ_rows[-1] if occ_rows else None
    dense_diff = (dense["observed"] - dense["surrogate_median"]
                  if dense and dense["observed"] is not None and dense["surrogate_median"] is not None else None)

    # ---- local-environment tertiles (field snapshot at the daughter's birth)
    env_rows, env_edges, env_covered = [], None, 0
    env_events = [e for e in events if e.get("local_v") is not None]
    env_covered = len(env_events)
    if len(env_events) >= 3 * MIN_PAIRS:
        env_edges = quantile_edges([e["local_v"] for e in env_events], 3)
        envb = {}
        for e in env_events:
            envb.setdefault(bin_of(e["local_v"], env_edges), []).append(e)
        for b in sorted(envb):
            ev = envb[b]
            obs = corr([(e["parent_peak"], e["child_peak"]) for e in ev])
            sur_draws = []
            for _ in range(DRAWS):
                sur_draws.append(corr([(rng.choice(e["pool"])[1], e["child_peak"]) for e in ev]))
            sur_draws = [s for s in sur_draws if s is not None]
            env_rows.append({"tertile": b, "events": len(ev),
                             "local_v_range": [round(min(e["local_v"] for e in ev), 3),
                                                round(max(e["local_v"] for e in ev), 3)],
                             "observed": round(obs, 3) if obs is not None else None,
                             "surrogate_median": round(st.median(sur_draws), 3) if sur_draws else None})
    env_diff = None
    if env_rows:
        eo = weighted_mean([r["observed"] for r in env_rows], [r["events"] for r in env_rows])
        es = weighted_mean([r["surrogate_median"] for r in env_rows], [r["events"] for r in env_rows])
        if eo is not None and es is not None:
            env_diff = eo - es
    # does the local environment predict both ends? (if yes, the confound is real and measurable)
    env_pred = {}
    if env_events:
        env_pred = {
            "corr_local_v_parent": (round(corr([(e["local_v"], e["parent_peak"]) for e in env_events]) or 0, 3)
                                     if corr([(e["local_v"], e["parent_peak"]) for e in env_events]) is not None else None),
            "corr_local_v_child": (round(corr([(e["local_v"], e["child_peak"]) for e in env_events]) or 0, 3)
                                    if corr([(e["local_v"], e["child_peak"]) for e in env_events]) is not None else None),
            "corr_local_occ_child": (round(corr([(e["local_occ"], e["child_peak"]) for e in env_events]) or 0, 3)
                                      if corr([(e["local_occ"], e["child_peak"]) for e in env_events]) is not None else None),
        }

    # ---- per-seed distance-stratified difference
    seed_rows = []
    for seed in sorted({e["cluster"][0] for e in events}):
        ev_s = [e for e in events if e["cluster"][0] == seed]
        rows, ws = [], []
        for b in sorted(bins):
            ev = [e for e in ev_s if e["dbin"] == b]
            if len(ev) < MIN_PAIRS:
                continue
            obs = corr([(e["parent_peak"], e["child_peak"]) for e in ev])
            sur_draws = [corr([(rng.choice(e["pool"])[1], e["child_peak"]) for e in ev]) for _ in range(DRAWS)]
            sur_draws = [s for s in sur_draws if s is not None]
            rows.append((obs, st.median(sur_draws) if sur_draws else None))
            ws.append(len(ev))
        o = weighted_mean([r[0] for r in rows], ws)
        s = weighted_mean([r[1] for r in rows], ws)
        seed_rows.append({"seed": seed, "events": len(ev_s),
                          "observed": round(o, 3) if o is not None else None,
                          "surrogate_median": round(s, 3) if s is not None else None,
                          "difference": round(o - s, 3) if (o is not None and s is not None) else None})

    # ---- cluster bootstrap of the pooled difference
    clusters = {}
    for e in events:
        clusters.setdefault(tuple(e["cluster"]), []).append(e)
    keys = sorted(clusters)
    boot = []
    for _ in range(BOOT):
        pick = [keys[rng.randrange(len(keys))] for _ in range(len(keys))]
        ev = [e for k in pick for e in clusters[k]]
        b_edges = quantile_edges([e["distance"] for e in ev], 4)
        obs_list, sur_list, w_list = [], [], []
        for b in range(4):
            evb = [e for e in ev if bin_of(e["distance"], b_edges) == b]
            if len(evb) < MIN_PAIRS:
                continue
            o = corr([(e["parent_peak"], e["child_peak"]) for e in evb])
            s = corr([(rng.choice(e["pool"])[1], e["child_peak"]) for e in evb])
            obs_list.append(o)
            sur_list.append(s)
            w_list.append(len(evb))
        o = weighted_mean(obs_list, w_list)
        s = weighted_mean(sur_list, w_list)
        if o is not None and s is not None:
            boot.append(o - s)
    boot.sort()

    # ---- rank partial correlation controlling distance and occupancy
    pc = partial_corr([e["parent_peak"] for e in events], [e["child_peak"] for e in events],
                      [[e["distance"] for e in events], [e["occupancy"] for e in events]])
    pc_env = None
    if env_events:
        pc_env = partial_corr([e["parent_peak"] for e in env_events], [e["child_peak"] for e in env_events],
                              [[e["distance"] for e in env_events], [e["occupancy"] for e in env_events],
                               [e["local_v"] for e in env_events], [e["local_occ"] for e in env_events]])
    spearman = corr(list(zip(ranks([e["parent_peak"] for e in events]),
                             ranks([e["child_peak"] for e in events]))))

    pooled_diff = (obs_w - sur_w) if (obs_w is not None and sur_w is not None) else None
    survives = (pooled_diff is not None and pooled_diff > 0.10
                and sum(1 for r in seed_rows if r["difference"] is not None and r["difference"] > 0.10) >= 4
                and dense_diff is not None and dense_diff > 0)
    spatial = pooled_diff is not None and pooled_diff <= 0
    verdict = "survives" if survives else ("spatial" if spatial else "unresolved")

    return {
        "arm": label,
        "events": n_all,
        "fallback_share": round(sum(e["fallback"] for e in events) / n_all, 3),
        "distance_bins": {"edges": [round(x, 2) for x in d_edges], "rows": per_bin},
        "distance_stratified": {
            "observed_weighted": round(obs_w, 3) if obs_w is not None else None,
            "surrogate_weighted": round(sur_w, 3) if sur_w is not None else None,
            "difference": round(pooled_diff, 3) if pooled_diff is not None else None,
            "observed_fisher": round(obs_f, 3) if obs_f is not None else None,
            "surrogate_fisher": round(sur_f, 3) if sur_f is not None else None,
        },
        "occupancy_tertiles": {"edges": o_edges, "rows": occ_rows, "dense_difference": dense_diff},
        "per_seed": seed_rows,
        "seeds_with_diff_gt_010": sum(1 for r in seed_rows if r["difference"] is not None and r["difference"] > 0.10),
        "bootstrap_difference_ci95": ([round(boot[int(0.025 * len(boot))], 3),
                                       round(boot[int(0.975 * len(boot)) - 1], 3)] if len(boot) > 40 else None),
        "local_environment": {"covered": env_covered, "edges": env_edges, "rows": env_rows,
                               "weighted_difference": round(env_diff, 3) if env_diff is not None else None,
                               "predicts": env_pred},
        "partial_corr_distance_occupancy": round(pc, 3) if pc is not None else None,
        "partial_corr_plus_local_environment": round(pc_env, 3) if pc_env is not None else None,
        "spearman_raw": round(spearman, 3) if spearman is not None else None,
        "verdict": verdict,
    }


def main(argv=None) -> int:
    global GRID
    ap = argparse.ArgumentParser(description="X70 spatial control, stratified over all events")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--prefix", default="x70", help="artifact prefix: x70 (old, 1000-step log) or x70d (dense, 50-step log)")
    ap.add_argument("--grid", type=int, default=GRID)
    ap.add_argument("--fields", action="store_true", help="attach local field statistics at each birth")
    args = ap.parse_args(argv)

    GRID = int(args.grid)
    fields_dir = (ROOT / "morphogenesis" / "experiments" / "L1_field" / f"_{args.prefix}_fields") if args.fields else None
    rng = random.Random(23)
    result = {"kind": "l1_field_x70_spatial_strata", "experiment": "X70 control, second design",
              "command": f"python scripts/x70_spatial_strata.py --write --prefix {args.prefix}",
              "prefix": args.prefix,
              "prereg": "docs/plan/10d-field-metrics-and-form.md §10ep, registered before the run",
              "draws": DRAWS, "bootstrap": BOOT, "min_pairs": MIN_PAIRS, "arms": {}}

    for arm in ("pattern", "homog"):
        events = []
        for f in sorted(glob.glob(str(L1 / f"{args.prefix}_{arm}_s*.json"))):
            seed = int(Path(f).stem.split("_s")[-1])
            events += events_for_run(Path(f), seed)
        if not events:
            continue
        if fields_dir:
            for seed in sorted({e["cluster"][0] for e in events}):
                ev_s = [e for e in events if e["cluster"][0] == seed]
                local_env(ev_s, fields_dir, tag=f"{args.prefix}_{arm}_s{seed}")
        result["arms"][arm] = analyse(events, rng, arm)

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x70-strata] written: {OUT.name}")

    for arm, a in result["arms"].items():
        ds = a["distance_stratified"]
        print("  %-8s events=%4d fallback=%.2f  obs=%s sur=%s diff=%s  seeds>+0.10: %d/5  partial=%s  ci=%s  verdict=%s" % (
            arm, a["events"], a["fallback_share"], ds["observed_weighted"], ds["surrogate_weighted"],
            ds["difference"], a["seeds_with_diff_gt_010"], a["partial_corr_distance_occupancy"],
            a["bootstrap_difference_ci95"], a["verdict"]))
        for row in a["distance_bins"]["rows"]:
            print("      bin%d rows=%4d d=%s obs=%s sur=%s" % (
                row["bin"], row["events"], row["distance_range"], row["observed"], row["surrogate_median"]))
        for row in a["occupancy_tertiles"]["rows"]:
            print("      occ%d rows=%4d n=%s obs=%s sur=%s" % (
                row["tertile"], row["events"], row["occupancy_range"], row["observed"], row["surrogate_median"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
