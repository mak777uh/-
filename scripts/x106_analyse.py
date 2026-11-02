"""x106_analyse.py — X106: what is the crowding term?  A property of places, of growth, or of persistence.

X103d found that a daughter born farther from the nearest NON-ancestor peak grows larger (+0.358 in the lattice, ten worlds out of
ten).  This analysis asks three questions on the same logs: does the same coordinate predict the mother's own area (a property of
places), does it predict the daughter's lifetime (persistence), and does the area effect survive controlling for lifetime.
Plan: reports/2026-11-02-x106-crowding-plan.md.

    python scripts/x106_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files, partial_spearman  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x103_analyse import ancestors_of, torus  # noqa: E402

PREFIX = "x100"   # X109: the same readouts on the dense series need only this to change
CELLS = {"f030": 0.030, "f040": 0.040}
MIN_PAIRS = 100
CONTROL_FLOOR = 0.35
REFS = {"f030": 0.358, "f040": 0.103}   # X103d's crowding coefficients, the replication band
REPLICATION_BAND = 0.10
RESOLUTION = 0.10
LIFETIME_FLOOR = 0.20     # lifetime is logged in 50-step quanta; only large coefficients count


def nearest_nonancestor(comps: list[dict], parent: dict[int, int], uid: int,
                        cy: float, cx: float) -> float | None:
    ban = ancestors_of(parent, uid)
    best = None
    for c in comps:
        other = int(c["uid"])
        if other in ban or c.get("cx") is None:
            continue
        d = math.hypot(torus(float(c["cy"]), cy), torus(float(c["cx"]), cx))
        if best is None or d < best:
            best = d
    return best


def lifetime_of(per_step: dict[int, list[dict]], uid: int) -> int | None:
    seen = [step for step, comps in per_step.items() if any(int(c["uid"]) == uid for c in comps)]
    return (max(seen) - min(seen)) if len(seen) >= 2 else None


def cell_stats(flow: float) -> dict:
    d_daughter, d_mother, area_d, area_m, life = [], [], [], [], []
    life_coeffs = []
    pairs = used = worlds = 0
    for path in cell_files((PREFIX,), flow, filename=""):
        w = world_data(path)
        worlds += 1
        wd, wm, wa, wc, wl = [], [], [], [], []
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            birth = w["first"].get(child) or w["peak"][child]
            mother = w["peak"][par]
            if birth.get("cx") is None or mother.get("cx") is None:
                continue
            comps_birth = w["per_step"].get(int(birth["step"])) or []
            d_d = nearest_nonancestor(comps_birth, w["parent"], child, float(birth["cy"]), float(birth["cx"]))
            comps_mother = w["per_step"].get(int(mother["step"])) or []
            d_m = nearest_nonancestor(comps_mother, w["parent"], par, float(mother["cy"]), float(mother["cx"]))
            lt = lifetime_of(w["per_step"], child)
            if d_d is None or d_m is None or lt is None:
                continue
            wd.append(d_d)
            wm.append(d_m)
            wa.append(float(mother["area"]))
            wc.append(float(w["peak"][child]["area"]))
            wl.append(float(lt))
            used += 1
        if len(wd) >= 30:
            r = spearman(wd, wl)
            life_coeffs.append({"world": path.name, "pairs": len(wd), "rho_life": round(r, 3) if r is not None else None})
        d_daughter.extend(wd)
        d_mother.extend(wm)
        area_d.extend(wc)
        area_m.extend(wa)
        life.extend(wl)

    rho_area = spearman(d_daughter, area_d)
    rho_place = spearman(d_mother, area_m)
    rho_life = spearman(d_daughter, life)
    rho_control = spearman(area_m, area_d)
    rho_area_given_life = partial_spearman(d_daughter, area_d, life)
    signs = [p["rho_life"] for p in life_coeffs if p["rho_life"] is not None]
    assert used <= pairs
    return {
        "flow": flow,
        "worlds": worlds,
        "pairs": pairs,
        "used": used,
        "coverage": round(used / pairs, 3) if pairs else None,
        "median_d_near": round(float(np.median(d_daughter)), 2) if d_daughter else None,
        "median_lifetime": round(float(np.median(life)), 1) if life else None,
        "rho_area": round(rho_area, 3) if rho_area is not None else None,
        "rho_place": round(rho_place, 3) if rho_place is not None else None,
        "rho_life": round(rho_life, 3) if rho_life is not None else None,
        "rho_control": round(rho_control, 3) if rho_control is not None else None,
        "rho_area_given_life": round(rho_area_given_life, 3) if rho_area_given_life is not None else None,
        "per_world_life": life_coeffs,
        "worlds_life_positive": sum(1 for s in signs if s > 0),
        "worlds_measured": len(signs),
    }


def verdict_of(cells: dict) -> str:
    bad = []
    for k, v in cells.items():
        if v["used"] < MIN_PAIRS:
            bad.append(f"{k}: {v['used']} pairs")
        if (v["rho_control"] or 0) < CONTROL_FLOOR:
            bad.append(f"{k}: heredity control {v['rho_control']}")
        if v["rho_area"] is None or abs(v["rho_area"] - REFS[k]) > REPLICATION_BAND:
            bad.append(f"{k}: crowding {v['rho_area']} misses X103d's {REFS[k]}")
    if bad:
        return "void: " + "; ".join(bad)
    place = all(abs(v["rho_place"] or 0) >= 0.20 and (v["rho_place"] or 0) * (v["rho_area"] or 0) > 0
                for v in cells.values())
    growth = all((v["rho_area"] or 0) >= 0.20 and abs(v["rho_life"] or 0) <= RESOLUTION for v in cells.values())
    persist = all((v["rho_area"] or 0) >= 0.20 and abs(v["rho_life"] or 0) >= LIFETIME_FLOOR
                  and (v["rho_life"] or 0) * (v["rho_area"] or 0) > 0 for v in cells.values())
    if place:
        return ("a property of places: the same distance predicts the mother's own area with the same sign, so crowding "
                "describes where structures can grow, not what daughters inherit")
    if growth:
        return ("a constraint on growth: room predicts the daughter's area but not her lifetime, so crowding sets how large a "
                "structure becomes, not how long it lasts")
    if persist:
        return ("a constraint on persistence: room predicts both the area and the lifetime with the same sign — a structure with "
                "space grows larger and lasts longer")
    return "mixed: the three readings are not separated with one sign in both cells — printed cell by cell"


def main(argv=None) -> int:
    global PREFIX
    ap = argparse.ArgumentParser(description="X106 crowding term")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--prefix", default=PREFIX, help="run-file prefix (x100 by default, x108 for the dense series)")
    ap.add_argument("--out", default=None, help="aggregate file name inside E09_pond")
    args = ap.parse_args(argv)
    PREFIX = args.prefix

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    verdict = verdict_of(cells)
    fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
    res = {
        "kind": "l1_field_x106_crowding",
        "experiment": "X106",
        "command": "python scripts/x106_analyse.py --write",
        "prereg": "reports/2026-11-02-x106-crowding-plan.md",
        "readout": ("Spearman(distance to the nearest non-ancestor peak, daughter area), the same coordinate against the mother's "
                    "area, and against the daughter's lifetime, with the area effect partialled on lifetime"),
        "cells": cells,
        "positive_control": {"fires": fires,
                             "note": "heredity >= 0.35; the crowding coefficient reproduces X103d within 0.10"},
        "references_x103d": REFS,
        "resolution": RESOLUTION,
        "verdict": verdict,
    }
    if args.write:
        out = Path(__file__).resolve().parents[1] / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x106_crowding.json"
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x106] written: {out.name}")
    for k, v in cells.items():
        print(f"  {k}: pairs={v['pairs']} used={v['used']} cover={v['coverage']} median d_near={v['median_d_near']} "
              f"lifetime={v['median_lifetime']} | rho_area={v['rho_area']} rho_place={v['rho_place']} "
              f"rho_life={v['rho_life']} ({v['worlds_life_positive']}/{v['worlds_measured']} positive) "
              f"area|life={v['rho_area_given_life']} control={v['rho_control']}")
    print("  control:", fires)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
