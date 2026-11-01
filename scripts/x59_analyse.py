"""x59_analyse.py — amplitude dose-response: does transmission fall as the inflow smooths?

Reads `x59_<arm>_s<seed>.json` for arms `a50`, `a25`, `a10` and the saved fields in `x59_fields/`, and applies the
preregistered criterion (`reports/2026-11-01-x59-amplitude-dose-plan.md`):

    medians strictly ordered a50 > a25 > a10,
    the extreme pair separated by at least a factor of 2,
    at least 4 of 5 seeds agreeing on that pair,
    spectral entropy ordered the same way at t = 6000 (more amplitude, broader spectrum).

Run:
    python scripts/x59_analyse.py --write
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
FIELDS = L1 / "x59_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x59_dose.json"

ARMS = ("a50", "a25", "a10")
SIGN_BAR = 4
FACTOR_BAR = 2.0


def load(arm: str) -> dict[int, dict]:
    out = {}
    for f in sorted(glob.glob(str(L1 / f"x59_{arm}_s*.json"))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        sel = d.get("selection") or {}
        out[seed] = {"splits": sel.get("splits"), "pairs": sel.get("parent_child_pairs"),
                     "r": sel.get("inheritability_r"), "s_mean_last": sel.get("s_mean_last")}
    return out


def spectral_entropy(arm: str, t: int) -> dict | None:
    ps = []
    for seed in range(171, 176):
        f = FIELDS / f"x59_{arm}_s{seed}_t{t}.npy"
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
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, 13) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    q = max(shares, key=shares.get)
    return {"q_peak": q, "peak_share": round(shares[q], 3), "entropy": round(ent, 3),
            "entropy_max_ln12": round(math.log(12), 3)}


def med(values):
    v = [x for x in values if x is not None]
    return round(st.median(v), 2) if v else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X59: amplitude dose-response")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    data = {arm: load(arm) for arm in ARMS}
    if not any(data.values()):
        print("[x59] нет прогонов")
        return 0

    arms = {}
    for arm in ARMS:
        rows = data[arm]
        if rows:
            arms[arm] = {"n": len(rows), "splits_median": med([r["splits"] for r in rows.values()]),
                         "pairs_median": med([r["pairs"] for r in rows.values()]),
                         "r_median": med([r["r"] for r in rows.values()]),
                         "s_mean_last_median": med([r["s_mean_last"] for r in rows.values()])}

    order = {a: arms[a]["splits_median"] for a in ARMS if a in arms}
    ordered = (order["a50"] > order["a25"] > order["a10"]) if len(order) == 3 else False
    factor = (order["a50"] / order["a10"]) if len(order) == 3 and order["a10"] else None

    extremes = []
    for s in sorted(set(data["a50"]) & set(data["a10"])):
        a, b = data["a50"][s]["splits"], data["a10"][s]["splits"]
        if a is not None and b is not None:
            extremes.append(a - b)
    seeds_agree = sum(1 for d in extremes if d > 0)

    spectra = {arm: spectral_entropy(arm, 6000) for arm in ARMS}
    ent_ordered = None
    if all(spectra.get(a) for a in ARMS):
        ent_ordered = spectra["a50"]["entropy"] > spectra["a25"]["entropy"] > spectra["a10"]["entropy"]

    supported = bool(ordered and factor and factor >= FACTOR_BAR and seeds_agree >= SIGN_BAR)
    out = {
        "kind": "l1_field_x59_dose",
        "experiment": "X59",
        "command": "python scripts/x59_analyse.py --write",
        "prereg": "reports/2026-11-01-x59-amplitude-dose-plan.md",
        "criterion": {"sign_bar": SIGN_BAR, "factor_bar": FACTOR_BAR,
                      "prediction": "splits fall monotonically with inflow amplitude, spectrum broadens with it"},
        "arms": arms,
        "ordering": {"strictly_ordered": ordered, "extreme_factor": round(factor, 2) if factor else None,
                     "seeds_agreeing": seeds_agree, "n_pairs": len(extremes)},
        "spectra_t6000": spectra,
        "entropy_ordered": ent_ordered,
        "prediction_supported": supported,
        "not_claimed": [
            "five seeds per amplitude; the argument is the ordering, not a test",
            "splits count events under the overlap rule, not verified lineages",
            "the amplitude also changes how much area is occupied, so the dose is not a pure geometry knob",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x59] written: {OUT.name}")
    for arm, a in arms.items():
        print("  %-4s n=%d splits=%s pairs=%s r=%s s_end=%s" % (
            arm, a["n"], a["splits_median"], a["pairs_median"], a["r_median"], a["s_mean_last_median"]))
    print("  ordered:", ordered, "factor:", out["ordering"]["extreme_factor"],
          "seeds:", seeds_agree, "/", len(extremes))
    for arm, sp in spectra.items():
        if sp:
            print("  %-4s H=%s peak=%s at q=%s" % (arm, sp["entropy"], sp["peak_share"], sp["q_peak"]))
    print("  prediction supported:", supported)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
