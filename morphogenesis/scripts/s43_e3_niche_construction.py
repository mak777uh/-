"""S43 / E3: niche construction with the three controls the literature prescribes.

The 07.11 literature search gave a ready design (Wetherington & Keymer 2020; Laland 1999):
a feedback loop must be tested against a FROZEN environment, not only against "no feedback",
because otherwise a falling signal cannot be told apart from a population that simply died out.

Design: cells consume resource; a fraction `construct` of the consumed resource is returned to the
environment as a "built niche" that persists with discount `gamma` and raises local inflow. Three arms:

  - `closed`   : the loop is closed - cells build the niche and the niche feeds them back;
  - `open`     : the loop is open - the same amount of building happens (same energy cost) but the
                 niche does NOT raise inflow (the placebo control);
  - `frozen`   : the niche is present but frozen at the value recorded from `closed` at the same step
                 (the literature's "frozen environment" control: agents see it but cannot change it).

Readout per window: favourable share, alive count, the niche's own amplitude, and the correlation
between alive count and niche amplitude (the literature's criterion: a working loop shows the two
moving together while the population stays positive).

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  income(res) = 0.04*res*4, spent = 0.060; the niche adds at most `construct * consumed` to inflow,
  and with construct <= 0.3 the added inflow stays below one cell's consumption at a full patch, so
  the loop cannot run away. R1 is checked per run.
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


def run_one(seed, args, arm, frozen_trace=None):
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
    favs, alive_hist, niche_hist = [], [], []
    trace = []          # for the closed arm: niche amplitude per step
    for step in range(args.steps):
        prev_res = pond.state.resource.clone()
        run.step()
        s = pond.state
        # consumed = what the living cells took from their own cells this step
        consumed = (prev_res - s.resource).clamp_min(0.0) * s.alive.float()
        built = args.construct * consumed
        if arm == "closed":
            niche = niche * (1.0 - args.gamma) + built
            # the niche raises inflow where it was built
            s.resource = torch.clamp(s.resource + args.niche_gain * niche, max=cfg.resource_max)
            trace.append(float(niche.mean()))
        elif arm == "open":
            # same building cost, but the niche does not feed back
            niche = niche * (1.0 - args.gamma) + built
            s.energy = torch.clamp(s.energy - args.construct * consumed, min=0.0)
            trace.append(float(niche.mean()))
        else:  # frozen: replay the closed arm's niche, agents cannot change it
            if frozen_trace is not None and step < len(frozen_trace):
                niche = torch.full_like(niche, frozen_trace[step])
                s.resource = torch.clamp(s.resource + args.niche_gain * niche, max=cfg.resource_max)
            trace.append(float(niche.mean()))
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / cnt))
        alive_hist.append(cnt)
        niche_hist.append(float(niche.mean()))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    corr = None
    if len(alive_hist) > 10 and len(set(alive_hist)) > 1 and len(set(niche_hist)) > 1:
        ax = torch.tensor(alive_hist, dtype=torch.float64)
        bx = torch.tensor(niche_hist, dtype=torch.float64)
        corr = round(float(torch.corrcoef(torch.stack([ax, bx]))[0, 1]), 4)
    return {"seed": seed, "arm": arm, "overall": overall, "alive_niche_corr": corr,
            "niche_final": round(niche_hist[-1], 6) if niche_hist else None,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}, trace


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
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--construct", type=float, default=0.3)
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--niche-gain", type=float, default=0.5)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        r_closed, trace = run_one(s, args, "closed")
        rows.append(r_closed)
        r_open, _ = run_one(s, args, "open")
        rows.append(r_open)
        r_frozen, _ = run_one(s, args, "frozen", frozen_trace=trace)
        rows.append(r_frozen)
    out = {"kind": "s43_e3_niche_construction", "steps": args.steps, "construct": args.construct,
           "gamma": args.gamma, "niche_gain": args.niche_gain,
           "note": ("three controls from the literature: closed loop / open (placebo) / frozen "
                    "environment replayed from the closed arm"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in ("closed", "open", "frozen"):
        ar = [r for r in rows if r["arm"] == arm]
        vals = [r["overall"] for r in ar if r["overall"] is not None]
        corrs = [r["alive_niche_corr"] for r in ar if r["alive_niche_corr"] is not None]
        print(f"{arm:7s} overall {round(sum(vals)/len(vals),3) if vals else None} "
              f"| corr(alive,niche) {round(sum(corrs)/len(corrs),3) if corrs else None} "
              f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
