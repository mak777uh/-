"""P0 behavior metric (plan-alive): survival/deaths by rich-vs-poor zone, before vs after gradient flip.

Uses PondRun directly so we can read per-step zone populations (not available in run_pond JSON log).
Zones follow pond._return_on_death / deaths_by_zone convention: rich = resource > 2/3*max, poor < 1/3*max.
'Correct' zone = the rich side (by current gradient position) at that step.
"""
from __future__ import annotations
import argparse, json, os, sys, time
import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def zone_masks(pond):
    cfg, s = pond.cfg, pond.state
    if cfg.resource_max <= 0:
        z = torch.zeros_like(s.resource, dtype=torch.bool)
        return z, z, ~z
    rich = s.resource > cfg.resource_max * 2 / 3
    poor = s.resource < cfg.resource_max / 3
    mid = ~rich & ~poor
    return rich, mid, poor


def correct_mask(pond):
    """Behaviorally meaningful zone: favorable half by current gradient position (flips with the environment).
    gradient_position is per row (1.0 = rich end now). Correct = top half now (pos >= 0.5)."""
    pos = pond._gradient_position()  # (grid,)
    grid = pond.cfg.grid
    # row mask broadcast to (grid,grid)
    return (pos >= 0.5)[:, None].expand(grid, grid)


