"""x88_analyse.py — the percolating arm: does memory rise again above the band, or keep declining?

Criteria: `reports/2026-11-02-x88-percolating-arm-plan.md`. Three inflows (0.040 / 0.045 / 0.050), twenty worlds each, flags identical
to X87 so the per-world half-lives are comparable with 1.82 / 1.16 / 1.07.

The primary readout is the per-world median half-life with its range and fittable count; `rho1` is the level beside it. The regime
check is deliberately the opposite of the lattice cells: few components and beta1 > 0.

Run:
    python scripts/x88_analyse.py --write
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
FIELDS = L1 / "_x88_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x88_percolating_arm.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from x60_analyse import beta0, drop_small, euler  # noqa: E402

LAGS = (1, 2, 3)
THRESHOLD = 0.2
MIN_CELLS = 5
FLOWS = {"f040": 0.040, "f045": 0.045, "f050": 0.050}
REF_HALF_035 = 1.07          # X87, twenty worlds at F = 0.035
CONTROL_RHO1 = (0.42, 0.55)  # X74's F = 0.040, five worlds, same convention
CONTROL_HALF = (1.2, 2.3)
RESOLUTION = 0.40
FORCING_Q = 8


def angular(path: Path) -> dict:
    v = np.load(path)
    n = v.shape[0]
    std = float(v.std())
    if std < 0.01:
        return {"q_axis": None, "symmetry": None, "field_std": round(std, 4)}
    spec = np.abs(np.fft.fft2(v - v.mean())) ** 2

    def pw(ky: int, kx: int, rad: int = 1) -> float:
        total = 0.0
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                total += float(spec[(ky + dy) % n, (kx + dx) % n])
        return total

    p_diag = sum(pw(sy * FORCING_Q, sx * FORCING_Q) for sy in (1, -1) for sx in (1, -1))
    best_q, best_val = 0, -1.0
    for q in range(4, 15):
        val = pw(q, 0) + pw(0, q)
        if val > best_val:
            best_q, best_val = q, val
    sym = p_diag / (p_diag + best_val) if (p_diag + best_val) > 0 else None
    return {"q_axis": best_q, "symmetry": round(sym, 3) if sym is not None else None, "field_std": round(std, 4)}


def cell_stats(flow: str) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, betas, worlds = [], [], []
    for path in sorted(L1.glob(f"x88_{flow}_pattern_s*.json")):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        series = d.get("series") or []
        comps.append(st.mean([s.get("components") or 0 for s in series]))
        f = FIELDS / f"{path.stem}_t6000.npy"
        ang = angular(f) if f.is_file() else {"q_axis": None, "symmetry": None, "field_std": None}
        # beta1 = beta0 - chi on the saved field (the regime check: the percolating arm has holes)
        b1 = None
        if f.is_file():
            mask = drop_small(np.load(f) > THRESHOLD, MIN_CELLS)
            b1 = int(round(beta0(mask) - euler(mask)))
        betas.append(b1)
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
        worlds.append({"seed": seed, "s": ang["symmetry"], "q_axis": ang["q_axis"], "field_std": ang.get("field_std")})

    out = {"flow": FLOWS[flow], "worlds": len(worlds),
           "components_median": round(st.median(comps), 1) if comps else None,
           "components_range": [min(comps), max(comps)] if comps else None,
           "b1_positive_worlds": sum(1 for b in betas if b) if any(b is not None for b in betas) else None}
    for k in LAGS:
        pairs = per_lag[k]["pairs"]
        out[str(k)] = {"pairs": len(pairs),
                       "rho": round(spearman([a for a, _ in pairs], [b for _, b in pairs]) or 0.0, 3) if pairs else None,
                       "worlds": per_lag[k]["worlds"]}

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
    out["half_life_iqr"] = [round(st.quantiles(halfs, n=4)[0], 2), round(st.quantiles(halfs, n=4)[2], 2)] if len(halfs) >= 4 else None
    out["half_life_individual"] = [round(h, 2) for h in halfs]
    syms = [x["s"] for x in worlds if x["s"] is not None]
    out["symmetry_median"] = round(st.median(syms), 3) if syms else None
    out["world_detail"] = worlds
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X88 percolating arm")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x88_percolating_arm", "experiment": "X88",
           "command": "python scripts/x88_analyse.py --write",
           "prereg": "reports/2026-11-02-x88-percolating-arm-plan.md",
           "reference_half_life_035": REF_HALF_035, "resolution": RESOLUTION,
           "cells": {}}
    for flow in FLOWS:
        res["cells"][flow] = cell_stats(flow)
    c = res["cells"]

    regime_ok = all((x["components_median"] or 0) < 15 and (x["b1_positive_worlds"] or 0) >= 15 for x in c.values())
    control_a = c["f040"]["1"]["rho"] is not None and CONTROL_RHO1[0] <= c["f040"]["1"]["rho"] <= CONTROL_RHO1[1]
    control_b = c["f040"]["half_life_median"] is not None and CONTROL_HALF[0] <= c["f040"]["half_life_median"] <= CONTROL_HALF[1]
    res["regime"] = {"percolating": bool(regime_ok),
                     "detail": {k: [x["components_median"], x["b1_positive_worlds"]] for k, x in c.items()}}
    res["positive_control"] = {"fires": bool(regime_ok and control_a and control_b),
                               "f040_rho1": c["f040"]["1"]["rho"], "band_rho1": list(CONTROL_RHO1),
                               "f040_half": c["f040"]["half_life_median"], "band_half": list(CONTROL_HALF)}

    void = [k for k, x in c.items() if (x["1"]["pairs"] or 0) < 400 or x["half_life_median"] is None]
    halves = {k: x["half_life_median"] for k, x in c.items()}

    if void:
        verdict = f"void: underpowered or unfittable cells: {void}"
    elif not res["positive_control"]["fires"]:
        verdict = "void: the positive control did not fire (regime, rho1 band or half-life band)"
    elif any(halves[k] is not None and halves[k] - REF_HALF_035 >= RESOLUTION for k in ("f045", "f050")):
        verdict = "rise: memory turns back up above the band, so the two-armed shape survives"
    elif all(halves[k] is not None for k in halves) and halves["f040"] <= halves["f045"] + RESOLUTION \
            and halves["f045"] <= halves["f050"] + RESOLUTION:
        verdict = "decline: no U — memory stays short above the band and the curve is monotone"
    else:
        verdict = "inconclusive"
    res["halves"] = halves
    res["steps_from_035"] = {k: (round(v - REF_HALF_035, 2) if v is not None else None) for k, v in halves.items()}
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x88] written: {OUT.name}")

    for k, x in c.items():
        print(f"  {k}: half={x['half_life_median']} iqr={x['half_life_iqr']} range={x['half_life_range']} "
              f"rho1={x['1']['rho']} pairs={x['1']['pairs']} fit={x['worlds_fittable']} "
              f"comp={x['components_median']} b1+={x['b1_positive_worlds']} s={x['symmetry_median']}")
    print("  regime:", res["regime"], " control:", res["positive_control"])
    print("  steps from 1.07:", res["steps_from_035"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
