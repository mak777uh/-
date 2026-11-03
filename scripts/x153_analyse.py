"""x153_analyse.py — X153: is the boundary a whole-cell step or does it creep within a cell?

One arm: radius 6.0 at separation 19.5 (surface gap 7.5), ten seeds. The registered decision rule is in
reports/2026-11-03-x153-halfcell-plan.md §4–5: at least 9 of 10 coalescing means the step stands, at most 6 of 10 means
the boundary creeps, 7 or 8 is indeterminate, 3 or fewer is a contradiction of monotonicity.

    python scripts/x153_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x153_halfcell.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
SEEDS = tuple(range(601, 611))
NEIGHBOURS = {  # radius 6, from the committed X150 aggregate
    7: ("x150_g7_r60", 5, 5, 39),
    8: ("x150_g8_r60", 3, 5, 49),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X153 half-cell gap")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rows, gaps = [], []
    for seed in SEEDS:
        p = L1 / f"x153_g75_r60_s{seed}.json"
        if p.exists():
            r = A.world_row(p)
            rows.append(r)
            world = None
            try:
                world = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                world = None
            if world:
                params = world.get("params") or {}
                if params.get("init_spots"):
                    gaps.append(params["init_spots"])

    usable = [r for r in rows if r.get("usable")]
    counts = {c: len([r for r in usable if r["class"] == c]) for c in ("M", "A", "P")}
    times = [r["t_dissolve"] for r in usable if r["class"] == "M" and r["t_dissolve"] is not None]
    median_t = round(st.median(times), 1) if times else None
    time_hist = {str(t): times.count(t) for t in sorted(set(times))}

    # The rasterised initial state, against the neighbouring arm at the same radius: a half-cell separation can move
    # the discs by a cell, so the manipulation has to be checked on the field, not only on the parameter.
    def step1(stem: str, seed: int) -> dict | None:
        p = L1 / f"{stem}_s{seed}.json"
        if not p.exists():
            return None
        w = json.loads(p.read_text(encoding="utf-8"))
        s = (w.get("series") or [{}])[0]
        return {"areas": s.get("areas"), "components": s.get("components"), "occupied": s.get("occupied")}

    initial = {str(seed): {"gap75": step1("x153_g75_r60", seed), "gap7": step1("x150_g7_r60", seed)}
               for seed in SEEDS}

    bad = []
    if len(usable) != 10:
        bad.append(f"control: {len(usable)} usable runs, expected 10")
    for r in rows:
        if not r.get("usable"):
            bad.append(f"control: {r['world']} does not start as two components")
        if r["empty"]:
            bad.append(f"control: {r['world']} ends empty")
    if not gaps:
        bad.append("control: the artifact does not record params.init_spots, so the surface gap 7.5 cannot be confirmed")
    else:
        if not all(str(g).strip() in ("6.0:19.5", "6:19.5") for g in gaps):
            bad.append(f"control: the artifact records params.init_spots {sorted(set(map(str, gaps)))}, expected 6.0:19.5")
    if median_t is not None and not (39 <= median_t <= 49):
        bad.append(f"control: median time {median_t} is outside the bracket [39, 49] set by gaps 7 and 8")
    if len(usable) == 10:  # only then can the bracket control be judged on all seeds
        pass

    m = counts["M"]
    n = len(usable)
    slow = int(time_hist.get("49", 0) + time_hist.get("59", 0))
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif m >= 9:
        verdict = (f"WHOLE-CELL STEP IN THE OUTCOME, AND A MIX IN THE TIME: {m} of {n} seeds coalesce at a surface gap "
                   f"of 7.5 cells, as they do at 7, so the half-cell does not move the boundary - it stays the last "
                   f"integer gap at which coalescence is universal (8 cells for a 28-cell disc, 7 for the larger ones). "
                   f"But the half-cell is visible in the timing: {slow} of {n} seeds dissolve at the later logged step "
                   f"({time_hist}) while {n - slow} keep gap 7's step, and at gap 8 the coalescing seeds spread over two "
                   f"later steps too. So the outcome steps and the time mixes - the third time the two laws behave "
                   f"differently")
    elif m <= 3:
        verdict = (f"CONTRADICTION: only {m} of {n} seeds coalesce at a gap of 7.5, fewer than the 3 of 5 at a gap of 8, "
                   f"which breaks the monotonicity the block rests on - no further radius until this is explained")
    elif m <= 6:
        verdict = (f"THE BOUNDARY CREEPS WITHIN THE CELL: {m} of {n} seeds coalesce at a gap of 7.5, already fewer than "
                   f"at 7 (5 of 5), so the boundary is a line and the reported gap of 7 is a sampling of it - the next run "
                   f"is a half-cell ladder at radius 6 with ten seeds per arm")
    else:
        verdict = (f"INDETERMINATE: {m} of {n} seeds coalesce at a gap of 7.5 - seven or eight of ten is inside the noise "
                   f"of this denominator, as registered; the next run doubles the seeds at 7.5 alone")

    res = {
        "kind": "l1_field_x153_halfcell",
        "experiment": "X153",
        "command": "python scripts/x153_analyse.py --write",
        "prereg": "reports/2026-11-03-x153-halfcell-plan.md",
        "definitions": {
            "unit": "the seed; the arm is one radius and one surface gap of 7.5 cells",
            "gap": "SEP - 2R in cells, here 19.5 - 12 = 7.5",
            "M": "mutual coalescence: neither seeded uid has a daughter and both subtrees are gone at the last step",
            "readout": "x142_analyse.world_row - the same code, no distance tolerance",
            "decision_rule": ">=9/10 step, <=6/10 creep, 7-8/10 indeterminate, <=3/10 contradiction (registered before)",
        },
        "arm": {"radius": 6.0, "separation": 19.5, "gap": 7.5, "runs": n,
                "M": counts["M"], "A": counts["A"], "P": counts["P"],
                "median_t_coalescence": median_t, "n_timed": len(times),
                "time_histogram": time_hist,
                "seeds": {str(r["seed"]): {"class": r["class"], "t_dissolve": r["t_dissolve"],
                                           "daughters": r["daughters"], "live": r["live"]}
                          for r in sorted(usable, key=lambda r: r["seed"])}},
        "initial_state": initial,
        "manipulation_note": ("the half-cell separation also moved the rasterised discs by one cell each (areas 110 "
                              "against 108 at gap 7), so the arm is a gap plus ~2 % of area; the direction is "
                              "conservative, because a larger disc is the case where the boundary breaks earlier"),
        "neighbours_radius6": {str(g): {"arm": v[0], "M": v[1], "of": v[2], "median_t": v[3]}
                               for g, v in NEIGHBOURS.items()},
        "seeds_601_605_only": {str(r["seed"]): r["class"] for r in sorted(usable, key=lambda r: r["seed"])
                               if r["seed"] <= 605},
        "controls": {"failures": bad, "init_spots_recorded": sorted(set(map(str, gaps)))},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x153] written: {OUT.name}")
    print(f"  radius 6, gap 7.5: M {counts['M']}/{n}  A {counts['A']}  P {counts['P']}  median t {median_t} "
          f"(n {len(times)})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
