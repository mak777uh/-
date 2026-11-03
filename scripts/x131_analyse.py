"""x131_analyse.py — X131: per-world values, then a bootstrap over WORLDS rather than over pairs.

Every interval this block published was bootstrapped inside ten worlds. This computes each statistic per world, resamples the ten worlds, and compares the
world-level interval with the published value, so the report can say which cell differences are properties of the habitat and which belong to these ten seeds.

Plan: reports/2026-11-03-x131-worlds-plan.md.

    python scripts/x131_analyse.py --write
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
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x131_worlds.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",)},
    {"tag": "f035", "flow": 0.035, "series": ("x126",)},
    {"tag": "f040", "flow": 0.040, "series": ("x108",)},
]
PUBLISHED = {
    ("f030", "absorbed"): 0.5534, ("f035", "absorbed"): 0.4775, ("f040", "absorbed"): 0.4837,
    ("f030", "isolated"): 0.3130, ("f035", "isolated"): 0.2938, ("f040", "isolated"): 0.2123,
    ("f030", "vanished"): 0.1050, ("f035", "vanished"): 0.2168, ("f040", "vanished"): 0.2740,
    ("f030", "kin"): 0.8724, ("f035", "kin"): 0.3921, ("f040", "kin"): 0.3766,
    ("f030", "remerge"): 0.1839, ("f035", "remerge"): 0.0859, ("f040", "remerge"): 0.1741,
    ("f030", "survival"): 0.2496, ("f035", "survival"): 0.2984, ("f040", "survival"): 0.1372,
    ("f030", "depth"): 1.479, ("f035", "depth"): 1.416, ("f040", "depth"): 2.213,
}
STATS = ("absorbed", "isolated", "vanished", "kin", "remerge", "survival", "depth")
ABSORBED_AT = 0.50
VANISHED_AT = 0.10
PARTNER_SHARE = 0.50
REACH = 2.0
TOL_PUBLISHED = 0.005
MIN_WORLDS = 8
BOOTSTRAP = 2000


def boot(vals, seed, stat=st.mean):
    if len(vals) < 3:
        return None
    rng = random.Random(seed)
    draws = sorted(stat([rng.choice(vals) for _ in range(len(vals))]) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(draws) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(draws) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(draws[lo], 4), round(draws[hi], 4)]


def descendants(kids, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def depth_of(kids, uid, memo):
    if uid in memo:
        return memo[uid]
    k = kids.get(uid, [])
    memo[uid] = 0 if not k else 1 + max(depth_of(kids, x, memo) for x in k)
    return memo[uid]


def chain(parent, uid, depth=3):
    out = [uid]
    for _ in range(depth):
        p = parent.get(out[-1])
        if p is None or p in out:
            break
        out.append(p)
    return out


def kin_class(parent, dead, absorber):
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


def world_stats(path, flow: float) -> dict:
    w = world_data(path)
    parent = {int(c): int(p) for c, p in w["parent"].items()}
    kids: dict[int, list[int]] = {}
    for child, par in parent.items():
        kids.setdefault(par, []).append(child)
    first = {int(u): int(v.get("step", 0)) for u, v in w["first"].items()}
    steps = sorted(int(s) for s in w["per_step"])
    last_step = steps[-1]
    last_step_of: dict[int, int] = {}
    last_pos: dict[int, tuple[int, float, float, float]] = {}
    for t in steps:
        for c in (w["per_step"].get(t) or []):
            u = int(c["uid"])
            last_step_of[u] = t
            last_pos[u] = (t, float(c.get("cx", 0)), float(c.get("cy", 0)), float(c["area"]))
    present_uid = {u for u, t in last_step_of.items() if t == last_step}

    fates = {"absorbed": 0, "isolated": 0, "vanished": 0, "unclear": 0}
    kin_ok = kin_all = 0
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
                fates["isolated"] += 1
                continue
            local = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near)
            ratio = local / dead_area
            if ratio >= ABSORBED_AT:
                fates["absorbed"] += 1
                gains = {u: float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near}
                positive = {u: g for u, g in gains.items() if g > 1e-9}
                tot = sum(positive.values())
                if positive and tot > 0:
                    absorber = max(positive, key=positive.get)
                    if positive[absorber] / tot >= PARTNER_SHARE:
                        kin_all += 1
                        if kin_class(parent, uid, absorber) != "unrelated":
                            kin_ok += 1
            elif ratio <= VANISHED_AT:
                fates["vanished"] += 1
            else:
                fates["unclear"] += 1

    memo: dict[int, int] = {}
    sub_memo: dict[int, list[int]] = {}

    def sub(u):
        if u not in sub_memo:
            sub_memo[u] = descendants(kids, u)
        return sub_memo[u]

    surv, depths = [], []
    merged = pairs = 0
    for mother, daughters in kids.items():
        if len(daughters) < 2:
            continue
        ds = [d for d in daughters if d in w["peak"]]
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                a, b = ds[i], ds[j]
                big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                alive_big = any(u in present_uid for u in sub(big))
                alive_small = any(u in present_uid for u in sub(small))
                surv.append(int(alive_big) - int(alive_small))
                depths.append(depth_of(kids, big, memo) - depth_of(kids, small, memo))
                pairs += 1
                # X130's clock, faithfully: one sister's uid ends into the other's reach inside the run
                event = False
                for dead, other in ((a, b), (b, a)):
                    if dead not in last_pos:
                        continue
                    t_end, cx, cy, area = last_pos[dead]
                    if t_end >= last_step or kids.get(dead):
                        continue
                    o = last_pos.get(other)
                    if o is None or o[0] < t_end:
                        continue
                    if math.hypot(o[1] - cx, o[2] - cy) <= math.sqrt(area / math.pi) + math.sqrt(o[3] / math.pi) + REACH:
                        event = True
                        break
                if event:
                    merged += 1

    n = max(1, sum(fates.values()))
    return {
        "world": Path(path).name,
        # ratios for the world-level bootstrap, counts for the pooled check
        "absorbed": fates["absorbed"] / n, "absorbed_n": fates["absorbed"], "deaths": sum(fates.values()),
        "isolated": fates["isolated"] / n, "isolated_n": fates["isolated"],
        "vanished": fates["vanished"] / n, "vanished_n": fates["vanished"],
        "kin": (kin_ok / kin_all) if kin_all else None, "kin_n": kin_ok, "kin_den": kin_all,
        "remerge": (merged / pairs) if pairs else None, "remerge_n": merged, "pairs": pairs,
        "survival": st.mean(surv) if surv else None, "survival_sum": sum(surv), "survival_den": len(surv),
        "depth": st.mean(depths) if depths else None, "depth_sum": sum(depths), "depth_den": len(depths),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X131 world-level uncertainty")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    per_world = {}
    for spec in CELLS:
        per_world[spec["tag"]] = [world_stats(p, spec["flow"])
                                  for p in cell_files(spec["series"], spec["flow"], filename="")]

    NUM = {"absorbed": ("absorbed_n", "deaths"), "isolated": ("isolated_n", "deaths"), "vanished": ("vanished_n", "deaths"),
           "kin": ("kin_n", "kin_den"), "remerge": ("remerge_n", "pairs"), "survival": ("survival_sum", "survival_den"),
           "depth": ("depth_sum", "depth_den")}
    out = {}
    bad = []
    for tag, rows in per_world.items():
        cell = {}
        for k, stat in enumerate(STATS):
            vals = [r[stat] for r in rows if r.get(stat) is not None]
            if len(vals) < MIN_WORLDS:
                cell[stat] = {"worlds": len(vals), "unavailable": True}
                continue
            num_k, den_k = NUM[stat]
            pooled_num = sum(r.get(num_k, 0) or 0 for r in rows)
            pooled_den = sum(r.get(den_k, 0) or 0 for r in rows)
            pooled_here = (pooled_num / pooled_den) if pooled_den else None
            ci = boot(vals, 1310 + k)
            published = PUBLISHED.get((tag, stat))
            cell[stat] = {
                "worlds": len(vals),
                "values": [round(v, 4) for v in vals],
                "world_mean": round(st.mean(vals), 4),
                "sd_across_worlds": round(st.stdev(vals), 4) if len(vals) > 1 else None,
                "world_ci": ci,
                "world_width": round(ci[1] - ci[0], 4) if ci else None,
                "pooled_recomputed": round(pooled_here, 4) if pooled_here is not None else None,
                "published": published,
                "pooled_gap": round(pooled_here - published, 4) if (pooled_here is not None and published is not None) else None,
                "weighting_gap": round(st.mean(vals) - pooled_here, 4) if pooled_here is not None else None,
            }
            if published is not None and (pooled_here is None or abs(pooled_here - published) > TOL_PUBLISHED):
                bad.append(f"{tag}/{stat}: pooled {pooled_here} misses the published {published}")
        out[tag] = cell

    # paired across seeds: the three cells use seeds 301-310, so the correct world-level test of a
    # difference is the per-seed difference, not the overlap of two marginal intervals.
    def by_seed(rows):
        out = {}
        for r in rows:
            name = r["world"]
            seed = name.split("_s")[-1].replace(".json", "")
            out[seed] = r
        return out

    seeds = sorted(set.intersection(*[set(by_seed(rows)) for rows in per_world.values()]))
    paired = {}
    for stat in STATS:
        entry = {}
        for a, b in (("f030", "f040"), ("f030", "f035"), ("f035", "f040")):
            ra, rb = by_seed(per_world[a]), by_seed(per_world[b])
            diffs = [rb[s][stat] - ra[s][stat] for s in seeds
                     if rb[s].get(stat) is not None and ra[s].get(stat) is not None]
            if len(diffs) < MIN_WORLDS:
                entry[f"{b}_minus_{a}"] = {"seeds": len(diffs), "unavailable": True}
                continue
            ci = boot(diffs, 1320 + len(diffs))
            entry[f"{b}_minus_{a}"] = {
                "seeds": len(diffs),
                "mean": round(st.mean(diffs), 4),
                "ci": ci,
                "excludes_zero": bool(ci and (ci[0] > 0 or ci[1] < 0)),
                "per_seed": [round(d, 4) for d in diffs],
            }
        paired[stat] = entry

    res = {
        "kind": "l1_field_x131_worlds",
        "experiment": "X131",
        "command": "python scripts/x131_analyse.py --write",
        "prereg": "reports/2026-11-03-x131-worlds-plan.md",
        "note": "per-world values of six statistics; the world-level interval is the bootstrap over the ten worlds of each cell",
        "cells": out,
        "per_world": per_world,
        "paired_by_seed": paired,
    }
    verdict = ("void: " + "; ".join(bad)) if bad else "per-world values computed for every statistic and every world"
    res["verdict"] = verdict
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x131] written: {OUT.name}")
    for tag, cell in out.items():
        for stat, c in cell.items():
            if c.get("unavailable"):
                print(f"  {tag} {stat}: unavailable ({c['worlds']} worlds)")
                continue
            print(f"  {tag} {stat}: pooled={c['pooled_recomputed']} world_mean={c['world_mean']} "
                  f"sd={c['sd_across_worlds']} world_ci={c['world_ci']} published={c['published']}")
    print("  paired by seed (world-level test of each difference):")
    for stat, entry in paired.items():
        for k, v in entry.items():
            if v.get("unavailable"):
                print(f"    {stat} {k}: unavailable ({v['seeds']} seeds)")
            else:
                print(f"    {stat} {k}: mean={v['mean']} ci={v['ci']} excludes_zero={v['excludes_zero']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
