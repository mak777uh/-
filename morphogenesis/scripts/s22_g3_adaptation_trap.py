"""S22 / G3: does turning OFF prediction adaptation remove the adaptation trap?

S21/G2 found the mechanism behind the harmful greed under slow resource recovery: the step
rule fires only when `resource < pred`, and `pred` is an EMA that tracks the falling
resource, so cells stop noticing that they are in a bad place. At step 300 only 3 of 45
cells still qualified to move; by step 400, 102 of 108 living cells sat on depleted cells.

That gives a sharp, falsifiable prediction: if the prediction is NOT adapted (a fixed
reference instead of an EMA), cells should keep noticing the drop and leave, and the
negative gap under slow recovery should disappear.

Arms (slow recovery, where the trap appears):
  - `baseline`   : no movement (control);
  - `greedy_ema` : movement gated by the adaptive prediction (the S19/G1 setting);
  - `greedy_fix` : movement gated by a FIXED reference = the resource at seeding time.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  resource_regen = 0.010 -> patch inflow 0.040/step vs one cell eating 0.160 -> a patch
  cell depletes, which is the condition under which the trap appears in S19/G1.
  income(res) = 0.04*res*4, spent = 0.060, so a full patch cell nets +0.100 and the colony
  stays viable (R1 is checked per run).

Readout per window: favourable share, share of living cells on depleted cells
(resource < 0.3), and how many cells qualify to move (resource < reference).
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


def moves_with_reference(pond, reference):
    """Engine-style greedy moves, but gated by an arbitrary reference field."""
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    poor = s.alive & (s.resource < reference) & (s.energy > cfg.plastic_move_cost)
    if not bool(poor.any()):
        return [], 0
    n_qualify = int(poor.sum())
    cand = poor.nonzero(as_tuple=False)
    order = torch.randperm(cand.shape[0], generator=pond.gen_sel)
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
    # fixed reference: the resource field at seeding time (never updated)
    fixed_ref = pond.state.resource.clone()
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        n_qualify = 0
        if arm != "baseline" and bool(s.alive.any()):
            ref = s.pred if arm == "greedy_ema" else fixed_ref
            moves, n_qualify = moves_with_reference(pond, ref)
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
        rich = res >= thr
        fav = float((a & rich).sum() / n)
        depleted = float((a & (res < args.depleted_threshold)).sum() / n)
        if acc is None:
            acc = {"start": st, "n": 0, "fav": 0.0, "dep": 0.0, "qual": 0, "alive": 0}
        acc["n"] += 1
        acc["fav"] += fav
        acc["dep"] += depleted
        acc["qual"] += n_qualify
        acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "on_depleted_share": round(acc["dep"] / acc["n"], 4),
                            "qualify_to_move": round(acc["qual"] / acc["n"], 1),
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
    ap.add_argument("--depleted-threshold", type=float, default=0.3)
    ap.add_argument("--arms", nargs="+", default=["baseline", "greedy_ema", "greedy_fix"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm, args.resource_regen))
    out = {"kind": "s22_g3_adaptation_trap", "steps": args.steps, "window": args.window,
           "resource_regen": args.resource_regen, "depleted_threshold": args.depleted_threshold,
           "sensitivity_note": ("regen 0.010 -> patch inflow 0.040/step vs 0.160 eaten, i.e. the "
                                "depleting regime where S19/G1 found the trap"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        print(f"== {arm}")
        for field in ("favourable_share", "on_depleted_share", "qualify_to_move", "alive_mean"):
            vals = []
            for i in range(nw):
                v = [r["windows"][i][field] for r in ar if i < len(r["windows"])]
                vals.append(round(sum(v) / len(v), 3) if v else None)
            print(f"   {field:20s} {vals}")
        print(f"   R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
