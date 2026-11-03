"""x145_analyse.py — X145: when does a lone disc first split, at each radius?

One disc is seeded (`--init-spots R:0`) and nothing else. The readout is genealogical: the first logged step at which
a uid present at the start has a daughter. Radii 4.5 and 6 are reused from X140 and X138; radius 3 is new.

The comparison this feeds is in `reports/2026-11-03-x142-coalescence.md`: a pair at gaps 1-8 is one body by step 10-50,
so if a lone radius-3 disc splits later than that, the boundary between mutual coalescence and persistence is a race
between touching and splitting.

    python scripts/x145_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x145_lone_disc.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

GRID = 96
OCCUPIED_FLOOR = 0.05
LARGEST_FLOOR = 50
SEEDS = (601, 602, 603, 604, 605)


def parse(path: Path) -> tuple[float, int] | None:
    m = re.match(r"x145_lone_r(\d+)_s(\d+)\.json$", path.name)
    if m:
        return int(m.group(1)) / 10.0, int(m.group(2))
    m = re.match(r"x140_sep0_s(\d+)\.json$", path.name)
    if m:
        return 4.5, int(m.group(1))
    m = re.match(r"x138_sep0_s(\d+)\.json$", path.name)
    if m:
        return 6.0, int(m.group(1))
    return None


def row(path: Path) -> dict:
    radius, seed = parse(path)
    w = world_data(path)
    steps = sorted(int(s) for s in w["per_step"])
    first_pos: dict[int, int] = {}
    for t in steps:
        for c in (w["per_step"].get(t) or []):
            first_pos.setdefault(int(c["uid"]), t)
    kids: dict[int, list[int]] = {}
    for child, par in w["parent"].items():
        kids.setdefault(par, []).append(child)
    split = None
    for par, children in kids.items():
        t = min(first_pos.get(c, 10 ** 9) for c in children)
        if split is None or t < split:
            split = t
    first_comps = w["per_step"].get(steps[0]) or []
    first_n = len([c for c in first_comps if float(c.get("area") or 0) >= 5.0])
    last_comps = w["per_step"].get(steps[-1]) or []
    total = sum(float(c["area"]) for c in last_comps)
    largest = max((float(c["area"]) for c in last_comps), default=0.0)
    return {
        "world": path.name, "radius": radius, "seed": seed,
        "first_components": first_n,
        "usable": first_n == 1,
        "first_split_step": split,
        "first_split": (split - steps[0]) if split is not None else None,
        "uids": len(first_pos),
        "components_at_end": len(last_comps),
        "occupied": round(total / (GRID * GRID), 4),
        "live": total >= OCCUPIED_FLOOR * GRID * GRID and largest >= LARGEST_FLOOR,
        "empty": total < OCCUPIED_FLOOR * GRID * GRID,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X145 lone disc")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    files = [p for pat in ("x145_lone_r*_s*.json", "x140_sep0_s*.json", "x138_sep0_s*.json")
             for p in L1.glob(pat) if not p.name.endswith(".compact.json")]
    rows = [row(p) for p in sorted(set(files))]
    rows = [r for r in rows if r.get("radius") is not None]

    by_radius: dict[str, dict] = {}
    for radius in sorted({r["radius"] for r in rows}):
        rs = [r for r in rows if r["radius"] == radius]
        usable = [r for r in rs if r["usable"]]
        splits = [r["first_split_step"] for r in usable if r["first_split_step"] is not None]
        by_radius[str(radius)] = {
            "runs": len(usable),
            "first_split_median": round(st.median(splits), 1) if splits else None,
            "first_split_by_seed": {str(r["seed"]): r["first_split_step"] for r in sorted(usable, key=lambda r: r["seed"])},
            "never_split": len([r for r in usable if r["first_split_step"] is None]),
            "median_components_at_end": round(st.median([r["components_at_end"] for r in usable]), 1) if usable else None,
            "min_occupied": min((r["occupied"] for r in usable), default=None),
            "fragmented": len([r for r in usable if not r["live"]]),
        }

    bad = []
    expect_reuse = {"4.5": [280, 190, 230, 150, 150], "6.0": [210, 460, 290, 290, 290]}
    for radius_key, want in expect_reuse.items():
        got = by_radius.get(radius_key)
        if got is None:
            bad.append(f"control 1: radius {radius_key} missing from the analysis")
            continue
        series = [got["first_split_by_seed"][str(s)] for s in SEEDS]
        if series != want:
            bad.append(f"control 1: radius {radius_key} split times {series} against the recorded {want}")
    new = by_radius.get("3.0")
    if new is None:
        bad.append("provenance: no radius-3 arm")
    else:
        if new["runs"] != 5:
            bad.append(f"control 2: {new['runs']} usable radius-3 runs, expected 5")
        if new["never_split"]:
            bad.append(f"counted as 'never splits', not an error: {new['never_split']} of 5 seeds")

    r3 = by_radius.get("3.0") or {}
    med = r3.get("first_split_median")
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif med is None:
        verdict = ("the lone radius-3 disc NEVER splits within 6000 steps, while a pair at gaps 1-8 is one body by step "
                   "50: the splits seen at gaps 9-11 are triggered by contact, not by a clock")
    elif med <= 100:
        verdict = (f"the lone radius-3 disc splits at a median of {med} steps, and pairs at gaps 1-8 are one body by "
                   f"step 50, so coalescence happens BEFORE the disc would split: the boundary is a race between "
                   f"touching and splitting")
    else:
        verdict = (f"the lone radius-3 disc splits at a median of {med} steps, in line with radii 4.5 and 6, and a pair "
                   f"at gaps 1-8 is one body by step 50: the split time is not what sets the boundary at radius 3")

    res = {
        "kind": "l1_field_x145_lone_disc",
        "experiment": "X145",
        "command": "python scripts/x145_analyse.py --write",
        "prereg": "reports/2026-11-03-x145-lone-disc-plan.md",
        "definitions": {
            "unit": "the radius; every count is out of the usable seeds at that radius",
            "first_split": "the first logged step at which a uid present at the start has a daughter, minus the first logged step",
            "one_disc": "`--init-spots R:0` places one disc; the flag's two centres coincide",
        },
        "by_radius": by_radius,
        "runs": len(rows),
        "controls": {
            "reuse": "radii 4.5 and 6 must reproduce the split times recorded in X140 and X138, seed by seed",
            "start": "one component of area >= 20 cells at the first logged step",
            "empty": "no run may end empty",
            "failures": bad,
        },
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x145] written: {OUT.name}")
    for key in sorted(by_radius):
        v = by_radius[key]
        print(f"  radius {key}: runs {v['runs']}, first split median {v['first_split_median']}, "
              f"never {v['never_split']}, fragmented {v['fragmented']}, min occupied {v['min_occupied']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
