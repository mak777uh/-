"""x155_analyse.py — heredity of the field's trait: is it the medium's or the copying rule's?

Reconstructs (parent, daughter) pairs of `s` from the full logs (`uid_pairs` + `components_log`), reproduces the
artifact's stored `selection.inheritability_r` as a validity control, and reports: the slope with a cluster bootstrap,
a shuffled-parent null, the division-rate partial, and the horizon share of variance between lineages.

Plan: reports/2026-11-03-x155-heredity-plan.md

Run:
    python scripts/x155_analyse.py --cells x108_f030,x108_f040 --write
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x155_heredity.json"

RNG = np.random.default_rng(20261103)


def pearson(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def ols_slope(x: np.ndarray, y: np.ndarray) -> float | None:
    vx = float(np.var(x))
    if len(x) < 3 or vx == 0:
        return None
    return float(np.cov(x, y, bias=True)[0, 1] / vx)


def partial_slope(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float | None:
    """Slope of y on x, controlling linearly for z."""
    if len(x) < 5:
        return None
    A = np.column_stack([np.ones_like(x), x, z])
    try:
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    return float(coef[1])


def load_runs(prefix: str) -> list[dict]:
    files = sorted(p for p in L1.glob(f"{prefix}_s*.json") if ".compact" not in p.name)
    runs = []
    for p in files:
        runs.append(json.loads(p.read_text(encoding="utf-8")))
    return runs


def pairs_of(run: dict) -> tuple[list[tuple[int, int]], dict[int, int]]:
    pairs = [tuple(int(v) for v in pc) for pc in (run.get("uid_pairs") or [])]
    step_of_uid: dict[int, dict[int, float]] = {}
    for row in run.get("series") or []:
        step = int(row.get("step", 0))
        for comp in row.get("components_log") or []:
            step_of_uid.setdefault(int(comp["uid"]), {})[step] = float(comp.get("s", 0.0))
    return pairs, step_of_uid


def reconstruct(run: dict) -> dict:
    """Pairs are (parent, daughter) but with `--split-new-uid` the parent's uid ends at the split, so the two are never
    logged together: the parent is read at its LAST logged step before the daughter appears, the daughter at her FIRST."""
    pairs, uid_steps = pairs_of(run)
    xs, ys, parents, kids, steps_used = [], [], [], [], []
    for p, c in pairs:
        sp, sc = uid_steps.get(p), uid_steps.get(c)
        if not sp or not sc:
            continue
        t_c = min(sc)
        before = [t for t in sp if t <= t_c]
        if not before:
            continue
        t_p = max(before)
        xs.append(sp[t_p])
        ys.append(sc[t_c])
        parents.append(p)
        kids.append(c)
        steps_used.append((t_p, t_c))
    xs_a = np.asarray(xs, dtype=float)
    ys_a = np.asarray(ys, dtype=float)
    stored = (run.get("selection") or {}).get("inheritability_r")
    return {
        "id": run.get("params", {}).get("seed"),
        "n_pairs": len(xs),
        "r": pearson(xs_a, ys_a),
        "r_stored": stored,
        "slope": ols_slope(xs_a, ys_a),
        "xs": xs_a,
        "ys": ys_a,
        "parents": parents,
        "n_pairs_total": len(pairs),
        "horizon": horizon_variance(run, pairs),
    }


def horizon_variance(run: dict, pairs: list[tuple[int, int]]) -> dict:
    """Share of trait variance at the horizon that sits between lineage roots (union-find over uid_pairs)."""
    parent_of: dict[int, int] = {}
    for p, c in pairs:
        parent_of.setdefault(c, p)

    def root(u: int) -> int:
        seen = set()
        while u in parent_of and u not in seen:
            seen.add(u)
            u = parent_of[u]
        return u

    rows = run.get("series") or []
    if not rows:
        return {}
    last = max(rows, key=lambda r: int(r.get("step", 0)))
    comps = last.get("components_log") or []
    s = np.asarray([float(c.get("s", 0.0)) for c in comps], dtype=float)
    g = [root(int(c["uid"])) for c in comps]
    if len(s) < 3:
        return {"n_components": int(len(s))}
    total = float(np.sum((s - s.mean()) ** 2))
    within = 0.0
    groups = defaultdict(list)
    for val, key in zip(s, g):
        groups[key].append(val)
    for vals in groups.values():
        arr = np.asarray(vals)
        within += float(np.sum((arr - arr.mean()) ** 2))
    return {
        "n_components": int(len(s)),
        "n_lineages": len(groups),
        "v_total": total / len(s),
        "h2_between": (1.0 - within / total) if total > 0 else None,
    }


def bootstrap_slope(recs: list[dict], n_boot: int = 2000) -> list[float]:
    """Cluster bootstrap over parent uids, pooled across runs."""
    clusters: dict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for r in recs:
        for x, y, p in zip(r["xs"], r["ys"], r["parents"]):
            clusters[(r.get("id") or 0, p)].append((float(x), float(y)))
    keys = list(clusters)
    if len(keys) < 5:
        return []
    out = []
    for _ in range(n_boot):
        pick = RNG.integers(0, len(keys), len(keys))
        xs, ys = [], []
        for i in pick:
            for x, y in clusters[keys[i]]:
                xs.append(x)
                ys.append(y)
        b = ols_slope(np.asarray(xs), np.asarray(ys))
        if b is not None:
            out.append(b)
    return out


def shuffled_null(recs: list[dict], n_perm: int = 1000) -> dict:
    obs = ols_slope(np.concatenate([r["xs"] for r in recs]), np.concatenate([r["ys"] for r in recs]))
    if obs is None:
        return {}
    null = []
    for _ in range(n_perm):
        xs, ys = [], []
        for r in recs:
            perm = RNG.permutation(len(r["xs"]))
            xs.append(r["xs"][perm])
            ys.append(r["ys"])
        b = ols_slope(np.concatenate(xs), np.concatenate(ys))
        if b is not None:
            null.append(b)
    null_a = np.asarray(null)
    p = float((np.sum(null_a >= obs) + 1) / (len(null_a) + 1))
    return {"observed": obs, "null_mean": float(null_a.mean()), "null_sd": float(null_a.std()), "p_one_sided": p}


def daughters_count(recs: list[dict]) -> np.ndarray:
    out = []
    for r in recs:
        cnt = Counter(r["parents"])
        out.extend(float(cnt[p]) for p in r["parents"])
    return np.asarray(out)


def ablation_summary(prefix: str) -> dict:
    """The mutation-off arm: with `--mutation 0` the trait is constant (s = 1.0, sd 0), so `r` and the slope are
    undefined. That degenerate outcome is the strongest form of perfect transmission and is reported as such, with
    the shares of exactly-equal pairs rather than as a coefficient."""
    runs = load_runs(prefix)
    sds, rs, splits, eq = [], [], [], []
    for run in runs:
        sel = run.get("selection") or {}
        sds.append(sel.get("s_sd_between_last"))
        rs.append(sel.get("inheritability_r"))
        splits.append(sel.get("splits"))
        pairs, uid_steps = pairs_of(run)
        same = tot = 0
        for p, c in pairs:
            sp, sc = uid_steps.get(p), uid_steps.get(c)
            if not sp or not sc:
                continue
            t_c = min(sc)
            before = [t for t in sp if t <= t_c]
            if not before:
                continue
            tot += 1
            if abs(sp[max(before)] - sc[t_c]) <= 1e-12:
                same += 1
        eq.append(same / tot if tot else None)
    return {
        "cell": prefix,
        "worlds": len(runs),
        "s_sd_between_last": [v for v in sds if v is not None],
        "r": None if all(v is None for v in rs) else rs,
        "splits": splits,
        "identical_pair_share": eq,
    }


def analyse(cell: str) -> dict:
    runs = load_runs(cell)
    recs = []
    dropped = []
    for run in runs:
        rec = reconstruct(run)
        if rec["n_pairs"] < 10 or rec["r"] is None:
            dropped.append({"seed": rec["id"], "n_pairs": rec["n_pairs"]})
            continue
        recs.append(rec)
    if not recs:
        return {"cell": cell, "worlds": 0, "dropped": dropped}
    all_x = np.concatenate([r["xs"] for r in recs])
    all_y = np.concatenate([r["ys"] for r in recs])
    boot = bootstrap_slope(recs)
    boot_a = np.asarray(boot)
    stored = [r["r_stored"] for r in recs if r["r_stored"] is not None]
    per_world = [r["r"] for r in recs]
    # The stored coefficient is a per-world number, so the control compares like with like: the mean over worlds,
    # not a pooled r (pooling across worlds adds between-world variance and inflates r by ~0.03).
    pooled = pearson(all_x, all_y)
    mean_world_r = float(np.mean(per_world)) if per_world else None
    mean_stored = float(np.mean(stored)) if stored else None
    h2 = [r["horizon"].get("h2_between") for r in recs if r["horizon"].get("h2_between") is not None]
    return {
        "cell": cell,
        "worlds": len(recs),
        "dropped": dropped,
        "pairs": int(len(all_x)),
        "pairs_total": int(sum(r["n_pairs_total"] for r in recs)),
        "r": pooled,
        "r_stored_mean": mean_stored,
        "r_per_world_mean": mean_world_r,
        "r_delta_vs_stored": (mean_world_r - mean_stored) if (mean_world_r is not None and mean_stored is not None) else None,
        "r_pooled_less_world_mean": (pooled - mean_world_r) if (pooled is not None and mean_world_r is not None) else None,
        "slope": ols_slope(all_x, all_y),
        "slope_ci": [float(np.percentile(boot_a, 2.5)), float(np.percentile(boot_a, 97.5))] if len(boot_a) else None,
        "slope_partial_given_daughters": partial_slope(all_x, all_y, daughters_count(recs)),
        "residual_sd": float(np.std(all_y - all_x)),
        "shuffle_null": shuffled_null(recs),
        "h2_between_mean": float(np.mean(h2)) if h2 else None,
        "h2_between_per_world": h2,
        "per_world_slope": [r["slope"] for r in recs],
        "per_world_r": [r["r"] for r in recs],
    }


def verdict(cells: list[dict], ablation: dict | None) -> dict:
    out = {"rule": "reports/2026-11-03-x155-heredity-plan.md", "criteria": {}}
    ok_validity = all(
        c.get("r_delta_vs_stored") is not None and abs(c["r_delta_vs_stored"]) <= 0.02 for c in cells if c.get("pairs")
    )
    out["criteria"]["validity_control"] = bool(ok_validity)
    sl = [c.get("slope") for c in cells if c.get("slope") is not None]
    if sl:
        out["criteria"]["slope_positive"] = bool(all(s > 0 for s in sl))
    for c in cells:
        ci = c.get("slope_ci") or []
        if ci:
            out["criteria"][f"ci_excludes_zero_{c['cell']}"] = bool(ci[0] > 0 or ci[1] < 0)
        null = c.get("shuffle_null") or {}
        if "p_one_sided" in null:
            out["criteria"][f"null_rejected_{c['cell']}"] = bool(null["p_one_sided"] < 0.05)
        ps = c.get("slope_partial_given_daughters")
        if ps is not None:
            out["criteria"][f"partial_positive_{c['cell']}"] = bool(ps > 0)
    if ablation:
        sds = ablation.get("s_sd_between_last") or []
        eq = [v for v in (ablation.get("identical_pair_share") or []) if v is not None]
        degenerate = bool(sds) and all(v <= 1e-12 for v in sds) and eq and min(eq) >= 0.99
        out["criteria"]["ablation_degenerate_no_variance"] = degenerate
        out["criteria"]["ablation_near_perfect"] = bool(
            degenerate
            or ((ablation.get("r") or 0) >= 0.99 and (ablation.get("slope") or 0) >= 0.95)
        )
    resid = [c.get("residual_sd") for c in cells if c.get("residual_sd") is not None]
    if resid:
        out["criteria"]["residual_matches_sigma"] = bool(all(0.075 <= r <= 0.30 for r in resid))
    c = out["criteria"]
    validity = c.get("validity_control", False)
    if not validity:
        out["verdict"] = "VOID: the reconstruction does not reproduce the stored coefficient"
    elif c.get("ablation_near_perfect"):
        out["verdict"] = "HEREDITY IS THE RULE"
    elif all(v for k, v in c.items() if k.startswith(("ci_excludes_zero", "null_rejected", "partial_positive"))):
        out["verdict"] = "HEREDITY IS PARTLY THE MEDIUM"
    elif any(not v for k, v in c.items() if k.startswith(("ci_excludes_zero", "null_rejected", "partial_positive"))):
        out["verdict"] = "NO MEASURABLE HEREDITY BEYOND THE RULE"
    else:
        out["verdict"] = "UNDETERMINED (no ablation arm)"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X155: heredity of the field's trait")
    ap.add_argument("--cells", default="x108_f030,x108_f040")
    ap.add_argument("--ablation", default="", help="comma-separated prefixes of the mutation-off arm")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = [analyse(c.strip()) for c in args.cells.split(",") if c.strip()]
    abl = [ablation_summary(c.strip()) for c in args.ablation.split(",") if c.strip()] if args.ablation else None
    payload = {
        "kind": "l1_field_x155_heredity",
        "plan": "reports/2026-11-03-x155-heredity-plan.md",
        "cells": cells,
        "ablation": abl,
        "verdict": verdict(cells, abl[0] if abl else None),
    }
    for c in cells:
        print(f"[x155] {c['cell']}: worlds {c.get('worlds')} pairs {c.get('pairs')} "
              f"r_per_world {c.get('r_per_world_mean')} stored {c.get('r_stored_mean')} "
              f"delta {c.get('r_delta_vs_stored')} slope {c.get('slope')} ci {c.get('slope_ci')}")
    if abl:
        for c in abl:
            print(f"[x155] ablation {c['cell']}: worlds {c['worlds']} r {c['r']} "
                  f"sd_between {c['s_sd_between_last']} identical {c['identical_pair_share']}")
    print("[x155] verdict:", payload["verdict"]["verdict"])
    if args.write:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("[x155] wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
