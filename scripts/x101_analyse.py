"""x101_analyse.py — basins by steepest ascent: a structure size with no level set at all.

Criteria: `reports/2026-11-02-x101-watershed-plan.md`. Every cell of the field is assigned to the local maximum reached by steepest ascent
(8-neighbourhood, periodic); a structure's size is the area of the basin its centroid drains to. No threshold, no fraction.

Reads X100's twenty runs (a field at every logged step) and compares, on the same ancestor-descendant pairs, the heredity of the
threshold-0.20 area with the heredity of the basin area.

Run:
    python scripts/x101_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x100_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x101_watershed.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402
from field_metrics import cell_files  # noqa: E402

CELLS = {"f030": 0.030, "f040": 0.040}
X100_THRESHOLD_RHO = {0.030: 0.531, 0.040: 0.384}
REPRO_TOL = 0.02
MIN_PAIRS, MIN_COVERAGE = 100, 0.80
EXTENT = 0.10
NEEDS_CUT = 0.20
FLOOR = 0.01   # ниже этого поле считается пустым: у таких клеток нет «водораздела», они не входят в бассейны


def field_for(run_json: Path, step: int) -> Path | None:
    p = FIELDS / f"{run_json.stem}_t{step}.npy"
    return p if p.is_file() else None


def basins(field: np.ndarray) -> tuple[np.ndarray, int]:
    """Идентификатор локального максимума для каждой клетки (подъём по градиенту, 8 соседей, заворот)."""
    g = field.shape[0]
    flat = field.ravel()
    target = -np.ones(g * g, dtype=np.int64)
    shifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for idx in range(g * g):
        y, x = divmod(idx, g)
        best, bestv = idx, flat[idx]
        for dy, dx in shifts:
            ny, nx = (y + dy) % g, (x + dx) % g
            j = ny * g + nx
            if flat[j] > bestv:
                best, bestv = j, flat[j]
        target[idx] = best
    # путь до неподвижной точки с запоминанием
    root = np.arange(g * g, dtype=np.int64)
    for idx in range(g * g):
        cur, path = idx, []
        seen = set()
        while target[cur] != cur and cur not in seen:
            if root[cur] != cur:
                cur = int(root[cur])
                break
            seen.add(cur)
            path.append(cur)
            cur = int(target[cur])
        for p in path:
            root[p] = cur
        root[idx] = cur
    live = flat > FLOOR
    ids, counts = np.unique(root[live], return_counts=True)
    area_of = dict(zip(ids.tolist(), counts.tolist()))
    labels = np.where(live, root, -1)
    return labels.reshape(g, g), len(area_of)


def world_sizes(run_json: Path) -> dict:
    d = json.loads(run_json.read_text(encoding="utf-8"))
    peak_row: dict[int, dict] = {}
    for row in (d.get("series") or []):
        for c in (row.get("components_log") or []):
            uid = int(c["uid"])
            area = float(c.get("area") or 0)
            if uid not in peak_row or area > float(peak_row[uid].get("area") or 0):
                peak_row[uid] = {"area": area, "cx": c.get("cx"), "cy": c.get("cy"), "step": row.get("step")}
    out = {"area": {}, "basin": {}, "partition_ok": True}
    for uid, info in peak_row.items():
        out["area"][uid] = info["area"]
        f = field_for(run_json, int(info["step"]))
        if f is None or info["cx"] is None:
            continue
        field = np.load(f)
        labels, n_basins = basins(field)
        g = field.shape[0]
        yi, xi = int(round(float(info["cy"]))) % g, int(round(float(info["cx"]))) % g
        lab = int(labels[yi, xi])
        if lab < 0:
            continue
        out["basin"][uid] = float((labels == lab).sum())
        if out["partition_ok"]:
            live = field > FLOOR
            out["partition_ok"] = bool(live.sum() == (labels >= 0).sum())
    return out


def cell_stats(flow_tag: str, flow: float) -> dict:
    ax_area, ay_area, ax_basin, ay_basin = [], [], [], []
    pairs, covered, expected, worlds, partitions = 0, 0, 0, 0, 0
    for path in cell_files(("x100",), flow, filename=""):
        sizes = world_sizes(path)
        worlds += 1
        partitions += 1 if sizes["partition_ok"] else 0
        links = json.loads(path.read_text(encoding="utf-8")).get("uid_pairs") or []
        parent = {int(b): int(a) for a, b in links}
        for child, par in parent.items():
            pairs += 1
            expected += 1
            if child in sizes["basin"]:
                covered += 1
            if par in sizes["area"] and child in sizes["area"]:
                ax_area.append(sizes["area"][par])
                ay_area.append(sizes["area"][child])
            if par in sizes["basin"] and child in sizes["basin"]:
                ax_basin.append(sizes["basin"][par])
                ay_basin.append(sizes["basin"][child])
    rho_area = spearman(ax_area, ay_area)
    rho_basin = spearman(ax_basin, ay_basin)
    return {"flow": flow, "worlds": worlds, "pairs": pairs, "partitions_ok": partitions,
            "basin_coverage": round(covered / expected, 3) if expected else None,
            "rho1_area": round(rho_area, 3) if rho_area is not None else None,
            "rho1_basin": round(rho_basin, 3) if rho_basin is not None else None,
            "n_pairs_area": len(ax_area), "n_pairs_basin": len(ax_basin),
            "median_area": round(st.median(ax_area), 1) if ax_area else None,
            "median_basin": round(st.median(ax_basin), 1) if ax_basin else None,
            "delta": (round(rho_basin - rho_area, 3) if rho_basin is not None and rho_area is not None else None),
            "delta_vs_x100": (round(rho_basin - X100_THRESHOLD_RHO[flow], 3) if rho_basin is not None else None)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X101 watershed basins")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x101_watershed", "experiment": "X101",
           "command": "python scripts/x101_analyse.py --write",
           "prereg": "reports/2026-11-02-x101-watershed-plan.md",
           "basin_definition": "each cell assigned to the local maximum reached by steepest ascent (8-neighbourhood, periodic); a "
                               "structure's size is the area of the basin its centroid drains to; no level set, no free parameter",
           "cells": {}}
    for name, flow in CELLS.items():
        res["cells"][name] = cell_stats(name, flow)
    c = res["cells"]

    control_ok = all(
        v["rho1_area"] is not None and abs(v["rho1_area"] - X100_THRESHOLD_RHO[v["flow"]]) <= REPRO_TOL
        and v["partitions_ok"] == v["worlds"] for v in c.values())
    res["positive_control"] = {"fires": bool(control_ok),
                               "threshold_vs_x100": {k: [v["rho1_area"], X100_THRESHOLD_RHO[v["flow"]]] for k, v in c.items()},
                               "partitions": {k: [v["partitions_ok"], v["worlds"]] for k, v in c.items()}}

    void = [k for k, v in c.items()
            if (v["pairs"] or 0) < MIN_PAIRS or (v["basin_coverage"] or 0) < MIN_COVERAGE or v["rho1_basin"] is None]
    deltas = {k: v["delta"] for k, v in c.items()}

    if not control_ok:
        verdict = "void: the threshold-based reproduction or the basin partition check failed"
    elif void:
        verdict = f"void: underpowered or unreadable cells: {void}"
    elif all(d is not None and abs(d) <= EXTENT for d in deltas.values()):
        verdict = "heredity is carried by extent: the basin area gives a rho1 within 0.10 of the threshold area in both cells"
    elif any(d is not None and abs(d) >= NEEDS_CUT for d in deltas.values()):
        verdict = "heredity needs the cut: the basin area moves rho1 by at least 0.20 in at least one cell"
    else:
        verdict = "mixed"
    res["deltas"] = deltas
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x101] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k}: rho1 area={v['rho1_area']} basin={v['rho1_basin']} delta={v['delta']} "
              f"pairs={v['pairs']} cover={v['basin_coverage']} med area={v['median_area']} med basin={v['median_basin']} "
              f"partitions={v['partitions_ok']}/{v['worlds']}")
    print("  control:", res["positive_control"]["fires"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
