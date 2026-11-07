"""S62 / E7e: make the trait part of the RULE, not an overstructure.

E7d concluded that a trait cannot be selected because it is an overstructure: the cell's fate is set
by energy and age, which are RULES, and a trait that merely nudges a reserve cannot compete with a
rule. The remaining test is the opposite design:

    let the trait change the RULE ITSELF - the cell's upkeep.

A cell with trait `t` pays `update_cost * (1 + t)` per step. This is not a bonus added on top: it
changes the rate at which the cell loses energy, i.e. the very quantity that decides both survival
(E7: +0.154 on energy) and how soon it can divide. The trait is now inside the rule, not beside it.

Arms:
  - `fixed`     : mutation_rate = 0 (no heritable variation);
  - `heritable` : mutation_rate > 0.

Prediction if the overstructure explanation is right: the mean trait should now MOVE systematically,
because a 10 % change in upkeep is comparable to the margin between income (0.16) and spend (0.06).

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  income at a full patch = 0.16, spent = 0.060, margin = 0.100. A trait of 0.5 raises upkeep to
  0.090, cutting the margin to 0.070 (30 %); a trait of -0.5 lowers it to 0.030, raising the margin
  to 0.130 (30 %). So the trait moves the margin by +-30 %, which is far above the 1:30 noise ratio
  that defeated E7d. The trait starts at 0 for every cell.
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


def seed_on_patch(run, cells: int, energy: float, patch_xy: tuple[int, int]) -> None:
    n = run.world_cfg.grid
    cy, cx = patch_xy
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


def run_one(seed, args, arm):
    mutation = args.mutation_rate if arm == "heritable" else 0.0
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=args.budding_mass, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        mutation_rate=mutation, mutation_trait_sigma=args.trait_sigma,
        type_mode="mixfixed",
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    if pond.state.tag_trait is not None:
        pond.state.tag_trait.zero_()
    windows, acc = [], None
    for step in range(1, args.steps + 1):
        # THE TRAIT IS INSIDE THE RULE: it scales the upkeep the cell pays this step, BEFORE the
        # engine applies its own cost, so a high-trait cell loses energy faster than a low-trait one.
        s = pond.state
        if s.tag_trait is not None and bool(s.alive.any()):
            extra = args.rule_strength * s.tag_trait * s.alive.float()
            s.energy = torch.clamp(s.energy - extra, min=0.0)
        run.step()
        s = pond.state
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        tr = s.tag_trait
        if acc is None:
            acc = {"start": step, "n": 0, "mean": 0.0, "std": 0.0, "alive": 0}
        acc["n"] += 1
        if tr is not None:
            acc["mean"] += float(tr[a].mean())
            acc["std"] += float(tr[a].std())
        acc["alive"] += cnt
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": step,
                            "trait_mean": round(acc["mean"] / acc["n"], 5),
                            "trait_std": round(acc["std"] / acc["n"], 5),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = int(pond.state.alive.sum())
    return {"seed": seed, "arm": arm, "mutation_rate": mutation, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--patch-y", type=int, default=7)
    ap.add_argument("--patch-x", type=int, default=7)
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
    ap.add_argument("--budding-mass", type=float, default=24.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--trait-sigma", type=float, default=0.1)
    ap.add_argument("--rule-strength", type=float, default=0.06,
                    help="energy per step per unit of trait - comparable to the upkeep itself")
    ap.add_argument("--arms", nargs="+", default=["fixed", "heritable"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    margin = args.income * 4.0 - (args.update_cost + args.repair_cost)
    print(f"[e7e] margin at a full patch {margin:.3f}/step; trait moves upkeep by "
          f"+-{args.rule_strength:.3f} per unit, i.e. +-{100*args.rule_strength/margin:.0f}% of the margin")

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s62_e7e_trait_in_rule", "steps": args.steps, "window": args.window,
           "mutation_rate": args.mutation_rate, "trait_sigma": args.trait_sigma,
           "rule_strength": args.rule_strength, "margin": round(margin, 4),
           "note": ("the trait scales the cell's UPKEEP, i.e. it is inside the rule, not an add-on"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        means, stds = [], []
        for i in range(nw):
            v = [r["windows"][i]["trait_mean"] for r in ar if i < len(r["windows"])]
            s2 = [r["windows"][i]["trait_std"] for r in ar if i < len(r["windows"])]
            means.append(round(sum(v) / len(v), 4) if v else None)
            stds.append(round(sum(s2) / len(s2), 4) if s2 else None)
        print(f"{arm:10s} trait_mean {means}")
        print(f"{'':10s} trait_std  {stds} | R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
