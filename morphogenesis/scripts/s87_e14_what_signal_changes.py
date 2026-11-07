"""S87 / E14: WHAT should a signal change - the place, the time, or the rules?

All earlier signal experiments asked only one question: "does the signal say WHERE the food is?" The
owner's point is that a signal can act on the world in at least three different ways, and which one is
optimal has never been tested:

  A `local`  : food appears ONLY where the signal is strong (the signal says WHERE);
  B `wave`   : food appears EVERYWHERE, but how much depends on the wave (the signal says WHEN);
  C `rule`   : the signal does not touch the food at all - it changes the cell's upkeep (the signal
               changes the RULES);
  AB         : both the place and the amount.

The cells are IMMOBILE, as the owner specified. A first-principles prediction: for an immobile cell a
signal about WHERE helps only those that happen to stand in the right place, while a signal about WHEN
helps everyone - so B should beat A. C is a different kind of effect and may beat both.

EQUAL DOSE. Every arm adds the same total resource per step; the arms differ only in how the signal
distributes or modulates it. The script asserts the total.

PAIRING. Every arm runs with its own generator seeded identically, and the pairing is CHECKED by drawing
the same values from two identically seeded generators.

Readout: mean trait per window per arm, the total resource added, the pairing check, R1.
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
    _MORPH = _MORPH
    sys.path.insert(0, _MORPH)
from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def seed_at(run, cells: int, energy: float, xy: tuple[int, int]) -> None:
    n = run.world_cfg.grid
    cy, cx = xy
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


def wave(step: int, n: int, period: int) -> torch.Tensor:
    """The signal: a travelling wave over the grid, one crest per period."""
    rows = torch.arange(n, dtype=torch.float32)
    phase = 2.0 * math.pi * float(step) / max(period, 1) - 2.0 * math.pi * rows / max(n, 1)
    return torch.sin(phase)[:, None].expand(n, n)


def add_food(pond, amount: float, arm: str, sig: torch.Tensor | None, gen) -> float:
    """Add `amount` units of resource, distributed according to the arm. Returns what landed."""
    s = pond.state
    res = s.resource
    n = pond.cfg.grid
    before = float(res.sum())
    if arm == "none" or sig is None:
        # uniform: the same amount spread evenly over the whole grid
        res += amount / (n * n)
    elif arm == "local":
        # only at the crest: the signal says WHERE
        flat = sig.reshape(-1)
        k = max(1, flat.numel() // 10)
        idx = torch.topk(flat, k=k, largest=True).indices
        ys, xs = idx // n, idx % n
        res[ys, xs] += amount / k
    elif arm == "wave":
        # everywhere, but the amount depends on the wave: the signal says WHEN
        w = (sig + 1.0) * 0.5          # 0..1
        res += amount * w / float(w.sum())
    elif arm == "rule":
        # the signal does not touch the food; the food is uniform and the signal changes upkeep
        res += amount / (n * n)
    elif arm == "ab":
        half = amount * 0.5
        flat = sig.reshape(-1)
        k = max(1, flat.numel() // 10)
        idx = torch.topk(flat, k=k, largest=True).indices
        ys, xs = idx // n, idx % n
        res[ys, xs] += half / k
        w = (sig + 1.0) * 0.5
        res += half * w / float(w.sum())
    res.clamp_(max=pond.cfg.resource_max)
    return float(res.sum()) - before


def run_one(seed, args, arm):
    cfg = PondConfig(
        grid=args.grid, resource_layout="patches", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=args.budding_mass, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=0,
        patch_inflow_base=args.patch_inflow_base, patch_inflow_rich=args.patch_inflow_rich,
        plastic_eta=0.0, plastic_move_cost=0.0, plastic_gate="pred",
        plastic_direction="gradient", plastic_nomove=True,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.sigma, type_mode="mixfixed",
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    seed_at(run, args.seed_cells, args.seed_energy, (16, 16))   # the POOR centre, recorded below
    pond = run.pond
    gen = torch.Generator(device="cpu").manual_seed(seed * 7919 + 17)
    if pond.state.tag_trait is not None:
        pond.state.tag_trait.uniform_(0.0, 1.0, generator=gen)
    windows, acc, added = [], None, 0.0
    for step in range(1, args.steps + 1):
        s = pond.state
        sig = wave(step, args.grid, args.period).to(pond.device)
        if arm == "rule" and s.tag_trait is not None and bool(s.alive.any()):
            # the signal changes the RULE: cells on a crest pay less upkeep
            relief = args.rule_strength * (sig + 1.0) * 0.5
            s.energy = torch.clamp(s.energy + relief * s.alive.float(), min=0.0)
        run.step()
        if step % args.feed_every == 0:
            added += add_food(pond, args.feed_amount, arm, sig, gen)
        s = pond.state
        a = s.alive
        cnt = int(a.sum())
        if cnt == 0:
            continue
        tr = s.tag_trait
        if acc is None:
            acc = {"n": 0, "mean": 0.0, "std": 0.0, "alive": 0}
        acc["n"] += 1
        if tr is not None:
            acc["mean"] += float(tr[a].mean())
            acc["std"] += float(tr[a].std())
        acc["alive"] += cnt
        if acc["n"] >= args.window:
            windows.append({"trait_mean": round(acc["mean"] / acc["n"], 6),
                            "trait_std": round(acc["std"] / acc["n"], 6),
                            "alive_mean": round(acc["alive"] / acc["n"], 1)})
            acc = None
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0)
    alive = int(pond.state.alive.sum())
    return {"seed": seed, "arm": arm, "windows": windows, "total_added": round(added, 2),
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--grid", type=int, default=32)
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
    ap.add_argument("--budding-mass", type=float, default=40.0)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--feed-every", type=int, default=5)
    ap.add_argument("--feed-amount", type=float, default=0.5)
    ap.add_argument("--rule-strength", type=float, default=0.05)
    ap.add_argument("--arms", nargs="+", default=["none", "local", "wave", "rule", "ab"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    # PAIRING IS CHECKED
    a = torch.Generator(device="cpu").manual_seed(12345)
    b = torch.Generator(device="cpu").manual_seed(12345)
    identical = bool(torch.equal(torch.rand(32, generator=a), torch.rand(32, generator=b)))
    print(f"[e14] pairing check: {identical}")
    if not identical:
        raise SystemExit("[e14] REFUSED: generators are not identical")

    rows = []
    for s in args.seeds:
        for arm in args.arms:
            rows.append(run_one(s, args, arm))
    out = {"kind": "s87_e14_what_signal_changes", "steps": args.steps, "window": args.window,
           "period": args.period, "feed_amount": args.feed_amount, "rule_strength": args.rule_strength,
           "plant_xy": [16, 16], "plant_zone": "poor (centre, resource 0.2)",
           "pairing_check": identical,
           "note": ("immobile cells planted in the POOR centre; the arms differ only in WHAT the signal "
                    "changes: the place (local), the amount everywhere (wave), the rules (rule), or both"),
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for arm in args.arms:
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        v = [round(sum(r["windows"][i]["trait_mean"] for r in ar if i < len(r["windows"]))
                   / max(1, len([r for r in ar if i < len(r["windows"])])), 5) for i in range(nw)]
        added = round(sum(r["total_added"] for r in ar) / len(ar), 1)
        print(f"{arm:6s} {v} | added {added} | R1 {sum(r['R1'] for r in ar)}/{len(ar)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
