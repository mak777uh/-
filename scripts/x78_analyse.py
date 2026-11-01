"""x78_analyse.py — causal test: does memory depth follow the number of preferred scales, or the inflow?

Two cells at the same inflow `F = 0.040`: the prescribed hetero wavelength **matches** the medium's own (8.7 cells) or
**mismatches** it (12.0 cells), imposing a second scale at an inflow where the field itself is single-valued. Same machinery as
X73–X76 for the depth curve, plus the manipulation check: the two arms must differ in the field's spatial spectrum.

Criteria: `reports/2026-11-02-x78-causal-plan.md`.

Run:
    python scripts/x78_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x78_causal.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
ARMS = {"match": "x78_match_s*.json", "mismatch": "x78_mismatch_s*.json"}
BENCHMARK_040 = 1.61


def cell_stats(pattern: str, rng: random.Random) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    spectra = []
    for path in sorted(L1.glob(pattern)):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        comps = [s.get("components") or 0 for s in (json.loads(path.read_text(encoding="utf-8")).get("series") or [])]
        spectra.append((seed, round(st.mean(comps), 1) if comps else None))
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
    out["components_per_world"] = spectra
    return out


def lam_of(cell: dict):
    r1, r2, r3 = (cell[k]["rho"] for k in LAGS)
    if not r1 or not r2 or not r3 or r1 <= 0:
        return None, None
    ratios = [x / y for x, y in ((r2, r1), (r3, r2)) if x > 0 and y > 0]
    if not ratios:
        return None, None
    lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    return lam, (math.log(0.5) / math.log(lam) if 0 < lam < 1 else None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X78 causal test of the two-scale reading")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(78)

    res = {"kind": "l1_field_x78_causal", "experiment": "X78",
           "command": "python scripts/x78_analyse.py --write",
           "prereg": "reports/2026-11-02-x78-causal-plan.md",
           "benchmark_0_040": BENCHMARK_040, "cells": {}}
    for name, pattern in ARMS.items():
        cell = cell_stats(pattern, rng)
        lam, half = lam_of(cell)
        cell["lambda"] = round(lam, 3) if lam else None
        cell["half_life"] = round(half, 2) if half else None
        res["cells"][name] = cell

    m, x = res["cells"]["match"], res["cells"]["mismatch"]
    comps_m = [c for _, c in (m["components_per_world"] or []) if c is not None]
    comps_x = [c for _, c in (x["components_per_world"] or []) if c is not None]
    res["manipulation_visible"] = bool(comps_m and comps_x and abs(st.mean(comps_m) - st.mean(comps_x)) > 0.5)

    lag1_ok = 0.40 <= (m[1]["rho"] or 0) <= 0.60
    half_m, half_x = m["half_life"], x["half_life"]
    if not res["manipulation_visible"] and not lag1_ok:
        verdict = "void: the manipulation did not reach the world, or the matched cell left its band"
    elif half_m and half_x:
        ratio = half_m / half_x if half_x else None
        if half_x < 1.0 and ratio and ratio >= 1.3:
            verdict = "supports the causal reading: imposing the second scale shortens memory by >= 1.3x"
        elif ratio and ratio < 1.2:
            verdict = "refutes it: changing the prescribed scale did not move memory"
        else:
            verdict = "inconclusive"
    else:
        verdict = "inconclusive: a half-life could not be fitted"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x78] written: {OUT.name}")

    for name, c in res["cells"].items():
        print(f"  {name}: pairs {c[1]['pairs']}/{c[2]['pairs']}/{c[3]['pairs']}  "
              f"rho {c[1]['rho']}/{c[2]['rho']}/{c[3]['rho']}  lambda={c['lambda']} half={c['half_life']}")
    print(f"  components: match {st.mean(comps_m) if comps_m else None:.1f} vs mismatch "
          f"{st.mean(comps_x) if comps_x else None:.1f}; manipulation visible: {res['manipulation_visible']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
