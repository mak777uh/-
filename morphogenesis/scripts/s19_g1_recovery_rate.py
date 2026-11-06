"""S19 / G1: does the advantage of local greed depend on the RESOURCE RECOVERY RATE?

Why this test. The literature on forager mobility with several agents per site predicts that the gain
from mobility depends on how fast the resource recovers, not only on population density (Sci Rep 2019,
s41598-019-42006-2; lit-queue item B-Q052). We cannot test the multi-occupancy part without changing the
engine (S17/F1), but we CAN test whether the single-occupancy result already depends on the recovery
rate. That is a clean, cheap prediction test with the world as it is.

Design: vary `resource_regen`, which scales the inflow everywhere (rich patches and poor background
alike), so the recovery rate changes while the geometry and the one-organism-per-cell rule stay fixed.

  - `slow`  : resource_regen = 0.010
  - `base`  : resource_regen = 0.020   (the S12/S13/S14 setting)
  - `fast`  : resource_regen = 0.040

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  income(res) = baseline_income * res * 4 = 0.04 * res * 4 ; spent = 0.060
  A full patch cell (res 1.0) earns 0.160 regardless of regen, so the colony stays viable at a patch in
  all three regimes (net +0.100). What changes is how fast a depleted cell refills:
    regen 0.010 -> patch inflow 0.040/step vs one cell eating 0.160 -> a patch cell DRAINS
    regen 0.020 -> patch inflow 0.080/step vs 0.160 -> still drains (slower)
    regen 0.040 -> patch inflow 0.160/step vs 0.160 -> break-even
  So this sweep spans "patches deplete" to "patches hold", which is exactly the recovery axis the
  literature points at. R1 is checked per run; a regime that starves the colony is reported as invalid.

Arms: `baseline` (no movement) and `local1` (step to the free neighbour with the highest resource).
Colonies are seeded ON a patch, as established in S12/D2.
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


def local_moves(pond):
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    field = s.resource
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


def run_one(seed, args, arm, regen):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if arm == "local1" and bool(s.alive.any()):
            moves = local_moves(pond)
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
        rich = res >= thr
        rc = int(rich.sum())
        ra = int((a & rich).sum())
        if acc is None:
            acc = {"start": st, "n": 0, "fav": 0.0, "occ": 0.0, "rres": 0.0, "alive": 0}
        acc["n"] += 1
        acc["fav"] += ra / n
        acc["occ"] += (ra / rc) if rc else 0.0
        acc["rres"] += float(res[rich].mean())
        acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "rich_occupancy": round(acc["occ"] / acc["n"], 4),
                            "rich_resource": round(acc["rres"] / acc["n"], 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "resource_regen": regen, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


REGIMES = {"slow": 0.010, "base": 0.020, "fast": 0.040}


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
    ap.add_argument("--patch-inflow-base", type=float, default=0.1)
    ap.add_argument("--patch-inflow-rich", type=float, default=4.0)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--regimes", nargs="+", default=["slow", "base", "fast"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for regime in args.regimes:
        regen = REGIMES[regime]
        for s in args.seeds:
            for arm in ("baseline", "local1"):
                r = run_one(s, args, arm, regen)
                r["regime"] = regime
                rows.append(r)
    out = {"kind": "s19_g1_recovery_rate", "steps": args.steps, "window": args.window,
           "regimes": {k: {"resource_regen": v,
                           "patch_inflow_per_step": round(v * args.patch_inflow_rich, 4),
                           "one_cell_consumption": round(args.income * 1.0 * 4, 4)}
                       for k, v in REGIMES.items()},
           "sensitivity_note": ("income(1.0)=0.160 regardless of regen, so the colony stays viable at a "
                                "patch; what changes is refill speed: 0.040/0.080/0.160 per step vs 0.160 "
                                "eaten, i.e. this sweep spans 'patches deplete' to 'patches hold'"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for regime in args.regimes:
        rr = [r for r in rows if r["regime"] == regime]
        nw = max((len(r["windows"]) for r in rr), default=0)
        print(f"== {regime} (regen {REGIMES[regime]}, patch inflow {REGIMES[regime]*args.patch_inflow_rich:.3f}/step)")
        for arm in ("baseline", "local1"):
            ar = [r for r in rr if r["arm"] == arm]
            fav, rres = [], []
            for i in range(nw):
                f = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
                v = [r["windows"][i]["rich_resource"] for r in ar if i < len(r["windows"])]
                fav.append(round(sum(f) / len(f), 3) if f else None)
                rres.append(round(sum(v) / len(v), 3) if v else None)
            print(f"   {arm:9s} fav {fav} | rich_res {rres} | R1 {[r['R1'] for r in ar]}")
        gap = []
        for i in range(nw):
            b = [r["windows"][i]["favourable_share"] for r in rr if r["arm"] == "baseline" and i < len(r["windows"])]
            l = [r["windows"][i]["favourable_share"] for r in rr if r["arm"] == "local1" and i < len(r["windows"])]
            gap.append(round(sum(l) / len(l) - sum(b) / len(b), 3) if b and l else None)
        print(f"   GAP {gap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
