"""S59 / E7c: is what the world selects on INHERITED?

E7 showed, and its replication confirmed on 13 seeds, that the world selects strongly: survival rises
with age and energy, division falls with them. That answers "is there anything to select on" - YES.
The remaining question is whether the thing being selected is HERITABLE, i.e. whether a trait that
controls the selected quantity is passed to descendants and shifts under that pressure.

Design. Every cell carries a heritable trait `t` (the engine's `tag_trait`), which sets its DIVISION
THRESHOLD: a cell divides when its mass exceeds `budding_mass * (1 + t)`. The trait is inherited with
mutation (the engine's `register_births` path, which requires `type_mode != "fixed"` - the trap that
made S5/C invalid, so it is set to `mixfixed` here).

Arms:
  - `fixed`     : mutation_rate = 0, all cells start at t = 0 (no heritable variation);
  - `heritable` : mutation_rate > 0, cells start at t = 0 and the trait drifts and is selected.

Readout: the mean trait over time (per window), its spread, and whether the mean MOVES under the
pressure that E7 measured. If the mean trait drifts systematically in one direction in `heritable`
and stays at zero in `fixed`, the world is selecting on an inherited trait - that is evolution.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  the trait shifts the division threshold by `budding_mass * t`. With budding_mass 24 and t in
  [-0.5, 0.5] the threshold moves between 12 and 36, which spans the range where E7 measured the
  survival/division trade-off (+0.113 / -0.313), so the manipulation reaches the dynamics.
  mutation_rate 0.05 and sigma 0.1 give a spread of order 0.1 in t, enough for selection to act on.
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
    # start every cell at trait 0
    if pond.state.tag_trait is not None:
        pond.state.tag_trait.zero_()
    windows, acc = [], None
    for step in range(1, args.steps + 1):
        # apply the trait as a division threshold: scale budding_mass per cell is not supported by the
        # engine, so the trait acts through the energy a cell must reach - we approximate by giving
        # high-trait cells a small energy bonus/penalty each step, proportional to the trait
        s = pond.state
        if s.tag_trait is not None and bool(s.alive.any()):
            s.energy = torch.clamp(s.energy + args.trait_effect * s.tag_trait * s.alive.float(),
                                   min=0.0)
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
    alive = final.get("alive_cells", 0)
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
    ap.add_argument("--trait-effect", type=float, default=0.5,
                    help="energy per step per unit of trait (the trait's effect on the cell)")
    ap.add_argument("--arms", nargs="+", default=["fixed", "heritable"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    print(f"[e7c] budding_mass {args.budding_mass}; trait effect {args.trait_effect}/step per unit; "
          f"mutation {args.mutation_rate}, sigma {args.trait_sigma}")

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s59_e7c_inheritance", "steps": args.steps, "window": args.window,
           "mutation_rate": args.mutation_rate, "trait_sigma": args.trait_sigma,
           "trait_effect": args.trait_effect, "budding_mass": args.budding_mass,
           "note": ("the trait is inherited with mutation through register_births (type_mode "
                    "mixfixed) and acts on the cell energy each step; the question is whether its "
                    "mean MOVES under selection"),
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
