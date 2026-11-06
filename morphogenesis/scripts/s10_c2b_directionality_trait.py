"""S10 / C2b: heritable DIRECTIONALITY (not mobility) + transplant control.

Why this test after S9/C2: in C2 the heritable trait controlled *how often* a cell
moves. That costs energy and gave no advantage (heritable 0.459 vs neutral 0.533 right
after the flip). But the property that could actually be selected for is *direction*:
whether a moving cell picks the favourable neighbour or a random one. Here the trait
sets that probability, so a lineage can become "good at going the right way".

Design (no engine changes; uses tag / tag_trait / mutation machinery):
- `type_mode="mixfixed"` is REQUIRED: register_births() - and therefore inheritance and
  mutation - only runs when `cell_type is not None` (run_pond.py:600-602, pond.py:279).
  With the default "fixed" the trait never varies (this is the trap that invalidated S5/C).
- Movement is executed by the engine's own `plastic_moves()` with
  `plastic_direction="random"` (uniformly random free neighbour). We then REPLACE the
  chosen target for a fraction of cells with the favourable neighbour, where that
  fraction is the cell's own heritable trait value. Physics (cost, collisions) stays
  the engine's; only the choice of target changes.

Arms (same seeds, same non-degenerate regime, flip at 200):
  - `neutral`    : trait does not affect the choice (all moves random) -> null model;
  - `heritable`  : P(favourable) = sigmoid(trait * scale);
  - `transplant` : after the flip, swap the trait values of the top-10% and bottom-10%
                   cells. If directionality is adaptive, the swapped "good" cells should
                   now do better; if the effect is positional, nothing changes.

Readout per window: correct_share overall, correct_share of high-trait vs low-trait
cells, R1 (died>=10, alive>=10).
"""
from __future__ import annotations
import argparse, json, os, sys
import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)
from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def correct_mask(pond):
    pos = pond._gradient_position()
    g = pond.cfg.grid
    return (pos >= 0.5)[:, None].expand(g, g)


def favourable_target(pond, y, x, taken):
    """Best free neighbour by current gradient position (the 'right way')."""
    pos = pond._gradient_position()
    n = pond.cfg.grid
    s = pond.state
    best, best_pos = None, -1e9
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if not (0 <= ny < n and 0 <= nx < n):
            continue
        if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
            continue
        pv = float(pos[ny])
        if pv > best_pos:
            best, best_pos = (ny, nx), pv
    return best


def directional_moves(pond, prob_map):
    """Engine picks random targets; we redirect a trait-dependent fraction to the good side."""
    s = pond.state
    moves = pond.plastic_moves()          # plastic_direction="random"
    if not moves:
        return []
    taken = torch.zeros_like(s.alive)
    out = []
    for sy, sx, ty, tx in moves:
        p = float(prob_map[sy, sx])
        if float(torch.rand((), generator=pond.gen_sel).item()) < p:
            fav = favourable_target(pond, sy, sx, taken)
            if fav is not None:
                ty, tx = fav
        taken[ty, tx] = True
        out.append((sy, sx, ty, tx))
    return out


