"""x62_analyse.py — correlation length against turnover.

Applies the preregistered criterion of `reports/2026-11-01-x62-correlation-length-plan.md`:

    splits ordered s04 > s12 > s24,
    extreme pair separated by at least a factor of 2,
    at least 4 of 5 seeds agreeing on that pair,
    entropy at s24 below entropy at s04.

Run:
    python scripts/x62_analyse.py --write
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
FIELDS = L1 / "x62_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x62_scale.json"

ARMS = ("s04", "s12", "s24")
SIGN_BAR = 4
FACTOR_BAR = 2.0


def load(arm: str) -> dict[int, dict]:
    out = {}
    for f in sorted(glob.glob(str(L1 / f"x62_{arm}_s*.json"))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        sel = d.get("selection") or {}
        out[seed] = {"splits": sel.get("splits"), "pairs": sel.get("parent_child_pairs"),
                     "r": sel.get("inheritability_r"), "s_mean_last": sel.get("s_mean_last"),
                     "components": (d.get("heterogeneity") or {}).get("components_last")}
    return out


def spectrum(arm: str, t: int = 6000) -> dict | None:
    ps = []
    for seed in range(171, 176):
        f = FIELDS / f"x62_{arm}_s{seed}_t{t}.npy"
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
    q = max(shares, key=shares.get)
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    return {"q_peak": q, "peak_share": round(shares[q], 3), "entropy": round(ent, 3),
            "entropy_max_ln12": round(math.log(12), 3)}


def med(values):
    v = [x for x in values if x is not None]
    return round(st.median(v), 2) if v else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X62: correlation length")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    data = {arm: load(arm) for arm in ARMS}
    if not any(data.values()):
        print("[x62] нет прогонов")
        return 0

    arms = {}
    for arm in ARMS:
        rows = data[arm]
        if rows:
            arms[arm] = {"n": len(rows), "splits_median": med([r["splits"] for r in rows.values()]),
                         "pairs_median": med([r["pairs"] for r in rows.values()]),
                         "r_median": med([r["r"] for r in rows.values()]),
                         "components_median": med([r["components"] for r in rows.values()]),
                         "s_mean_last_median": med([r["s_mean_last"] for r in rows.values()])}

    ordered = (arms["s04"]["splits_median"] > arms["s12"]["splits_median"] > arms["s24"]["splits_median"]) \
        if len(arms) == 3 else False
    factor = (arms["s04"]["splits_median"] / arms["s24"]["splits_median"]) \
        if len(arms) == 3 and arms["s24"]["splits_median"] else None

    diffs = []
    for s in sorted(set(data["s04"]) & set(data["s24"])):
        a, b = data["s04"][s]["splits"], data["s24"][s]["splits"]
        if a is not None and b is not None:
            diffs.append(a - b)
    agree = sum(1 for d in diffs if d > 0)

    spectra = {arm: spectrum(arm) for arm in ARMS}
    ent_ok = None
    if spectra["s04"] and spectra["s24"]:
        ent_ok = spectra["s24"]["entropy"] < spectra["s04"]["entropy"]

    supported = bool(ordered and factor and factor >= FACTOR_BAR and agree >= SIGN_BAR)

    out = {
        "kind": "l1_field_x62_scale",
        "experiment": "X62",
        "command": "python scripts/x62_analyse.py --write",
        "prereg": "reports/2026-11-01-x62-correlation-length-plan.md",
        "criterion": {"sign_bar": SIGN_BAR, "factor_bar": FACTOR_BAR,
                      "prediction": "splits ordered s04 > s12 > s24; entropy s24 < s04"},
        "arms": arms,
        "ordering": {"as_predicted": ordered, "extreme_factor": round(factor, 2) if factor else None,
                     "seeds_agreeing": agree, "n_pairs": len(diffs)},
        "spectra_t6000": spectra,
        "entropy_ordered": ent_ok,
        "prediction_supported": supported,
        "not_claimed": [
            "five seeds per arm; the argument is the ordering, not a test",
            "correlation length and amplitude both change the occupied area, so the knob is not pure",
            "splits count events under the overlap rule, not verified lineages",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x62] written: {OUT.name}")
    for arm, a in arms.items():
        print("  %-4s n=%d splits=%s pairs=%s r=%s components=%s" % (
            arm, a["n"], a["splits_median"], a["pairs_median"], a["r_median"], a["components_median"]))
    print("  ordered:", ordered, "factor:", out["ordering"]["extreme_factor"], "seeds:", agree, "/", len(diffs))
    for arm, sp in spectra.items():
        if sp:
            print("  %-4s H=%s peak=%s at q=%s" % (arm, sp["entropy"], sp["peak_share"], sp["q_peak"]))
    print("  prediction supported:", supported)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
