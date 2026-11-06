"""S13 / D3: does the patchy-transfer advantage decay because the rich zone saturates?

S12/D2 found a real but decaying advantage: local greed beat baseline by +0.118 in the
first window, falling to +0.036 by the end, with equal survival in all arms. Two
candidate explanations:
  (a) CROWDING: the rich zone fills up, so arriving there stops paying - the resource
      under alive cells falls (0.327 -> 0.114 in baseline) and local competition eats
      the gain;
  (b) DRIFT: the population simply spreads out over the whole grid, so the *share* in
      the rich zone falls for everyone and the difference shrinks mechanically.

This script separates them by varying the CARRYING CAPACITY, i.e. the population
density, while keeping everything else fixed:

  - `low_density`  : higher upkeep (update_cost/repair_cost raised) -> fewer cells alive;
  - `base`         : the S12/D2 settings;
  - `high_density` : lower upkeep -> more cells alive.

If (a) crowding is the cause, the local-minus-baseline gap should be LARGER and last
LONGER at low density, and vanish at high density. If (b) drift is the cause, the gap
should scale with density but not last longer.

Sensitivity arithmetic (contract 3c, computed before the run):
  spent = update + repair; income(res) = baseline_income * res * 4
  res 1.0 -> income 0.160. For the colony to survive at all we need spent < 0.160.
  base: spent 0.060 (net +0.100 at a patch)
  low_density:  spent 0.110 (net +0.050) - still positive, so the colony survives
  high_density: spent 0.030 (net +0.130) - much more energy, denser population
All three keep the colony viable at a patch, which is the condition S11 lacked.

Readout: favourable share and resource-under-alive per window, plus alive count, for
both arms; the reported quantity is the GAP (local1 - baseline) per window.
"""
from __future__ import annotations
import argparse, json, math, os, sys
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


def run_one(seed, args, arm: str, update_cost: float, repair_cost: float):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=update_cost, repair_cost=repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
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
        fav = float((a & (res >= thr)).sum() / n)
        if acc is None:
            acc = {"start": st, "n": 0, "fav": 0.0, "alive": 0, "res": 0.0}
        acc["n"] += 1; acc["fav"] += fav; acc["alive"] += n; acc["res"] += float(res[a].mean())
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1),
                            "resource_under_alive": round(acc["res"] / acc["n"], 4)})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(pond.state.step),
                        "favourable_share": round(acc["fav"] / acc["n"], 4),
                        "alive_mean": round(acc["alive"] / acc["n"], 1),
                        "resource_under_alive": round(acc["res"] / acc["n"], 4)})
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


REGIMES = {
    "low_density": (0.070, 0.040),    # spent 0.110 -> net +0.050 at a patch
    "base": (0.038, 0.022),           # spent 0.060 -> net +0.100
    "high_density": (0.020, 0.010),   # spent 0.030 -> net +0.130
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--patch-y", type=int, default=7)
    ap.add_argument("--patch-x", type=int, default=7)
    ap.add_argument("--income", type=float, default=0.04)
    ap.add_argument("--init-resource-fill", type=float, default=1.0)
    ap.add_argument("--resource-regen", type=float, default=0.05)
    ap.add_argument("--patch-inflow-base", type=float, default=0.1)
    ap.add_argument("--patch-inflow-rich", type=float, default=4.0)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--regimes", nargs="+", default=["low_density", "base", "high_density"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for regime in args.regimes:
        uc, rc = REGIMES[regime]
        for s in args.seeds:
            for arm in ("baseline", "local1"):
                r = run_one(s, args, arm, uc, rc)
                r["regime"] = regime
                r["update_cost"], r["repair_cost"] = uc, rc
                rows.append(r)
    out = {"kind": "s13_d3_crowding_vs_drift", "steps": args.steps, "window": args.window,
           "regimes": {k: {"update_cost": v[0], "repair_cost": v[1],
                           "spent": v[0] + v[1], "net_at_patch": round(0.16 - (v[0] + v[1]), 4)}
                       for k, v in REGIMES.items()},
           "sensitivity_note": ("spent = update+repair; income(1.0) = 0.160; all three regimes "
                                "keep net positive at a patch so the colony stays viable"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for regime in args.regimes:
        rr = [r for r in rows if r["regime"] == regime]
        nw = max((len(r["windows"]) for r in rr), default=0)
        print(f"== {regime} (spent {REGIMES[regime][0]+REGIMES[regime][1]:.3f})")
        for arm in ("baseline", "local1"):
            ar = [r for r in rr if r["arm"] == arm]
            fav = []
            alive = []
            for i in range(nw):
                v = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
                a = [r["windows"][i]["alive_mean"] for r in ar if i < len(r["windows"])]
                fav.append(round(sum(v) / len(v), 3) if v else None)
                alive.append(round(sum(a) / len(a), 0) if a else None)
            print(f"   {arm:9s} fav {fav} | alive {alive} | R1 {[r['R1'] for r in ar]}")
        gap = []
        for i in range(nw):
            b = [r["windows"][i]["favourable_share"] for r in rr if r["arm"] == "baseline" and i < len(r["windows"])]
            l = [r["windows"][i]["favourable_share"] for r in rr if r["arm"] == "local1" and i < len(r["windows"])]
            gap.append(round(sum(l) / len(l) - sum(b) / len(b), 3) if b and l else None)
        print(f"   GAP(local1-baseline) {gap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
