"""e6p_analyse.py — three selection regimes: does the survival channel drift, and does frequency dependence hold diversity?

Reads `morphogenesis/experiments/L1_field/e6p_<arm>_s<seed>.json` (arms: `ctrl`, `surv`, `survfd`) and writes
`morphogenesis/experiments/E09_pond/l1_field_e6p_selection.json`.

The criterion is the preregistered one (`reports/2026-11-01-e6p-selection-regimes-plan.md`): a **paired-by-seed drift** of
`s_mean_last` against the control, claimed only if the median drift exceeds **+0.20** and **at least 8 of 10** seeds agree
in sign. No p-values: on ten autocorrelated trajectories a t-test would overstate precision.

What it reports, and why each is needed:

- `s_mean_last` — the trait itself. Drift up means the composition moved towards decay protection.
- `components` — fixation is the failure mode: the earlier runs ended with one structure and the trait could no longer
  vary. Median structures per arm is the direct readout of that.
- `s_sd_between_last` — the fuel for selection. If it collapses, drift is meaningless even when large.
- `splits`, `parent_child_pairs`, `inheritability_r` — whether transmission events happened at all.

Run:
    python scripts/e6p_analyse.py --write
    python scripts/e6p_analyse.py
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_e6p_selection.json"

ARMS = ("ctrl", "surv", "survfd")
DRIFT_BAR = 0.20
SIGN_BAR = 8


def load() -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {a: {} for a in ARMS}
    for arm in ARMS:
        for f in sorted(glob.glob(str(L1 / f"e6p_{arm}_s*.json"))):
            seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            sel = d.get("selection") or {}
            out[arm][seed] = {
                "s_mean_last": sel.get("s_mean_last"),
                "s_sd_between": sel.get("s_sd_between_last"),
                "splits": sel.get("splits"),
                "pairs": sel.get("parent_child_pairs"),
                "r": sel.get("inheritability_r"),
                "components": (d.get("heterogeneity") or {}).get("components_last"),
            }
    return out


def med(values) -> float | None:
    v = [x for x in values if x is not None]
    return round(st.median(v), 3) if v else None


def summarise(data: dict[str, dict[int, dict]]) -> dict:
    arms = {}
    for arm in ARMS:
        rows = data[arm]
        if not rows:
            continue
        arms[arm] = {
            "n": len(rows),
            "s_mean_last_median": med([r["s_mean_last"] for r in rows.values()]),
            "s_sd_between_median": med([r["s_sd_between"] for r in rows.values()]),
            "splits_median": med([r["splits"] for r in rows.values()]),
            "pairs_median": med([r["pairs"] for r in rows.values()]),
            "r_median": med([r["r"] for r in rows.values()]),
            "components_median": med([r["components"] for r in rows.values()]),
            "fixation_share": (round(sum(1 for r in rows.values()
                                         if (r["components"] or 0) <= 1) / len(rows), 3) if rows else None),
        }

    contrast = {}
    ctrl = data["ctrl"]
    for arm in ("surv", "survfd"):
        seeds = sorted(set(ctrl) & set(data[arm]))
        diffs = [data[arm][s]["s_mean_last"] - ctrl[s]["s_mean_last"]
                 for s in seeds
                 if data[arm][s]["s_mean_last"] is not None and ctrl[s]["s_mean_last"] is not None]
        if diffs:
            contrast[arm] = {
                "n": len(diffs),
                "median_drift": round(st.median(diffs), 3),
                "seeds_positive": sum(1 for d in diffs if d > 0),
                "per_seed": [round(d, 3) for d in diffs],
                "meets_bar": (st.median(diffs) > DRIFT_BAR and sum(1 for d in diffs if d > 0) >= SIGN_BAR),
            }
    return {"arms": arms, "contrast_vs_control": contrast}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E6p analysis: three selection regimes")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = load()
    if not any(data.values()):
        print("[e6p] нет прогонов — нечего считать")
        return 0
    summary = summarise(data)
    out = {
        "kind": "l1_field_e6p_selection",
        "experiment": "E6p",
        "command": "python scripts/e6p_analyse.py --write",
        "prereg": "reports/2026-11-01-e6p-selection-regimes-plan.md",
        "criterion": {"drift_bar": DRIFT_BAR, "sign_bar": SIGN_BAR, "paired_by": "seed"},
        **summary,
        "not_claimed": [
            "p-values are not computed: ten autocorrelated trajectories would overstate precision",
            "fixation is defined as median components <= 1, not as a dynamical criterion",
            "the survival channel is implemented as k_eff = k*(1 + beta*(s_ref - s)), so 'selection' here means 'drift of a trait that changes decay'",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[e6p] written: {OUT.name}")
    for arm, a in summary["arms"].items():
        print("  %-7s n=%2d  s_end=%s  spred=%s  splits=%s  r=%s  components=%s  fixation=%s" % (
            arm, a["n"], a["s_mean_last_median"], a["s_sd_between_median"], a["splits_median"],
            a["r_median"], a["components_median"], a["fixation_share"]))
    for arm, c in summary["contrast_vs_control"].items():
        print("  %-7s drift %+0.3f (%d/%d seeds positive)  meets bar: %s" % (
            arm, c["median_drift"], c["seeds_positive"], c["n"], c["meets_bar"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
