"""x90_analyse.py — does the lineage trickle stop, or does it only slow down?

Criteria: `reports/2026-11-02-x90-trickle-plan.md`. Compares lag-1 pairs per world at a 12 000-step horizon against the 6000-step
values measured by X88 (0.050: 6 pairs over 20 worlds) and X89 (0.048: 2.0 per world, 0.049: 1.0 per world).

Run:
    python scripts/x90_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x90_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x90_trickle.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import beta0, drop_small, euler  # noqa: E402

THRESHOLD, MIN_CELLS = 0.2, 5
FLOWS = {"f048": 0.048, "f049": 0.049, "f050": 0.050}
SIX_THOUSAND = {"f048": 2.0, "f049": 1.0, "f050": 0.3}   # pairs per world, X88/X89
CONTINUES = 1.5
STOPPED = 1.2


def cell_stats(flow: str) -> dict:
    pairs, comps, betas, share_one = [], [], [], []
    for path in sorted(L1.glob(f"x90_{flow}_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        pairs.append(len(d.get("uid_pairs") or []))
        series = d.get("series") or []
        c = [s.get("components") or 0 for s in series]
        comps.append(st.mean(c) if c else None)
        f = FIELDS / f"{path.stem}_t12000.npy"
        if f.is_file():
            mask = drop_small(np.load(f) > THRESHOLD, MIN_CELLS)
            b0 = beta0(mask)
            betas.append(int(round(b0 - euler(mask))))
            share_one.append(1.0 if b0 == 1 else 0.0)
    return {"flow": FLOWS[flow], "worlds": len(pairs),
            "pairs_median": st.median(pairs) if pairs else None,
            "pairs_mean": round(st.mean(pairs), 2) if pairs else None,
            "pairs_range": [min(pairs), max(pairs)] if pairs else None,
            "pairs_per_world": pairs,
            "components_median": round(st.median([c for c in comps if c is not None]), 1) if any(c is not None for c in comps) else None,
            "single_component_share": round(sum(share_one) / len(share_one), 2) if share_one else None,
            "b1_positive_worlds": sum(1 for b in betas if b > 0) if betas else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X90 trickle")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x90_trickle", "experiment": "X90",
           "command": "python scripts/x90_analyse.py --write",
           "prereg": "reports/2026-11-02-x90-trickle-plan.md",
           "horizon": 12000, "reference_6000": SIX_THOUSAND,
           "thresholds": {"continues": CONTINUES, "stopped": STOPPED},
           "cells": {}}
    for flow in FLOWS:
        res["cells"][flow] = cell_stats(flow)

    c = res["cells"]
    ratios = {}
    for flow, x in c.items():
        base = SIX_THOUSAND[flow]
        ratios[flow] = round(x["pairs_median"] / base, 2) if x["pairs_median"] is not None and base else None
    res["ratio_vs_6000"] = ratios

    void = [k for k, x in c.items() if x["pairs_median"] is None]
    control = c["f050"]["pairs_median"] is not None and c["f050"]["pairs_median"] >= 1
    res["positive_control"] = {"fires": bool(control), "f050_median_pairs": c["f050"]["pairs_median"]}

    if void:
        verdict = f"void: unreadable cells: {void}"
    elif not control:
        verdict = "void: the 0.050 cell still carries fewer than one event per world at double the horizon, so the horizon is too short to compare"
    elif sum(1 for r in ratios.values() if r is not None and r >= CONTINUES) >= 2:
        verdict = "the trickle continues: doubling the horizon raises the lineage count by at least 1.5x in two cells, so reproduction is rare but real"
    elif all(r is not None and r <= STOPPED for r in ratios.values()):
        verdict = "reproduction has stopped: doubling the horizon leaves the count unchanged, so the remaining events are transient"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x90] written: {OUT.name}")

    for k, x in c.items():
        print(f"  {k}: pairs median={x['pairs_median']} mean={x['pairs_mean']} {x['pairs_range']} ratio={ratios[k]} "
              f"comp={x['components_median']} single={x['single_component_share']} b1+={x['b1_positive_worlds']}/{x['worlds']}")
    print("  control:", res["positive_control"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
