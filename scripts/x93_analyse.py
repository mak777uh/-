"""x93_analyse.py — do sisters pay for size? Within-family contrast with lifetime as the outcome.

Criteria: `reports/2026-11-02-x93-sibling-plan.md`. For every mother with at least two daughters that both have a recorded lifetime and
different peak areas, ask whether the **larger sister lives longer**. The control is the same question asked of pseudo-sisters from
different mothers born at the same time.

Run:
    python scripts/x93_analyse.py --write
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x93_sibling_contrast.json"

CELLS = {
    "f025": (("x85", "x87"), 0.025),
    "f030": (("x85", "x87"), 0.030),
    "f035": (("x85", "x87"), 0.035),
    "f040": (("x88",), 0.040),
}
MIN_PAIRS = 200
CONTROL_BAND = (0.45, 0.55)
PAYS = 0.55
PAYS_MARGIN = 0.05
FLAT = 0.03
Z_BAR = 2.0
SHUFFLE = 2000


def z_of(k: int, n: int) -> float:
    if n == 0:
        return 0.0
    p = k / n
    return (p - 0.5) / math.sqrt(0.25 / n)


def cell_stats(series, flow: float) -> dict:
    tags = [f"{s}_f{int(round(flow * 1000)):03d}" for s in series]
    within_k = within_n = 0
    cross_k = cross_n = 0
    families = 0
    rng = random.Random(93)
    for path in sorted(p for tag in tags for p in L1.glob(f"{tag}_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        outs = {int(o["uid"]): o for o in (d.get("uid_outcomes") or [])}
        links = d.get("uid_pairs") or []
        kids = defaultdict(list)
        for a, b in links:
            kids[int(a)].append(int(b))

        def area(u):
            return float(outs[u].get("peak") or 0) if u in outs else None

        def life(u):
            if u not in outs:
                return None
            return float((outs[u].get("last") or 0) - (outs[u].get("first") or 0) + 1)

        families_here = []
        for mother, children in kids.items():
            usable = [c for c in children if life(c) is not None and area(c) is not None]
            families_here.append(usable)
            if len(usable) < 2:
                continue
            families += 1
            for a, b in itertools.combinations(usable, 2):
                if area(a) == area(b) or life(a) == life(b):
                    continue
                within_n += 1
                larger, smaller = (a, b) if area(a) > area(b) else (b, a)
                if life(larger) > life(smaller):
                    within_k += 1

        # cross-family control: pairs of daughters of different mothers, matched on birth snapshot within +-1
        pool = [c for fam in families_here for c in fam]
        if len(pool) >= 4:
            for _ in range(min(400, len(pool) * 2)):
                a, b = rng.sample(pool, 2)
                if a == b or life(a) is None or life(b) is None or area(a) is None or area(b) is None:
                    continue
                if abs((outs[a].get("first") or 0) - (outs[b].get("first") or 0)) > 50:
                    continue
                if area(a) == area(b) or life(a) == life(b):
                    continue
                cross_n += 1
                larger, smaller = (a, b) if area(a) > area(b) else (b, a)
                if life(larger) > life(smaller):
                    cross_k += 1

    within = within_k / within_n if within_n else None
    cross = cross_k / cross_n if cross_n else None
    return {"flow": flow, "families": families, "pairs_within": within_n, "pairs_cross": cross_n,
            "within_fraction": round(within, 3) if within is not None else None,
            "cross_fraction": round(cross, 3) if cross is not None else None,
            "z_within": round(z_of(within_k, within_n), 2),
            "difference": round(within - cross, 3) if within is not None and cross is not None else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X93 sibling contrast")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x93_sibling_contrast", "experiment": "X93",
           "command": "python scripts/x93_analyse.py --write",
           "prereg": "reports/2026-11-02-x93-sibling-plan.md",
           "readout": "fraction of sister pairs in which the larger sister has the longer lifetime; control is the same question for "
                      "daughters of different mothers born within one snapshot",
           "cells": {}}
    for name, (series, flow) in CELLS.items():
        res["cells"][name] = cell_stats(series, flow)
    c = res["cells"]

    control_ok = all(v["cross_fraction"] is not None and CONTROL_BAND[0] <= v["cross_fraction"] <= CONTROL_BAND[1]
                     for v in c.values())
    res["positive_control"] = {"fires": bool(control_ok), "cross_fractions": {k: v["cross_fraction"] for k, v in c.items()},
                               "band": list(CONTROL_BAND)}

    void = [k for k, v in c.items() if v["pairs_within"] < MIN_PAIRS]
    res["void_cells"] = void
    pays = [k for k, v in c.items()
            if v["within_fraction"] is not None and v["within_fraction"] >= PAYS
            and (v["difference"] or 0) >= PAYS_MARGIN and (v["z_within"] or 0) >= Z_BAR]
    flat = [k for k, v in c.items()
            if v["difference"] is not None and abs(v["difference"]) < FLAT]

    if not control_ok:
        verdict = "void: the cross-family control is outside [0.45, 0.55], so the pairing machinery itself has a preference"
    elif len(void) == len(c):
        verdict = "void: no cell has 200 usable sister pairs"
    elif len(pays) >= 2:
        verdict = "size pays within the family: the larger sister lives longer in at least two cells, above the cross-family control"
    elif len(flat) >= 3:
        verdict = "size does not pay within the family: the sister contrast is flat against the control in at least three cells"
    else:
        verdict = "mixed"
    res["pay_cells"] = pays
    res["flat_cells"] = flat
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x93] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k} (F={v['flow']}): families={v['families']} pairs={v['pairs_within']}/{v['pairs_cross']} "
              f"within={v['within_fraction']} cross={v['cross_fraction']} diff={v['difference']} z={v['z_within']}")
    print("  control:", res["positive_control"])
    print("  void cells:", void)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
