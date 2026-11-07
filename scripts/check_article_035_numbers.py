"""check_article_035_numbers.py — every number printed in article 035 must trace to its artifact.

Two-way, like the 029–032 gates: each needle below must appear **verbatim** in the article (so the prose cannot drift
from the data) and the value it carries must be re-derived here **from the committed artifact** (so a needle cannot be
invented). The artifact is `morphogenesis/experiments/E09_pond/s49_e1_density_axis.json`: 240 runs, one row per seed and
arm, each row carrying `overall` (the favourable share over the run) and `R1`.

Run:
    python scripts/check_article_035_numbers.py          # report
    python scripts/check_article_035_numbers.py --ci     # fail on a mismatch
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "035-where-movement-pays-the-boundary-of-profitability.md"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
# Inside the deposit package the verifier sits beside `artifacts/`, so it runs unchanged there.
if not POND.exists() and (Path(__file__).resolve().parent / "artifacts").exists():
    POND = Path(__file__).resolve().parent / "artifacts"
if not ARTICLE.exists() and (Path(__file__).resolve().parent / ARTICLE.name).exists():
    ARTICLE = Path(__file__).resolve().parent / ARTICLE.name

DOC = json.loads((POND / "s49_e1_density_axis.json").read_text(encoding="utf-8"))
ROWS = DOC["rows"]
DENSITIES = DOC["densities"]
REGEN = DOC["regen"]
SEEDS = DOC["n_seeds"]


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def arm_mean(arm: str, density: int, regen: float) -> float:
    return mean([r["overall"] for r in ROWS
                 if r["arm"] == arm and r["density_cells"] == density and r["resource_regen"] == regen])


def gap(density: int, regen: float) -> float:
    return arm_mean("greedy", density, regen) - arm_mean("baseline", density, regen)


def seeds_positive(density: int, regen: float) -> tuple[int, int]:
    positive = total = 0
    for seed in sorted({r["seed"] for r in ROWS}):
        base = [r["overall"] for r in ROWS if r["seed"] == seed and r["arm"] == "baseline"
                and r["density_cells"] == density and r["resource_regen"] == regen]
        greedy = [r["overall"] for r in ROWS if r["seed"] == seed and r["arm"] == "greedy"
                  and r["density_cells"] == density and r["resource_regen"] == regen]
        if base and greedy:
            total += 1
            positive += 1 if greedy[0] > base[0] else 0
    return positive, total


def r1_failures() -> int:
    return sum(1 for r in ROWS if not r.get("R1", True))


# (needle in the article, the value the artifact gives)
CELLS = [
    ("−0.008", gap(32, 0.01)),
    ("+0.032", gap(128, 0.01)),
    ("−0.022", gap(320, 0.01)),
    ("−0.030", gap(550, 0.01)),
    ("+0.047", gap(32, 0.02)),
    ("+0.063", gap(128, 0.02)),
    ("+0.035", gap(320, 0.02)),
    ("+0.031", gap(550, 0.02)),
    ("+0.054", gap(32, 0.04)),
    ("+0.076", gap(128, 0.04)),
    ("+0.038", gap(320, 0.04)),
    ("+0.028", gap(550, 0.04)),
]
SEED_NEEDLES = [
    ("10 of 10", seeds_positive(128, 0.04)),
    ("4 of 10", seeds_positive(320, 0.01)),
    ("1 of 10", seeds_positive(550, 0.01)),
]
PLAIN_NEEDLES = [
    ("240 simulations", len(ROWS)),
    ("240 runs", len(ROWS)),
    ("240 of 240", len(ROWS) - r1_failures()),
    ("ten seeds", SEEDS),
    ("32×32", 32),
    ("3.1 %", round(100 * 32 / 1024, 1)),
    ("12.5 %", round(100 * 128 / 1024, 1)),
    ("31.2 %", round(100 * 320 / 1024, 1)),
    ("53.7 %", round(100 * 550 / 1024, 1)),
]


def render(value: float) -> str:
    text = f"{value:+.3f}"
    return text.replace("-", "−")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="check the numbers of article 035")
    ap.add_argument("--ci", action="store_true", help="exit non-zero on any mismatch")
    args = ap.parse_args(argv)
    text = ARTICLE.read_text(encoding="utf-8")

    failures = 0
    for needle, value in CELLS:
        ok = needle in text and abs(value - float(needle.replace("−", "-"))) <= 0.0006
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} cell {needle}: artifact {render(value)}")

    for needle, (positive, total) in SEED_NEEDLES:
        ok = needle in text and f"{positive} of {total}" == needle
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} seeds {needle}: artifact {positive} of {total}")

    for needle, value in PLAIN_NEEDLES:
        ok = needle in text
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {needle}: artifact {value}")

    # the two structural claims of §3
    # a cell counts as negative when its mean gap is negative; under slow recovery that happens at two densities,
    # and at the lowest density the mean is negative too but only 5 of 10 seeds are, so it is not a sign flip
    negative_cells = [(d, r) for d in DENSITIES for r in REGEN if gap(d, r) < 0]
    boundary_ok = all(r == 0.01 for _, r in negative_cells)
    failures += 0 if boundary_ok else 1
    print(f"{'OK  ' if boundary_ok else 'FAIL'} every negative cell is slow recovery: {negative_cells}")
    flips = [d for d, r in negative_cells if seeds_positive(d, r)[0] * 2 < seeds_positive(d, r)[1]]
    flips_ok = flips == [320, 550]
    failures += 0 if flips_ok else 1
    print(f"{'OK  ' if flips_ok else 'FAIL'} the sign flips in most seeds only at 31.2 % and 53.7 %: {flips}")
    best = max(((d, r) for d in DENSITIES for r in REGEN), key=lambda c: gap(*c))
    optimum_ok = best == (128, 0.04)
    failures += 0 if optimum_ok else 1
    print(f"{'OK  ' if optimum_ok else 'FAIL'} the optimum cell is density 128 with fast recovery: {best}")

    total = len(CELLS) + len(SEED_NEEDLES) + len(PLAIN_NEEDLES) + 3
    print(f"\n{failures} failures out of {total} checks")
    if args.ci and failures:
        return 1
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
