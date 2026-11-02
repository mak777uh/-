"""x80_analyse.py — with amplitude fixed, does memory dip where the mixture is richest?

Three cells at `F = 0.030` with the amplitude-normalised composite pattern (12.0 + 8.7 cells): `w = 0.25`, `0.50`, `0.75`. With the
amplitude held fixed the cells differ only in spectral content, so a **dip** at `w = 0.5` means mixedness is the cause, and a
**slope** means the dominant scale is.

Criteria: `reports/2026-11-02-x80-dip-plan.md`.

Run:
    python scripts/x80_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x80_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x80_dip.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x60_analyse import radial_profile  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
CELLS = {"w025": ("0.25", "x80_w025_s*.json"), "w050": ("0.50", "x80_w05_s*.json"),
         "w075": ("0.75", "x80_w075_s*.json")}
SINGLE_SCALE = 1.47


def cell_stats(pattern: str, rng: random.Random) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, two_peak = [], 0
    for path in sorted(L1.glob(pattern)):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        f = FIELDS / f"{path.stem}_t6000.npy"
        if f.is_file():
            prof = radial_profile(np.load(f))
            if prof:
                keys = sorted(prof)
                peaks = [q for i, q in enumerate(keys)
                         if 1 < i < len(keys) - 1 and prof[keys[i]] > prof[keys[i - 1]] and prof[keys[i]] >= prof[keys[i + 1]]]
                if any(6 <= q <= 9 for q in peaks) and any(10 <= q <= 13 for q in peaks):
                    two_peak += 1
        for k in LAGS:
            pairs = []
            for uid in w["peaks"]:
                anc = ancestors(uid, w["parent"], k)
                if anc is None or anc not in w["peaks"]:
                    continue
                pairs.append((w["peaks"][anc], w["peaks"][uid]))
            per_lag[k]["pairs"].extend(pairs)
            r = spearman([a for a, _ in pairs], [b for _, b in pairs])
            per_lag[k]["worlds"][seed] = {"pairs": len(pairs), "rho": round(r, 3) if r is not None else None}

    out = {}
    for k in LAGS:
        pairs = per_lag[k]["pairs"]
        rho = spearman([a for a, _ in pairs], [b for _, b in pairs])
        draws = []
        if pairs:
            anc = [a for a, _ in pairs]
            desc = [b for _, b in pairs]
            for _ in range(SHUFFLE):
                sh = anc[:]
                rng.shuffle(sh)
                v = spearman(sh, desc)
                if v is not None:
                    draws.append(v)
        draws.sort()
        out[k] = {"pairs": len(pairs), "rho": round(rho, 3) if rho is not None else None,
                  "shuffle_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
                  "worlds": per_lag[k]["worlds"]}
    r1, r2, r3 = (out[k]["rho"] for k in LAGS)
    lam = half = None
    if r1 and r2 and r3 and r1 > 0:
        ratios = [x / y for x, y in ((r2, r1), (r3, r2)) if x > 0 and y > 0]
        if ratios:
            lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
            half = math.log(0.5) / math.log(lam) if 0 < lam < 1 else None
    out["components_mean"] = round(st.mean(comps), 1) if comps else None
    out["two_peak_worlds"] = two_peak
    out["worlds"] = len(comps)
    out["lambda"] = round(lam, 3) if lam else None
    out["half_life"] = round(half, 2) if half else None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X80 dip test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(80)

    res = {"kind": "l1_field_x80_dip", "experiment": "X80",
           "command": "python scripts/x80_analyse.py --write",
           "prereg": "reports/2026-11-02-x80-dip-plan.md",
           "single_scale_030": SINGLE_SCALE, "cells": {}}
    for key, (w, pattern) in CELLS.items():
        cell = cell_stats(pattern, rng)
        cell["weight"] = float(w)
        res["cells"][key] = cell

    a, b, c = res["cells"]["w025"], res["cells"]["w050"], res["cells"]["w075"]
    void = [k for k, x in res["cells"].items()
            if (x["components_mean"] or 0) < 10 or (x[1]["pairs"] or 0) < 400]
    most_two_peak = max((x["two_peak_worlds"] for x in (a, b, c)))
    middle_most = b["two_peak_worlds"] == most_two_peak and most_two_peak > 0
    h25, h50, h75 = a["half_life"], b["half_life"], c["half_life"]
    if void:
        verdict = f"void: collapsed or underpowered cells: {void}"
    elif not middle_most:
        verdict = ("void: the middle cell is not the most two-peaked, so the amplitude fix did not isolate spectral content "
                   f"(two-peak worlds: {a['two_peak_worlds']}/{b['two_peak_worlds']}/{c['two_peak_worlds']})")
    elif not (h25 and h50 and h75):
        verdict = "inconclusive: a half-life could not be fitted"
    elif h50 < min(h25, h75) - 0.15:
        verdict = "dip: memory is shortest where the mixture is richest, so mixedness is the cause"
    elif (h25 > h50 > h75) or (h25 < h50 < h75):
        verdict = "slope: memory follows the dominant scale monotonically"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x80] written: {OUT.name}")

    for key, x in res["cells"].items():
        print(f"  {key} (w={x['weight']}): components={x['components_mean']} two-peak={x['two_peak_worlds']}/{x['worlds']} "
              f"pairs={x[1]['pairs']} rho={x[1]['rho']}/{x[2]['rho']}/{x[3]['rho']} half={x['half_life']}")
    print("  single-scale 0.030 reference: 1.47")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
