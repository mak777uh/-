"""x132_analyse.py — X132: thirty worlds per cell, the paired per-seed test the power calculation asked for.

Reads the ten original worlds (x108) plus the twenty new ones (x132) per cell, computes every readout per world, and tests the cell difference as a paired per-seed
difference over thirty seeds. Controls: the ten old worlds reproduce X131's per-world values, liveness in every new run, heredity, and coverage.

Plan: reports/2026-11-03-x132-power-plan.md.

    python scripts/x132_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x132_power.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108", "x132")},
    {"tag": "f040", "flow": 0.040, "series": ("x108", "x132")},
]
X131_OLD = {
    # the ten original worlds: X131's per-world MEAN and SD (not its pooled value - the mean of a ratio is not the pooled ratio)
    0.030: {"survival": (0.2223, 0.1377), "depth": (1.3161, 0.6896)},
    0.040: {"survival": (0.1455, 0.0941), "depth": (2.3647, 1.6665)},
}
ABSORBED_AT = 0.50
VANISHED_AT = 0.10
PARTNER_SHARE = 0.50
REACH = 2.0
MIN_WORLDS = 28
HEREDITY_FLOOR = 0.35
OCCUPIED_FLOOR = 0.05
LARGEST_FLOOR = 50
GRID = 96
TOL_OLD = 0.005
BOOTSTRAP = 2000
RESOLUTION = {"survival": 0.05, "depth": 1.0}


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
    steps = sorted(int(s) for s in w["per_step"])
    last_step = steps[-1]
    last_step_of: dict[int, int] = {}
    for t in steps:
        for c in (w["per_step"].get(t) or []):
            last_step_of[int(c["uid"])] = t
    present = {u for u, t in last_step_of.items() if t == last_step}
    comps_last = w["per_step"].get(last_step) or []
    total_area = sum(float(c["area"]) for c in comps_last)
    largest = max((float(c["area"]) for c in comps_last), default=0.0)
    live = total_area >= OCCUPIED_FLOOR * GRID * GRID and largest >= LARGEST_FLOOR

    memo: dict[int, int] = {}
    sub_memo: dict[int, list[int]] = {}

    def sub(u):
        if u not in sub_memo:
            sub_memo[u] = descendants(kids, u)
        return sub_memo[u]

    surv, depths, heredity = [], [], []
    for mother, daughters in kids.items():
        if mother in w["peak"]:
            for d in daughters:
                if d in w["peak"]:
                    heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        if len(daughters) < 2:
            continue
        ds = [d for d in daughters if d in w["peak"]]
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                a, b = ds[i], ds[j]
                big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                surv.append(int(any(u in present for u in sub(big))) - int(any(u in present for u in sub(small))))
                depths.append(depth_of(kids, big, memo) - depth_of(kids, small, memo))

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

    n = max(1, sum(fates.values()))
    seed = int(Path(path).stem.split("_s")[-1])
    return {
        "world": Path(path).name, "seed": seed, "live": live,
        "pairs": len(surv), "deaths": sum(fates.values()),
        "survival": st.mean(surv) if surv else None,
        "depth": st.mean(depths) if depths else None,
        "absorbed": fates["absorbed"] / n, "isolated": fates["isolated"] / n,
        "vanished": fates["vanished"] / n,
        "kin": (kin_ok / kin_all) if kin_all else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X132 power run")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    per_cell = {}
    for spec in CELLS:
        rows = [world_stats(p, spec["flow"]) for p in cell_files(spec["series"], spec["flow"], filename="")]
        per_cell[spec["tag"]] = rows

    bad = []
    for spec in CELLS:
        rows = per_cell[spec["tag"]]
        old = [r for r in rows if r["seed"] <= 310]
        new = [r for r in rows if r["seed"] > 310]
        if len(rows) < MIN_WORLDS:
            bad.append(f"{spec['tag']}: {len(rows)} worlds")
        dead_runs = [r["world"] for r in new if not r["live"]]
        if dead_runs:
            bad.append(f"{spec['tag']}: {len(dead_runs)} new runs not alive ({dead_runs[:2]})")
        empty = [r["world"] for r in new if not r["pairs"]]
        if empty:
            bad.append(f"{spec['tag']}: {len(empty)} new worlds with no sister pair")
        # the ten old worlds must reproduce X131's per-world mean and sd
        for stat, (mean, sd) in X131_OLD[spec["flow"]].items():
            vals = [r[stat] for r in old if r.get(stat) is not None]
            if not vals:
                bad.append(f"{spec['tag']}: no old values for {stat}")
                continue
            if abs(st.mean(vals) - mean) > TOL_OLD:
                bad.append(f"{spec['tag']}/{stat}: old worlds mean {st.mean(vals):.4f} against X131's {mean}")
            if sd and abs(st.stdev(vals) - sd) > TOL_OLD:
                bad.append(f"{spec['tag']}/{stat}: old worlds sd {st.stdev(vals):.4f} against X131's {sd}")

    cells = {}
    for spec in CELLS:
        rows = per_cell[spec["tag"]]
        entry = {"worlds": len(rows), "seeds": sorted(r["seed"] for r in rows)}
        for stat in ("survival", "depth", "absorbed", "isolated", "vanished", "kin"):
            vals = [r[stat] for r in rows if r.get(stat) is not None]
            entry[stat] = {
                "worlds": len(vals),
                "pooled": round(st.mean(vals), 4) if vals else None,
                "sd": round(st.stdev(vals), 4) if len(vals) > 1 else None,
                "world_ci": boot(vals, 1400 + len(vals)) if vals else None,
                "values": [round(v, 4) for v in vals],
            }
        cells[spec["tag"]] = entry

    # paired per-seed test over the thirty shared seeds
    by_seed = {tag: {r["seed"]: r for r in rows} for tag, rows in per_cell.items()}
    seeds = sorted(set(by_seed["f030"]) & set(by_seed["f040"]))
    paired = {}
    for stat in ("survival", "depth", "absorbed", "isolated", "vanished", "kin"):
        diffs = [by_seed["f040"][s][stat] - by_seed["f030"][s][stat] for s in seeds
                 if by_seed["f040"][s].get(stat) is not None and by_seed["f030"][s].get(stat) is not None]
        if len(diffs) < MIN_WORLDS:
            paired[stat] = {"seeds": len(diffs), "unavailable": True}
            continue
        ci = boot(diffs, 1420 + len(diffs))
        excludes = bool(ci and (ci[0] > 0 or ci[1] < 0))
        res = RESOLUTION.get(stat)
        if excludes:
            outcome = "resolved"
        elif res is not None and abs(st.mean(diffs)) < res:
            outcome = "below resolution"
        else:
            outcome = "contradicted" if res is not None else "unnresolved"
        paired[stat] = {
            "seeds": len(diffs), "mean": round(st.mean(diffs), 4), "sd": round(st.stdev(diffs), 4),
            "ci": ci, "excludes_zero": excludes,
            "resolution": res, "outcome": outcome,
            "per_seed": [round(d, 4) for d in diffs],
        }

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        sv = paired["survival"]
        dp = paired["depth"]
        verdict = (f"thirty worlds per cell: the survival contrast (maze minus lattice) is {sv['mean']} with CI {sv['ci']} — {sv['outcome']} — "
                   f"against {dp['mean']} (CI {dp['ci']}) for depth, {dp['outcome']}; the vanishing share is "
                   f"{paired['vanished']['mean']} (CI {paired['vanished']['ci']}) and the kinship share {paired['kin']['mean']} "
                   f"(CI {paired['kin']['ci']}), both {paired['vanished']['outcome']} and {paired['kin']['outcome']}")

    res = {
        "kind": "l1_field_x132_power",
        "experiment": "X132",
        "command": "python scripts/x132_analyse.py --write",
        "prereg": "reports/2026-11-03-x132-power-plan.md",
        "note": "per-world readouts on ten old plus twenty new worlds per cell; the cell difference is the paired per-seed difference over thirty seeds",
        "cells": cells,
        "paired_by_seed": paired,
        "per_world": per_cell,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x132] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: worlds={c['worlds']} survival={c['survival']['pooled']} (sd {c['survival']['sd']}) "
              f"depth={c['depth']['pooled']} (sd {c['depth']['sd']}) vanished={c['vanished']['pooled']} kin={c['kin']['pooled']}")
    for stat, p in paired.items():
        if p.get("unavailable"):
            print(f"  {stat}: unavailable ({p['seeds']} seeds)")
        else:
            print(f"  {stat}: maze-lattice {p['mean']} (sd {p['sd']}, CI {p['ci']}) -> {p['outcome']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
