"""x150_analyse.py — X150: a third radius (6.0) against the two already measured.

Puts the three radii in one matrix, radius against surface gap, and asks the two questions the block now carries
separately: where does universal coalescence stop, and does the coalescence time stay the gap's.

Population (all read with `x142_analyse.world_row`, no distance tolerance):
  radius 6.0  gaps 6, 7, 8   — this run, separations 18, 19, 20
  radius 4.5  gaps 7, 8, 9   — X140 separation 16, X147 separation 17, X140 separation 18
  radius 3.0  gaps 6, 7, 8, 9 — X142 and X136 arms already in git

Plan: reports/2026-11-03-x150-radius6-plan.md.

    python scripts/x150_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x150_radius6.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

ARMS = {
    "r30_g6": ("x142_g6_r30", 3.0, 6),
    "r30_g7": ("x142_g7_r30", 3.0, 7),
    "r30_g8": ("x136_sep14", 3.0, 8),
    "r30_g9": ("x142_g9_r30", 3.0, 9),
    "r45_g7": ("x140_sep16", 4.5, 7),
    "r45_g8": ("x147_g8_r45", 4.5, 8),
    "r45_g9": ("x140_sep18", 4.5, 9),
    "r60_g6": ("x150_g6_r60", 6.0, 6),
    "r60_g7": ("x150_g7_r60", 6.0, 7),
    "r60_g8": ("x150_g8_r60", 6.0, 8),
}
SEEDS = (601, 602, 603, 604, 605)
# The timing law registered before the run: median logged steps in the arms that coalesce in every seed.
EXPECTED_TIME = {("r30", 6): 29, ("r30", 7): 39, ("r30", 8): 49,
                 ("r45", 7): 39, ("r45", 8): 49,
                 ("r60", 6): 29, ("r60", 7): 39, ("r60", 8): 49}


def load() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for key, (stem, _r, _g) in ARMS.items():
        rows = []
        for seed in SEEDS:
            p = L1 / f"{stem}_s{seed}.json"
            if p.exists():
                rows.append(A.world_row(p))
        out[key] = rows
    return out


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
    ap = argparse.ArgumentParser(description="X150 radius 6")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    raw = load()
    by_arm = {k: summarise(v) for k, v in raw.items()}

    bad = []
    if by_arm["r60_g6"]["runs"] != 5 or by_arm["r60_g7"]["runs"] != 5 or by_arm["r60_g8"]["runs"] != 5:
        bad.append("control: one of the three radius-6 arms does not have five usable runs")
    for key, rows in raw.items():
        for r in rows:
            if not r.get("usable"):
                bad.append(f"control: {key} {r['world']} does not start as two components")
            if r["empty"]:
                bad.append(f"control: {key} {r['world']} ends empty")

    # Control 1: the timing law must repeat in the arms that coalesce in every seed.
    timing = {}
    for key, (radius, gap) in ((k, (ARMS[k][1], ARMS[k][2])) for k in ARMS):
        rk = f"r{int(round(radius * 10))}"
        want = EXPECTED_TIME.get((rk, gap))
        arm = by_arm[key]
        if want is None or arm["M"] != arm["runs"] or arm["median_t_coalescence"] is None:
            continue
        timing[f"{rk}_g{gap}"] = {"observed": arm["median_t_coalescence"], "expected": want}
        if arm["median_t_coalescence"] != want:
            bad.append(f"control: {rk} gap {gap} coalesces at {arm['median_t_coalescence']} steps, the law says {want}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        r60 = {g: by_arm[f"r60_g{g}"] for g in (6, 7, 8)}
        first_break = None
        for g in (6, 7, 8):
            if r60[g]["M"] < r60[g]["runs"]:
                first_break = g
                break
        if first_break == 7:
            verdict = ("THE SHIFT IS A TREND: radius 6 coalesces in 5/5 seeds at a surface gap of 6 cells and breaks at "
                       "7, one cell inside radius 4.5 (break at 8) and two inside radius 3 (break at 9) - the boundary "
                       "moves inward by about half a cell per unit of radius, while the coalescence time stays the "
                       "gap's at 29 / 39 / 49 logged steps on all three radii")
        elif first_break == 8 or first_break is None:
            verdict = ("THE SHIFT SATURATES: radius 6 still coalesces in 5/5 seeds at a gap of 7 cells"
                       + ("" if first_break is None else " and breaks only at 8")
                       + ", the same place radius 4.5 breaks, so the inward move stops after 4.5 and something other "
                         "than the radius takes over past that size")
        elif first_break == 6:
            verdict = ("THE SHIFT ACCELERATES: radius 6 is already mixed at a gap of 6 cells, so the boundary falls "
                       "faster than linearly with the radius and the next step is a finer radius ladder rather than a "
                       "fourth radius")
        else:
            verdict = "void: no first break found in the radius-6 sweep"

    # The boundary per radius, as the largest gap that still coalesces in every seed.
    boundary = {}
    for rk, radius in (("r30", 3.0), ("r45", 4.5), ("r60", 6.0)):
        gaps = sorted(ARMS[k][2] for k in ARMS if ARMS[k][1] == radius)
        full = [g for g in gaps if by_arm[f"{rk}_g{g}"]["M"] == by_arm[f"{rk}_g{g}"]["runs"]]
        boundary[rk] = {"radius": radius, "gaps_measured": gaps,
                        "largest_gap_all_coalesce": max(full) if full else None}

    res = {
        "kind": "l1_field_x150_radius6",
        "experiment": "X150",
        "command": "python scripts/x150_analyse.py --write",
        "prereg": "reports/2026-11-03-x150-radius6-plan.md",
        "definitions": {
            "unit": "the arm (one radius, one surface gap); counts are out of the usable seeds",
            "gap": "SEP - 2R in cells",
            "M": "mutual coalescence: neither seeded uid has a daughter and both subtrees are gone at the last step",
            "A": "absorption: exactly one seeded subtree is alive at the last step",
            "P": "persistence: both seeded subtrees are alive at the last step",
            "boundary": "the largest surface gap measured at which every seed of the arm coalesces",
        },
        "by_arm": by_arm,
        "boundary": boundary,
        "timing_control": timing,
        "controls": {"failures": bad},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x150] written: {OUT.name}")
    for key in ARMS:
        a = by_arm.get(key)
        if a and a["runs"]:
            print(f"  {key:8s} M {a['M']}/{a['runs']}  A {a['A']}  P {a['P']}  "
                  f"median t {a['median_t_coalescence']} (n {a['n_timed']})")
    for rk, b in boundary.items():
        print(f"  boundary {rk}: largest gap with 5/5 coalescence = {b['largest_gap_all_coalesce']} "
              f"(gaps measured {b['gaps_measured']})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
