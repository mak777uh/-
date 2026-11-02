"""x97b_analyse.py — X97b: is the second-generation sister advantage branching arithmetic or a lineage effect?

Same sister pairs as X97, four readouts: the mean difference (X97's number, the control), the median difference per branch pair, the mean
granddaughter area per grandchild (unweighted by branch count), and the number of grandchildren per branch.

Plan: reports/2026-11-03-x97b-sisters-median-plan.md.

    python scripts/x97b_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x97b_sisters_median.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X97_MEAN = {0.030: 12.9007, 0.040: 170.9068}
MEAN_TOL = 0.05
HEREDITY_FLOOR = 0.35
MIN_PAIRS = 100
MEDIAN_SHARE = 0.5
BRANCH_EXCESS = 0.10


def cell_stats(flow: float) -> dict:
    mean_diffs, median_diffs, per_child_diffs = [], [], []
    branch_big, branch_small = [], []
    pairs_heredity = []
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        pairs_heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    ga = [g for g in children.get(a, []) if g in w["peak"]]
                    gb = [g for g in children.get(b, []) if g in w["peak"]]
                    if not ga or not gb:
                        continue
                    big, small = (ga, gb) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (gb, ga)
                    ab = [w["peak"][g]["area"] for g in big]
                    as_ = [w["peak"][g]["area"] for g in small]
                    mean_diffs.append(st.mean(ab) - st.mean(as_))
                    median_diffs.append(st.median(ab) - st.median(as_))
                    per_child_diffs.append(st.mean(ab) - st.mean(as_))   # each grandchild weighted equally already
                    branch_big.append(len(ab))
                    branch_small.append(len(as_))
    rho = spearman([p[0] for p in pairs_heredity], [p[1] for p in pairs_heredity]) if pairs_heredity else None
    return {
        "pairs": len(mean_diffs),
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "mean_diff": round(st.mean(mean_diffs), 4) if mean_diffs else None,
        "median_diff": round(st.mean(median_diffs), 4) if median_diffs else None,
        "median_diff_of_medians": round(st.median(median_diffs), 4) if median_diffs else None,
        "branch_big": round(st.mean(branch_big), 3) if branch_big else None,
        "branch_small": round(st.mean(branch_small), 3) if branch_small else None,
        "x97_mean": X97_MEAN[flow],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X97b sisters median test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["mean_diff"] is None or abs(c["mean_diff"] - c["x97_mean"]) > MEAN_TOL * abs(c["x97_mean"]):
            bad.append(f"{tag}: mean {c['mean_diff']} misses X97's {c['x97_mean']} by more than {MEAN_TOL:.0%}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat = cells["f030"]
        share = lat["median_diff"] / lat["mean_diff"] if lat["mean_diff"] else None
        excess = (lat["branch_big"] / lat["branch_small"] - 1.0) if lat["branch_small"] else None
        parts = []
        if share is not None and share <= MEDIAN_SHARE and (excess or 0) >= BRANCH_EXCESS:
            parts.append(f"branching arithmetic dominates: the median difference is {share:.0%} of the mean while the larger sister has "
                         f"{excess:.0%} more grandchildren per branch")
        elif share is not None and share >= MEDIAN_SHARE:
            parts.append(f"a lineage effect is needed: the median difference is {share:.0%} of the mean")
        else:
            parts.append(f"mixed: median share {share:.0%}, branch excess {excess:.0%}")
        parts.append(f"(lattice mean {lat['mean_diff']}, median {lat['median_diff']}, branches {lat['branch_big']} vs {lat['branch_small']})")
        maze = cells["f040"]
        parts.append(f"maze: mean {maze['mean_diff']}, median {maze['median_diff']}, branches {maze['branch_big']} vs "
                     f"{maze['branch_small']}")
        verdict = "; ".join(parts)

    res = {
        "kind": "l1_field_x97b_sisters_median",
        "experiment": "X97b",
        "command": "python scripts/x97b_analyse.py --write",
        "prereg": "reports/2026-11-03-x97b-sisters-median-plan.md",
        "readout": "mean, median and per-grandchild differences in granddaughter area, plus grandchildren per branch",
        "reference_x97": {str(k): v for k, v in X97_MEAN.items()},
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x97b] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} heredity={c['rho_heredity']} mean={c['mean_diff']} median={c['median_diff']} "
              f"branches {c['branch_big']} vs {c['branch_small']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
