"""x71b_analyse.py — is the two-branch coexistence of X71 stable or a transient?

Reads `x71b_pattern_s*.json` and the fields in `_x71b_fields/` at four horizons, computes the radial spectrum per horizon,
and applies X71's rule unchanged: a world is **mixed** at a horizon if it has two modes with shares both >= 0.2 and at least
three bins apart; **collapsed** if one mode holds more than 0.6 of the power and no second mode reaches 0.2.

Criteria: `reports/2026-11-01-x71b-persistence-plan.md`.

Run:
    python scripts/x71b_analyse.py --write
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
FIELDS = L1 / "_x71b_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x71b_persistence.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile  # noqa: E402

GRID = 96
HORIZONS = (6000, 12000, 18000, 24000)
SECOND_MODE = 0.2
COLLAPSE_SHARE = 0.6
SPLIT_BINS = 3.0


def stats(v: np.ndarray) -> dict:
    prof = radial_profile(v)
    if not prof:
        return {"q_peak": None, "share_peak": None, "share_second": None, "state": "empty"}
    q = np.array([float(k) for k in sorted(prof)])
    s = np.array([prof[int(k)] for k in sorted(prof)], dtype=float)
    total = float(s.sum())
    i_peak = int(np.argmax(s))
    share_peak = float(s[i_peak] / total)
    far = np.abs(np.arange(len(s)) - i_peak) >= SPLIT_BINS
    share_second = float(s[far].max() / total) if far.any() else 0.0
    if share_peak > COLLAPSE_SHARE and share_second < SECOND_MODE:
        state = "collapsed"
    elif share_peak >= SECOND_MODE and share_second >= SECOND_MODE:
        state = "mixed"
    else:
        state = "intermediate"
    return {"q_peak": float(q[i_peak]), "share_peak": round(share_peak, 3),
            "share_second": round(share_second, 3), "state": state}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X71b persistence")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x71b_persistence", "experiment": "X71b",
           "command": "python scripts/x71b_analyse.py --write",
           "prereg": "reports/2026-11-01-x71b-persistence-plan.md",
           "horizons": list(HORIZONS), "second_mode": SECOND_MODE, "collapse_share": COLLAPSE_SHARE,
           "worlds": {}, "per_horizon": {}}

    for path in sorted(L1.glob("x71b_pattern_s*.json")):
        seed = path.stem.split("_s")[-1]
        rows = {}
        for step in HORIZONS:
            f = FIELDS / f"{path.stem}_t{step}.npy"
            if not f.is_file():
                rows[step] = {"state": "missing"}
                continue
            rows[step] = stats(np.load(f))
        res["worlds"][seed] = rows

    for step in HORIZONS:
        states = [w.get(str(step), w.get(step, {})).get("state") for w in res["worlds"].values()]
        res["per_horizon"][step] = {
            "mixed": sum(1 for s in states if s == "mixed"),
            "collapsed": sum(1 for s in states if s == "collapsed"),
            "intermediate": sum(1 for s in states if s == "intermediate"),
            "missing": sum(1 for s in states if s == "missing"),
            "states": states,
        }

    six = res["per_horizon"][6000]["mixed"]
    long_ = res["per_horizon"][24000]["mixed"]
    if six < 4:
        verdict = "uninformative: fewer than four worlds reproduce the mixed state at 6000"
    elif long_ >= 4:
        verdict = "bistable: at least four of five worlds are still mixed at 24000"
    elif res["per_horizon"][24000]["collapsed"] >= 4:
        verdict = "transient: at least four of five have collapsed to one mode by 24000"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x71b] written: {OUT.name}")

    for step in HORIZONS:
        h = res["per_horizon"][step]
        print(f"  t={step:5d}: mixed={h['mixed']} collapsed={h['collapsed']} intermediate={h['intermediate']} "
              f"missing={h['missing']}")
    for seed, rows in res["worlds"].items():
        line = "  s" + seed + ": " + " ".join(
            f"{step}:" + (rows.get(step, {}) or {}).get("state", "?")[0] for step in HORIZONS)
        print(line)
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
