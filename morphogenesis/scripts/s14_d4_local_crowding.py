"""S14 / D4: does LOCAL crowding in the rich cells predict the decay of the advantage?

S13/D3 showed the local-greed advantage falls monotonically as population density rises,
which points at competition for the rich zone. But density was only the *global* knob;
the mechanism claims something narrower: the RICH CELLS themselves fill up.

This script measures, per step and per arm:
  - `rich_occupancy` : mean fraction of cells in the top-50% resource zone that are alive
                       (how full the rich zone is);
  - `rich_res`       : mean resource in that zone (how much is left there);
  - `favourable`     : share of alive cells standing in the rich zone.

Then, across all (regime x arm x window) points, it correlates the local-greed MINUS
baseline gap with rich-zone occupancy. Prediction if the crowding story is right: the
gap is large when the rich zone is empty and small/negative when it is full.

Sensitivity arithmetic (contract 3c, before the run): same three upkeep regimes as S13,
all with a positive net balance at a patch (0.050 / 0.100 / 0.130), so the colony stays
viable and the measurement is not an extinction artefact.
"""
from __future__ import annotations
import argparse, json, math, os, statistics, sys
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
        rich = res >= thr
        rich_cells = int(rich.sum())
        rich_alive = int((a & rich).sum())
        occ = rich_alive / rich_cells if rich_cells else 0.0
        fav = rich_alive / n
        rich_res = float(res[rich].mean())
        if acc is None:
            acc = {"start": st, "n": 0, "occ": 0.0, "fav": 0.0, "rres": 0.0, "alive": 0}
        acc["n"] += 1; acc["occ"] += occ; acc["fav"] += fav; acc["rres"] += rich_res; acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "rich_occupancy": round(acc["occ"] / acc["n"], 4),
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "rich_resource": round(acc["rres"] / acc["n"], 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(pond.state.step),
                        "rich_occupancy": round(acc["occ"] / acc["n"], 4),
                        "favourable_share": round(acc["fav"] / acc["n"], 4),
                        "rich_resource": round(acc["rres"] / acc["n"], 4),
                        "alive_mean": round(acc["alive"] / acc["n"], 1)})
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


REGIMES = {
    "low_density": (0.070, 0.040),
    "base": (0.038, 0.022),
    "high_density": (0.020, 0.010),
}


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


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
                rows.append(r)

    # gap per (regime, window) and the rich occupancy that goes with it
    points = []
    for regime in args.regimes:
        rr = [r for r in rows if r["regime"] == regime]
        nw = max((len(r["windows"]) for r in rr), default=0)
        for i in range(nw):
            b = [r["windows"][i] for r in rr if r["arm"] == "baseline" and i < len(r["windows"])]
            l = [r["windows"][i] for r in rr if r["arm"] == "local1" and i < len(r["windows"])]
            if not b or not l:
                continue
            gap = sum(w["favourable_share"] for w in l) / len(l) - sum(w["favourable_share"] for w in b) / len(b)
            occ = sum(w["rich_occupancy"] for w in b) / len(b)
            points.append({"regime": regime, "window": i, "gap": round(gap, 4),
                           "baseline_rich_occupancy": round(occ, 4),
                           "baseline_rich_resource": round(sum(w["rich_resource"] for w in b) / len(b), 4)})
    xs = [p["baseline_rich_occupancy"] for p in points]
    ys = [p["gap"] for p in points]
    r_all = pearson(xs, ys)
    out = {"kind": "s14_d4_local_crowding", "steps": args.steps, "window": args.window,
           "regimes": {k: {"update_cost": v[0], "repair_cost": v[1], "spent": v[0] + v[1]}
                       for k, v in REGIMES.items()},
           "sensitivity_note": ("spent = update+repair; income(1.0)=0.160; all regimes keep a "
                                "positive net balance at a patch, so no extinction artefact"),
           "pearson_gap_vs_rich_occupancy": round(r_all, 4) if r_all is not None else None,
           "n_points": len(points), "points": points,
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for regime in args.regimes:
        rr = [r for r in rows if r["regime"] == regime]
        nw = max((len(r["windows"]) for r in rr), default=0)
        print(f"== {regime}")
        for arm in ("baseline", "local1"):
            ar = [r for r in rr if r["arm"] == arm]
            occ, fav = [], []
            for i in range(nw):
                o = [r["windows"][i]["rich_occupancy"] for r in ar if i < len(r["windows"])]
                f = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
                occ.append(round(sum(o) / len(o), 3) if o else None)
                fav.append(round(sum(f) / len(f), 3) if f else None)
            print(f"   {arm:9s} rich_occ {occ} | fav {fav}")
    print(f"pearson(gap, baseline_rich_occupancy) = {out['pearson_gap_vs_rich_occupancy']} over {len(points)} points")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
