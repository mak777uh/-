"""x82_analyse.py — prescribed vs realised spectral share: how far does inflow modulation reach?

Criteria: `reports/2026-11-02-x82-reach-plan.md`. The realised share is measured from the saved field with the definition fixed in
the preregistration: the dominant family is the local maximum in bins [6, 9], the second family the local maximum in [10, 13]
(q = 11 cells) or [13, 18] (q = 14 cell), each summed over `abs(k - q*) <= 1`, and the share is `P2 / (P1 + P2)`.

Run:
    python scripts/x82_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x82_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x82_reach.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x60_analyse import radial_profile  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
CELLS = {
    "s0_q11": {"share": 0.0, "q2_window": (10, 13)},
    "s1_q11": {"share": 1.0, "q2_window": (10, 13)},
    "s4_q11": {"share": 4.0, "q2_window": (10, 13)},
    "s16_q11": {"share": 16.0, "q2_window": (10, 13)},
    "s4_q14": {"share": 4.0, "q2_window": (13, 18)},
}
CONTROL_BAND = (0.45, 0.56)


def family_power(prof: dict[int, float], window: tuple[int, int]) -> tuple[int | None, float]:
    keys = [k for k in sorted(prof) if window[0] <= k <= window[1]]
    if not keys:
        return None, 0.0
    q = max(keys, key=lambda k: prof[k])
    total = sum(prof[k] for k in prof if abs(k - q) <= 1)
    return q, float(total)


def angular(path: Path) -> dict:
    """Axis-aligned period q' and symmetry s = P_diag/(P_diag+P_axis) (X84's instrument).

    X84 showed that a radial share cannot tell the forcing diagonal from a stripe morphology, so the X82 aggregate carries both readings:
    the preregistered radial share *and* the angular one, which is the one that can be interpreted.
    """
    v = np.load(path)
    n = v.shape[0]
    std = float(v.std())
    if std < 0.01:
        return {"q_axis": None, "wavelength_cells": None, "symmetry": None, "field_std": round(std, 4)}
    spec = np.abs(np.fft.fft2(v - v.mean())) ** 2

    def pw(ky: int, kx: int, rad: int = 1) -> float:
        total = 0.0
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                total += float(spec[(ky + dy) % n, (kx + dx) % n])
        return total

    q_forcing = 8  # 12.0-cell checkerboard
    p_diag = sum(pw(sy * q_forcing, sx * q_forcing) for sy in (1, -1) for sx in (1, -1))
    best_q, best_val = 0, -1.0
    for q in range(4, 15):
        val = pw(q, 0) + pw(0, q)
        if val > best_val:
            best_q, best_val = q, val
    sym = p_diag / (p_diag + best_val) if (p_diag + best_val) > 0 else None
    return {"q_axis": best_q, "wavelength_cells": round(n / best_q, 1) if best_q else None,
            "symmetry": round(sym, 3) if sym is not None else None, "field_std": round(std, 4)}


def realised_share(path: Path, q2_window: tuple[int, int]) -> dict:
    prof = radial_profile(np.load(path))
    q1, p1 = family_power(prof, (6, 9))
    q2, p2 = family_power(prof, q2_window)
    share = p2 / (p1 + p2) if (p1 + p2) > 0 else None
    return {"q1": q1, "q2": q2, "p1": round(p1, 1), "p2": round(p2, 1),
            "share": round(share, 3) if share is not None else None}


def cell_stats(cell: str) -> dict:
    spec = CELLS[cell]
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, shares, details = [], [], {}
    for path in sorted(L1.glob(f"x82_{cell}_s*.json")):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        f = FIELDS / f"{path.stem}_t6000.npy"
        if f.is_file():
            r = realised_share(f, spec["q2_window"])
            details[seed] = r
            if r["share"] is not None:
                shares.append(r["share"])
        for k in LAGS:
            pairs = []
            for uid in w["peaks"]:
                anc = ancestors(uid, w["parent"], k)
                if anc is None or anc not in w["peaks"]:
                    continue
                pairs.append((w["peaks"][anc], w["peaks"][uid]))
            per_lag[k]["pairs"].extend(pairs)
            rho = spearman([a for a, _ in pairs], [b for _, b in pairs])
            per_lag[k]["worlds"][seed] = {"pairs": len(pairs), "rho": round(rho, 3) if rho is not None else None}

    out = {"prescribed_share": spec["share"], "worlds": len(comps),
           "components_mean": round(st.mean(comps), 1) if comps else None,
           "share_median": round(st.median(shares), 3) if shares else None,
           "share_range": [min(shares), max(shares)] if shares else None,
           "share_worlds": details}
    ang = [angular(f) for f in (FIELDS / f"{p.stem}_t6000.npy" for p in sorted(L1.glob(f"x82_{cell}_s*.json"))) if f.is_file()]
    syms = [a["symmetry"] for a in ang if a["symmetry"] is not None]
    out["angular"] = {
        "q_axis": [a["q_axis"] for a in ang],
        "wavelength_cells": [a["wavelength_cells"] for a in ang],
        "symmetry_median": round(st.median(syms), 3) if syms else None,
        "symmetry_range": [min(syms), max(syms)] if syms else None,
        "worlds": len(ang),
    }

    for k in LAGS:
        pairs = per_lag[k]["pairs"]
        out[str(k)] = {"pairs": len(pairs),
                       "rho": round(spearman([a for a, _ in pairs], [b for _, b in pairs]) or 0.0, 3) if pairs else None,
                       "worlds": per_lag[k]["worlds"]}

    # per-world lambda and half-life (the X80 correction: pooled and per-world answers may disagree)
    halfs, fittable = [], 0
    for seed in per_lag[1]["worlds"]:
        rs = [per_lag[k]["worlds"].get(seed, {}).get("rho") for k in LAGS]
        if any(r is None for r in rs):
            continue
        ratios = [x / y for x, y in ((rs[1], rs[0]), (rs[2], rs[1])) if x is not None and y is not None and x > 0 and y > 0]
        if not ratios:
            continue
        lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
        fittable += 1
        if 0 < lam < 1:
            halfs.append(math.log(0.5) / math.log(lam))
    out["worlds_fittable"] = f"{fittable}/{len(per_lag[1]['worlds'])}"
    out["half_life_median"] = round(st.median(halfs), 2) if halfs else None
    out["half_life_range"] = [round(min(halfs), 2), round(max(halfs), 2)] if halfs else None

    r1, r2, r3 = out["1"]["rho"], out["2"]["rho"], out["3"]["rho"]
    if r1 and r2 and r3 and r1 > 0:
        ratios = [x / y for x, y in ((r2, r1), (r3, r2)) if x > 0 and y > 0]
        lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios)) if ratios else None
        out["lambda_pooled"] = round(lam, 3) if lam else None
        out["half_life_pooled"] = round(math.log(0.5) / math.log(lam), 2) if lam and 0 < lam < 1 else None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X82 reach of the imposed second peak")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x82_reach", "experiment": "X82",
           "command": "python scripts/x82_analyse.py --write",
           "prereg": "reports/2026-11-02-x82-reach-plan.md",
           "share_definition": "P2/(P1+P2), families as local maxima in [6,9] and [10,13] or [13,18], each summed over abs(k-q*)<=1",
           "control_band": list(CONTROL_BAND), "cells": {}}
    for cell in CELLS:
        res["cells"][cell] = cell_stats(cell)

    c = res["cells"]
    s0, s1, s4, s16, s4q14 = (c["s0_q11"], c["s1_q11"], c["s4_q11"], c["s16_q11"], c["s4_q14"])

    void = [k for k, x in c.items()
            if (x["components_mean"] or 0) < 10 or (x["1"]["pairs"] or 0) < 400
            or x["share_median"] is None
            or any(v.get("q2") is None for v in x["share_worlds"].values())]
    control = (s0["share_median"] is not None and s0["share_median"] < 0.15
               and s0["1"]["rho"] is not None and CONTROL_BAND[0] <= s0["1"]["rho"] <= CONTROL_BAND[1])
    res["positive_control"] = {"fires": bool(control), "share_median": s0["share_median"], "rho1": s0["1"]["rho"]}

    def diff(a, b):
        return None if a["share_median"] is None or b["share_median"] is None else round(b["share_median"] - a["share_median"], 3)

    steps = {"share(4) - share(1)": diff(s1, s4), "share(16) - share(4)": diff(s4, s16),
             "share(4,q11) - share(4,q14)": diff(s4, s4q14)}
    res["steps"] = steps

    if void:
        verdict = f"void: collapsed, underpowered or unreadable cells: {void}"
    elif not control:
        verdict = ("void: the single-scale control did not fire — the radial share of a world with no imposed second scale is "
                   f"{s0['share_median']}, so the radial share is not measuring an imposed peak at all (X84: it mixes the forcing "
                   "diagonal with the structure band); the angular readout is carried alongside and is the interpretable one")
    elif (steps["share(4) - share(1)"] or 0) >= 0.05 and (steps["share(16) - share(4)"] or 0) < 0.05:
        verdict = "saturating: the realised share rises from 1 to 4 and then stops, so the channel has a ceiling near a third"
    elif (steps["share(16) - share(4)"] or 0) >= 0.05:
        verdict = "graded: the realised share still grows at prescribed 16, so the ceiling has not been reached"
    else:
        verdict = "inconclusive"
    if abs(steps["share(4,q11) - share(4,q14)"] or 0) >= 0.05:
        verdict += "; wavelength-dependent (the q = 14 cell differs from q = 11 at the same prescribed share)"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x82] written: {OUT.name}")

    for k, x in c.items():
        a = x["angular"]
        print(f"  {k}: prescribed={x['prescribed_share']} radial share={x['share_median']} {x['share_range']} "
              f"| q'={a['q_axis']} s={a['symmetry_median']} {a['symmetry_range']} "
              f"| comp={x['components_mean']} rho1={x['1']['rho']} half_pooled={x.get('half_life_pooled')} "
              f"half_median={x['half_life_median']} fit={x['worlds_fittable']}")
    print("  control:", res["positive_control"])
    print("  steps:", steps)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
