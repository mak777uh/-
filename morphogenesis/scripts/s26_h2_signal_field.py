"""S26 / H2: does a continuous diffusing field stabilise the lineage, and does an oscillating
source favour a cell that follows the phase over one that holds a fixed reference?

Owner's proposal: the world is discrete, but a continuous field (a diffusing "chemical" signal)
can carry information at a distance and can oscillate; the scientific question is whether those
oscillations stabilise or destabilise a lineage.

Engine addition (additive, off by default): `PondConfig.signal_*` and `Pond.update_signal()`.
With every signal parameter at zero the world is bit-for-bit the old one (anchor checked).

Arms:
  - `no_field`    : no field at all (control);
  - `field_static`: field on, source from living cells, cells step up the field gradient;
  - `field_osc`   : the same, but the source is modulated sinusoidally with `signal_period`;
  - `field_noise` : the same, but the source is pure noise unrelated to food (the CONTROL that
                    separates "field as a channel" from "field as another food sensor").

Readout per window: favourable share, the temporal standard deviation of that share inside the
window (this is the "stability of the lineage" the owner asked about), the field's own amplitude,
and R1.
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


def field_moves(pond):
    """Each living cell that is short of its prediction steps up the field gradient."""
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    if s.signal is None:
        return []
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
        tgt = pond.signal_gradient_step(y, x, taken, n)
        if tgt is None:
            continue
        taken[tgt[0], tgt[1]] = True
        moves.append((y, x, tgt[0], tgt[1]))
    return moves


def run_one(seed, args, arm):
    on = arm != "no_field"
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.2, plastic_move_cost=args.plastic_move_cost,
        plastic_gate="pred", plastic_direction="gradient", plastic_nomove=True,
        signal_diffusion=(args.diffusion if on else 0.0),
        signal_decay=(args.decay if on else 0.0),
        signal_source=(0.0 if arm == "field_noise" else (args.source if on else 0.0)),
        signal_noise=(args.noise if arm == "field_noise" else 0.0),
        signal_oscillate=(args.oscillate if arm == "field_osc" else 0.0),
        signal_period=(args.period if arm == "field_osc" else 0),
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    windows, acc = [], None
    for _ in range(args.steps):
        run.step()
        st = int(pond.state.step)
        s = pond.state
        if on:
            pond.update_signal()
            moves = field_moves(pond)
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
        amp = float(s.signal.abs().mean()) if s.signal is not None else 0.0
        if acc is None:
            acc = {"start": st, "n": 0, "favs": [], "amp": 0.0, "alive": 0}
        acc["n"] += 1
        acc["favs"].append(fav)
        acc["amp"] += amp
        acc["alive"] += n
        if acc["n"] >= args.window:
            f = acc["favs"]
            mu = sum(f) / len(f)
            sd = (sum((v - mu) ** 2 for v in f) / len(f)) ** 0.5
            windows.append({"start": acc["start"], "end": st,
                            "favourable_share": round(mu, 4),
                            "stability_sd": round(sd, 4),
                            "field_amplitude": round(acc["amp"] / acc["n"], 4),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": arm, "windows": windows,
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
    ap.add_argument("--diffusion", type=float, default=0.10)
    ap.add_argument("--decay", type=float, default=0.05)
    ap.add_argument("--source", type=float, default=1.0)
    ap.add_argument("--noise", type=float, default=0.5)
    ap.add_argument("--oscillate", type=float, default=0.8)
    ap.add_argument("--period", type=int, default=50)
    ap.add_argument("--arms", nargs="+", default=["no_field", "field_static", "field_osc", "field_noise"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s26_h2_signal_field", "steps": args.steps, "window": args.window,
           "diffusion": args.diffusion, "decay": args.decay, "source": args.source,
           "noise": args.noise, "oscillate": args.oscillate, "period": args.period,
           "note": ("field is additive: with all signal_* at zero the world is bit-for-bit the old one "
                    "(anchor checked). field_noise is the control that separates 'field as a channel' "
                    "from 'field as another food sensor'."),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        print(f"== {arm}")
        for field in ("favourable_share", "stability_sd", "field_amplitude", "alive_mean"):
            vals = []
            for i in range(nw):
                v = [r["windows"][i][field] for r in ar if i < len(r["windows"])]
                vals.append(round(sum(v) / len(v), 3) if v else None)
            print(f"   {field:18s} {vals}")
        print(f"   R1 {[r['R1'] for r in ar]} | alive {[r['final']['alive'] for r in ar]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
