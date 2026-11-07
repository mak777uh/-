"""S60 / E7d: a trait that changes an ACTION, not a reserve.

The previous version (s59) gave the cell energy proportional to its trait. Ten-fold strengthening
changed nothing, which was informative: the trait did not change any ACTION, so selection had nothing
to see. A cell with a high trait simply held more energy and behaved identically.

This version makes the trait change the DIVISION THRESHOLD:

    a cell divides when its energy exceeds `budding_mass * (1 + trait)`

so a high-trait cell divides EARLIER (more offspring, shorter life) and a low-trait cell divides LATER
(longer life, fewer offspring). That is exactly the trade-off E7 measured (young divide more:
-0.313; old survive better: +0.113), so selection now has an action to act on.

Implementation. The engine's `budding_mass` is a global config value, so the division decision is made
HERE: each step, living cells whose energy exceeds their own threshold are divided manually. The
engine's own budding is disabled by setting `budding_mass` far above any reachable energy.

Arms:
  - `fixed`     : mutation_rate = 0 - no heritable variation;
  - `heritable` : mutation_rate > 0 - the trait is inherited with mutation and can be selected.

Readout: mean trait per window, its spread, and whether the mean MOVES in one direction.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  the threshold moves between `budding_mass * (1 - 0.5)` and `* (1 + 0.5)`, i.e. 12 to 36 for
  budding_mass 24. E7 measured the survival/division trade-off across exactly this range, so the
  manipulation reaches the dynamics. The trait starts at 0 for every cell.
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


def divide_by_threshold(pond, base_mass: float, cost: float):
    """Divide every living cell whose energy exceeds its own threshold.

    Returns the number of divisions performed. The offspring is placed on a free neighbour and
    inherits the parent's trait through the engine's own `register_births` path (which needs
    `type_mode != "fixed"`), so mutation and tag inheritance work exactly as the engine defines them.
    """
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    if s.tag_trait is None:
        return 0
    thr = base_mass * (1.0 + s.tag_trait.clamp(-0.9, 3.0))
    ready = s.alive & (s.energy >= thr)
    if not bool(ready.any()):
        return 0
    count = 0
    newly = torch.zeros_like(s.alive)
    parent_mask = torch.zeros_like(s.alive)
    ys, xs = ready.nonzero(as_tuple=True)
    order = torch.randperm(ys.numel(), generator=pond.gen_sel)
    for k in order.tolist():
        y, x = int(ys[k]), int(xs[k])
        if not bool(s.alive[y, x]):
            continue
        # find a free neighbour
        free = None
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < n and 0 <= nx < n and not bool(s.alive[ny, nx]):
                free = (ny, nx)
                break
        if free is None:
            continue
        ny, nx = free
        half = float(s.energy[y, x]) * 0.5
        s.energy[y, x] = half
        s.alive[ny, nx] = True
        s.energy[ny, nx] = half * (1.0 - cost)
        s.tag_trait[ny, nx] = s.tag_trait[y, x]
        s.tag[ny, nx] = s.tag[y, x]
        newly[ny, nx] = True
        parent_mask[y, x] = True
        count += 1
    if count:
        # the engine's own birth bookkeeping: lineage label, mutation, counters
        pond.register_births(newly, parent_mask)
    return count


def run_one(seed, args, arm):
    mutation = args.mutation_rate if arm == "heritable" else 0.0
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        # the engine's own budding is disabled: the threshold is far above any reachable energy
        budding_mass=1e9, budding_cost=0.2, resource_max=1.0,
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
    windows, acc, total_div = [], None, 0
    for step in range(1, args.steps + 1):
        run.step()
        total_div += divide_by_threshold(pond, args.budding_mass, args.budding_cost)
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
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "mutation_rate": mutation, "divisions": total_div,
            "windows": windows,
            "final": {"alive": int(pond.state.alive.sum()), "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and int(pond.state.alive.sum()) >= 10)}


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
    ap.add_argument("--budding-cost", type=float, default=0.2)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--trait-sigma", type=float, default=0.1)
    ap.add_argument("--arms", nargs="+", default=["fixed", "heritable"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    print(f"[e7d] threshold = {args.budding_mass} * (1 + trait); trait in [-0.9, 3.0]; "
          f"mutation {args.mutation_rate}, sigma {args.trait_sigma}")

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s60_e7d_trait_threshold", "steps": args.steps, "window": args.window,
           "mutation_rate": args.mutation_rate, "trait_sigma": args.trait_sigma,
           "budding_mass": args.budding_mass,
           "note": ("the trait sets the DIVISION THRESHOLD, so it changes an action; the engine's own "
                    "budding is disabled and division is performed by the script"),
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
        print(f"{'':10s} trait_std  {stds} | divisions {[r['divisions'] for r in ar]} "
              f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
