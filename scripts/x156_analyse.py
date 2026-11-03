"""x156_analyse.py — is a shape measured from the field itself inherited?

Traits per component, all read from the same twenty runs (see reports/2026-11-04-x156-shape-heredity-plan.md):

    s       the assigned trait, the positive control (X155: slope 0.98)
    area    geometric control (a daughter is part of its parent, expected slope near 0.5)
    elong   elongation from second moments, the question
    width   minor-axis width in cells, the question

Pairs are reconstructed exactly as in X155: `--split-new-uid` means a parent and its daughter are never logged on the
same step, so the parent is read at its last logged step before the daughter's first, the daughter at her first. The
"delay" analysis reads the daughter 1, 2 or 3 logged steps after her first appearance, which is what separates a copied
number (slope independent of delay) from a shape that relaxes towards the medium's typical shape (slope decays with
delay).

Run:
    python scripts/x156_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x156_shape_heredity.json"

RNG = np.random.default_rng(20261104)
TRAITS = {"s": ("s", False), "area": ("area", False), "elong": ("elong", False), "width": ("width", False),
          "log_elong": ("elong", True), "log_width": ("width", True)}


def ols_slope(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3:
        return None
    vx = float(np.var(x))
    if vx == 0:
        return None
    return float(np.cov(x, y, bias=True)[0, 1] / vx)


def pearson(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3 or float(np.std(x)) == 0 or float(np.std(y)) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def partial_slope(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float | None:
    if len(x) < 5:
        return None
    A = np.column_stack([np.ones_like(x), x, z])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[1])


def load_cell(cell: str) -> list[dict]:
    files = sorted(L1.glob(f"x156_shape_{cell}_s*.json"))
    return [json.loads(p.read_text(encoding="utf-8")) for p in files]


def index_run(run: dict) -> dict[int, dict[int, dict]]:
    """uid -> step -> row, for every trait we read."""
    out: dict[int, dict[int, dict]] = {}
    for row in run.get("series") or []:
        step = int(row.get("step", 0))
        for comp in row.get("components_log") or []:
            uid = int(comp["uid"])
            out.setdefault(uid, {})[step] = comp
    return out


def pairs_of(run: dict) -> list[tuple[int, int]]:
    return [tuple(int(v) for v in pc) for pc in (run.get("uid_pairs") or [])]


def collect(runs: list[dict], trait: str, delay: int = 0, log: bool = False) -> dict:
    """Flat arrays of parent and daughter values for one trait and one daughter-read delay."""
    xs, ys, cluster, world, log_area = [], [], [], [], []
    n_total = 0
    for run in runs:
        idx = index_run(run)
        wid = int((run.get("params") or {}).get("seed") or 0)
        for p, c in pairs_of(run):
            n_total += 1
            sp, sc = idx.get(p), idx.get(c)
            if not sp or not sc:
                continue
            steps_c = sorted(sc)
            if delay >= len(steps_c):
                continue
            t_c = steps_c[delay]
            before = [t for t in sp if t <= t_c]
            if not before:
                continue
            t_p = max(before)
            row_p, row_c = sp[t_p], sc[t_c]
            vp, vc = row_p.get(trait), row_c.get(trait)
            if vp is None or vc is None:
                continue
            # amendment 1: shape traits only where the second moment is meaningful
            if trait in ("elong", "width"):
                pa, ca = row_p.get("area"), row_c.get("area")
                pw, cw = row_p.get("width"), row_c.get("width")
                if not pa or not ca or pa < 10 or ca < 10 or pw is None or cw is None or pw < 1.0 or cw < 1.0:
                    continue
            if log:
                if vp <= 0 or vc <= 0:
                    continue
                vp, vc = math.log(vp), math.log(vc)
            xs.append(float(vp))
            ys.append(float(vc))
            log_area.append(math.log1p(float(row_p.get("area") or 0.0)))
            cluster.append((wid, p))
            world.append(wid)
    return {"xs": np.asarray(xs, dtype=float), "ys": np.asarray(ys, dtype=float),
            "log_area": np.asarray(log_area, dtype=float),
            "cluster": cluster, "world": np.asarray(world), "pairs_total": n_total}


def cluster_bootstrap(block: dict, n_boot: int = 2000) -> list[float]:
    xs, ys, cluster = block["xs"], block["ys"], block["cluster"]
    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for i, key in enumerate(cluster):
        groups[key].append(i)
    keys = list(groups)
    if len(keys) < 5:
        return []
    out = []
    for _ in range(n_boot):
        pick = RNG.integers(0, len(keys), len(keys))
        sel = np.concatenate([groups[keys[i]] for i in pick])
        b = ols_slope(xs[sel], ys[sel])
        if b is not None:
            out.append(b)
    return out


def shuffled_null(block: dict, n_perm: int = 1000) -> dict:
    xs, ys, world = block["xs"], block["ys"], block["world"]
    obs = ols_slope(xs, ys)
    if obs is None:
        return {}
    null = []
    for _ in range(n_perm):
        perm = RNG.permutation(len(xs))
        b = ols_slope(xs[perm], ys)
        if b is not None:
            null.append(b)
    arr = np.asarray(null)
    return {"observed": obs, "null_mean": float(arr.mean()), "null_sd": float(arr.std()),
            "p_one_sided": float((np.sum(arr >= obs) + 1) / (len(arr) + 1))}


def summary(block: dict, boot) -> dict:
    xs, ys = block["xs"], block["ys"]
    slope = ols_slope(xs, ys)
    ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))] if boot else None
    return {
        "pairs": int(len(xs)),
        "pairs_total": int(block["pairs_total"]),
        "r": pearson(xs, ys),
        "slope": slope,
        "slope_ci": ci,
        "parent_mean": float(xs.mean()) if len(xs) else None,
        "parent_sd": float(xs.std()) if len(xs) else None,
        "daughter_mean": float(ys.mean()) if len(ys) else None,
        "daughter_sd": float(ys.std()) if len(ys) else None,
        "residual_sd": float(np.std(ys - (xs * slope if slope is not None else 0.0))) if slope is not None else None,
    }


def analyse_cell(cell: str, runs: list[dict]) -> dict:
    out = {"cell": cell, "runs": len(runs), "traits": {}}
    area_block = collect(runs, "area", 0)
    log_area_p = np.log1p(area_block["xs"])
    for name, (key, use_log) in TRAITS.items():
        block = collect(runs, key, 0, log=use_log)
        boot = cluster_bootstrap(block)
        row = summary(block, boot)
        row["shuffled_null"] = shuffled_null(block)
        if key != "area":
            row["partial_given_log_area"] = partial_slope(block["xs"], block["ys"], block["log_area"])
        else:
            row["partial_given_log_area"] = None
        delays = {}
        for delay in (0, 1, 2, 3):
            b = collect(runs, key, delay, log=use_log)
            if len(b["xs"]) >= 30:
                delays[str(delay)] = {"slope": ols_slope(b["xs"], b["ys"]), "pairs": int(len(b["xs"]))}
        row["by_delay"] = delays
        out["traits"][name] = row
    return out


def verdict(cells: dict) -> str:
    lines = []
    rows = []
    for cell, data in cells.items():
        t = data["traits"]
        s_slope = t["s"]["slope"]
        area_slope = t["area"]["slope"]
        e_slope = t["log_elong"]["slope"]
        w_slope = t["log_width"]["slope"]
        null_e = (t["log_elong"].get("shuffled_null") or {}).get("null_mean")
        rows.append(f"{cell}: s {s_slope:.3f}, area {area_slope:.3f}, elong {e_slope:.3f} "
                    f"(null {null_e if null_e is None else round(null_e, 3)}), width {w_slope:.3f}")
        if not (0.90 <= (s_slope or 0) <= 1.05):
            return "VOID: the positive control (the assigned trait s) is outside [0.90, 1.05]"
        if not (0.35 <= (area_slope or 0) <= 0.65):
            return "VOID: the geometric control (area) is outside [0.35, 0.65]"
        if (t["log_elong"].get("parent_sd") or 0) < 0.05:
            return "VOID: the shape readout has no variance"
    lines.extend(rows)
    e_slopes = [cells[c]["traits"]["log_elong"]["slope"] for c in cells]
    w_slopes = [cells[c]["traits"]["log_width"]["slope"] for c in cells]
    e_nulls = [(cells[c]["traits"]["log_elong"].get("shuffled_null") or {}).get("null_mean", 0.0) for c in cells]
    delay_drop = []
    for c in cells:
        by_delay = cells[c]["traits"]["log_elong"]["by_delay"]
        if "0" in by_delay and "3" in by_delay and by_delay["0"]["slope"] is not None and by_delay["3"]["slope"] is not None:
            delay_drop.append(by_delay["0"]["slope"] - by_delay["3"]["slope"])
    mean_e = float(np.mean(e_slopes))
    mean_w = float(np.mean(w_slopes))
    max_null = float(np.max(e_nulls))
    head = " | ".join(lines)
    # which aspect dominates inside each habitat, and does it swap?
    dominance = []
    for c in cells:
        e_row = cells[c]["traits"]["log_elong"]
        w_row = cells[c]["traits"]["log_width"]
        e_ci, w_ci = e_row.get("slope_ci") or [None, None], w_row.get("slope_ci") or [None, None]
        if None in e_ci or None in w_ci:
            dominance.append((c, None))
        elif e_ci[0] > w_ci[1]:
            dominance.append((c, "elong"))
        elif w_ci[0] > e_ci[1]:
            dominance.append((c, "width"))
        else:
            dominance.append((c, None))
    swap = len({d for _, d in dominance}) == 2 and all(d for _, d in dominance)
    if mean_e >= 0.70 and max_null < 0.30:
        body = (f"SHAPE IS INHERITED: elongation slope {mean_e:.3f} across habitats, width {mean_w:.3f}, "
                f"shuffled null at most {max_null:.3f}")
    elif mean_e >= 0.30 and delay_drop and float(np.max(delay_drop)) > 0.10:
        body = (f"SHAPE RELAXES: elongation slope {mean_e:.3f}, falling by up to {float(np.max(delay_drop)):.3f} "
                f"as the daughter ages; width {mean_w:.3f}")
    elif swap:
        body = ("SHAPE IS PARTIALLY TRANSMITTED, and the habitat decides which aspect: "
                + ", ".join(f"{c} {d}" for c, d in dominance)
                + f"; elongation {mean_e:.3f} and width {mean_w:.3f} on average, both far below the tracked trait's "
                f"1.0 and both unaffected by the daughter's age")
    elif mean_e >= 0.30:
        body = (f"SHAPE IS WEAKLY TRANSMITTED: elongation slope {mean_e:.3f}, width {mean_w:.3f}, "
                f"no measurable dependence on the daughter's age")
    else:
        body = (f"SHAPE IS NOT INHERITED: elongation slope {mean_e:.3f} (null {max_null:.3f}), width {mean_w:.3f}; "
                f"the only heritable quantity is the one the tracker writes")
    return f"{body}. Controls: {head}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X156 shape heredity")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--cells", default="f030,f040", help="comma-separated cells to analyse")
    args = ap.parse_args(argv)
    cells = {}
    for cell in [c.strip() for c in args.cells.split(",") if c.strip()]:
        runs = load_cell(cell)
        if not runs:
            print(f"[x156] no runs for {cell}")
            return 1
        cells[cell] = analyse_cell(cell, runs)
        t = cells[cell]["traits"]
        print(f"[x156] {cell}: runs {len(runs)}, pairs {t['s']['pairs']}, s {t['s']['slope']}, "
              f"area {t['area']['slope']}, elong {t['elong']['slope']}, width {t['width']['slope']}")
    out = {"kind": "l1_field_x156_shape_heredity", "experiment": "X156",
           "plan": "reports/2026-11-04-x156-shape-heredity-plan.md",
           "question": "is a shape measured from the field itself inherited across divisions?",
           "definitions": {
               "elong": "sqrt(l1/l2) from the second-moment matrix of the component's pixels; 1 = round",
               "width": "2*sqrt(l2) in cells, the minor-axis extent",
               "delay": "logged steps between the daughter's first appearance and the step at which she is read",
               "partial_given_log_area": "slope of the daughter on the parent, controlling linearly for log area",
           },
           "cells": cells,
           "series": "scripts/x156_series.py",
           "verdict": verdict(cells)}
    print(f"[x156] {out['verdict']}")
    if args.write:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[x156] written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
