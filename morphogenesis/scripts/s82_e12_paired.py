"""S82 / E12: PAIRED design - the same random numbers for every environment.

All four retractions today (E7d, E8d, E8g, E10) had one technical cause: the runs were not paired by
randomness. When an experiment has four environments and a follow-up has two, the RNG stream differs and
the apparent difference between environments can be an artefact of the CALL ORDER rather than a property
of the signal.

This script fixes that at the root: for each seed, every environment is run with its OWN generator
initialised from the SAME seed, and the comparison is made SEED BY SEED (paired), so the same random
numbers are used for the same decision in every environment.

Design:
  - environments: `none` (no signal), `external_linked` (signal predicts the food with a lead),
    `external` (unrelated noise), `cpu` (signal coincides with the food);
  - every environment gets `torch.Generator(seed=seed * 7919 + 17)` - identical streams;
  - the readout is the PAIRED difference (env - none) per seed, and the number of seeds where the
    difference is positive.

If the paired difference is systematically positive for `external_linked` and near zero for `external`,
the predictive-signal claim survives the pairing test. If the paired differences scatter around zero for
every environment, the claim is dead and the honest conclusion is that a signal does not pay in this
geometry.
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
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "e8mod", os.path.join(_MORPH, "scripts", "s69_e8_immobile_signal.py"))
e8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e8)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
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
    ap.add_argument("--budding-mass", type=float, default=40.0)
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--lag", type=int, default=2)
    ap.add_argument("--share", type=float, default=1.0)
    ap.add_argument("--reach", type=int, default=3)
    ap.add_argument("--feed-every", type=int, default=5)
    ap.add_argument("--feed-amount", type=float, default=0.2)
    ap.add_argument("--envs", nargs="+",
                    default=["none", "external_linked", "external", "cpu"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    # run every environment for every seed with the SAME generator seed
    per_seed = {}
    for s in args.seeds:
        per_seed[s] = {}
        for env in args.envs:
            r = e8.run_one(s, args, env)
            last = r["windows"][-1]["trait_mean"] if r["windows"] else None
            per_seed[s][env] = {"last": last, "R1": r["R1"], "alive": r["final"]["alive"]}
        print(f"[e12] seed {s}: " + " | ".join(
            f"{e}={per_seed[s][e]['last']}" for e in args.envs))

    # PAIRED differences against `none`
    base = "none"
    paired = {}
    for env in args.envs:
        if env == base:
            continue
        diffs = []
        for s in args.seeds:
            a, b = per_seed[s][env]["last"], per_seed[s][base]["last"]
            if a is not None and b is not None:
                diffs.append(a - b)
        if diffs:
            pos = sum(1 for d in diffs if d > 0)
            paired[env] = {"n": len(diffs), "mean_diff": round(sum(diffs) / len(diffs), 4),
                           "positive": pos, "diffs": [round(d, 4) for d in diffs]}
            print(f"[e12] {env:16s} paired diff {paired[env]['mean_diff']:+.4f} "
                  f"({pos}/{len(diffs)} seeds positive)")

    out = {"kind": "s82_e12_paired", "steps": args.steps, "lag": args.lag,
           "feed_amount": args.feed_amount, "budding_mass": args.budding_mass,
           "note": ("PAIRED design: every environment runs with its own generator seeded identically, "
                    "so the same random numbers drive the same decisions in every arm"),
           "per_seed": {str(k): v for k, v in per_seed.items()},
           "paired": paired}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\n[e12] written {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
