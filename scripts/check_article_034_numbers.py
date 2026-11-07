"""Verify the headline numbers of article 034 against the committed artifact.

Run:  python scripts/check_article_034_numbers.py
Exit: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond", "s89_e14b_20seeds.json")
# Inside the deposit package the verifier sits beside `artifacts/`, so it runs unchanged there.
if not os.path.exists(ARTIFACT):
    ARTIFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "s89_e14b_20seeds.json")

with open(ARTIFACT, encoding="utf-8") as fh:
    D = json.load(fh)

ROWS = D["rows"]
ARMS = ["none", "local", "wave", "rule", "ab"]

CHECKS = []


def check(claim, fn, expected, tol):
    CHECKS.append((claim, fn, expected, tol))


def last_window(arm):
    vals = [r["windows"][-1]["trait_mean"] for r in ROWS if r["arm"] == arm and r["windows"]]
    return sum(vals) / len(vals) if vals else None


def paired(arm):
    base = {r["seed"]: r["windows"][-1]["trait_mean"] for r in ROWS
            if r["arm"] == "none" and r["windows"]}
    diffs = [r["windows"][-1]["trait_mean"] - base[r["seed"]] for r in ROWS
             if r["arm"] == arm and r["windows"] and r["seed"] in base]
    if not diffs:
        return None, None
    return sum(diffs) / len(diffs), sum(1 for d in diffs if d > 0)


# section 2 table
check("2 none 0.093", lambda: last_window("none"), 0.093, 0.004)
check("2 local 0.105", lambda: last_window("local"), 0.105, 0.004)
check("2 wave 0.101", lambda: last_window("wave"), 0.101, 0.004)
check("2 rule 0.145", lambda: last_window("rule"), 0.145, 0.004)
check("2 ab 0.111", lambda: last_window("ab"), 0.111, 0.004)

check("2 local paired +0.0117", lambda: paired("local")[0], 0.0117, 0.003)
check("2 wave paired +0.0080", lambda: paired("wave")[0], 0.0080, 0.003)
check("2 rule paired +0.0512", lambda: paired("rule")[0], 0.0512, 0.003)
check("2 ab paired +0.0172", lambda: paired("ab")[0], 0.0172, 0.003)

check("2 local 14/20 positive", lambda: paired("local")[1], 14, 0)
check("2 wave 11/20 positive", lambda: paired("wave")[1], 11, 0)
check("2 rule 18/20 positive", lambda: paired("rule")[1], 18, 0)
check("2 ab 15/20 positive", lambda: paired("ab")[1], 15, 0)

# design claims
check("1 twenty seeds", lambda: D["n_seeds"], 20, 0)
check("1 100 rows", lambda: len(ROWS), 100, 0)
check("1 R1 in every run", lambda: sum(1 for r in ROWS if r["R1"]), 100, 0)
check("1 equal dose: min", lambda: min(r["total_added"] for r in ROWS), 57.6, 0.3)
check("1 equal dose: max", lambda: max(r["total_added"] for r in ROWS), 57.8, 0.3)
check("1 planted at the poor centre", lambda: D["plant_xy"], [16, 16], 0)

# the headline ratio: rule is about four times local
check("2 rule is ~4x local", lambda: paired("rule")[0] / paired("local")[0], 4.0, 1.0)


def main() -> int:
    fails = 0
    for claim, fn, expected, tol in CHECKS:
        try:
            got = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {claim}: {exc}")
            fails += 1
            continue
        if isinstance(expected, list):
            ok = got == expected
        else:
            ok = got is not None and abs(got - expected) <= tol
        print(f"{'OK  ' if ok else 'FAIL'} {claim}: got {got if isinstance(got, list) else (None if got is None else round(got, 5))}")
        if not ok:
            fails += 1
    print(f"\n{fails} failures out of {len(CHECKS)} checks")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
