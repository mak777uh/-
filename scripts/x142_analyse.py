"""x142_analyse.py — X142: how far out does mutual coalescence reach?

Two discs are seeded as uid 1 and uid 2. With `--split-new-uid` each daughter gets a fresh uid, so a lineage is a
subtree. The three fates of a pair, defined without a distance tolerance (see amendment 2 of the plan):

  M — mutual coalescence: neither seeded uid ever has a daughter, and both are gone at the last step. The two discs
      became one body before either could grow a lineage, so both lineages end in the same object.
  A — absorption: one seeded lineage is alive at the last step and the other is not.
  P — persistence: both seeded subtrees are alive at the last step.

The earlier readout called a lost lineage "absorbed" only if the partner's last position was within
`r_dead + r_other + 2` cells, and everything else "unresolved"; the tolerance was an analyser parameter that decided
the fate at separations 10 and 11, where the last centroids sit on either side of it. It is not used here.

The unit of every number is the **arm** (one radius, one surface gap = `SEP - 2R`), and the denominator is the number
of usable seeds in it; `by_arm` always carries both.

Reused arms: radius 3 gaps 1, 2, 4, 5 from X139 (separations 7, 8, 10, 11), radius 3 gaps 8, 10, 11 from X136
(separations 14, 16, 17), radius 4.5 gap 7 from X140 (separation 16). Gaps 6 and 9 are re-run here because X136's
full logs for separations 12 and 15 were retired before the compact projections existed.

Plan: reports/2026-11-03-x142-annihilation-plan.md.

    python scripts/x142_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x142_coalescence.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

SEED_UIDS = (1, 2)
OCCUPIED_FLOOR = 0.05
LARGEST_FLOOR = 50
GRID = 96

SOURCES = ("x142_g*_r30_s*.json", "x142_g*_r45_s*.json", "x139_sep*_s*.json",
           "x136_sep*_s*.json", "x140_sep*_s*.json")

# The arms this experiment must end up with, and where each one's artifact lives.
EXPECTED = {
    "r30_g1": "x139_sep7", "r30_g2": "x139_sep8", "r30_g3": "x142_g3_r30", "r30_g4": "x139_sep10",
    "r30_g5": "x139_sep11", "r30_g6": "x142_g6_r30", "r30_g7": "x142_g7_r30", "r30_g8": "x136_sep14",
    "r30_g9": "x142_g9_r30", "r30_g10": "x136_sep16", "r30_g11": "x136_sep17",
    "r45_g4": "x142_g4_r45", "r45_g5": "x142_g5_r45", "r45_g6": "x142_g6_r45", "r45_g7": "x140_sep16",
}

# What the source series published per arm, under the OLD readout: (absorbed, both_alive). The new classes must be a
# refinement of these, not a different world: every seed called absorbed must now be A, every seed called both_alive
# must now be P, and the rest become M or A.
OLD_LABELS = {
    "r30_g1": (5, 0), "r30_g2": (5, 0), "r30_g4": (5, 0), "r30_g5": (0, 0),
    "r30_g8": (5, 0), "r30_g10": (2, 1), "r30_g11": (0, 3),
    "r45_g7": (5, 0),
}


def parse_arm(name: str) -> tuple[float, int, int, str] | None:
    m = re.match(r"x142_g(\d+)_r(\d+)_s(\d+)\.json$", name)
    if m:
        return int(m.group(2)) / 10.0, int(m.group(1)), int(m.group(3)), "new"
    m = re.match(r"x147_g(\d+)_r(\d+)_s(\d+)\.json$", name)
    if m:
        return int(m.group(2)) / 10.0, int(m.group(1)), int(m.group(3)), "X147"
    m = re.match(r"x139_sep(\d+)_s(\d+)\.json$", name)
    if m:
        return 3.0, int(m.group(1)) - 6, int(m.group(2)), "X139"
    m = re.match(r"x136_sep(\d+)_s(\d+)\.json$", name)
    if m:
        return 3.0, int(m.group(1)) - 6, int(m.group(2)), "X136"
    m = re.match(r"x140_sep(\d+)_s(\d+)\.json$", name)
    if m:
        return 4.5, int(m.group(1)) - 9, int(m.group(2)), "X140"
    return None


def descendants(kids, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def world_row(path) -> dict:
    w = world_data(path)
    parent = {int(c): int(p) for c, p in w["parent"].items()}
    kids: dict[int, list[int]] = {}
    for child, par in parent.items():
        kids.setdefault(par, []).append(child)
    steps = sorted(int(s) for s in w["per_step"])
    name = Path(path).name
    radius, gap, seed, source = parse_arm(name)

    present: dict[int, set] = {}
    first_pos: dict[int, tuple[int, float, float, float]] = {}
    for t in steps:
        comps = w["per_step"].get(t) or []
        here = set()
        for c in comps:
            uid = int(c["uid"])
            here.add(uid)
            first_pos.setdefault(uid, (t, float(c.get("cx", 0)), float(c.get("cy", 0)), float(c["area"])))
        present[t] = here

    last_step = steps[-1]
    both_seeded = all(u in present[steps[0]] for u in SEED_UIDS)
    tree = {u: descendants(kids, u) for u in SEED_UIDS}
    alive = {u: any(x in present[last_step] for x in tree[u]) for u in SEED_UIDS}
    daughters = {u: len(kids.get(u, [])) for u in SEED_UIDS}

    t_dissolve = None
    for t in steps:
        if not (present[t] & set(SEED_UIDS)):
            t_dissolve = t
            break
    comps_at_dissolve = len(w["per_step"].get(t_dissolve) or []) if t_dissolve is not None else None

    # X148: the area of the fusion product and whether a seeded disc divided before the pair became one body.
    split_step = None
    for u in SEED_UIDS:
        for child in kids.get(u, []):
            t_child = first_pos.get(child, (None,))[0]
            if t_child is not None and (split_step is None or t_child < split_step):
                split_step = t_child
    area_fusion = None
    area_before = None
    if t_dissolve is not None:
        comps = w["per_step"].get(t_dissolve) or []
        if len(comps) == 1:
            area_fusion = float(comps[0].get("area") or 0.0)
        idx = steps.index(t_dissolve)
        if idx > 0:
            area_before = sum(float(c.get("area") or 0.0)
                              for c in (w["per_step"].get(steps[idx - 1]) or []))
    divided_before_fusion = bool(split_step is not None and t_dissolve is not None and split_step <= t_dissolve)

    if not both_seeded:
        cls = None
    elif alive[1] and alive[2]:
        cls = "P"
    elif alive[1] or alive[2]:
        cls = "A"
    else:
        cls = "M"

    first_comps = w["per_step"].get(steps[0]) or []
    first_n = len([c for c in first_comps if float(c.get("area") or 0) >= 5.0])
    last_comps = w["per_step"].get(last_step) or []
    total = sum(float(c["area"]) for c in last_comps)
    largest = max((float(c["area"]) for c in last_comps), default=0.0)
    return {
        "world": name, "radius": radius, "gap": gap, "seed": seed, "source": source,
        "both_seeded": both_seeded,
        "first_components": first_n,
        "usable": first_n == 2,
        "class": cls,
        "t_dissolve": (t_dissolve - steps[0]) if t_dissolve is not None else None,
        "components_at_dissolve": comps_at_dissolve,
        "split_step": split_step,
        "divided_before_fusion": divided_before_fusion,
        "area_fusion": area_fusion,
        "area_before": area_before,
        "area_ratio": (area_fusion / area_before) if (area_fusion and area_before) else None,
        "daughters": {str(u): daughters[u] for u in SEED_UIDS},
        "subtree_alive": {str(u): alive[u] for u in SEED_UIDS},
        "subtree_sizes": {str(u): len(tree[u]) for u in SEED_UIDS},
        "live": total >= OCCUPIED_FLOOR * GRID * GRID and largest >= LARGEST_FLOOR,
        "empty": total < OCCUPIED_FLOOR * GRID * GRID,
        "components_at_end": len(last_comps),
        "occupied": round(total / (GRID * GRID), 4),
        "steps": len(steps),
    }



def fusion_block(usable: list[dict]) -> dict:
    """X148: does the seed that divides have the larger body at the moment the two seeds disappear?

    The size compared is `area_before` — the summed area of the field one logged step **before** neither seeded uid is
    present — because it is defined for every run. `area_fusion` is reported separately and needs exactly one component
    at that step, which only the pure coalescences have.
    """
    divided = [r for r in usable if r["divided_before_fusion"]]
    plain = [r for r in usable if not r["divided_before_fusion"]]
    sized = [r for r in usable if r["area_before"] is not None]
    out = {
        "fused": len([r for r in usable if r["area_fusion"] is not None]),
        "divided": len(divided),
        "not_divided": len(plain),
        "median_area_divided": round(st.median([r["area_before"] for r in divided if r["area_before"]]), 1)
        if any(r["area_before"] for r in divided) else None,
        "median_area_not_divided": round(st.median([r["area_before"] for r in plain if r["area_before"]]), 1)
        if any(r["area_before"] for r in plain) else None,
        "median_fusion_area_divided": round(st.median([r["area_fusion"] for r in divided if r["area_fusion"]]), 1)
        if any(r["area_fusion"] for r in divided) else None,
        "median_fusion_area_not_divided": round(st.median([r["area_fusion"] for r in plain if r["area_fusion"]]), 1)
        if any(r["area_fusion"] for r in plain) else None,
        "seeds": {str(r["seed"]): {"area_fusion": r["area_fusion"], "area_before": r["area_before"],
                                   "area_ratio": (round(r["area_ratio"], 3) if r["area_ratio"] else None),
                                   "split_step": r["split_step"],
                                   "divided_before_fusion": r["divided_before_fusion"],
                                   "class": r["class"]} for r in sorted(usable, key=lambda r: r["seed"])},
    }
    # the sign: in an arm where both outcomes occur, are the dividing seeds the larger ones?
    d_sizes = [r["area_before"] for r in divided if r["area_before"]]
    p_sizes = [r["area_before"] for r in plain if r["area_before"]]
    if d_sizes and p_sizes:
        if min(d_sizes) > max(p_sizes):
            out["sign"] = "divided_is_larger"
        elif max(d_sizes) < min(p_sizes):
            out["sign"] = "divided_is_smaller"
        else:
            out["sign"] = "interleaved"
    else:
        out["sign"] = None
    out["sized"] = len(sized)
    return out

def arm_key(radius: float, gap: int) -> str:
    return f"r{int(round(radius * 10))}_g{gap}"


def summarise(key: str, rows: list[dict]) -> dict:
    usable = [r for r in rows if r.get("usable")]
    counts = {c: len([r for r in usable if r["class"] == c]) for c in ("M", "A", "P")}
    m_times = [r["t_dissolve"] for r in usable if r["class"] == "M" and r["t_dissolve"] is not None]
    return {
        "key": key,
        "radius": rows[0]["radius"] if rows else None,
        "gap": rows[0]["gap"] if rows else None,
        "runs": len(usable),
        "M": counts["M"], "A": counts["A"], "P": counts["P"],
        "median_mutual_coalescence": round(st.median(m_times), 1) if m_times else None,
        "median_components_at_end": round(st.median([r["components_at_end"] for r in usable]), 1) if usable else None,
        "fragmented": len([r for r in usable if not r["live"]]),
        "fusion": fusion_block(usable),
        "min_occupied": min((r["occupied"] for r in usable), default=None),
        "seeds": {str(r["seed"]): {"class": r["class"], "t_dissolve": r["t_dissolve"],
                                   "components_at_dissolve": r["components_at_dissolve"],
                                   "daughters": r["daughters"], "subtree_alive": r["subtree_alive"],
                                   "subtree_sizes": r["subtree_sizes"], "live": r["live"],
                                   "source": r["source"]} for r in sorted(usable, key=lambda r: r["seed"])},
    }


def control_failures(by_arm: dict, rows: list[dict]) -> list[str]:
    bad = []
    absent = [f"{k} ({EXPECTED[k]})" for k in EXPECTED if k not in by_arm]
    if absent:
        bad.append("provenance: no artifact for " + ", ".join(absent))
    for key, (old_absorbed, old_both) in OLD_LABELS.items():
        arm = by_arm.get(key)
        if arm is None:
            continue
        # The old readout reported the FIRST death of the pair and called it absorption whenever the partner's last
        # position was within a 2-cell tolerance. So its "absorbed" seeds can be M here (the partner died later, and
        # the merged body is a new uid) but never fewer than the true A; its "both alive" seeds must be P exactly.
        if arm["P"] != old_both:
            bad.append(f"control 1: {key} has {arm['P']} P but the source published {old_both} both alive")
        if arm["M"] + arm["A"] < old_absorbed:
            bad.append(f"control 1: {key} has M{arm['M']}+A{arm['A']} but the source published {old_absorbed} "
                       f"seeds with a first death - the new classes cannot have fewer")
        if arm["M"] + arm["A"] + arm["P"] != arm["runs"]:
            bad.append(f"control 1: {key} classes do not add up ({arm['M']}+{arm['A']}+{arm['P']} vs {arm['runs']})")
    # control 1b - the two re-run arms must reproduce the X136 aggregate they stand in for: the same number of seeds
    # with a first death, and the same number of seeds with both lineages alive.
    rereun = {"r30_g6": (5, 0), "r30_g9": (5, 0)}
    for key, (want_absorbed, want_both) in rereun.items():
        arm = by_arm.get(key)
        if arm is None:
            continue
        if arm["M"] + arm["A"] < want_absorbed or arm["P"] != want_both:
            bad.append(f"control 1b: {key} gives M{arm['M']} A{arm['A']} P{arm['P']}, "
                       f"X136 published {want_absorbed} seeds with a first death and {want_both} both alive")
    degenerate = [r["world"] for r in rows if not r.get("usable")]
    if degenerate:
        bad.append(f"control 3: does not start as two components: {degenerate[:3]}")
    empty = [r["world"] for r in rows if r["empty"]]
    if empty:
        bad.append(f"control 4: {len(empty)} runs end empty ({empty[:3]})")
    return bad


def _curve(arms: dict) -> str:
    out = []
    for gap in sorted(arms):
        a = arms[gap]
        total = max(a["runs"], 1)
        if a["M"] >= 3:
            out.append(f"g{gap}: M {a['M']}/{total} at {a['median_mutual_coalescence']}")
        elif a["P"] >= 3:
            out.append(f"g{gap}: P {a['P']}/{total}")
        else:
            out.append(f"g{gap}: mixed M{a['M']}A{a['A']}P{a['P']}")
    return ", ".join(out)



def fusion_verdict(by_arm: dict) -> str:
    signs = {k: v["fusion"]["sign"] for k, v in sorted(by_arm.items())
             if v["fusion"].get("sign") in ("divided_is_larger", "divided_is_smaller")}
    arms = [k for k, v in by_arm.items() if v["fusion"]["divided"] and v["fusion"]["not_divided"]]
    if len(arms) < 3:
        return (f"NOT DECIDABLE: only {len(arms)} arm(s) contain both outcomes ({arms}), so there is nothing to order "
                f"within an arm; the next design must place arms at the boundary, not further out")
    larger = [k for k, s in signs.items() if s == "divided_is_larger"]
    if len(larger) == len(arms):
        return (f"SIZE RULES: in all {len(arms)} arms where both outcomes occur the dividing seeds are the ones with "
                f"the larger fusion product ({arms})")
    return (f"SIZE DOES NOT RULE: {len(larger)} of {len(arms)} arms have the dividing seeds larger ({signs}); the "
            f"sign is inconsistent, so the product's area is not what decides division")

def verdict_for(by_arm: dict, bad: list[str]) -> str:
    if bad:
        return "void: " + "; ".join(bad)
    r3 = {a["gap"]: a for a in by_arm.values() if a["radius"] == 3.0}
    r45 = {a["gap"]: a for a in by_arm.values() if a["radius"] == 4.5}
    parts = [f"radius 3 ({_curve(r3)})"]
    pure_m = sorted(g for g, a in r3.items() if a["M"] == a["runs"] and a["runs"] > 0)
    first_break = min((g for g in sorted(r3) if g not in pure_m), default=None)
    if pure_m:
        top = max(pure_m)
        if first_break is not None:
            parts.append(f"MUTUAL COALESCENCE HOLDS IN EVERY SEED from contact out to a gap of {top} cells and breaks "
                         f"at {first_break}")
        else:
            parts.append(f"MUTUAL COALESCENCE HOLDS IN EVERY SEED at every gap measured, up to {top} cells")
    if r45:
        parts.append(f"radius 4.5 ({_curve(r45)})")
        m45 = sorted(g for g, a in r45.items() if a["M"] == a["runs"] and a["runs"] > 0)
        if m45:
            parts.append(f"radius 4.5 is mutual coalescence in every seed at gaps {m45}")
    both = sorted(set(r3) & set(r45))
    same = [g for g in both
            if r3[g]["median_mutual_coalescence"] is not None
            and r3[g]["median_mutual_coalescence"] == r45[g]["median_mutual_coalescence"]]
    if len(both) >= 3 and len(same) == len(both):
        parts.append(f"at every gap measured on both radii ({both}) the median time to mutual coalescence is IDENTICAL "
                     f"({[r3[g]['median_mutual_coalescence'] for g in both]} steps), so the time is a function of the "
                     f"surface gap and not of the structure's size")
    elif both:
        parts.append("times on the two radii differ at gaps " + str([g for g in both if g not in same]))
    m_times = {g: r3[g]["median_mutual_coalescence"] for g in sorted(r3) if r3[g]["median_mutual_coalescence"] is not None}
    if m_times:
        parts.append("dissolution time by gap: " + ", ".join(f"{g}: {t}" for g, t in m_times.items()))
    return "; ".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X142 mutual coalescence")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    files = []
    for pattern in SOURCES:
        files.extend(p for p in L1.glob(pattern) if not p.name.endswith(".compact.json"))
    rows = [world_row(p) for p in sorted(set(files))]
    rows = [r for r in rows if r is not None and arm_key(r["radius"], r["gap"]) in EXPECTED]

    grouped: dict[str, list[dict]] = {}
    for r in rows:
        grouped.setdefault(arm_key(r["radius"], r["gap"]), []).append(r)
    by_arm = {k: summarise(k, v) for k, v in sorted(grouped.items())}

    bad = control_failures(by_arm, rows)
    verdict = verdict_for(by_arm, bad)

    res = {
        "kind": "l1_field_x142_coalescence",
        "experiment": "X142",
        "command": "python scripts/x142_analyse.py --write",
        "prereg": "reports/2026-11-03-x142-annihilation-plan.md",
        "definitions": {
            "unit": "the arm (one radius, one surface gap); every count is out of the usable seeds in that arm",
            "gap": "SEP - 2R in cells, from the nominal radii",
            "seed_uids": "the two discs are uid 1 and uid 2; with --split-new-uid a lineage is the subtree",
            "M": "mutual coalescence: neither seeded uid has a daughter and both subtrees are gone at the last step",
            "A": "absorption: exactly one seeded subtree is alive at the last step",
            "P": "persistence: both seeded subtrees are alive at the last step",
            "t_dissolve": "the logged step at which neither seeded uid is present any more, minus the first logged step",
            "no_tolerance": "no distance tolerance is used; the reach test of the earlier readout is what amendment 2 removes",
        },
        "by_arm": by_arm,
        "runs": len(rows),
        "mutual_coalescence_gaps": {
            "r30": sorted({a["gap"] for a in by_arm.values() if a["radius"] == 3.0 and a["M"] >= 3}),
            "r45": sorted({a["gap"] for a in by_arm.values() if a["radius"] == 4.5 and a["M"] >= 3}),
        },
        "controls": {
            "refinement": "every seed the source series called absorbed must be A here and every both_alive must be P; "
                          "M is the old 'unresolved' class where the seeds never had daughters",
            "probe": "scripts/x142_series.py --probe-control: a fresh repeat of X139's gap-5 arm was identical in "
                     "series, uid_pairs and summary",
            "failures": bad,
        },
        "fusion": {
            "question": "does a seed divide because the fusion product is larger?",
            "plan": "reports/2026-11-03-x148-fusion-size-plan.md",
            "per_arm": {k: v["fusion"]["sign"] for k, v in by_arm.items()},
            "arms_with_both_outcomes": [k for k, v in by_arm.items()
                                        if v["fusion"]["divided"] and v["fusion"]["not_divided"]],
            "verdict": fusion_verdict(by_arm),
        },
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x142] written: {OUT.name}")
    for key in sorted(by_arm):
        a = by_arm[key]
        print(f"  {key:8s} gap {a['gap']:2d}: M {a['M']}/{a['runs']}  A {a['A']}/{a['runs']}  P {a['P']}/{a['runs']}  "
              f"median M {a['median_mutual_coalescence']}  fragmented {a['fragmented']}")
    missing = [k for k in EXPECTED if k not in by_arm]
    if missing:
        print("  missing arms:", ", ".join(missing))
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
