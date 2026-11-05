"""P1c: do post-flip-born cohorts show increasing occupancy of the new correct half over time?
Same non-degenerate setup as P0/P1. Windowed correct_share overall and for cells born after flip (age < step-flip_at).
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


def run_one(seed, args):
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        plastic_eta=args.plastic_eta, plastic_move_cost=args.plastic_move_cost,
        plastic_gate=args.plastic_gate, plastic_nomove=False, plastic_prob=0.5,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    win = args.window
    windows = []  # (start,end,overall_correct_share,postflip_born_correct_share,postflip_n,overall_n)
    acc = None
    for step_i in range(1, args.steps + 1):
        run.step()
        pond = run.pond
        a = pond.state.alive
        corr = correct_mask(pond)
        born_after = pond.state.age < (pond.state.step - args.flip_at)  # alive now, born after flip
        overall_n = int(a.sum()); post_n = int((a & born_after).sum())
        o_c = int((a & corr).sum()); p_c = int((a & born_after & corr).sum())
        if pond.state.step >= args.flip_at:
            if acc is None:
                acc = {"start": pond.state.step, "o_c": 0, "o_n": 0, "p_c": 0, "p_n": 0, "n": 0}
            acc["o_c"] += o_c; acc["o_n"] += overall_n; acc["p_c"] += p_c; acc["p_n"] += post_n; acc["n"] += 1
            if acc["n"] >= win:
                windows.append({
                    "start": acc["start"], "end": pond.state.step,
                    "overall_correct_share": (acc["o_c"]/acc["o_n"]) if acc["o_n"] else None,
                    "postflip_born_correct_share": (acc["p_c"]/acc["p_n"]) if acc["p_n"] else None,
                    "postflip_cellsteps": acc["p_n"], "overall_cellsteps": acc["o_n"],
                })
                acc = None
    if acc and acc["n"] > 0:
        windows.append({
            "start": acc["start"], "end": args.steps,
            "overall_correct_share": (acc["o_c"]/acc["o_n"]) if acc["o_n"] else None,
            "postflip_born_correct_share": (acc["p_c"]/acc["p_n"]) if acc["p_n"] else None,
            "postflip_cellsteps": acc["p_n"], "overall_cellsteps": acc["o_n"],
        })
    final = run.log[-1] if run.log else {}
    return {"seed": seed, "plastic_eta": args.plastic_eta, "windows_post_flip": windows,
            "final": {"alive": final.get("alive_cells"), "born": final.get("born"), "died": final.get("died")},
            "R1": (final.get("died",0)>=10 and final.get("alive_cells",0)>=10)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1,2,3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--flip-at", type=int, default=200)
    ap.add_argument("--window", type=int, default=50)
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
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rows = [run_one(s, args) for s in args.seeds]
    # aggregate by window index
    nwin = max((len(r["windows_post_flip"]) for r in rows), default=0)
    agg_win = []
    for i in range(nwin):
        vals_o=[]; vals_p=[]; label=None
        for r in rows:
            if i < len(r["windows_post_flip"]):
                w=r["windows_post_flip"][i]; label=(w["start"],w["end"])
                if w["overall_correct_share"] is not None: vals_o.append(w["overall_correct_share"])
                if w["postflip_born_correct_share"] is not None: vals_p.append(w["postflip_born_correct_share"])
        agg_win.append({"window": label, "overall_mean": (sum(vals_o)/len(vals_o) if vals_o else None),
                        "postflip_born_mean": (sum(vals_p)/len(vals_p) if vals_p else None)})
    out = {"kind":"p1c_lineage_adaptation_windows","plastic_eta":args.plastic_eta,"steps":args.steps,"flip_at":args.flip_at,
           "window":args.window,"n_seeds":len(rows),"agg_windows":agg_win,"rows":rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as fh: json.dump(out,fh,ensure_ascii=False,indent=1)
    print(json.dumps({"agg_windows": agg_win}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
