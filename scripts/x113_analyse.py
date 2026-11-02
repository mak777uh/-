"""x113_analyse.py — X113: does size buy generations?

Consequence in a currency that is not size: how many generations a lineage propagates (`depth`), and whether the larger sister's line goes
deeper than the smaller's. Read from X108's dense logs, no new runs.

Plan: reports/2026-11-03-x113-depth-plan.md.

    python scripts/x113_analyse.py --write
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
from x97_analyse import ranks_of, spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x113_depth.json"

CELLS = {"f030": 0.030, "f040": 0.040}
MIN_UIDS = 300
HEREDITY_FLOOR = 0.35
LIFE_OVERLAP_MAX = 0.8
RESOLUTION = 0.10
BOOTSTRAP = 2000


def life_of(w: dict, uid: int) -> float:
    """Lifetime from the component log: last step a uid appears minus its first. `world_data` records first and peak, not last."""
    first = w["first"].get(uid, {}).get("step")
    if first is None:
        return 0.0
    last = first
    for step, comps in w["per_step"].items():
        if any(int(c["uid"]) == uid for c in comps):
            last = max(last, int(step))
    return float(last - int(first) + 1)


def partial(x, y, z):
    rx, ry, rz = ranks_of(x), ranks_of(y), ranks_of(z)
    def corr(a, b):
        n = len(a)
        mx, my = sum(a) / n, sum(b) / n
        sxy = sum((p - mx) * (q - my) for p, q in zip(a, b))
        sxx = sum((p - mx) ** 2 for p in a)
        syy = sum((q - my) ** 2 for q in b)
        return sxy / (sxx * syy) ** 0.5 if sxx and syy else None
    rxy, rxz, ryz = corr(rx, ry), corr(rx, rz), corr(ry, rz)
    if None in (rxy, rxz, ryz):
        return None
    den = (1 - rxz ** 2) * (1 - ryz ** 2)
    return (rxy - rxz * ryz) / den ** 0.5 if den > 0 else None


def depth_of(children: dict[int, list[int]], uid: int, memo: dict[int, int]) -> int:
    if uid in memo:
        return memo[uid]
    kids = children.get(uid, [])
    memo[uid] = 0 if not kids else 1 + max(depth_of(children, k, memo) for k in kids)
    return memo[uid]


def cell_stats(flow: float) -> dict:
    areas, depths, lifes, subtrees = [], [], [], []
    sister_diffs = []
    heredity = []
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        memo: dict[int, int] = {}
        for uid in w["peak"]:
            if uid not in children:
                continue
            areas.append(w["peak"][uid]["area"])
            depths.append(depth_of(children, uid, memo))
            lifes.append(life_of(w, uid))
            subtrees.append(len(w["parent"]) and _subtree(children, uid, {}))
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    da, db = depth_of(children, a, memo), depth_of(children, b, memo)
                    bigger, smaller = (da, db) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (db, da)
                    sister_diffs.append(bigger - smaller)
    rho_area = spearman(areas, depths) if areas else None
    rho_partial = partial(areas, depths, lifes) if areas else None
    rho_life = spearman(depths, lifes) if depths else None
    rho_heredity = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {"uids": len(areas), "rho_area_depth": round(rho_area, 3) if rho_area is not None else None,
            "rho_partial_life": round(rho_partial, 3) if rho_partial is not None else None,
            "rho_depth_life": round(rho_life, 3) if rho_life is not None else None,
            "rho_heredity": round(rho_heredity, 3) if rho_heredity is not None else None,
            "median_depth": st.median(depths) if depths else None,
            "max_depth": max(depths) if depths else None,
            "sister_pairs": len(sister_diffs),
            "sister_diff_mean": round(st.mean(sister_diffs), 3) if sister_diffs else None,
            "_diffs": sister_diffs}


def _subtree(children: dict[int, list[int]], uid: int, memo: dict[int, int]) -> int:
    if uid in memo:
        return memo[uid]
    memo[uid] = sum(1 + _subtree(children, k, memo) for k in children.get(uid, []))
    return memo[uid]


def bootstrap_ci(vals, seed=113):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 3), round(means[int(0.975 * BOOTSTRAP)], 3)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X113 depth as a consequence currency")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    for tag, c in cells.items():
        diffs = c.pop("_diffs")
        c["sister_diff_ci"] = bootstrap_ci(diffs)

    bad = []
    for tag, c in cells.items():
        if c["uids"] < MIN_UIDS:
            bad.append(f"{tag}: {c['uids']} uids with descendants")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["rho_depth_life"] is None or c["rho_depth_life"] >= LIFE_OVERLAP_MAX:
            bad.append(f"{tag}: depth correlates with lifetime at {c['rho_depth_life']} — a re-labelling")
    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        buys = (lat["sister_diff_ci"] and lat["sister_diff_ci"][0] > 0
                and (lat["rho_partial_life"] or 0) >= 0.10 and (maz["rho_partial_life"] or 0) >= 0.10)
        nothing = ((lat["sister_diff_ci"] and lat["sister_diff_ci"][0] <= 0 <= lat["sister_diff_ci"][1])
                   or (abs(lat["rho_partial_life"] or 0) <= 0.05 and abs(maz["rho_partial_life"] or 0) <= 0.05))
        if buys:
            verdict = (f"size buys generations: the larger sister's line goes {lat['sister_diff_mean']} generations deeper "
                       f"(CI {lat['sister_diff_ci']}) and the partial of area given lifetime is "
                       f"{lat['rho_partial_life']} / {maz['rho_partial_life']}")
        elif nothing:
            verdict = (f"no consequence in this currency: the sister contrast is {lat['sister_diff_mean']} generations "
                       f"(CI {lat['sister_diff_ci']}) and the partial of area given lifetime is "
                       f"{lat['rho_partial_life']} / {maz['rho_partial_life']}")
        else:
            verdict = (f"mixed: sister contrast {lat['sister_diff_mean']} (CI {lat['sister_diff_ci']}), partial "
                       f"{lat['rho_partial_life']} / {maz['rho_partial_life']}; maze sister contrast {maz['sister_diff_mean']} "
                       f"(CI {maz['sister_diff_ci']})")
    res = {
        "kind": "l1_field_x113_depth",
        "experiment": "X113",
        "command": "python scripts/x113_analyse.py --write",
        "prereg": "reports/2026-11-03-x113-depth-plan.md",
        "readout": "rho(area, depth), the same partialled on lifetime, and the paired sister contrast in depth",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x113] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: uids={c['uids']} rho_area_depth={c['rho_area_depth']} partial={c['rho_partial_life']} "
              f"depth~life={c['rho_depth_life']} heredity={c['rho_heredity']} sister={c['sister_diff_mean']} "
              f"(CI {c['sister_diff_ci']}, n={c['sister_pairs']}) median depth={c['median_depth']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
