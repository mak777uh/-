"""x103_analyse.py — X103: is heredity topographic?  Where in the mother's basin, not how big it is.

For every ancestor-daughter pair in X100's stored snapshots: the mother's basin by steepest ascent at her own peak frame, the
daughter's birth position (her centroid at the first logged step at which she exists), and the torus distance between the two.
The question is whether that distance predicts the daughter's excursion-set area — and whether the mother's area survives as a
predictor once the distance is controlled.  Plan: reports/2026-11-02-x103-basin-position-plan.md.

    python scripts/x103_analyse.py --write
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
from x101_analyse import basins, field_for  # noqa: E402
from x102_analyse import world_data  # noqa: E402

CELLS = {"f030": 0.030, "f040": 0.040}
GRID = 96
MIN_PAIRS, MIN_COVERAGE = 100, 0.60
MIN_PAIRS_C = 600         # X103c: both cells must carry ten per-world coefficients of >= 30 pairs
CONTROL_FLOOR = 0.35      # the subset must still carry the heredity the ladder rests on
COVERAGE_LOGGED = 0.90    # X103b's gate: the instrument, not the world's logging resolution
SELECT_MIN, SELECT_MAX = 0.75, 1.33   # kept / dropped median daughter area: is the subset the long-lived tail?
RESOLUTION = 0.10         # declared in the plan: SE 0.024 / 0.032, ~4 sigma
TOP_DIST = 0.20           # "position predicts" — twice the resolution
TOP_DROP = 0.15           # and the mother's area must lose this much once position is known


def torus(a: float, b: float) -> float:
    d = abs(a - b) % GRID
    return min(d, GRID - d)


def labels_at(cache: dict, run_json: Path, step: int):
    key = ("labels", int(step))
    if key in cache:
        return cache[key]
    f = field_for(run_json, int(step))
    if f is None:
        cache[key] = None
        return None
    labels, _ = basins(np.load(f))
    cache[key] = labels
    return labels


def basin_radius(labels, py: int, px: int, lab: int) -> float | None:
    ys, xs = np.nonzero(labels == lab)
    if len(ys) == 0:
        return None
    dy = np.minimum(np.abs(ys - py), GRID - np.abs(ys - py)).astype(float)
    dx = np.minimum(np.abs(xs - px), GRID - np.abs(xs - px)).astype(float)
    return float(np.hypot(dy, dx).max())


def cell_stats_c(flow: float) -> dict:
    """X103c: distance only — no basin, no label, no radius, so nothing but the log decides who is in.

    The two earlier designs lost pairs to the basin definition (a mother on a ridge has no drainage basin) and, at 0.030, the 54
    pairs lost that way turned out to have larger daughters (selection ratio 0.66). This design needs only the mother's peak
    centroid and the daughter's birth centroid, which exist whenever both structures were logged at all — so the only loss is
    structural, and it can be stated as one number instead of hidden in a definition.
    """
    dist, mother_a, daughter_a = [], [], []
    per_world = []
    pairs, logged, used, worlds = 0, 0, 0, 0
    for path in cell_files(("x100",), flow, filename=""):
        w = world_data(path)
        worlds += 1
        wd, wm, wc = [], [], []
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            logged += 1
            mother = w["peak"][par]
            if mother.get("cx") is None:
                continue
            birth = w["first"].get(child) or w["peak"][child]
            if birth.get("cx") is None:
                continue
            d = math.hypot(torus(float(birth["cy"]), float(mother["cy"])),
                           torus(float(birth["cx"]), float(mother["cx"])))
            wd.append(d)
            wm.append(float(mother["area"]))
            wc.append(float(w["peak"][child]["area"]))
            used += 1
        if len(wd) >= 30:
            r = spearman(wd, wc)
            per_world.append({"world": path.name, "pairs": len(wd), "rho_dist": round(r, 3) if r is not None else None})
        dist.extend(wd)
        mother_a.extend(wm)
        daughter_a.extend(wc)

    rho_dist = spearman(dist, daughter_a)
    rho_control = spearman(mother_a, daughter_a)
    rho_partial_area = partial_spearman(mother_a, daughter_a, dist)
    rho_partial_dist = partial_spearman(dist, daughter_a, mother_a)
    signs = [p["rho_dist"] for p in per_world if p["rho_dist"] is not None]
    # the denominator that bit twice: keep the three counts ordered and visible (docs/design-checks.md, X103)
    assert used <= logged <= pairs, (used, logged, pairs)
    return {
        "flow": flow,
        "worlds": worlds,
        "pairs": pairs,
        "pairs_logged": logged,
        "used": used,
        "coverage_logged": round(used / logged, 3) if logged else None,
        "structural_loss": round(1 - logged / pairs, 3) if pairs else None,
        "median_distance": round(float(np.median(dist)), 2) if dist else None,
        "rho_dist": round(rho_dist, 3) if rho_dist is not None else None,
        "rho_control": round(rho_control, 3) if rho_control is not None else None,
        "rho_partial_area": round(rho_partial_area, 3) if rho_partial_area is not None else None,
        "rho_partial_dist": round(rho_partial_dist, 3) if rho_partial_dist is not None else None,
        "drop_area": (round(rho_control - rho_partial_area, 3)
                      if rho_control is not None and rho_partial_area is not None else None),
        "per_world": per_world,
        "worlds_negative": sum(1 for s in signs if s < 0),
        "worlds_measured": len(signs),
    }


def cell_stats(flow: float) -> dict:
    dist, mother_a, daughter_a, radius, outside = [], [], [], [], []
    pairs, logged, used, worlds = 0, 0, 0, 0
    used_keys: set[tuple[str, int]] = set()
    for path in cell_files(("x100",), flow, filename=""):
        w = world_data(path)
        cache: dict = {}
        worlds += 1
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            logged += 1
            mother = w["peak"][par]
            if mother.get("cx") is None:
                continue
            labels = labels_at(cache, path, int(mother["step"]))
            if labels is None:
                continue
            my = int(round(float(mother["cy"]))) % GRID
            mx = int(round(float(mother["cx"]))) % GRID
            lab = int(labels[my, mx])
            if lab < 0:
                continue
            birth = w["first"].get(child) or w["peak"][child]
            if birth.get("cx") is None:
                continue
            by = float(birth["cy"])
            bx = float(birth["cx"])
            d = math.hypot(torus(by, my), torus(bx, mx))
            R = basin_radius(labels, my, mx, lab)
            if R is None or R <= 0:
                continue
            dist.append(d)
            radius.append(R)
            outside.append(d > R)
            mother_a.append(float(mother["area"]))
            daughter_a.append(float(w["peak"][child]["area"]))
            used_keys.add((path.name, child))
            used += 1

    kept_da, dropped_da = [], []
    for path in cell_files(("x100",), flow, filename=""):
        w = world_data(path)
        for child in w["parent"]:
            if child not in w["peak"]:
                continue
            area = float(w["peak"][child]["area"])
            (kept_da if (path.name, child) in used_keys else dropped_da).append(area)
    med_kept = float(np.median(kept_da)) if kept_da else None
    med_dropped = float(np.median(dropped_da)) if dropped_da else None

    rho_dist = spearman(dist, daughter_a)
    rho_r = spearman([d / R for d, R in zip(dist, radius)], daughter_a)
    rho_control = spearman(mother_a, daughter_a)
    rho_partial_area = partial_spearman(mother_a, daughter_a, dist)
    rho_partial_dist = partial_spearman(dist, daughter_a, mother_a)
    return {
        "flow": flow,
        "worlds": worlds,
        "pairs": pairs,
        "pairs_logged": logged,
        "used": used,
        "coverage": round(used / pairs, 3) if pairs else None,
        "coverage_logged": round(used / logged, 3) if logged else None,
        "median_distance": round(float(np.median(dist)), 2) if dist else None,
        "median_basin_radius": round(float(np.median(radius)), 2) if radius else None,
        "frac_outside": round(float(np.mean(outside)), 3) if outside else None,
        "rho_dist": round(rho_dist, 3) if rho_dist is not None else None,
        "rho_r": round(rho_r, 3) if rho_r is not None else None,
        "rho_control": round(rho_control, 3) if rho_control is not None else None,
        "rho_partial_area": round(rho_partial_area, 3) if rho_partial_area is not None else None,
        "rho_partial_dist": round(rho_partial_dist, 3) if rho_partial_dist is not None else None,
        "drop_area": (round(rho_control - rho_partial_area, 3)
                      if rho_control is not None and rho_partial_area is not None else None),
        "median_daughter_kept": round(med_kept, 1) if med_kept is not None else None,
        "median_daughter_dropped": round(med_dropped, 1) if med_dropped is not None else None,
        "selection_ratio": (round(med_kept / med_dropped, 3)
                            if med_kept is not None and med_dropped not in (None, 0) else None),
    }


def verdict_of(cells: dict) -> str:
    vals = [v for v in cells.values()]
    thin = [f"{k}: used {v['used']}, coverage {v['coverage']} (logged-only {v['coverage_logged']})"
            for k, v in cells.items() if v["used"] < MIN_PAIRS or (v["coverage"] or 0) < MIN_COVERAGE]
    if thin:
        return "void: the registered coverage gate failed — " + "; ".join(thin)
    if any((v["rho_control"] or 0) < CONTROL_FLOOR for v in vals):
        return "void: the positive control did not fire on this subset"
    skirt = all(abs(v["rho_dist"] or 0) <= RESOLUTION and abs(v["rho_partial_dist"] or 0) <= RESOLUTION
                and abs(v["drop_area"] or 0) <= RESOLUTION for v in vals)
    topo = all(abs(v["rho_dist"] or 0) >= TOP_DIST and (v["drop_area"] or 0) >= TOP_DROP for v in vals)
    if skirt:
        return ("the skirt reading survives: where a daughter is born inside her mother's basin carries no size information, "
                "and the mother's area keeps its coefficient once the position is controlled — what is inherited is the width "
                "of the excursion, not the valley")
    if topo:
        return ("the topographic reading wins: the birth position predicts the daughter's size, and the mother's area loses "
                "its coefficient once the position is known — heredity is a property of the basin, not of the excursion")
    return "mixed: printed cell by cell, and the two cells disagree, so the answer is not one number"


def verdict_b(cells: dict) -> str:
    """X103b's rule: gate on the instrument's availability, and on the selection ratio."""
    bad = [f"{k}: coverage among loggable pairs {v['coverage_logged']}, selection ratio {v['selection_ratio']}"
           for k, v in cells.items()
           if v["used"] < MIN_PAIRS or (v["coverage_logged"] or 0) < COVERAGE_LOGGED
           or not (SELECT_MIN <= (v["selection_ratio"] or 0) <= SELECT_MAX)
           or (v["rho_control"] or 0) < CONTROL_FLOOR]
    if bad:
        return "void: " + "; ".join(bad)
    vals = list(cells.values())
    skirt = all(abs(v["rho_r"] or 0) <= RESOLUTION and abs(v["drop_area"] or 0) <= RESOLUTION for v in vals)
    topo = all(abs(v["rho_r"] or 0) >= TOP_DIST and (v["drop_area"] or 0) >= TOP_DROP for v in vals)
    additive = (any(abs(v["rho_r"] or 0) >= TOP_DIST for v in vals)
                and all(abs(v["drop_area"] or 0) <= RESOLUTION for v in vals))
    if skirt:
        return ("the skirt reading survives on the normalized radius: where a daughter is born inside her mother's basin "
                "carries no size information, and the mother's area keeps its coefficient once the position is controlled")
    if topo:
        return ("the topographic reading wins on the normalized radius: the birth position predicts the daughter's size, and "
                "the mother's area loses its coefficient once the position is known")
    if additive:
        return ("additive: the position carries information about the daughter's size in at least one cell, but it does not "
                "replace the inherited width — the mother's area keeps its coefficient when the position is controlled, so the "
                "medium passes an excursion width AND the daughter's place inside the valley matters")
    return "mixed: the cells disagree, so the answer is not one number — printed cell by cell"


def verdict_c(cells: dict) -> str:
    """X103c's rule: distance only; gate on usable pairs and on the heredity control."""
    bad = [f"{k}: used {v['used']}, coverage among loggable pairs {v['coverage_logged']}, control {v['rho_control']}"
           for k, v in cells.items()
           if v["used"] < MIN_PAIRS_C or (v["coverage_logged"] or 0) < COVERAGE_LOGGED
           or (v["rho_control"] or 0) < CONTROL_FLOOR]
    if bad:
        return "void: " + "; ".join(bad)
    vals = list(cells.values())
    skirt = all(abs(v["rho_dist"] or 0) <= RESOLUTION and abs(v["drop_area"] or 0) <= RESOLUTION for v in vals)
    topo = all(abs(v["rho_dist"] or 0) >= TOP_DIST and (v["drop_area"] or 0) >= TOP_DROP for v in vals)
    additive = (any(abs(v["rho_dist"] or 0) >= TOP_DIST for v in vals)
                and all(abs(v["drop_area"] or 0) <= RESOLUTION for v in vals))
    if skirt:
        return ("the skirt reading survives: the birth distance carries no size information, and the mother's area keeps its "
                "coefficient once the distance is controlled — what is inherited is the width of the excursion, not the valley")
    if topo:
        return ("the topographic reading wins: the birth distance predicts the daughter's size, and the mother's area loses its "
                "coefficient once the distance is known")
    if additive:
        return ("additive: the birth distance carries size information in at least one cell, but the mother's area keeps its "
                "coefficient once the distance is controlled — the medium passes an excursion width and the daughter's place "
                "inside the valley adds a term")
    return ("mixed: the cells disagree, so the answer is not one number — and the next step is denser logging (X105), not "
            "another analysis of these artifacts")


