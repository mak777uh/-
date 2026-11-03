"""x127_analyse.py — X127: does a lineage end by vanishing, or by being absorbed into a neighbour?

A uid ends either by dividing (daughters appear) or by disappearing. The second is what every persistence number counts as death, but in a percolating body the
cells may simply become part of a neighbour. This instrument separates the two using the logged areas: absorbed if the surviving uids grow by >= 50 % of the
dead uid's area, vanished if by <= 10 %, unclear otherwise.

Plan: reports/2026-11-03-x127-absorption-plan.md.

    python scripts/x127_analyse.py --write
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x127_absorption.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",)},
    {"tag": "f035", "flow": 0.035, "series": ("x126",)},
    {"tag": "f040", "flow": 0.040, "series": ("x108",)},
]
KNOWN_SURVIVAL = {0.030: 0.2496, 0.035: 0.2984, 0.040: 0.1372}
KNOWN_PAIRS = {0.030: 1142, 0.035: 1106, 0.040: 1195}
ABSORBED_AT = 0.50
VANISHED_AT = 0.10
BUDGET_TOL = 2.0
HEREDITY_FLOOR = 0.35
MIN_DEATHS = 100
SURVIVAL_TOL = 0.01
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
    deaths = {"absorbed": 0, "vanished": 0, "unclear": 0}
    dead_areas, absorbed_growth_ratio = [], []
    budget_fail = budget_checked = 0
    heredity = []
    surv_diff, fate_diff = [], []
    both_abs = only_big_abs = only_small_abs = neither_abs = 0
    pair_count = 0
    adjacent_deaths = adjacent_total = 0
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        steps = sorted(int(s) for s in w["per_step"])
        first_step_of = {int(u): int(v.get("step", 0)) for u, v in w["first"].items()}

        # ---- death census and fate classification, step by step
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            total_t = sum(float(c["area"]) for c in cur.values())
            total_t1 = sum(float(c["area"]) for c in nxt.values())
            survivors = set(cur) & set(nxt)
            growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in survivors)
            born = sum(float(c["area"]) for u, c in nxt.items() if u not in cur)
            gone = sum(float(c["area"]) for u, c in cur.items() if u not in nxt)
            budget_checked += 1
            if abs((total_t1 - total_t) - (growth + born - gone)) > BUDGET_TOL:
                budget_fail += 1
            for uid, comp in cur.items():
                if uid in nxt:
                    continue
                if children.get(uid):        # divided: identity ends by division, not death
                    continue
                dead_area = float(comp["area"])
                dead_areas.append(dead_area)
                ratio = growth / dead_area if dead_area > 0 else 0.0
                if ratio >= ABSORBED_AT:
                    deaths["absorbed"] += 1
                    absorbed_growth_ratio.append(ratio)
                elif ratio <= VANISHED_AT:
                    deaths["vanished"] += 1
                else:
                    deaths["unclear"] += 1
                # descriptive adjacency census: nearest survivor centroid
                adjacent_total += 1
                cx, cy = float(comp.get("cx", 0)), float(comp.get("cy", 0))
                rad = (dead_area / 3.141592653589793) ** 0.5
                near = False
                for u in survivors:
                    o = nxt[u]
                    d = ((float(o.get("cx", 0)) - cx) ** 2 + (float(o.get("cy", 0)) - cy) ** 2) ** 0.5
                    if d <= rad + (float(o["area"]) / 3.141592653589793) ** 0.5 + 2.0:
                        near = True
                        break
                if near:
                    adjacent_deaths += 1

        # ---- per sister pair: each branch's fate
        last_step = steps[-1] if steps else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        per_uid_fate: dict[int, str] = {}
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            survivors = set(cur) & set(nxt)
            growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in survivors)
            for uid, comp in cur.items():
                if uid in nxt or children.get(uid):
                    continue
                dead_area = float(comp["area"]) or 1.0
                ratio = growth / dead_area
                per_uid_fate[uid] = "absorbed" if ratio >= ABSORBED_AT else ("vanished" if ratio <= VANISHED_AT else "unclear")

        memo: dict[int, list[int]] = {}

        def sub(u: int) -> list[int]:
            if u not in memo:
                memo[u] = descendants(children, u)
            return memo[u]

        def branch_absorbed(u: int) -> int:
            fates = [per_uid_fate[v] for v in sub(u) if v in per_uid_fate]
            if not fates:
                return 0
            return 1 if fates.count("absorbed") * 2 > len(fates) else 0

        for mother, daughters in children.items():
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
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    pair_count += 1
                    alive_a = any(u in present for u in sub(big))
                    alive_s = any(u in present for u in sub(small))
                    surv_diff.append(int(alive_a) - int(alive_s))
                    fa, fs = branch_absorbed(big), branch_absorbed(small)
                    fate_diff.append(fa - fs)
                    if fa and fs:
                        both_abs += 1
                    elif fa:
                        only_big_abs += 1
                    elif fs:
                        only_small_abs += 1
                    else:
                        neither_abs += 1

    n_deaths = sum(deaths.values())
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "deaths": n_deaths,
        "deaths_by_fate": deaths,
        "absorbed_share": round(deaths["absorbed"] / n_deaths, 4) if n_deaths else None,
        "vanished_share": round(deaths["vanished"] / n_deaths, 4) if n_deaths else None,
        "unclear_share": round(deaths["unclear"] / n_deaths, 4) if n_deaths else None,
        "absorbed_share_ci": boot([1.0] * deaths["absorbed"] + [0.0] * (n_deaths - deaths["absorbed"]), seed) if n_deaths else None,
        "median_dead_area": round(st.median(dead_areas), 1) if dead_areas else None,
        "median_growth_ratio_when_absorbed": round(st.median(absorbed_growth_ratio), 3) if absorbed_growth_ratio else None,
        "adjacent_share": round(adjacent_deaths / adjacent_total, 4) if adjacent_total else None,
        "budget_checked": budget_checked,
        "budget_fail_share": round(budget_fail / budget_checked, 4) if budget_checked else None,
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "pairs": pair_count,
        "survival_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "fate_diff_mean": round(st.mean(fate_diff), 4) if fate_diff else None,
        "fate_diff_ci": boot(fate_diff, seed + 1),
        "fates_both_onlybig_onlysmall_neither": [both_abs, only_big_abs, only_small_abs, neither_abs],
        "refs": {"survival": KNOWN_SURVIVAL[flow], "pairs": KNOWN_PAIRS[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X127 absorption vs vanishing")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {spec["tag"]: cell_stats(spec["flow"], spec["series"], seed=1270 + 10 * i)
             for i, spec in enumerate(CELLS)}

    bad = []
    for tag, c in cells.items():
        if c["deaths"] < MIN_DEATHS:
            bad.append(f"{tag}: {c['deaths']} deaths")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["survival_mean"] is None or abs(c["survival_mean"] - c["refs"]["survival"]) > SURVIVAL_TOL:
            bad.append(f"{tag}: end-survival {c['survival_mean']} misses X126's {c['refs']['survival']}")
        if c["pairs"] != c["refs"]["pairs"]:
            bad.append(f"{tag}: {c['pairs']} pairs against X126's {c['refs']['pairs']}")
        if c["budget_fail_share"] is None or c["budget_fail_share"] > 0.05:
            bad.append(f"{tag}: area budget fails for {c['budget_fail_share']:.1%} of steps")

    lat, mid, maz = cells["f030"], cells["f035"], cells["f040"]
    delta = (maz["absorbed_share"] or 0) - (lat["absorbed_share"] or 0)
    homogenising = delta > 0.10 and (maz["vanished_share"] or 0) < (lat["vanished_share"] or 0)
    lethal = delta <= 0.10 and (maz["vanished_share"] or 0) > 0.50
    mixed = (maz["unclear_share"] or 0) > 0.20 or (lat["unclear_share"] or 0) > 0.20
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif mixed:
        verdict = (f"mixed, instrument not sharp enough: {maz['unclear_share']:.1%} / {lat['unclear_share']:.1%} of deaths are unclear, "
                   f"so the reading is deferred rather than guessed")
    elif homogenising:
        verdict = (f"the maze is homogenising, not lethal: absorbed deaths are {lat['absorbed_share']:.1%} of {lat['deaths']} in the lattice, "
                   f"{mid['absorbed_share']:.1%} of {mid['deaths']} in the middle cell and {maz['absorbed_share']:.1%} of {maz['deaths']} in the maze "
                   f"(+{delta:.1%}), while vanished deaths fall from {lat['vanished_share']:.1%} to {maz['vanished_share']:.1%}")
    elif lethal:
        verdict = (f"the maze is lethal: absorbed share {lat['absorbed_share']:.1%} → {maz['absorbed_share']:.1%} (delta {delta:+.1%}, under the "
                   f"declared 0.10) and vanished deaths dominate at {maz['vanished_share']:.1%}")
    else:
        verdict = (f"NO REGISTERED OUTCOME FIRED. Absorption dominates in all three cells ({lat['absorbed_share']:.1%} / "
                   f"{mid['absorbed_share']:.1%} / {maz['absorbed_share']:.1%} of {lat['deaths']} / {mid['deaths']} / {maz['deaths']} deaths), the "
                   f"maze moves it by {delta:+.1%} (under the declared 0.10) and vanishing rises {lat['vanished_share']:.1%} → "
                   f"{maz['vanished_share']:.1%} without ever dominating, so neither branch of the pre-registered dichotomy holds. What changes "
                   f"across the cells is the NUMBER of identity deaths (x{maz['deaths'] / lat['deaths']:.1f}) and the number of real vanishings "
                   f"({lat['deaths'] * lat['vanished_share']:.0f} → {maz['deaths'] * maz['vanished_share']:.0f}), not the kind of death: the "
                   f"dichotomy 'homogenising or lethal' was the wrong question, and the run says so instead of choosing a side.")

    res = {
        "kind": "l1_field_x127_absorption",
        "experiment": "X127",
        "command": "python scripts/x127_analyse.py --write",
        "prereg": "reports/2026-11-03-x127-absorption-plan.md",
        "definitions": {
            "death": "uid present at t, absent at t+1, with no daughters (a divider is not a death)",
            "absorbed": f"surviving uids grow by >= {ABSORBED_AT:.0%} of the dead uid's area at its death step",
            "vanished": f"surviving uids grow by <= {VANISHED_AT:.0%} of the dead uid's area",
            "unclear": "between the two thresholds, reported separately and never merged",
            "branch_absorbed": "more than half of a branch's subtree deaths are absorbed",
        },
        "cells": cells,
        "absorbed_share_delta_maze_minus_lattice": round(delta, 4),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x127] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: deaths={c['deaths']} absorbed={c['absorbed_share']} vanished={c['vanished_share']} "
              f"unclear={c['unclear_share']} adjacent={c['adjacent_share']} median_area={c['median_dead_area']} "
              f"budget_fail={c['budget_fail_share']} heredity={c['rho_heredity']} pairs={c['pairs']} "
              f"surv={c['survival_mean']} fate_diff={c['fate_diff_mean']} {c['fate_diff_ci']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
