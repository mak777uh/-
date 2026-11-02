"""x113c_analyse.py — X113c: faster propagation or more division events?

X113 measured a generation advantage (+1.479 / +2.213) with depth negatively correlated with lifetime. This normalises by lifetime: generations per
1 000 steps (speed) and generations per division (arithmetic). Same pairs, same controls.

Plan: reports/2026-11-03-x113b-depth-rate-plan.md.

    python scripts/x113b_analyse.py --write
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
from x102_analyse import world_data  # noqa: E402
from x113_analyse import depth_of, life_of, _subtree  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x113c_depth_rate.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
DEPTH_TOL = 0.15   # X113c: the filter may shift the contrast by up to 15 %, and the shift is printed
MIN_UIDS = 300
MIN_LIFE = 50.0
HEREDITY_FLOOR = 0.35
RESOLUTION = 0.10
BOOTSTRAP = 2000


def bootstrap_ci(vals, seed=1131):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 3), round(means[int(0.975 * BOOTSTRAP)], 3)]


def cell_stats(flow: float) -> dict:
    areas, rates, per_div, lifes = [], [], [], []
    rate_diff, perdiv_diff, depth_diff = [], [], []
    heredity = []
    excluded = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        memo: dict[int, int] = {}
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for uid in list(children):
            life = life_of(w, uid)
            if life < MIN_LIFE:
                excluded += 1
                continue
            depth = depth_of(children, uid, memo)
            sub = _subtree(children, uid, {})
            areas.append(w["peak"][uid]["area"])
            lifes.append(life)
            rates.append(depth / life * 1000.0)
            per_div.append(depth / sub if sub else 0.0)
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    la, lb = life_of(w, a), life_of(w, b)
                    if la < MIN_LIFE or lb < MIN_LIFE:
                        continue
                    da, db = depth_of(children, a, memo), depth_of(children, b, memo)
                    ra, rb = da / la * 1000.0, db / lb * 1000.0
                    sa, sb = _subtree(children, a, {}), _subtree(children, b, {})
                    pa, pb = (da / sa if sa else 0.0), (db / sb if sb else 0.0)
                    big = w["peak"][a]["area"] >= w["peak"][b]["area"]
                    rate_diff.append((ra - rb) if big else (rb - ra))
                    perdiv_diff.append((pa - pb) if big else (pb - pa))
                    depth_diff.append((da - db) if big else (db - da))
    return {
        "uids": len(areas), "excluded_short_life": excluded,
        "rho_heredity": round(spearman([p[0] for p in heredity], [p[1] for p in heredity]), 3) if heredity else None,
        "rho_area_rate": round(spearman(areas, rates), 3) if areas else None,
        "median_rate": round(st.median(rates), 3) if rates else None,
        "sister_pairs": len(rate_diff),
        "rate_diff_mean": round(st.mean(rate_diff), 3) if rate_diff else None,
        "rate_diff_ci": bootstrap_ci(rate_diff),
        "perdiv_diff_mean": round(st.mean(perdiv_diff), 3) if perdiv_diff else None,
        "perdiv_diff_ci": bootstrap_ci(perdiv_diff),
        "depth_diff_mean": round(st.mean(depth_diff), 3) if depth_diff else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X113b depth rate")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["uids"] < MIN_UIDS:
            bad.append(f"{tag}: {c['uids']} uids with a usable rate")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        ref = X113_DEPTH[CELLS[tag]]
        if c["depth_diff_mean"] is None or abs(c["depth_diff_mean"] - ref) > DEPTH_TOL * abs(ref):
            bad.append(f"{tag}: raw-depth contrast {c['depth_diff_mean']} misses X113's {ref} by more than {DEPTH_TOL:.0%}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        speed = (lat["rate_diff_ci"] and lat["rate_diff_ci"][0] > 0
                 and (lat["rho_area_rate"] or 0) >= 0.10 and (maz["rho_area_rate"] or 0) >= 0.10)
        nothing = ((lat["rate_diff_ci"] and lat["rate_diff_ci"][0] <= 0 <= lat["rate_diff_ci"][1])
                   or (abs(lat["rho_area_rate"] or 0) <= 0.05 and abs(maz["rho_area_rate"] or 0) <= 0.05))
        if speed:
            verdict = (f"size buys speed: the larger sister's line gains {lat['rate_diff_mean']} generations per 1 000 steps "
                       f"(CI {lat['rate_diff_ci']}) and rho(area, rate) is {lat['rho_area_rate']} / {maz['rho_area_rate']}")
        elif nothing:
            verdict = (f"the count was arithmetic: the rate contrast is {lat['rate_diff_mean']} generations per 1 000 steps "
                       f"(CI {lat['rate_diff_ci']}) and rho(area, rate) is {lat['rho_area_rate']} / {maz['rho_area_rate']}, while the raw "
                       f"depth advantage was +1.479 / +2.213")
        else:
            verdict = (f"mixed: rate contrast {lat['rate_diff_mean']} (CI {lat['rate_diff_ci']}), rho(area, rate) "
                       f"{lat['rho_area_rate']} / {maz['rho_area_rate']}; per-division contrast {lat['perdiv_diff_mean']} "
                       f"(CI {lat['perdiv_diff_ci']})")
        verdict += (f"; per-division contrast {lat['perdiv_diff_mean']} (CI {lat['perdiv_diff_ci']}) / "
                    f"{maz['perdiv_diff_mean']} (CI {maz['perdiv_diff_ci']})")

    res = {
        "kind": "l1_field_x113c_depth_rate",
        "experiment": "X113b",
        "command": "python scripts/x113b_analyse.py --write",
        "prereg": "reports/2026-11-03-x113c-depth-rate-plan.md",
        "readout": "sister contrast in generations per 1 000 steps (speed) and per division (arithmetic), plus rho(area, rate)",
        "reference_x113": {str(k): v for k, v in X113_DEPTH.items()},
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x113b] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: uids={c['uids']} (excluded {c['excluded_short_life']}) heredity={c['rho_heredity']} "
              f"rate contrast={c['rate_diff_mean']} (CI {c['rate_diff_ci']}) rho(area,rate)={c['rho_area_rate']} "
              f"per-division {c['perdiv_diff_mean']} (CI {c['perdiv_diff_ci']}) depth contrast {c['depth_diff_mean']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
