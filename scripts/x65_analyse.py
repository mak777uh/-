"""x65_analyse.py — the grid-120 bracket: does the heterogeneous arm select at 15 cells per period?

Applies the preregistered criterion of `reports/2026-11-01-x65-grid120-bracket-plan.md`:

    homogeneous peak within 14-16 cells (its physical wavelength is 12 units = 15 cells here)
    heterogeneous normalised entropy >= 0.8  => still broadband, transition above 15 cells
    heterogeneous normalised entropy <= 0.7  => already selecting, transition between 12 and 15

Normalised entropy is the comparable quantity across grids, because the maximum depends on how many modes the grid allows
(the lesson of X64, where a raw entropy bar was mis-specified).

Run:
    python scripts/x65_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x65_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x65_bracket.json"

GRID = 120
DOMAIN = 96.0
DX = DOMAIN / GRID           # 0.8
STEPS = (4000, 8000, 12000)
ARMS = ("pattern", "homog")


def spectrum(arm: str, t: int) -> dict | None:
    ps = []
    for seed in range(171, 176):
        f = FIELDS / f"x65_{arm}_s{seed}_t{t}.npy"
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
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, 19) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    q = max(shares, key=shares.get)
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    ent_max = math.log(len(shares))
    return {"arm": arm, "t": t, "n_seeds": len(ps), "q_peak": q,
            "lambda_cells": round(n / q, 2), "lambda_units": round((n / q) * DX, 2),
            "peak_share": round(shares[q], 3),
            "entropy": round(ent, 3), "entropy_max": round(ent_max, 3),
            "entropy_normalised": round(ent / ent_max, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X65 grid-120 bracket")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    spec = [s for s in (spectrum(a, t) for t in STEPS for a in ARMS) if s]
    if not spec:
        print("[x65] no fields yet")
        return 0

    last = max((s for s in spec), key=lambda s: s["t"])
    homog_last = next((s for s in spec if s["arm"] == "homog" and s["t"] == last["t"]), None)
    pat_last = next((s for s in spec if s["arm"] == "pattern" and s["t"] == last["t"]), None)

    homog_ok = bool(homog_last and 14.0 <= homog_last["lambda_cells"] <= 16.0)
    verdict = "unmapped"
    if pat_last:
        e = pat_last["entropy_normalised"]
        if e >= 0.8:
            verdict = "broadband (transition above 15 cells)"
        elif e <= 0.7:
            verdict = "selecting (transition between 12 and 15 cells)"

    out = {
        "kind": "l1_field_x65_bracket",
        "experiment": "X65",
        "command": "python scripts/x65_analyse.py --write",
        "prereg": "reports/2026-11-01-x65-grid120-bracket-plan.md",
        "design": {"grid": GRID, "dx": round(DX, 4), "dt": 0.5, "Du": 0.25, "Dv": 0.125, "steps": 12000,
                   "cells_per_period": 15},
        "spectra": spec,
        "criterion": {"homog_band_cells": [14, 16], "homog_in_band": homog_ok,
                      "heterogeneous_broadband_at": 0.8, "heterogeneous_selecting_at": 0.7},
        "verdict": verdict,
        "not_claimed": [
            "five seeds, seed-averaged spectra, no p-values",
            "one bracket point; the transition is bounded, not located",
            "normalised entropy is comparable across grids, raw entropy is not",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x65] written: {OUT.name}")
    for s in spec:
        print("  t=%5d %-8s q=%2d λ=%5.2f cells = %5.2f units  share=%.3f  H/ln=%5.3f" % (
            s["t"], s["arm"], s["q_peak"], s["lambda_cells"], s["lambda_units"],
            s["peak_share"], s["entropy_normalised"]))
    print("  homog in band:", homog_ok, "| verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