def run_one(seed, args, arm: str):
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="random", plastic_nomove=False,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
        # REQUIRED: inheritance/mutation only run when cell_type exists (design check 06.11)
        type_mode=args.type_mode,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    pond = run.pond
    windows, acc, transplanted = [], None, False
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if s.tag_trait is not None and bool(s.alive.any()):
            if arm == "neutral":
                prob = torch.zeros_like(s.energy)
            elif arm == "heritable":
                prob = torch.sigmoid(s.tag_trait * args.trait_scale)
            else:  # transplant: same rule as heritable, plus the swap below
                prob = torch.sigmoid(s.tag_trait * args.trait_scale)
            moves = directional_moves(pond, prob)
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        if arm == "transplant" and not transplanted and st >= args.flip_at + args.transplant_delay:
            tr = s.tag_trait
            if tr is not None and bool(s.alive.any()):
                vals = tr[s.alive]
                if vals.numel() > 4:
                    hi = float(torch.quantile(vals, 0.9)); lo = float(torch.quantile(vals, 0.1))
                    hi_mask = s.alive & (tr >= hi); lo_mask = s.alive & (tr <= lo)
                    if int(hi_mask.sum()) and int(lo_mask.sum()):
                        tr2 = tr.clone(); tr2[hi_mask] = lo; tr2[lo_mask] = hi
                        s.tag_trait = tr2
            transplanted = True
        a = s.alive; corr = correct_mask(pond); n = int(a.sum())
        if n == 0:
            continue
        cs = float((a & corr).sum() / n)
        tr = s.tag_trait
        hi_share = lo_share = None
        if tr is not None:
            vals = tr[a]
            if vals.numel() > 4:
                q90 = torch.quantile(vals, 0.9); q10 = torch.quantile(vals, 0.1)
                hm = a & (tr >= q90); lm = a & (tr <= q10)
                if int(hm.sum()):
                    hi_share = float((hm & corr).sum() / int(hm.sum()))
                if int(lm.sum()):
                    lo_share = float((lm & corr).sum() / int(lm.sum()))
        if acc is None:
            acc = {"start": st, "n": 0, "cs": 0.0, "hi": [], "lo": []}
        acc["n"] += 1; acc["cs"] += cs
        if hi_share is not None: acc["hi"].append(hi_share)
        if lo_share is not None: acc["lo"].append(lo_share)
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "correct_share": round(acc["cs"] / acc["n"], 4),
                            "hi_trait_correct": round(sum(acc["hi"]) / len(acc["hi"]), 4) if acc["hi"] else None,
                            "lo_trait_correct": round(sum(acc["lo"]) / len(acc["lo"]), 4) if acc["lo"] else None})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(pond.state.step),
                        "correct_share": round(acc["cs"] / acc["n"], 4),
                        "hi_trait_correct": round(sum(acc["hi"]) / len(acc["hi"]), 4) if acc["hi"] else None,
                        "lo_trait_correct": round(sum(acc["lo"]) / len(acc["lo"]), 4) if acc["lo"] else None})
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
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--income", type=float, default=0.04)
    ap.add_argument("--update-cost", type=float, default=0.038)
    ap.add_argument("--repair-cost", type=float, default=0.022)
    ap.add_argument("--init-resource-fill", type=float, default=1.0)
    ap.add_argument("--resource-regen", type=float, default=0.05)
    ap.add_argument("--income-mode", default="proportional")
    ap.add_argument("--seed-cells", type=int, default=32)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--mutation-trait-sigma", type=float, default=0.3)
    ap.add_argument("--trait-scale", type=float, default=2.0)
    ap.add_argument("--transplant-delay", type=int, default=50)
    ap.add_argument("--type-mode", default="mixfixed", choices=["fixed", "mixfixed", "random", "learn"])
    ap.add_argument("--arms", nargs="+", default=["neutral", "heritable", "transplant"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s10_c2b_directionality_trait", "flip_at": args.flip_at, "steps": args.steps,
           "window": args.window, "mutation_rate": args.mutation_rate,
           "mutation_trait_sigma": args.mutation_trait_sigma, "trait_scale": args.trait_scale,
           "type_mode": args.type_mode, "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        cs, hi, lo = [], [], []
        for i in range(nw):
            v = [r["windows"][i]["correct_share"] for r in ar if i < len(r["windows"])]
            h = [r["windows"][i]["hi_trait_correct"] for r in ar if i < len(r["windows"]) and r["windows"][i]["hi_trait_correct"] is not None]
            l = [r["windows"][i]["lo_trait_correct"] for r in ar if i < len(r["windows"]) and r["windows"][i]["lo_trait_correct"] is not None]
            cs.append(round(sum(v) / len(v), 3) if v else None)
            hi.append(round(sum(h) / len(h), 3) if h else None)
            lo.append(round(sum(l) / len(l), 3) if l else None)
        print(f"{arm:11s} correct {cs} | hi {hi} | lo {lo} | R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
