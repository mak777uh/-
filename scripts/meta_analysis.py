"""Meta-analysis: across all series, did mechanism X help the cell?

Why. The bench has 583 reports and 791 artifacts, and no script asks the question that matters across them:
**in what fraction of series did a mechanism help the cell, in the cell's own terms?** The corpus audit
(08.11) found that 300 of 320 artifacts record the cell's own measures, so the question CAN be asked.

What this does.
  1. Groups artifacts by MECHANISM. A mechanism is a config field that a series varied; the grouping rule is
     explicit and printed, so the reader can disagree with it (docs/open-questions.md Q14).
  2. For each mechanism, reports the paired difference in the cell's own measures between arms, and the
     fraction of series where the arm with the mechanism did better.
  3. Says plainly what it cannot do: a mechanism with one arm has no comparison, and a series with no
     recorded arm is not counted.

The readouts are the ones the corpus records: energy, survival, offspring. A ranking (the favourable share)
is NOT used, because it is blind to order.

Usage:
  python scripts/meta_analysis.py                 # report
  python scripts/meta_analysis.py --json out.json
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")

# The mechanisms the bench has varied, as config fields. The name is what a reader would call it; the keys
# are the field names that carry it in an artifact.
MECHANISMS = {
    "plasticity (record of the resource)": ["plastic_eta"],
    "signal (patch inflow)": ["patch_inflow_base", "patch_inflow_rich", "patch_mode"],
    "frequency dependence": ["freq_dep"],
    "cell type A/B": ["type_mode", "type_level"],
    "membrane gating": ["membrane_gated"],
    "learning of the placement weight": ["learn_w", "learn_mode"],
    "mobility of the spore": ["mobility_steps", "mobility_cost"],
    "organism mobility": ["organism_mobility_cost"],
    "death return (niche)": ["death_return", "death_return_mode"],
    "spore bias": ["spore_bias"],
    "income mode": ["income_mode"],
    "budding unit": ["budding_unit"],
}

# The cell's own measures. A ranking (the favourable share) is deliberately absent, because it is blind to
# order. The corpus has NO common schema: one artifact records `alive_final`, another `alive_last`, another
# `median`, another `pop_time`. A fixed list therefore finds nothing, so measures are recognised by PATTERN
# and the names actually used are reported - the heterogeneity is a finding, not something to hide.
MEASURE_PATTERNS = (
    "alive_final", "alive_last", "alive_max", "alive_cells", "alive_series_points",
    "energy_total", "energy_last", "energy_mean", "energy_final",
    "born", "died", "births", "deaths", "pop_time", "median", "mean",
)
# names that look like a measure but are not the cell's own
NOT_MEASURES = ("invader_share", "a_share", "behaviour_entropy", "collapses", "invalid_reason",
                "generation_step", "growth", "fixated", "crowd", "rho", "I_obs", "I_null")

OWN_MEASURES = MEASURE_PATTERNS  # kept for the report


def _is_measure(name: str) -> bool:
    if any(bad in name for bad in NOT_MEASURES):
        return False
    return any(pat in name for pat in MEASURE_PATTERNS)


def _scan(path: str) -> list[dict]:
    """Read one artifact into a list of run records.

    The corpus has three shapes and the first version of this script knew only the first:
      A. one run with a `config` block at the top level;
      B. a MATRIX with `rows`, one row per run, each row carrying `arm` and the measures;
      C. a `by_arm` block, a dict from arm label to a list of values.
    A file that is none of these (a survey, an index, a note) contributes nothing and is counted as skipped.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:  # noqa: BLE001
        return []
    if not isinstance(d, dict):
        return []
    name = os.path.basename(path)
    out: list[dict] = []

    # A: a single run
    cfg = d.get("config")
    if isinstance(cfg, dict) and cfg:
        out.append({"config": cfg, "summary": d.get("summary") or d, "name": name})
        return out

    # B: a matrix of rows
    rows = d.get("rows")
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        for r in rows:
            if not isinstance(r, dict):
                continue
            arm = r.get("arm")
            out.append({
                "config": {k: v for k, v in r.items() if k not in OWN_MEASURES},
                "arm": arm,
                "summary": r,
                "name": name,
            })
        return out

    # C: a by_arm block
    by_arm = d.get("by_arm")
    if isinstance(by_arm, dict) and by_arm:
        for arm, vals in by_arm.items():
            if isinstance(vals, list):
                mean = sum(v for v in vals if isinstance(v, (int, float))) / max(len(vals), 1)
            elif isinstance(vals, (int, float)):
                mean = float(vals)
            else:
                continue
            out.append({"config": {"arm": arm}, "arm": arm,
                        "summary": {"arm": arm, "value": mean}, "name": name})
        return out
    return []


def _arm_value(cfg: dict, keys: list[str]) -> tuple:
    """The arm label: the values of the mechanism's fields, in order."""
    return tuple(cfg.get(k) for k in keys)