def ancestors_of(parent: dict[int, int], uid: int, depth: int = 6) -> set[int]:
    out = {uid}
    cur = uid
    for _ in range(depth):
        nxt = parent.get(cur)
        if nxt is None or nxt in out:
            break
        out.add(nxt)
        cur = nxt
    return out


def cell_stats_d(flow: float) -> dict:
    """X103d: the mother's peak versus the nearest non-ancestor peak at the daughter's birth step."""
    d_mother, d_other, mother_a, daughter_a = [], [], [], []
    per_world = []
    pairs, logged, used, worlds = 0, 0, 0, 0
    for path in cell_files(("x100",), flow, filename=""):
        w = world_data(path)
        worlds += 1
        wm, wo, wa, wc = [], [], [], []
        for child, par in w["parent"].items():
            pairs += 1
            if child not in w["peak"] or par not in w["peak"]:
                continue
            logged += 1
            mother = w["peak"][par]
            birth = w["first"].get(child) or w["peak"][child]
            if mother.get("cx") is None or birth.get("cx") is None:
                continue
            comps = w["per_step"].get(int(birth["step"])) or []
            if not comps:
                continue
            ban = ancestors_of(w["parent"], child)
            by, bx = float(birth["cy"]), float(birth["cx"])
            best = None
            for c in comps:
                uid = int(c["uid"])
                if uid in ban or c.get("cx") is None:
                    continue
                dd = math.hypot(torus(float(c["cy"]), by), torus(float(c["cx"]), bx))
                if best is None or dd < best:
                    best = dd
            if best is None:
                continue
            dm = math.hypot(torus(float(birth["cy"]), float(mother["cy"])),
                            torus(float(birth["cx"]), float(mother["cx"])))
            wm.append(dm)
            wo.append(best)
            wa.append(float(mother["area"]))
            wc.append(float(w["peak"][child]["area"]))
            used += 1
        if len(wm) >= 30:
            r1, r2 = spearman(wm, wc), spearman(wo, wc)
            per_world.append({"world": path.name, "pairs": len(wm),
                              "rho_mother": round(r1, 3) if r1 is not None else None,
                              "rho_other": round(r2, 3) if r2 is not None else None})
        d_mother.extend(wm)
        d_other.extend(wo)
        mother_a.extend(wa)
        daughter_a.extend(wc)

    rho_m = spearman(d_mother, daughter_a)
    rho_o = spearman(d_other, daughter_a)
    rho_c = spearman(mother_a, daughter_a)
    assert used <= logged <= pairs, (used, logged, pairs)
    return {
        "flow": flow,
        "worlds": worlds,
        "pairs": pairs,
        "pairs_logged": logged,
        "used": used,
        "coverage_logged": round(used / logged, 3) if logged else None,
        "median_d_mother": round(float(np.median(d_mother)), 2) if d_mother else None,
        "median_d_other": round(float(np.median(d_other)), 2) if d_other else None,
        "rho_mother": round(rho_m, 3) if rho_m is not None else None,
        "rho_other": round(rho_o, 3) if rho_o is not None else None,
        "contrast": (round(abs(rho_m) - abs(rho_o), 3)
                     if rho_m is not None and rho_o is not None else None),
        "rho_control": round(rho_c, 3) if rho_c is not None else None,
        "per_world": per_world,
        "worlds_mother_negative": sum(1 for p in per_world
                                      if p["rho_mother"] is not None and p["rho_mother"] < 0),
        "worlds_other_negative": sum(1 for p in per_world
                                     if p["rho_other"] is not None and p["rho_other"] < 0),
        "worlds_measured": len(per_world),
    }


