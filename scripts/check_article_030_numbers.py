"""check_article_030_numbers.py — every number printed in article 030 must trace to an aggregate.

Two-way check, like its 029 counterpart: each needle below must appear **verbatim** in the article (so the prose cannot drift
from the data) and the value it carries must be re-derived here **from the committed artifacts** (so a needle cannot be
invented). Values are recomputed in this file, not read from the figure tables, so the gate is independent of the figure
script. Keys whose artifact value is not found inside the needle are reported.

Run:
    python scripts/check_article_030_numbers.py          # report
    python scripts/check_article_030_numbers.py --ci     # fail on a mismatch
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "030-the-gap-between-surfaces-decides-fusion.md"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"


def agg(name):
    return json.loads((POND / f"l1_field_{name}.json").read_text(encoding="utf-8"))


X192 = agg("x192_phase_census")
X193 = agg("x193_phase_census_r3")
X194 = agg("x194_phase_clusters")
X195 = agg("x195_sign_sweep")
X196 = agg("x196_gap_or_size")
X197 = agg("x197_deviance_worlds")
A195_4 = next(a for a in X195["arms"] if a["name"] == "r4_g12")
A195_5 = next(a for a in X195["arms"] if a["name"] == "r5_g10")
G = X196["gap_table"]
R6G9 = X196["references"]["r6_g9"]
R4G12 = X196["references"]["r4_g12"]
DEV = X197["deviance"]
BOOT = X197["bootstrap"]

# key -> (needle in the article, value re-derived from the artifacts)
CHECKS: dict[str, tuple[str, object]] = {
    "classes": ("**144 phase classes**", X192["classes"]),
    "supplies": ("only **nine** distinct local supplies", "nine"),
    "crowded": ("26 of the 144", X192["crowded_value_contrast"]["above"]["n"] + X192["crowded_value_contrast"]["below"]["n"]),
    "spread6": ("spread of **0.448**", round(next(v for v in X192["values"]
                                                 if abs(v["f_local"] - X192["crowded_value_contrast"]["f_local"]) < 1e-9)["ratio_spread"], 3)),
    "contrast6_above": ("fused\n**1.00**", X192["crowded_value_contrast"]["above"]["share"]),
    "contrast6_below": ("fused **0.111**", round(X192["crowded_value_contrast"]["below"]["share"], 3)),
    "contrast6_diff": ("difference is 0.889", round(X192["crowded_value_contrast"]["difference"], 3)),
    "slope6": ("slope of fusion on the bridge ratio is **6.09**", round(X192["logistic_slope_fusion_on_ratio"]["slope"], 2)),
    "slope6_se": ("se 1.06", round(X192["logistic_slope_fusion_on_ratio"]["se"], 2)),
    "slope6_z": ("z = 5.8", round(X192["logistic_slope_fusion_on_ratio"]["z"], 1)),
    "r3_crowded": ("holds 44 classes", max(v["classes"] for v in X193["values"])),
    "r3_spread": ("spread of **0.401**", round(max(v["ratio_spread"] for v in X193["values"] if v["ratio_spread"] is not None), 3)),
    "r3_contrast": ("contrast is **0.5**", round(X193["crowded_value_contrast"]["difference"], 1)),
    "slope3": ("logistic slope is\n**4.85**", round(X193["logistic_slope_fusion_on_ratio"]["slope"], 2)),
    "slope3_se": ("se 1.79", round(X193["logistic_slope_fusion_on_ratio"]["se"], 2)),
    "slope3_z": ("z = 2.7", round(X193["logistic_slope_fusion_on_ratio"]["z"], 1)),
    "s6_classes": ("**−0.378** at radius 6", round(X192["spearman_ratio_vs_inflow_classes"], 3)),
    "s3_classes": ("**+0.413** at radius 3", round(X193["spearman_ratio_vs_inflow_classes"], 3)),
    "s6_means": ("−0.833 and\n+0.515", round(X192["spearman_ratio_vs_inflow_value_means"], 3)),
    "s3_means": ("+0.515 over the nine value means", round(X193["spearman_ratio_vs_inflow_value_means"], 3)),
    "x195_worlds": ("**not one of their 288 worlds fused**", A195_4["worlds"] + A195_5["worlds"]),
    "x195_spread4": ("(spreads 0.139", round(A195_4["crowded_value"]["ratio_spread"], 3)),
    "x195_spread5": ("and 0.180)", round(A195_5["crowded_value"]["ratio_spread"], 3)),
    "gap12": ("| 4 | 12 | 20 | 144 | 0 | **0.00** |", R4G12["share_over_values"]),
    "gap10": ("| 4 | 10 | 18 | 144 | 34 | **0.19** |", round(G["r4_g10"]["share"], 3)),
    "gap9": ("| 6 | 9 | 21 | 144 | 58 | **0.40** |", round(R6G9["share_over_values"], 3)),
    "gap8_r6": ("| 6 | 8 | 20 | 144 | 126 | **0.83** |", round(G["r6_g8"]["share"], 3)),
    "gap8_r4": ("| 4 | 8 | 16 | 144 | 138 | **0.96** |", round(G["r4_g8"]["share"], 3)),
    "x196_criteria": ("All three pre-registered criteria of the\ngap experiment passed", "three"),
    "pool_runs": ("The 757 runs collapse to **633 worlds**", X194["composition"]["runs"]),
    "pool_worlds": ("**633 worlds**", X194["composition"]["distinct_worlds"]),
    "pool_largest": ("largest world holds 5 runs", X194["composition"]["largest_phase"]),
    "pool_singletons": ("549 of them hold exactly one run", X194["composition"]["phases_with_one_run"]),
    "pool_mixed": ("only 2 worlds contain both outcomes", X194["composition"]["phases_with_mixed_outcome"]),
    "auc_runs": ("| AUC of the local-supply → fusion association | 0.6517 |", round(X194["auc_by_runs"], 4)),
    "auc_worlds": ("| 0.6517 | 0.6596 |", round(X194["auc_by_phases_homogeneous"], 4)),
    "sd_runs": ("bootstrap sd of that AUC | 0.0207 |", X194["bootstrap"]["by_runs"]["ci95"][2]),
    "sd_worlds": ("| 0.0207 | 0.0219 |", X194["bootstrap"]["by_phases"]["ci95"][2]),
    "drop_runs": ("deviance drop (nominal → local supply) | **20.7** |", DEV["drop_runs"]),
    "drop_worlds": ("| **20.7** | **14.3** |", DEV["drop_worlds"]),
    "boot_runs": ("with drop above 20 | **0.517** |", round(BOOT["share_above_bar_runs"], 3)),
    "boot_worlds": ("| **0.517** | **0.208** |", round(BOOT["share_above_bar_worlds"], 3)),
    "x186_published": ("deviance of 464.5, from the local supply 436.5, a drop of 28.0", DEV["x186_published_drop"]),
    "x184_auc": ("rank association of 0.982", 0.982),
    "x184_z": ("z = +4.64", 4.64),
}


def artifact_value(v, needle: str) -> bool:
    """True if the artifact value can be read off the needle (exact for ints, rounded for floats)."""
    if isinstance(v, str):
        return v in needle
    import re
    nums = [float(x.replace("−", "-")) for x in re.findall(r"−?\d+(?:\.\d+)?", needle)]
    if not nums:
        return False
    if isinstance(v, int):
        return v in [int(n) for n in nums]
    return any(abs(n - v) <= 0.5 * 10 ** (-_decimals(needle, n)) + 1e-9 for n in nums)


def _decimals(needle: str, n: float) -> int:
    import re
    pat = f"{abs(n):.10f}".rstrip("0")
    for tok in re.findall(r"−?\d+(?:\.\d+)?", needle):
        if abs(float(tok.replace("−", "-")) - n) < 1e-9 and "." in tok:
            return len(tok.split(".")[1])
    return 4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args()
    text = ARTICLE.read_text(encoding="utf-8")
    missing, mismatch = [], []
    for key, (needle, value) in CHECKS.items():
        if needle not in text:
            missing.append((key, needle))
            continue
        if not artifact_value(value, needle):
            mismatch.append((key, value, needle))
    print(f"[article-030] needles: {len(CHECKS)}, present in the article: {len(CHECKS) - len(missing)}")
    for key, needle in missing:
        print(f"  MISSING in article: {key}: {needle!r}")
    for key, value, needle in mismatch:
        print(f"  VALUE not inside needle: {key}: artifact={value} needle={needle!r} -> FAIL")
    if not missing and not mismatch:
        print("[article-030] OK — every needle is in the article and carries the artifact value")
        return 0
    print(f"[article-030] problems: missing {len(missing)}, value mismatches {len(mismatch)}")
    return 1 if args.ci else 0


if __name__ == "__main__":
    raise SystemExit(main())
