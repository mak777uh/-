"""x154_analyse.py — X154: is the width in the time measurable, or is it noise of ten seeds?

Four arms of one radius (6.0), ten seeds each, all read through `x142_analyse.world_row`:
gap 6.5 (x154, 601-610), 7.0 (x150 601-605 + x154 606-610), 7.5 (x153, 601-610), 8.0 (x150 601-605 + x154 606-610).

The registered decision rule is in reports/2026-11-03-x154-mixing-curve-plan.md §4-5: a monotone rise of at least 0.3 in
the fraction of slow coalescences between the first and the last arm means a real width; unordered or smaller means ten-seed
noise; a flat curve that jumps to 1.0 at gap 8 means the time has the same whole-cell threshold as the outcome.

    python scripts/x154_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x154_mixing.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

# arm: list of (stem, seeds)
ARMS = [
    (6.5, 18.5, [("x154_g65_r60", tuple(range(601, 611)))]),
    (7.0, 19.0, [("x150_g7_r60", tuple(range(601, 606))), ("x154_g70_r60", tuple(range(606, 611)))]),
    (7.5, 19.5, [("x153_g75_r60", tuple(range(601, 611)))]),
    (8.0, 20.0, [("x150_g8_r60", tuple(range(601, 606))), ("x154_g80_r60", tuple(range(606, 611)))]),
]


def step1(path: Path) -> dict | None:
    if not path.exists():
        return None
    w = json.loads(path.read_text(encoding="utf-8"))
    s = (w.get("series") or [{}])[0]
    return {"areas": s.get("areas"), "components": s.get("components"), "occupied": s.get("occupied")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X154 mixing curve")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    curve, problems = [], []
    for gap, sep, sources in ARMS:
        rows = []
        for stem, seeds in sources:
            for seed in seeds:
                p = L1 / f"{stem}_s{seed}.json"
                if not p.exists():
                    problems.append(f"missing artifact {p.name} (gap {gap})")
                    continue
                r = A.world_row(p)
                r["source"] = stem
                rows.append(r)
        usable = [r for r in rows if r.get("usable")]
        coalescing = [r for r in usable if r["class"] == "M"]
        times = [r["t_dissolve"] for r in coalescing if r["t_dissolve"] is not None]
        slow = [t for t in times if t >= 49]
        areas = [step1(L1 / f"{r['source']}_s{r['seed']}.json") for r in usable]
        areas = [a for a in areas if a and a.get("areas")]
        per_disc = sorted({x for a in areas for x in a["areas"]})
        if len(usable) != 10:
            problems.append(f"gap {gap}: {len(usable)} usable runs, expected 10")
        off_grid = [t for t in times if t % 10 != 0]
        if off_grid:
            problems.append(f"gap {gap}: dissolution times off the 10-step logging grid: {off_grid}")
        for r in usable:
            if r["empty"]:
                problems.append(f"gap {gap}: {r['world']} ends empty")
        curve.append({
            "gap": gap, "separation": sep, "runs": len(usable),
            "M": len(coalescing), "A": len([r for r in usable if r["class"] == "A"]),
            "P": len([r for r in usable if r["class"] == "P"]),
            "coalescing_fraction": round(len(coalescing) / max(1, len(usable)), 2),
            "time_histogram": {str(t): times.count(t) for t in sorted(set(times))},
            "median_t": round(st.median(times), 1) if times else None,
            "slow": len(slow),
            "slow_fraction": round(len(slow) / max(1, len(times)), 2) if times else None,
            "slow_fraction_of_all": round(len(slow) / max(1, len(usable)), 2),
            "rasterised_area_per_disc": per_disc,
            "seeds": {str(r["seed"]): {"class": r["class"], "t_dissolve": r["t_dissolve"],
                                       "source": r["source"]} for r in sorted(usable, key=lambda r: r["seed"])},
        })

    by_gap = {c["gap"]: c for c in curve}
    slow_seq = [by_gap[g]["slow_fraction"] for g in (6.5, 7.0, 7.5, 8.0)]
    co_seq = [by_gap[g]["coalescing_fraction"] for g in (6.5, 7.0, 7.5, 8.0)]

    if problems:
        verdict = "void: " + "; ".join(problems)
    else:
        rise = (slow_seq[-1] or 0) - (slow_seq[0] or 0)
        monotone = all(slow_seq[i + 1] >= slow_seq[i] - 0.1 for i in range(3))
        interior = [s for s in slow_seq if 0 < (s or 0) < 1]
        if not monotone:
            verdict = (f"TEN-SEED NOISE: the slow fraction does not order monotonically ({slow_seq} at gaps 6.5-8.0), so "
                       f"X153's two slow seeds were the tail of a split rather than a width; the block stops quoting a "
                       f"'mix'")
        elif rise >= 0.3 and interior:
            verdict = (f"REAL WIDTH: the slow fraction rises from {slow_seq[0]} at a gap of 6.5 to {slow_seq[-1]} at 8.0 "
                       f"({[f'{g}: {s}' for g, s in zip((6.5, 7.0, 7.5, 8.0), slow_seq)]}), with interior values strictly "
                       f"between 0 and 1, so the transition has a measurable width in the time while it has none in the "
                       f"outcome ({co_seq} coalescing)")
        elif (slow_seq[0] or 0) == 0 and (slow_seq[1] or 0) == 0 and (slow_seq[2] or 0) == 0 and (slow_seq[3] or 0) == 1:
            verdict = (f"THE SAME WHOLE-CELL THRESHOLD IN THE TIME: every arm up to a gap of 7.5 sits at 0 slow seeds and "
                       f"8.0 jumps to 1, so the time steps where the outcome steps and X153's two slow seeds are the "
                       f"edge of that step, not a width")
        else:
            verdict = (f"BELOW THE RESOLUTION OF THE DESIGN: the slow fraction moves from {slow_seq[0]} at 6.5 to "
                       f"{slow_seq[-1]} at 8.0, less than the 0.3 the ten-seed design can defend, so the curve does not "
                       f"establish a width and no width is quoted")

    res = {
        "kind": "l1_field_x154_mixing",
        "experiment": "X154",
        "command": "python scripts/x154_analyse.py --write",
        "prereg": "reports/2026-11-03-x154-mixing-curve-plan.md",
        "definitions": {
            "unit": "the seed; four arms of one radius (6.0), ten seeds each",
            "slow": "a coalescing seed whose mutual coalescence lands at 49 or later logged steps, i.e. not at gap 7's 39",
            "slow_fraction": "slow seeds over coalescing seeds in the arm (the time readout)",
            "coalescing_fraction": "M over all seeds in the arm (the outcome readout)",
            "decision_rule": "rise of at least 0.3 with an interior value = width; unordered = noise; flat then 1.0 = step",
        },
        "curve": curve,
        "controls": {"failures": problems},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x154] written: {OUT.name}")
    for c in curve:
        print(f"  gap {c['gap']:>4}: M {c['M']}/{c['runs']}  slow {c['slow']} of {c['M']} "
              f"({c['slow_fraction']})  times {c['time_histogram']}  areas {c['rasterised_area_per_disc']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
