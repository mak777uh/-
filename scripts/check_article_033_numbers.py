"""Verify the headline numbers of article 033 v3.0 against the committed artifacts.

Run:  python scripts/check_article_033_numbers.py
Exit: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")

CHECKS = []


def check(claim, fn, expected, tol):
    CHECKS.append((claim, fn, expected, tol))


def load(name):
    with open(os.path.join(POND, name), encoding="utf-8") as fh:
        return json.load(fh)


# ---- section 2: the selection table
D7 = load("s55_e7_full.json")
D7R = load("s58_e7_replication.json")


def diff(doc, key, target):
    cell = (doc.get("table") or {}).get(key, {}).get(target)
    return cell["diff"] if cell else None


check("2 E7 energy survive +0.135", lambda: diff(D7, "energy", "survive"), 0.135, 0.006)
check("2 E7 energy divide -0.434", lambda: diff(D7, "energy", "divide"), -0.434, 0.006)
check("2 E7 age survive +0.106", lambda: diff(D7, "age", "survive"), 0.106, 0.006)
check("2 E7 age divide -0.306", lambda: diff(D7, "age", "divide"), -0.306, 0.006)
check("2 E7 density survive +0.104", lambda: diff(D7, "density", "survive"), 0.104, 0.006)
check("2 E7 density divide -0.131", lambda: diff(D7, "density", "divide"), -0.131, 0.006)
check("2 E7 rich survive +0.041", lambda: diff(D7, "rich", "survive"), 0.041, 0.006)
check("2 E7 rich divide -0.128", lambda: diff(D7, "rich", "divide"), -0.128, 0.006)

check("2 E7r energy survive +0.154", lambda: diff(D7R, "energy", "survive"), 0.154, 0.006)
check("2 E7r age survive +0.113", lambda: diff(D7R, "age", "survive"), 0.113, 0.006)
check("2 E7r density divide -0.087", lambda: diff(D7R, "density", "divide"), -0.087, 0.006)

# ---- section 3: the cost axis
D15 = load("s91_e15_full.json")
ROWS = D15["rows"]


def paired(zone, strength):
    base = {r["seed"]: r["windows"][-1]["trait_mean"] for r in ROWS
            if r["zone_name"] == zone and r["rule_strength"] == strength
            and r["arm"] == "fixed" and r["windows"]}
    her = {r["seed"]: r["windows"][-1]["trait_mean"] for r in ROWS
           if r["zone_name"] == zone and r["rule_strength"] == strength
           and r["arm"] == "heritable" and r["windows"]}
    diffs = [her[k] - base[k] for k in sorted(base) if k in her]
    if not diffs:
        return None, None, None
    m = sum(diffs) / len(diffs)
    sd = (sum((x - m) ** 2 for x in diffs) / max(1, len(diffs) - 1)) ** 0.5
    t = m / (sd / len(diffs) ** 0.5) if sd else 0.0
    return m, t, sum(1 for x in diffs if x > 0)


check("3 rich strength 0.0 mean", lambda: paired("rich", 0.0)[0], -0.00002, 0.0005)
check("3 rich strength 0.0 |t|<1", lambda: abs(paired("rich", 0.0)[1]), 0.01, 1.0)
check("3 poor strength 0.0 mean", lambda: paired("poor", 0.0)[0], -0.0016, 0.0005)
check("3 poor strength 0.0 |t|<1", lambda: abs(paired("poor", 0.0)[1]), 0.72, 1.0)
check("3 rich strength 0.06 mean", lambda: paired("rich", 0.06)[0], -0.048, 0.004)
check("3 rich strength 0.06 t", lambda: paired("rich", 0.06)[1], -1.83, 0.08)
check("3 rich strength 0.6 mean", lambda: paired("rich", 0.6)[0], -0.013, 0.004)
check("3 poor strength 0.06 mean", lambda: paired("poor", 0.06)[0], 0.016, 0.004)
check("3 poor strength 0.06 t", lambda: paired("poor", 0.06)[1], 0.85, 0.08)
check("3 poor strength 0.6 mean", lambda: paired("poor", 0.6)[0], -0.010, 0.004)

# the claim that all nonzero strengths are non-significant on five seeds
check("3 all nonzero |t| < 2", lambda: max(abs(paired(z, s)[1]) for z in ("rich", "poor")
                                           for s in (0.06, 0.6)) < 2.0, True, 0)
# the claim that the effect is smaller at 0.6 than at 0.06 in the rich zone
check("3 rich 0.6 weaker than 0.06",
      lambda: abs(paired("rich", 0.6)[0]) < abs(paired("rich", 0.06)[0]), True, 0)
# the claim that the poor zone at 0.06 rises rather than falls
check("3 poor 0.06 rises", lambda: paired("poor", 0.06)[0] > 0, True, 0)

# ---- design claims
check("3 five seeds", lambda: D15["n_seeds"], 5, 0)
check("3 three strengths", lambda: len(D15["strengths"]), 3, 0)
check("3 two zones", lambda: len(D15["zones"]), 2, 0)
check("3 60 rows", lambda: len(ROWS), 60, 0)
check("3 R1 in every run", lambda: sum(1 for r in ROWS if r["R1"]), 60, 0)
check("3 planting recorded", lambda: all("zone" in r and r["zone"].get("class") for r in ROWS), True, 0)


def main() -> int:
    fails = 0
    for claim, fn, expected, tol in CHECKS:
        try:
            got = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {claim}: {exc}")
            fails += 1
            continue
        if isinstance(expected, bool):
            ok = got is expected
        else:
            ok = got is not None and abs(got - expected) <= tol
        shown = got if isinstance(got, (bool, int)) else (None if got is None else round(got, 6))
        print(f"{'OK  ' if ok else 'FAIL'} {claim}: got {shown}")
        if not ok:
            fails += 1
    print(f"\n{fails} failures out of {len(CHECKS)} checks")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
