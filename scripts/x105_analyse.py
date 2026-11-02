"""x105_analyse.py — X105: does the maternal-decay term survive dense logging?

X103c measured a maternal decay of size at F = 0.040: rho(distance from the mother's peak to the daughter's birth site, daughter's
area) = -0.367, ten worlds out of ten. But 35.3 % of the maze cell's ancestor-daughter pairs have a member that was never logged, so
every maze number describes long-lived structures only. X105 reran both cells at --sample-every 10 and this analysis asks whether the
term is still there when nine times more structures are visible.

Plan: reports/2026-11-02-x105-dense-logging-plan.md.

    python scripts/x105_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import partial_spearman  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x103_analyse import torus  # noqa: E402
from x106_analyse import nearest_nonancestor  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x105_dense.json"

CELLS = {"f030": 0.030, "f040": 0.040}
MIN_PAIRS = 100
MAX_STRUCTURAL_LOSS = 0.10
CONTROL_FLOOR = 0.35
RESOLUTION = 0.10
REFERENCES = {"f030": -0.008, "f040": -0.367}     # X103c's distance coefficients
MAZE_FLOOR = -0.20
LATTICE_BAND = 0.15
CROWD_REFERENCES = {"f030": 0.358, "f040": 0.103}  # X103d's crowding coefficients


def world_files(tag: str) -> list[Path]:
    return sorted(L1.glob(f"x105_{tag}_s*.json"))


def cell_stats(tag: str, flow: float) -> dict:
    dist, crowd, mother_a, daughter_a = [], [], [], []
    per_world = []
    pairs = logged = used = 0
    for path in world_files(tag):
        w = world_data(path)
        wd, wc, wm, wa = [], [], [], []
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            logged += 1
            mother = w["peak"][par]
            birth = w["first"].get(child) or w["peak"][child]
            if mother.get("cx") is None or birth.get("cx") is None:
                continue
            d = math.hypot(torus(float(birth["cy"]), float(mother["cy"])),
                           torus(float(birth["cx"]), float(mother["cx"])))
            comps = w["per_step"].get(int(birth["step"])) or []
            dc = nearest_nonancestor(comps, w["parent"], child, float(birth["cy"]), float(birth["cx"]))
            wd.append(d)
            wc.append(dc if dc is not None else float("nan"))
            wm.append(float(mother["area"]))
            wa.append(float(w["peak"][child]["area"]))
            used += 1
        if len(wd) >= 30:
            valid = [(c, a) for c, a in zip(wc, wa) if not math.isnan(c)]
            r_dist = spearman(wd, wa)
            r_crowd = spearman([c for c, _ in valid], [a for _, a in valid]) if len(valid) >= 30 else None
            per_world.append({"world": path.name, "pairs": len(wd),
                              "rho_dist": round(r_dist, 3) if r_dist is not None else None,
                              "rho_crowd": round(r_crowd, 3) if r_crowd is not None else None})
        for a, b, c, e in zip(wd, wc, wm, wa):
            dist.append(a)
            crowd.append(b)
            mother_a.append(c)
            daughter_a.append(e)

    valid_pairs = [(c, d) for c, d in zip(crowd, daughter_a) if not math.isnan(c)]
    rho_dist = spearman(dist, daughter_a)
    rho_control = spearman(mother_a, daughter_a)
    rho_partial = partial_spearman(mother_a, daughter_a, dist)
    rho_crowd = spearman([c for c, _ in valid_pairs], [a for _, a in valid_pairs]) if valid_pairs else None
    signs_d = [p["rho_dist"] for p in per_world if p["rho_dist"] is not None]
    signs_c = [p["rho_crowd"] for p in per_world if p["rho_crowd"] is not None]
    assert used <= logged <= pairs, (used, logged, pairs)
    return {
        "flow": flow,
        "worlds": len(per_world),
        "pairs": pairs,
        "pairs_logged": logged,
        "used": used,
        "coverage_logged": round(used / logged, 3) if logged else None,
        "structural_loss": round(1 - logged / pairs, 3) if pairs else None,
        "median_distance": round(float(np.median(dist)), 2) if dist else None,
        "rho_dist": round(rho_dist, 3) if rho_dist is not None else None,
        "rho_control": round(rho_control, 3) if rho_control is not None else None,
        "rho_partial_area": round(rho_partial, 3) if rho_partial is not None else None,
        "rho_crowd": round(rho_crowd, 3) if rho_crowd is not None else None,
        "per_world": per_world,
        "worlds_dist_negative": sum(1 for s in signs_d if s < 0),
        "worlds_crowd_positive": sum(1 for s in signs_c if s > 0),
        "worlds_measured": len(signs_d),
    }


def verdict_of(cells: dict) -> str:
    bad = []
    for k, v in cells.items():
        if v["used"] < MIN_PAIRS:
            bad.append(f"{k}: {v['used']} pairs")
        if (v["structural_loss"] or 0) >= MAX_STRUCTURAL_LOSS:
            bad.append(f"{k}: structural loss {v['structural_loss']} >= {MAX_STRUCTURAL_LOSS}")
        if (v["rho_control"] or 0) < CONTROL_FLOOR:
            bad.append(f"{k}: heredity {v['rho_control']} below {CONTROL_FLOOR}")
    maze, lat = cells["f040"], cells["f030"]
    if maze["rho_dist"] is None or maze["rho_dist"] > 0:
        bad.append(f"f040: distance coefficient {maze['rho_dist']} is not negative (sign contradicts X103c)")
    if lat["rho_dist"] is None or abs(lat["rho_dist"]) > LATTICE_BAND:
        bad.append(f"f030: distance coefficient {lat['rho_dist']} outside +-{LATTICE_BAND} (contradicts X103c)")
    if bad:
        return "void: " + "; ".join(bad)
    parts = [f"maze distance {maze['rho_dist']} ({maze['worlds_dist_negative']}/{maze['worlds_measured']} worlds negative)"]
    if (maze["rho_dist"] or 0) <= MAZE_FLOOR and maze["worlds_dist_negative"] >= 8:
        parts.append("the maternal decay is robust to dense logging")
    elif abs(maze["rho_dist"] or 0) <= RESOLUTION or maze["worlds_dist_negative"] < 6:
        parts.append("the maternal decay was a selection artefact of the long-lived structures")
    else:
        parts.append("the maternal decay is weaker than at X100's density but not gone")
    parts.append(f"lattice crowding {lat['rho_crowd']} ({lat['worlds_crowd_positive']}/{lat['worlds_measured']} worlds positive)")
    if (lat["rho_crowd"] or 0) >= 0.20 and lat["worlds_crowd_positive"] >= 8:
        parts.append("crowding is robust")
    elif abs(lat["rho_crowd"] or 0) <= RESOLUTION or lat["worlds_crowd_positive"] < 6:
        parts.append("crowding is not robust")
    else:
        parts.append("crowding is weaker but present")
    return "; ".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X105 dense logging")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(tag, flow) for tag, flow in CELLS.items()}
    verdict = verdict_of(cells)
    fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
    res = {
        "kind": "l1_field_x105_dense",
        "experiment": "X105",
        "command": "python scripts/x105_analyse.py --write",
        "prereg": "reports/2026-11-02-x105-dense-logging-plan.md",
        "series": "twenty runs, seeds 301-310 per inflow, --sample-every 10",
        "readout": ("structural loss; health of the genealogies; rho(distance, daughter area) against X103c's references; "
                    "rho(distance to the nearest non-ancestor peak, daughter area) against X103d's"),
        "cells": cells,
        "positive_control": {"fires": fires,
                             "note": "heredity >= 0.35; maze distance coefficient negative and <= -0.20; lattice within +-0.15"},
        "references": {"distance": REFERENCES, "crowding": CROWD_REFERENCES},
        "resolution": RESOLUTION,
        "verdict": verdict,
    }
    if args.write:
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x105] written: {OUT.name}")
    for k, v in cells.items():
        print(f"  {k}: worlds={v['worlds']} pairs={v['pairs']} logged={v['pairs_logged']} used={v['used']} "
              f"structural_loss={v['structural_loss']} cover={v['coverage_logged']} median d={v['median_distance']} | "
              f"rho_dist={v['rho_dist']} ({v['worlds_dist_negative']}/{v['worlds_measured']} -) "
              f"crowd={v['rho_crowd']} ({v['worlds_crowd_positive']}/{v['worlds_measured']} +) "
              f"control={v['rho_control']} partial_area={v['rho_partial_area']}")
        for p in v["per_world"]:
            print(f"      {p['world']}: n={p['pairs']} dist={p['rho_dist']} crowd={p['rho_crowd']}")
    print("  control:", fires)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
