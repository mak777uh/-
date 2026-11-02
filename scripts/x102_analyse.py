"""x102_analyse.py — does the SPECIFICITY of inheritance (parent beats neighbour) survive a weaker size definition?

X91 established, under the excursion set at 0.20, that a daughter's area follows her parent (0.39-0.55) far more than her nearest
non-ancestor (0.06-0.25). X101 then showed the *level* of heredity collapses down a ladder of definitions: 0.531/0.384 for the excursion
set, 0.300/0.174 for a topological basin, 0.176/0.058 for a relative core. The open question is whether the *gap* — the part X91 measured
— also collapses, or whether specificity is robust where the level is not.

Analysis only, on the snapshots X100 already saved.

Run:
    python scripts/x102_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x100_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x102_specificity_ladder.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402
from field_metrics import cell_files  # noqa: E402
from x101_analyse import basins, field_for  # noqa: E402

CELLS = {"f030": 0.030, "f040": 0.040}
GRID = 96
MIN_PAIRS, MIN_COVERAGE = 100, 0.80
GAP_ROBUST = 0.15   # X91's bar under the strong definition
GAP_SHRINKS = 0.15  # a fall of this size in the gap means specificity is definition-bound too


def world_data(run_json: Path) -> dict:
    """Пики (площадь, центроид, шаг) по uid + кэш бассейнов по (uid, шаг)."""
    d = json.loads(run_json.read_text(encoding="utf-8"))
    peak: dict[int, dict] = {}
    first: dict[int, dict] = {}
    per_step: dict[int, list[dict]] = {}
    for row in (d.get("series") or []):
        step = int(row.get("step") or 0)
        comps = row.get("components_log") or []
        per_step[step] = comps
        for c in comps:
            uid = int(c["uid"])
            area = float(c.get("area") or 0)
            if uid not in first:
                first[uid] = {"step": step, "cx": c.get("cx"), "cy": c.get("cy")}
            if uid not in peak or area > float(peak[uid].get("area") or 0):
                peak[uid] = {"area": area, "cx": c.get("cx"), "cy": c.get("cy"), "step": step}
    return {"peak": peak, "first": first, "per_step": per_step,
            "parent": {int(b): int(a) for a, b in (d.get("uid_pairs") or [])}}


def labels_for(cache: dict, run_json: Path, step: int) -> np.ndarray | None:
    """Basin labels of one saved frame, cached by step (labels are per frame)."""
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


def pixel(cy, cx) -> tuple[int, int]:
    return int(round(float(cy))) % GRID, int(round(float(cx))) % GRID


def basin_of(cache: dict, run_json: Path, uid: int, info: dict) -> tuple[float | None, int | None]:
    """(area, label) of the steepest-ascent basin holding this uid's peak pixel."""
    if info.get("cx") is None:
        return None, None
    labels = labels_for(cache, run_json, int(info["step"]))
    if labels is None:
        return None, None
    yi, xi = pixel(info["cy"], info["cx"])
    lab = int(labels[yi, xi])
    return (float((labels == lab).sum()), lab) if lab >= 0 else (None, None)


def shares_basin(cache: dict, run_json: Path, host: dict, guest: dict) -> bool | None:
    """Is the guest's peak site inside the host's basin, **in the host's own frame**?

    Labels are assigned per frame, so comparing a label from one snapshot with a
    label from another is meaningless.  The only honest degeneracy check is a
    same-frame containment question.
    """
    if host.get("cx") is None or guest.get("cx") is None:
        return None
    labels = labels_for(cache, run_json, int(host["step"]))
    if labels is None:
        return None
    hy, hx = pixel(host["cy"], host["cx"])
    gy, gx = pixel(guest["cy"], guest["cx"])
    lh, lg = int(labels[hy, hx]), int(labels[gy, gx])
    if lh < 0 or lg < 0:
        return None
    return lh == lg


def chain_of(parent: dict[int, int], uid: int) -> set[int]:
    out, cur = set(), uid
    while cur is not None:
        out.add(cur)
        cur = parent.get(cur)
    return out


def nearest_stranger(world: dict, uid: int) -> int | None:
    """Ближайший не-предок в снимке первого появления uid (как x73_depth.stranger_peak, но возвращает uid)."""
    f = world["first"].get(uid)
    if f is None:
        return None
    step, cx, cy = f["step"], f["cx"], f["cy"]
    if cx is None:
        return None
    blocked = chain_of(world["parent"], uid)
    best = None
    for c in world["per_step"].get(step, []):
        other = int(c["uid"])
        if other in blocked or c.get("cx") is None:
            continue
        dx = min(abs(float(c["cx"]) - float(cx)), GRID - abs(float(c["cx"]) - float(cx)))
        dy = min(abs(float(c["cy"]) - float(cy)), GRID - abs(float(c["cy"]) - float(cy)))
        d = math.hypot(dx, dy)
        if best is None or d < best[0]:
            best = (d, other)
    return best[1] if best else None


