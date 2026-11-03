"""x128_analyse.py — X128: when a lineage loses its name, do its cells go to kin?

X127 showed that 75-85 % of a lineage's deaths are absorptions. This asks who takes the cells: the survivor whose area grew most, provided it accounts for at
least half of the total survivor growth; otherwise the absorption is 'diffuse' and no partner is invented. Relatedness is read from the genealogy in the same
logs, three generations deep.

Plan: reports/2026-11-03-x128-kinship-plan.md.

    python scripts/x128_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x128_kinship.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",)},
    {"tag": "f035", "flow": 0.035, "series": ("x126",)},
    {"tag": "f040", "flow": 0.040, "series": ("x108",)},
]
KNOWN_ABSORBED = {0.030: 0.8454, 0.035: 0.7867, 0.040: 0.7568}
KNOWN_SURVIVAL = {0.030: 0.2496, 0.035: 0.2984, 0.040: 0.1372}
KNOWN_PAIRS = {0.030: 1142, 0.035: 1106, 0.040: 1195}
ABSORBED_AT = 0.50
PARTNER_SHARE = 0.50
MIN_PARTNERED = 100
PARTNER_COVERAGE_FLOOR = 0.80
MAX_DIFFUSE = 0.20
HEREDITY_FLOOR = 0.35
TOL_ABSORBED = 0.01
TOL_SURVIVAL = 0.01
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


def descendants(children: dict[int, list[int]], uid: int) -> list[int]:
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
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
    classes = {"sibling": 0, "aunt": 0, "cousin": 0, "distant": 0, "unrelated": 0, "diffuse": 0}
    absorbed_total = deaths_total = 0
    ages, absorber_areas = [], []
    heredity = []
    surv_diff = []
    pair_count = 0
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        parent = {int(c): int(p) for c, p in w["parent"].items()}
        children: dict[int, list[int]] = {}
        for child, par in parent.items():
            children.setdefault(par, []).append(child)
        birth = {int(u): int(v.get("step", 0)) for u, v in w["first"].items()}
        steps = sorted(int(s) for s in w["per_step"])
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            survivors = set(cur) & set(nxt)
            growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in survivors)
            if growth <= 0:
                continue
            for uid, comp in cur.items():
                if uid in nxt or children.get(uid):
                    continue
                deaths_total += 1
                dead_area = float(comp["area"]) or 1.0
                if growth / dead_area < ABSORBED_AT:
                    continue
                absorbed_total += 1
                gains = {u: float(nxt[u]["area"]) - float(cur[u]["area"]) for u in survivors}
                positive = {u: g for u, g in gains.items() if g > 1e-9}
                total_pos = sum(positive.values())
                if not positive or total_pos <= 0:
                    classes["diffuse"] += 1
                    continue
                absorber = max(positive, key=positive.get)
                if positive[absorber] / total_pos < PARTNER_SHARE:
                    classes["diffuse"] += 1
                    continue
                classes[kin_class(parent, uid, absorber)] += 1
                ages.append(t - birth.get(uid, t) + 1)
                absorber_areas.append(float(nxt[absorber]["area"]))

        last_step = steps[-1] if steps else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        memo: dict[int, list[int]] = {}

        def sub(u: int) -> list[int]:
            if u not in memo:
                memo[u] = descendants(children, u)
            return memo[u]

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
                    surv_diff.append(int(any(u in present for u in sub(big))) - int(any(u in present for u in sub(small))))

    partnered = sum(v for k, v in classes.items() if k != "diffuse")
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    kin = classes["sibling"] + classes["aunt"] + classes["cousin"] + classes["distant"]
    return {
        "deaths": deaths_total,
        "absorbed": absorbed_total,
        "absorbed_share": round(absorbed_total / deaths_total, 4) if deaths_total else None,
        "partnered": partnered,
        "partner_coverage": round(partnered / absorbed_total, 4) if absorbed_total else None,
        "classes": classes,
        "shares": {k: (round(v / partnered, 4) if partnered else None) for k, v in classes.items() if k != "diffuse"},
        "diffuse_share_of_absorbed": round(classes["diffuse"] / absorbed_total, 4) if absorbed_total else None,
        "kin_share": round(kin / partnered, 4) if partnered else None,
        "kin_share_ci": boot([1.0] * kin + [0.0] * (partnered - kin), seed) if partnered else None,
        "median_swallowed_age": round(st.median(ages), 1) if ages else None,
        "median_absorber_area": round(st.median(absorber_areas), 1) if absorber_areas else None,
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "pairs": pair_count,
        "survival_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "refs": {"absorbed": KNOWN_ABSORBED[flow], "survival": KNOWN_SURVIVAL[flow], "pairs": KNOWN_PAIRS[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X128 kinship of the absorber")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {spec["tag"]: cell_stats(spec["flow"], spec["series"], seed=1280 + 10 * i)
             for i, spec in enumerate(CELLS)}

    bad = []
    for tag, c in cells.items():
        ref = c["refs"]
        if c["partnered"] < MIN_PARTNERED:
            bad.append(f"{tag}: {c['partnered']} absorbed deaths with a partner")
        if c["partner_coverage"] is None or c["partner_coverage"] < PARTNER_COVERAGE_FLOOR:
            bad.append(f"{tag}: partner coverage {c['partner_coverage']}")
        if c["diffuse_share_of_absorbed"] is not None and c["diffuse_share_of_absorbed"] > MAX_DIFFUSE:
            bad.append(f"{tag}: diffuse share {c['diffuse_share_of_absorbed']}")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["absorbed_share"] is None or abs(c["absorbed_share"] - ref["absorbed"]) > TOL_ABSORBED:
            bad.append(f"{tag}: absorbed share {c['absorbed_share']} misses X127's {ref['absorbed']}")
        if c["survival_mean"] is None or abs(c["survival_mean"] - ref["survival"]) > TOL_SURVIVAL:
            bad.append(f"{tag}: end-survival {c['survival_mean']} misses X126's {ref['survival']}")
        if c["pairs"] != ref["pairs"]:
            bad.append(f"{tag}: {c['pairs']} pairs against X126's {ref['pairs']}")

    lat, mid, maz = cells["f030"], cells["f035"], cells["f040"]
    fam = all((c["kin_share"] or 0) > 0.50 for c in cells.values())
    strangers = [tag for tag, c in cells.items() if (c["shares"]["unrelated"] or 0) > 0.50]
    delta_unrel = (maz["shares"]["unrelated"] or 0) - (lat["shares"]["unrelated"] or 0)
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif fam:
        verdict = (f"continuity inside a family: kin account for {lat['kin_share']:.1%} (CI {lat['kin_share_ci']}) of the partnered absorptions in the "
                   f"lattice, {mid['kin_share']:.1%} in the middle cell and {maz['kin_share']:.1%} in the maze — a lineage's cells are usually taken by a "
                   f"sibling ({lat['shares']['sibling']:.1%} / {mid['shares']['sibling']:.1%} / {maz['shares']['sibling']:.1%}), so 'name loss' is a "
                   f"bookkeeping event inside a family, not a takeover")
    elif strangers:
        named = ", ".join(f"{t}: {cells[t]['shares']['unrelated']:.1%}" for t in strangers)
        verdict = (f"takeover by strangers in {named} of the partnered absorptions, "
                   f"against {lat['shares']['unrelated']:.1%} in the lattice")
    else:
        verdict = (f"mixed: unrelated absorbers are {lat['shares']['unrelated']:.1%} / {mid['shares']['unrelated']:.1%} / "
                   f"{maz['shares']['unrelated']:.1%} of the partnered absorptions (maze minus lattice {delta_unrel:+.1%}, declared 0.08), and kin "
                   f"{lat['kin_share']:.1%} / {mid['kin_share']:.1%} / {maz['kin_share']:.1%}")

    res = {
        "kind": "l1_field_x128_kinship",
        "experiment": "X128",
        "command": "python scripts/x128_analyse.py --write",
        "prereg": "reports/2026-11-03-x128-kinship-plan.md",
        "definitions": {
            "absorber": f"the survivor whose area grew most, provided it holds >= {PARTNER_SHARE:.0%} of the total positive survivor growth",
            "diffuse": "no survivor reaches that share, so no partner is named",
            "kinship": "read from parent links up to three generations: sibling, aunt, cousin, distant, unrelated",
        },
        "cells": cells,
        "unrelated_delta_maze_minus_lattice": round(delta_unrel, 4),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x128] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: absorbed={c['absorbed']} partnered={c['partnered']} ({c['partner_coverage']}) "
              f"kin={c['kin_share']} shares={c['shares']} diffuse={c['diffuse_share_of_absorbed']} "
              f"age={c['median_swallowed_age']} absorber_area={c['median_absorber_area']} "
              f"heredity={c['rho_heredity']} pairs={c['pairs']} surv={c['survival_mean']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
