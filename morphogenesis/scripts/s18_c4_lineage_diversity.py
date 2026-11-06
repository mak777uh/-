"""S18 / C4: is the inheritance null caused by the lineage monopoly, or by the trait itself?

Why this test. S9/C2 and S10/C2b found that a heritable behavioural trait gives no advantage. But in
every run one lineage held 95-97% of the population, so there was almost no standing variation for
selection to act on. That is a confound: the null could mean "the trait is not selectable" OR "there
was nothing to select among".

This script attacks the confound with knobs that already exist in the engine (no world/ changes):

  - `quota_share`      : a lineage may not hold more than a fraction of the living cells
  - `bud_refractory`   : a lineage may not bud more often than once per K steps
  - `mutation_rate`    : how often a newborn gets a fresh lineage label with a mutated trait
  - `mutation_trait_sigma` : how far the trait moves per mutation

Arms (same seeds, same world, heritable DIRECTIONALITY as in S10 - the trait sets the chance that a
moving cell picks the favourable neighbour):
  - `monopoly`  : quota_share=1.0, bud_refractory=0   (the S10 setting; one lineage dominates)
  - `diverse`   : quota_share=0.25, bud_refractory=20 (no lineage may hold a quarter of the cells)

Readout per window: number of living lineages, top lineage share, and the correct share of the
high-trait vs low-trait cells. If the null was a monopoly artefact, `diverse` should show (a) many more
lineages, (b) hi-trait cells clearly above lo-trait cells, and (c) a rising trend in that difference.

Sensitivity arithmetic (contract 3c, computed BEFORE the run):
  - the trait must actually vary: mutation_rate > 0 and type_mode != "fixed" (register_births is gated
    on cell_type, see S9); both are set here;
  - the quota must be able to bind: 0.25 of a ~550-cell population is ~137 cells, well above the
    observed top-lineage sizes once the quota acts, so the knob is not inert;
  - R1 (died >= 10, alive >= 10) is checked per run.
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


def favourable_target(pond, y, x, taken):
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
    s = pond.state
    moves = pond.plastic_moves()
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


def run_one(seed, args, arm):
    quota, refractory = (1.0, 0) if arm == "monopoly" else (args.quota, args.refractory)
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="random", plastic_nomove=False,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
        type_mode=args.type_mode,
        quota_share=quota, bud_refractory=refractory,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if s.tag_trait is not None and bool(s.alive.any()):
            prob = torch.sigmoid(s.tag_trait * args.trait_scale)
            moves = directional_moves(pond, prob)
            if moves:
                pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        a = s.alive
        n = int(a.sum())
        if n == 0:
            continue
        pos = pond._gradient_position()
        corr = (pos >= 0.5)[:, None].expand(cfg.grid, cfg.grid)
        cs = float((a & corr).sum() / n)
        tr = s.tag_trait
        hi_share = lo_share = None
        n_lines = top_share = None
        if tr is not None and s.tag is not None:
            vals = tr[a]
            if vals.numel() > 4:
                q90 = torch.quantile(vals, 0.9)
                q10 = torch.quantile(vals, 0.1)
                hm = a & (tr >= q90)
                lm = a & (tr <= q10)
                if int(hm.sum()):
                    hi_share = float((hm & corr).sum() / int(hm.sum()))
                if int(lm.sum()):
                    lo_share = float((lm & corr).sum() / int(lm.sum()))
            alive_tags = s.tag[a]
            uniq, counts = torch.unique(alive_tags, return_counts=True)
            n_lines = int(uniq.numel())
            top_share = float(counts.max() / counts.sum())
        if acc is None:
            acc = {"start": st, "n": 0, "cs": 0.0, "hi": [], "lo": [], "lines": [], "top": []}
        acc["n"] += 1
        acc["cs"] += cs
        if hi_share is not None:
            acc["hi"].append(hi_share)
        if lo_share is not None:
            acc["lo"].append(lo_share)
        if n_lines is not None:
            acc["lines"].append(n_lines)
            acc["top"].append(top_share)
        if acc["n"] >= args.window:
            windows.append({
                "start": acc["start"], "end": st,
                "correct_share": round(acc["cs"] / acc["n"], 4),
                "hi_trait_correct": round(sum(acc["hi"]) / len(acc["hi"]), 4) if acc["hi"] else None,
                "lo_trait_correct": round(sum(acc["lo"]) / len(acc["lo"]), 4) if acc["lo"] else None,
                "n_lineages": round(sum(acc["lines"]) / len(acc["lines"]), 1) if acc["lines"] else None,
                "top_lineage_share": round(sum(acc["top"]) / len(acc["top"]), 3) if acc["top"] else None,
            })
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "quota_share": quota, "bud_refractory": refractory,
            "windows": windows,
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
    ap.add_argument("--type-mode", default="mixfixed", choices=["fixed", "mixfixed", "random", "learn"])
    ap.add_argument("--quota", type=float, default=0.25)
    ap.add_argument("--refractory", type=int, default=20)
    ap.add_argument("--arms", nargs="+", default=["monopoly", "diverse"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s18_c4_lineage_diversity", "flip_at": args.flip_at, "steps": args.steps,
           "window": args.window, "mutation_rate": args.mutation_rate,
           "mutation_trait_sigma": args.mutation_trait_sigma, "quota": args.quota,
           "refractory": args.refractory, "type_mode": args.type_mode,
           "sensitivity_note": ("trait varies only with mutation_rate>0 and type_mode!=fixed; quota 0.25 of "
                                "~550 cells is ~137, above the observed top-lineage sizes, so the knob can bind"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        print(f"== {arm} (quota {ar[0]['quota_share']}, refractory {ar[0]['bud_refractory']})")
        for field in ("correct_share", "n_lineages", "top_lineage_share", "hi_trait_correct", "lo_trait_correct"):
            vals = []
            for i in range(nw):
                v = [r["windows"][i][field] for r in ar
                     if i < len(r["windows"]) and r["windows"][i].get(field) is not None]
                vals.append(round(sum(v) / len(v), 3) if v else None)
            print(f"   {field:20s} {vals}")
        print(f"   R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
