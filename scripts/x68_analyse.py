"""x68_analyse.py — does the lifetime contrast survive a different identity rule?

Applies the preregistered criterion of `reports/2026-11-01-x68-identity-rule-plan.md`: at each overlap rule (0.3, 0.5, 0.7)
the heterogeneous median lifetime must sit below the homogeneous one in at least 4 of 5 seeds, paired. The 0.5 arm is the
published one and comes from the X60 files already on disk.

Run:
    python scripts/x68_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x68_identity.json"

# amendment: все три правила в нейтральном мире (beta=0), иначе сравнение смешивает режимы
RULES = {"0.3": "x68_ov03", "0.5": "x68_ov05", "0.7": "x68_ov07"}
ARMS = ("pattern", "homog")
SIGN_BAR = 4


def load(prefix: str, arm: str) -> dict[int, dict]:
    out = {}
    for f in sorted(glob.glob(str(L1 / f"{prefix}_{arm}_s*.json"))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        lt = d.get("lifetimes") or {}
        out[seed] = {"median_life": lt.get("median_life_steps"), "n_uids": lt.get("n_uids"),
                     "components": [s.get("components") for s in d.get("series") or []]}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X68 identity-rule sensitivity")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    table = {}
    for rule, prefix in RULES.items():
        p = load(prefix, "pattern")
        h = load(prefix, "homog")
        if not p or not h:
            continue
        seeds = sorted(set(p) & set(h))
        below = 0
        rows = []
        for s in seeds:
            mp, mh = p[s]["median_life"], h[s]["median_life"]
            if mp is None or mh is None:
                continue
            below += 1 if mp < mh else 0
            rows.append({"seed": s, "pattern_median": mp, "homog_median": mh,
                         "pattern_uids": p[s]["n_uids"], "homog_uids": h[s]["n_uids"]})
        if rows:
            table[rule] = {
                "n": len(rows),
                "pattern_median": st.median([r["pattern_median"] for r in rows]),
                "homog_median": st.median([r["homog_median"] for r in rows]),
                "seeds_hetero_below": below,
                "ordering_holds": below >= SIGN_BAR,
                "rows": rows,
            }

    # leak check: components must be identical across rules within an arm and seed
    leaks = []
    for arm in ARMS:
        base = load(RULES["0.5"], arm)
        for rule in ("0.3", "0.7"):
            other = load(RULES[rule], arm)
            for s in sorted(set(base) & set(other)):
                if base[s]["components"] != other[s]["components"]:
                    leaks.append({"arm": arm, "seed": s, "rule": rule})

    out = {
        "kind": "l1_field_x68_identity",
        "experiment": "X68",
        "command": "python scripts/x68_analyse.py --write",
        "prereg": "reports/2026-11-01-x68-identity-rule-plan.md",
        "criterion": {"sign_bar": SIGN_BAR, "claim": "heterogeneous median lifetime below homogeneous at each rule"},
        "by_rule": table,
        "leaks": leaks,
        "verdict": ("holds at all rules" if table and all(v["ordering_holds"] for v in table.values())
                    else "fails at least one rule" if table else "no data"),
        "not_claimed": [
            "five seeds per cell; the argument is the per-seed ordering, not a test",
            "0.5 comes from the X60 files, the other two from X68; same parameters and seeds",
            "the rule changes only the observer, which the leak check verifies",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x68] written: {OUT.name}")
    for rule, v in table.items():
        print("  overlap %s  n=%d  pattern=%6s  homog=%7s  hetero below: %d/%d  holds: %s" % (
            rule, v["n"], v["pattern_median"], v["homog_median"], v["seeds_hetero_below"], v["n"], v["ordering_holds"]))
    print("  leaks:", len(leaks), "| verdict:", out["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
