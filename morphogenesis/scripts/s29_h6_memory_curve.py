"""S29 / H6: the memory-length curve — is there an optimal lag, and does it scale with how fast
the environment changes?

S28/H5 found the first field variant with a positive effect: a field whose source is the resource
`lag` steps ago. It helped while the food stayed put (+0.030, +0.068) and crashed right after the
patches jumped (-0.154), then recovered. That suggests the value of memory depends on how fast the
environment changes.

This script measures the curve directly: sweep the lag and repeat it at two rates of environmental
change, so the prediction "the optimal lag scales with the change rate" becomes testable.

Design:
  - the rich patches jump every `move_every` steps (0 = never move);
  - `--move-every 300` : one jump in a 600-step run (slow change);
  - `--move-every 100` : six jumps (fast change);
  - lags: 0 (no memory), 10, 40, 100, 200.

Readout: the favourable share over the whole run (mean of all windows) and per window, so both the
overall value of a lag and its stability across changes are visible. R1 is checked per run.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  the field has diffusion 0.10 and decay 0.05, so its own memory is a few steps; the lag is what
  sets how far back the SOURCE looks. With `move_every` 100 and 300 the environment changes on
  timescales comparable to the lags tested (10..200), so the sweep spans "memory much shorter than
  the change", "comparable", and "memory much longer". The colony is seeded on a patch (S12/D2) and
  stays viable; R1 is checked.
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


def run_one(seed, args, lag, move_every):
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
    windows, acc = [], None
    next_move = move_every if move_every > 0 else None
    toggle = False
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if next_move is not None and st >= next_move:
            toggle = not toggle
            move_patches(pond, (args.new_y, args.new_x) if toggle else (args.patch_y, args.patch_x))
            next_move += move_every
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
        fav = float((a & (res >= thr)).sum() / n)
        if acc is None:
            acc = {"start": st, "n": 0, "favs": [], "alive": 0}
        acc["n"] += 1
        acc["favs"].append(fav)
        acc["alive"] += n
        if acc["n"] >= args.window:
            mu = sum(acc["favs"]) / len(acc["favs"])
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(mu, 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = None
    if windows:
        overall = round(sum(w["favourable_share"] for w in windows) / len(windows), 4)
    return {"seed": seed, "lag": lag, "move_every": move_every, "windows": windows,
            "overall": overall,
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
    ap.add_argument("--mem-source", type=float, default=1.0)
    ap.add_argument("--lags", type=int, nargs="+", default=[0, 10, 40, 100, 200])
    ap.add_argument("--move-everys", type=int, nargs="+", default=[0, 300, 100])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for me in args.move_everys:
        for lag in args.lags:
            for s in args.seeds:
                rows.append(run_one(s, args, lag, me))
    out = {"kind": "s29_h6_memory_curve", "steps": args.steps, "window": args.window,
           "lags": args.lags, "move_everys": args.move_everys,
           "note": ("lag 0 is the no-memory control; move_every 0 = static environment, 300 = one "
                    "jump, 100 = six jumps. The prediction is that the best lag scales with the "
                    "change rate."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("lag | " + " | ".join(f"move_every={me}" for me in args.move_everys))
    for lag in args.lags:
        cells = []
        for me in args.move_everys:
            vals = [r["overall"] for r in rows
                    if r["lag"] == lag and r["move_every"] == me and r["overall"] is not None]
            r1 = [r["R1"] for r in rows if r["lag"] == lag and r["move_every"] == me]
            cells.append(f"{round(sum(vals) / len(vals), 3) if vals else None} (R1 {sum(r1)}/{len(r1)})")
        print(f"{lag:3d} | " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
