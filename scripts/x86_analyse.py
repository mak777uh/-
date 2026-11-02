"""x86_analyse.py — place the symmetry curve, then read the memory against it.

Criteria: `reports/2026-11-02-x86-symmetry-curve-plan.md`. Three inflows, twenty worlds each, one logging regime.

Two questions in one dataset:
1. the curve `s(F)` with its spread (the axis every memory number in this line is reported against);
2. `rho1` against `s` — the question X85 registered but could not test, now with twenty worlds per cell.

Identity convention note: these runs inherit X71's (`--split-new-uid` off), because the symmetry numbers they are compared with come
from X71. Heredity levels are therefore not directly comparable with X73–X76, which split; the correlations are internal to this
series and need no such comparison.

Run:
    python scripts/x86_analyse.py --write
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
FIELDS = L1 / "_x86_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x86_symmetry_curve.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
FLOWS = {"f025": 0.025, "f030": 0.030, "f035": 0.035}
FORCING_Q = 8
CONTROL_GAP = 0.15          # s(0.035) - s(0.025) must be at least this
CONTROL_F030 = (0.50, 0.78)  # envelope of the two existing 50-step series (0.603, 0.671)
RESOLUTION = 0.05           # declared detectable difference between adjacent cell medians


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
    for path in sorted(L1.glob(f"x86_{flow}_pattern_s*.json")):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        f = FIELDS / f"{path.stem}_t6000.npy"
        ang = angular(f) if f.is_file() else {"q_axis": None, "symmetry": None, "field_std": None}
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

    syms = sorted(x["s"] for x in worlds if x["s"] is not None)
    out["symmetry_median"] = round(st.median(syms), 3) if syms else None
    out["symmetry_iqr"] = [round(st.quantiles(syms, n=4)[0], 3), round(st.quantiles(syms, n=4)[2], 3)] if len(syms) >= 4 else None
    out["symmetry_range"] = [min(syms), max(syms)] if syms else None
    out["symmetry_sd"] = round(st.pstdev(syms), 3) if len(syms) > 1 else None
    out["q_axis"] = [x["q_axis"] for x in worlds]
    out["world_detail"] = worlds

    pairs = [(w["s"], per_lag[1]["worlds"][w["seed"]]["rho"]) for w in worlds
             if w["s"] is not None and per_lag[1]["worlds"].get(w["seed"], {}).get("rho") is not None]
    out["within_cell_rho1_vs_s"] = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 5 else None
    out["worlds_with_both"] = len(pairs)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X86 symmetry curve and memory")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x86_symmetry_curve", "experiment": "X86",
           "command": "python scripts/x86_analyse.py --write",
           "prereg": "reports/2026-11-02-x86-symmetry-curve-plan.md",
           "logging_regime": 50,
           "identity_note": "split_new_uid off (X71's convention) so the symmetry numbers match X71's; heredity levels are not "
                            "directly comparable with X73-X76",
           "resolution": RESOLUTION, "cells": {}}
    for flow in FLOWS:
        res["cells"][flow] = cell_stats(flow)

    c = res["cells"]
    med = {k: v["symmetry_median"] for k, v in c.items()}
    ordered = all(med[a] is not None and med[b] is not None for a, b in (("f025", "f030"), ("f030", "f035")))
    order_ok = ordered and med["f025"] < med["f030"] < med["f035"]
    gap = round(med["f035"] - med["f025"], 3) if ordered else None
    control = bool(order_ok and gap is not None and gap >= CONTROL_GAP
                   and med["f030"] is not None and CONTROL_F030[0] <= med["f030"] <= CONTROL_F030[1])
    res["positive_control"] = {"fires": control, "medians": med, "gap_025_035": gap,
                              "required_gap": CONTROL_GAP, "f030_band": list(CONTROL_F030)}

    void = [k for k, x in c.items()
            if (x["components_mean"] or 0) < 10 or (x["1"]["pairs"] or 0) < 400
            or x["symmetry_range"] is None or (x["symmetry_range"][1] - x["symmetry_range"][0]) < 0.05]
    steps = {"030-025": round(med["f030"] - med["f025"], 3) if ordered else None,
             "035-030": round(med["f035"] - med["f030"], 3) if ordered else None}

    xs, ys, zs = [], [], []
    for flow, cell in c.items():
        for w in cell["world_detail"]:
            rho1 = cell["1"]["worlds"].get(w["seed"], {}).get("rho")
            if w["s"] is None or rho1 is None:
                continue
            xs.append(float(w["s"]))
            ys.append(float(rho1))
            zs.append(FLOWS[flow])
    res["memory"] = {"worlds": len(xs), "rho_s_rho1": spearman(xs, ys), "rho_s_flow": spearman(xs, zs),
                     "rho_rho1_flow": spearman(ys, zs), "partial_rho1_s_given_flow": partial_spearman(ys, xs, zs),
                     "within_cell": {k: v["within_cell_rho1_vs_s"] for k, v in c.items()}}

    if void:
        verdict = f"void: collapsed, underpowered or no spread to place: {void}"
    elif not control:
        verdict = "void: the positive control did not fire (ordering, gap or the 0.030 band)"
    elif min(s for s in steps.values() if s is not None) >= RESOLUTION:
        verdict = "curve placed: every adjacent pair of cell medians differs by at least the declared resolution"
    elif min(abs(s) for s in steps.values() if s is not None) < RESOLUTION:
        verdict = "curve flat within resolution: at least one adjacent pair differs by less than 0.05"
    else:
        verdict = "inconclusive"
    res["steps"] = steps
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x86] written: {OUT.name}")

    for k, x in c.items():
        print(f"  {k}: s={x['symmetry_median']} iqr={x['symmetry_iqr']} sd={x['symmetry_sd']} range={x['symmetry_range']} "
              f"q'={sorted(set(q for q in x['q_axis'] if q))} rho1={x['1']['rho']} half={x['half_life_median']} "
              f"fit={x['worlds_fittable']} within={x['within_cell_rho1_vs_s']}")
    print("  control:", res["positive_control"])
    print("  steps:", steps)
    print("  memory:", res["memory"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
