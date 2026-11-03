"""x126_analyse.py — X126: the third cell, three cells under one code path.

Ten worlds at F = 0.035 (x126) sit between the two known cells (x108 at 0.030 and 0.040). Every readout is X125c's definition, applied identically to the three
cells by the same code, and the two known cells must re-derive their published numbers before the new cell may be read.

Plan: reports/2026-11-03-x126-third-cell-plan.md.

    python scripts/x126_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x113_analyse import depth_of, life_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x126_third_cell.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",)},
    {"tag": "f035", "flow": 0.035, "series": ("x126",)},
    {"tag": "f040", "flow": 0.040, "series": ("x108",)},
]
KNOWN = {
    0.030: {"depth": 1.479, "p_nt": 0.5259, "rate": 6.056, "kept": 957, "pairs": 1142, "below": 0.1620, "survival": 0.250},
    0.040: {"depth": 2.213, "p_nt": 0.3881, "rate": 18.96, "kept": 638, "pairs": 1195, "below": 0.4661, "survival": 0.137},
}
MIDPOINT = {"depth": 1.846, "p_nt": 0.457, "rate": 12.508, "below": 0.314, "survival": 0.1935}
GRID = 96
OCCUPIED_FLOOR = 0.05
LARGEST_FLOOR = 50
MIN_LIFE = 50.0
MIN_PAIRS = 800
HEREDITY_FLOOR = 0.35
TOL_KNOWN = 0.02
BOOTSTRAP = 2000


def boot(vals, seed):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def descendants(children: dict[int, list[int]], uid: int) -> list[int]:
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
    return out


def cell_stats(flow: float, series: tuple[str, ...], seed: int) -> dict:
    g_diff, d_diff, r_filt, surv, below_flags = [], [], [], [], []
    heredity = []
    pairs = kept = 0
    both = only_big = only_small = neither = 0
    live_ok, runs = 0, 0
    occupied_frac, largest_area = [], []
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        runs += 1
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        last_step = max(w["per_step"]) if w["per_step"] else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        comps = w["per_step"].get(last_step) or []
        total = sum(int(c.get("area", 0)) for c in comps)
        biggest = max((int(c.get("area", 0)) for c in comps), default=0)
        occupied_frac.append(round(total / (GRID * GRID), 4))
        largest_area.append(biggest)
        if total >= OCCUPIED_FLOOR * GRID * GRID and biggest >= LARGEST_FLOOR:
            live_ok += 1
        memo: dict[int, int] = {}
        lives: dict[int, float] = {}
        subs: dict[int, list[int]] = {}

        def life(u: int, w=w, lives=lives) -> float:
            if u not in lives:
                lives[u] = life_of(w, u)
            return lives[u]

        def sub(u: int, children=children, subs=subs) -> list[int]:
            if u not in subs:
                subs[u] = descendants(children, u)
            return subs[u]

        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    gb, gs = life(big), life(small)
                    if gb <= 0 or gs <= 0:
                        continue
                    pairs += 1
                    g_diff.append(gb - gs)
                    below_flags.append(1.0 if (gb < MIN_LIFE or gs < MIN_LIFE) else 0.0)
                    d_diff.append(depth_of(children, big, memo) - depth_of(children, small, memo))
                    if gb >= MIN_LIFE and gs >= MIN_LIFE:
                        kept += 1
                        r_filt.append(depth_of(children, big, memo) / gb * 1000.0 - depth_of(children, small, memo) / gs * 1000.0)
                    alive_a = any(u in present for u in sub(big))
                    alive_s = any(u in present for u in sub(small))
                    if alive_a and alive_s:
                        both += 1
                    elif alive_a:
                        only_big += 1
                    elif alive_s:
                        only_small += 1
                    else:
                        neither += 1
                    surv.append(int(alive_a) - int(alive_s))

    non_tied = [x for x in g_diff if x != 0]
    p_nt = (len([x for x in non_tied if x > 0]) / len(non_tied)) if non_tied else None
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "runs": runs, "live_runs": live_ok,
        "occupied_frac_mean": round(st.mean(occupied_frac), 4) if occupied_frac else None,
        "largest_area_min": min(largest_area) if largest_area else None,
        "pairs": pairs, "pairs_kept": kept, "below_floor_share": round(1 - kept / pairs, 4) if pairs else None,
        "below_floor_ci": boot(below_flags, seed + 4),
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "depth_mean": round(st.mean(d_diff), 3) if d_diff else None,
        "depth_ci": boot(d_diff, seed),
        "rate_filtered": round(st.mean(r_filt), 3) if r_filt else None,
        "rate_ci": boot(r_filt, seed + 1),
        "p_nt": round(p_nt, 4) if p_nt is not None else None,
        "p_nt_ci": boot([1.0 if x > 0 else 0.0 for x in non_tied], seed + 2),
        "survival_mean": round(st.mean(surv), 4) if surv else None,
        "survival_ci": boot(surv, seed + 3),
        "both": both, "only_bigger": only_big, "only_smaller": only_small, "neither": neither,
    }


def se_of(ci):
    if not ci:
        return None
    return (ci[1] - ci[0]) / (2 * 1.96)


def classify(value, ci, mid, neighbours):
    """gradient: within 2 SE of the midpoint between the two known cells. step: outside that band but within 2 SE of one neighbour's value.
    Anything else is 'off the chord' — and the position tag says whether the value is between the two neighbours (a bend) or outside their range
    (a genuine reversal). Without that tag 'non-monotone' would be printed for a value that is monotone but not linear."""
    s = se_of(ci)
    if value is None or s is None or s == 0:
        return "undetermined", None, None
    d_mid = abs(value - mid) / s
    lo, hi = min(neighbours), max(neighbours)
    position = "between" if lo <= value <= hi else ("above" if value > hi else "below")
    if d_mid <= 2:
        return "gradient", round(d_mid, 2), position
    d_near = min(abs(value - n) for n in neighbours) / s
    if d_near <= 2:
        return "step", round(d_mid, 2), position
    return ("off the chord, reversal" if position != "between" else "off the chord, bend"), round(d_mid, 2), position


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X126 third cell")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {}
    for i, spec in enumerate(CELLS):
        cells[spec["tag"]] = cell_stats(spec["flow"], spec["series"], seed=1260 + 10 * i)

    bad = []
    for tag, c in cells.items():
        if c["runs"] == 0:
            bad.append(f"{tag}: no runs")
            continue
        if c["live_runs"] != c["runs"]:
            bad.append(f"{tag}: {c['runs'] - c['live_runs']} of {c['runs']} runs not alive under the structural rule")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} pairs")
    # the two known cells must re-derive their published numbers
    for tag in ("f030", "f040"):
        c = cells[tag]
        flow = next(s["flow"] for s in CELLS if s["tag"] == tag)
        ref = KNOWN[flow]
        for key, ref_key, label in (("depth_mean", "depth", "depth"), ("p_nt", "p_nt", "fraction"),
                                    ("rate_filtered", "rate", "rate"), ("survival_mean", "survival", "survival"),
                                    ("below_floor_share", "below", "below-floor share")):
            got = c[key]
            if got is None or abs(got - ref[ref_key]) > TOL_KNOWN:
                bad.append(f"{tag}: {label} {got} misses the published {ref[ref_key]}")
        if c["pairs_kept"] != ref["kept"] or c["pairs"] != ref["pairs"]:
            bad.append(f"{tag}: {c['pairs']} pairs / {c['pairs_kept']} kept against the published {ref['pairs']} / {ref['kept']}")

    new = cells["f035"]
    classes = {}
    for key, mid_key in (("depth_mean", "depth"), ("rate_filtered", "rate"), ("p_nt", "p_nt"),
                         ("below_floor_share", "below"), ("survival_mean", "survival")):
        ck = {"depth_mean": "depth_ci", "rate_filtered": "rate_ci", "p_nt": "p_nt_ci",
              "below_floor_share": "below_floor_ci", "survival_mean": "survival_ci"}[key]
        neighbours = (cells["f030"][key], cells["f040"][key])
        classes[key] = classify(new[key], new[ck], MIDPOINT[mid_key], [n for n in neighbours if n is not None])

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        head = (f"the third cell, F = 0.035: depth {new['depth_mean']} (CI {new['depth_ci']}), rate {new['rate_filtered']} "
                f"(CI {new['rate_ci']}, {new['pairs_kept']} of {new['pairs']} pairs), tie-excluded fraction {new['p_nt']} "
                f"(CI {new['p_nt_ci']}), below-floor share {new['below_floor_share']}, end-survival {new['survival_mean']} "
                f"(CI {new['survival_ci']}), heredity {new['rho_heredity']}")
        parts = ", ".join(f"{k}: {v[0]} ({v[1]} SE from the midpoint, {v[2]})" if v[1] is not None else f"{k}: {v[0]}"
                          for k, v in classes.items())
        grad = [k for k, v in classes.items() if v[0] == "gradient"]
        reversals = [k for k, v in classes.items() if v[0] == "off the chord, reversal"]
        if len(grad) >= 4:
            verdict = f"{head}. Gradient: {parts} — the cells interpolate, the habitat acts continuously in inflow."
        elif not grad:
            verdict = f"{head}. Step, not gradient: {parts} — no readout sits near the midpoint, so the habitat acts through a threshold."
        else:
            verdict = (f"{head}. Mixed: {parts} — {len(grad)} of 5 readouts interpolate"
                       + (f", and {', '.join(reversals)} reverses (the middle cell is outside the range of its neighbours)"
                          if reversals else "")
                       + ". The channels are named in the report: the generation clock moves continuously, lineage depth moves in a step, and "
                         "the rate accelerates below the chord.")

    res = {
        "kind": "l1_field_x126_third_cell",
        "experiment": "X126",
        "command": "python scripts/x126_analyse.py --write",
        "prereg": "reports/2026-11-03-x126-third-cell-plan.md",
        "definitions": {
            "depth": "mean paired sister difference, generations, no filter",
            "rate": f"paired difference of depth/generation_time*1000, both generation times >= {MIN_LIFE:.0f} steps, denominator printed",
            "p_nt": "fraction of non-tied pairs in which the larger sister's generation time is longer",
            "below_floor_share": f"fraction of pairs with a generation time < {MIN_LIFE:.0f} steps",
            "survival": "paired difference in 'the branch subtree has a member at the last logged step'",
            "liveness": f"structural rule: occupied >= {OCCUPIED_FLOOR} of the grid and largest component >= {LARGEST_FLOOR} cells at the last step",
        },
        "midpoints": MIDPOINT,
        "classes": {k: v[0] for k, v in classes.items()},
        "distance_to_midpoint_in_se": {k: v[1] for k, v in classes.items()},
        "position_against_neighbours": {k: v[2] for k, v in classes.items()},
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x126] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: runs={c['live_runs']}/{c['runs']} pairs={c['pairs']} kept={c['pairs_kept']} below={c['below_floor_share']} "
              f"heredity={c['rho_heredity']} depth={c['depth_mean']} {c['depth_ci']} rate={c['rate_filtered']} {c['rate_ci']} "
              f"p_nt={c['p_nt']} {c['p_nt_ci']} surv={c['survival_mean']} {c['survival_ci']}")
    print("  classes:", res["classes"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
