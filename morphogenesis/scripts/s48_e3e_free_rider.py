"""S48 / E3e: is the niche-construction failure caused by the FREE-RIDER problem?

E3 gave a negative result: at every usable strength the closed loop was WORSE than the placebo
(gap -0.016 to -0.042). The proposed explanation is the free-rider problem: a cell fertilises its
site, then moves away, and the neighbours harvest what it built. The builder pays, everyone gains.

That explanation makes a sharp, testable prediction:

    if the cells CANNOT move, the benefit cannot leak away, and the loop should pay.

Design: the same three arms as s46 (closed / open / frozen), run at two mobilities:
  - `mobile`   : the normal world - cells step to the best neighbour when short of their prediction;
  - `immobile` : cells never move (plastic_nomove), everything else identical.

Prediction if the free-rider explanation is right:
  - `mobile`   : closed <= open (reproducing E3's negative gap);
  - `immobile` : closed >  open (the loop pays once the benefit stays where it was built).

If `immobile` ALSO shows closed <= open, the free-rider explanation is wrong and the niche simply
does not work in this geometry at all - which is a different and equally useful answer.

The arithmetic guard from s46 is kept: the run refuses to start if the niche would add more than
`max_share` of one cell's consumption, and any run whose favourable share exceeds `max_fav` is
flagged as saturated.
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


def moves_up_resource(pond):
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
    return moves


def run_one(seed, args, arm, mobility):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    n = cfg.grid
    niche = torch.zeros((n, n), device=run.device)
    favs = []
    for _ in range(args.steps):
        prev_res = pond.state.resource.clone()
        run.step()
        s = pond.state
        if mobility == "mobile" and bool(s.alive.any()):
            mv = moves_up_resource(pond)
            if mv:
                pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
        consumed = (prev_res - s.resource).clamp_min(0.0) * s.alive.float()
        built = args.construct * consumed
        niche = niche * (1.0 - args.gamma) + built
        if arm == "closed":
            s.resource = torch.clamp(
                s.resource + args.niche_gain * niche * cfg.resource_regen, max=cfg.resource_max)
        elif arm == "open":
            s.energy = torch.clamp(s.energy - args.construct * consumed, min=0.0)
        # frozen: the field is tracked but contributes nothing
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / cnt))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    peak = round(max(favs), 4) if favs else None
    return {"seed": seed, "arm": arm, "mobility": mobility, "overall": overall, "peak_fav": peak,
            "saturated": bool(peak is not None and peak > args.max_fav),
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
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
    ap.add_argument("--construct", type=float, default=0.5)
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--niche-gain", type=float, default=0.2)
    ap.add_argument("--max-share", type=float, default=0.25)
    ap.add_argument("--max-fav", type=float, default=0.85)
    ap.add_argument("--mobilities", nargs="+", default=["mobile", "immobile"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    eat = args.income * 1.0 * 4.0
    niche_steady = args.construct * eat / max(args.gamma, 1e-6)
    contribution = args.niche_gain * niche_steady * args.resource_regen
    cap = args.max_share * eat
    print(f"[e3e] eats {eat:.4f}/step; niche steady {niche_steady:.3f}; "
          f"contribution {contribution:.4f}; cap {cap:.4f}")
    if contribution > cap:
        raise SystemExit(f"[e3e] REFUSED: niche contributes {contribution:.4f} > cap {cap:.4f}")

    rows = []
    for mob in args.mobilities:
        for s in args.seeds:
            for arm in ("closed", "open", "frozen"):
                rows.append(run_one(s, args, arm, mob))
    out = {"kind": "s48_e3e_free_rider", "steps": args.steps, "construct": args.construct,
           "gamma": args.gamma, "niche_gain": args.niche_gain, "mobilities": args.mobilities,
           "arithmetic": {"eat": eat, "contribution": round(contribution, 5), "cap": round(cap, 5)},
           "note": ("free-rider test: if the negative gap is caused by the benefit leaking to "
                    "neighbours, then IMMOBILE cells should show a POSITIVE gap"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for mob in args.mobilities:
        print(f"== mobility {mob}")
        vals = {}
        for arm in ("closed", "open", "frozen"):
            ar = [r for r in rows if r["arm"] == arm and r["mobility"] == mob]
            v = [r["overall"] for r in ar if r["overall"] is not None]
            vals[arm] = round(sum(v) / len(v), 3) if v else None
            sat = sum(r["saturated"] for r in ar)
            print(f"   {arm:7s} {vals[arm]} | saturated {sat}/{len(ar)} "
                  f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
        if vals["closed"] is not None and vals["open"] is not None:
            print(f"   GAP closed-open = {vals['closed'] - vals['open']:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
