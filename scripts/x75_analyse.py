"""x75_analyse.py — depth curves at the multistable band edges.

Same machinery as X73/X74 (`x73_depth.build`, `ancestors`), applied to the two new cells `F = 0.033` and `0.037`, and compared
with the X74 curve at `0.030 / 0.035 / 0.040`.

Criteria: `reports/2026-11-02-x75-edges-plan.md`.

Run:
    python scripts/x75_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x75_edges.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
EDGES = {"f033": "x75_f033_pattern_s*.json", "f037": "x75_f037_pattern_s*.json"}
REFERENCE = {"f030": 1.47, "f035": 0.73, "f040": 1.61}


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


def lam_of(cell: dict):
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
    ap = argparse.ArgumentParser(description="X75 band edges")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(75)

    res = {"kind": "l1_field_x75_edges", "experiment": "X75",
           "command": "python scripts/x75_analyse.py --write",
           "prereg": "reports/2026-11-02-x75-edges-plan.md",
           "reference_half_lives": REFERENCE, "cells": {}}

    for name, pattern in EDGES.items():
        cell = cell_stats(pattern, rng)
        lam, half = lam_of(cell)
        cell["lambda"] = round(lam, 3) if lam else None
        cell["half_life"] = round(half, 2) if half else None
        cell["void"] = (cell[2]["pairs"] < 200 or not (0.40 <= (cell[1]["rho"] or 0) <= 0.60)
                        or (cell[1]["shuffle_p95"] or 0) > 0.10)
        res["cells"][name] = cell

    cells = res["cells"]
    void = [k for k, c in cells.items() if c["void"]]
    halves = [c["half_life"] for c in cells.values() if c["half_life"]]
    if void or len(halves) < 2:
        verdict = f"void: cells without a usable depth curve: {void}"
    elif all(h < 1.0 for h in halves):
        verdict = "supports mixedness: both band edges are shallow (half-life below 1.0)"
    elif all(h > 1.3 for h in halves):
        verdict = "refutes mixedness: both edges remember as long as their outer neighbours"
    else:
        verdict = "inconclusive: one edge shallow, one not"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x75] written: {OUT.name}")

    for name, c in cells.items():
        print(f"  {name}: pairs {c[1]['pairs']}/{c[2]['pairs']}/{c[3]['pairs']}  "
              f"rho {c[1]['rho']}/{c[2]['rho']}/{c[3]['rho']}  lambda={c['lambda']} half={c['half_life']} void={c['void']}")
    print("  reference: 0.030 -> 1.47, 0.035 -> 0.73, 0.040 -> 1.61")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
