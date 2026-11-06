"""Verify the headline numbers of article 032 against the committed artifacts.

Every claim in the prose is re-derived from the JSON under morphogenesis/experiments/E09_pond/,
so the text can never drift from the data.

Run:  python scripts/check_article_032_numbers.py
Exit: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")


def load(name):
    with open(os.path.join(POND, name), encoding="utf-8") as fh:
        return json.load(fh)


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def fav(doc, arm, idx, regime=None, key="favourable_share"):
    rows = [r for r in doc["rows"] if r["arm"] == arm]
    if regime is not None:
        rows = [r for r in rows if r.get("regime") == regime]
    vals = [r["windows"][idx][key] for r in rows
            if idx < len(r["windows"]) and r["windows"][idx].get(key) is not None]
    return mean(vals)


def overall(doc, arm, **match):
    rows = [r for r in doc["rows"] if r["arm"] == arm]
    for k, v in match.items():
        rows = [r for r in rows if r.get(k) == v]
    return mean([r["overall"] for r in rows])


CHECKS = []


def check(claim, fn, expected, tol):
    CHECKS.append((claim, fn, expected, tol))


# 4.1 recovery rate
check("4.1 slow control last window 0.340",
      lambda: fav(load("s19_g1_full.json"), "baseline", 5, regime="slow"), 0.340, 0.004)
check("4.1 slow greedy last window 0.166",
      lambda: fav(load("s19_g1_full.json"), "local1", 5, regime="slow"), 0.166, 0.004)
check("4.1 fast control last window 0.325",
      lambda: fav(load("s19_g1_full.json"), "baseline", 5, regime="fast"), 0.325, 0.004)
check("4.1 fast greedy last window 0.361",
      lambda: fav(load("s19_g1_full.json"), "local1", 5, regime="fast"), 0.361, 0.004)

# 4.3 fixed vs adaptive reference
check("4.3 control window 0 0.363",
      lambda: fav(load("s22_g3_full.json"), "baseline", 0), 0.363, 0.004)
check("4.3 fixed reference window 5 0.678",
      lambda: fav(load("s22_g3_full.json"), "greedy_fix", 5), 0.678, 0.004)
check("4.3 adaptive reference window 5 0.166",
      lambda: fav(load("s22_g3_full.json"), "greedy_ema", 5), 0.166, 0.004)
check("4.3 fast recovery fixed 0.675",
      lambda: fav(load("s23_g4_fast_recovery.json"), "greedy_fix", 5), 0.675, 0.004)

# 4.3 equal-budget control
check("4.3 equal budget control 0.340",
      lambda: fav(load("s25_g7_full.json"), "baseline", 5), 0.340, 0.004)
check("4.3 equal budget adaptive 0.238",
      lambda: fav(load("s25_g7_full.json"), "ema_abs", 5), 0.238, 0.004)
check("4.3 equal budget fixed 0.246",
      lambda: fav(load("s25_g7_full.json"), "fixed_abs", 5), 0.246, 0.004)

# 4.4 field designs
check("4.4 cells field 0.318",
      lambda: fav(load("s26_h2_full.json"), "field_static", 5), 0.318, 0.004)
check("4.4 external phase 0.332",
      lambda: fav(load("s27_h4_full.json"), "phase", 5), 0.332, 0.004)
check("4.4 external level 0.330",
      lambda: fav(load("s27_h4_full.json"), "level", 5), 0.330, 0.004)
check("4.4 memory field overall 0.297",
      lambda: overall(load("s34_h11_full.json"), "mem_field"), 0.297, 0.004)
check("4.4 plain smoothing overall 0.299",
      lambda: overall(load("s34_h11_full.json"), "smooth_r5"), 0.299, 0.004)
check("4.4 control overall 0.260",
      lambda: overall(load("s34_h11_full.json"), "no_field"), 0.260, 0.004)

# 4.5 displacement
check("4.5 displacement mobility 1",
      lambda: mean([r["windows"][5]["mean_displacement"] for r in load("s33_h10_full.json")["rows"]
                    if r["moves_per_step"] == 1 and len(r["windows"]) > 5]), 0.14, 0.03)
check("4.5 displacement mobility 3",
      lambda: mean([r["windows"][5]["mean_displacement"] for r in load("s33_h10_full.json")["rows"]
                    if r["moves_per_step"] == 3 and len(r["windows"]) > 5]), 0.19, 0.03)

# 4.6 memory optimum levers
check("4.6 change rate static 0.297",
      lambda: overall(load("s29_h6_full.json"), "mem_field", move_every=0) if False else
      mean([r["overall"] for r in load("s29_h6_full.json")["rows"]
            if r["lag"] == 10 and r["move_every"] == 0]), 0.297, 0.004)
check("4.6 change rate fast 0.292",
      lambda: mean([r["overall"] for r in load("s29_h6_full.json")["rows"]
                    if r["lag"] == 10 and r["move_every"] == 100]), 0.292, 0.004)
check("4.6 lifetime fast decay 0.300",
      lambda: mean([r["overall"] for r in load("s30_h7_full.json")["rows"]
                    if r["lag"] == 10 and r["decay"] == 0.15]), 0.300, 0.004)
check("4.6 distance near 0.298",
      lambda: mean([r["overall"] for r in load("s32_h9_full.json")["rows"]
                    if r["lag"] == 10 and r["separation"] == "near"]), 0.298, 0.004)
check("4.6 distance far 0.299",
      lambda: mean([r["overall"] for r in load("s32_h9_full.json")["rows"]
                    if r["lag"] == 10 and r["separation"] == "far"]), 0.299, 0.004)
check("4.6 mobility 1 best lag 10 = 0.297",
      lambda: mean([r["overall"] for r in load("s31_h8_full.json")["rows"]
                    if r["lag"] == 10 and r["moves_per_step"] == 1]), 0.297, 0.004)
check("4.6 mobility 3 best lag 40 = 0.305",
      lambda: mean([r["overall"] for r in load("s31_h8_full.json")["rows"]
                    if r["lag"] == 40 and r["moves_per_step"] == 3]), 0.305, 0.004)


def main() -> int:
    fails = 0
    for claim, fn, expected, tol in CHECKS:
        try:
            got = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {claim}: {exc}")
            fails += 1
            continue
        ok = got is not None and abs(got - expected) <= tol
        print(f"{'OK  ' if ok else 'FAIL'} {claim}: got {None if got is None else round(got, 4)}")
        if not ok:
            fails += 1
    print(f"\n{fails} failures out of {len(CHECKS)} checks")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
