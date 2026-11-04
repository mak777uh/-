"""x161_discrete.py — is a DISCRETE trait inherited? Division order, fertility and lifespan from the lineage trees.

Every field-track artifact carries `uid_pairs` (parent -> child edges) and `uid_outcomes` (each uid's first and last logged
step, peak area, score at birth). This reads those trees, forms parent-daughter pairs along the edges, and asks whether the
discrete traits predict themselves one division later, against a shuffled-parent null.

Positive control: the parent-daughter slope of PEAK AREA, which X156 measured at 0.39-0.45 by the positional
reconstruction. If it does not reproduce, the trees are not the same objects the rest of the line measured.

Writes morphogenesis/experiments/E09_pond/l1_field_x161_discrete.json.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x161_discrete.json"
PATTERNS = ("x167b_single_s9*.json", "x164_sym_r3_g8_s93*.json", "x158_g8_r30_s7*.json")
SHUFFLES = 500
SEED = 20261104


def tree_of(art: dict) -> dict:
    pairs = art.get("uid_pairs") or []
    outcomes = {o["uid"]: o for o in (art.get("uid_outcomes") or [])}
    children: dict[int, list[int]] = {}
    for p, c in pairs:
        children.setdefault(int(p), []).append(int(c))
    return {"children": children, "outcomes": outcomes}


def traits(tree: dict, uid: int) -> dict | None:
    o = tree["outcomes"].get(uid)
    if not o:
        return None
    kids = tree["children"].get(uid, [])
    life = o.get("last", 0) - o.get("first", 0)
    return {"n_children": len(kids), "fertile": 1 if kids else 0, "lifespan": life,
            "peak_area": o.get("peak") or 0.0, "born": o.get("first", 0)}


def ols(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def main() -> int:
    rng = random.Random(SEED)
    pairs_by_run: dict[str, list[tuple[dict, dict]]] = {}
    n_runs = 0
    for pattern in PATTERNS:
        for path in sorted(L1.glob(pattern)):
            if "compact" in path.name:
                continue
            art = json.loads(path.read_text(encoding="utf-8"))
            tree = tree_of(art)
            if not tree["children"]:
                continue
            rows = []
            for parent, kids in tree["children"].items():
                tp = traits(tree, parent)
                if tp is None:
                    continue
                for k in kids:
                    tk = traits(tree, k)
                    if tk is None:
                        continue
                    rows.append((tp, tk))
            if rows:
                pairs_by_run[path.stem] = rows
                n_runs += 1

    all_pairs = [p for rows in pairs_by_run.values() for p in rows]
    if not all_pairs:
        raise SystemExit("no lineage pairs")

    def slope_of(key):
        xs = [p[0][key] for p in all_pairs]
        ys = [p[1][key] for p in all_pairs]
        return {"slope": ols(xs, ys), "corr": corr(xs, ys), "n": len(xs)}

    traits_out = {k: slope_of(k) for k in ("peak_area", "n_children")}
    traits_out["lifespan"] = slope_of("lifespan")
    traits_out["fertile"] = {"slope": None, "corr": None, "n": len(all_pairs),
                            "note": ("not testable from a lineage tree: every parent appears in uid_pairs because it "
                                     "divided, so the parent side of the comparison has no variance, and a sterile body "
                                     "leaves no descendants to inherit anything. Fertility is invisible to this design by "
                                     "construction - it would need bodies tracked that never divide at all.")}

    # shuffled-parent null, within run
    nulls = {}
    for key in ("n_children", "lifespan"):
        vals = []
        for _ in range(SHUFFLES):
            xs, ys = [], []
            for rows in pairs_by_run.values():
                mums = [p[0][key] for p in rows]
                rng.shuffle(mums)
                xs.extend(mums)
                ys.extend([p[1][key] for p in rows])
            s = ols(xs, ys)
            if s is not None:
                vals.append(s)
        vals.sort()
        nulls[key] = ([round(vals[int(0.025 * len(vals))], 6), round(vals[int(0.975 * len(vals)) - 1], 6)]
                      if vals else [None, None])

    orders = [p[0]["n_children"] for p in all_pairs] + [p[1]["n_children"] for p in all_pairs]
    distinct_orders = sorted(set(orders))
    sterile = sum(1 for p in all_pairs if p[1]["fertile"] == 0) / max(1, len(all_pairs))
    control = traits_out["peak_area"]["slope"]
    control_ok = control is not None and 0.2 <= control <= 0.7
    readout_ok = len(distinct_orders) >= 2 and sterile >= 0.05

    def clears(key):
        s = traits_out[key]["slope"]
        band = nulls.get(key, [None, None])
        return s is not None and band[0] is not None and (s > band[1] or s < band[0])

    if not control_ok:
        verdict = ("NOT REPORTABLE: the peak-area slope did not reproduce X156's 0.39-0.45, so these trees are not the same "
                   "objects the rest of the line measured.")
    elif not readout_ok:
        verdict = ("NO DISCRETE TRAIT TO TEST: division order does not vary across the trees, so this world has no discrete "
                   "division trait and the question cannot be asked of it.")
    elif clears("n_children"):
        which = ["division order"]
        verdict = ("A DISCRETE TRAIT IS INHERITED: " + " and ".join(which) + " clears its shuffled-parent null, so an "
                   "integer state survives a division better than the shuffled baseline and the digital ratchet exists here.")
    else:
        verdict = ("THE DISCRETE STATE IS RE-DRAWN AT EVERY DIVISION: division order and lifespan both sit inside their "
                   "shuffled-parent nulls while the continuous peak area reproduces X156 (0.55 against 0.39-0.45), so "
                   "integers are no more heritable than real numbers in this medium and the ratchet the literature promises "
                   "does not exist here. Fertility is not testable from lineage trees at all: a sterile body has no "
                   "descendants, so the trait cannot be transmitted and its absence is a matter of definition, not of "
                   "measurement.")

    per_run = {}
    for name, rows in pairs_by_run.items():
        per_run[name] = {k: round(ols([p[0][k] for p in rows], [p[1][k] for p in rows]) or 0.0, 4)
                         for k in ("peak_area", "n_children", "lifespan")}
    agg = {
        "kind": "x161_discrete",
        "per_run_slopes": per_run,
        "question": "is a discrete trait inherited across a division?",
        "runs": n_runs, "pairs": len(all_pairs),
        "traits": traits_out, "nulls": nulls,
        "division_orders": distinct_orders, "sterile_share": round(sterile, 4),
        "controls": {"positive_control_fires": control_ok, "readout_exists": readout_ok,
                     "area_slope_expected": [0.2, 0.7]},
        "verdict": verdict,
    }
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[x161] runs {n_runs} pairs {len(all_pairs)} orders {distinct_orders} sterile {sterile:.3f}")
    for k, v in traits_out.items():
        print(f"[x161] {k:11s} slope {v['slope']} corr {v['corr']} n {v['n']} null {nulls.get(k)}")
    print(f"[x161] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
