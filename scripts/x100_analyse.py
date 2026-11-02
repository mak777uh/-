"""x100_analyse.py — does the heredity of size survive a definition that needs no excursion cut?

Criteria: `reports/2026-11-02-x100-cutfree-plan.md`.

For every structure (uid) the analysis takes the snapshot where its logged area is largest — that is its peak — and measures two sizes on
the same field:

* `area` — the threshold-0.20 component area from the log (the committed definition);
* `S_cf` — the integral of `v` over the basin around the uid's centroid, the basin being the 4-connected set (with wrap) where
  `v >= 0.5 * max(v)` inside a neighbourhood of the centroid. No global threshold enters;
* `A_cf` — the number of cells in that basin.

Then Spearman(ancestor, descendant) at lag 1 is computed for each definition on the same pair set, so the comparison is paired.

Run:
    python scripts/x100_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x100_cutfree.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402
from field_metrics import cell_files  # noqa: E402

CELLS = {"f030": (("x100",), 0.030), "f040": (("x100",), 0.040)}
REFERENCE = {0.030: 0.549, 0.040: 0.471}
CONTROL_BAND = {0.030: (0.50, 0.60), 0.040: (0.42, 0.52)}
MIN_PAIRS, MIN_COVERAGE = 100, 0.80
SURVIVES = 0.10
DEFINITION_BOUND = 0.20
HOOD = 12          # радиус окрестности центроида, клеток
FLOOR_SPLIT = 0.5  # бассейн — половина собственного максимума


def field_for(run_json: Path, step: int) -> Path | None:
    p = FIELDS / f"{run_json.stem}_t{step}.npy"
    return p if p.is_file() else None


def basin(field: np.ndarray, cx: float, cy: float) -> dict:
    """Компонента без порога: максимум в окрестности и связная область >= 0.5 от него."""
    g = field.shape[0]
    xi, yi = int(round(cx)) % g, int(round(cy)) % g
    xs = (np.arange(xi - HOOD, xi + HOOD + 1)) % g
    ys = (np.arange(yi - HOOD, yi + HOOD + 1)) % g
    hood = field[np.ix_(ys, xs)]
    peak = float(hood.max())
    if peak <= 0:
        return {"S_cf": None, "A_cf": None}
    cut = FLOOR_SPLIT * peak
    seen = np.zeros_like(field, dtype=bool)
    stack = [(yi, xi)]
    total, count = 0.0, 0
    while stack:
        y, x = stack.pop()
        if seen[y, x] or field[y, x] < cut:
            continue
        seen[y, x] = True
        total += float(field[y, x])
        count += 1
        stack.extend((((y + 1) % g, x), ((y - 1) % g, x), (y, (x + 1) % g), (y, (x - 1) % g)))
    return {"S_cf": total, "A_cf": count}


def world_sizes(run_json: Path) -> dict:
    d = json.loads(run_json.read_text(encoding="utf-8"))
    peak_row: dict[int, dict] = {}
    for row in (d.get("series") or []):
        for c in (row.get("components_log") or []):
            uid = int(c["uid"])
            area = float(c.get("area") or 0)
            if uid not in peak_row or area > float(peak_row[uid].get("area") or 0):
                peak_row[uid] = {"area": area, "cx": c.get("cx"), "cy": c.get("cy"), "step": row.get("step")}
    out = {"area": {}, "S_cf": {}, "A_cf": {}}
    for uid, info in peak_row.items():
        out["area"][uid] = info["area"]
        f = field_for(run_json, int(info["step"]))
        if f is None or info["cx"] is None:
            continue
        got = basin(np.load(f), float(info["cx"]), float(info["cy"]))
        if got["S_cf"] is not None:
            out["S_cf"][uid] = got["S_cf"]
            out["A_cf"][uid] = got["A_cf"]
    return out


def cell_stats(series, flow: float) -> dict:
    per_def = {"area": ([], []), "S_cf": ([], []), "A_cf": ([], [])}
    worlds, pairs_total, covered, expected = 0, 0, 0, 0
    for path in cell_files(series, flow, filename=""):
        sizes = world_sizes(path)
        worlds += 1
        links = json.loads(path.read_text(encoding="utf-8")).get("uid_pairs") or []
        parent = {}
        for a, b in links:
            parent[int(b)] = int(a)
        for child, par in parent.items():
            pairs_total += 1
            expected += 1
            if child in sizes["S_cf"]:
                covered += 1
            for name, (ax, ay) in per_def.items():
                if par in sizes[name] and child in sizes[name]:
                    ax.append(sizes[name][par])
                    ay.append(sizes[name][child])
    out = {"flow": flow, "worlds": worlds, "pairs": pairs_total,
           "basin_coverage": round(covered / expected, 3) if expected else None}
    for name, (ax, ay) in per_def.items():
        rho = spearman(ax, ay)
        out[f"rho1_{name}"] = round(rho, 3) if rho is not None else None
        out[f"n_{name}"] = len(ax)
        out[f"median_{name}"] = round(st.median(ax), 1) if ax else None
    out["reference_rho1"] = REFERENCE[flow]
    out["delta"] = round(out["rho1_S_cf"] - REFERENCE[flow], 3) if out["rho1_S_cf"] is not None else None
    out["paired_delta"] = (round(out["rho1_S_cf"] - out["rho1_area"], 3)
                           if out["rho1_S_cf"] is not None and out["rho1_area"] is not None else None)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X100 cut-free size")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x100_cutfree", "experiment": "X100",
           "command": "python scripts/x100_analyse.py --write",
           "prereg": "reports/2026-11-02-x100-cutfree-plan.md",
           "definition": "S_cf = sum of v over the 4-connected basin around the uid centroid at its peak, boundary at 0.5 of the local "
                         "maximum; no global threshold",
           "reference_rho1_020": {str(k): v for k, v in REFERENCE.items()},
           "survives": SURVIVES, "definition_bound": DEFINITION_BOUND, "cells": {}}
    for name, (series, flow) in CELLS.items():
        res["cells"][name] = cell_stats(series, flow)
    c = res["cells"]

    control_ok = True
    detail = {}
    for name, flow in (("f030", 0.030), ("f040", 0.040)):
        got = c[name]["rho1_area"]
        lo, hi = CONTROL_BAND[flow]
        ok = got is not None and lo <= got <= hi
        detail[name] = {"rho1_area": got, "band": [lo, hi], "ok": ok}
        control_ok = control_ok and ok
    res["positive_control"] = {"fires": bool(control_ok), "detail": detail}

    void = [k for k, v in c.items() if (v["pairs"] or 0) < MIN_PAIRS or (v["basin_coverage"] or 0) < MIN_COVERAGE
            or v["rho1_S_cf"] is None]
    res["void_cells"] = void

    deltas = {k: v["delta"] for k, v in c.items()}
    if not control_ok:
        verdict = "void: the threshold-based control does not reproduce the committed rho1 — the pairing or the field parsing differs"
    elif void:
        verdict = f"void: underpowered or unreadable cells: {void}"
    elif all(d is not None and abs(d) <= SURVIVES for d in deltas.values()):
        verdict = "heredity survives the change of definition: the cut-free size gives a rho1 within 0.10 of the threshold-based one in both cells"
    elif any(d is not None and abs(d) >= DEFINITION_BOUND for d in deltas.values()):
        verdict = "heredity is definition-bound too: the cut-free size moves rho1 by at least 0.20 in at least one cell"
    else:
        verdict = "mixed"
    res["deltas"] = deltas
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x100] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k}: rho1 area={v['rho1_area']} (ref {v['reference_rho1']}) S_cf={v['rho1_S_cf']} A_cf={v['rho1_A_cf']} "
              f"delta={v['delta']} paired={v['paired_delta']} pairs={v['pairs']} cover={v['basin_coverage']} "
              f"median S_cf={v['median_S_cf']} median area={v['median_area']}")
    print("  control:", res["positive_control"]["fires"], {k: x["ok"] for k, x in detail.items()})
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
