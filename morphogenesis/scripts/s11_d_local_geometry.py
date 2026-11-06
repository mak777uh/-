"""S11 / D: transfer to PATCHY environments with a LOCAL-geometry signal.

Why: S3/D showed that row-axis taxis (`gradpos`) does not transfer to patches - it drags
cells along the global axis while the resource sits in three separate patches. The one
signal that did transfer a little was the local resource argmax (0.385 vs 0.247 baseline),
but it is weak: a single-neighbour comparison sees almost no gradient inside a patch.

This test asks whether a SMOOTHED LOCAL signal - the mean resource over the 5x5
neighbourhood (the cell's own position plus two rings) - does better than the raw
one-step argmax, and whether it still works on the gradient layout (transfer both ways).

Arms (same seeds, patchy layout unless --layout says otherwise):
  - `baseline`   : no plasticity (control);
  - `local1`     : move to the free neighbour with the highest raw resource (S3/D signal);
  - `local5`     : move to the free neighbour with the highest 5x5 smoothed resource;
  - `local5_trait`: same as local5 but the smoothing radius is a heritable trait
                    (requires type_mode != fixed for inheritance to run).

Readout: share of alive cells sitting in the favourable zone. For patches the favourable
zone is the top-50% of cells by CURRENT resource (layout-agnostic, same as S3/D); for
gradient it is the current gradient half. R1: died>=10 and alive>=10.
"""
from __future__ import annotations
import argparse, json, os, sys
import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)
from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def favourable_mask(pond, layout: str):
    if layout == "gradient":
        pos = pond._gradient_position()
        g = pond.cfg.grid
        return (pos >= 0.5)[:, None].expand(g, g)
    res = pond.state.resource
    flat = res.reshape(-1)
    k = max(1, flat.numel() // 2)
    thr = float(torch.topk(flat, k=k, largest=True).values.min())
    return res >= thr


def smooth5(res: torch.Tensor, radius: int) -> torch.Tensor:
    """Box mean over a (2r+1)^2 window with edge replication."""
    r = int(radius)
    if r <= 0:
        return res
    x = res.unsqueeze(0).unsqueeze(0)                      # (1,1,H,W)
    x = torch.nn.functional.pad(x, (r, r, r, r), mode="replicate")
    k = 2 * r + 1
    w = torch.ones((1, 1, k, k), dtype=res.dtype, device=res.device) / (k * k)
    return torch.nn.functional.conv2d(x, w).squeeze(0).squeeze(0)


def local_moves(pond, field: torch.Tensor):
    """Engine-style moves: each 'poor' cell steps to the free neighbour with max field."""
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


def run_one(seed, args, arm: str):
    cfg = PondConfig(
        grid=args.grid, resource_layout=args.layout, income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=(args.flip_at if args.layout == "gradient" else 0),
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
        type_mode=args.type_mode,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if arm != "baseline" and bool(s.alive.any()):
            if arm == "local1":
                field = s.resource
            elif arm == "local5":
                field = smooth5(s.resource, args.radius)
            else:  # local5_trait: radius scales with the heritable trait
                tr = s.tag_trait
                base = smooth5(s.resource, args.radius)
                fine = s.resource
                w = torch.sigmoid(tr * args.trait_scale) if tr is not None else torch.zeros_like(s.energy)
                field = w * base + (1.0 - w) * fine
            moves = local_moves(pond, field)
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        a = s.alive
        n = int(a.sum())
        if n == 0:
            continue
        fav = favourable_mask(pond, args.layout)
        share = float((a & fav).sum() / n)
        if acc is None:
            acc = {"start": st, "n": 0, "share": 0.0}
        acc["n"] += 1; acc["share"] += share
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["share"] / acc["n"], 4)})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(pond.state.step),
                        "favourable_share": round(acc["share"] / acc["n"], 4)})
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--flip-at", type=int, default=200)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--layout", default="patches", choices=["patches", "gradient"])
    ap.add_argument("--radius", type=int, default=2, help="smoothing radius for local5")
    ap.add_argument("--grid", type=int, default=32)
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
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--mutation-trait-sigma", type=float, default=0.3)
    ap.add_argument("--trait-scale", type=float, default=2.0)
    ap.add_argument("--type-mode", default="mixfixed", choices=["fixed", "mixfixed", "random", "learn"])
    ap.add_argument("--arms", nargs="+", default=["baseline", "local1", "local5"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s11_d_local_geometry", "layout": args.layout, "radius": args.radius,
           "steps": args.steps, "window": args.window, "flip_at": args.flip_at,
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        vals = []
        for i in range(nw):
            v = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
            vals.append(round(sum(v) / len(v), 3) if v else None)
        print(f"{arm:12s} favourable {vals} | R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
