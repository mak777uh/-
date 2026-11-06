"""S39 / H13: does prediction start to pay once the cell can actually MOVE?

S38/H12 gave a wave that creates food with a lag - a real prediction - and it did not help: positive
lags (prediction) were no better than negative ones (chasing). The explanation was that the cell moves
only 0.14 cells in a lifetime, so it cannot reach what the wave predicts.

That is a testable claim, and this script tests it: the SAME lag sweep, but with mobile cells
(`moves_per_step` 3 and 5, i.e. three and five movement rounds per step, each charged).

Prediction if the explanation is right:
  - at mobility 1 the lags are indistinguishable (the H12 result, reproduced here as a control);
  - at mobility 3 and 5 the POSITIVE lags (prediction) should beat the negative ones (chasing).

If instead the lags stay indistinguishable at every mobility, then prediction does not pay for a
different reason and the H10 explanation is incomplete.

Readout: favourable share per arm, plus moves per step, per mobility. R1 checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  the wave period is 40 steps and the lag is 10-20, so the lead is a quarter to a half period. A cell at
  mobility 5 covers ~5 cells per step, i.e. 50-100 cells within one lag - more than enough to cross the
  grid (32 cells), so at mobility 5 the cell can in principle reach the predicted place in time. At
  mobility 1 it covers 10-20 cells in the same window, which is enough to cross a patch but not the
  grid. The sweep therefore spans "cannot reach" to "can reach".
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


def wave_field(pond, lag):
    cfg = pond.cfg
    period = int(getattr(cfg, "signal_external_period", 0) or 0)
    if period <= 0:
        return None
    t = 2.0 * math.pi * (float(pond.state.step) - float(lag)) / float(period)
    rows = torch.arange(cfg.grid, device=pond.device, dtype=torch.float32)
    phase = t - 2.0 * math.pi * rows / max(cfg.grid, 1)
    return torch.sin(phase)[:, None].expand(cfg.grid, cfg.grid)


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


def run_one(seed, args, lag, coupling, mps):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        signal_external_period=args.period,
        signal_food_coupling=coupling,
        signal_food_lag=lag,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    favs, moves_total, steps = [], 0, 0
    for _ in range(args.steps):
        run.step()
        s = pond.state
        if bool(s.alive.any()):
            for _round in range(mps):
                field = wave_field(pond, lag)
                if field is None:
                    break
                mv = moves_up_field(pond, field)
                if not mv:
                    break
                pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
                moves_total += len(mv)
        a = s.alive
        n = int(a.sum())
        if n == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / n))
        steps += 1
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    mps_actual = round(moves_total / steps, 2) if steps else 0.0
    return {"seed": seed, "lag": lag, "coupling": coupling, "moves_per_step": mps,
            "overall": overall, "moves_actual": mps_actual,
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
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--coupling", type=float, default=0.8)
    ap.add_argument("--lags", type=int, nargs="+", default=[-20, 0, 20])
    ap.add_argument("--mobilities", type=int, nargs="+", default=[1, 3, 5])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for mps in args.mobilities:
        for lag in args.lags:
            for s in args.seeds:
                rows.append(run_one(s, args, lag, args.coupling, mps))
        # the no-wave control at this mobility
        for s in args.seeds:
            rows.append(run_one(s, args, 0, 0.0, mps))
    out = {"kind": "s39_h13_prediction_mobile", "steps": args.steps, "period": args.period,
           "coupling": args.coupling, "lags": args.lags, "mobilities": args.mobilities,
           "note": ("same lag sweep as H12 but with mobile cells; prediction (positive lag) should beat "
                    "chasing (negative lag) if the H10 explanation is right"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("mobility | no_wave | lag-20 | lag0 | lag+20 | moves/step")
    for mps in args.mobilities:
        def val(lag, coupling):
            v = [r["overall"] for r in rows
                 if r["moves_per_step"] == mps and r["lag"] == lag and r["coupling"] == coupling
                 and r["overall"] is not None]
            return round(sum(v) / len(v), 3) if v else None
        mv = [r["moves_actual"] for r in rows if r["moves_per_step"] == mps and r["lag"] == 0 and r["coupling"] == args.coupling]
        print(f"{mps:8d} | {val(0, 0.0)} | {val(-20, args.coupling)} | {val(0, args.coupling)} "
              f"| {val(20, args.coupling)} | {round(sum(mv) / len(mv), 2) if mv else None}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
