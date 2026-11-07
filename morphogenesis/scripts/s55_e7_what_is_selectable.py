"""S55 / E7: is there anything to select on in this world at all?

The owner's point: this is not biology, and the optimal forms may differ. So instead of importing
another mechanism (field, niche, membrane, decoder - all four failed), this script asks the world a
direct question:

    DOES SURVIVAL OR REPRODUCTIVE SUCCESS DIFFER BY ANY QUANTITY THAT ALREADY EXISTS?

Nothing is added to the rules. The world runs exactly as before; the script only OBSERVES, for every
cell at every step, the quantities that the world already contains:

  - `age`        : how many steps the cell has lived (follows from death existing);
  - `density`    : how many living cells within Chebyshev radius R (follows from bodies sharing space);
  - `rich`       : whether the cell stands in the top half of cells by current resource;
  - `energy`     : its current energy;
  - `mass`       : its current mass.

For each of these, the script records whether the cell was still alive `horizon` steps later, and
whether it divided within that horizon. Then it reports, per quantity:

  - `P(survive | low quartile)` vs `P(survive | high quartile)` of that quantity;
  - the same for `P(divide | ...)`;
  - the difference, which is the SELECTION DIFFERENTIAL on that quantity.

If every differential is within noise, there is nothing to select on in this world, and the honest
next step is to change the world rather than to add another mechanism. If some differential is real,
we know WHICH quantity the world discriminates by, and can build from there.

Readout: per-quantity table of survival and division probabilities for the low and high quartiles,
with the number of observations. R1 checked per run.
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
    """Number of living cells within Chebyshev radius `radius` (excluding the cell itself)."""
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

    # per-cell bookkeeping: age, and a birth counter
    age = torch.zeros((n, n), device=run.device)
    births = torch.zeros((n, n), device=run.device)

    # observations: (quantity values, survived, divided) collected every `sample_every` steps,
    # then resolved `horizon` steps later
    pending = []          # list of dicts with tensors
    records = []          # resolved observations

    prev_alive = torch.zeros((n, n), dtype=torch.bool, device=run.device)
    for step in range(1, args.steps + 1):
        run.step()
        s = pond.state
        a = s.alive
        # age: survivors age by one, newborns start at zero
        age = (age + 1.0) * (a & prev_alive).float()
        # births: cells that appeared this step
        new = a & ~prev_alive
        if bool(new.any()):
            births = births.clone()
            births[new] = births[new] + 1.0
        prev_alive = a.clone()

        # sample the quantities for every living cell
        if step % args.sample_every == 0 and int(a.sum()) > 10:
            dens = local_density(a, args.radius)
            res = s.resource
            flat = res.reshape(-1)
            kk = max(1, flat.numel() // 2)
            thr = float(torch.topk(flat, k=kk, largest=True).values.min())
            ys, xs = a.nonzero(as_tuple=True)
            pending.append({
                "step": step,
                "y": ys.clone(), "x": xs.clone(),
                "age": age[ys, xs].clone(),
                "density": dens[ys, xs].clone(),
                "rich": (res[ys, xs] >= thr).float(),
                "energy": s.energy[ys, xs].clone(),
                "births0": births[ys, xs].clone(),
            })
        # resolve observations older than the horizon
        while pending and step - pending[0]["step"] >= args.horizon:
            obs = pending.pop(0)
            ys, xs = obs["y"], obs["x"]
            alive_now = a[ys, xs].float()
            divided = (births[ys, xs] - obs["births0"] > 0).float()
            records.append({
                "age": obs["age"].cpu(), "density": obs["density"].cpu(),
                "rich": obs["rich"].cpu(), "energy": obs["energy"].cpu(),
                "survived": alive_now.cpu(), "divided": divided.cpu(),
            })
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return records, {"alive": alive, "born": final.get("born"), "died": died,
                     "R1": bool(died >= 10 and alive >= 10)}


def quartile_effect(records, key, target):
    """P(target | low quartile) vs P(target | high quartile) of `key`."""
    vals = torch.cat([r[key] for r in records]).float()
    tgt = torch.cat([r[target] for r in records]).float()
    if vals.numel() < 50:
        return None
    q25 = float(torch.quantile(vals, 0.25))
    q75 = float(torch.quantile(vals, 0.75))
    lo = vals <= q25
    hi = vals >= q75
    if int(lo.sum()) < 10 or int(hi.sum()) < 10:
        return None
    p_lo = float(tgt[lo].mean())
    p_hi = float(tgt[hi].mean())
    return {"q25": round(q25, 4), "q75": round(q75, 4),
            "p_low": round(p_lo, 4), "p_high": round(p_hi, 4),
            "diff": round(p_hi - p_lo, 4),
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
        print(f"[e7] seed {s}: {len(recs)} observations, alive {fin['alive']}, R1 {fin['R1']}")

    keys = ["age", "density", "rich", "energy"]
    table = {}
    for key in keys:
        table[key] = {
            "survive": quartile_effect(all_records, key, "survived"),
            "divide": quartile_effect(all_records, key, "divided"),
        }

    out = {"kind": "s55_e7_what_is_selectable", "steps": args.steps, "radius": args.radius,
           "sample_every": args.sample_every, "horizon": args.horizon,
           "n_observations": len(all_records), "finals": finals,
           "note": ("nothing is added to the rules; the script only observes whether survival and "
                    "division differ between the low and high quartiles of quantities the world "
                    "already contains"),
           "table": table}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print(f"\nobservations: {len(all_records)}")
    print(f"{'quantity':10s} | {'P(survive) low->high':30s} | {'P(divide) low->high':30s}")
    for key in keys:
        sv = table[key]["survive"]
        dv = table[key]["divide"]
        s_txt = f"{sv['p_low']:.3f}->{sv['p_high']:.3f} ({sv['diff']:+.3f})" if sv else "n/a"
        d_txt = f"{dv['p_low']:.3f}->{dv['p_high']:.3f} ({dv['diff']:+.3f})" if dv else "n/a"
        print(f"{key:10s} | {s_txt:30s} | {d_txt:30s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
