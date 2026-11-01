"""x74_analyse.py — does the half-life of the size memory depend on the inflow?

Reuses the X73 genealogy machinery (`x73_depth.build`, `ancestors`) on three cells: `F = 0.030` and `0.040` (new, `x74_*`) and
`F = 0.035` (already measured, `x72c_pattern_*`). Per cell: Spearman at lags 1–3, the cross-lineage shuffle null, then the decay
rate `λ` as the geometric mean of `ρ₂/ρ₁` and `ρ₃/ρ₂`, and the half-life `ln 0.5 / ln λ`.

Criteria: `reports/2026-11-02-x74-rate-plan.md`.

Run:
    python scripts/x74_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x74_rate.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
CELLS = {"f030": "x74_f030_pattern_s*.json", "f035": "x72c_pattern_s*.json", "f040": "x74_f040_pattern_s*.json"}


def cell_stats(pattern: str, rng: random.Random) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    for path in sorted(L1.glob(pattern)):
        w = build(path)
        seed = path.stem.split("_s")[-1]
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
    return out


def lam_of(cell: dict) -> tuple[float | None, float | None]:
    r1, r2, r3 = (cell[k]["rho"] for k in LAGS)
    if not r1 or not r2 or not r3 or r1 <= 0:
        return None, None
    ratios = [x / y for x, y in ((r2, r1), (r3, r2)) if y > 0 and x > 0]
    if not ratios:
        return None, None
    lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    half = math.log(0.5) / math.log(lam) if 0 < lam < 1 else None
    return lam, half


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X74 decay rate vs inflow")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(74)

    res = {"kind": "l1_field_x74_rate", "experiment": "X74",
           "command": "python scripts/x74_analyse.py --write",
           "prereg": "reports/2026-11-02-x74-rate-plan.md", "cells": {}}

    for name, pattern in CELLS.items():
        cell = cell_stats(pattern, rng)
        lam, half = lam_of(cell)
        cell["lambda"] = round(lam, 3) if lam else None
        cell["half_life"] = round(half, 2) if half else None
        cell["void"] = (cell[2]["pairs"] < 200 or (cell[1]["rho"] or 0) < 0.30
                        or (cell[1]["shuffle_p95"] or 0) > 0.10)
        res["cells"][name] = cell

    cells = res["cells"]
    void = [k for k, c in cells.items() if c["void"]]
    halves = {k: c["half_life"] for k, c in cells.items() if c["half_life"]}
    lams = {k: c["lambda"] for k, c in cells.items() if c["lambda"]}
    if void or len(halves) < 3:
        verdict = f"void: cells without a usable decay: {void}"
    else:
        spread = max(halves.values()) / min(halves.values())
        lam_spread = max(lams.values()) - min(lams.values())
        if spread >= 1.3:
            verdict = "the rate depends on the inflow (half-lives differ by a factor >= 1.3)"
        elif lam_spread <= 0.10:
            verdict = "the rate is a property of the event (lambda within +/-0.10 across cells)"
        else:
            verdict = "inconclusive"
    res["verdict"] = verdict
    res["half_life_spread"] = round(max(halves.values()) / min(halves.values()), 2) if len(halves) >= 3 else None

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x74] written: {OUT.name}")

    for name, c in cells.items():
        print(f"  {name}: pairs {c[1]['pairs']}/{c[2]['pairs']}/{c[3]['pairs']}  "
              f"rho {c[1]['rho']}/{c[2]['rho']}/{c[3]['rho']}  shuffle {c[1]['shuffle_p95']}  "
              f"lambda={c['lambda']} half={c['half_life']} void={c['void']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
