"""S56 / E8: diagnose the ENVIRONMENT from first principles.

E7 asked the world "is there anything to select on?" and answered YES: survival and division differ
strongly by age and energy. But E7 only looked at the BODIES. The other half of the world is the
FIELD, and we have never diagnosed it.

This script measures quantities that the environment ALREADY HAS, without adding any mechanism:

  - `patch_lifetime`  : how many steps a rich patch survives when NOBODY eats it (a run with no
                        cells, only the resource dynamics);
  - `recovery_time`   : how many steps a depleted cell needs to return to 90 % of its ceiling;
  - `occupancy`       : what fraction of the rich zone is actually occupied by bodies;
  - `autocorrelation` : how long the resource field remembers its own past (lag-1 and lag-k);
  - `body_to_env`     : the ratio of a body's lifetime to the environment's recovery time.

Why these: they are the quantities that decide whether a body can ever "use" the environment. If the
environment changes much faster than a body lives, no body can adapt to it; if it is much slower, the
environment is effectively constant and there is nothing to adapt to. The interesting regime is the
middle, and the ratio measures where we are.

Readout: one JSON with the five quantities, each with the seeds it was computed from. R1 is checked
for the runs that have bodies.
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


def make_cfg(args):
    return PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
    )


def empty_world(args, seed):
    """A world with NO cells: only the resource dynamics run."""
    run = PondRun(world_cfg=make_cfg(args), seed=seed, device=args.device,
                  rule_checkpoint=args.checkpoint)
    return run


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


def measure_environment(args, seed):
    """patch lifetime, recovery time, autocorrelation - measured with NO cells."""
    run = empty_world(args, seed)
    pond = run.pond
    n = args.grid
    # start with the patches full and the rest poor, then let the field evolve untouched
    res0 = pond.state.resource.clone()
    flat = res0.reshape(-1)
    k = max(1, flat.numel() // 2)
    thr0 = float(torch.topk(flat, k=k, largest=True).values.min())
    rich_mask = res0 >= thr0

    # deplete the rich zone completely, then time the recovery to 90 % of its starting value
    target = float(res0[rich_mask].mean()) * 0.9
    pond.state.resource[rich_mask] = 0.0
    recovery = None
    hist = []
    for step in range(1, args.env_steps + 1):
        run.step()
        r = pond.state.resource
        hist.append(r.clone())
        if recovery is None and float(r[rich_mask].mean()) >= target:
            recovery = step
    # patch lifetime: how long the rich zone stays above 90 % of its ceiling with no eaters
    life = None
    for i, r in enumerate(hist, start=1):
        if float(r[rich_mask].mean()) < 0.9 * target / 0.9:
            life = i
            break
    if life is None:
        life = len(hist)
    # autocorrelation of the field at lags 1, 5, 20
    ac = {}
    for lag in (1, 5, 20):
        if len(hist) > lag + 5:
            a = torch.stack(hist[:-lag]).flatten()
            b = torch.stack(hist[lag:]).flatten()
            a = a - a.mean()
            b = b - b.mean()
            denom = float((a * a).mean() ** 0.5 * (b * b).mean() ** 0.5)
            ac[f"lag{lag}"] = round(float((a * b).mean()) / denom, 4) if denom > 0 else None
    return {"recovery_time": recovery, "patch_lifetime": life, "autocorr": ac,
            "rich_cells": int(rich_mask.sum()), "target": round(target, 4)}


def measure_occupancy(args, seed):
    """fraction of the rich zone occupied by bodies, and the body lifetime."""
    run = PondRun(world_cfg=make_cfg(args), seed=seed, device=args.device,
                  rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    occ, ages, alive_hist = [], [], []
    n = args.grid
    age = torch.zeros((n, n), device=run.device)
    prev = torch.zeros((n, n), dtype=torch.bool, device=run.device)
    for step in range(1, args.steps + 1):
        run.step()
        s = pond.state
        a = s.alive
        age = (age + 1.0) * (a & prev).float()
        prev = a.clone()
        if step % 10 == 0 and bool(a.any()):
            res = s.resource
            flat = res.reshape(-1)
            k = max(1, flat.numel() // 2)
            thr = float(torch.topk(flat, k=k, largest=True).values.min())
            rich = res >= thr
            rc = int(rich.sum())
            if rc:
                occ.append(float((a & rich).sum()) / rc)
            ages.append(float(age[a].mean()))
            alive_hist.append(int(a.sum()))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"occupancy": round(sum(occ) / len(occ), 4) if occ else None,
            "mean_age": round(sum(ages) / len(ages), 2) if ages else None,
            "alive_mean": round(sum(alive_hint := alive_hist) / len(alive_hist), 1) if alive_hist else None,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--env-steps", type=int, default=400)
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
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    env_rows, occ_rows = [], []
    for s in args.seeds:
        env_rows.append(measure_environment(args, s))
        occ_rows.append(measure_occupancy(args, s))
        print(f"[e8] seed {s}: recovery {env_rows[-1]['recovery_time']}, "
              f"lifetime {env_rows[-1]['patch_lifetime']}, occupancy {occ_rows[-1]['occupancy']}, "
              f"mean age {occ_rows[-1]['mean_age']}")

    def mean_of(rows, key):
        v = [r[key] for r in rows if r.get(key) is not None]
        return round(sum(v) / len(v), 3) if v else None

    rec = mean_of(env_rows, "recovery_time")
    age = mean_of(occ_rows, "mean_age")
    out = {"kind": "s56_e8_environment_diagnosis", "steps": args.steps,
           "env_steps": args.env_steps, "n_seeds": len(args.seeds),
           "environment": env_rows, "occupancy": occ_rows,
           "summary": {
               "recovery_time": rec,
               "patch_lifetime": mean_of(env_rows, "patch_lifetime"),
               "occupancy": mean_of(occ_rows, "occupancy"),
               "mean_body_age": age,
               "body_to_env_ratio": round(age / rec, 3) if (age and rec) else None,
           },
           "note": ("nothing is added to the rules; the script measures quantities the environment "
                    "already has: how fast it recovers, how long a patch lasts, how much of the rich "
                    "zone bodies occupy, and how long the field remembers its own past")}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    su = out["summary"]
    print(f"\nrecovery_time {su['recovery_time']} steps | patch_lifetime {su['patch_lifetime']} "
          f"| occupancy {su['occupancy']} | mean_body_age {su['mean_body_age']} "
          f"| body_to_env {su['body_to_env_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