def cell_stats(flow_tag: str, flow: float) -> dict:
    parent_a, parent_d, stranger_a, stranger_d = [], [], [], []
    b_parent_a, b_parent_d, b_stranger_a, b_stranger_d = [], [], [], []
    same_stranger_hits, same_parent_hits = 0, 0
    n_same_stranger, n_same_parent = 0, 0
    pairs, covered, expected, worlds = 0, 0, 0, 0
    for path in cell_files(("x100",), flow, filename=""):
        w = world_data(path)
        cache: dict = {}
        worlds += 1
        for child, par in w["parent"].items():
            if child not in w["peak"] or par not in w["peak"]:
                continue
            pairs += 1
            expected += 1
            s = nearest_stranger(w, child)
            parent_a.append(w["peak"][par]["area"])
            parent_d.append(w["peak"][child]["area"])
            bs, ls = basin_of(cache, path, par, w["peak"][par])
            bc, lc = basin_of(cache, path, child, w["peak"][child])
            if s is not None and s in w["peak"]:
                stranger_a.append(w["peak"][s]["area"])
                stranger_d.append(w["peak"][child]["area"])
                bst, _ = basin_of(cache, path, s, w["peak"][s])
                if None not in (bst, bc, bs):
                    b_stranger_a.append(bst)
                    b_stranger_d.append(bc)
                    b_parent_a.append(bs)
                    b_parent_d.append(bc)
                    covered += 1
                    same_s = shares_basin(cache, path, w["peak"][s], w["peak"][child])
                    same_p = shares_basin(cache, path, w["peak"][par], w["peak"][child])
                    if same_s is not None:
                        n_same_stranger += 1
                        same_stranger_hits += int(same_s)
                    if same_p is not None:
                        n_same_parent += 1
                        same_parent_hits += int(same_p)
    rho_p = spearman(parent_a, parent_d)
    rho_s = spearman(stranger_a, stranger_d)
    brho_p = spearman(b_parent_a, b_parent_d)
    brho_s = spearman(b_stranger_a, b_stranger_d)
    gap_thr = round(rho_p - rho_s, 3) if rho_p is not None and rho_s is not None else None
    gap_basin = round(brho_p - brho_s, 3) if brho_p is not None and brho_s is not None else None
    return {"flow": flow, "worlds": worlds, "pairs": pairs,
            "coverage_basin": round(covered / expected, 3) if expected else None,
            "stranger_same_basin": round(same_stranger_hits / n_same_stranger, 3) if n_same_stranger else None,
            "parent_same_basin": round(same_parent_hits / n_same_parent, 3) if n_same_parent else None,
            "n_same_basin": n_same_stranger,
            "rho_parent_threshold": round(rho_p, 3) if rho_p is not None else None,
            "rho_stranger_threshold": round(rho_s, 3) if rho_s is not None else None,
            "gap_threshold": gap_thr,
            "rho_parent_basin": round(brho_p, 3) if brho_p is not None else None,
            "rho_stranger_basin": round(brho_s, 3) if brho_s is not None else None,
            "gap_basin": gap_basin,
            "gap_change": (round(gap_basin - gap_thr, 3) if gap_basin is not None and gap_thr is not None else None),
            "n_basin_pairs": len(b_parent_a)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X102 specificity down the ladder")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x102_specificity_ladder", "experiment": "X102",
           "command": "python scripts/x102_analyse.py --write",
           "prereg": "reports/2026-11-02-x102-specificity-plan.md",
           "readout": "Spearman(parent, daughter) minus Spearman(nearest non-ancestor, daughter), under the excursion-set area and under "
                      "the topological basin area, on the same daughters",
           "cells": {}}
    for name, flow in CELLS.items():
        res["cells"][name] = cell_stats(name, flow)
    c = res["cells"]

    control_ok = all(v["gap_threshold"] is not None and v["gap_threshold"] > 0 for v in c.values())
    res["positive_control"] = {"fires": bool(control_ok),
                               "note": "the threshold gap must be positive in both cells — that is X91's result reproduced on these worlds"}
    void = [k for k, v in c.items()
            if (v["pairs"] or 0) < MIN_PAIRS or (v["coverage_basin"] or 0) < MIN_COVERAGE or v["gap_basin"] is None]

    changes = {k: v["gap_change"] for k, v in c.items()}
    if not control_ok:
        verdict = "void: the threshold gap is not positive, so X91's result does not reproduce on these worlds"
    elif void:
        verdict = f"void: underpowered or unreadable cells: {void}"
    elif all(ch is not None and abs(ch) < GAP_SHRINKS for ch in changes.values()) and \
            all(v["gap_basin"] is not None and v["gap_basin"] >= GAP_ROBUST for v in c.values()):
        verdict = "specificity is robust: the parent-versus-neighbour gap keeps its size under the weaker definition, so specificity is not definition-bound even though the level is"
    elif any(ch is not None and ch <= -GAP_SHRINKS for ch in changes.values()):
        verdict = "specificity is definition-bound too: the gap collapses under the weaker definition, so heredity in this medium is an excursion-set concept through and through"
    else:
        verdict = "mixed"
    res["gap_changes"] = changes
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x102] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k}: threshold parent={v['rho_parent_threshold']} stranger={v['rho_stranger_threshold']} gap={v['gap_threshold']} | "
              f"basin parent={v['rho_parent_basin']} stranger={v['rho_stranger_basin']} gap={v['gap_basin']} "
              f"change={v['gap_change']} pairs={v['pairs']} cover={v['coverage_basin']}")
    print("  control:", res["positive_control"]["fires"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
