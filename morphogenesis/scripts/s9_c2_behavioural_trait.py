"""S9 / C2: heritable BEHAVIOURAL trait + transplant control.

Owner's hypothesis: "adaptive individuals appear later". S5/C showed that a heritable
trait modulating *investment* produced no visible lineage selection, because one clone
holds 95-97% of the population. This test makes the trait directly behavioural and
mortality-relevant, and adds the control that S5 lacked: a TRANSPLANT.

Design (no engine changes; uses existing tag / tag_trait / mutation machinery):
- `tag_trait` is heritable and mutates (mutation_rate, mutation_trait_sigma).
- We read the trait OUTSIDE the engine to decide mobility: a cell's own trait value
  scales its chance to attempt a directed step. Cells are moved by the engine's own
  `plastic_moves()` path, so the physics stays the same; only WHO moves changes.
  Implementation: run the world with `plastic_eta>0` (so `plastic_moves` is live) and
  temporarily set `plastic_gate="random"` with `plastic_prob` = the trait-derived
  probability per cell. Because `plastic_prob` is a scalar, we approximate by drawing a
  per-cell gate ourselves: we call `pond.plastic_moves()` only for cells whose trait
  exceeds a threshold, by masking `state.alive` for the call (see `_gated_moves`).

Arms (same seeds, same non-degenerate regime, flip at 200):
  - `neutral`   : trait has NO effect on movement (mobility uniform) -> null model;
  - `heritable` : mobility probability = sigmoid(trait) -> heritable behavioural variation;
  - `transplant`: after the flip, take the top-trait lineage and the bottom-trait lineage
                  and swap their positions; if the trait is adaptive, the high-trait
                  lineage should recover faster in the new environment.

Readout per window after flip: correct_share overall, correct_share of high-trait vs
low-trait cells, lineage counts, R1 (died>=10, alive>=10).
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


def gated_moves(pond, prob_map):
    """Run the engine's own plastic_moves() but only for cells whose trait gate passes.

    We temporarily hide the cells that fail the gate from `state.alive`, call the engine
    method (so movement physics, collision resolution and the CI counters are unchanged),
    then restore the mask. Cells that pass are the only candidates.
    """
    s = pond.state
    keep = s.alive.clone()
    fail = keep & (torch.rand(keep.shape, generator=pond.gen_sel, device=pond.device) >= prob_map)
    s.alive = keep & ~fail
    try:
        moves = pond.plastic_moves()
    finally:
        s.alive = keep
    return moves


def run_one(seed, args, arm: str):
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=False,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
        # DESIGN CHECK (06.11): register_births() - and therefore tag inheritance and
        # mutation - is only called when `cell_type is not None` (run_pond.py:600-602),
        # and cell_type exists only when `type_mode != "fixed"` (pond.py:279). With the
        # default "fixed" the trait never varies at all (std=0, mutations=0), which is
        # exactly why S5/C saw null==selection. "mixfixed" turns the machinery on.
        type_mode=args.type_mode,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    pond = run.pond
    windows, acc = [], None
    transplanted = False
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        # --- behavioural step driven by the heritable trait (outside the engine) ---
        if arm != "neutral" and s.tag_trait is not None and bool(s.alive.any()):
            prob = torch.full_like(s.energy, 0.5)
            if arm == "heritable":
                prob = torch.sigmoid(s.tag_trait * args.trait_scale)
            moves = gated_moves(pond, prob)
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        # --- transplant control: swap top-trait and bottom-trait lineages once, after flip ---
        if arm == "transplant" and not transplanted and st >= args.flip_at + args.transplant_delay:
            tr = s.tag_trait
            if tr is not None and bool(s.alive.any()):
                vals = tr[s.alive]
                hi = float(torch.quantile(vals, 0.9)); lo = float(torch.quantile(vals, 0.1))
                hi_mask = s.alive & (tr >= hi); lo_mask = s.alive & (tr <= lo)
                if int(hi_mask.sum()) and int(lo_mask.sum()):
                    # swap the trait labels (not the cells): the high-trait cells now sit
                    # where the low-trait cells were and vice versa
                    tr2 = tr.clone()
                    tr2[hi_mask] = lo; tr2[lo_mask] = hi
                    s.tag_trait = tr2
            transplanted = True
        # --- readout ---
        a = s.alive; corr = correct_mask(pond)
        n = int(a.sum())
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
    ap.add_argument("--type-mode", default="mixfixed", choices=["fixed", "mixfixed", "random", "learn"],
                    help="must be != fixed for tag inheritance/mutation to run (design check)")
    ap.add_argument("--arms", nargs="+", default=["neutral", "heritable", "transplant"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s9_c2_behavioural_trait", "flip_at": args.flip_at, "steps": args.steps,
           "window": args.window, "mutation_rate": args.mutation_rate,
           "mutation_trait_sigma": args.mutation_trait_sigma, "trait_scale": args.trait_scale,
           "n_seeds": len(args.seeds), "rows": rows}
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
