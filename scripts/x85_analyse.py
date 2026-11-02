"""x85_analyse.py — does the symmetry of the pattern carry the size memory?

Criteria: `reports/2026-11-02-x85-symmetry-memory-plan.md`. Per world: the symmetry `s` (X84's angular instrument), the axis period
`q'`, the depth correlations `rho1..3` from `uid_pairs`, a per-world `lambda`/half-life, components.

Primary: `rho1` against `s` **within** each inflow (eight worlds) and the pooled rank partial correlation controlling inflow.

Run:
    python scripts/x85_analyse.py --write
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
FIELDS = L1 / "_x85_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x85_symmetry_memory.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
FLOWS = {"f025": 0.025, "f030": 0.030, "f035": 0.035}
CONTROL_RHO1 = (0.45, 0.56)     # X74's single-scale 0.030 cell
CONTROL_S = (0.64, 0.81)        # X71's 0.035 symmetry
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


def partial_spearman(x: list[float], y: list[float], z: list[float]) -> float | None:
    rxy, rxz, ryz = spearman(x, y), spearman(x, z), spearman(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = (1 - rxz ** 2) * (1 - ryz ** 2)
    if den <= 0:
        return None
    return round((rxy - rxz * ryz) / math.sqrt(den), 3)


def cell_stats(flow: str) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, worlds = [], []
    for path in sorted(L1.glob(f"x85_{flow}_pattern_s*.json")):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        f = FIELDS / f"{path.stem}_t6000.npy"
        ang = angular(f) if f.is_file() else {"q_axis": None, "symmetry": None}
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
        worlds.append({"seed": seed, "s": ang["symmetry"], "q_axis": ang["q_axis"],
                       "field_std": ang.get("field_std")})

    out = {"flow": FLOWS[flow], "worlds": len(worlds),
           "components_mean": round(st.mean(comps), 1) if comps else None}
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

    syms = [x["s"] for x in worlds if x["s"] is not None]
    out["symmetry_median"] = round(st.median(syms), 3) if syms else None
    out["symmetry_range"] = [min(syms), max(syms)] if syms else None
    out["q_axis"] = [x["q_axis"] for x in worlds]
    out["world_detail"] = worlds

    rho1s = [per_lag[1]["worlds"][x["seed"]]["rho"] for x in worlds]
    pairs = [(s, r) for s, r in zip([x["s"] for x in worlds], rho1s) if s is not None and r is not None]
    out["within_cell_rho1_vs_s"] = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 4 else None
    out["worlds_with_both"] = len(pairs)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X85 symmetry and memory")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x85_symmetry_memory", "experiment": "X85",
           "command": "python scripts/x85_analyse.py --write",
           "prereg": "reports/2026-11-02-x85-symmetry-memory-plan.md",
           "primary": "rho1 against the symmetry s; within-cell Spearman and a pooled rank partial correlation controlling inflow",
           "cells": {}}
    for flow in FLOWS:
        res["cells"][flow] = cell_stats(flow)

    c = res["cells"]
    # pooled partial correlation over all worlds, controlling inflow
    xs, ys, zs = [], [], []
    for flow, cell in c.items():
        for w in cell["world_detail"]:
            rho1 = cell["1"]["worlds"].get(w["seed"], {}).get("rho")
            if w["s"] is None or rho1 is None:
                continue
            xs.append(float(w["s"]))
            ys.append(float(rho1))
            zs.append(FLOWS[flow])
    res["pooled"] = {"worlds": len(xs), "rho_s_rho1": spearman(xs, ys),
                     "rho_s_flow": spearman(xs, zs), "rho_rho1_flow": spearman(ys, zs),
                     "partial_rho1_s_given_flow": partial_spearman(ys, xs, zs)}

    control_a = c["f030"]["1"]["rho"] is not None and CONTROL_RHO1[0] <= c["f030"]["1"]["rho"] <= CONTROL_RHO1[1]
    control_b = c["f035"]["symmetry_median"] is not None and CONTROL_S[0] <= c["f035"]["symmetry_median"] <= CONTROL_S[1]
    res["positive_control"] = {"fires": bool(control_a and control_b),
                               "f030_rho1": c["f030"]["1"]["rho"], "band_rho1": list(CONTROL_RHO1),
                               "f035_symmetry": c["f035"]["symmetry_median"], "band_symmetry": list(CONTROL_S)}

    void = [k for k, x in c.items()
            if (x["components_mean"] or 0) < 10 or (x["1"]["pairs"] or 0) < 400
            or x["symmetry_range"] is None or (x["symmetry_range"][1] - x["symmetry_range"][0]) < 0.05]
    within = {k: x["within_cell_rho1_vs_s"] for k, x in c.items()}
    res["within_cell"] = within
    negative = [k for k, v in within.items() if v is not None and v <= -0.5]
    positive = [k for k, v in within.items() if v is not None and v >= 0.5]
    flat = all(v is not None and -0.3 <= v <= 0.3 for v in within.values())
    part = res["pooled"]["partial_rho1_s_given_flow"]

    if void:
        verdict = f"void: collapsed, underpowered or no spread to correlate: {void}"
    elif not res["positive_control"]["fires"]:
        verdict = "void: the positive control did not fire (rho1 or symmetry out of band)"
    elif len(negative) >= 2 and part is not None and part <= -0.45:
        verdict = "symmetry carries memory: rho1 falls as the pattern locks to the forcing, in at least two cells and in the pooled partial correlation"
    elif len(positive) >= 2 or flat:
        verdict = "symmetry does not carry memory: the coefficients are positive or all inside +/-0.3"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x85] written: {OUT.name}")

    for k, x in c.items():
        print(f"  {k}: s={x['symmetry_median']} {x['symmetry_range']} q'={x['q_axis']} rho1={x['1']['rho']} "
              f"half_median={x['half_life_median']} fit={x['worlds_fittable']} within={x['within_cell_rho1_vs_s']}")
    print("  pooled:", res["pooled"])
    print("  control:", res["positive_control"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
