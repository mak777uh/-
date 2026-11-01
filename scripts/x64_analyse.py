"""x64_analyse.py — did the refinement preserve the physical wavelength?

Applies the preregistered criterion of `reports/2026-11-01-x64-real-refinement-plan.md`. At grid 144 with the physical
domain fixed at 96 units, Δx = 96/144 = 2/3, so a wavelength measured in cells becomes physical units by multiplying by
2/3. The homogeneous arm must land at 12 units, i.e. **18 cells, q = 8**.

    scaling validated  => homogeneous peak at 17-19 cells with entropy < 1.8
    scaling wrong      => peak outside that band (and the number says by how much)

Run:
    python scripts/x64_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x64_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x64_refinement.json"

GRID = 144
DOMAIN = 96.0
DX = DOMAIN / GRID          # 2/3
STEPS = (4000, 8000, 12000)
ARMS = ("pattern", "homog")
BAND_CELLS = (17.0, 19.0)


def spectrum(arm: str, t: int) -> dict | None:
    ps = []
    for seed in range(171, 176):
        f = FIELDS / f"x64_{arm}_s{seed}_t{t}.npy"
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
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, 21) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    q = max(shares, key=shares.get)
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    return {"arm": arm, "t": t, "n_seeds": len(ps), "q_peak": q,
            "lambda_cells": round(n / q, 2), "lambda_units": round((n / q) * DX, 2),
            "peak_share": round(shares[q], 3), "entropy": round(ent, 3),
            "entropy_max": round(math.log(len(shares)), 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X64 refinement analysis")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    spec = [s for s in (spectrum(a, t) for t in STEPS for a in ARMS) if s]
    if not spec:
        print("[x64] no fields yet")
        return 0

    homog = [s for s in spec if s["arm"] == "homog"]
    last_h = max(homog, key=lambda s: s["t"]) if homog else None
    in_band = bool(last_h and BAND_CELLS[0] <= last_h["lambda_cells"] <= BAND_CELLS[1])
    ent_ok = bool(last_h and last_h["entropy"] < 1.8)
    verdict = "validated" if (in_band and ent_ok) else "wrong"

    out = {
        "kind": "l1_field_x64_refinement",
        "experiment": "X64",
        "command": "python scripts/x64_analyse.py --write",
        "prereg": "reports/2026-11-01-x64-real-refinement-plan.md",
        "design": {"grid": GRID, "domain_units": DOMAIN, "dx": round(DX, 4), "dt": 0.5,
                   "Du": 0.36, "Dv": 0.18, "steps": 12000},
        "spectra": spec,
        "criterion": {"band_cells": list(BAND_CELLS), "entropy_below": 1.8,
                      "homog_in_band": in_band, "homog_entropy_ok": ent_ok},
        "verdict": verdict,
        "not_claimed": [
            "five seeds, seed-averaged spectra, no p-values",
            "one refinement factor (1.5x), not a convergence study",
            "grid 192 would need dt <= 0.39 and four times the steps, so it is not attempted here",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x64] written: {OUT.name}")
    for s in spec:
        print("  t=%5d %-8s q=%2d  λ=%5.2f cells = %5.2f units  share=%.3f  H=%.2f/%.2f" % (
            s["t"], s["arm"], s["q_peak"], s["lambda_cells"], s["lambda_units"],
            s["peak_share"], s["entropy"], s["entropy_max"]))
    print("  homog in band:", in_band, "| entropy ok:", ent_ok, "| verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
