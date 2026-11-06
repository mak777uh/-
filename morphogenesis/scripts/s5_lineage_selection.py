"""S5/C: heritable variation + lineage selection after environment flip.

Question (owner's hypothesis): do *lineages born after the flip* become enriched in the
new favorable zone over time (adaptive lineages appear later), above demographic noise?

Design:
- Existing engine machinery: tag (lineage label), tag_trait (heritable, mutated with
  mutation_rate/mutation_trait_sigma), tag_born_at, lineage_offspring, tag_trait_of.
- Null arm: trait_effect=0 (tags are neutral markers) -> any post-flip lineage enrichment
  is demographic noise (this is the null model).
- Selection arm: trait_effect>0 (trait modulates investment factor; see pond.py:941-951).
- Per window after flip we log: n_lineages_alive, top lineage share, I=Var(w)/mean(w)^2
  (opportunity for selection, Waples), mean correct_share of cells of post-flip-born
  lineages vs pre-flip lineages, alive/died (R1).
- correct zone = current gradient half (flips), same as P0 metric.
"""
from __future__ import annotations
import argparse, json, math, os, sys
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


def window_stats(pond, flip_at):
    s = pond.state
    a = s.alive
    corr = correct_mask(pond)
    tag = s.tag
    n_alive = int(a.sum())
    if n_alive == 0 or tag is None:
        return None
    # per-lineage alive counts and correct share
    alive_tags = tag[a]
    uniq, counts = torch.unique(alive_tags, return_counts=True)
    w = counts.float()
    mean_w = float(w.mean())
    I = float(w.var(unbiased=False) / (mean_w ** 2)) if mean_w > 0 else 0.0
    top_share = float(w.max() / w.sum())
    # correct share by lineage birth cohort (born before vs after flip)
    born_at = torch.tensor([pond.tag_born_at.get(int(t), 0) for t in uniq.tolist()],
                           device=counts.device, dtype=torch.long)
    post_mask = born_at >= flip_at
    pre_mask = ~post_mask
    corr_share_post = None
    corr_share_pre = None
    # cell-level correct share within each cohort
    post_tags = set(uniq[post_mask].tolist())
    pre_tags = set(uniq[pre_mask].tolist())
    if post_tags:
        m = a & torch.isin(tag, torch.tensor(list(post_tags), device=tag.device))
        corr_share_post = float((m & corr).sum() / m.sum()) if int(m.sum()) else None
    if pre_tags:
        m = a & torch.isin(tag, torch.tensor(list(pre_tags), device=tag.device))
        corr_share_pre = float((m & corr).sum() / m.sum()) if int(m.sum()) else None
    return {
        "step": int(s.step),
        "alive": n_alive,
        "n_lineages_alive": int(uniq.numel()),
        "top_lineage_share": round(top_share, 4),
        "I_opportunity": round(I, 4),
        "mean_lineage_size": round(mean_w, 2),
        "postflip_lineage_correct_share": corr_share_post,
        "preflip_lineage_correct_share": corr_share_pre,
        "postflip_alive": int(a[torch.isin(tag, torch.tensor(list(post_tags), device=tag.device))].sum()) if post_tags else 0,
        "preflip_alive": n_alive - (int(a[torch.isin(tag, torch.tensor(list(post_tags), device=tag.device))].sum()) if post_tags else 0),
    }


def run_one(seed, args):
    cfg = PondConfig(
        grid=args.grid, resource_layout="gradient", income_mode=args.income_mode,
        init_resource_fill=args.init_resource_fill, baseline_income=args.income,
        update_cost=args.update_cost, repair_cost=args.repair_cost,
        budding_mass=24, budding_cost=0.2, resource_max=1.0,
        resource_regen=args.resource_regen, flip_at=args.flip_at,
        plastic_eta=args.plastic_eta, plastic_move_cost=args.plastic_move_cost,
        plastic_gate=args.plastic_gate, plastic_nomove=True, plastic_prob=0.5,
        plastic_direction="gradient",
        mutation_rate=args.mutation_rate, mutation_trait_sigma=args.mutation_trait_sigma,
        trait_effect=args.trait_effect, trait_effect_mode=args.trait_effect_mode,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=args.device, rule_checkpoint=args.checkpoint)
    run.seed(cells=args.seed_cells, energy=args.seed_energy)
    windows = []
    acc = None
    for _ in range(args.steps):
        run.step()
        pond = run.pond
        if pond.state.step >= args.flip_at:
            st = window_stats(pond, args.flip_at)
            if st is None:
                continue
            if acc is None:
                acc = {k: 0.0 for k in st if k != "step"}
                acc["n"] = 0
                acc["start"] = st["step"]
            for k in acc:
                if k in ("n", "start"):
                    continue
                v = st.get(k)
                if v is not None:
                    acc[k] += v
            acc["n"] += 1
            if acc["n"] >= args.window:
                w = {"start": acc["start"], "end": st["step"], "n": acc["n"]}
                for k in acc:
                    if k in ("n", "start"):
                        continue
                    w[k] = round(acc[k] / acc["n"], 4) if acc[k] != 0 or k in ("I_opportunity",) else (acc[k] / acc["n"] if acc["n"] else None)
                windows.append(w)
                acc = None
    if acc and acc["n"] > 0:
        w = {"start": acc["start"], "end": int(run.pond.state.step), "n": acc["n"]}
        for k in acc:
            if k in ("n", "start"):
                continue
            w[k] = acc[k] / acc["n"] if acc["n"] else None
        windows.append(w)
    final = run.log[-1] if run.log else {}
    died = final.get("died", 0); alive = final.get("alive_cells", 0)
    return {"seed": seed, "windows_post_flip": windows,
            "mutation_events": int(getattr(run.pond, "mutation_events", 0)),
            "n_lineages_total": int(run.pond.next_tag),
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
    ap.add_argument("--plastic-eta", type=float, default=0.0)
    ap.add_argument("--plastic-move-cost", type=float, default=0.03)
    ap.add_argument("--plastic-gate", default="pred")
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--mutation-trait-sigma", type=float, default=0.05)
    ap.add_argument("--trait-effect", type=float, default=0.0)
    ap.add_argument("--trait-effect-mode", default="invest", choices=["invest", "update"])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--checkpoint", default=os.path.join(_MORPH, "checkpoints", "world_base_rule.pt"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rows = [run_one(s, args) for s in args.seeds]
    nwin = max((len(r["windows_post_flip"]) for r in rows), default=0)
    agg = []
    for i in range(nwin):
        rec = {"window_idx": i}
        for key in ("alive", "n_lineages_alive", "top_lineage_share", "I_opportunity",
                    "postflip_lineage_correct_share", "preflip_lineage_correct_share",
                    "postflip_alive", "preflip_alive"):
            vals = [r["windows_post_flip"][i][key] for r in rows
                    if i < len(r["windows_post_flip"]) and r["windows_post_flip"][i].get(key) is not None]
            rec[key] = round(sum(vals) / len(vals), 4) if vals else None
        agg.append(rec)
    out = {"kind": "s5_lineage_selection_windows", "flip_at": args.flip_at, "steps": args.steps,
           "window": args.window, "mutation_rate": args.mutation_rate,
           "mutation_trait_sigma": args.mutation_trait_sigma,
           "trait_effect": args.trait_effect, "trait_effect_mode": args.trait_effect_mode,
           "n_seeds": len(rows), "agg_windows": agg, "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"agg_windows": agg}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
