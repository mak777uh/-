"""S6/C3: double flip (A -> B -> A) — does the SECOND recovery cost less than the first?

Owner's hypothesis ("adaptive ones appear later") tested without waiting longer in one
environment: if adaptation is heritable/learned, the population should recover FASTER (or
stay higher) after the second flip than after the first.

Engine note: `PondConfig.flip_at` is a ONE-SHOT flip (`step >= flip_at` -> inverted
gradient). A second flip is expressed by the additive config field `flip2_at`
(`step >= flip2_at` -> back to the original orientation, A -> B -> A), added to
`PondConfig`/`_gradient_position` with default 0 so old worlds stay bit-for-bit.

NOTE (06.11, design check): the first version of this script tried to realise the
second flip by mirroring the world state from outside the engine. That was WRONG:
`_gradient_position()` is a function of the step counter, not of the state, so
mirroring the state did not flip the environment — both arms stayed in the same
(B) environment and the "double" arm was not a different treatment at all.
The mirror helper is kept only for diagnostics; the arms now differ by `flip2_at`.

Arms (same seeds, same non-degenerate regime):
  - control: single flip at T1 (what P0/P1 already measured), run to the end;
  - double:  flip at T1, then flip back at T2 (mirror), run to the end.
Readout: correct_share (current favorable half) in windows after each flip; the
difference between the second and the first recovery is the effect of interest.
R1 guard: died >= 10 and alive >= 10 per run.
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


def mirror_world(run) -> None:
    """Mirror the world vertically: state field i <-> n-1-i (equivalent to flipping the env)."""
    s = run.pond.state
    n = run.pond.cfg.grid
    idx = torch.arange(n - 1, -1, -1, device=run.pond.device)
    for name in ("alive", "energy", "age", "pred", "res_prev", "heading", "tag", "tag_trait",
                 "resource", "resource_b", "cell_type", "membrane", "founder"):
        t = getattr(s, name, None)
        if t is not None and t.dim() >= 2:
            setattr(s, name, t[idx, :].clone())
    # heading sign flips with the mirror (up <-> down)
    if getattr(s, "heading", None) is not None:
        s.heading = -s.heading
    # keep the rule's input channel in sync with the mirrored alive mask
    try:
        run._apply_alive(s.alive.bool())
    except Exception:
        pass


def run_one(seed, args, double: bool):
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        flip2_at=(args.flip2_at if double else 0),
        plastic_eta=args.plastic_eta, plastic_move_cost=args.plastic_move_cost,
        plastic_gate=args.plastic_gate, plastic_nomove=args.plastic_nomove,
        plastic_prob=0.5, plastic_direction=args.plastic_direction,
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    windows = []          # list of dicts per window
    acc = None
    for _ in range(args.steps):
        run.step()
        pond = run.pond
        st = int(pond.state.step)
        a = pond.state.alive
        corr = correct_mask(pond)
        n_alive = int(a.sum())
        c_alive = int((a & corr).sum())
        if acc is None:
            acc = {"start": st, "n": 0, "alive": 0, "correct": 0}
        acc["n"] += 1; acc["alive"] += n_alive; acc["correct"] += c_alive
        if acc["n"] >= args.window:
            windows.append({"start": acc["start"], "end": st,
                            "correct_share": (acc["correct"] / acc["alive"]) if acc["alive"] else None,
                            "alive_mean": round(acc["alive"] / acc["n"], 2)})
            acc = None
    if acc and acc["n"]:
        windows.append({"start": acc["start"], "end": int(run.pond.state.step),
                        "correct_share": (acc["correct"] / acc["alive"]) if acc["alive"] else None,
                        "alive_mean": round(acc["alive"] / acc["n"], 2)})
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "arm": "double" if double else "control",
            "windows": windows,
            "final": {"alive": alive, "born": final.get("born"), "died": died},
            "R1": bool(died >= 10 and alive >= 10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--flip-at", type=int, default=200)
    ap.add_argument("--flip2-at", type=int, default=500)
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
    ap.add_argument("--plastic-eta", type=float, default=0.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--plastic-gate", default="pred")
    ap.add_argument("--plastic-direction", default="gradient")
    ap.add_argument("--plastic-nomove", action="store_true")
    ap.add_argument("--mutation-rate", type=float, default=0.0)
    ap.add_argument("--mutation-trait-sigma", type=float, default=0.05)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    rows = []
    for s in args.seeds:
        rows.append(run_one(s, args, double=False))
        rows.append(run_one(s, args, double=True))
    out = {"kind": "s6_double_flip", "flip_at": args.flip_at, "flip2_at": args.flip2_at,
           "steps": args.steps, "window": args.window, "plastic_eta": args.plastic_eta,
           "plastic_direction": args.plastic_direction, "mutation_rate": args.mutation_rate,
           "n_seeds": len(args.seeds), "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    # compact print: per arm, per window mean correct_share
    for arm in ("control", "double"):
        ar = [r for r in rows if r["arm"] == arm]
        nw = max((len(r["windows"]) for r in ar), default=0)
        means = []
        for i in range(nw):
            vals = [r["windows"][i]["correct_share"] for r in ar
                    if i < len(r["windows"]) and r["windows"][i]["correct_share"] is not None]
            means.append(round(sum(vals) / len(vals), 3) if vals else None)
        print(arm, "windows:", means, "| R1:", [r["R1"] for r in ar],
              "| alive:", [r["final"]["alive"] for r in ar])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
