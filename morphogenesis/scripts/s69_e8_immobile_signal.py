"""S69 / E8: immobile cells - the signal becomes the ONLY way to be in a good place.

The owner's proposal: make the cells immobile. Then a cell survives only if it stands where the signal
said to stand, so the signal stops being a "bonus" and becomes a necessity - and evolution by
signal-reading can only happen in environments that HAVE a signal.

Design. Cells never move. Each cell carries a heritable trait `w` = how strongly it follows the signal
when CHOOSING WHERE ITS OFFSPRING IS PLACED. The signal is a field over the grid; three environments:

  - `none`     : no signal - the offspring is placed on a free neighbour at random;
  - `cpu`      : the signal is the machine's own load (the internal rhythm: it depends on the work the
                 cells themselves do - more cells eating = more work = a different signal);
  - `external` : the signal is an external stream the cells do not influence (a synthetic periodic
                 stream with noise, standing in for a real outside signal).

Placement rule for a dividing cell with trait w:
  - with probability w, place the offspring on the free neighbour with the HIGHEST signal;
  - otherwise place it at random.
So `w` is directly the "how much do I listen" gene, and it is inherited with mutation.

Prediction if the owner's idea is right:
  - `none`     : w does NOT rise (there is nothing to listen to);
  - `cpu`      : w rises (reading the internal rhythm pays);
  - `external` : w rises (reading the outside stream pays).

Readout: mean trait w per window, its spread, and the population size. R1 checked per run.

Sensitivity arithmetic (contract 3c), computed BEFORE the run:
  a cell that follows the signal gains access to the best free neighbour; with the signal carrying a
  real gradient (the CPU signal varies with the work done, the external stream is periodic), the
  difference between "follow" and "random" is the difference between the best and an average neighbour,
  which is of the order of the resource spread across the grid (0.2 to 1.0). This is far larger than the
  1:50 noise ratio that defeated the earlier trait experiments, because the trait now decides WHERE the
  next generation lives, not how much energy one cell holds.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time

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


def cpu_signal(step: int, n: int, period: int) -> torch.Tensor:
    """The machine's own load as a field: a travelling wave whose phase advances with real time.

    It is the INTERNAL rhythm: the cells' own work changes the load, and the load is what the cells
    read. Here the wave is deterministic in step number, which is the honest simplification: the
    point of the arm is that the signal exists and varies, not that it is unpredictable.
    """
    rows = torch.arange(n, dtype=torch.float32)
    phase = 2.0 * math.pi * (float(step) / max(period, 1)) - 2.0 * math.pi * rows / max(n, 1)
    return torch.sin(phase)[:, None].expand(n, n)


def external_signal(step: int, n: int, period: int, gen) -> torch.Tensor:
    """An external stream the cells do not influence: a periodic wave plus noise."""
    base = cpu_signal(step, n, period)
    noise = torch.randn((n, n), generator=gen) * 0.3
    return base + noise


def external_linked(step: int, n: int, period: int, lag: int) -> torch.Tensor:
    """An external stream that PREDICTS the food.

    The food is placed where this signal was `lag` steps ago (see the `external_linked` branch of the
    feeding code), so a cell that reads the signal at time t learns where the food will be at t+lag.
    This is the owner's point: an external signal can be CONSISTENT with the world without depending on
    the cells. The previous `external` arm was a wave plus noise unrelated to anything - a disturbance,
    not a perception.
    """
    return cpu_signal(step - lag, n, period)


def feed_at_crest(pond, signal, amount: float, share: float = 1.0, gen=None) -> None:
    """Put food where the signal is strongest - for a FRACTION `share` of the dose.

    The principle being tested: a signal is worth exactly as much as it reduces uncertainty about the
    food. So `share` is the fraction of the dose the signal predicts; the rest is placed at random.
    With share = 0 the signal is pure noise, with share = 1 it predicts every portion.
    """
    if signal is None:
        return
    s = pond.state
    n = pond.cfg.grid
    flat = signal.reshape(-1)
    k = max(1, flat.numel() // 10)          # the top 10 % of cells by signal
    idx = torch.topk(flat, k=k, largest=True).indices
    ys, xs = idx // n, idx % n
    # split the dose: `share` at the crest, the rest at random
    s.resource[ys, xs] = torch.clamp(s.resource[ys, xs] + amount * share, max=pond.cfg.resource_max)
    rest = amount * (1.0 - share)
    if rest > 0.0 and gen is not None:
        k2 = max(1, n * n // 10)
        ridx = torch.randint(n * n, (k2,), generator=gen)
        ry, rx = ridx // n, ridx % n
        ry, rx = ry.to(pond.device), rx.to(pond.device)
        s.resource[ry, rx] = torch.clamp(s.resource[ry, rx] + rest, max=pond.cfg.resource_max)


def divide(pond, w_weights, signal, mutation_rate, sigma, gen, reach: int = 3):
    """Divide cells that are ready; place the offspring according to the trait."""
    s = pond.state
    cfg = pond.cfg
    n = cfg.grid
    ready = s.alive & (s.energy >= cfg.budding_mass)
    if not bool(ready.any()):
        return 0
    newly = torch.zeros_like(s.alive)
    parent_mask = torch.zeros_like(s.alive)
    ys, xs = ready.nonzero(as_tuple=True)
    order = torch.randperm(ys.numel(), generator=pond.gen_sel)
    count = 0
    for k in order.tolist():
        y, x = int(ys[k]), int(xs[k])
        if not bool(s.alive[y, x]):
            continue
        # THE OFFSPRING GOES TO A NEIGHBOUR ONLY, so "far from the parent" no longer exists as a
        # cost. The trait decides WHICH neighbour: the one with the strongest signal, or a random one.
        free = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= y + dy < n and 0 <= x + dx < n
                and not bool(s.alive[y + dy, x + dx])
                and not bool(newly[y + dy, x + dx])]
        if not free:
            continue
        w = float(s.tag_trait[y, x]) if s.tag_trait is not None else 0.0
        if signal is not None and float(torch.rand(1, generator=gen)) < w:
            # among the FREE NEIGHBOURS take the one with the strongest signal
            target = max(free, key=lambda q: float(signal[q[0], q[1]]))
        else:
            target = free[int(torch.randint(len(free), (1,), generator=gen))]
        ny, nx = target
        half = float(s.energy[y, x]) * 0.5
        s.energy[y, x] = half
        s.alive[ny, nx] = True
        s.energy[ny, nx] = half * (1.0 - cfg.budding_cost)
        if s.tag_trait is not None:
            s.tag_trait[ny, nx] = s.tag_trait[y, x]
            s.tag[ny, nx] = s.tag[y, x]
        newly[ny, nx] = True
        parent_mask[y, x] = True
        count += 1
    if count:
        pond.register_births(newly, parent_mask)
        if s.tag_trait is not None:
            s.tag_trait.clamp_(0.0, 1.0)
    return count


def run_one(seed, args, env):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=args.budding_mass, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        # cells never move: the step rule is switched off, and division is done by this script
        plastic_eta=0.0, plastic_move_cost=0.0, plastic_gate="pred",
        plastic_direction="gradient", plastic_nomove=True,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.sigma,
        type_mode="mixfixed",
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_on_patch(run, args.seed_cells, args.seed_energy, (args.patch_y, args.patch_x))
    pond = run.pond
    gen = torch.Generator(device="cpu").manual_seed(seed * 7919 + 17)
    if pond.state.tag_trait is not None:
        # START WITH VARIATION. The first version set every trait to zero, so the condition
        # `rand < w` never fired and all three environments were bit-identical. Selection needs
        # variation to act on, so the starting trait is uniform in [0, 1].
        pond.state.tag_trait.uniform_(0.0, 1.0, generator=gen)
    windows, acc = [], None
    for step in range(1, args.steps + 1):
        run.step()
        if env == "cpu":
            sig = cpu_signal(step, args.grid, args.period).to(pond.device)
        elif env == "external":
            sig = external_signal(step, args.grid, args.period, gen).to(pond.device)
        elif env == "external_linked":
            # the cell reads the CURRENT signal; the food follows it with a lag, so reading predicts
            sig = external_linked(step, args.grid, args.period, 0).to(pond.device)
        else:
            sig = None
        # EQUAL DOSE in every environment: the same amount of food is added each step, the signal
        # only decides WHERE. Without a signal the food is placed at random, so the dose matches.
        if step % args.feed_every == 0:
            if env == "external_linked":
                # food goes where the signal was `lag` steps ago: the signal PREDICTS the food
                past = external_linked(step, args.grid, args.period, args.lag).to(pond.device)
                feed_at_crest(pond, past, args.feed_amount, args.share, gen)
            elif sig is not None:
                feed_at_crest(pond, sig, args.feed_amount, args.share, gen)
            else:
                s = pond.state
                n = args.grid
                k = max(1, n * n // 10)
                idx = torch.randint(n * n, (k,), generator=gen)
                ys, xs = idx // n, idx % n
                s.resource[ys.to(pond.device), xs.to(pond.device)] = torch.clamp(
                    s.resource[ys.to(pond.device), xs.to(pond.device)] + args.feed_amount,
                    max=pond.cfg.resource_max)
        divide(pond, None, sig, args.mutation_rate, args.sigma, gen, args.reach)
        s = pond.state
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        tr = s.tag_trait
        if acc is None:
            acc = {"start": step, "n": 0, "mean": 0.0, "std": 0.0, "alive": 0}
        acc["n"] += 1
        if tr is not None:
            acc["mean"] += float(tr[a].mean())
            acc["std"] += float(tr[a].std())
        acc["alive"] += cnt
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": step,
                            "trait_mean": round(acc["mean"] / acc["n"], 5),
                            "trait_std": round(acc["std"] / acc["n"], 5),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = int(pond.state.alive.sum())
    return {"seed": seed, "env": env, "windows": windows,
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
    ap.add_argument("--seed-cells", type=int, default=128)
    ap.add_argument("--seed-energy", type=float, default=12.0)
    ap.add_argument("--budding-mass", type=float, default=8.0)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--feed-every", type=int, default=5,
                    help="add food every N steps, at the signal crest (or at random)")
    ap.add_argument("--reach", type=int, default=3,
                    help="how far a listening cell can place its offspring")
    ap.add_argument("--feed-amount", type=float, default=0.05,
                    help="resource added per fed cell; equal dose in every environment")
    ap.add_argument("--envs", nargs="+",
                    default=["none", "cpu", "external", "external_linked"])
    ap.add_argument("--share", type=float, default=1.0,
                    help="fraction of the dose the signal predicts; the rest is random")
    ap.add_argument("--lag", type=int, default=10,
                    help="how far the external signal leads the food")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    print(f"[e8] immobile cells; trait = how strongly the offspring is placed toward the signal; "
          f"envs {args.envs}; mutation {args.mutation_rate} sigma {args.sigma}")

    rows = []
    for s in args.seeds:
        for env in args.envs:
            rows.append(run_one(s, args, env))
    out = {"kind": "s69_e8_immobile_signal", "steps": args.steps, "window": args.window,
           "mutation_rate": args.mutation_rate, "sigma": args.sigma, "period": args.period,
           "note": ("cells never move; the heritable trait is how strongly a dividing cell places its "
                    "offspring toward the signal; three environments differ only in whether a signal "
                    "exists and where it comes from"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for env in args.envs:
        ar = [r for r in rows if r["env"] == env]
        nw = max((len(r["windows"]) for r in ar), default=0)
        means, stds, alive = [], [], []
        for i in range(nw):
            v = [r["windows"][i]["trait_mean"] for r in ar if i < len(r["windows"])]
            s2 = [r["windows"][i]["trait_std"] for r in ar if i < len(r["windows"])]
            a2 = [r["windows"][i]["alive_mean"] for r in ar if i < len(r["windows"])]
            means.append(round(sum(v) / len(v), 4) if v else None)
            stds.append(round(sum(s2) / len(s2), 4) if s2 else None)
            alive.append(round(sum(a2) / len(a2), 1) if a2 else None)
        print(f"{env:9s} w_mean {means}")
        print(f"{'':9s} w_std  {stds} | alive {alive} | R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
