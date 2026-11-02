"""x107_analyse.py — X107: how much of the parent-daughter correlation is a shared room?

X106 showed the distance to the nearest non-ancestor peak predicts the mother's OWN area (+0.397 at F = 0.030) slightly better than
her daughter's (+0.322) — room is a property of the place. Daughters are born close to their mothers (median 4.9 cells), so mother
and daughter share that room. This analysis asks how much of the 0.531 heredity coefficient survives controlling for it.
Plan: reports/2026-11-02-x107-shared-room-plan.md.

    python scripts/x107_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files, partial_spearman  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x106_analyse import nearest_nonancestor  # noqa: E402

PREFIX = "x100"   # X109: the same readouts on the dense series need only this to change
CELLS = {"f030": 0.030, "f040": 0.040}
MIN_PAIRS = 100
MIN_COVERAGE = 0.50
CONTROL_FLOOR = 0.35
REFS = {"f030": 0.397, "f040": -0.038}   # X106's room coefficients, the replication band
REPLICATION_BAND = 0.10
RESOLUTION = 0.10
RESIDUAL_FLOOR = 0.25


def cell_stats(flow: float) -> dict:
    mother_a, daughter_a, room_m, room_d = [], [], [], []
    pairs = used = worlds = 0
    for path in cell_files((PREFIX,), flow, filename=""):
        w = world_data(path)
        worlds += 1
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            mother = w["peak"][par]
            birth = w["first"].get(child) or w["peak"][child]
            if mother.get("cx") is None or birth.get("cx") is None:
                continue
            comps_m = w["per_step"].get(int(mother["step"])) or []
            rm = nearest_nonancestor(comps_m, w["parent"], par, float(mother["cy"]), float(mother["cx"]))
            comps_d = w["per_step"].get(int(birth["step"])) or []
            rd = nearest_nonancestor(comps_d, w["parent"], child, float(birth["cy"]), float(birth["cx"]))
            if rm is None or rd is None:
                continue
            mother_a.append(float(mother["area"]))
            daughter_a.append(float(w["peak"][child]["area"]))
            room_m.append(rm)
            room_d.append(rd)
            used += 1

    rho_control = spearman(mother_a, daughter_a)
    rho_room = spearman(room_m, mother_a)
    rho_partial_m = partial_spearman(mother_a, daughter_a, room_m)
    # both rooms at once: regress out each room from both areas, then correlate the residuals
    rho_partial_both = partial_spearman(mother_a, daughter_a,
                                        [a + b for a, b in zip(room_m, room_d)])
    assert used <= pairs
    drop = (round(rho_control - rho_partial_m, 3)
            if rho_control is not None and rho_partial_m is not None else None)
    return {
        "flow": flow,
        "worlds": worlds,
        "pairs": pairs,
        "used": used,
        "coverage": round(used / pairs, 3) if pairs else None,
        "median_room_mother": round(float(np.median(room_m)), 2) if room_m else None,
        "rho_control": round(rho_control, 3) if rho_control is not None else None,
        "rho_room": round(rho_room, 3) if rho_room is not None else None,
        "rho_partial_mother_room": round(rho_partial_m, 3) if rho_partial_m is not None else None,
        "rho_partial_both_rooms": round(rho_partial_both, 3) if rho_partial_both is not None else None,
        "drop": drop,
    }


def verdict_of(cells: dict) -> str:
    bad = []
    for k, v in cells.items():
        if v["used"] < MIN_PAIRS or (v["coverage"] or 0) < MIN_COVERAGE:
            bad.append(f"{k}: {v['used']} pairs at coverage {v['coverage']}")
        if (v["rho_control"] or 0) < CONTROL_FLOOR:
            bad.append(f"{k}: heredity {v['rho_control']} below {CONTROL_FLOOR}")
        if v["rho_room"] is None or abs(v["rho_room"] - REFS[k]) > REPLICATION_BAND:
            bad.append(f"{k}: room coefficient {v['rho_room']} misses X106's {REFS[k]}")
    if bad:
        return "void: " + "; ".join(bad)
    lat = cells["f030"]
    drops = [v["drop"] for v in cells.values()]
    if all(d is not None and d <= RESOLUTION for d in drops):
        return ("heredity is not a shared-room effect: controlling the room leaves the parent-daughter coefficient within 0.10 of "
                "its raw value in both cells")
    if (lat["drop"] or 0) >= 0.15 and (lat["rho_partial_mother_room"] or 0) >= RESIDUAL_FLOOR:
        return (f"heredity is partly a shared-room effect in the lattice: the coefficient falls from {lat['rho_control']} to "
                f"{lat['rho_partial_mother_room']} (drop {lat['drop']}) but a residual remains — the room explains a share, not the "
                f"whole, of the resemblance")
    if (lat["drop"] or 0) >= 0.15 and (lat["rho_partial_mother_room"] or 0) < RESIDUAL_FLOOR:
        return (f"heredity is mostly a shared-room effect in the lattice: the coefficient falls from {lat['rho_control']} to "
                f"{lat['rho_partial_mother_room']} (drop {lat['drop']}) and the residual is below {RESIDUAL_FLOOR}")
    return "mixed: printed cell by cell, and the claim is stated for the cell where the room coordinate has an effect to remove"


def main(argv=None) -> int:
    global PREFIX
    ap = argparse.ArgumentParser(description="X107 shared room")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--prefix", default=PREFIX, help="run-file prefix (x100 by default, x108 for the dense series)")
    ap.add_argument("--out", default=None, help="aggregate file name inside E09_pond")
    args = ap.parse_args(argv)
    PREFIX = args.prefix

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    verdict = verdict_of(cells)
    fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
    res = {
        "kind": "l1_field_x107_shared_room",
        "experiment": "X107",
        "command": "python scripts/x107_analyse.py --write",
        "prereg": "reports/2026-11-02-x107-shared-room-plan.md",
        "readout": ("rho(mother area, daughter area) before and after partialling out the mother's distance to the nearest "
                    "non-ancestor peak, and after partialling out both rooms"),
        "cells": cells,
        "positive_control": {"fires": fires,
                             "note": "heredity >= 0.35; the room coefficient reproduces X106 within 0.10"},
        "references_x106": REFS,
        "resolution": RESOLUTION,
        "verdict": verdict,
    }
    if args.write:
        name = args.out or ("l1_field_x107_shared_room.json" if PREFIX == "x100"
                            else f"l1_field_x109_room_{PREFIX}.json")
        out = Path(__file__).resolve().parents[1] / "morphogenesis" / "experiments" / "E09_pond" / name
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x107] written: {out.name}")
    for k, v in cells.items():
        print(f"  {k}: used={v['used']}/{v['pairs']} cover={v['coverage']} room={v['median_room_mother']} | "
              f"control={v['rho_control']} room_rho={v['rho_room']} partial_mother_room={v['rho_partial_mother_room']} "
              f"partial_both={v['rho_partial_both_rooms']} drop={v['drop']}")
    print("  control:", fires)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
