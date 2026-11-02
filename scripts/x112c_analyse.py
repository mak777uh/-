"""x112c_analyse.py — X112c: the ladder and the specificity at cuts 0.15 and 0.25, on X108's worlds.

`--threshold` is an observer parameter, so the ten seeds at each cut are the same worlds X108 measured at 0.20. The comparison is paired:
the 0.20 reference is X108's own 0.548 (area) and 0.302 (gap), not a number from another sample.

Plan: reports/2026-11-02-x112c-cuts-maze-plan.md.

    python scripts/x112c_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from x102_analyse import nearest_stranger, world_data  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x112c_cuts_maze.json"

FLOW_TAG, FLOW = "f040", 0.040
THRESHOLDS = ("0.15", "0.25")
REF20 = {"rho1": 0.480, "gap": 0.443}      # X108's own 0.20 numbers, quoted
LEVEL_BOUND, LEVEL_STABLE = 0.10, 0.05
GAP_BOUND, GAP_STABLE = 0.15, 0.10
MIN_PAIRS = 300
MIN_OCCUPIED, MIN_LARGEST = 0.05, 50


def runs_for(thr: str) -> list[Path]:
    return sorted(L1.glob(f"x112c_{FLOW_TAG}_thr{thr.replace('.', '')}_s*.json"))


def cut_stats(thr: str) -> dict:
    pa, ca, sa = [], [], []
    pairs = worlds = 0
    alive = True
    for path in runs_for(thr):
        w = world_data(path)
        worlds += 1
        d = json.loads(path.read_text(encoding="utf-8"))
        last = (d.get("series") or [{}])[-1]
        areas = last.get("areas") or []
        # X110b's liveness rule: a component count rejects the maze cell's one percolating body by construction
        occ = last.get("occupied") or 0.0
        largest = max(areas) if areas else 0
        if not (occ >= 0.05 and largest >= 50):
            alive = False
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            pa.append(w["peak"][par]["area"])
            ca.append(w["peak"][child]["area"])
            s = nearest_stranger(w, child)
            if s is not None and s in w["peak"]:
                sa.append((w["peak"][s]["area"], w["peak"][child]["area"]))
    rho = spearman(pa, ca)
    gap = None
    if sa:
        rho_s = spearman([x[0] for x in sa], [x[1] for x in sa])
        if rho is not None and rho_s is not None:
            gap = round(rho - rho_s, 3)
    return {
        "threshold": thr,
        "worlds": worlds,
        "pairs": pairs,
        "used": len(pa),
        "coverage": round(len(pa) / pairs, 3) if pairs else None,
        "all_alive": bool(alive),
        "rho1": round(rho, 3) if rho is not None else None,
        "gap": gap,
        "median_area": float(np.median(pa)) if pa else None,
        "stranger_pairs": len(sa),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X112c cut analysis")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {thr: cut_stats(thr) for thr in THRESHOLDS}

    bad = []
    for thr, c in cells.items():
        if c["used"] < MIN_PAIRS:
            bad.append(f"{thr}: {c['used']} pairs")
        if not c["all_alive"]:
            bad.append(f"{thr}: a run kept fewer than {MIN_COMPONENTS} components")
    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        level = {thr: round((c["rho1"] or 0) - REF20["rho1"], 3) for thr, c in cells.items()}
        gap = {thr: (round((c["gap"] or 0) - REF20["gap"], 3) if c["gap"] is not None else None) for thr, c in cells.items()}
        level_bound = any(abs(v) >= LEVEL_BOUND for v in level.values())
        level_stable = all(abs(v) <= LEVEL_STABLE for v in level.values())
        gap_bound = any(v is not None and abs(v) >= GAP_BOUND for v in gap.values())
        gap_stable = all(v is not None and abs(v) <= GAP_STABLE for v in gap.values())
        parts = ["the level is cut-bound" if level_bound else ("the level is cut-stable" if level_stable
                 else "the level moves less than 0.10")]
        parts.append(f"(deltas against 0.548: {level})")
        parts.append("the gap is cut-bound" if gap_bound else ("the gap is cut-stable" if gap_stable
                     else "the gap moves less than 0.15"))
        parts.append(f"(deltas against 0.302: {gap})")
        verdict = "; ".join(parts)

    res = {
        "kind": "l1_field_x112c_cuts",
        "experiment": "X112c",
        "command": "python scripts/x112c_analyse.py --write",
        "prereg": "reports/2026-11-02-x112c-cuts-maze-plan.md",
        "design": "thresholds 0.15 and 0.25 on seeds 301-310, the same worlds as the 0.20 reference (threshold is an observer parameter)",
        "reference_x108": REF20,
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x112c] written: {OUT.name}")
    for thr, c in cells.items():
        print(f"  {thr}: worlds={c['worlds']} pairs={c['pairs']} used={c['used']} rho1={c['rho1']} gap={c['gap']} "
              f"median={c['median_area']} alive={c['all_alive']}")
    print("  reference 0.20:", REF20)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
