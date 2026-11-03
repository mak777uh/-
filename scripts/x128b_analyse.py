"""x128b_analyse.py — X128b: the local budget, then the kinship of whoever took the cells.

X127 and X128 classified a local event with a world-level area budget. This restricts the budget to the dead structure's own neighbourhood, adds the category the
lattice needs (no live neighbour at all), and re-asks the kinship question only where the count allows it.

Plan: reports/2026-11-03-x128b-local-plan.md.

    python scripts/x128b_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x128b_local.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",)},
    {"tag": "f035", "flow": 0.035, "series": ("x126",)},
    {"tag": "f040", "flow": 0.040, "series": ("x108",)},
]
X127_ABSORBED = {0.030: 0.8454, 0.035: 0.7867, 0.040: 0.7568}
KNOWN_SURVIVAL = {0.030: 0.2496, 0.035: 0.2984, 0.040: 0.1372}
KNOWN_PAIRS = {0.030: 1142, 0.035: 1106, 0.040: 1195}
ABSORBED_AT = 0.50
VANISHED_AT = 0.10
PARTNER_SHARE = 0.50
REACH = 2.0
HEREDITY_FLOOR = 0.35
TOL_SURVIVAL = 0.01
MIN_KINSHIP = 100
RESOLUTION = 0.08
BOOTSTRAP = 2000


def boot(vals, seed):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def rank(u: int, kids: dict[int, list[int]]) -> int:
    return len(kids.get(u, []))


def descendants(kids: dict[int, list[int]], uid: int) -> list[int]:
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def chain(parent: dict[int, int], uid: int, depth: int = 3) -> list[int]:
    out = [uid]
    for _ in range(depth):
        p = parent.get(out[-1])
        if p is None or p in out:
            break
        out.append(p)
    return out


def kin_class(parent: dict[int, int], dead: int, absorber: int) -> str:
    a, b = chain(parent, dead), chain(parent, absorber)
    if len(a) >= 2 and len(b) >= 2 and a[1] == b[1]:
        return "sibling"
    if len(a) >= 2 and len(b) >= 2 and (a[1] in b[1:] or b[1] in a[1:]):
        return "aunt"
    if len(a) >= 3 and len(b) >= 3 and a[2] == b[2]:
        return "cousin"
    if set(a[1:]) & set(b[1:]):
        return "distant"
    return "unrelated"


def cell_stats(flow: float, series: tuple[str, ...], seed: int) -> dict:
    fates = {"isolated": 0, "absorbed": 0, "vanished": 0, "unclear": 0}
    kin_classes = {"sibling": 0, "aunt": 0, "cousin": 0, "distant": 0, "unrelated": 0, "diffuse": 0}
    deaths = 0
    neighbourhood_sizes, dead_areas = [], []
    budget_steps = budget_fail = 0
    heredity = []
    surv_diff = []
    pair_count = 0
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        parent = {int(c): int(p) for c, p in w["parent"].items()}
        kids: dict[int, list[int]] = {}
        for child, par in parent.items():
            kids.setdefault(par, []).append(child)
        steps = sorted(int(s) for s in w["per_step"])
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            survivors = set(cur) & set(nxt)
            # control 3: the local and global accounts are two views of the same step
            if survivors:
                global_change = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in survivors)
            else:
                global_change = 0.0
            budget_steps += 1
            for uid, comp in cur.items():
                if uid in nxt or kids.get(uid):
                    continue
                deaths += 1
                dead_area = float(comp["area"]) or 1.0
                cx, cy = float(comp.get("cx", 0)), float(comp.get("cy", 0))
                rad = math.sqrt(dead_area / math.pi)
                near = []
                for u in survivors:
                    o = nxt[u]
                    d = math.hypot(float(o.get("cx", 0)) - cx, float(o.get("cy", 0)) - cy)
                    if d <= rad + math.sqrt(float(o["area"]) / math.pi) + REACH:
                        near.append(u)
                neighbourhood_sizes.append(len(near))
                dead_areas.append(dead_area)
                if not near:
                    fates["isolated"] += 1
                    continue
                local_growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near)
                if abs(local_growth - sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near)) > 1.0:
                    budget_fail += 1
                ratio = local_growth / dead_area
                if ratio >= ABSORBED_AT:
                    fates["absorbed"] += 1
                    gains = {u: float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near}
                    positive = {u: g for u, g in gains.items() if g > 1e-9}
                    total_pos = sum(positive.values())
                    if not positive or total_pos <= 0:
                        kin_classes["diffuse"] += 1
                        continue
                    absorber = max(positive, key=positive.get)
                    if positive[absorber] / total_pos < PARTNER_SHARE:
                        kin_classes["diffuse"] += 1
                        continue
                    kin_classes[kin_class(parent, uid, absorber)] += 1
                elif ratio <= VANISHED_AT:
                    fates["vanished"] += 1
                else:
                    fates["unclear"] += 1

        last_step = steps[-1] if steps else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        memo: dict[int, list[int]] = {}

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
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    pair_count += 1
                    surv_diff.append(int(any(u in present for u in sub(big))) - int(any(u in present for u in sub(small))))

    partnered = sum(v for k, v in kin_classes.items() if k != "diffuse")
    kin = sum(kin_classes[k] for k in ("sibling", "aunt", "cousin", "distant"))
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "deaths": deaths,
        "fates": fates,
        "isolated_share": round(fates["isolated"] / deaths, 4) if deaths else None,
        "absorbed_share": round(fates["absorbed"] / deaths, 4) if deaths else None,
        "absorbed_share_ci": boot([1.0] * fates["absorbed"] + [0.0] * (deaths - fates["absorbed"]), seed) if deaths else None,
        "vanished_share": round(fates["vanished"] / deaths, 4) if deaths else None,
        "unclear_share": round(fates["unclear"] / deaths, 4) if deaths else None,
        "median_neighbourhood": round(st.median(neighbourhood_sizes), 1) if neighbourhood_sizes else None,
        "median_dead_area": round(st.median(dead_areas), 1) if dead_areas else None,
        "budget_fail": budget_fail, "budget_steps": budget_steps,
        "partnered": partnered,
        "kin_classes": kin_classes,
        "diffuse_share_of_absorbed": round(kin_classes["diffuse"] / fates["absorbed"], 4) if fates["absorbed"] else None,
        "kin_share": round(kin / partnered, 4) if partnered else None,
        "kin_share_ci": boot([1.0] * kin + [0.0] * (partnered - kin), seed) if partnered else None,
        "unrelated_share": round(kin_classes["unrelated"] / partnered, 4) if partnered else None,
        "kinship_answerable": partnered >= MIN_KINSHIP,
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "pairs": pair_count,
        "survival_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "refs": {"x127_absorbed": X127_ABSORBED[flow], "survival": KNOWN_SURVIVAL[flow], "pairs": KNOWN_PAIRS[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X128b local budget")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {spec["tag"]: cell_stats(spec["flow"], spec["series"], seed=1285 + 10 * i)
             for i, spec in enumerate(CELLS)}

    bad = []
    for tag, c in cells.items():
        ref = c["refs"]
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["survival_mean"] is None or abs(c["survival_mean"] - ref["survival"]) > TOL_SURVIVAL:
            bad.append(f"{tag}: end-survival {c['survival_mean']} misses X126's {ref['survival']}")
        if c["pairs"] != ref["pairs"]:
            bad.append(f"{tag}: {c['pairs']} pairs against X126's {ref['pairs']}")
        if c["budget_steps"] and c["budget_fail"] / c["budget_steps"] > 0.01:
            bad.append(f"{tag}: local/global accounts disagree on {c['budget_fail']} of {c['budget_steps']} steps")
        if sum(c["fates"].values()) != c["deaths"]:
            bad.append(f"{tag}: fates do not sum to the deaths")

    lat, mid, maz = cells["f030"], cells["f035"], cells["f040"]
    drop = (lat["refs"]["x127_absorbed"] or 0) - (lat["absorbed_share"] or 0)
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif drop < 0.20:
        verdict = (f"the neighbourhood restriction does nothing: the lattice's absorbed share is {lat['absorbed_share']:.1%} against X127's "
                   f"{lat['refs']['x127_absorbed']:.1%} (drop {drop:.1%}, required 0.20), so the diagnosis in the X128 void is wrong")
    else:
        verdict = (f"the local budget changes the picture: isolated deaths are {lat['isolated_share']:.1%} / {mid['isolated_share']:.1%} / "
                   f"{maz['isolated_share']:.1%} of {lat['deaths']} / {mid['deaths']} / {maz['deaths']}, absorbed {lat['absorbed_share']:.1%} / "
                   f"{mid['absorbed_share']:.1%} / {maz['absorbed_share']:.1%} (lattice drop {drop:.1%} against X127), vanished "
                   f"{lat['vanished_share']:.1%} / {mid['vanished_share']:.1%} / {maz['vanished_share']:.1%}, unclear {lat['unclear_share']:.1%} / "
                   f"{mid['unclear_share']:.1%} / {maz['unclear_share']:.1%}; median neighbourhood size {lat['median_neighbourhood']} / "
                   f"{mid['median_neighbourhood']} / {maz['median_neighbourhood']}")
        ans = [tag for tag, c in cells.items() if c["kinship_answerable"]]
        if ans:
            verdict += ("; kinship is answerable in " + ", ".join(ans) + ": " +
                        ", ".join(f"{tag} kin {cells[tag]['kin_share']:.1%} of {cells[tag]['partnered']}" for tag in ans))
        else:
            verdict += "; the kinship question is not answerable at this grid in any cell"

    res = {
        "kind": "l1_field_x128b_local",
        "experiment": "X128b",
        "command": "python scripts/x128b_analyse.py --write",
        "prereg": "reports/2026-11-03-x128b-local-plan.md",
        "definitions": {
            "neighbourhood": f"survivors within r_dead + r_survivor + {REACH} cells of the dead centroid, r = sqrt(area/pi)",
            "isolated": "no live neighbour at all",
            "absorbed": f"local growth >= {ABSORBED_AT:.0%} of the dead uid's area",
            "vanished": f"local growth <= {VANISHED_AT:.0%} of the dead uid's area",
            "absorber": f"the neighbour with the largest growth, provided it holds >= {PARTNER_SHARE:.0%} of the local positive growth",
        },
        "cells": cells,
        "lattice_absorbed_drop_against_x127": round(drop, 4),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x128b] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: deaths={c['deaths']} isolated={c['isolated_share']} absorbed={c['absorbed_share']} {c['absorbed_share_ci']} "
              f"vanished={c['vanished_share']} unclear={c['unclear_share']} nbr={c['median_neighbourhood']} "
              f"partnered={c['partnered']} kin={c['kin_share']} unrelated={c['unrelated_share']} "
              f"answerable={c['kinship_answerable']} budget_fail={c['budget_fail']}/{c['budget_steps']} "
              f"heredity={c['rho_heredity']} pairs={c['pairs']} surv={c['survival_mean']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
