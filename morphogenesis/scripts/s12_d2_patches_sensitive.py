"""S12 / D2: patchy environment with a SENSITIVE design (seeded on a patch).

Why D2 after S11: the first patchy test was insensitive by construction - cells were
seeded at the grid centre (resource 0.2, net -0.028/step) while the nearest rich patch
was 9.2 cells away, so every moving arm starved out (alive 0/0/0) before direction could
matter. Here the design is fixed by SEEDING ON A PATCH, where the energy balance is
positive.

Sensitivity arithmetic (contract 3c, computed BEFORE the run, see report):
  spent = update_cost + repair_cost = 0.060 / step
  income(res) = baseline_income * res * 4  (proportional mode)
  res 0.2 -> income 0.032 -> net -0.028  (centre: cells lose energy)
  res 1.0 -> income 0.160 -> net +0.100  (patch: cells gain energy)
So a colony seeded on a patch can pay for movement; a colony in the centre cannot.

Arms:
  - `baseline` : no plasticity (control);
  - `local1`   : step to the free neighbour with the highest raw resource;
  - `local5`   : step to the free neighbour with the highest 5x5-smoothed resource.

Readout: share of alive cells in the top-50% resource cells (favourable zone), plus the
mean resource under alive cells (the quantity that actually decides survival here).
R1: died>=10 and alive>=10.
"""
from __future__ import annotations
import argparse, json, math, os, sys
import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)
from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def smooth5(res: torch.Tensor, radius: int) -> torch.Tensor:
    r = int(radius)
    if r <= 0:
        return res
    x = res.unsqueeze(0).unsqueeze(0)
    x = torch.nn.functional.pad(x, (r, r, r, r), mode="replicate")
    k = 2 * r + 1
    w = torch.ones((1, 1, k, k), dtype=res.dtype, device=res.device) / (k * k)
    return torch.nn.functional.conv2d(x, w).squeeze(0).squeeze(0)


def local_moves(pond, field: torch.Tensor):
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


def seed_on_patch(run, cells: int, energy: float, patch_xy: tuple[int, int]) -> None:
    """Seed a square block centred on a rich patch (replaces the default centre seeding).

    The engine's `seed()` always uses the grid centre; for this design we need the colony
    to start where the energy balance is positive. We build the same mask shape and call
    the engine's own `seed_life` / state sync so nothing else changes.
    """
    n = run.world_cfg.grid
    cy, cx = patch_xy
    side = max(1, math.isqrt(int(cells) - 1) + 1)
    top = max(0, min(n - side, cy - side // 2))
    left = max(0, min(n - side, cx - side // 2))
    mask = torch.zeros((n, n), dtype=torch.bool, device=run.device)
    placed = 0
    for i in range(int(cells)):
        y = top + i // side
        x = left + i % side
        if 0 <= y < n and 0 <= x < n:
            mask[y, x] = True
            placed += 1
    run.pond.seed_life(mask, energy=energy)
    run._apply_alive(mask.to(run.device))
    run._apply_genome(mask, run.genome[0, :, mask])


def run_one(seed, args, arm: str):
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
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if arm != "baseline" and bool(s.alive.any()):
            field = s.resource if arm == "local1" else smooth5(s.resource, args.radius)
            moves = local_moves(pond, field)
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
        res_alive = float(res[a].mean())
        if acc is None:
            acc = {"start": st, "n": 0, "fav": 0.0, "res": 0.0}
        acc["n"] += 1; acc["fav"] += fav; acc["res"] += res_alive
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(acc["fav"] / acc["n"], 4),
                            "resource_under_alive": round(acc["res"] / acc["n"], 4)})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(pond.state.step),
                        "favourable_share": round(acc["fav"] / acc["n"], 4),
                        "resource_under_alive": round(acc["res"] / acc["n"], 4)})
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--patch-y", type=int, default=7, help="centre of the rich patch to seed on")
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
    ap.add_argument("--arms", nargs="+", default=["baseline", "local1", "local5"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s12_d2_patches_sensitive", "radius": args.radius, "steps": args.steps,
           "window": args.window, "patch_xy": [args.patch_y, args.patch_x],
           "sensitivity_note": ("spent=0.060/step; income(res)=baseline*res*4; "
                                "net(0.2)=-0.028, net(1.0)=+0.100; colony seeded ON a patch "
                                "so movement can be paid for (contract 3c arithmetic)."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        fav, resv = [], []
        for i in range(nw):
            f = [r["windows"][i]["favourable_share"] for r in ar if i < len(r["windows"])]
            v = [r["windows"][i]["resource_under_alive"] for r in ar if i < len(r["windows"])]
            fav.append(round(sum(f) / len(f), 3) if f else None)
            resv.append(round(sum(v) / len(v), 3) if v else None)
        print(f"{arm:9s} fav {fav} | res {resv} | R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