def verdict_d(cells: dict, refs: dict) -> str:
    """X103d: is the maze-cell signal maternal or local geometry?"""
    bad = []
    for k, v in cells.items():
        if v["used"] < MIN_PAIRS or (v["coverage_logged"] or 0) < 0.60:
            bad.append(f"{k}: only {v['used']} contrast pairs at coverage {v['coverage_logged']}")
        if (v["rho_control"] or 0) < CONTROL_FLOOR:
            bad.append(f"{k}: heredity control {v['rho_control']} below {CONTROL_FLOOR}")
        if v["rho_mother"] is None or abs(v["rho_mother"] - refs[k]) > 0.10:
            bad.append(f"{k}: mother-distance coefficient {v['rho_mother']} does not reproduce X103c's {refs[k]}")
    if bad:
        return "void: " + "; ".join(bad)
    maze = cells["f040"]
    lat = cells["f030"]
    why = (f"lattice: mother {lat['rho_mother']}, stranger peaks {lat['rho_other']}; "
           f"maze: mother {maze['rho_mother']}, stranger peaks {maze['rho_other']}, contrast {maze['contrast']}")
    if abs(maze["rho_other"] or 0) >= 0.20 and (maze["contrast"] or 0) <= 0.10:
        return ("local geometry wins in the maze cell: stranger peaks predict the daughter's size as well as her mother's, so "
                f"the negative distance term is about where she sits in the medium, not about her mother — {why}")
    if abs(maze["rho_mother"] or 0) >= 0.20 and (maze["contrast"] or 0) >= 0.15:
        return ("maternal: the mother's position carries information that other peaks do not, so the term is about the mother — "
                f"{why}")
    if abs(maze["rho_other"] or 0) < 0.20 and abs(maze["rho_mother"] or 0) < 0.20:
        return f"nothing to explain in either cell — {why}"
    return f"mixed: neither reading is separated cleanly — {why}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X103 birth position inside the mother's basin")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--b", action="store_true", help="X103b: gate on coverage among loggable pairs and on the selection ratio")
    ap.add_argument("--c", action="store_true", help="X103c: distance only, no basin")
    ap.add_argument("--d", action="store_true", help="X103d: mother's peak versus the nearest non-ancestor peak")
    args = ap.parse_args(argv)

    if args.d:
        refs = {"f030": -0.008, "f040": -0.367}   # X103c, the registered reference
        cells = {tag: cell_stats_d(flow) for tag, flow in CELLS.items()}
        verdict = verdict_d(cells, refs)
        fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
        res = {
            "kind": "l1_field_x103d_peak_null",
            "experiment": "X103d",
            "command": "python scripts/x103_analyse.py --d --write",
            "prereg": "reports/2026-11-02-x103d-peak-null-plan.md",
            "readout": ("Spearman(distance to the mother's peak, daughter's area) against Spearman(distance to the nearest "
                        "non-ancestor peak at her birth step, daughter's area), on the same pairs"),
            "cells": cells,
            "positive_control": {"fires": fires,
                                 "note": "heredity >= 0.35 and the mother-distance coefficient reproduces X103c within 0.10"},
            "references_x103c": refs,
            "resolution": RESOLUTION,
            "verdict": verdict,
        }
        if args.write:
            out = Path(__file__).resolve().parents[1] / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x103d_peak_null.json"
            out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[x103d] written: {out.name}")
        for k, v in cells.items():
            print(f"  {k}: pairs={v['pairs']} used={v['used']} cover={v['coverage_logged']} "
                  f"median d_mother={v['median_d_mother']} d_other={v['median_d_other']} | "
                  f"rho_mother={v['rho_mother']} rho_other={v['rho_other']} contrast={v['contrast']} "
                  f"control={v['rho_control']} worlds(-) mother {v['worlds_mother_negative']}/{v['worlds_measured']}, "
                  f"other {v['worlds_other_negative']}/{v['worlds_measured']}")
            for p in v["per_world"]:
                print(f"      {p['world']}: n={p['pairs']} mother={p['rho_mother']} other={p['rho_other']}")
        print("  control:", fires)
        print("  verdict:", verdict)
        return 0

    if args.c:
        cells = {tag: cell_stats_c(flow) for tag, flow in CELLS.items()}
        verdict = verdict_c(cells)
        fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
        res = {
            "kind": "l1_field_x103c_birth_distance",
            "experiment": "X103c",
            "command": "python scripts/x103_analyse.py --c --write",
            "prereg": "reports/2026-11-02-x103c-birth-distance-plan.md",
            "readout": ("Spearman(torus distance from the mother's peak centroid to the daughter's birth centroid, daughter's "
                        "peak area), with the partial of the mother's area given the distance, the partial of the distance given "
                        "the mother's area, and a per-world coefficient table"),
            "cells": cells,
            "positive_control": {"fires": fires, "note": "rho(mother area, daughter area) >= 0.35 on the kept pairs"},
            "coverage_gate": COVERAGE_LOGGED,
            "resolution": RESOLUTION,
            "verdict": verdict,
        }
        if args.write:
            out = Path(__file__).resolve().parents[1] / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x103c_birth_distance.json"
            out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[x103c] written: {out.name}")
        for k, v in cells.items():
            print(f"  {k}: pairs={v['pairs']} used={v['used']} cover_logged={v['coverage_logged']} "
                  f"median d={v['median_distance']} | rho_dist={v['rho_dist']} control={v['rho_control']} "
                  f"partial_area={v['rho_partial_area']} partial_dist={v['rho_partial_dist']} drop={v['drop_area']} "
                  f"worlds {v['worlds_negative']}/{v['worlds_measured']} negative")
            for p in v["per_world"]:
                print(f"      {p['world']}: n={p['pairs']} rho={p['rho_dist']}")
        print("  control:", fires)
        print("  verdict:", verdict)
        return 0

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    if args.b:
        verdict = verdict_b(cells)
        fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
        res = {
            "kind": "l1_field_x103b_basin_position",
            "experiment": "X103b",
            "command": "python scripts/x103_analyse.py --b --write",
            "prereg": "reports/2026-11-02-x103b-basin-position-plan.md",
            "readout": ("Spearman(r, daughter's peak area) with r = distance / R_basin, the partial of the mother's area given r, "
                        "the partial of r given the mother's area, and the selection ratio of median daughter areas "
                        "kept / dropped"),
            "cells": cells,
            "positive_control": {
                "fires": fires,
                "note": "rho(mother area, daughter area) >= 0.35 on the kept pairs; and the selection ratio kept/dropped in "
                        "[0.75, 1.33]",
            },
            "selection_band": [SELECT_MIN, SELECT_MAX],
            "coverage_gate": COVERAGE_LOGGED,
            "resolution": RESOLUTION,
            "verdict": verdict,
        }
        name = "l1_field_x103b_basin_position.json"
    else:
        verdict = verdict_of(cells)
        fires = all((v["rho_control"] or 0) >= CONTROL_FLOOR for v in cells.values())
        res = {
            "kind": "l1_field_x103_basin_position",
            "experiment": "X103",
            "command": "python scripts/x103_analyse.py --write",
            "prereg": "reports/2026-11-02-x103-basin-position-plan.md",
            "readout": ("Spearman(torus distance from the mother's peak to the daughter's birth centroid, daughter's peak area), "
                        "and the same on the normalized radius, with partial correlations against the mother's excursion area"),
            "cells": cells,
            "positive_control": {"fires": fires, "note": "rho(mother area, daughter area) >= 0.35 on the same subset"},
            "selection_band": [SELECT_MIN, SELECT_MAX],
            "coverage_gate": MIN_COVERAGE,
            "resolution": RESOLUTION,
            "verdict": verdict,
        }
        name = "l1_field_x103_basin_position.json"
    if args.write:
        out = Path(__file__).resolve().parents[1] / "morphogenesis" / "experiments" / "E09_pond" / name
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x103] written: {out.name}")
    for k, v in cells.items():
        print(f"  {k}: pairs={v['pairs']} logged={v['pairs_logged']} used={v['used']} cover={v['coverage']} "
              f"cover_logged={v['coverage_logged']} selected={v['selection_ratio']} "
              f"({v['median_daughter_kept']} vs {v['median_daughter_dropped']}) "
              f"median d={v['median_distance']} R={v['median_basin_radius']} outside={v['frac_outside']} | "
              f"rho_dist={v['rho_dist']} rho_r={v['rho_r']} control={v['rho_control']} "
              f"partial_area={v['rho_partial_area']} partial_dist={v['rho_partial_dist']} drop={v['drop_area']}")
    print("  control:", fires)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
