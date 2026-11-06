"""S32 / H9: does the optimal memory lag scale with the DISTANCE to the food?

S31/H8 found the mechanism: the optimal lag tracks the cell's mobility, because a cell can only use
memory it can travel to within the memory's lifetime. That makes a quantitative prediction:

    optimal_lag  ~  distance / mobility

This script tests the distance half of it: the same lag sweep at three separations between the old
and the new patch. If the prediction holds, the best lag should grow with the distance.

Design:
  - the rich patches jump once, at `move_at`, from (7,7) to a new place;
  - three separations: `near` (7,7)->(12,12) ~7 cells, `mid` (7,7)->(17,17) ~14, `far` (7,7)->(24,24) ~24;
  - lags 0 (no memory), 10, 40, 100.

Readout: favourable share averaged over the run, per (separation, lag). R1 checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  with mobility 1 a cell covers ~lag cells in `lag` steps, so if the optimum is distance/mobility the
  best lag should be ~7 / ~14 / ~24 for the three separations, i.e. the near case should prefer lag 10
  and the far case should prefer lag 40 or more. The sweep 0/10/40/100 brackets that.
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


def move_patches(pond, new_xy: tuple[int, int]) -> None:
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    third = n // 3
    olds = [(third // 2, third // 2), (n - third, n - third), (third // 2, n - third)]
    for (y, x) in olds:
        s.resource[y:y + third // 2, x:x + third // 2] = cfg.resource_max * 0.2
    cy, cx = new_xy
    half = third // 2
    s.resource[max(0, cy - half):cy + half, max(0, cx - half):cx + half] = cfg.resource_max


def run_one(seed, args, lag, new_xy):
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
    moved = False
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if not moved and st >= args.move_at:
            move_patches(pond, new_xy)
            moved = True
        if lag > 0 and bool(s.alive.any()):
            pond.update_signal()
            if s.signal is not None:
                mv = moves_up_field(pond, s.signal)
                if mv:
                    pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
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
    return {"seed": seed, "lag": lag, "new_patch": list(new_xy), "overall": overall,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


SEPARATIONS = {"near": (12, 12), "mid": (17, 17), "far": (24, 24)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--move-at", type=int, default=300)
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
    ap.add_argument("--seps", nargs="+", default=["near", "mid", "far"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for sep in args.seps:
        xy = SEPARATIONS[sep]
        for lag in args.lags:
            for s in args.seeds:
                r = run_one(s, args, lag, xy)
                r["separation"] = sep
                rows.append(r)
    out = {"kind": "s32_h9_distance_curve", "steps": args.steps, "move_at": args.move_at,
           "lags": args.lags, "separations": {k: list(v) for k, v in SEPARATIONS.items()},
           "note": ("prediction: optimal_lag ~ distance/mobility, so the best lag should grow with "
                    "the separation between the old and the new patch"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("lag | " + " | ".join(f"{s} {SEPARATIONS[s]}" for s in args.seps))
    for lag in args.lags:
        cells = []
        for sep in args.seps:
            vals = [r["overall"] for r in rows
                    if r["lag"] == lag and r["separation"] == sep and r["overall"] is not None]
            r1 = [r["R1"] for r in rows if r["lag"] == lag and r["separation"] == sep]
            cells.append(f"{round(sum(vals) / len(vals), 3) if vals else None} ({sum(r1)}/{len(r1)})")
        print(f"{lag:3d} | " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
