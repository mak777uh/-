"""e6q_analyse.py — did removing the niches collapse coexistence?

Compares the homogeneous series (`e6q_*`) against the heterogeneous one already on disk (`e6p_*`, same seeds, same
parameters, only `hetero_amp` differs) and applies the preregistered criterion from
`reports/2026-11-01-e6q-no-niches-plan.md`:

    the prediction is supported if the median paired drop in structures is < 0
    with at least 8 of 10 seeds agreeing, or if the fixation share rises to >= 0.4.

Everything is paired by seed, because the two series share seeds 171-180 and differ in exactly one parameter.

Run:
    python scripts/e6q_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_e6q_niches.json"

SIGN_BAR = 8
FIXATION_BAR = 0.4


def load(prefix: str, arm: str) -> dict[int, dict]:
    out = {}
    for f in sorted(glob.glob(str(L1 / f"{prefix}_{arm}_s*.json"))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        sel = d.get("selection") or {}
        out[seed] = {
            "components": (d.get("heterogeneity") or {}).get("components_last"),
            "s_mean_last": sel.get("s_mean_last"),
            "s_sd_between": sel.get("s_sd_between_last"),
            "splits": sel.get("splits"),
            "r": sel.get("inheritability_r"),
        }
    return out


def med(values):
    v = [x for x in values if x is not None]
    return round(st.median(v), 3) if v else None


def fixation_share(rows: dict[int, dict]) -> float | None:
    if not rows:
        return None
    fixed = sum(1 for r in rows.values() if (r["components"] or 0) <= 1)
    return round(fixed / len(rows), 3)


def arm_summary(rows: dict[int, dict]) -> dict | None:
    if not rows:
        return None
    return {
        "n": len(rows),
        "components_median": med([r["components"] for r in rows.values()]),
        "s_mean_last_median": med([r["s_mean_last"] for r in rows.values()]),
        "s_sd_between_median": med([r["s_sd_between"] for r in rows.values()]),
        "splits_median": med([r["splits"] for r in rows.values()]),
        "r_median": med([r["r"] for r in rows.values()]),
        "fixation_share": fixation_share(rows),
    }


def paired(a: dict[int, dict], b: dict[int, dict], key: str) -> dict | None:
    seeds = sorted(set(a) & set(b))
    diffs = [a[s][key] - b[s][key] for s in seeds
             if a[s][key] is not None and b[s][key] is not None]
    if not diffs:
        return None
    return {"n": len(diffs), "median_diff": round(st.median(diffs), 3),
            "seeds_negative": sum(1 for d in diffs if d < 0),
            "per_seed": [round(d, 3) for d in diffs]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E6q: no niches")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    e6q_ctrl = load("e6q", "ctrl_h")
    e6q_survfd = load("e6q", "survfd_h")
    e6p_survfd = load("e6p", "survfd")
    e6p_ctrl = load("e6p", "ctrl")

    if not (e6q_ctrl or e6q_survfd):
        print("[e6q] нет прогонов")
        return 0

    comp = paired(e6q_survfd, e6p_survfd, "components")
    fix_h = fixation_share(e6q_survfd)
    fix_het = fixation_share(e6p_survfd)
    supported = bool(comp and comp["median_diff"] < 0 and comp["seeds_negative"] >= SIGN_BAR)
    if not supported and fix_h is not None and fix_het is not None and fix_h >= FIXATION_BAR and fix_h > fix_het:
        supported = True

    out = {
        "kind": "l1_field_e6q_niches",
        "experiment": "E6q",
        "command": "python scripts/e6q_analyse.py --write",
        "prereg": "reports/2026-11-01-e6q-no-niches-plan.md",
        "criterion": {"sign_bar": SIGN_BAR, "fixation_bar": FIXATION_BAR,
                      "prediction": "homogeneous survfd keeps fewer than 2.5 structures"},
        "arms": {
            "homog_ctrl": arm_summary(e6q_ctrl),
            "homog_survfd": arm_summary(e6q_survfd),
            "hetero_ctrl_e6p": arm_summary(e6p_ctrl),
            "hetero_survfd_e6p": arm_summary(e6p_survfd),
        },
        "paired_components_homog_minus_hetero": comp,
        "drift_homog": paired(e6q_survfd, e6q_ctrl, "s_mean_last"),
        "prediction_supported": supported,
        "not_claimed": [
            "no p-values: ten paired seeds and a pre-declared sign rule",
            "components is the count at the last snapshot, not a time average",
            "the two series differ only in hetero_amp, but they were run at different times on the same machine",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[e6q] written: {OUT.name}")
    for name, a in out["arms"].items():
        if a:
            print("  %-16s n=%2d structures=%s s_end=%s fixation=%s" % (
                name, a["n"], a["components_median"], a["s_mean_last_median"], a["fixation_share"]))
    if comp:
        print("  paired structures homog-hetero: %+0.2f (%d/%d seeds lower)" % (
            comp["median_diff"], comp["seeds_negative"], comp["n"]))
    print("  prediction supported:", supported)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
