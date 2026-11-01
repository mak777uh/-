"""x78b_analyse.py — does an imposed second scale shorten memory at a long-memory inflow?

Composite pattern (0.5·G(12.0) + 0.5·G(8.7)) at `F = 0.030`, where the single-scale cell remembers for 1.47 divisions. Checks, in
order: does the world stay patterned, does the spectrum carry **two peaks**, and only then what the depth curve says.

Criteria: `reports/2026-11-02-x78b-two-scale-plan.md`.

Run:
    python scripts/x78b_analyse.py --write
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
FIELDS = L1 / "_x78b_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x78b_causal.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x60_analyse import radial_profile  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
SINGLE_SCALE_030 = 1.47
PATTERN = "x78b_two_scale_s*.json"
MIN_COMPONENTS = 10
MIN_PAIRS = 600


def two_peaks(path: Path) -> dict:
    f = FIELDS / f"{path.stem}_t6000.npy"
    if not f.is_file():
        return {"field": False}
    prof = radial_profile(np.load(f))
    if not prof:
        return {"field": True, "peaks": []}
    keys = sorted(prof)
    vals = [prof[k] for k in keys]
    peaks = [q for i, q in enumerate(keys)
             if 1 < i < len(vals) - 1 and vals[i] > vals[i - 1] and vals[i] >= vals[i + 1] and q >= 3]
    return {"field": True, "peaks": peaks, "top": sorted(keys, key=lambda k: prof[k], reverse=True)[:4]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X78b two-scale causal test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(78)

    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, spectra = [], {}
    for path in sorted(L1.glob(PATTERN)):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        spectra[seed] = two_peaks(path)
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

    # two-peak check: at least two worlds with maxima near q=8 and q=11 (>=2 bins apart)
    two_peak_worlds = 0
    for seed, s in spectra.items():
        pk = s.get("peaks") or []
        wide = [q for q in pk if 6 <= q <= 9]
        narrow = [q for q in pk if 10 <= q <= 13]
        if wide and narrow:
            two_peak_worlds += 1

    res = {"kind": "l1_field_x78b_causal", "experiment": "X78b",
           "command": "python scripts/x78b_analyse.py --write",
           "prereg": "reports/2026-11-02-x78b-two-scale-plan.md",
           "single_scale_030": SINGLE_SCALE_030, "lags": out,
           "lambda": round(lam, 3) if lam else None,
           "half_life": round(half, 2) if half else None,
           "components_mean": round(st.mean(comps), 1) if comps else None,
           "two_peak_worlds": two_peak_worlds, "worlds": len(comps), "spectra": spectra}

    collapsed = (res["components_mean"] or 0) < MIN_COMPONENTS or (out[1]["pairs"] or 0) < MIN_PAIRS
    if collapsed:
        verdict = "void: the composite world collapsed or gave too few divisions"
    elif two_peak_worlds < max(2, len(comps) // 2):
        verdict = "void: the composite did not put two peaks into the spectrum"
    elif half and half < 1.0 and SINGLE_SCALE_030 / half >= 1.3:
        verdict = "supports the causal reading: an imposed second scale shortens memory by >= 1.3x"
    elif half and half > 1.3:
        verdict = "refutes it: memory stayed at the single-scale level"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x78b] written: {OUT.name}")

    print(f"  components mean={res['components_mean']} worlds={res['worlds']} two-peak worlds={two_peak_worlds}")
    print(f"  pairs {out[1]['pairs']}/{out[2]['pairs']}/{out[3]['pairs']}  rho {r1}/{r2}/{r3}  "
          f"lambda={res['lambda']} half={res['half_life']} (single-scale 0.030 = 1.47)")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
