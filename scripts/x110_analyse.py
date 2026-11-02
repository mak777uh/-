"""x110_analyse.py — X110: gamma_cell, the largest autocatalysis cut a cell survives, as a bracket.

Readouts: components at step 6000 (the liveness floor is 10), peak amplitude and q' for the live runs. `gamma_cell` for a cell is the
largest coupling alive in at least two of three seeds — a bracket on the bisection grid, not a calibrated constant.
Plan: reports/2026-11-02-x110-gamma-cell-plan.md.

    python scripts/x110_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import angular  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x110_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x110_gamma_cell.json"

CELLS = {"f030": 0.030, "f040": 0.040}
SEEDS = (421, 422, 423)
GAMMAS = ("0.10", "0.15", "0.20", "0.30", "0.50")
MIN_ALIVE = 10
ALIVE_IN_SEEDS = 2      # gamma_cell needs two of three seeds alive


def read_run(cell: str, seed: int, gamma: str) -> dict | None:
    tag = f"x110_{cell}_g{gamma.replace('.', '')}_s{seed}"
    run = L1 / f"{tag}.json"
    if not run.is_file():
        return None
    d = json.loads(run.read_text(encoding="utf-8"))
    last = (d.get("series") or [{}])[-1]
    out = {"components": last.get("components"), "v_max": last.get("v_max")}
    field = FIELDS / f"{tag}_t6000.npy"
    if field.is_file():
        a = angular(np.load(field), forcing_q=8, q_max=14)
        out["q"] = a.get("q_axis")
        out["symmetry"] = round(float(a["symmetry"]), 3) if a.get("symmetry") is not None else None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X110 gamma_cell analysis")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells: dict[str, dict] = {}
    for cell in CELLS:
        table: dict[str, list[dict]] = {}
        for gamma in GAMMAS:
            table[gamma] = []
            for seed in SEEDS:
                r = read_run(cell, seed, gamma)
                if r is not None:
                    table[gamma].append({"seed": seed, **r})
        bracket = None
        for gamma in GAMMAS:
            alive = sum(1 for r in table[gamma] if (r.get("components") or 0) >= MIN_ALIVE)
            if alive >= ALIVE_IN_SEEDS:
                bracket = gamma
        cells[cell] = {"by_gamma": table, "gamma_cell": bracket}

    # controls
    low = all(cells[c]["by_gamma"]["0.10"] and
              all((r.get("components") or 0) >= MIN_ALIVE for r in cells[c]["by_gamma"]["0.10"])
              for c in cells)
    high = all(all((r.get("components") or 0) < MIN_ALIVE for r in cells[c]["by_gamma"]["0.50"])
               for c in cells)
    covered = all(cells[c]["by_gamma"]["0.50"] and cells[c]["by_gamma"]["0.10"] for c in cells)

    if not covered:
        verdict = "void: the grid is incomplete — some couplings have no runs yet"
    elif not low:
        verdict = "void: the control failed — gamma = 0.10 is not alive in all six runs"
    elif not high:
        verdict = "void: the control failed — gamma = 0.50 left a pattern somewhere, so the collapse is not monotone"
    else:
        lat, maz = cells["f030"]["gamma_cell"], cells["f040"]["gamma_cell"]
        order = {g: i for i, g in enumerate(GAMMAS)}
        if lat is None or maz is None:
            verdict = f"not decided: one cell never reached two live seeds (lattice {lat}, maze {maz})"
        elif order[maz] < order[lat]:
            verdict = (f"the cells differ in their distance to the edge: gamma_cell is {maz} in the maze against {lat} in the "
                       f"lattice — at least one bisection step apart")
        else:
            verdict = (f"the cells do not differ within the grid: gamma_cell {lat} (lattice) against {maz} (maze), brackets "
                       f"overlapping")

    res = {
        "kind": "l1_field_x110_gamma_cell",
        "experiment": "X110",
        "command": "python scripts/x110_analyse.py --write",
        "prereg": "reports/2026-11-02-x110-gamma-cell-plan.md",
        "rule": "uvv = u*v*v/(1+gamma*w); dw/dt = 0.16*lap(w) + 0.05*(v - w); gamma swept",
        "readout": "components at step 6000 with a liveness floor of 10; q' and symmetry for live runs",
        "grid": list(GAMMAS),
        "min_alive": MIN_ALIVE,
        "alive_in_seeds": ALIVE_IN_SEEDS,
        "cells": cells,
        "positive_control": {"gamma_010_alive_everywhere": bool(low), "gamma_050_dead_everywhere": bool(high),
                             "note": "the weakest coupling must keep a pattern and the strongest must not"},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x110] written: {OUT.name}")
    for cell, c in cells.items():
        row = " ".join(f"{g}:{[r.get('components') for r in c['by_gamma'][g]]}" for g in GAMMAS)
        print(f"  {cell}: gamma_cell={c['gamma_cell']} | {row}")
    print("  controls:", low, high)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
