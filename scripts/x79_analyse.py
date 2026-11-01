"""x79_analyse.py — does memory shorten gradually with the weight of an imposed second scale?

Two cells at `F = 0.030` with a composite pattern (12.0 + 8.7 cells): mix weight 0.25 and 0.75, against the reference points 0
(single scale, half-life 1.47) and 0.5 (X78b, 1.03).

Criteria: `reports/2026-11-02-x79-mix-plan.md`.

Run:
    python scripts/x79_analyse.py --write
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
FIELDS = L1 / "_x79_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x79_mix.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x60_analyse import radial_profile  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
CELLS = {"mix025": "x79_mix025_s*.json", "mix075": "x79_mix075_s*.json"}
REFERENCE = {"mix000": 1.47, "mix050": 1.03}


def cell_stats(pattern: str, rng: random.Random) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, peaks_per_world = [], {}
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
                peaks_per_world[seed] = peaks
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
    out["lambda"] = round(lam, 3) if lam else None
    out["half_life"] = round(half, 2) if half else None
    out["two_peak_worlds"] = sum(1 for pk in peaks_per_world.values()
                                 if any(6 <= q <= 9 for q in pk) and any(10 <= q <= 13 for q in pk))
    out["worlds"] = len(comps)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X79 mix sweep")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(79)

    res = {"kind": "l1_field_x79_mix", "experiment": "X79",
           "command": "python scripts/x79_analyse.py --write",
           "prereg": "reports/2026-11-02-x79-mix-plan.md",
           "reference": REFERENCE, "cells": {}}
    for name, pattern in CELLS.items():
        res["cells"][name] = cell_stats(pattern, rng)

    a, b = res["cells"]["mix025"], res["cells"]["mix075"]
    void = [k for k, c in res["cells"].items()
            if (c["components_mean"] or 0) < 10 or (c[1]["pairs"] or 0) < 400]
    if void:
        verdict = f"void: collapsed or underpowered cells: {void}"
    else:
        h25, h75 = a["half_life"], b["half_life"]
        if not h25 or not h75:
            verdict = "inconclusive: a half-life could not be fitted"
        elif h25 > 1.03 > h75 and (h25 - h75) >= 0.2:
            verdict = "graded: memory shortens monotonically with the weight of the imposed second scale"
        elif abs(h25 - 1.03) < 0.15 and abs(h75 - 1.03) < 0.15 and abs(h25 - h75) < 0.1:
            verdict = "saturating: a quarter weight already gives the full effect"
        else:
            verdict = "inconclusive: the three points are not monotone or the spread is inside the noise"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x79] written: {OUT.name}")

    for name, c in res["cells"].items():
        print(f"  {name}: components={c['components_mean']} worlds={c['worlds']} two-peak={c['two_peak_worlds']} "
              f"pairs={c[1]['pairs']}/{c[2]['pairs']}/{c[3]['pairs']} "
              f"rho={c[1]['rho']}/{c[2]['rho']}/{c[3]['rho']} lambda={c['lambda']} half={c['half_life']}")
    print("  reference: mix 0 -> 1.47, mix 0.5 -> 1.03")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
