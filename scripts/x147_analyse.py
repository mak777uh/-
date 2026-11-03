"""x147_analyse.py — X147: is the coalescence boundary at the same surface gap for two radii?

Reads the classification of `x142_analyse.world_row` (M — mutual coalescence, A — absorption, P — persistence; no
distance tolerance) and puts the two radii side by side at one-cell spacing.

Population:
  radius 4.5  gaps 7, 9, 11, 13 — X140 separations 16, 18, 20, 22 (reused)
  radius 4.5  gap 8            — five new runs, separation 17
  radius 3    gaps 7, 8, 9     — X142 and X136 arms already in git, as the comparison

Plan: reports/2026-11-03-x147-radius45-plan.md.

    python scripts/x147_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x147_radius45.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

ARMS = {
    "r45_g7": ("x140_sep16", 4.5, 7),
    "r45_g8": ("x147_g8_r45", 4.5, 8),
    "r45_g9": ("x140_sep18", 4.5, 9),
    "r45_g11": ("x140_sep20", 4.5, 11),
    "r45_g13": ("x140_sep22", 4.5, 13),
    "r30_g7": ("x142_g7_r30", 3.0, 7),
    "r30_g8": ("x136_sep14", 3.0, 8),
    "r30_g9": ("x142_g9_r30", 3.0, 9),
}
SEEDS = (601, 602, 603, 604, 605)


def load() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for key, (stem, _radius, _gap) in ARMS.items():
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
    times = [r["t_dissolve"] for r in usable if r["t_dissolve"] is not None]
    return {
        "runs": len(usable), "M": counts["M"], "A": counts["A"], "P": counts["P"],
        "median_t_dissolve": round(st.median(times), 1) if times else None,
        "seeds": {str(r["seed"]): {"class": r["class"], "t_dissolve": r["t_dissolve"],
                                   "daughters": r["daughters"]} for r in sorted(usable, key=lambda r: r["seed"])},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X147 radius 4.5 transition")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    raw = load()
    by_arm = {k: summarise(v) for k, v in raw.items()}

    bad = []
    expected = {
        "r45_g7": (5, 0, 0), "r45_g9": (2, 2, 1), "r45_g11": (0, 0, 5), "r45_g13": (0, 0, 5),
        "r30_g7": (5, 0, 0), "r30_g8": (5, 0, 0), "r30_g9": (3, 2, 0),
    }
    for key, (m, a, p) in expected.items():
        arm = by_arm.get(key)
        if arm is None or arm["runs"] == 0:
            bad.append(f"control: {key} missing from the analysis")
            continue
        if (arm["M"], arm["A"], arm["P"]) != (m, a, p):
            bad.append(f"control: {key} gives M{arm['M']} A{arm['A']} P{arm['P']}, recorded M{m} A{a} P{p}")
    new = by_arm.get("r45_g8")
    if not new or new["runs"] != 5:
        bad.append(f"control: the new arm has {new['runs'] if new else 0} usable runs, expected 5")
    for key, rows in raw.items():
        for r in rows:
            if not r.get("usable"):
                bad.append(f"control: {key} {r['world']} does not start as two components")
            if r["empty"]:
                bad.append(f"control: {key} {r['world']} ends empty")

    if bad:
        verdict = "void: " + "; ".join(bad)
    elif new["M"] == 5:
        verdict = ("THE BOUNDARY IS THE GAP'S: radius 4.5 coalesces in 5/5 seeds at surface gap 8, as radius 3 does, "
                   "and both radii are mixed at gap 9 (radius 3 M3 A2, radius 4.5 M2 A2 P1) - the transition sits at a "
                   "gap of 8-9 cells on both, so it belongs to the distance between surfaces and not to the radius")
    elif new["M"] >= 4:
        verdict = (f"INDETERMINATE: radius 4.5 gap 8 is M {new['M']}/5 against 5/5 at radius 3 - one seed apart, which "
                   f"this sweep cannot resolve; the next run doubles the seeds at gaps 8 and 9 rather than adding gaps")
    else:
        verdict = (f"THE BOUNDARY MOVES INWARD WITH THE RADIUS: radius 4.5 gap 8 is only M {new['M']}/5 while radius 3 "
                   f"is M 5/5, so the bigger discs begin to fail a cell earlier in gap")

    res = {
        "kind": "l1_field_x147_radius45",
        "experiment": "X147",
        "command": "python scripts/x147_analyse.py --write",
        "prereg": "reports/2026-11-03-x147-radius45-plan.md",
        "definitions": {
            "unit": "the arm (one radius, one surface gap); counts are out of the usable seeds",
            "gap": "SEP - 2R in cells",
            "M": "mutual coalescence: neither seeded uid has a daughter and both subtrees are gone at the last step",
            "A": "absorption: exactly one seeded subtree is alive at the last step",
            "P": "persistence: both seeded subtrees are alive at the last step",
            "readout": "x142_analyse.world_row - the same code, no distance tolerance",
        },
        "by_arm": by_arm,
        "timing_note": "the reused radius-4.5 arms come from X140, whose series was run for the crossing; their flags "
                       "and probe are the same, checked key by key when that series closed",
        "controls": {"failures": bad},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x147] written: {OUT.name}")
    for key in ("r45_g7", "r45_g8", "r45_g9", "r45_g11", "r45_g13", "r30_g7", "r30_g8", "r30_g9"):
        a = by_arm.get(key)
        if a:
            print(f"  {key:8s} M {a['M']}/{a['runs']}  A {a['A']}  P {a['P']}  median t {a['median_t_dissolve']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