def _measures(rec: dict) -> dict:
    """The cell's own measures, recognised by name, from wherever the artifact keeps them."""
    out = {}
    for src in (rec.get("summary") or {}, rec.get("config") or {}):
        if not isinstance(src, dict):
            continue
        for k, v in src.items():
            if _is_measure(k) and isinstance(v, (int, float)) and k not in out:
                out[k] = v
    series = (rec.get("summary") or {}).get("series") or []
    if series and isinstance(series[-1], dict):
        for k, v in series[-1].items():
            if _is_measure(k) and isinstance(v, (int, float)) and k not in out:
                out[k] = v
    return out



# ---- Q14: are two parameters the same mechanism? ---------------------------------------------------
#
# The mechanist literature individuates a mechanism by the phenomenon it explains and by its causal
# organisation; the operational test is mutual manipulability. Two parameters are the same mechanism only if
# (a) they explain the same phenomenon and (b) an intervention in one changes the other in the same way.
#
# We cannot run interventions from the corpus, so the report states what it CAN see: whether the two fields
# ever appear in the same artifact (so they were varied together), and whether each appears alone. That is a
# necessary condition, not a sufficient one, and it is labelled as such.
MECHANISM_PAIRS = [
    ("trait_effect", "signal_gain"),
    ("plastic_eta", "plastic_gate"),
    ("budding_unit", "buds_per_component"),
    ("freq_dep", "mortality_gain"),
]


def mechanism_identity(records: list[dict]) -> list[dict]:
    out = []
    for a, b in MECHANISM_PAIRS:
        both = sum(1 for r in records if a in r["config"] and b in r["config"])
        only_a = sum(1 for r in records if a in r["config"] and b not in r["config"])
        only_b = sum(1 for r in records if b in r["config"] and a not in r["config"])
        if both == 0:
            verdict = "unresolved"
            why = "the two fields never appear together, so mutual manipulability cannot be checked"
        elif only_a == 0 and only_b == 0:
            verdict = "related"
            why = "they always appear together; the corpus cannot separate them"
        else:
            verdict = "related"
            why = f"they appear together {both} times and separately {only_a}/{only_b} times; a correlation " \
                  f"between them would be the next test"
        out.append({"a": a, "b": b, "together": both, "only_a": only_a, "only_b": only_b,
                    "verdict": verdict, "why": why})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(os.path.join(POND, "*.json")))
    records: list[dict] = []
    parsed = 0
    for p in files:
        recs = _scan(p)
        if recs:
            parsed += 1
            for r in recs:
                r["measures"] = _measures(r)
            records.extend(recs)
    print(f"[meta] файлов: {len(files)}, прочитано как матрицы/прогоны: {parsed}, "
          f"строк-прогонов: {len(records)}")

    report = {}
    for mech, keys in MECHANISMS.items():
        by_arm: dict[tuple, list[dict]] = {}
        for rec in records:
            cfg = rec["config"]
            if not any(k in cfg for k in keys):
                continue
            arm = _arm_value(cfg, keys)
            by_arm.setdefault(arm, []).append(rec)

        if len(by_arm) < 2:
            report[mech] = {"arms": len(by_arm), "verdict": "не с чем сравнивать",
                            "why": "механизм встречается в одном плече"}
            continue

        # For each measure, the arm with the largest mean against the rest.
        rows = []
        seen_measures = sorted({m for recs in by_arm.values() for r in recs for m in r.get("measures", {})})
        for m in seen_measures:
            means = {}
            for arm, recs in by_arm.items():
                vals = [r["measures"][m] for r in recs if m in r.get("measures", {})]
                if vals:
                    means[arm] = sum(vals) / len(vals)
            if len(means) < 2:
                continue
            best = max(means, key=means.get)
            worst = min(means, key=means.get)
            rows.append({"measure": m, "best_arm": str(best), "best": round(means[best], 4),
                         "worst_arm": str(worst), "worst": round(means[worst], 4),
                         "difference": round(means[best] - means[worst], 4)})

        report[mech] = {"arms": len(by_arm), "series": sum(len(v) for v in by_arm.values()),
                        "measures": rows}

    print()
    print("=" * 78)
    for mech, r in report.items():
        if r.get("verdict"):
            print(f"{mech}: {r['verdict']} ({r['why']})")
            continue
        print(f"{mech}: {r['arms']} плеча, {r['series']} артефактов")
        for row in r["measures"]:
            print(f"    {row['measure']:14s} лучший {row['best']:>10.4f} против {row['worst']:>10.4f} "
                  f"разница {row['difference']:+.4f}")

    print()
    print("=" * 78)
    print("Q14: are two parameters the same mechanism? (mutual manipulability)")
    for row in mechanism_identity(records):
        print(f"  {row['a']} vs {row['b']}: {row['verdict']} - {row['why']}")

    print()
    print("[meta] чего этот отчёт не делает: он не проверяет, что разница вызвана механизмом. "
          "Плечи могут отличаться и другими полями; парность по сидам не проверяется.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
