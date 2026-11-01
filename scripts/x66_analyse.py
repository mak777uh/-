"""x66_analyse.py — the four-point grid map, all at dt = 0.5.

Combines the new points (96 and 108, from X66) with the existing ones (120 from X65, 144 from X64) and reports, per grid and
arm: peak position in cells and in physical units, peak share, and normalised entropy. The primary readout is the **peak
position relative to the medium's 12 units** — the lesson X65 paid for.

Criterion, per the preregistration (`reports/2026-11-01-x66-grid-map-plan.md`):

    homogeneous peak within +-1 cell of the expected position on each grid
        (96 -> 12, 108 -> 13.5, 120 -> 15, 144 -> 18)
    heterogeneous arm read on the same axis: does its peak sit at the medium's wavelength or elsewhere?

Run:
    python scripts/x66_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x66_map.json"

# grid -> (field prefix, expected peak in cells, domain units)
POINTS = {
    96: ("x66_fields/x66_g096", 12.0),
    108: ("x66_fields/x66_g108", 13.5),
    120: ("x65_fields/x65", 15.0),
    144: ("x64_fields/x64", 18.0),
}
STEPS = (4000, 8000, 12000)
DOMAIN = 96.0


def spectrum(grid: int, arm: str, t: int) -> dict | None:
    prefix, expected = POINTS[grid]
    ps = []
    for seed in range(171, 176):
        f = L1 / f"{prefix}_{arm}_s{seed}_t{t}.npy"
        if not f.exists():
            continue
        v = np.load(f).astype(np.float64)
        ps.append(np.abs(np.fft.fft2(v - v.mean())) ** 2)
    if not ps:
        return None
    p = np.mean(ps, axis=0)
    n = p.shape[0]
    k = np.fft.fftfreq(n) * n
    ky, kx = np.meshgrid(k, k, indexing="ij")
    r = np.round(np.sqrt(ky ** 2 + kx ** 2)).astype(int)
    qmax = min(n // 2, 20)
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, qmax + 1) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    q = max(shares, key=shares.get)
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    ent_max = math.log(len(shares))
    dx = DOMAIN / grid
    return {"grid": grid, "arm": arm, "t": t, "n_seeds": len(ps), "q_peak": q,
            "lambda_cells": round(n / q, 2), "lambda_units": round((n / q) * dx, 2),
            "expected_cells": expected, "in_band": abs((n / q) - expected) <= 1.0,
            "peak_share": round(shares[q], 3),
            "entropy_normalised": round(ent / ent_max, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X66 grid map")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    spec = [s for s in (spectrum(g, a, t) for g in POINTS for t in STEPS for a in ("homog", "pattern")) if s]
    if not spec:
        print("[x66] no fields yet")
        return 0

    last = {}
    for g in POINTS:
        for a in ("homog", "pattern"):
            rows = [s for s in spec if s["grid"] == g and s["arm"] == a]
            if rows:
                last[(g, a)] = max(rows, key=lambda s: s["t"])

    homog_ok = all(v["in_band"] for (g, a), v in last.items() if a == "homog")
    map_rows = []
    for g in sorted(POINTS):
        h = last.get((g, "homog"))
        p = last.get((g, "pattern"))
        map_rows.append({
            "grid": g,
            "cells_per_period_expected": POINTS[g][1],
            "homog_lambda_units": h["lambda_units"] if h else None,
            "homog_in_band": h["in_band"] if h else None,
            "homog_entropy": h["entropy_normalised"] if h else None,
            "pattern_lambda_units": p["lambda_units"] if p else None,
            "pattern_at_medium_wavelength": (abs((p["lambda_units"] or 0) - 12.0) <= 1.0) if p else None,
            "pattern_entropy": p["entropy_normalised"] if p else None,
            "pattern_share": p["peak_share"] if p else None,
        })

    out = {
        "kind": "l1_field_x66_map",
        "experiment": "X66",
        "command": "python scripts/x66_analyse.py --write",
        "prereg": "reports/2026-11-01-x66-grid-map-plan.md",
        "design": {"dt": 0.5, "steps": 12000, "domain_units": 96.0, "grids": sorted(POINTS)},
        "spectra": spec,
        "map": map_rows,
        "homogeneous_scaling_ok": homog_ok,
        "not_claimed": [
            "five seeds, seed-averaged spectra, no p-values",
            "peak position is quantised by mode number, so one cell of tolerance is about one mode",
            "120 and 144 come from earlier series; only the time step is now matched",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x66] written: {OUT.name}")
    for r in map_rows:
        print("  grid %3d  homog %5s units (in band: %s)  pattern %5s units (at 12: %s)  H_p=%s share=%s" % (
            r["grid"], r["homog_lambda_units"], r["homog_in_band"], r["pattern_lambda_units"],
            r["pattern_at_medium_wavelength"], r["pattern_entropy"], r["pattern_share"]))
    print("  homogeneous scaling ok on every grid:", homog_ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
