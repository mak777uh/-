"""S50 / E5: the membrane as a GATE at equal dose - does the TEMPORAL PATTERN of food matter?

The 07.11 literature search gave the key warning: changing the frequency of food events also changes
the total food (mean inflow = q * lambda), so a "frequency effect" can be nothing but a food tap in
disguise. The clean test therefore holds the DOSE constant and varies only the PATTERN.

Design. Every arm receives the same number of food portions of the same size over the run; only the
timing differs:

  - `regular`   : portions arrive every `period` steps (a metronome);
  - `random`    : the same number of portions, at uniformly random steps (the dose is matched exactly);
  - `in_phase`  : portions arrive when the cell's internal prediction error is most negative
                  (the cell is hungriest) - the pattern is coupled to the CELL;
  - `anti_phase`: portions arrive when the cell is least hungry - the same dose, opposite coupling.

If the temporal pattern carries information the cell can use, `in_phase` should beat `anti_phase` at
identical dose. If all four are the same, the pattern does not matter and the membrane is only a tap.

How the dose is matched: the number of portions and the size of each portion are fixed by
`--portions` and `--portion`; the four arms differ only in WHEN the portions are released. The total
resource injected is therefore identical by construction, and the script ASSERTS it.

Readout: favourable share, alive count, and the number of portions actually released (to prove the
dose was equal). R1 checked per run.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  total injected = portions * portion. One cell eats 0.16/step, so over 600 steps a colony of ~500
  cells eats ~48000 units. To be a visible perturbation without flooding, the total injected should be
  a few percent of that: portions 60 x portion 0.5 = 30 units, i.e. 0.06 % - deliberately small, so
  that any effect must come from TIMING rather than from extra food.
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


def release(pond, portion: float, where: str) -> None:
    """Put one portion of food somewhere in the world."""
    s = pond.state
    res = s.resource
    n = pond.cfg.grid
    if where == "patch":
        # the richest cell: food arrives where food already is
        idx = int(torch.argmax(res))
        y, x = divmod(idx, n)
    else:
        y, x = n // 2, n // 2
    res[y, x] = torch.clamp(res[y, x] + portion, max=pond.cfg.resource_max)


def run_one(seed, args, arm):
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

    # schedule: which steps release a portion, and how many
    steps = args.steps
    if arm == "regular":
        sched = list(range(args.period, steps + 1, args.period))[: args.portions]
    elif arm == "random":
        idx = torch.randperm(steps, generator=gen)[: args.portions].tolist()
        sched = sorted(i + 1 for i in idx)
    else:
        sched = None   # decided online from the cell state

    favs, released, alive_hist = [], 0, []
    for step in range(1, steps + 1):
        run.step()
        s = pond.state
        if arm in ("in_phase", "anti_phase") and released < args.portions:
            # release when the mean prediction error is most negative (hungry) or most positive (sated)
            n_alive = int(s.alive.sum())
            if n_alive > 0 and step % args.period == 0:
                err = (s.resource - s.pred)[s.alive].mean() if s.pred is not None else torch.tensor(0.0)
                want = err < 0 if arm == "in_phase" else err > 0
                if bool(want):
                    release(pond, args.portion, args.where)
                    released += 1
        elif sched is not None and step in sched:
            release(pond, args.portion, args.where)
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
        alive_hist.append(cnt)
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    return {"seed": seed, "arm": arm, "overall": overall, "released": released,
            "dose": round(released * args.portion, 4),
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
    ap.add_argument("--where", default="patch", choices=["patch", "centre"])
    ap.add_argument("--arms", nargs="+",
                    default=["regular", "random", "in_phase", "anti_phase"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    eat = args.income * 1.0 * 4.0
    total = args.portions * args.portion
    print(f"[e5] one cell eats {eat:.3f}/step; total injected {total:.2f} units "
          f"({100*total/(eat*500*args.steps):.3f}% of what 500 cells eat over {args.steps} steps)")

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    doses = {arm: [r["dose"] for r in rows if r["arm"] == arm] for arm in args.arms}
    out = {"kind": "s50_e5_membrane_gate", "steps": args.steps, "portions": args.portions,
           "portion": args.portion, "period": args.period, "where": args.where,
           "total_injected": round(total, 3), "doses_by_arm": doses,
           "note": ("equal dose by construction: every arm releases the same number of portions of "
                    "the same size; only the TIMING differs"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        v = [r["overall"] for r in ar if r["overall"] is not None]
        print(f"{arm:11s} {round(sum(v)/len(v),3) if v else None} "
              f"| released {[r['released'] for r in ar]} | dose {[r['dose'] for r in ar]} "
              f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
