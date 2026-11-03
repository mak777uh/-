"""x130_analyse.py — X130: do sisters merge back, and how long does it take?

For every division with two measurable daughters: their centroid separation at birth, and the first step at which one daughter's own uid ends while the other is
present and within reach of its last centroid. Censored at the run's end, and the censoring share is printed next to the merge share.

Plan: reports/2026-11-03-x130-remerge-plan.md.

    python scripts/x130_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x130_remerge.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",), "sibling_absorptions": 186},
    {"tag": "f035", "flow": 0.035, "series": ("x126",), "sibling_absorptions": 31},
    {"tag": "f040", "flow": 0.040, "series": ("x108",), "sibling_absorptions": 57},
]
KNOWN_SURVIVAL = {0.030: 0.2496, 0.035: 0.2984, 0.040: 0.1372}
KNOWN_PAIRS = {0.030: 1142, 0.035: 1106, 0.040: 1195}
REACH = 2.0
MIN_PAIRS = 300
HEREDITY_FLOOR = 0.35
TOL_SURVIVAL = 0.01
TOL_SIBLING = 0.05
BOOTSTRAP = 2000


def boot(vals, seed, stat=None):
    """Bootstrap interval for the statistic that is actually quoted, not for its cousin."""
    if len(vals) < 5:
        return None
    stat = stat or st.mean
    rng = random.Random(seed)
    means = sorted(stat([rng.choice(vals) for _ in range(len(vals))]) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def descendants(kids, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def cell_stats(flow: float, series, seed: int) -> dict:
    pairs = 0
    d0s, merged_d0s, unmerged_d0s, times = [], [], [], []
    merged = censored = 0
    sibling_absorptions = 0
    heredity = []
    surv_diff = []
    pair_count = 0
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        parent = {int(c): int(p) for c, p in w["parent"].items()}
        kids: dict[int, list[int]] = {}
        for child, par in parent.items():
            kids.setdefault(par, []).append(child)
        first = {int(u): int(v.get("step", 0)) for u, v in w["first"].items()}
        steps = sorted(int(s) for s in w["per_step"])
        last_step = steps[-1] if steps else 0
        # last appearance and last centroid per uid
        last_step_of: dict[int, int] = {}
        last_pos: dict[int, tuple[int, float, float, float]] = {}
        first_area: dict[int, float] = {}
        for t in steps:
            for c in (w["per_step"].get(t) or []):
                u = int(c["uid"])
                last_step_of[u] = t
                last_pos[u] = (t, float(c.get("cx", 0)), float(c.get("cy", 0)), float(c["area"]))
                first_area.setdefault(u, float(c["area"]))

        memo: dict[int, list[int]] = {}

        # control 1: X128b's sibling-absorption census, same local budget and partner rule
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            survivors = set(cur) & set(nxt)
            for uid, comp in cur.items():
                if uid in nxt or kids.get(uid):
                    continue
                dead_area = float(comp["area"]) or 1.0
                cx, cy = float(comp.get("cx", 0)), float(comp.get("cy", 0))
                rad = math.sqrt(dead_area / math.pi)
                near = [u for u in survivors
                        if math.hypot(float(nxt[u].get("cx", 0)) - cx, float(nxt[u].get("cy", 0)) - cy)
                        <= rad + math.sqrt(float(nxt[u]["area"]) / math.pi) + REACH]
                if not near:
                    continue
                local_growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near)
                if local_growth / dead_area < 0.50:
                    continue
                gains = {u: float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near}
                positive = {u: g for u, g in gains.items() if g > 1e-9}
                total_pos = sum(positive.values())
                if not positive or total_pos <= 0:
                    continue
                absorber = max(positive, key=positive.get)
                if positive[absorber] / total_pos < 0.50:
                    continue
                if parent.get(absorber) is not None and parent.get(uid) is not None \
                        and parent.get(absorber) == parent.get(uid):
                    sibling_absorptions += 1

        def sub(u: int) -> list[int]:
            if u not in memo:
                memo[u] = descendants(kids, u)
            return memo[u]

        for mother, daughters in kids.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    pair_count += 1
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    alive_big = any(last_step_of.get(u) == last_step for u in sub(big))
                    alive_small = any(last_step_of.get(u) == last_step for u in sub(small))
                    surv_diff.append(int(alive_big) - int(alive_small))
                    # birth separation
                    pa = next((c for c in (w["per_step"].get(first.get(a, -1)) or []) if int(c["uid"]) == a), None)
                    pb = next((c for c in (w["per_step"].get(first.get(b, -1)) or []) if int(c["uid"]) == b), None)
                    if pa is None or pb is None:
                        continue
                    d0 = math.hypot(float(pa.get("cx", 0)) - float(pb.get("cx", 0)),
                                    float(pa.get("cy", 0)) - float(pb.get("cy", 0)))
                    pairs += 1
                    d0s.append(d0)
                    # does one daughter's uid end into the other's subtree inside the run?
                    event = None
                    for dead, other in ((a, b), (b, a)):
                        if dead not in last_pos:
                            continue
                        t_end, cx, cy, area = last_pos[dead]
                        if t_end >= last_step:
                            continue          # still present at the end: censored
                        if kids.get(dead):
                            continue          # ended by dividing, not by absorption
                        o = last_pos.get(other)
                        if o is None:
                            continue
                        t_o, ox, oy, oarea = o
                        if t_o < t_end:
                            continue          # the other is already gone
                        d = math.hypot(ox - cx, oy - cy)
                        if d <= math.sqrt(area / math.pi) + math.sqrt(oarea / math.pi) + REACH:
                            tb = min(first.get(a, t_end), first.get(b, t_end))
                            event = t_end - tb
                            break
                    if event is None:
                        censored += 1
                        unmerged_d0s.append(d0)
                    else:
                        merged += 1
                        merged_d0s.append(d0)
                        times.append(event)

    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "pairs": pairs,
        "merged": merged,
        "censored": censored,
        "merge_share": round(merged / pairs, 4) if pairs else None,
        "merge_share_ci": boot([1.0] * merged + [0.0] * (pairs - merged), seed) if pairs else None,
        "censoring_share": round(censored / pairs, 4) if pairs else None,
        "sibling_absorptions": sibling_absorptions,
        "median_d0": round(st.median(d0s), 2) if d0s else None,
        "median_d0_merged": round(st.median(merged_d0s), 2) if merged_d0s else None,
        "median_d0_unmerged": round(st.median(unmerged_d0s), 2) if unmerged_d0s else None,
        "median_time": round(st.median(times), 1) if times else None,
        "median_time_ci": boot(times, seed + 1, stat=st.median) if times else None,
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "survival_pairs": pair_count,
        "survival_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "refs": {"survival": KNOWN_SURVIVAL[flow], "sister_pairs": KNOWN_PAIRS[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X130 sister re-merge")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {spec["tag"]: cell_stats(spec["flow"], spec["series"], seed=1300 + 10 * i)
             for i, spec in enumerate(CELLS)}
    for spec in CELLS:
        cells[spec["tag"]]["sibling_absorptions_x128b"] = spec["sibling_absorptions"]

    bad = []
    for tag, c in cells.items():
        ref = c["refs"]
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} usable sister pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["survival_mean"] is None or abs(c["survival_mean"] - ref["survival"]) > TOL_SURVIVAL:
            bad.append(f"{tag}: end-survival {c['survival_mean']} misses X126's {ref['survival']}")
        if c["survival_pairs"] != ref["sister_pairs"]:
            bad.append(f"{tag}: {c['survival_pairs']} pairs against X126's {ref['sister_pairs']}")
        if c["sibling_absorptions"] != c["sibling_absorptions_x128b"]:
            bad.append(f"{tag}: {c['sibling_absorptions']} sibling absorptions against X128b's {c['sibling_absorptions_x128b']}")

    lat, mid, maz = cells["f030"], cells["f035"], cells["f040"]
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif (lat["merge_share"] or 0) > 0.50:
        verdict = (f"sisters merge back: {lat['merge_share']:.1%} of {lat['pairs']} lattice sister pairs re-merge inside the run "
                   f"(CI {lat['merge_share_ci']}), median {lat['median_time']} steps after the split, and the censoring share is "
                   f"{lat['censoring_share']:.1%}; the daughters' birth separation is {lat['median_d0_merged']} cells among merged pairs "
                   f"against {lat['median_d0_unmerged']} among the rest, and in the maze the same statistics are {maz['merge_share']:.1%} "
                   f"of {maz['pairs']} with a median of {maz['median_time']} steps (censoring {maz['censoring_share']:.1%})")
    elif (lat["merge_share"] or 0) < 0.25:
        verdict = (f"sisters separate: only {lat['merge_share']:.1%} of {lat['pairs']} lattice sister pairs re-merge (CI "
                   f"{lat['merge_share_ci']}), so the lattice's 54.6 % sibling absorption comes from a minority of families and the "
                   f"median censoring share is {lat['censoring_share']:.1%}")
    else:
        verdict = (f"partial: {lat['merge_share']:.1%} of {lat['pairs']} lattice sister pairs re-merge (CI {lat['merge_share_ci']}, "
                   f"censoring {lat['censoring_share']:.1%}) with a median of {lat['median_time']} steps, against {maz['merge_share']:.1%} "
                   f"in the maze (censoring {maz['censoring_share']:.1%}); median birth separation {lat['median_d0']} / {mid['median_d0']} / "
                   f"{maz['median_d0']} cells")

    res = {
        "kind": "l1_field_x130_remerge",
        "experiment": "X130",
        "command": "python scripts/x130_analyse.py --write",
        "prereg": "reports/2026-11-03-x130-remerge-plan.md",
        "definitions": {
            "birth_separation": "centroid distance between two sister uids at their first logged step",
            "re_merge": f"one sister's uid ends without daughters while the other is present within r_dead + r_other + {REACH} cells of its last centroid",
            "censoring": "no re-merge inside the run; reported next to the merge share because it cannot distinguish never from not yet",
        },
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x130] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} merged={c['merged']} share={c['merge_share']} {c['merge_share_ci']} "
              f"censored={c['censoring_share']} d0={c['median_d0']} (merged {c['median_d0_merged']} / rest {c['median_d0_unmerged']}) "
              f"time={c['median_time']} {c['median_time_ci']} heredity={c['rho_heredity']} pairs_all={c['survival_pairs']} "
              f"surv={c['survival_mean']} x128b_siblings={c['sibling_absorptions_x128b']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
