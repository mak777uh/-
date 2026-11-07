"""Verify the headline numbers of article 035 against the committed artifact.

Run:  python scripts/check_article_035_numbers.py
Exit: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond", "s49_e1_density_axis.json")
# Inside the deposit package the verifier sits beside `artifacts/`, so it runs unchanged there.
if not os.path.exists(ARTIFACT):
    ARTIFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "s49_e1_density_axis.json")

CHECKS = []


def check(claim, fn, expected, tol):
    CHECKS.append((claim, fn, expected, tol))


with open(ARTIFACT, encoding="utf-8") as fh:
    D = json.load(fh)

ROWS = D["rows"]
DENS = D["densities"]
REGEN = D["regen"]


def gap(regen, dens):
    def mean(arm):
        v = [r["overall"] for r in ROWS
             if r["resource_regen"] == regen and r["density_cells"] == dens
             and r["arm"] == arm and r["overall"] is not None]
        return sum(v) / len(v) if v else None
    b, g = mean("baseline"), mean("greedy")
    return None if (b is None or g is None) else g - b


# the table in section 3
check("3 slow 3.1% -0.008", lambda: gap(0.01, 32), -0.008, 0.006)
check("3 slow 12.5% +0.032", lambda: gap(0.01, 128), 0.032, 0.006)
check("3 slow 31.3% -0.022", lambda: gap(0.01, 320), -0.022, 0.006)
check("3 slow 53.7% -0.030", lambda: gap(0.01, 550), -0.030, 0.006)
check("3 medium 3.1% +0.047", lambda: gap(0.02, 32), 0.047, 0.006)
check("3 medium 12.5% +0.063", lambda: gap(0.02, 128), 0.063, 0.006)
check("3 medium 31.3% +0.035", lambda: gap(0.02, 320), 0.035, 0.006)
check("3 medium 53.7% +0.031", lambda: gap(0.02, 550), 0.031, 0.006)
check("3 fast 3.1% +0.054", lambda: gap(0.04, 32), 0.054, 0.006)
check("3 fast 12.5% +0.076", lambda: gap(0.04, 128), 0.076, 0.006)
check("3 fast 31.3% +0.038", lambda: gap(0.04, 320), 0.038, 0.006)
check("3 fast 53.7% +0.028", lambda: gap(0.04, 550), 0.028, 0.006)

# the grid and the validity claim
check("2 four densities", lambda: len(DENS), 4, 0)
check("2 three recovery rates", lambda: len(REGEN), 3, 0)
check("2 ten seeds", lambda: D["n_seeds"], 10, 0)
check("2 240 runs", lambda: len(ROWS), 240, 0)
check("2 R1 in every run", lambda: sum(1 for r in ROWS if r["R1"]), 240, 0)

# the claim that the highest density is the worst case for movement
check("3 slow 53.7% is the worst cell", lambda: min(gap(0.01, d) for d in DENS), gap(0.01, 550), 0.002)

# the claim that the optimum is at 12.5% for every recovery rate
for reg in REGEN:
    check(f"3 optimum at 12.5% for regen {reg}",
          (lambda r=reg: max(DENS, key=lambda d: gap(r, d))), 128, 0)


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
        print(f"{'OK  ' if ok else 'FAIL'} {claim}: got {None if got is None else round(got, 5)}")
        if not ok:
            fails += 1
    print(f"\n{fails} failures out of {len(CHECKS)} checks")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
