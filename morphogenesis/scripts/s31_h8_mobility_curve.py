"""S31 / H8: does the optimal memory lag track the cell's own MOBILITY?

Two explanations of the memory optimum have already been refuted: the rate of environmental change
(H6) and the field's lifetime (H7). The third candidate is the simplest: a cell moves one step per
step and only when it is hungry, so in `lag` steps it covers about `lag` cells. A memory longer than
that is useless - the cell cannot reach what the memory points at before the food moves on.

Prediction if this is right: faster cells should support LONGER optimal memory.

Mobility is changed without touching the step rule, by allowing a cell to move more than once per
step: `moves_per_step` (1 = the normal world, 2 = each hungry cell may move twice, 3 = three times).
The move cost is charged per move, so faster cells also pay more - the comparison is not free.

Readout: favourable share averaged over the run, per (mobility, lag). R1 checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  with `moves_per_step` m the cell covers ~m*lag cells during one memory lifetime, so the lag at
  which memory stops being reachable is ~distance/m. The rich patches are ~24 cells apart (from
  (7,7) to (24,24)), so m=1 needs lag ~24, m=2 ~12, m=3 ~8. If the optimum tracks mobility, the
  best lag should FALL as m rises - the opposite direction from the naive "faster = longer memory"
  reading, which is exactly what makes this a real test.
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
    favs = []
    for _ in range(args.steps):
        run.step()
        s = pond.state
        if bool(s.alive.any()):
            # mobility: up to mps rounds of movement per step (0 rounds when there is no field)
            for _round in range(mps if lag > 0 else 0):
                if lag > 0:
                    pond.update_signal()
                if s.signal is None:
                    break
                moves = moves_up_field(pond, s.signal)
                if not moves:
                    break
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        a = s.alive
        n = int(a.sum())
        if n == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / n))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    return {"seed": seed, "lag": lag, "moves_per_step": mps, "overall": overall,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
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
    ap.add_argument("--lags", type=int, nargs="+", default=[0, 10, 40, 100])
    ap.add_argument("--mobilities", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for mps in args.mobilities:
        for lag in args.lags:
            for s in args.seeds:
                rows.append(run_one(s, args, lag, mps))
    out = {"kind": "s31_h8_mobility_curve", "steps": args.steps,
           "lags": args.lags, "mobilities": args.mobilities,
           "note": ("moves_per_step = how many movement rounds a step allows; the move cost is "
                    "charged per move, so faster cells pay more. The patches are ~24 cells apart, "
                    "so if the optimum tracks mobility the best lag should FALL as mobility rises."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("lag | " + " | ".join(f"mps={m}" for m in args.mobilities))
    for lag in args.lags:
        cells = []
        for mps in args.mobilities:
            vals = [r["overall"] for r in rows
                    if r["lag"] == lag and r["moves_per_step"] == mps and r["overall"] is not None]
            r1 = [r["R1"] for r in rows if r["lag"] == lag and r["moves_per_step"] == mps]
            cells.append(f"{round(sum(vals) / len(vals), 3) if vals else None} ({sum(r1)}/{len(r1)})")
        print(f"{lag:3d} | " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
