"""x115_analyse.py — X115: does the faster line persist? Survival to the horizon, paired within sister pairs.

Reads X108's logs (restored and verified). Per sister pair: does each branch's subtree contain a member at the last logged step? Plus the number of living
descendants, which is sensitive to how much survives rather than whether.

Plan: reports/2026-11-03-x115-persistence-plan.md.

    python scripts/x115_analyse.py --write
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
from x113_analyse import depth_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x115_persistence.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
DEPTH_TOL = 0.05
MIN_PAIRS = 300
HEREDITY_FLOOR = 0.35
RESOLUTION = 0.05
BOOTSTRAP = 2000


def descendants(children: dict[int, list[int]], uid: int) -> list[int]:
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
    return out


def bootstrap_ci(vals, seed=115):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 4), round(means[int(0.975 * BOOTSTRAP)], 4)]


def cell_stats(flow: float) -> dict:
    heredity, depth_diff, surv_diff, count_diff = [], [], [], []
    both = only_big = only_small = neither = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        last_step = max(w["per_step"]) if w["per_step"] else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        memo: dict[int, int] = {}
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    da = descendants(children, big)
                    ds = descendants(children, small)
                    la = len([u for u in da if u in present])
                    ls = len([u for u in ds if u in present])
                    alive_a, alive_s = la > 0, ls > 0
                    if alive_a and alive_s:
                        both += 1
                    elif alive_a:
                        only_big += 1
                    elif alive_s:
                        only_small += 1
                    else:
                        neither += 1
                    surv_diff.append(int(alive_a) - int(alive_s))
                    count_diff.append((la - ls) / max(1, la + ls))
                    depth_diff.append(depth_of(children, big, memo) - depth_of(children, small, memo))
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "pairs": len(surv_diff),
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "depth_diff_mean": round(st.mean(depth_diff), 3) if depth_diff else None,
        "survival_diff_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "survival_diff_ci": bootstrap_ci(surv_diff),
        "count_diff_mean": round(st.mean(count_diff), 4) if count_diff else None,
        "count_diff_ci": bootstrap_ci(count_diff),
        "both": both, "only_bigger": only_big, "only_smaller": only_small, "neither": neither,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X115 persistence of the faster line")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        ref = X113_DEPTH[CELLS[tag]]
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["depth_diff_mean"] is None or abs(c["depth_diff_mean"] - ref) > DEPTH_TOL * abs(ref):
            bad.append(f"{tag}: depth contrast {c['depth_diff_mean']} misses X113's {ref}")
        if c["both"] == c["pairs"]:
            bad.append(f"{tag}: every pair has both branches alive at the end — no discrimination")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        better = all(c["survival_diff_ci"] and c["survival_diff_ci"][0] > 0 for c in (lat, maz))
        same = all(c["survival_diff_ci"] and c["survival_diff_ci"][0] <= 0 <= c["survival_diff_ci"][1] for c in (lat, maz))
        if better:
            verdict = (f"faster lines persist better: the larger sister's branch is alive at the end {lat['survival_diff_mean']:.3f} more often "
                       f"(CI {lat['survival_diff_ci']}) in the lattice and {maz['survival_diff_mean']:.3f} in the maze "
                       f"(CI {maz['survival_diff_ci']})")
        elif same:
            verdict = (f"no consequence in persistence: the survival difference is {lat['survival_diff_mean']:.3f} (CI "
                       f"{lat['survival_diff_ci']}) and {maz['survival_diff_mean']:.3f} (CI {maz['survival_diff_ci']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['survival_diff_mean']:.3f} (CI {lat['survival_diff_ci']}), maze "
                       f"{maz['survival_diff_mean']:.3f} (CI {maz['survival_diff_ci']})")
        verdict += (f"; counts both/only bigger/only smaller/neither: {lat['both']}/{lat['only_bigger']}/{lat['only_smaller']}/"
                    f"{lat['neither']} and {maz['both']}/{maz['only_bigger']}/{maz['only_smaller']}/{maz['neither']}")

    res = {
        "kind": "l1_field_x115_persistence",
        "experiment": "X115",
        "command": "python scripts/x115_analyse.py --write",
        "prereg": "reports/2026-11-03-x115-persistence-plan.md",
        "readout": "paired difference in end-survival between the larger and the smaller sister, and the difference in living descendants",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x115] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} heredity={c['rho_heredity']} survival diff={c['survival_diff_mean']} "
              f"(CI {c['survival_diff_ci']}) count diff={c['count_diff_mean']} (CI {c['count_diff_ci']}) "
              f"both/onlyBig/onlySmall/neither={c['both']}/{c['only_bigger']}/{c['only_smaller']}/{c['neither']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
