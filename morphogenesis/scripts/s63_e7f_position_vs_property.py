"""S63 / E7f: is the fate of a cell set by WHERE it is, not by WHAT it is?

Five attempts (s59-s62) failed to make selection shift a heritable trait. The explanation those
failures suggest is: a cell's fate is decided by its POSITION, not by its properties. This script
tests that directly, without adding any mechanism.

Design. One run of the ordinary world. Every `sample_every` steps, for each living cell, record:
  - its position class (`rich` = in the top half of cells by resource, else `poor`);
  - its energy, age, density (the quantities E7 found to matter);
  - whether it is still alive `horizon` steps later.

Then, WITHIN each position class, compute the same quartile differentials that E7 computed globally:

  - if the position is what decides, then INSIDE a class the differentials should COLLAPSE toward zero
    (all cells in the rich zone fare alike, whatever their energy or age);
  - if the properties still matter inside a class, the differentials should survive.

This separates "the world selects on position" from "the world selects on properties", which is the
conclusion the five failed attempts point at.

Readout: for each position class, P(survive | low quartile) vs P(survive | high quartile) of energy,
age and density. R1 checked per run.
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


def local_density(alive: torch.Tensor, radius: int) -> torch.Tensor:
    a = alive.float().unsqueeze(0).unsqueeze(0)
    k = 2 * radius + 1
    box = torch.nn.functional.avg_pool2d(
        torch.nn.functional.pad(a, (radius, radius, radius, radius), mode="replicate"),
        k, stride=1) * (k * k)
    return box.squeeze(0).squeeze(0) - alive.float()


def run_one(seed, args):
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
    age = torch.zeros((n, n), device=run.device)
    pending, records = [], []
    prev = torch.zeros((n, n), dtype=torch.bool, device=run.device)
    for step in range(1, args.steps + 1):
        run.step()
        s = pond.state
        a = s.alive
        age = (age + 1.0) * (a & prev).float()
        prev = a.clone()
        if step % args.sample_every == 0 and int(a.sum()) > 10:
            dens = local_density(a, args.radius)
            res = s.resource
            flat = res.reshape(-1)
            k = max(1, flat.numel() // 2)
            thr = float(torch.topk(flat, k=k, largest=True).values.min())
            ys, xs = a.nonzero(as_tuple=True)
            pending.append({
                "step": step, "y": ys.clone(), "x": xs.clone(),
                "rich": (res[ys, xs] >= thr).cpu(),
                "energy": s.energy[ys, xs].cpu(),
                "age": age[ys, xs].cpu(),
                "density": dens[ys, xs].cpu(),
            })
        while pending and step - pending[0]["step"] >= args.horizon:
            obs = pending.pop(0)
            ys, xs = obs["y"], obs["x"]
            records.append({**{k: obs[k] for k in ("rich", "energy", "age", "density")},
                            "survived": a[ys, xs].float().cpu()})
    final = run.log[-1] if run.log else {}
    return records, {"alive": int(pond.state.alive.sum()), "died": final.get("died", 0),
                     "R1": bool(final.get("died", 0) >= 10 and int(pond.state.alive.sum()) >= 10)}


def quartile(records, key, target="survived"):
    if not records:
        return None
    vals = torch.cat([r[key] for r in records]).float()
    tgt = torch.cat([r[target] for r in records]).float()
    if vals.numel() < 40:
        return None
    q25 = float(torch.quantile(vals, 0.25))
    q75 = float(torch.quantile(vals, 0.75))
    lo, hi = vals <= q25, vals >= q75
    if int(lo.sum()) < 8 or int(hi.sum()) < 8:
        return None
    return {"p_low": round(float(tgt[lo].mean()), 4), "p_high": round(float(tgt[hi].mean()), 4),
            "diff": round(float(tgt[hi].mean() - tgt[lo].mean()), 4),
            "n_low": int(lo.sum()), "n_high": int(hi.sum())}


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
    ap.add_argument("--seed-cells", type=int, default=128)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--sample-every", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    all_records, finals = [], []
    for s in args.seeds:
        recs, fin = run_one(s, args)
        all_records.extend(recs)
        finals.append(fin)
        print(f"[e7f] seed {s}: {len(recs)} observations, alive {fin['alive']}, R1 {fin['R1']}")

    rich = [r for r in all_records if bool(r["rich"][0])]
    poor = [r for r in all_records if not bool(r["rich"][0])]
    print(f"\nrich-zone observations: {len(rich)} | poor-zone: {len(poor)}")
    print(f"overall survival: rich {torch.cat([r['survived'] for r in rich]).mean():.3f} "
          f"| poor {torch.cat([r['survived'] for r in poor]).mean():.3f}")

    table = {}
    for label, subset in (("rich", rich), ("poor", poor)):
        table[label] = {k: quartile(subset, k) for k in ("energy", "age", "density")}
        print(f"\n== inside the {label} zone")
        for k, v in table[label].items():
            if v:
                print(f"   {k:8s} survive {v['p_low']:.3f} -> {v['p_high']:.3f} ({v['diff']:+.3f})")
            else:
                print(f"   {k:8s} n/a")

    out = {"kind": "s63_e7f_position_vs_property", "steps": args.steps,
           "n_observations": len(all_records), "finals": finals,
           "survival_rich": round(float(torch.cat([r["survived"] for r in rich]).mean()), 4) if rich else None,
           "survival_poor": round(float(torch.cat([r["survived"] for r in poor]).mean()), 4) if poor else None,
           "table": table,
           "note": ("if position decides, the property differentials should COLLAPSE inside each "
                    "position class; if properties still matter, they survive")}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\n[e7f] written {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
