"""x151_analyse.py — X151: is the stop of the boundary a threshold or a plateau?

Radius 5.25 (disc area ~87 cells) at surface gaps 7 and 8, five seeds each, read with the same tolerance-free
classification as the rest of the block. The comparison rows (radius 3, 4.5, 6) are read from the committed X150
aggregate so that the whole ladder is assembled in one place.

Plan: reports/2026-11-03-x151-radius525-plan.md.

    python scripts/x151_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import x142_analyse as A  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x151_radius525.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
X150 = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x150_radius6.json"

ARMS = {"r525_g7": ("x151_g7_r525", 5.25, 7), "r525_g8": ("x151_g8_r525", 5.25, 8)}
SEEDS = (601, 602, 603, 604, 605)
EXPECTED_TIME = {7: 39, 8: 49}


def summarise(rows: list[dict]) -> dict:
    usable = [r for r in rows if r.get("usable")]
    counts = {c: len([r for r in usable if r["class"] == c]) for c in ("M", "A", "P")}
    times = [r["t_dissolve"] for r in usable if r["class"] == "M" and r["t_dissolve"] is not None]
    return {
        "runs": len(usable), "M": counts["M"], "A": counts["A"], "P": counts["P"],
        "median_t_coalescence": round(st.median(times), 1) if times else None,
        "n_timed": len(times),
        "seeds": {str(r["seed"]): {"class": r["class"], "t_dissolve": r["t_dissolve"],
                                   "daughters": r["daughters"], "live": r["live"]}
                  for r in sorted(usable, key=lambda r: r["seed"])},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X151 radius 5.25")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    raw, by_arm, bad = {}, {}, []
    for key, (stem, _r, _g) in ARMS.items():
        rows = []
        for seed in SEEDS:
            p = L1 / f"{stem}_s{seed}.json"
            if p.exists():
                rows.append(A.world_row(p))
        raw[key] = rows
        by_arm[key] = summarise(rows)

    for key in ARMS:
        if by_arm[key]["runs"] != 5:
            bad.append(f"control: {key} has {by_arm[key]['runs']} usable runs, expected 5")
    for key, rows in raw.items():
        for r in rows:
            if not r.get("usable"):
                bad.append(f"control: {key} {r['world']} does not start as two components")
            if r["empty"]:
                bad.append(f"control: {key} {r['world']} ends empty")

    # Control 1: the timing law, in whichever arm coalesces in every seed.
    timing = {}
    for key, (stem, _r, gap) in ((k, ARMS[k]) for k in ARMS):
        arm = by_arm[key]
        if arm["M"] != arm["runs"] or arm["median_t_coalescence"] is None:
            continue
        want = EXPECTED_TIME[gap]
        timing[f"r525_g{gap}"] = {"observed": arm["median_t_coalescence"], "expected": want}
        if arm["median_t_coalescence"] != want:
            bad.append(f"control: r525 gap {gap} coalesces at {arm['median_t_coalescence']} steps, the law says {want}")

    ladder = {}
    if X150.exists():
        ladder = {rk: v for rk, v in json.loads(X150.read_text(encoding="utf-8"))["boundary"].items()}

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        g7, g8 = by_arm["r525_g7"], by_arm["r525_g8"]
        if g8["M"] == 5 and g7["M"] == 5:
            verdict = ("THRESHOLD, CROSSED BEFORE 64 CELLS: radius 5.25 coalesces in 5/5 seeds at a gap of 8 cells, as "
                       "radius 3 does, while radius 4.5 and 6 break there - so the boundary is already back out at 87 "
                       "cells and the inward move of X147 is confined to a band of sizes, not a plateau")
        elif g8["M"] <= 3 and g7["M"] == 5:
            verdict = ("THE CREEP CONTINUES: radius 5.25 breaks at a gap of 8 (M "
                       f"{g8['M']}/5) and holds 5/5 at 7, so the boundary is still moving at 87 cells and the agreement "
                       "of radius 4.5 and 6 at gap 7 is not a plateau - the next run is the same radius at gap 7 with "
                       "sub-cell gaps")
        elif g8["M"] == 5 and g7["M"] < 5:
            verdict = ("NOT MONOTONE IN THE RADIUS: radius 5.25 is 5/5 at gap 8 and mixed at gap 7, so the boundary went "
                       "out and back between radius 4.5, 5.25 and 6 - the arms are not measuring one quantity and the "
                       "block stops to re-examine the readout before any further radius")
        else:
            verdict = (f"INDETERMINATE: radius 5.25 gives M {g7['M']}/5 at gap 7 and M {g8['M']}/5 at gap 8 - one seed "
                       f"separates the arms; the next run doubles the seeds at gaps 7 and 8 rather than adding a radius")
        ladder["r525"] = {"radius": 5.25,
                          "gaps_measured": [7, 8],
                          "largest_gap_all_coalesce": 7 if g7["M"] == 5 and g8["M"] < 5 else (8 if g8["M"] == 5 else None)}

    res = {
        "kind": "l1_field_x151_radius525",
        "experiment": "X151",
        "command": "python scripts/x151_analyse.py --write",
        "prereg": "reports/2026-11-03-x151-radius525-plan.md",
        "definitions": {
            "unit": "the arm (one radius, one surface gap); counts are out of the usable seeds",
            "gap": "SEP - 2R in cells",
            "boundary": "the largest surface gap measured at which every seed of the arm coalesces",
            "readout": "x142_analyse.world_row - the same code, no distance tolerance",
        },
        "by_arm": by_arm,
        "ladder": ladder,
        "timing_control": timing,
        "controls": {"failures": bad},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x151] written: {OUT.name}")
    for key in ARMS:
        a = by_arm[key]
        print(f"  {key:8s} M {a['M']}/{a['runs']}  A {a['A']}  P {a['P']}  "
              f"median t {a['median_t_coalescence']} (n {a['n_timed']})")
    for rk, b in ladder.items():
        print(f"  boundary {rk}: radius {b['radius']}, largest gap with 5/5 = {b['largest_gap_all_coalesce']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