def run_one(seed, args):
    # lethal-ish: proportional income, prefilled, high upkeep (calibratable). gradient+flip.
    cfg = PondConfig(
        grid=args.grid,
        resource_layout="gradient",
        income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill,
        baseline_income=args.income,
        update_cost=args.update_cost,
        repair_cost=args.repair_cost,
        budding_mass=24,
        budding_cost=0.2,
        resource_max=1.0,
        resource_regen=args.resource_regen,
        flip_at=args.flip_at,
        plastic_eta=args.plastic_eta,
        plastic_move_cost=args.plastic_move_cost,
        plastic_gate=args.plastic_gate,
        plastic_nomove=args.plastic_nomove,
        plastic_prob=args.plastic_prob,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    flip = args.flip_at
    pre = {"alive_rich": 0, "alive_poor": 0, "alive_mid": 0, "steps": 0, "deaths_rich": 0, "deaths_poor": 0, "deaths_mid": 0,
           "alive_correct": 0, "alive_wrong": 0, "deaths_correct": 0, "deaths_wrong": 0}
    post = {"alive_rich": 0, "alive_poor": 0, "alive_mid": 0, "steps": 0, "deaths_rich": 0, "deaths_poor": 0, "deaths_mid": 0,
            "alive_correct": 0, "alive_wrong": 0, "deaths_correct": 0, "deaths_wrong": 0}
    last_dz = {"rich": 0, "poor": 0, "mid": 0}
    t0 = time.perf_counter()
    for _ in range(args.steps):
        alive_before = run.pond.state.alive.clone()
        run.step()
        pond = run.pond
        rich, mid, poor = zone_masks(pond)
        corr = correct_mask(pond)
        a = pond.state.alive
        died = alive_before & ~a
        bucket = post if (flip and pond.state.step >= flip) else pre
        bucket["steps"] += 1
        bucket["alive_rich"] += int((a & rich).sum())
        bucket["alive_poor"] += int((a & poor).sum())
        bucket["alive_mid"] += int((a & mid).sum())
        bucket["alive_correct"] += int((a & corr).sum())
        bucket["alive_wrong"] += int((a & ~corr).sum())
        bucket["deaths_correct"] += int((died & corr).sum())
        bucket["deaths_wrong"] += int((died & ~corr).sum())
        dz = pond.state.deaths_by_zone
        for z in ("rich", "poor", "mid"):
            d = int(dz.get(z, 0)) - last_dz[z]
            bucket[f"deaths_{z}"] += max(d, 0)
            last_dz[z] = int(dz.get(z, 0))
    elapsed = time.perf_counter() - t0
    # "correct" = rich zone relative to resource (post-flip the gradient inverts via _gradient_position,
    # so 'rich' by resource level remains the favorable zone; metric compares rich-share before vs after).
    def pack(b):
        ar, ap = b["alive_rich"], b["alive_poor"]
        denom = ar + ap
        dr, dp = b["deaths_rich"], b["deaths_poor"]
        dden = dr + dp
        ac, aw = b.get("alive_correct", 0), b.get("alive_wrong", 0)
        cden = ac + aw
        dc, dw = b.get("deaths_correct", 0), b.get("deaths_wrong", 0)
        dcden = dc + dw
        return {
            **b,
            "alive_rich_share": (ar / denom) if denom else None,
            "deaths_rich_share": (dr / dden) if dden else None,
            "alive_rich_per_step": (ar / b["steps"]) if b["steps"] else 0,
            "alive_poor_per_step": (ap / b["steps"]) if b["steps"] else 0,
            "alive_correct_share": (ac / cden) if cden else None,
            "deaths_correct_share": (dc / dcden) if dcden else None,
            "alive_correct_per_step": (ac / b["steps"]) if b["steps"] else 0,
        }
    pre_p, post_p = pack(pre), pack(post)
    final = run.log[-1] if run.log else {}
    return {
        "seed": seed,
        "config": {"grid": args.grid, "income": args.income, "update_cost": args.update_cost,
                   "repair_cost": args.repair_cost, "init_resource_fill": args.init_resource_fill,
                   "resource_regen": args.resource_regen, "flip_at": args.flip_at, "steps": args.steps,
                   "layout": "gradient", "income_mode": args.income_mode, "seed_cells": args.seed_cells,
                   "seed_energy": args.seed_energy, "plastic_eta": args.plastic_eta,
                   "plastic_move_cost": args.plastic_move_cost, "plastic_gate": args.plastic_gate},
        "before_flip": pre_p,
        "after_flip": post_p,
        "final": {"alive": final.get("alive_cells"), "born": final.get("born"), "died": final.get("died")},
        "deaths_by_zone_total": dict(run.pond.state.deaths_by_zone),
        "wall_seconds": round(elapsed, 2),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--flip-at", type=int, default=150)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--income", type=float, default=0.04)
    ap.add_argument("--update-cost", type=float, default=0.06)
    ap.add_argument("--repair-cost", type=float, default=0.04)
    ap.add_argument("--init-resource-fill", type=float, default=0.9)
    ap.add_argument("--resource-regen", type=float, default=0.02)
    ap.add_argument("--income-mode", default="proportional", choices=["cap", "proportional"])
    ap.add_argument("--seed-cells", type=int, default=4)
    ap.add_argument("--seed-energy", type=float, default=8.0)
    ap.add_argument("--plastic-eta", type=float, default=0.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.05)
    ap.add_argument("--plastic-gate", default="pred", choices=["pred","random"])
    ap.add_argument("--plastic-nomove", action="store_true")
    ap.add_argument("--plastic-prob", type=float, default=0.5)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rows = [run_one(s, args) for s in args.seeds]
    # aggregate
    def mean(keypath, rs):
        vals = []
        for r in rs:
            v = r
            for k in keypath: v = v[k]
            if v is not None: vals.append(v)
        return (sum(vals) / len(vals)) if vals else None
    agg = {
        "kind": "p0_flip_behavior_metric",
        "plan": "docs/plan-alive.md P0",
        "metric_note": "resource-threshold zones (rich/poor) + gradient-half 'correct' zone that flips with environment; primary P0 read uses alive_correct_share before/after.",
        "n_seeds": len(rows),
        "alive_final_mean": mean(("final","alive"), rows),
        "died_total_mean": mean(("final","died"), rows),
        "rich_share_before_mean": mean(("before_flip","alive_rich_share"), rows),
        "rich_share_after_mean": mean(("after_flip","alive_rich_share"), rows),
        "correct_share_before_mean": mean(("before_flip","alive_correct_share"), rows),
        "correct_share_after_mean": mean(("after_flip","alive_correct_share"), rows),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(agg, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: agg[k] for k in ("kind","n_seeds","alive_final_mean","died_total_mean","correct_share_before_mean","correct_share_after_mean")}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
