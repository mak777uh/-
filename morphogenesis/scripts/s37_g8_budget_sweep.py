"""S37 / G8: where does the reference stop mattering? A budget sweep.

S35-S36 found that at a truly equal mobility budget (2 cells/step, both arms at 1.62-1.63 moves/step)
the ADAPTIVE reference wins (0.372 vs 0.318 for the fixed one), while at budget 20 the fixed one
appeared to win - but there the budget never bound the adaptive arm, so the comparison was invalid.

This script sweeps the budget from 1 to 8 and, for every level, records both the favourable share AND
the actual moves/step in each arm, so the reader can see for which budgets the comparison is fair
(the two arms move equally) and for which it is not.

Design:
  - arms: `baseline` (no movement), `ema_abs` (adaptive reference), `fixed_abs` (fixed reference);
  - budgets: 1, 2, 3, 4, 6, 8;
  - the same seeds and world as S35-S36.

Readout: for each budget, the mean favourable share per arm over all windows, the mean moves/step per
arm, and the ratio between them. A budget is FAIR when the ratio is close to 1; only fair budgets can
be used to compare the references.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  at budget 2 both arms move 1.62-1.63 per step (fair); at budget 5 they move 3.58 vs 4.16 (unfair);
  so the crossover between "fair" and "unfair" lies between 2 and 5, and the sweep brackets it.
  R1 is checked per run.
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


def greedy_moves_absolute(pond, reference, budget):
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    poor = s.alive & (s.resource < reference) & (s.energy > cfg.plastic_move_cost)
    n_qualify = int(poor.sum())
    if n_qualify == 0 or budget <= 0:
        return [], 0
    cand = poor.nonzero(as_tuple=False)
    order = torch.randperm(cand.shape[0], generator=pond.gen_sel)[:budget]
    taken = torch.zeros_like(s.alive)
    moves = []
    for k in order.tolist():
        y, x = int(cand[k, 0]), int(cand[k, 1])
        if not bool(s.alive[y, x]) or bool(taken[y, x]):
            continue
        best, best_v = None, float(s.resource[y, x])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                continue
            v = float(s.resource[ny, nx])
            if v > best_v:
                best, best_v = (ny, nx), v
        if best is None:
            continue
        taken[best[0], best[1]] = True
        moves.append((y, x, best[0], best[1]))
    return moves, n_qualify


def run_one(seed, args, arm, budget):
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
    fixed_ref = pond.state.resource.clone()
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        s = pond.state
        moved = 0
        if arm != "baseline" and bool(s.alive.any()):
            ref = s.pred if arm == "ema_abs" else fixed_ref
            moves, _ = greedy_moves_absolute(pond, ref, budget)
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
                moved = len(moves)
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
            acc = {"n": 0, "fav": 0.0, "moved": 0, "alive": 0}
        acc["n"] += 1
        acc["fav"] += fav
        acc["moved"] += moved
        acc["alive"] += n
        if acc["n"] >= args.window:
            windows.append({"favourable_share": round(acc["fav"] / acc["n"], 4),
                            "moves_per_step": round(acc["moved"] / acc["n"], 2),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(w["favourable_share"] for w in windows) / len(windows), 4) if windows else None
    mv = round(sum(w["moves_per_step"] for w in windows) / len(windows), 2) if windows else 0.0
    return {"seed": seed, "arm": arm, "budget": budget, "overall": overall,
            "moves_per_step": mv, "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


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
    ap.add_argument("--resource-regen", type=float, default=0.05)
    ap.add_argument("--patch-inflow-base", type=float, default=0.1)
    ap.add_argument("--patch-inflow-rich", type=float, default=4.0)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--budgets", type=int, nargs="+", default=[1, 2, 3, 4, 6, 8])
    ap.add_argument("--arms", nargs="+", default=["baseline", "ema_abs", "fixed_abs"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for budget in args.budgets:
        for arm in args.arms:
            for s in args.seeds:
                rows.append(run_one(s, args, arm, budget))
    out = {"kind": "s37_g8_budget_sweep", "steps": args.steps, "window": args.window,
           "budgets": args.budgets,
           "note": ("a budget is FAIR when both reference arms move equally; only fair budgets can "
                    "compare the references"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("budget | ema fav / fixed fav / baseline | ema mov / fixed mov | ratio | fair?")
    for budget in args.budgets:
        def val(arm, key):
            v = [r[key] for r in rows if r["budget"] == budget and r["arm"] == arm and r[key] is not None]
            return round(sum(v) / len(v), 3) if v else None
        e, f, b = val("ema_abs", "overall"), val("fixed_abs", "overall"), val("baseline", "overall")
        em, fm = val("ema_abs", "moves_per_step"), val("fixed_abs", "moves_per_step")
        ratio = round(fm / em, 2) if em else None
        fair = "yes" if ratio is not None and abs(ratio - 1.0) <= 0.05 else "NO"
        print(f"{budget:6d} | {e} / {f} / {b} | {em} / {fm} | {ratio} | {fair}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
