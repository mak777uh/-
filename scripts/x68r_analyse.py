"""x68r_analyse.py — X68 lifetimes on five genuinely different neutral worlds per identity rule.

X68 measured the lifetime contrast in a `beta = 0` world, where the seed does not move the geometry: its five "seeds" were
one world copied five times, so "0/5 seeds" meant one world. `x68r_series.py` repeats the same measurement with
`--init-jitter`; this script reads the result.

Per rule (`--overlap` 0.3 / 0.5 / 0.7) and arm (heterogeneous amp 0.5, homogeneous amp 0.0) it reports, for each world, the
number of uids and the median lifetime, then counts in how many worlds the heterogeneous median is below the homogeneous
one — the direction the published (feedback-regime) number claims.

Run:
    python scripts/x68r_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x68r_identity.json"

RULES = ("ov03", "ov05", "ov07")
ARMS = ("pattern", "homog")


def read_worlds(rule: str, arm: str) -> dict[int, dict]:
    out = {}
    for f in sorted(L1.glob(f"x68r_{rule}_{arm}_s*.json")):
        seed = int(Path(f).stem.split("_s")[-1])
        d = json.loads(f.read_text(encoding="utf-8"))
        lt = d.get("lifetimes") or {}
        out[seed] = {"n_uids": lt.get("n_uids"), "median_life": lt.get("median_life_steps"),
                     "components": [s.get("components") for s in (d.get("series") or [])]}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X68 on real neutral worlds")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x68r_identity", "experiment": "X68 replicated",
           "command": "python scripts/x68r_analyse.py --write",
           "why": "in a beta=0 world the seed does not move the geometry, so the X68 arms were one world per rule; "
                  "--init-jitter makes five real worlds, and only then is a per-world contrast a replication",
           "prereg": "reports/2026-11-01-x68-identity-rule-plan.md (design unchanged; replication route repaired)",
           "rules": {}}

    for rule in RULES:
        het = read_worlds(rule, "pattern")
        hom = read_worlds(rule, "homog")
        seeds = sorted(set(het) & set(hom))
        rows = []
        for s in seeds:
            a = het[s]["median_life"]
            b = hom[s]["median_life"]
            rows.append({"seed": s,
                         "hetero_n_uids": het[s]["n_uids"], "homog_n_uids": hom[s]["n_uids"],
                         "hetero_median_life": a, "homog_median_life": b,
                         "hetero_below": (a is not None and b is not None and a < b),
                         "difference": (a - b) if (a is not None and b is not None) else None})
        pairs = [(r["hetero_median_life"], r["homog_median_life"]) for r in rows
                 if r["hetero_median_life"] is not None and r["homog_median_life"] is not None]
        below = sum(1 for a, b in pairs if a < b)
        above = sum(1 for a, b in pairs if a > b)
        # five-world null: if the direction were coin-like, all five pointing one way has p = 2/32 = 0.0625
        res["rules"][rule] = {
            "worlds": len(pairs),
            "hetero_below": below,
            "hetero_above": above,
            "direction": ("hetero shorter" if below > above else ("hetero longer" if above > below else "mixed")),
            "unanimous": (below == len(pairs) and len(pairs) > 0) or (above == len(pairs) and len(pairs) > 0),
            "rows": rows,
            "hetero_median_of_medians": st.median([a for a, _ in pairs]) if pairs else None,
            "homog_median_of_medians": st.median([b for _, b in pairs]) if pairs else None,
        }

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x68r] written: {OUT.name}")

    for rule, r in res["rules"].items():
        print("  %-5s worlds=%d  hetero shorter %d/%d  hetero longer %d/%d  -> %s%s" % (
            rule, r["worlds"], r["hetero_below"], r["worlds"], r["hetero_above"], r["worlds"], r["direction"],
            " (unanimous)" if r["unanimous"] else ""))
        for row in r["rows"]:
            print("      seed %d: hetero %s (uid %s)  homog %s (uid %s)" % (
                row["seed"], row["hetero_median_life"], row["hetero_n_uids"],
                row["homog_median_life"], row["homog_n_uids"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
