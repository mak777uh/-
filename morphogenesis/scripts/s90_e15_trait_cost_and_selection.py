"""S90 / E15: redo the trait experiments as ONE script that records everything.

The second referee of article 033 found that s64/s65/s66/s67 cannot be compared or even interpreted:

  - none of them records WHERE the colony was planted or which zone that is;
  - s66 raises `rule_strength` from 0.06 to 0.6, i.e. makes the trait ten times more EXPENSIVE, so the
    trait falls because of the cost, not because it was selected - and the article used that as evidence
    of selection;
  - s85 reseeded the trait as `uniform(0,1)` with mean 0.5, which is a different parameterisation from
    the s62 line that centres it near zero, so its numbers cannot be spliced into a "shift toward zero"
    argument.

This script removes all three problems by construction:

  - the planting position is an argument and `plant_xy`, the block mean and the zone class are written
    into EVERY row;
  - `rule_strength` is written into every row, and **0.0 is a real arm** - the control that shows what
    the trait does when it costs nothing;
  - the trait is always initialised the same way (`uniform(0,1)`), so the arms differ only in what is
    varied deliberately;
  - the readout is the PAIRED difference (heritable - fixed) per seed, so cost and selection are
    separated: with `rule_strength = 0` any shift is selection; with a nonzero strength the shift mixes
    selection and cost, and the control tells us how much.

Design: 2 zones (rich 7,7 / poor 16,16) x 3 strengths (0.0, 0.06, 0.6) x 2 arms (fixed, heritable) x N seeds.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys

import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)
from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402

ZONES = {"rich": (7, 7), "poor": (16, 16)}
RICH_LEVEL, POOR_LEVEL = 0.9, 0.3


def seed_at(run, cells: int, energy: float, xy: tuple[int, int]) -> None:
    n = run.world_cfg.grid
    cy, cx = xy
    side = max(1, math.isqrt(int(cells) - 1) + 1)
    top = max(0, min(n - side, cy - side // 2))
    left = max(0, min(n - side, cx - side // 2))
    mask = torch.zeros((n, n), dtype=torch.bool, device=run.device)
    for i in range(int(cells)):
        y, x = top + i // side, left + i % side
        if 0 <= y < n and 0 <= x < n:
            mask[y, x] = True
    run.pond.seed_life(mask, energy=energy)
    run._apply_alive(mask.to(run.device))
    run._apply_genome(mask, run.genome[0, :, mask])


def zone_of(pond, xy):
    res = pond.state.resource
    n = pond.cfg.grid
    cy, cx = xy
    side = max(1, math.isqrt(127) + 1)
    top, left = max(0, min(n - side, cy - side // 2)), max(0, min(n - side, cx - side // 2))
    block = res[top:top + side, left:left + side]
    mean = float(block.mean())
    klass = "rich" if mean >= RICH_LEVEL else ("poor" if mean <= POOR_LEVEL else "mixed")
    return {"plant_xy": [cy, cx], "block_mean": round(mean, 4), "class": klass}


def run_one(seed, args, arm, strength, xy):
    mutation = args.mutation_rate if arm == "heritable" else 0.0
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=args.budding_mass, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.0, plastic_move_cost=0.0, plastic_gate="pred",
        plastic_direction="gradient", plastic_nomove=True,
        mutation_rate=mutation, mutation_trait_sigma=args.sigma, type_mode="mixfixed",
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_at(run, args.seed_cells, args.seed_energy, xy)
    zone = zone_of(run.pond, xy)
    pond = run.pond
    gen = torch.Generator(device="cpu").manual_seed(seed * 7919 + 17)
    if pond.state.tag_trait is not None:
        pond.state.tag_trait.uniform_(0.0, 1.0, generator=gen)
    windows, acc = [], None
    for step in range(1, args.steps + 1):
        s = pond.state
        if strength > 0.0 and s.tag_trait is not None and bool(s.alive.any()):
            # the trait COSTS: a high-trait cell pays more upkeep. With strength 0 it costs nothing,
            # so any shift in that arm is selection alone.
            s.energy = torch.clamp(
                s.energy - strength * s.tag_trait * s.alive.float(), min=0.0)
        run.step()
        s = pond.state
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        tr = s.tag_trait
        if acc is None:
            acc = {"n": 0, "mean": 0.0, "std": 0.0, "alive": 0}
        acc["n"] += 1
        if tr is not None:
            acc["mean"] += float(tr[a].mean())
            acc["std"] += float(tr[a].std())
        acc["alive"] += cnt
        if acc["n"] >= args.window:
            windows.append({"trait_mean": round(acc["mean"] / acc["n"], 6),
                            "trait_std": round(acc["std"] / acc["n"], 6),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = int(pond.state.alive.sum())
    return {"seed": seed, "arm": arm, "rule_strength": strength, "zone": zone,
            "windows": windows, "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--income", type=float, default=0.04)
    ap.add_argument("--update-cost", type=float, default=0.038)
    ap.add_argument("--repair-cost", type=float, default=0.022)
    ap.add_argument("--init-resource-fill", type=float, default=1.0)
    ap.add_argument("--resource-regen", type=float, default=0.05)
    ap.add_argument("--patch-inflow-base", type=float, default=0.1)
    ap.add_argument("--patch-inflow-rich", type=float, default=4.0)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=128)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--budding-mass", type=float, default=8.0)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--strengths", type=float, nargs="+", default=[0.0, 0.06, 0.6])
    ap.add_argument("--zones", nargs="+", default=["rich", "poor"])
    ap.add_argument("--arms", nargs="+", default=["fixed", "heritable"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for zname in args.zones:
        xy = ZONES[zname]
        for strength in args.strengths:
            for s in args.seeds:
                for arm in args.arms:
                    r = run_one(s, args, arm, strength, xy)
                    r["zone_name"] = zname
                    rows.append(r)
            got = rows[-1]["zone"]
            print(f"[e15] zone {zname} strength {strength}: planted {got['plant_xy']} "
                  f"class {got['class']} (block {got['block_mean']})")
    out = {"kind": "s90_e15_trait_cost_and_selection", "steps": args.steps, "window": args.window,
           "strengths": args.strengths, "zones": {k: list(v) for k, v in ZONES.items()},
           "note": ("planting position and zone class are written into every row; rule_strength 0.0 is a "
                    "real arm, so a shift there is selection alone while a nonzero strength mixes "
                    "selection and cost"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    # paired difference heritable - fixed, last window, per (zone, strength)
    for zname in args.zones:
        for strength in args.strengths:
            base, her = {}, {}
            for r in rows:
                if r["zone_name"] != zname or r["rule_strength"] != strength or not r["windows"]:
                    continue
                (base if r["arm"] == "fixed" else her)[r["seed"]] = r["windows"][-1]["trait_mean"]
            diffs = [her[k] - base[k] for k in sorted(base) if k in her]
            if diffs:
                pos = sum(1 for d in diffs if d > 0)
                print(f"{zname:5s} strength {strength:4}: paired diff "
                      f"{sum(diffs)/len(diffs):+.5f} ({pos}/{len(diffs)} positive)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
