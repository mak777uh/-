"""x63_analyse.py — the correlation-length profile: is there an interior maximum?

Combines the anchors already on disk (X62: scales 4, 12, 24) with the new arms (X63: 6, 8, 16, 32) and applies the
preregistered shape criterion of `reports/2026-11-01-x63-scale-sweep-plan.md`:

    resonance   => at least one of {8, 16} >= 154 divisions, both 6 and 32 < 154
    monotone    => the profile rises or falls across the whole range
    unclear     => anything else

`154` is half of the 308 measured at scale 12, chosen before the data as the "within a factor of two" bar.

Run:
    python scripts/x63_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x63_profile.json"

ANCHORS = {"s04": 4, "s12": 12, "s24": 24}       # from X62
NEW = {"s06": 6, "s08": 8, "s16": 16, "s32": 32}  # from X63
BAR = 154.0


def load(prefix: str, arm: str) -> list[float]:
    vals = []
    for f in sorted(glob.glob(str(L1 / f"{prefix}_{arm}_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        s = (d.get("selection") or {}).get("splits")
        if s is not None:
            vals.append(s)
    return vals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X63: profile")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    profile = {}
    for arm, scale in {**ANCHORS, **NEW}.items():
        prefix = "x62" if arm in ANCHORS else "x63"
        vals = load(prefix, arm)
        if vals:
            profile[scale] = {"arm": arm, "n": len(vals), "median_splits": round(st.median(vals), 1),
                              "min": min(vals), "max": max(vals)}

    if not profile:
        print("[x63] no runs")
        return 0

    scales = sorted(profile)
    med = [profile[s]["median_splits"] for s in scales]
    interior_ok = any(profile.get(s, {}).get("median_splits", 0) >= BAR for s in (8, 16))
    ends_ok = all(profile.get(s, {}).get("median_splits", 1e9) < BAR for s in (6, 32))
    monotone_rise = all(b >= a for a, b in zip(med, med[1:]))
    monotone_fall = all(b <= a for a, b in zip(med, med[1:]))
    verdict = "resonance" if (interior_ok and ends_ok) else ("monotone" if (monotone_rise or monotone_fall) else "unclear")

    out = {
        "kind": "l1_field_x63_profile",
        "experiment": "X63",
        "command": "python scripts/x63_analyse.py --write",
        "prereg": "reports/2026-11-01-x63-scale-sweep-plan.md",
        "bar": BAR,
        "profile": {str(k): v for k, v in profile.items()},
        "criterion": {"interior_at_least_bar": interior_ok, "endpoints_below_bar": ends_ok,
                      "monotone_rise": monotone_rise, "monotone_fall": monotone_fall},
        "verdict": verdict,
        "not_claimed": [
            "five seeds per scale, medians, no curve fitting",
            "the anchors 4/12/24 come from X62, the rest from X63, same parameters and seeds",
            "correlation length also changes occupied area, so the knob is not pure geometry",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x63] written: {OUT.name}")
    for s in scales:
        p = profile[s]
        print("  scale %2d  n=%d  splits=%6.1f  [%d..%d]" % (s, p["n"], p["median_splits"], p["min"], p["max"]))
    print("  interior:", interior_ok, "endpoints:", ends_ok,
          "monotone rise/fall:", monotone_rise, monotone_fall, "| verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
