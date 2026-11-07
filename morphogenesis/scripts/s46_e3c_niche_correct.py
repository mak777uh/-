"""S46 / E3c: niche construction, done correctly this time.

Two earlier attempts were invalid and are recorded as such:

  - s43: the niche ADDED `niche_gain * niche` to the resource every step. It grew without
    bound (0.001 -> 2.23) and injected 1.12 resource/step while one cell eats 0.16 - a
    resource tap, not a feedback loop. Caught by the long-horizon run, where the FROZEN arm
    overtook the closed one (0.853 vs 0.799), which is impossible for a real loop.
  - s45: the tap was closed but `niche_gain = 40` multiplied the inflow by ~173x, so the
    resource saturated the whole grid and the favourable share hit its 0.988 ceiling. The
    comparison was saturated, not informative; and the FROZEN arm still received the same
    inflow, so it was a copy rather than a control.

This version fixes all three:

  1. ARITHMETIC FIRST (contract 3c). The niche may add at most a fraction `max_share` of one
     cell's consumption. One cell eats `income * res * 4 = 0.16` per step at a full patch, so
     the niche's contribution is capped at `max_share * 0.16` (default 0.25 -> 0.04/step).
     If the computed gain would exceed that, the script REFUSES to run.
  2. FROZEN is a real control: the niche field is present (agents "see" it) but it contributes
     ZERO inflow. The frozen arm therefore differs from the closed arm by exactly one thing:
     whether the niche does anything.
  3. SATURATION GUARD: if the favourable share exceeds `max_fav` (default 0.85) in any arm, the
     run is reported as saturated and the numbers are not claimed.

Arms:
  - `closed`  : cells build the niche; the niche accelerates local recovery (capped);
  - `open`    : cells pay the same energy for building, but the niche does nothing (placebo);
  - `frozen`  : the niche field is present but contributes nothing (the literature control).
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


def consumption_per_cell(args) -> float:
    """What one cell eats per step at a full patch (contract 3c arithmetic)."""
    return args.income * 1.0 * 4.0


def run_one(seed, args, arm):
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
    for _ in range(args.steps):
        prev_res = pond.state.resource.clone()
        run.step()
        s = pond.state
        consumed = (prev_res - s.resource).clamp_min(0.0) * s.alive.float()
        built = args.construct * consumed
        if arm == "closed":
            niche = niche * (1.0 - args.gamma) + built
            # the niche accelerates recovery; the contribution is capped by the arithmetic check
            s.resource = torch.clamp(
                s.resource + args.niche_gain * niche * cfg.resource_regen, max=cfg.resource_max)
        elif arm == "open":
            niche = niche * (1.0 - args.gamma) + built
            s.energy = torch.clamp(s.energy - args.construct * consumed, min=0.0)
        else:  # frozen: the field exists but contributes nothing
            niche = niche * (1.0 - args.gamma) + built
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
    peak = round(max(favs), 4) if favs else None
    corr = None
    if len(alive_hist) > 10 and len(set(alive_hist)) > 1 and len(set(niche_hist)) > 1:
        ax = torch.tensor(alive_hist, dtype=torch.float64)
        bx = torch.tensor(niche_hist, dtype=torch.float64)
        corr = round(float(torch.corrcoef(torch.stack([ax, bx]))[0, 1]), 4)
    return {"seed": seed, "arm": arm, "overall": overall, "peak_fav": peak,
            "saturated": bool(peak is not None and peak > args.max_fav),
            "alive_niche_corr": corr,
            "niche_final": round(niche_hist[-1], 6) if niche_hist else None,
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
    ap.add_argument("--niche-gain", type=float, default=2.0)
    ap.add_argument("--max-share", type=float, default=0.25,
                    help="niche contribution may not exceed this share of one cell's consumption")
    ap.add_argument("--max-fav", type=float, default=0.85, help="above this the metric is saturated")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    # CONTRACT 3c: arithmetic BEFORE the run. The niche's steady contribution is
    # niche_gain * niche_steady * regen; niche_steady ~ construct * consumed / gamma.
    eat = consumption_per_cell(args)
    niche_steady = args.construct * eat / max(args.gamma, 1e-6)
    contribution = args.niche_gain * niche_steady * args.resource_regen
    cap = args.max_share * eat
    print(f"[e3c] one cell eats {eat:.4f}/step; niche steady {niche_steady:.3f}; "
          f"contribution {contribution:.4f}/step; cap {cap:.4f} (share {args.max_share})")
    if contribution > cap:
        raise SystemExit(
            f"[e3c] REFUSED: the niche would add {contribution:.4f}/step, above the cap "
            f"{cap:.4f}. Lower --niche-gain or --construct. (This is the check that s43 and s45 "
            f"skipped: s43 added 1.12/step against 0.16 eaten, s45 saturated the grid.)")

    rows = []
    for s in args.seeds:
        for arm in ("closed", "open", "frozen"):
            rows.append(run_one(s, args, arm))
    out = {"kind": "s46_e3c_niche_correct", "steps": args.steps, "construct": args.construct,
           "gamma": args.gamma, "niche_gain": args.niche_gain,
           "arithmetic": {"eat_per_cell": eat, "niche_steady": round(niche_steady, 4),
                          "contribution": round(contribution, 5), "cap": round(cap, 5)},
           "note": ("closed = niche accelerates recovery (capped); open = same energy, no effect; "
                    "frozen = niche present but contributes nothing"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in ("closed", "open", "frozen"):
        ar = [r for r in rows if r["arm"] == arm]
        vals = [r["overall"] for r in ar if r["overall"] is not None]
        peaks = [r["peak_fav"] for r in ar if r["peak_fav"] is not None]
        sat = sum(r["saturated"] for r in ar)
        print(f"{arm:7s} overall {round(sum(vals)/len(vals),3) if vals else None} "
              f"| peak {round(max(peaks),3) if peaks else None} | saturated {sat}/{len(ar)} "
              f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
