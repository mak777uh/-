"""S34 / H11: is the memory field just a smoothed resource? Field vs plain smoothing at equal width.

S33/H10 found that a cell barely moves (0.14 cells from its birth cell), so the memory field cannot be
long-range vision: it must act as a local smoother of the resource. That gives a sharp, cheap test:

    if the field is only a smoother, then a PLAIN smoothing of the resource - no field, no memory,
    no diffusion - should do the same job at the same window width.

Arms (all at mobility 1, patches layout, colony seeded on a patch):
  - `no_field`      : no movement (control);
  - `mem_field`     : the memory field (lag 10, diffusion 0.10, decay 0.05) - the H6-H10 best;
  - `smooth_r1`     : step up the resource smoothed over a 3x3 window (radius 1), no field;
  - `smooth_r3`     : step up the resource smoothed over a 7x7 window (radius 3), no field;
  - `smooth_r5`     : step up the resource smoothed over an 11x11 window (radius 5), no field.

The radii bracket the effective width of the memory field, so if smoothing is the whole story one of
them should match `mem_field` and the field itself is unnecessary.

Readout: favourable share averaged over the run, per arm; plus the within-window sd. R1 checked.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  the field diffuses with coefficient 0.10 for `lag` 10 steps, so its effective spread is on the order
  of sqrt(4*0.10*10) ~ 2 cells, i.e. a 5x5 neighbourhood. `smooth_r3` (7x7) is the closest plain
  analogue, with r1 and r5 bracketing it. The comparison is therefore not rigged in favour of either
  arm.
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


def smooth(res: torch.Tensor, radius: int) -> torch.Tensor:
    r = int(radius)
    if r <= 0:
        return res
    x = res.unsqueeze(0).unsqueeze(0)
    x = torch.nn.functional.pad(x, (r, r, r, r), mode="replicate")
    k = 2 * r + 1
    w = torch.ones((1, 1, k, k), dtype=res.dtype, device=res.device) / (k * k)
    return torch.nn.functional.conv2d(x, w).squeeze(0).squeeze(0)


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


ARMS = {
    "no_field": None,
    "mem_field": "field",
    "smooth_r1": 1,
    "smooth_r3": 3,
    "smooth_r5": 5,
}


def run_one(seed, args, arm):
    spec = ARMS[arm]
    use_field = spec == "field"
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        signal_diffusion=(args.diffusion if use_field else 0.0),
        signal_decay=(args.decay if use_field else 0.0),
        signal_memory_lag=(args.lag if use_field else 0),
        signal_memory_source=(args.mem_source if use_field else 0.0),
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        s = pond.state
        if spec is not None and bool(s.alive.any()):
            if use_field:
                pond.update_signal()
                field = s.signal
            else:
                field = smooth(s.resource, int(spec))
            if field is not None:
                mv = moves_up_field(pond, field)
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
        fav = float((a & (res >= thr)).sum() / n)
        if acc is None:
            acc = {"n": 0, "favs": [], "alive": 0}
        acc["n"] += 1
        acc["favs"].append(fav)
        acc["alive"] += n
        if acc["n"] >= args.window:
            mu = sum(acc["favs"]) / len(acc["favs"])
            windows.append({"favourable_share": round(mu, 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(w["favourable_share"] for w in windows) / len(windows), 4) if windows else None
    return {"seed": seed, "arm": arm, "windows": windows, "overall": overall,
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
    ap.add_argument("--arms", nargs="+", default=list(ARMS))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for arm in args.arms:
        for s in args.seeds:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s34_h11_field_vs_smoothing", "steps": args.steps, "window": args.window,
           "lag": args.lag, "diffusion": args.diffusion, "decay": args.decay,
           "note": ("if the memory field is only a smoother, one of the plain smoothing radii should "
                    "match it; the field's effective spread is ~sqrt(4*0.10*10) ~ 2 cells (5x5), so "
                    "smooth_r3 (7x7) is the closest analogue"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        vals = [r["overall"] for r in ar if r["overall"] is not None]
        r1 = [r["R1"] for r in ar]
        print(f"{arm:12s} overall {round(sum(vals) / len(vals), 3) if vals else None} "
              f"| per seed {[round(v, 3) for v in vals]} | R1 {sum(r1)}/{len(r1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
