"""S38 / H12: does a wave that CREATES food become a usable prediction?

S27/H4 showed that an external rhythm unrelated to food is useless: the cell follows the wave and goes
where there is nothing. The owner's proposal closes that gap: let the wave CREATE the food, with a lag.
Then the wave is not noise, it is a prediction.

Design: the food inflow is modulated by the wave phase, with the wave leading the food by `lag` steps:

    inflow *= clamp(1 + coupling * sin(phase(t - lag) - 2*pi*row/n), 0)

  - lag > 0 : the crest arrives BEFORE the food, so following the wave is a prediction;
  - lag = 0 : the crest and the food coincide, so following the wave is just following the food;
  - lag < 0 : the crest arrives AFTER the food, so following the wave is chasing what has already gone.

Arms:
  - `no_wave`   : no wave, no coupling (control);
  - `wave_lagN` : wave coupled to food with lag N, cells step up the wave gradient;
  - `wave_off`  : the wave is present but NOT coupled to food (the S27 control) - it must lose if the
                  coupling is what makes the wave useful.

Readout: favourable share per window, and the number of moves. R1 checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  the wave period is 40 steps; the cells live on the timescale of hundreds of steps, so a lag of 10 is
  about a quarter period - long enough to be a real lead, short enough that the food is still where the
  crest was. The coupling 0.8 keeps the inflow positive (clamped at 0) and does not change the mean
  inflow, so the colony's energy budget is unchanged across arms.
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
    """The wave as the cell sees it: sin(phase(t - lag) - 2*pi*row/n)."""
    cfg = pond.cfg
    period = int(getattr(cfg, "signal_external_period", 0) or 0)
    if period <= 0:
        return None
    t = 2.0 * math.pi * (float(pond.state.step) - float(lag)) / float(period)
    rows = torch.arange(cfg.grid, device=cfg.grid and pond.device, dtype=torch.float32)
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


def run_one(seed, args, arm, lag, coupling):
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
        signal_food_spatial=bool(getattr(args, "spatial", False)),
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        s = pond.state
        moved = 0
        if arm != "no_wave" and bool(s.alive.any()):
            field = wave_field(pond, lag)
            if field is not None:
                mv = moves_up_field(pond, field)
                if mv:
                    pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
                    moved = len(mv)
        a = s.alive
        n = int(a.sum())
        if n == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        fav = float((a & (res >= thr)).sum() / n)
        if acc is None:
            acc = {"n": 0, "fav": 0.0, "moved": 0, "alive": 0}
        acc["n"] += 1
        acc["fav"] += fav
        acc["moved"] += moved
        acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"favourable_share": round(acc["fav"] / acc["n"], 4),
                            "moves_per_step": round(acc["moved"] / acc["n"], 2),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(w["favourable_share"] for w in windows) / len(windows), 4) if windows else None
    return {"seed": seed, "arm": arm, "lag": lag, "coupling": coupling, "overall": overall,
            "windows": windows,
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
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--coupling", type=float, default=0.8)
    ap.add_argument("--spatial", action="store_true",
                    help="H14: wave phase from distance to patches, not from row index")
    ap.add_argument("--lags", type=int, nargs="+", default=[-20, -10, 0, 10, 20])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        rows.append(run_one(s, args, "no_wave", 0, 0.0))
        rows.append(run_one(s, args, "wave_off", 0, 0.0))  # wave present, not coupled
        for lag in args.lags:
            rows.append(run_one(s, args, f"wave_lag{lag}", lag, args.coupling))
    out = {"kind": "s38_h12_wave_predicts_food", "steps": args.steps, "window": args.window,
           "period": args.period, "coupling": args.coupling, "lags": args.lags,
           "note": ("lag > 0: the crest arrives before the food (prediction); lag = 0: crest and food "
                    "coincide; lag < 0: the crest arrives after the food (chasing). wave_off is the "
                    "S27 control: wave present but not coupled to food."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("arm | overall | per seed | R1")
    for arm in ["no_wave", "wave_off"] + [f"wave_lag{l}" for l in args.lags]:
        ar = [r for r in rows if r["arm"] == arm]
        vals = [r["overall"] for r in ar if r["overall"] is not None]
        r1 = [r["R1"] for r in ar]
        print(f"{arm:12s} | {round(sum(vals) / len(vals), 3) if vals else None} "
              f"| {[round(v, 3) for v in vals]} | {sum(r1)}/{len(r1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
