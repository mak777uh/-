"""x96d_analyse.py — X96d: does the second species move the orientation, and does it replicate?

Per cell (seed x inflow): q' and s at Dw = 0.08, 0.16, 0.32, 0.64, the w-off control for that cell, and two Spearman coefficients —
rho(Dw, s) and rho(Dw, q'). Registered criteria (reports/2026-11-02-x96d-orientation-plan.md):
  * orientation replicates if at least 4 of 6 cells give rho(Dw, s) with one sign at |rho| >= 0.8;
  * the scale channel opens if q' leaves [3, 11] at Dw = 0.64 in at least 3 cells;
  * a collapsed corner (fewer than 10 components) is a regime boundary for that cell and is excluded from its coefficients.

    python scripts/x96d_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import angular  # noqa: E402


def ranks_of(vals: list[float]) -> list[float]:
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman_small(x: list[float], y: list[float]) -> float | None:
    """Spearman for small n (the shared helper in x72c_analyse needs five points; a Dw sweep has four)."""
    if len(x) < 3 or len(x) != len(y):
        return None
    rx, ry = ranks_of(x), ranks_of(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if not sxx or not syy:
        return None
    return sxy / (sxx * syy) ** 0.5

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x96d_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x96d_orientation.json"

CELLS = {"f030": 0.030, "f040": 0.040}
SEEDS = (411, 412, 413)
DWS = (0.08, 0.16, 0.32, 0.64)
BAND = (5, 9)
SCALE_LO, SCALE_HI = 3, 11     # two units outside the band
MIN_ALIVE = 10
MIN_RHO = 0.8
REPLICATE_CELLS = 4            # of six


def read_pair(tag: str) -> dict | None:
    run = L1 / f"{tag}.json"
    if not run.is_file():
        return None
    d = json.loads(run.read_text(encoding="utf-8"))
    last = (d.get("series") or [{}])[-1]
    out = {"components_end": last.get("components"), "v_max_end": last.get("v_max")}
    field = FIELDS / f"{tag}_t6000.npy"
    if field.is_file():
        a = angular(np.load(field), forcing_q=8, q_max=14)
        out["q"] = a.get("q_axis")
        out["symmetry"] = round(float(a["symmetry"]), 3) if a.get("symmetry") is not None else None
        out["field_std"] = round(float(a.get("field_std") or 0.0), 5)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X96d orientation analysis")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells: dict[str, dict] = {}
    for cell in CELLS:
        for seed in SEEDS:
            key = f"{cell}_s{seed}"
            ctrl = read_pair(f"x96d_{cell}_s{seed}")
            row = {"control": ctrl, "settings": {}}
            dws, s_vals, q_vals = [], [], []
            for dw in DWS:
                tag = f"x96d_{cell}_dw{str(dw).replace('.', '')}_s{seed}"
                r = read_pair(tag)
                row["settings"][str(dw)] = r
                if r and (r.get("components_end") or 0) >= MIN_ALIVE and r.get("symmetry") is not None:
                    dws.append(dw)
                    s_vals.append(r["symmetry"])
                    q_vals.append(r.get("q"))
            row["live_dws"] = [str(d) for d in dws]
            rs = spearman_small(dws, s_vals) if len(dws) >= 3 else None
            rq = spearman_small(dws, q_vals) if len(dws) >= 3 else None
            row["rho_dw_s"] = round(rs, 3) if rs is not None else None
            row["rho_dw_q"] = round(rq, 3) if rq is not None else None
            row["q_at_max"] = q_vals[-1] if q_vals else None
            row["scale_opens"] = bool(row["q_at_max"] is not None
                                      and (row["q_at_max"] <= SCALE_LO or row["q_at_max"] >= SCALE_HI))
            cells[key] = row

    control_q = [c["control"].get("q") for c in cells.values() if c.get("control")]
    control_ok = len(control_q) == 6 and all(q is not None and BAND[0] <= q <= BAND[1] for q in control_q)
    usable = [c for c in cells.values() if c.get("rho_dw_s") is not None]

    neg = [k for k, c in cells.items() if (c.get("rho_dw_s") or 0) <= -MIN_RHO]
    pos = [k for k, c in cells.items() if (c.get("rho_dw_s") or 0) >= MIN_RHO]
    scale_cells = [k for k, c in cells.items() if c.get("scale_opens")]

    if len(usable) < 4:
        verdict = f"void: only {len(usable)} cells yielded a coefficient"
    elif not control_ok:
        verdict = f"void: a control's q' left the 5-9 band ({control_q})"
    elif len(neg) >= REPLICATE_CELLS:
        verdict = (f"the orientation effect replicates: rho(Dw, s) is <= -0.8 in {len(neg)} of 6 cells "
                   f"({sorted(neg)}) — a second diffusion length makes the pattern less diagonal as it grows")
    elif len(pos) >= REPLICATE_CELLS:
        verdict = (f"the orientation effect replicates, with the opposite sign: rho(Dw, s) >= 0.8 in {len(pos)} of 6 cells "
                   f"({sorted(pos)})")
    elif len(neg) + len(pos) <= 2:
        verdict = (f"the orientation effect does not replicate: only {len(neg) + len(pos)} of 6 cells reach |rho| >= 0.8 "
                   f"(coefficients {[c.get('rho_dw_s') for c in cells.values()]})")
    else:
        verdict = (f"mixed: {len(neg)} cells negative and {len(pos)} positive at |rho| >= 0.8 — the sign is not one number")

    if scale_cells:
        verdict += f"; the scale channel opens in {sorted(scale_cells)}"

    res = {
        "kind": "l1_field_x96d_orientation",
        "experiment": "X96d",
        "command": "python scripts/x96d_analyse.py --write",
        "prereg": "reports/2026-11-02-x96d-orientation-plan.md",
        "rule": "uvv = u*v*v/(1+gamma*w); dw/dt = Dw*lap(w) + 0.05*(v - w); gamma = 0.05",
        "readout": "q' and s from field_metrics.angular at Dw = 0.08..0.64, with rho(Dw, s) and rho(Dw, q') per cell",
        "criteria": {"orientation": f"|rho(Dw, s)| >= {MIN_RHO} in >= {REPLICATE_CELLS} of 6 cells, one sign",
                     "scale": f"q' outside [{SCALE_LO}, {SCALE_HI}] at Dw = 0.64 in >= 3 cells",
                     "liveness": f">= {MIN_ALIVE} components at step 6000"},
        "cells": cells,
        "positive_control": {"fires": bool(control_ok), "control_q": control_q,
                             "note": "all six w-off controls must sit inside the 5-9 band"},
        "counts": {"negative": neg, "positive": pos, "scale": scale_cells, "usable": len(usable)},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x96d] written: {OUT.name}")
    for k, c in cells.items():
        print(f"  {k}: control q'={c['control'].get('q') if c.get('control') else None} "
              f"rho_dw_s={c['rho_dw_s']} rho_dw_q={c['rho_dw_q']} live={c['live_dws']} q@max={c['q_at_max']}")
    print("  control:", control_ok, "| negative:", sorted(neg), "| positive:", sorted(pos))
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
