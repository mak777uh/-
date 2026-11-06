"""S28 / H5: does a MEMORY field help - a field whose source is where the food WAS?

S26/H2 showed a field built from living cells duplicates local information. S27/H4 showed an
external rhythm carries new information but unrelated to food. The remaining design is the one
that has both properties: a field whose source is the resource as it was `lag` steps ago. It
carries information the cell does not have locally (where the food used to be) AND that
information is about food.

The environment makes this testable: the rich patches MOVE. At `move_at` the three rich patches
jump to new positions, so a cell standing where the food was sees a strong memory field but no
food, while the food is somewhere it has never been. A cell that follows the memory will be
wrong; a cell that follows the memory only WHILE the food is still there may be right.

Arms:
  - `no_field`   : no field (control);
  - `mem_field`  : cells step up the memory-field gradient;
  - `now_field`  : cells step up a field built from the CURRENT resource (the S26-style control,
                   which we know duplicates local greed);
  - `mem_lag0`   : memory field with lag 0 - should reproduce `now_field` (sanity check that the
                   memory machinery is inert at lag 0).

Readout per window: favourable share, its within-window sd, field amplitude, moves per step, R1.
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
    """Move the three rich patches to a new place: zero the old ones, fill the new one."""
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    third = n // 3
    # old patch coordinates (as built by PondConfig patches layout)
    olds = [(third // 2, third // 2), (n - third, n - third), (third // 2, n - third)]
    for (y, x) in olds:
        s.resource[y:y + third // 2, x:x + third // 2] = cfg.resource_max * 0.2
    cy, cx = new_xy
    half = third // 2
    s.resource[max(0, cy - half):cy + half, max(0, cx - half):cx + half] = cfg.resource_max


def run_one(seed, args, arm):
    on = arm != "no_field"
    lag = 0 if arm == "mem_lag0" else (args.lag if arm == "mem_field" else 0)
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        signal_diffusion=(args.diffusion if on else 0.0),
        signal_decay=(args.decay if on else 0.0),
        signal_memory_lag=(lag if arm in ("mem_field", "mem_lag0") else 0),
        signal_memory_source=(args.mem_source if arm in ("mem_field", "mem_lag0") else 0.0),
        signal_source=(args.source if arm == "now_field" else 0.0),
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    windows, acc = [], None
    moved_patches = False
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if not moved_patches and st >= args.move_at:
            move_patches(pond, (args.new_y, args.new_x))
            moved_patches = True
        moved = 0
        if on:
            pond.update_signal()
            if s.signal is not None:
                moves = moves_up_field(pond, s.signal)
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
        amp = float(s.signal.abs().mean()) if s.signal is not None else 0.0
        if acc is None:
            acc = {"start": st, "n": 0, "favs": [], "amp": 0.0, "moved": 0, "alive": 0}
        acc["n"] += 1
        acc["favs"].append(fav)
        acc["amp"] += amp
        acc["moved"] += moved
        acc["alive"] += n
        if acc["n"] >= args.window:
            f = acc["favs"]
            mu = sum(f) / len(f)
            sd = (sum((v - mu) ** 2 for v in f) / len(f)) ** 0.5
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(mu, 4),
                            "stability_sd": round(sd, 4),
                            "field_amplitude": round(acc["amp"] / acc["n"], 4),
                            "moves_per_step": round(acc["moved"] / acc["n"], 1),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--move-at", type=int, default=300, help="step at which the rich patches jump")
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--patch-y", type=int, default=7)
    ap.add_argument("--patch-x", type=int, default=7)
    ap.add_argument("--new-y", type=int, default=24)
    ap.add_argument("--new-x", type=int, default=24)
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
    ap.add_argument("--source", type=float, default=1.0)
    ap.add_argument("--mem-source", type=float, default=1.0)
    ap.add_argument("--lag", type=int, default=40)
    ap.add_argument("--arms", nargs="+", default=["no_field", "mem_field", "now_field", "mem_lag0"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s28_h5_memory_field", "steps": args.steps, "window": args.window,
           "move_at": args.move_at, "new_patch": [args.new_y, args.new_x],
           "diffusion": args.diffusion, "decay": args.decay, "lag": args.lag,
           "note": ("the rich patches JUMP at move_at, so a cell standing where the food was sees a "
                    "strong memory field but no food - the memory is either useful (it points at "
                    "food that is still there) or harmful (it points at food that left)"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        print(f"== {arm}")
        for field in ("favourable_share", "stability_sd", "field_amplitude", "moves_per_step", "alive_mean"):
            vals = []
            for i in range(nw):
                v = [r["windows"][i][field] for r in ar if i < len(r["windows"])]
                vals.append(round(sum(v) / len(v), 3) if v else None)
            print(f"   {field:18s} {vals}")
        print(f"   R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
