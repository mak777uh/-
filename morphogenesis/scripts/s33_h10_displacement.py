"""S33 / H10: how far does a cell actually travel? Testing the "local smoother" reading of H9.

H9 refuted the formula "optimal lag ~ distance / mobility": the distance between the old and the new
food did not shift the optimal lag at all. A plausible reading is that at mobility 1 the cell does not
travel to the food at all - it random-walks locally - so the memory acts as a local smoother of the
field, not as a map of a distant target. If that is true, the cell's actual displacement from where it
was born should be SMALL compared with the distance to the food.

This script measures the displacement directly, by tagging every living cell with its birth position
and reporting, per window:
  - `mean_displacement`   : mean Euclidean distance from the birth cell, over living cells;
  - `p90_displacement`    : the 90th percentile of that distance;
  - `max_displacement`    : the largest one;
  - `alive_mean`          : population size.

Arms: mobility 1 and mobility 3, both with the memory field on (lag 10, the H6-H9 optimum), plus a
no-memory control. If the cell is a local random walker, displacement should stay small at mobility 1
and grow at mobility 3 - which would explain why mobility, and not distance, moves the optimum.

No engine change: the birth position is tracked in the script by remembering, for each grid cell, the
position of the cell currently standing there.
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


def moves_up_field(pond, field):
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    err = s.resource - s.pred if s.pred is not None else torch.zeros_like(s.resource)
    poor = s.alive & (err < 0.0) & (s.energy > cfg.plastic_move_cost)
    if not bool(poor.any()):
        return []
    cand = poor.nonzero(as_tuple=False)
    order = torch.randperm(cand.shape[0], generator=pond.gen_sel)
    taken = torch.zeros_like(s.alive)
    moves = []
    for k in order.tolist():
        y, x = int(cand[k, 0]), int(cand[k, 1])
        if not bool(s.alive[y, x]) or bool(taken[y, x]):
            continue
        best, best_v = None, float(field[y, x])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                continue
            v = float(field[ny, nx])
            if v > best_v:
                best, best_v = (ny, nx), v
        if best is None:
            continue
        taken[best[0], best[1]] = True
        moves.append((y, x, best[0], best[1]))
    return moves


def run_one(seed, args, lag, mps):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        signal_diffusion=(args.diffusion if lag > 0 else 0.0),
        signal_decay=(args.decay if lag > 0 else 0.0),
        signal_memory_lag=lag,
        signal_memory_source=(args.mem_source if lag > 0 else 0.0),
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    n = cfg.grid
    # birth position of the cell currently standing on each grid cell (-1 = unknown/empty)
    birth = torch.full((n, n, 2), -1, dtype=torch.long, device=run.device)
    alive0 = pond.state.alive
    ys, xs = alive0.nonzero(as_tuple=True)
    birth[ys, xs, 0] = ys
    birth[ys, xs, 1] = xs
    windows, acc = [], None
    for _ in range(args.steps):
        prev_alive = pond.state.alive.clone()
        prev_birth = birth.clone()
        run.step()
        s = pond.state
        # cells that survived keep their birth position; new cells are born where they appear
        birth = torch.full((n, n, 2), -1, dtype=torch.long, device=run.device)
        keep = s.alive & prev_alive
        birth[keep] = prev_birth[keep]
        new = s.alive & ~prev_alive
        ny, nx = new.nonzero(as_tuple=True)
        birth[ny, nx, 0] = ny
        birth[ny, nx, 1] = nx
        if bool(s.alive.any()):
            for _round in range(mps if lag > 0 else 0):
                if lag > 0:
                    pond.update_signal()
                if s.signal is None:
                    break
                mv = moves_up_field(pond, s.signal)
                if not mv:
                    break
                # carry the birth tag along with each move
                for sy, sx, ty, tx in mv:
                    birth[ty, tx] = birth[sy, sx]
                pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
        a = pond.state.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        by = birth[a][:, 0].float()
        bx = birth[a][:, 1].float()
        ay, ax = a.nonzero(as_tuple=True)
        d = torch.sqrt((ay.float() - by) ** 2 + (ax.float() - bx) ** 2)
        if acc is None:
            acc = {"start": int(pond.state.step), "n": 0, "disp": [], "alive": 0}
        acc["n"] += 1
        acc["disp"].append(d)
        acc["alive"] += cnt
        if acc["n"] >= args.window:
            allv = torch.cat(acc["disp"])
            windows.append({"start": acc["start"], "end": int(pond.state.step),
                            "mean_displacement": round(float(allv.mean()), 3),
                            "p90_displacement": round(float(torch.quantile(allv, 0.9)), 3),
                            "max_displacement": round(float(allv.max()), 3),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "lag": lag, "moves_per_step": mps, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
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
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--diffusion", type=float, default=0.10)
    ap.add_argument("--decay", type=float, default=0.05)
    ap.add_argument("--mem-source", type=float, default=1.0)
    ap.add_argument("--lag", type=int, default=10)
    ap.add_argument("--mobilities", type=int, nargs="+", default=[1, 3])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for mps in args.mobilities:
        for s in args.seeds:
            rows.append(run_one(s, args, args.lag, mps))
    out = {"kind": "s33_h10_displacement", "steps": args.steps, "window": args.window,
           "lag": args.lag, "mobilities": args.mobilities,
           "note": ("measures how far a living cell actually travels from its birth cell; if the "
                    "cell is a local random walker the displacement stays small and the memory can "
                    "only act as a local smoother, which explains why distance (H9) does not matter"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for mps in args.mobilities:
        ar = [r for r in rows if r["moves_per_step"] == mps]
        nw = max((len(r["windows"]) for r in ar), default=0)
        print(f"== mobility {mps}")
        for field in ("mean_displacement", "p90_displacement", "max_displacement", "alive_mean"):
            vals = []
            for i in range(nw):
                v = [r["windows"][i][field] for r in ar if i < len(r["windows"])]
                vals.append(round(sum(v) / len(v), 2) if v else None)
            print(f"   {field:20s} {vals}")
        print(f"   R1 {[r['R1'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
