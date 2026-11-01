"""x71c_analyse.py — how wide is the multistable band? Measured, not assumed from the sweep step.

Reads `x71c_f<F>_pattern_s*.json` and the fields in `_x71c_fields/` at step 24 000, applies the X71/X71b two-mode rule to
each world, and reports per inflow how many worlds are mixed. The width of the band follows from which cells are mixed.

Criteria: `reports/2026-11-01-x71c-band-width-plan.md`.

Run:
    python scripts/x71c_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x71c_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x71c_width.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile  # noqa: E402

STEP = 24000
SECOND_MODE = 0.2
COLLAPSE_SHARE = 0.6
SPLIT_BINS = 3.0
FLOWS = {"f033": 0.033, "f037": 0.037}


def classify(v: np.ndarray) -> dict:
    prof = radial_profile(v)
    if not prof:
        return {"q_peak": None, "share_peak": None, "share_second": None, "state": "empty"}
    keys = sorted(prof)
    s = np.array([prof[k] for k in keys], dtype=float)
    total = float(s.sum())
    i_peak = int(np.argmax(s))
    share_peak = float(s[i_peak] / total)
    far = np.abs(np.arange(len(s)) - i_peak) >= SPLIT_BINS
    share_second = float(s[far].max() / total) if far.any() else 0.0
    if share_peak > COLLAPSE_SHARE and share_second < SECOND_MODE:
        state = "collapsed"
    elif share_peak >= SECOND_MODE and share_second >= SECOND_MODE:
        state = "mixed"
    elif share_peak > 0.8 and share_second < 0.1:
        state = "uniform"
    else:
        state = "single"
    return {"q_peak": float(keys[i_peak]), "share_peak": round(share_peak, 3),
            "share_second": round(share_second, 3), "state": state}


def main(argv=None) -> int:
    global SECOND_MODE
    ap = argparse.ArgumentParser(description="X71c band width")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--second-mode", type=float, default=SECOND_MODE,
                    help="порог доли второй моды (чувствительность к инструменту: 0.15 / 0.20 / 0.25)")
    args = ap.parse_args(argv)
    SECOND_MODE = float(args.second_mode)

    res = {"kind": "l1_field_x71c_width", "experiment": "X71c", "second_mode_used": SECOND_MODE,
           "command": "python scripts/x71c_analyse.py --write",
           "prereg": "reports/2026-11-01-x71c-band-width-plan.md",
           "step": STEP, "second_mode": SECOND_MODE, "collapse_share": COLLAPSE_SHARE, "cells": {}}

    for flow, F in FLOWS.items():
        worlds = {}
        for path in sorted(L1.glob(f"x71c_{flow}_pattern_s*.json")):
            seed = path.stem.split("_s")[-1]
            f = FIELDS / f"{path.stem}_t{STEP}.npy"
            worlds[seed] = classify(np.load(f)) if f.is_file() else {"state": "missing"}
        states = [w.get("state") for w in worlds.values()]
        mixed = sum(1 for s in states if s == "mixed")
        bearing = sum(1 for s in states if s in ("mixed", "single", "collapsed"))
        res["cells"][flow] = {"flow": F, "worlds": worlds, "mixed": mixed, "pattern_bearing": bearing,
                              "states": states, "mixed_cell": mixed >= 4 and bearing >= 4}

    a, b = res["cells"]["f033"], res["cells"]["f037"]
    if a["pattern_bearing"] < 4 or b["pattern_bearing"] < 4:
        verdict = "insufficient: fewer than four worlds per cell are pattern-bearing"
        width = None
    elif a["mixed_cell"] and b["mixed_cell"]:
        verdict = "wide: both half-steps are mixed, so the band spans at least 0.033-0.037"
        width = ">= 0.004 (three sweep cells)"
    elif a["mixed_cell"] or b["mixed_cell"]:
        side = "0.033-0.035" if a["mixed_cell"] else "0.035-0.037"
        verdict = f"narrow: only the {side} half is mixed"
        width = "0.002 < width < 0.005"
    else:
        verdict = "one step: neither half-step is mixed, so the band stays inside 0.030-0.040"
        width = "<= 0.005"
    res["verdict"] = verdict
    res["width"] = width

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x71c] written: {OUT.name}")

    for flow, cell in res["cells"].items():
        print(f"  F={cell['flow']:.3f}: mixed={cell['mixed']}/5 bearing={cell['pattern_bearing']}/5 states={cell['states']}")
        for seed, w in cell["worlds"].items():
            print(f"      s{seed}: q={w.get('q_peak')} peak={w.get('share_peak')} second={w.get('share_second')} {w.get('state')}")
    print("  verdict:", verdict, "| width:", width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
