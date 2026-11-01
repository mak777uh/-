"""x67_analyse.py — the box doubled: which scale does the heterogeneous field peak on?

Preregistered in `reports/2026-11-01-x67-bigger-box-plan.md`. Grid 192 means a domain of 192 units at Δx = 1, so the three
pre-declared outcomes map to modes:

    q = 1  -> 192 units: the organisation follows the box
    q = 2  -> ~96 units: a real 96-unit structure that the old box happened to fit
    q = 16 -> 12 units: the field selects the medium's wavelength after all

The homogeneous arm is the control and must land on q = 16.

Run:
    python scripts/x67_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x67_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x67_box.json"

GRID = 192
DOMAIN = 192.0
STEPS = (2000, 4000, 6000)
EXPECTED_HOMOG_Q = 16


def spectrum(arm: str, t: int) -> dict | None:
    ps = []
    for seed in range(171, 176):
        f = FIELDS / f"x67_{arm}_s{seed}_t{t}.npy"
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
    qmax = min(n // 2, 24)
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, qmax + 1) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    order = sorted(shares, key=shares.get, reverse=True)
    q = order[0]
    second = shares[order[1]] if len(order) > 1 else 0.0
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    ent_max = math.log(len(shares))
    return {"arm": arm, "t": t, "n_seeds": len(ps), "q_peak": q,
            "lambda_units": round(DOMAIN / q, 2), "peak_share": round(shares[q], 3),
            "second_share": round(second, 3),
            "split_peak": bool(shares[q] and second / shares[q] > 0.8),
            "entropy_normalised": round(ent / ent_max, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X67 bigger box")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    spec = [s for s in (spectrum(a, t) for t in STEPS for a in ("homog", "pattern")) if s]
    if not spec:
        print("[x67] no fields yet")
        return 0

    last_h = max((s for s in spec if s["arm"] == "homog"), key=lambda s: s["t"], default=None)
    last_p = max((s for s in spec if s["arm"] == "pattern"), key=lambda s: s["t"], default=None)

    homog_ok = bool(last_h and abs(last_h["q_peak"] - EXPECTED_HOMOG_Q) <= 1)
    verdict = "unmapped"
    if last_p:
        if last_p["q_peak"] == 1:
            verdict = "box: the organisation follows the domain"
        elif abs(last_p["q_peak"] - 2) <= 1:
            verdict = "fixed scale: a real ~96-unit structure"
        elif abs(last_p["q_peak"] - EXPECTED_HOMOG_Q) <= 1:
            verdict = "pattern: the field selects the medium's wavelength"
        elif last_p["split_peak"]:
            verdict = "refused: split peak"

    out = {
        "kind": "l1_field_x67_box",
        "experiment": "X67",
        "command": "python scripts/x67_analyse.py --write",
        "prereg": "reports/2026-11-01-x67-bigger-box-plan.md",
        "design": {"grid": GRID, "domain_units": DOMAIN, "dx": 1.0, "dt": 1.0, "steps": 6000},
        "spectra": spec,
        "homogeneous_control_ok": homog_ok,
        "verdict": verdict,
        "not_claimed": [
            "five seeds, seed-averaged spectra, no p-values",
            "one box size; a third size would be needed to call the box effect a law",
            "the 96-unit reading (q = 2) is within one mode of q = 1, so a peak there is suggestive, not sharp",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x67] written: {OUT.name}")
    for s in spec:
        print("  t=%5d %-8s q=%2d (%6.1f units)  share=%.3f  second=%.3f  H/ln=%.3f" % (
            s["t"], s["arm"], s["q_peak"], s["lambda_units"], s["peak_share"], s["second_share"],
            s["entropy_normalised"]))
    print("  homogeneous control ok:", homog_ok, "| verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
