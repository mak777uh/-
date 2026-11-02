"""x114_analyse.py — X114: is the generation-rate advantage an artefact of the horizon?

Equal-window test: each sister branch is measured only inside a window of W = 3 000 steps from her own first appearance, so truncation no longer
differs between the two branches of a pair. Plan: reports/2026-11-03-x114-window-plan.md.

    python scripts/x114_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from compact_world import world_from_compact  # noqa: E402
from x113_analyse import depth_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x114_window.json"

CELLS = {"f030": 0.030, "f040": 0.040}
WINDOW = 3000
MIN_PAIRS = 300
HEREDITY_FLOOR = 0.35
RESOLUTION = 0.30
BOOTSTRAP = 2000
X113_MEDIAN_DEPTH = 3.0


def windowed_depth(children: dict[int, list[int]], first: dict[int, int], uid: int, t0: int, w: int) -> int:
    """Generations reachable inside [t0, t0 + w], counting only descendants born inside the window."""
    best = 0
    stack = [(uid, 0)]
    while stack:
        node, depth = stack.pop()
        for kid in children.get(node, []):
            birth = first.get(kid)
            if birth is None or birth > t0 + w:
                continue
            d = depth + 1
            best = max(best, d)
            stack.append((kid, d))
    return best


def bootstrap_ci(vals, seed=114):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 3), round(means[int(0.975 * BOOTSTRAP)], 3)]


def cell_stats(flow: float) -> dict:
    heredity, depth_all, depth_win = [], [], []
    rate_diff, depth_diff = [], []
    exact_pairs = 0
    for path in sorted(L1.glob("x108_f030_*.compact.json" if abs(flow - 0.030) < 1e-9 else "x108_f040_*.compact.json")):
        w = world_from_compact(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        first = {uid: int(info["step"]) for uid, info in w["first"].items()}
        memo: dict[int, int] = {}
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for uid in list(children):
            t0 = first.get(uid)
            if t0 is None:
                continue
            d_all = depth_of(children, uid, memo)
            d_w = windowed_depth(children, first, uid, t0, WINDOW)
            depth_all.append(d_all)
            depth_win.append(d_w)
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    ta, tb = first.get(a), first.get(b)
                    if ta is None or tb is None:
                        continue
                    da = windowed_depth(children, first, a, ta, WINDOW)
                    db = windowed_depth(children, first, b, tb, WINDOW)
                    if ta + WINDOW >= max(first.values()) or tb + WINDOW >= max(first.values()):
                        exact_pairs += 1
                    big = w["peak"][a]["area"] >= w["peak"][b]["area"]
                    d_diff = (da - db) if big else (db - da)
                    depth_diff.append(d_diff)
                    rate_diff.append(d_diff / WINDOW * 1000.0)
    return {
        "pairs_heredity": len(heredity),
        "rho_heredity": round(spearman([p[0] for p in heredity], [p[1] for p in heredity]), 3) if heredity else None,
        "median_depth_all": st.median(depth_all) if depth_all else None,
        "median_depth_window": st.median(depth_win) if depth_win else None,
        "sister_pairs": len(rate_diff),
        "window_exact": exact_pairs,
        "depth_diff_mean": round(st.mean(depth_diff), 3) if depth_diff else None,
        "rate_diff_mean": round(st.mean(rate_diff), 3) if rate_diff else None,
        "rate_diff_ci": bootstrap_ci(rate_diff),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X114 equal-window test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["sister_pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['sister_pairs']} usable sister pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["median_depth_window"] is None or c["median_depth_all"] is None or c["median_depth_window"] >= c["median_depth_all"]:
            bad.append(f"{tag}: the window did not lower median depth ({c['median_depth_window']} vs {c['median_depth_all']})")
    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        survives = (lat["rate_diff_ci"] and lat["rate_diff_ci"][0] > 0 and maz["rate_diff_ci"] and maz["rate_diff_ci"][0] > 0)
        gone = all((c["rate_diff_ci"] and c["rate_diff_ci"][0] <= 0 <= c["rate_diff_ci"][1]) for c in (lat, maz))
        if survives:
            verdict = (f"the advantage survives the equal window: the larger sister gains {lat['rate_diff_mean']} generations per 1 000 "
                       f"windowed steps (CI {lat['rate_diff_ci']}) and {maz['rate_diff_mean']} in the maze (CI {maz['rate_diff_ci']})")
        elif gone:
            verdict = (f"the advantage was the horizon: with equal windows the contrast is {lat['rate_diff_mean']} generations per 1 000 "
                       f"steps (CI {lat['rate_diff_ci']}) and {maz['rate_diff_mean']} (CI {maz['rate_diff_ci']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['rate_diff_mean']} (CI {lat['rate_diff_ci']}), maze {maz['rate_diff_mean']} "
                       f"(CI {maz['rate_diff_ci']})")
        verdict += f"; windowed median depth {lat['median_depth_window']} against whole-run {lat['median_depth_all']}"

    res = {
        "kind": "l1_field_x114_window",
        "experiment": "X114",
        "command": "python scripts/x114_analyse.py --write",
        "prereg": "reports/2026-11-03-x114-window-plan.md",
        "window_steps": WINDOW,
        "readout": ("paired sister contrast in generations reached inside a fixed 3 000-step window per branch, and the same as a rate per "
                    "1 000 windowed steps"),
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x114] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['sister_pairs']} heredity={c['rho_heredity']} median depth {c['median_depth_window']} "
              f"(whole-run {c['median_depth_all']}) rate contrast={c['rate_diff_mean']} (CI {c['rate_diff_ci']}) "
              f"depth contrast={c['depth_diff_mean']} exact windows={c['window_exact']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
