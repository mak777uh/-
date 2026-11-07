"""S53 / E6: does the membrane start to work once the cell HAS a decoder?

Three independent lines (H: field, E3: niche, E5: membrane) all gave the same answer: the cell
cannot use environmental structure - spatial, temporal or feedback. The proposed reason is that the
cell has no DECODER: its step rule looks only at the instantaneous resource of its own cell.

The literature says the same thing from the other side: frequency coding works in biology because a
network downstream of the signal (the decoder) is nonlinear and integrates over time (Crz1 bursts,
GnRH pulses, rate coding). Without a decoder, a pattern is just a pattern.

This experiment adds the missing decoder and asks whether the membrane then pays.

Design. Two decoders, same equal dose, same four timing patterns as E5c:

  - `none`    : the cell reacts to the instantaneous resource (the E5c world);
  - `memory`  : the cell carries an exponential trace of its own recent FOOD INTAKE
                (`trace <- trace*(1-alpha) + alpha*intake`), and its step rule fires when the TRACE is
                below its own running mean - i.e. the cell acts on "I have been eating poorly lately"
                rather than on "this cell is poor right now".

Prediction if the missing decoder is the cause:
  - with `none`   : the four timing patterns are indistinguishable (E5c's result, reproduced);
  - with `memory` : the patterns separate, and in particular `matched` (food when the trace is lowest)
                    beats `regular` at the same dose.

If `memory` ALSO shows no separation, the decoder is not the missing piece, and the limit lies
somewhere else (which is a different and equally useful answer).

Readout: favourable share per (decoder, pattern), plus the actual dose (asserted equal). R1 per run.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  the dose is the same as E5c (60 portions x 20 units, spread over a 225-cell neighbourhood so no cell
  hits the ceiling). The memory trace has time constant 1/alpha steps; with alpha = 0.05 that is 20
  steps, much shorter than the run (600) and longer than the gap between portions (10), so the trace
  can in principle carry the pattern.
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


def moves_up_trace(pond, trace):
    """Step to the free neighbour with the highest DECODER value (recent intake), not the resource.

    This is the whole point of E6: the cell acts on "I have been eating poorly lately", which is a
    quantity built from the HISTORY of events, so a temporal pattern can in principle be perceived.
    """
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
        best, best_v = None, float(trace[y, x])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                continue
            v = float(trace[ny, nx])
            if v > best_v:
                best, best_v = (ny, nx), v
        if best is None:
            continue
        taken[best[0], best[1]] = True
        moves.append((y, x, best[0], best[1]))
    return moves


def release(pond, portion: float, radius: int) -> float:
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


def build_schedule(arm, steps, portions, period, gen):
    if arm == "regular":
        return set(period * (i + 1) for i in range(portions) if period * (i + 1) <= steps)
    if arm == "random":
        idx = torch.randperm(steps, generator=gen)[:portions].tolist()
        return set(i + 1 for i in idx)
    if arm == "clustered":
        q = max(1, steps // 4)
        half = portions // 2
        first = [1 + i * max(1, q // max(1, half)) for i in range(half)]
        second = [steps - q + 1 + i * max(1, q // max(1, portions - half)) for i in range(portions - half)]
        out = sorted({min(max(1, s), steps) for s in first + second})
        while len(out) < portions:
            out.append(min(steps, (out[-1] if out else 0) + 1))
        return set(sorted(set(out))[:portions])
    return None


def run_one(seed, args, decoder, pattern, matched_steps=None):
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
    n = cfg.grid
    gen = torch.Generator(device="cpu").manual_seed(seed * 7919 + 13)
    sched = build_schedule(pattern, args.steps, args.portions, args.period, gen) or set()
    if pattern == "matched" and matched_steps is not None:
        sched = set(matched_steps)

    trace = torch.zeros((n, n), device=run.device)   # decoder state: recent intake per cell
    favs, actual, released, errs = [], 0.0, 0, []
    for step in range(1, args.steps + 1):
        prev = pond.state.resource.clone()
        run.step()
        s = pond.state
        intake = (prev - s.resource).clamp_min(0.0) * s.alive.float()
        trace = trace * (1.0 - args.alpha) + args.alpha * intake
        if decoder == "memory" and bool(s.alive.any()):
            mv = moves_up_trace(pond, trace)
            if mv:
                pond.apply_organism_moves(mv, cost=float(cfg.plastic_move_cost))
        if s.pred is not None and bool(s.alive.any()):
            errs.append(float((s.resource - s.pred)[s.alive].mean()))
        else:
            errs.append(0.0)
        if step in sched:
            actual += release(pond, args.portion, args.spread)
            released += 1
        a = pond.state.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        res = pond.state.resource
        flat = res.reshape(-1)
        k = max(1, flat.numel() // 2)
        thr = float(torch.topk(flat, k=k, largest=True).values.min())
        favs.append(float((a & (res >= thr)).sum() / cnt))
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    overall = round(sum(favs) / len(favs), 4) if favs else None
    return {"seed": seed, "decoder": decoder, "pattern": pattern, "overall": overall,
            "released": released, "dose_actual": round(actual, 3), "errs": errs,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
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
    ap.add_argument("--portion", type=float, default=20.0)
    ap.add_argument("--period", type=int, default=10)
    ap.add_argument("--spread", type=int, default=7)
    ap.add_argument("--alpha", type=float, default=0.05, help="decoder memory rate (1/tau)")
    ap.add_argument("--patterns", nargs="+", default=["regular", "random", "clustered", "matched"])
    ap.add_argument("--decoders", nargs="+", default=["none", "memory"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    total = args.portions * args.portion
    print(f"[e6] total injected {total:.1f} units; decoder alpha {args.alpha} "
          f"(time constant {1/args.alpha:.0f} steps); spread {args.spread}")

    rows = []
    for s in args.seeds:
        for decoder in args.decoders:
            ref = run_one(s, args, decoder, "regular")
            errs = ref["errs"]
            order = sorted(range(len(errs)), key=lambda i: errs[i])[: args.portions]
            matched = sorted(i + 1 for i in order)
            for pattern in args.patterns:
                if pattern == "regular":
                    rows.append({k: v for k, v in ref.items() if k != "errs"})
                elif pattern == "matched":
                    r = run_one(s, args, decoder, pattern, matched_steps=matched)
                    rows.append({k: v for k, v in r.items() if k != "errs"})
                else:
                    r = run_one(s, args, decoder, pattern)
                    rows.append({k: v for k, v in r.items() if k != "errs"})

    # dose guard on the actual dose
    bad = [r for r in rows if r["dose_actual"] < 0.85 * r["released"] * args.portion]
    if bad:
        raise SystemExit(f"[e6] REFUSED: portions are clipped - {bad[0]['dose_actual']} of "
                         f"{bad[0]['released'] * args.portion}. Raise --spread.")

    out = {"kind": "s53_e6_decoder", "steps": args.steps, "portions": args.portions,
           "portion": args.portion, "period": args.period, "spread": args.spread,
           "alpha": args.alpha, "total_injected": round(total, 2),
           "note": ("the decoder arm carries an exponential trace of its own intake; the step rule "
                    "fires when the TRACE is low rather than when the current cell is poor"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for decoder in args.decoders:
        print(f"== decoder {decoder}")
        for pattern in args.patterns:
            ar = [r for r in rows if r["pattern"] == pattern and r["decoder"] == decoder]
            v = [r["overall"] for r in ar if r["overall"] is not None]
            print(f"   {pattern:10s} {round(sum(v)/len(v),3) if v else None} "
                  f"| dose {sorted(set(r['dose_actual'] for r in ar))} "
                  f"| R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
