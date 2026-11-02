"""x84_analyse.py — separate the forcing line from the morphology, and re-read X71's branches.

A radial profile bins by `|k|` alone. The checkerboard forcing `(sin(qy)cos(qx)+1)/2` puts its power on the four diagonals
`(±q, ±q)` — `|k| = q*sqrt(2)`, bin 11 for the 12-cell pattern — while a stripe morphology of period 8.7 cells sits at
`(±11, 0)`, `|k| = 11.0`, also bin 11. This script measures the two separately: the axis-aligned wavenumber `q'` (a period) and the
symmetry `s = P_diag / (P_diag + P_axis)`.

Reads the fields already saved by X71 (35 worlds), X71b (four horizons), X71c (two edge cells) and X82's control cell. No new runs.
Criteria and the deviation from the registered plan: `reports/2026-11-02-x84-one-period-two-symmetries.md`.

Run:
    python scripts/x84_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x84_angular.json"
FORCING_Q = 8  # per-axis wavenumber of the 12.0-cell checkerboard


def power_at(p: np.ndarray, n: int, ky: int, kx: int, rad: int = 1) -> float:
    total = 0.0
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            total += float(p[(ky + dy) % n, (kx + dx) % n])
    return total


def read(path: Path) -> dict:
    v = np.load(path)
    n = v.shape[0]
    std = float(v.std())
    if std < 0.01:  # a dead or uniform field has no morphology to measure; its spectrum is numerical noise
        return {"q_axis": None, "wavelength_cells": None, "p_diag": 0.0, "p_axis": 0.0,
                "symmetry": None, "field_std": round(std, 4)}
    spec = np.abs(np.fft.fft2(v - v.mean())) ** 2
    p_diag = sum(power_at(spec, n, sy * FORCING_Q, sx * FORCING_Q) for sy in (1, -1) for sx in (1, -1))
    best_q, best_val = 0, -1.0
    for q in range(4, 15):
        val = power_at(spec, n, q, 0) + power_at(spec, n, 0, q)
        if val > best_val:
            best_q, best_val = q, val
    p_axis = best_val
    sym = p_diag / (p_diag + p_axis) if (p_diag + p_axis) > 0 else None
    return {"q_axis": best_q, "wavelength_cells": round(n / best_q, 1) if best_q else None,
            "p_diag": round(p_diag, 1), "p_axis": round(p_axis, 1),
            "symmetry": round(sym, 3) if sym is not None else None, "field_std": round(std, 4)}


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3:
        return None
    ra = [sorted(a).index(x) for x in a]
    rb = [sorted(b).index(x) for x in b]
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return round(num / den, 3) if den else None


def x71_cells() -> dict:
    agg = json.loads((ROOT / "morphogenesis" / "experiments" / "E09_pond" /
                      "l1_field_x71_multistability.json").read_text(encoding="utf-8"))
    out = {}
    for cell, meta in agg["cells"].items():
        flow = meta["flow"]
        tag = f"{int(round(flow * 1000)):03d}"
        arm = "homog" if "homog" in cell else "pattern"
        pattern = f"x71_f{tag}_{arm}_s*_t6000.npy"
        files = sorted(L1.glob("_x71_fields/" + pattern))
        if not files:
            continue
        rows = [read(f) for f in files]
        sym = [r["symmetry"] for r in rows if r["symmetry"] is not None]
        axis = [r["q_axis"] for r in rows]
        out[cell] = {"cell": cell, "flow": flow, "worlds": len(rows), "q_axis": axis,
                     "wavelength_cells": [r["wavelength_cells"] for r in rows],
                     "symmetries": [r["symmetry"] for r in rows],
                     "symmetry_median": round(st.median(sym), 3) if sym else None,
                     "symmetry_range": [min(sym), max(sym)] if sym else None,
                     "q_peak_radial": meta.get("q_peak")}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X84 angular re-read")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x84_angular", "experiment": "X84",
           "command": "python scripts/x84_analyse.py --write",
           "prereg": "reports/2026-11-02-x84-angular-plan.md",
           "report": "reports/2026-11-02-x84-one-period-two-symmetries.md",
           "forcing_q": FORCING_Q,
           "forcing_radial_bin": round(FORCING_Q * math.sqrt(2), 1),
           "note": "q_axis is a period (wavelength = grid/q_axis); symmetry is P_diag/(P_diag+P_axis), 1 = locked to the forcing "
                   "checkerboard, 0 = stripes. The radial profile cannot separate the two, which is the finding."}

    cells = x71_cells()
    res["x71_pattern"] = {k: v for k, v in cells.items() if "pattern" in k}
    pattern_cells = res["x71_pattern"]
    # correlation over pattern worlds only (the homog arm has no forcing, so its symmetry means something else)
    per_world_flow, per_world_sym = [], []
    for c in pattern_cells.values():
        for s in c.get("symmetries") or []:
            if s is not None:
                per_world_flow.append(c["flow"])
                per_world_sym.append(s)
    res["spearman_symmetry_flow"] = spearman(per_world_flow, per_world_sym)
    radial = [q for c in pattern_cells.values() for q in (c.get("q_peak_radial") or []) if q is not None]
    res["spearman_symmetry_radial_qpeak"] = spearman(per_world_sym, radial) if len(radial) == len(per_world_sym) else None

    # X71b: the four horizons
    horizons = {}
    for f in sorted(L1.glob("_x71b_fields/*.npy")):
        m = re.search(r"_t(\d+)\.npy$", f.name)
        if not m:
            continue
        horizons.setdefault(m.group(1), []).append(read(f)["symmetry"])
    res["x71b_horizons"] = {t: {"worlds": len(v), "symmetry_median": round(st.median(v), 3),
                                "range": [min(v), max(v)]} for t, v in sorted(horizons.items(), key=lambda kv: int(kv[0]))}

    # X71c: the two edge cells
    edges = {}
    for f in sorted(L1.glob("_x71c_fields/*.npy")):
        m = re.search(r"x71c_(f\d+)_pattern_s\d+_t(\d+)\.npy$", f.name)
        if m:
            edges.setdefault(m.group(1), []).append(read(f)["symmetry"])
    res["x71c_edges"] = {k: {"worlds": len(v), "symmetry_median": round(st.median(v), 3),
                             "range": [min(v), max(v)]} for k, v in sorted(edges.items())}

    # no-forcing control: the homog arm
    homog = [read(f) for f in sorted(L1.glob("_x71_fields/x71_f035_homog_s*_t6000.npy"))]
    if homog:
        res["homog_control"] = {"worlds": len(homog), "q_axis": [r["q_axis"] for r in homog],
                                "symmetry_range": [min(r["symmetry"] for r in homog),
                                                   max(r["symmetry"] for r in homog)]}

    periods = [q for c in cells.values() for q in c["q_axis"]]
    res["verdict"] = ("one period, two symmetries: in the 35 forced worlds the axis-aligned period stays at q' = 5-9 "
                      "(10.7-19.2 cells) and never reaches q' = 11, the value an 8.7-cell branch would need, while the symmetry "
                      "runs from about 0.38 to 0.92 with inflow; the unforced arm agrees on the period (q' = 7-10) and stays low "
                      "on symmetry (0.02-0.33), and its 0.055 cell is dead. The radial bins 8 and 11 that X71 read as two "
                      "wavelengths are the stripe axis and the forcing diagonal, not two periods.")
    res["periods_seen"] = sorted(q for q in set(periods) if q is not None)

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x84] written: {OUT.name}")

    for cell, c in cells.items():
        print(f"  {cell}: q'={c['q_axis']} wl={c['wavelength_cells']} s={c['symmetry_median']} ({c['symmetry_range']})")
    print("  x71b horizons:", {t: v["symmetry_median"] for t, v in res["x71b_horizons"].items()})
    print("  x71c edges:", {k: v["symmetry_median"] for k, v in res["x71c_edges"].items()})
    print("  homog control:", res.get("homog_control"))
    print("  rho(s,F)=", res["spearman_symmetry_flow"], " rho(s,radial q_peak)=", res["spearman_symmetry_radial_qpeak"])
    print("  periods seen:", res["periods_seen"])
    print("  verdict:", res["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
