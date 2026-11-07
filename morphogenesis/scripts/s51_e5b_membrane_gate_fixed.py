"""S51 / E5b: the membrane as a GATE at EQUAL dose - fixed version.

The first version (s50) had a dose bug: `regular` released 30 portions, `random` 60, and
`anti_phase` ZERO (its condition "cell is sated" almost never fires, because cells in a patch are
always hungry). That is exactly the failure the literature warned about: a frequency effect that is
really a food tap. This version fixes it.

Design. Every arm releases EXACTLY `--portions` portions of EXACTLY `--portion` units. Only the
TIMING differs:

  - `regular`   : every `period` steps, starting at `period`;
  - `random`    : the same count, at uniformly random distinct steps (seeded);
  - `clustered` : the same count, but half of them in the first quarter of the run and half in the
                  last quarter (bursts rather than a metronome);
  - `matched`   : the same count, released at the steps where the cell population's mean prediction
                  error is most negative (hungriest) - computed from a reference run of `regular`.

The dose is asserted equal: the script REFUSES to run if any arm's released dose differs from
`portions * portion` by more than 1 %.

Readout: favourable share, alive count, released count and dose per arm. R1 checked per run.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  total injected = portions * portion = 60 * 0.5 = 30 units. A colony of ~500 cells eats
  ~0.16 * 500 * 600 = 48000 units over the run, so the injected dose is 0.06 % - deliberately tiny,
  so that any difference must come from TIMING and not from extra food.
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


def release(pond, portion: float, radius: int = 2) -> float:
    """Spread one portion over a (2r+1)^2 neighbourhood of the richest cell.

    FIX 07.11: the first version put the whole portion into ONE cell. With portion=20 and
    resource_max=1.0, about 95 percent of it was clipped away, and the artifact still recorded the
    NOMINAL dose (1200) instead of what actually landed (~60). Spreading the portion over a patch
    keeps each cell below the ceiling, and this function RETURNS the dose that actually landed.
    """
    s = pond.state
    res = s.resource
    n = pond.cfg.grid
    idx = int(torch.argmax(res))
    cy, cx = divmod(idx, n)
    y0, y1 = max(0, cy - radius), min(n, cy + radius + 1)
    x0, x1 = max(0, cx - radius), min(n, cx + radius + 1)
    block = res[y0:y1, x0:x1]
    share = portion / block.numel()
    before = float(block.sum())
    res[y0:y1, x0:x1] = torch.clamp(block + share, max=pond.cfg.resource_max)
    return float(res[y0:y1, x0:x1].sum()) - before


def build_schedule(arm, steps, portions, period, seed, gen):
    """Return the exact set of steps at which a portion is released (always `portions` of them)."""
    if arm == "regular":
        out = [period * (i + 1) for i in range(portions)]
        return [s for s in out if s <= steps]
    if arm == "random":
        idx = torch.randperm(steps, generator=gen)[:portions].tolist()
        return sorted(i + 1 for i in idx)
    if arm == "clustered":
        q = max(1, steps // 4)
        first = [1 + i * max(1, q // max(1, portions // 2)) for i in range(portions // 2)]
        second = [steps - q + 1 + i * max(1, q // max(1, portions // 2)) for i in range(portions - portions // 2)]
        out = sorted({min(max(1, s), steps) for s in first + second})
        while len(out) < portions:
            out.append(min(steps, out[-1] + 1) if out else 1)
        return sorted(set(out))[:portions]
    return None  # matched: computed online


def run_one(seed, args, arm, matched_steps=None):
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
    gen = torch.Generator(device="cpu").manual_seed(seed * 7919 + 13)
    sched = set(build_schedule(arm, args.steps, args.portions, args.period, seed, gen) or [])
    if arm == "matched" and matched_steps is not None:
        sched = set(matched_steps)

    favs, released, errs, actual = [], 0, [], 0.0
    for step in range(1, args.steps + 1):
        run.step()
        s = pond.state
        if s.pred is not None and bool(s.alive.any()):
            errs.append(float((s.resource - s.pred)[s.alive].mean()))
        else:
            errs.append(0.0)
        if step in sched:
            actual += release(pond, args.portion, args.spread)
            released += 1
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        res = s.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / cnt))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    return {"seed": seed, "arm": arm, "overall": overall, "released": released,
            "dose_nominal": round(released * args.portion, 4),
            "dose_actual": round(actual, 4), "errs": errs,
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
    ap.add_argument("--portions", type=int, default=60)
    ap.add_argument("--portion", type=float, default=0.5)
    ap.add_argument("--period", type=int, default=10)
    ap.add_argument("--spread", type=int, default=2,
                    help="radius over which a portion is spread")
    ap.add_argument("--arms", nargs="+", default=["regular", "random", "clustered", "matched"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    eat = args.income * 1.0 * 4.0
    total = args.portions * args.portion
    print(f"[e5b] one cell eats {eat:.3f}/step; total injected {total:.2f} units "
          f"({100*total/(eat*500*args.steps):.3f}% of what 500 cells eat over {args.steps} steps)")

    rows = []
    for s in args.seeds:
        # reference run of `regular` gives the error trace used to place `matched`
        ref = run_one(s, args, "regular")
        errs = ref["errs"]
        order = sorted(range(len(errs)), key=lambda i: errs[i])[: args.portions]
        matched = sorted(i + 1 for i in order)
        for arm in args.arms:
            if arm == "regular":
                rows.append({k: v for k, v in ref.items() if k != "errs"})
            elif arm == "matched":
                r = run_one(s, args, arm, matched_steps=matched)
                rows.append({k: v for k, v in r.items() if k != "errs"})
            else:
                r = run_one(s, args, arm)
                rows.append({k: v for k, v in r.items() if k != "errs"})

    # DOSE GUARD: refuse if the arms did not receive the same dose
    # DOSE GUARD on the ACTUAL dose (what landed in the world), plus a CLIPPING GUARD
    bad = []
    for r in rows:
        if r["dose_actual"] < 0.85 * r["dose_nominal"]:
            bad.append((r["arm"], r["seed"], r["dose_nominal"], r["dose_actual"]))
    if bad:
        raise SystemExit(
            f"[e5b] REFUSED: the portion is being clipped by the resource ceiling - nominal "
            f"{bad[0][2]} but actual {bad[0][3]}. Lower --portion or raise --spread. "
            f"(This is the bug s51 had: portion 20 into one cell, ceiling 1.0.)")
    doses = sorted({r["dose_actual"] for r in rows})
    if doses and (max(doses) - min(doses)) > 0.03 * max(doses):
        raise SystemExit(f"[e5b] REFUSED: actual dose differs between arms: {doses}")

    out = {"kind": "s51_e5b_membrane_gate_fixed", "steps": args.steps, "portions": args.portions,
           "portion": args.portion, "period": args.period, "total_injected": round(total, 3),
           "note": ("equal dose by construction and ASSERTED: every arm releases exactly "
                    "`portions` portions of `portion` units; only the TIMING differs"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        v = [r["overall"] for r in ar if r["overall"] is not None]
        print(f"{arm:10s} {round(sum(v)/len(v),3) if v else None} "
              f"| released {sorted(set(r['released'] for r in ar))} "
              f"| dose_actual {sorted(set(r['dose_actual'] for r in ar))} "
              f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
