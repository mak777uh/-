"""S30 / H7: is the optimal memory lag set by the LIFETIME OF THE FIELD?

S29/H6 found a clear optimum (lag 10-40 beats no memory by +0.035..+0.047) that does NOT shift with
the rate of environmental change. That suggested the optimum is set by the field's own lifetime
(diffusion + decay) rather than by the environment. This script tests that directly.

Design: sweep the lag at two field lifetimes, obtained by changing `signal_decay`:
  - `fast_decay` : decay 0.15 -> the field forgets in a few steps;
  - `slow_decay` : decay 0.01 -> the field remembers for a long time.

Prediction if the mechanism is "optimum = field lifetime": the best lag should be SHORTER under fast
decay and LONGER under slow decay. If the optimum does not move, then the lag is not tied to the
field lifetime and the H6 explanation is wrong too.

Readout: favourable share averaged over the run, per (decay, lag). R1 checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  the field obeys h <- h*(1-decay) + diffusion*laplacian + source. With decay 0.15 the field's
  memory is ~1/0.15 ~ 7 steps; with decay 0.01 it is ~100 steps. The lag sweep 0..200 therefore
  brackets both lifetimes, so a shift of the optimum, if it exists, is visible.
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


def run_one(seed, args, lag, decay):
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
        signal_decay=(decay if lag > 0 else 0.0),
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
        if lag > 0 and bool(s.alive.any()):
            pond.update_signal()
            if s.signal is not None:
                moves = moves_up_field(pond, s.signal)
                if moves:
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
    return {"seed": seed, "lag": lag, "decay": decay, "overall": overall,
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
    ap.add_argument("--mem-source", type=float, default=1.0)
    ap.add_argument("--lags", type=int, nargs="+", default=[0, 10, 40, 100, 200])
    ap.add_argument("--decays", type=float, nargs="+", default=[0.15, 0.05, 0.01])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for dec in args.decays:
        for lag in args.lags:
            for s in args.seeds:
                rows.append(run_one(s, args, lag, dec))
    out = {"kind": "s30_h7_lifetime_curve", "steps": args.steps,
           "lags": args.lags, "decays": args.decays,
           "note": ("decay sets the field's lifetime (~1/decay steps): 0.15 -> ~7, 0.05 -> ~20, "
                    "0.01 -> ~100. If the optimal lag tracks the lifetime, the best lag moves right "
                    "as decay falls."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("lag | " + " | ".join(f"decay={d}" for d in args.decays))
    for lag in args.lags:
        cells = []
        for dec in args.decays:
            vals = [r["overall"] for r in rows
                    if r["lag"] == lag and r["decay"] == dec and r["overall"] is not None]
            r1 = [r["R1"] for r in rows if r["lag"] == lag and r["decay"] == dec]
            cells.append(f"{round(sum(vals) / len(vals), 3) if vals else None} ({sum(r1)}/{len(r1)})")
        print(f"{lag:3d} | " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
