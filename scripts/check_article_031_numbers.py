"""Verify every headline number in article 031 against the committed artifacts.

The article claims a set of numbers; each must be traceable to a JSON artifact under
morphogenesis/experiments/E09_pond/. This script re-reads the artifacts and checks the
specific values the prose states, so the prose can never drift from the data.

Run:  python scripts/check_article_031_numbers.py
Exit: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")

CHECKS: list[tuple[str, str, str, float, float]] = [
    # (article claim, artifact file, json path, expected, tolerance)
    ("S12/D2 local greed first window 0.475", "s12_d2_full.json", "local1.fav0", 0.475, 0.002),
    ("S12/D2 baseline first window 0.357", "s12_d2_full.json", "baseline.fav0", 0.357, 0.002),
    ("S12/D2 gap last window 0.036", "s12_d2_full.json", "gap5", 0.036, 0.004),
    ("S13/D3 gap low density first window 0.221", "s13_d3_full.json", "low_density.gap0", 0.221, 0.003),
    ("S13/D3 gap base first window 0.118", "s13_d3_full.json", "base.gap0", 0.118, 0.003),
    ("S13/D3 gap high density first window 0.057", "s13_d3_full.json", "high_density.gap0", 0.057, 0.003),
    ("S14/D4 pearson -0.57", "s14_d4_full.json", "pearson_gap_vs_rich_occupancy", -0.5675, 0.01),
    ("S14/D4 rich occupancy first window 0.025", "s14_d4_full.json", "base.occ0", 0.025, 0.003),
    ("S14/D4 rich occupancy last window 0.348", "s14_d4_full.json", "base.occ5", 0.348, 0.004),
    ("S14/D4 rich resource first 0.26", "s14_d4_full.json", "base.rres0", 0.26, 0.005),
    ("S14/D4 rich resource last 0.22", "s14_d4_full.json", "base.rres5", 0.22, 0.005),
    ("S16/E1b drain_mid gap fourth window -0.022", "s16_e1b_full.json", "drain_mid.gap3", -0.022, 0.004),
    ("S6/C3 double recovery 0.648", "s6_c3_double_baseline.json", "double.win5", 0.648, 0.003),
    ("S6/C3 control 0.356", "s6_c3_double_baseline.json", "control.win5", 0.356, 0.003),
    ("S7/C3b new env C 0.609", "s7_c3b_baseline_ABC.json", "double_new.win5", 0.609, 0.003),
    ("S9/C2 heritable 0.459", "s9_c2_full.json", "heritable.win2", 0.459, 0.003),
    ("S9/C2 neutral 0.533", "s9_c2_full.json", "neutral.win2", 0.533, 0.003),
    ("S10/C2b neutral 0.429", "s10_c2b_full.json", "neutral.win2", 0.429, 0.003),
    ("S10/C2b heritable 0.431", "s10_c2b_full.json", "heritable.win2", 0.431, 0.003),
    ("S10/C2b transplant 0.427", "s10_c2b_full.json", "transplant.win2", 0.427, 0.003),
]


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def load(name):
    with open(os.path.join(POND, name), encoding="utf-8") as fh:
        return json.load(fh)


def fav_window(doc, arm, i, regime=None):
    """Mean favourable_share for `arm` in window i (s12/s13/s16 use favourable_share)."""
    rows = [r for r in doc["rows"] if r["arm"] == arm]
    if regime is not None:
        rows = [r for r in rows if r.get("regime") == regime]
    vals = [r["windows"][i]["favourable_share"] for r in rows
            if i < len(r["windows"]) and r["windows"][i].get("favourable_share") is not None]
    return mean(vals)


def resolve(name, path):
    doc = load(name)
    parts = path.split(".")
    if name == "s14_d4_full.json":
        if path == "pearson_gap_vs_rich_occupancy":
            return doc["pearson_gap_vs_rich_occupancy"]
        regime, key = parts
        rows = [r for r in doc["rows"] if r["regime"] == regime and r["arm"] == "baseline"]
        idx = int(key[-1])
        field = {"occ": "rich_occupancy", "rres": "rich_resource"}[key[:-1]]
        return mean([r["windows"][idx][field] for r in rows if idx < len(r["windows"])])
    if name in ("s12_d2_full.json", "s13_d3_full.json", "s16_e1b_full.json"):
        # s13/s16 rows carry a "regime" field; s12 does not (single regime)
        if len(parts) == 2 and parts[1].startswith("fav"):
            regime = parts[0] if name != "s12_d2_full.json" else None
            return fav_window(doc, "baseline" if regime else parts[0], int(parts[1][-1]), regime)
        if len(parts) == 2 and parts[1].startswith("gap"):
            idx = int(parts[1][-1])
            regime = parts[0] if name != "s12_d2_full.json" else None
            b = fav_window(doc, "baseline", idx, regime)
            l = fav_window(doc, "local1", idx, regime)
            return (l - b) if (b is not None and l is not None) else None
        if len(parts) == 1 and parts[0].startswith("gap"):
            # s12 form: "gap5" -> single regime, window 5
            idx = int(parts[0][-1])
            b = fav_window(doc, "baseline", idx)
            l = fav_window(doc, "local1", idx)
            return (l - b) if (b is not None and l is not None) else None
    if name in ("s6_c3_double_baseline.json", "s7_c3b_baseline_ABC.json"):
        arm, key = parts
        rows = [r for r in doc["rows"] if r["arm"] == arm]
        idx = int(key[-1])
        return mean([r["windows"][idx]["correct_share"] for r in rows if idx < len(r["windows"])])
    if name in ("s9_c2_full.json", "s10_c2b_full.json"):
        arm, key = parts
        rows = [r for r in doc["rows"] if r["arm"] == arm]
        idx = int(key[-1])
        return mean([r["windows"][idx]["correct_share"] for r in rows if idx < len(r["windows"])])
    raise SystemExit(f"no resolver for {name} / {path}")


def main() -> int:
    fails = 0
    for claim, name, path, expected, tol in CHECKS:
        try:
            got = resolve(name, path)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {claim}: {exc}")
            fails += 1
            continue
        ok = got is not None and abs(got - expected) <= tol
        mark = "OK  " if ok else "FAIL"
        print(f"{mark} {claim}: got {None if got is None else round(got, 4)} expected {expected}")
        if not ok:
            fails += 1
    print(f"\n{fails} failures out of {len(CHECKS)} checks")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
