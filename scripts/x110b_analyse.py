"""x110b_analyse.py — X110b: gamma_cell with a liveness test that can tell a pattern from a speckle.

X110's rule counted components, and a dying field can shatter into sixteen tiny ones (observed at F = 0.030, gamma = 0.50, seed 423).
The amendment: alive iff occupied >= 0.05 AND the largest component >= 50 cells, with two alternative threshold sets printed beside it.

Plan: reports/2026-11-02-x110b-liveness-plan.md.

    python scripts/x110b_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x110b_gamma_cell.json"

CELLS = {"f030": 0.030, "f040": 0.040}
SEEDS = (421, 422, 423)
GAMMAS = ("0.10", "0.15", "0.20", "0.30", "0.50")
ALIVE_IN_SEEDS = 2
THRESHOLDS = ((0.05, 50), (0.04, 40), (0.06, 60))   # nominal and two alternatives, registered before the maze column


def read_run(cell: str, seed: int, gamma: str) -> dict | None:
    p = L1 / f"x110_{cell}_g{gamma.replace('.', '')}_s{seed}.json"
    if not p.is_file():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    last = (d.get("series") or [{}])[-1]
    areas = last.get("areas") or []
    return {"components": last.get("components"), "occupied": last.get("occupied"),
            "max_area": max(areas) if areas else 0}


def gamma_cell(table: dict, occ_floor: float, area_floor: float) -> str | None:
    best = None
    for g in GAMMAS:
        alive = sum(1 for r in table[g] if r and (r["occupied"] or 0) >= occ_floor and (r["max_area"] or 0) >= area_floor)
        if alive >= ALIVE_IN_SEEDS:
            best = g
    return best


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X110b gamma_cell with a structural liveness test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {}
    for cell in CELLS:
        table = {g: [read_run(cell, s, g) for s in SEEDS] for g in GAMMAS}
        brackets = {f"{occ}/{area}": gamma_cell(table, occ, area) for occ, area in THRESHOLDS}
        cells[cell] = {"by_gamma": table, "gamma_cell_by_threshold": brackets,
                       "gamma_cell": brackets[f"{THRESHOLDS[0][0]}/{THRESHOLDS[0][1]}"]}

    complete = all(r is not None for c in cells.values() for g in GAMMAS for r in c["by_gamma"][g])
    low_ok = all(r and (r["occupied"] or 0) >= THRESHOLDS[0][0] and (r["max_area"] or 0) >= THRESHOLDS[0][1]
                 for c in cells.values() for r in c["by_gamma"]["0.10"])
    high_ok = all(r and not ((r["occupied"] or 0) >= THRESHOLDS[0][0] and (r["max_area"] or 0) >= THRESHOLDS[0][1])
                  for c in cells.values() for r in c["by_gamma"]["0.50"] if r is not None)

    if not complete:
        verdict = "void: the grid is incomplete"
    elif not low_ok:
        verdict = "void: the control failed — a gamma = 0.10 run is not alive under the nominal thresholds"
    elif not high_ok:
        verdict = "void: the control failed — a gamma = 0.50 run is alive under the nominal thresholds"
    else:
        lat = cells["f030"]
        maz = cells["f040"]
        order = {g: i for i, g in enumerate(GAMMAS)}
        distinct = set(lat["gamma_cell_by_threshold"].values()) | set(maz["gamma_cell_by_threshold"].values())
        lat_vals = set(lat["gamma_cell_by_threshold"].values())
        maz_vals = set(maz["gamma_cell_by_threshold"].values())
        if len(lat_vals) > 1 or len(maz_vals) > 1:
            verdict = (f"threshold-sensitive: gamma_cell moves with the liveness thresholds (lattice {lat['gamma_cell_by_threshold']}, "
                       f"maze {maz['gamma_cell_by_threshold']}) — the honest output is a range")
        else:
            lat_g = lat["gamma_cell"]
            maz_g = maz["gamma_cell"]
            if lat_g and maz_g and order[maz_g] < order[lat_g]:
                verdict = (f"the cells differ in their distance to the edge: gamma_cell is {maz_g} in the maze against {lat_g} in the "
                           f"lattice, and the same under all three threshold sets")
            elif lat_g == maz_g:
                verdict = f"the cells do not differ: gamma_cell {lat_g} in both, under all three threshold sets"
            else:
                verdict = f"not decided: lattice {lat_g}, maze {maz_g}"

    res = {
        "kind": "l1_field_x110b_gamma_cell",
        "experiment": "X110b",
        "command": "python scripts/x110b_analyse.py --write",
        "prereg": "reports/2026-11-02-x110b-liveness-plan.md",
        "liveness": "occupied >= 0.05 and largest component >= 50 cells; alternatives 0.04/40 and 0.06/60",
        "rule": "uvv = u*v*v/(1+gamma*w); dw/dt = 0.16*lap(w) + 0.05*(v - w); gamma swept",
        "grid": list(GAMMAS),
        "alive_in_seeds": ALIVE_IN_SEEDS,
        "cells": cells,
        "positive_control": {"gamma_010_alive": bool(low_ok), "gamma_050_dead": bool(high_ok)},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x110b] written: {OUT.name}")
    for cell, c in cells.items():
        row = " ".join(f"{g}:{[(r['components'], round(r['occupied'] or 0, 3), r['max_area']) if r else None for r in c['by_gamma'][g]]}"
                       for g in GAMMAS)
        print(f"  {cell}: gamma_cell={c['gamma_cell']} {c['gamma_cell_by_threshold']}")
        print(f"     {row}")
    print("  controls:", low_ok, high_ok)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
