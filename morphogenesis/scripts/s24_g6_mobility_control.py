"""S24 / G6: is the fixed reference better because of the reference, or just because it moves more?

S22/G3 and S23/G4 found that a FIXED reference (the resource at seeding time) beats an adaptive
EMA reference by a wide margin (+0.34 vs -0.17 under slow recovery). But the fixed reference also
makes about TEN TIMES more cells qualify to move (422 vs 21 on average). So the gain could be a
mobility effect, not a reference effect.

This script separates the two by holding the NUMBER OF MOVING CELLS FIXED:

  - `baseline`     : no movement;
  - `fixed_all`    : fixed reference, every qualifying cell may move (the G3/G4 arm);
  - `fixed_capped` : fixed reference, but at most as many cells move per step as the adaptive
                     arm would have moved (the cap is measured from the adaptive arm at the same
                     step, so the mobility budget is identical);
  - `ema`          : adaptive reference (the S19/G1 arm).

If `fixed_capped` keeps most of the gain of `fixed_all`, the effect is the REFERENCE. If it falls
back to the `ema` level, the effect was just more movement.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  slow recovery (resource_regen 0.010) -> patch inflow 0.040/step vs 0.160 eaten, the regime where
  the trap appears. The cap is taken from the adaptive arm's own qualifying count at the same step,
  so the comparison is paired by construction. R1 is checked per run.
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


def greedy_moves(pond, reference, cap=None):
    """Greedy moves gated by `reference`; if `cap` is given, at most that many cells move."""
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    poor = s.alive & (s.resource < reference) & (s.energy > cfg.plastic_move_cost)
    n_qualify = int(poor.sum())
    if n_qualify == 0:
        return [], 0
    cand = poor.nonzero(as_tuple=False)
    order = torch.randperm(cand.shape[0], generator=pond.gen_sel)
    if cap is not None and cap < len(order):
        order = order[:cap]
    taken = torch.zeros_like(s.alive)
    moves = []
    for k in order.tolist():
        y, x = int(cand[k, 0]), int(cand[k, 1])
        if not bool(s.alive[y, x]) or bool(taken[y, x]):
            continue
        best, best_v = None, float(s.resource[y, x])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                continue
            v = float(s.resource[ny, nx])
            if v > best_v:
                best, best_v = (ny, nx), v
        if best is None:
            continue
        taken[best[0], best[1]] = True
        moves.append((y, x, best[0], best[1]))
    return moves, n_qualify


def greedy_moves_absolute(pond, reference, budget):
    """G7: move EXACTLY `budget` cells (or as many as qualify), chosen by `reference`.

    The budget is an absolute number per step, identical in both reference arms, so the arms
    differ only in WHICH cells are picked, never in how many move.
    """
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    poor = s.alive & (s.resource < reference) & (s.energy > cfg.plastic_move_cost)
    n_qualify = int(poor.sum())
    if n_qualify == 0 or budget <= 0:
        return [], 0
    cand = poor.nonzero(as_tuple=False)
    order = torch.randperm(cand.shape[0], generator=pond.gen_sel)
    order = order[:budget]
    taken = torch.zeros_like(s.alive)
    moves = []
    for k in order.tolist():
        y, x = int(cand[k, 0]), int(cand[k, 1])
        if not bool(s.alive[y, x]) or bool(taken[y, x]):
            continue
        best, best_v = None, float(s.resource[y, x])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                continue
            v = float(s.resource[ny, nx])
            if v > best_v:
                best, best_v = (ny, nx), v
        if best is None:
            continue
        taken[best[0], best[1]] = True
        moves.append((y, x, best[0], best[1]))
    return moves, n_qualify


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


def run_one(seed, args, arm, regen):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    fixed_ref = pond.state.resource.clone()
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        moved = 0
        if arm != "baseline" and bool(s.alive.any()):
            if arm == "ema":
                moves, _ = greedy_moves(pond, s.pred)
            elif arm == "fixed_all":
                moves, _ = greedy_moves(pond, fixed_ref)
            elif arm in ("ema_abs", "fixed_abs"):
                # G7: identical ABSOLUTE budget; only the reference differs
                ref = s.pred if arm == "ema_abs" else fixed_ref
                moves, _ = greedy_moves_absolute(pond, ref, args.budget)
            else:  # fixed_capped: same mobility budget as the adaptive arm
                _, ema_budget = greedy_moves(pond, s.pred, cap=0)  # count only
                moves, _ = greedy_moves(pond, fixed_ref, cap=max(ema_budget, 0))
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
                moved = len(moves)
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
            acc = {"start": st, "n": 0, "fav": 0.0, "moved": 0, "alive": 0}
        acc["n"] += 1
        acc["fav"] += fav
        acc["moved"] += moved
        acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "moves_per_step": round(acc["moved"] / acc["n"], 1),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "resource_regen": regen, "windows": windows,
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
    ap.add_argument("--resource-regen", type=float, default=0.010)
    ap.add_argument("--patch-inflow-base", type=float, default=0.1)
    ap.add_argument("--patch-inflow-rich", type=float, default=4.0)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--arms", nargs="+", default=["baseline", "ema", "fixed_all", "fixed_capped"])
    ap.add_argument("--budget", type=int, default=20,
                    help="G7: absolute number of cells allowed to move per step in the *_abs arms")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm, args.resource_regen))
    out = {"kind": "s24_g6_mobility_control", "steps": args.steps, "window": args.window,
           "resource_regen": args.resource_regen,
           "sensitivity_note": ("fixed_capped takes its per-step mobility budget from the ema arm's own "
                                "qualifying count at the same step, so the two arms differ only in the "
                                "REFERENCE, not in how much they move"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        fav, mov = [], []
        for i in range(nw):
            f = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
            m = [r["windows"][i]["moves_per_step"] for r in ar if i < len(r["windows"])]
            fav.append(round(sum(f) / len(f), 3) if f else None)
            mov.append(round(sum(m) / len(m), 1) if m else None)
        print(f"== {arm:12s} fav {fav}")
        print(f"   {'':12s} mov {mov} | R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
