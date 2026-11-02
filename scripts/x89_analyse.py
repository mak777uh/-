"""x89_analyse.py — where do the lineages vanish between F = 0.045 and 0.050?

Criteria: `reports/2026-11-02-x89-lineage-edge-plan.md`. Primary readout: ancestor-descendant pairs per world (the quantity that goes
to zero). Regime: fraction of worlds with a single component, and beta1 from the field.

Run:
    python scripts/x89_analyse.py --write
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
FIELDS = L1 / "_x89_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x89_lineage_edge.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import beta0, drop_small, euler  # noqa: E402

THRESHOLD, MIN_CELLS = 0.2, 5
FLOWS = {"f046": 0.046, "f047": 0.047, "f048": 0.048, "f049": 0.049}
REF = {"0.045": 636, "0.050": 6}   # X88, twenty worlds each
RESOLUTION_FACTOR = 5.0
SHARP_FACTOR = 10.0


def cell_stats(flow: str) -> dict:
    pairs, comps, betas, share_one = [], [], [], []
    for path in sorted(L1.glob(f"x89_{flow}_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        series = d.get("series") or []
        n_pairs = len(d.get("uid_pairs") or [])
        pairs.append(n_pairs)
        c = [s.get("components") or 0 for s in series]
        comps.append(st.mean(c) if c else None)
        f = FIELDS / f"{path.stem}_t6000.npy"
        if f.is_file():
            mask = drop_small(np.load(f) > THRESHOLD, MIN_CELLS)
            b0 = beta0(mask)
            betas.append(int(round(b0 - euler(mask))))
            share_one.append(1.0 if b0 == 1 else 0.0)
    out = {"flow": FLOWS[flow], "worlds": len(pairs),
           "pairs_median": st.median(pairs) if pairs else None,
           "pairs_range": [min(pairs), max(pairs)] if pairs else None,
           "pairs_per_world": pairs,
           "components_median": round(st.median([c for c in comps if c is not None]), 1) if any(c is not None for c in comps) else None,
           "single_component_share": round(sum(share_one) / len(share_one), 2) if share_one else None,
           "b1_positive_worlds": sum(1 for b in betas if b > 0) if betas else None}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X89 lineage edge")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x89_lineage_edge", "experiment": "X89",
           "command": "python scripts/x89_analyse.py --write",
           "prereg": "reports/2026-11-02-x89-lineage-edge-plan.md",
           "endpoints_from_x88": REF, "cells": {}}
    for flow in FLOWS:
        res["cells"][flow] = cell_stats(flow)
    c = res["cells"]

    chain = [("0.045", REF["0.045"] / 20)] + [(f"{v['flow']:.3f}", v["pairs_median"]) for v in c.values()] + \
            [("0.050", REF["0.050"] / 20)]
    res["chain_pairs_per_world"] = [[k, round(v, 1) if v is not None else None] for k, v in chain]

    void = [k for k, v in c.items() if v["pairs_median"] is None]
    control = c["f046"]["pairs_median"] is not None and c["f046"]["pairs_median"] >= 10
    monotone = all(chain[i][1] is not None and chain[i + 1][1] is not None and chain[i + 1][1] <= chain[i][1] + 1e-9
                   for i in range(len(chain) - 1))
    steps = []
    for i in range(len(chain) - 1):
        a, b = chain[i][1], chain[i + 1][1]
        if a is None or b is None:
            steps.append([f"{chain[i][0]}->{chain[i+1][0]}", None])
            continue
        steps.append([f"{chain[i][0]}->{chain[i+1][0]}", round(a / b, 1) if b else None])
    res["steps_factor"] = steps
    sharp = any(v is not None and v >= SHARP_FACTOR for _, v in steps)

    if void:
        verdict = f"void: unreadable cells: {void}"
    elif not control:
        verdict = "void: the 0.046 cell has fewer than 10 pairs per world — the edge lies below 0.045 and the series missed it"
    elif sharp:
        verdict = "sharp boundary: one half-step drops the lineage count by at least 10x, so the medium stops dividing over a narrow inflow interval"
    elif monotone:
        verdict = "graded disappearance: the lineage count falls monotonically across the half-steps without a single 10x step"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x89] written: {OUT.name}")

    print("  chain (F -> pairs per world):", res["chain_pairs_per_world"])
    for k, v in c.items():
        print(f"  {k}: pairs median={v['pairs_median']} {v['pairs_range']} comp={v['components_median']} "
              f"single={v['single_component_share']} b1+={v['b1_positive_worlds']}/{v['worlds']}")
    print("  steps:", steps)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
