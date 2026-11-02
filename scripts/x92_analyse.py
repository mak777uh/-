"""x92_analyse.py — does size pay? Peak area against lifetime and against the number of daughters.

Criteria: `reports/2026-11-02-x92-pay-plan.md`. Reads the stored artifacts of X87 (0.025 / 0.030 / 0.035) and X88 (0.040): every uid's
`first`, `last` and `peak` from `uid_outcomes`, and the parent→child pairs from `uid_pairs`.

The honest readout is the partial correlation of area with the number of daughters controlling lifetime, because a longer-lived uid has
more chances to divide. The null is a within-world shuffle of areas.

Run:
    python scripts/x92_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x92_pay.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402

CELLS = {
    # twenty worlds per lattice cell: eight from X85 (191-198) plus twelve from X87 (221-232), as registered
    "f025": (("x85", "x87"), 0.025), "f030": (("x85", "x87"), 0.030), "f035": (("x85", "x87"), 0.035),
    "f040": (("x88",), 0.040),
}
MIN_UIDS, MIN_PAIRS = 500, 300
SHUFFLE = 1000
NULL_BAND_MAX = 0.10
RESOLUTION = 0.10
DECORATIVE = 0.05


def partial_spearman(x, y, z):
    rxy, rxz, ryz = spearman(x, y), spearman(x, z), spearman(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = (1 - rxz ** 2) * (1 - ryz ** 2)
    return round((rxy - rxz * ryz) / math.sqrt(den), 3) if den > 0 else None


def cell_stats(series: str, flow: float) -> dict:
    tags = [f"{s}_f{int(round(flow * 1000)):03d}" for s in series]
    areas, lifes, daughters, pairs_count = [], [], [], 0
    worlds = 0
    for path in sorted(p for tag in tags for p in L1.glob(f"{tag}_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        outcomes = d.get("uid_outcomes") or []
        links = d.get("uid_pairs") or []
        pairs_count += len(links)
        worlds += 1
        out_deg = {}
        for a, b in links:
            out_deg[int(a)] = out_deg.get(int(a), 0) + 1
        for o in outcomes:
            life = (o.get("last") or 0) - (o.get("first") or 0) + 1
            areas.append(float(o.get("peak") or 0))
            lifes.append(float(life))
            daughters.append(float(out_deg.get(int(o["uid"]), 0)))

    rho_life = spearman(areas, lifes)
    rho_daughters = spearman(areas, daughters)
    rho_partial = partial_spearman(areas, daughters, lifes)

    rng = random.Random(92)
    null = []
    for _ in range(SHUFFLE):
        sh = areas[:]
        rng.shuffle(sh)
        v = spearman(sh, daughters)
        if v is not None:
            null.append(abs(v))
    null.sort()
    band = round(null[int(0.95 * len(null)) - 1], 3) if null else None

    return {"flow": flow, "series": series, "worlds": worlds, "uids": len(areas), "pairs": pairs_count,
            "median_lifetime": st.median(lifes) if lifes else None,
            "median_area": st.median(areas) if areas else None,
            "rho_area_lifetime": round(rho_life, 3) if rho_life is not None else None,
            "rho_area_daughters": round(rho_daughters, 3) if rho_daughters is not None else None,
            "partial_area_daughters_given_lifetime": rho_partial,
            "null_p95_abs": band}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X92 pay")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x92_pay", "experiment": "X92",
           "command": "python scripts/x92_analyse.py --write",
           "prereg": "reports/2026-11-02-x92-pay-plan.md",
           "readout": "Spearman(area, lifetime); Spearman(area, daughters) raw and as a partial controlling lifetime; null = 1000 "
                      "within-world shuffles of area, 95th percentile of |rho|",
           "resolution": RESOLUTION, "cells": {}}
    for name, (series, flow) in CELLS.items():
        res["cells"][name] = cell_stats(series, flow)
    c = res["cells"]

    void = [k for k, v in c.items() if v["uids"] < MIN_UIDS or v["pairs"] < MIN_PAIRS]
    null_ok = all(v["null_p95_abs"] is not None and v["null_p95_abs"] < NULL_BAND_MAX for v in c.values())
    res["positive_control"] = {"fires": bool(null_ok and not void), "null_bands": {k: v["null_p95_abs"] for k, v in c.items()}}

    pays = [k for k, v in c.items()
            if (v["rho_area_lifetime"] or 0) >= RESOLUTION
            and (v["partial_area_daughters_given_lifetime"] or 0) >= RESOLUTION]
    decorative = [k for k, v in c.items()
                  if abs(v["rho_area_lifetime"] or 0) < DECORATIVE
                  and abs(v["partial_area_daughters_given_lifetime"] or 0) < DECORATIVE]

    if void or not null_ok:
        verdict = f"void: too small or null band too wide: {void or 'null band'}"
    elif len(pays) >= 3:
        verdict = "size pays: a larger structure lives longer and leaves more daughters even with lifetime held, in at least three cells"
    elif len(decorative) >= 3:
        verdict = "size is decorative: neither lifetime nor daughters depends on area beyond the null in at least three cells"
    else:
        verdict = "mixed"
    res["pay_cells"] = pays
    res["decorative_cells"] = decorative
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x92] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k} (F={v['flow']}): uids={v['uids']} pairs={v['pairs']} area~life={v['rho_area_lifetime']} "
              f"area~daughters={v['rho_area_daughters']} partial={v['partial_area_daughters_given_lifetime']} "
              f"null95={v['null_p95_abs']} med_life={v['median_lifetime']} med_area={v['median_area']}")
    print("  control:", res["positive_control"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
