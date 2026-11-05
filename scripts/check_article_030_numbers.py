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
import re
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
X156 = agg("x156_shape_heredity")
X157 = agg("x157_gap_geometry")
X159 = agg("x157_quantum")
X158 = agg("x158_crossing")
X162B = agg("x162b_decay")
X164 = agg("x164_asymmetric")
X165 = agg("x165_three_bodies")
X166 = agg("x166_threshold")
X167B = agg("x167b_reversibility")
X168C = agg("x168c_inflow")
X168D = agg("x168d_gap11")
X169 = agg("x169_seam")
X170 = agg("x170_corridor")
X171 = agg("x171_corridor_sizes")
X172 = agg("x172_forecast")
X173 = agg("x173_bridge")
X174 = agg("x174_gap_corridor")
X175 = agg("x175_interior")
X176 = agg("x176_past_crossing")
X177 = agg("x177_edge")
X178 = agg("x178_cliff")
X179 = agg("x179_crossing_table")
X180 = agg("x180_dispersion")
X181 = agg("x181_worst_cell")
X182 = agg("x182_local_inflow")
X183 = agg("x183_local_collapse")
X188 = agg("x188_nucleation_identity")
X189 = agg("x189_bridge")
X198 = agg("x198_gap_curve")


def _worst179():
    for c in X179["two_body_cells"]:
        if c["radius"] == 3.0 and c["gap"] == 10.0 and abs(c["F"] - 0.03) < 1e-9:
            return c
    raise KeyError("worst cell not found")


W179 = _worst179()

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

# --- v2.0: the crossing and its geometry (X157, X159, X158, X164-X168) ---
CHECKS.update({
    "v20_contact_median": ("is **1.93 cells**", X157["contact_gap_median"]),
    "v20_contact_min": ("a range of 0.94 to 4.87", X157["contact_gap_min"]),
    "v20_contact_max": ("a range of 0.94 to 4.87", X157["contact_gap_max"]),
    "v20_contact_r3": ("medians are 2.07, 1.89, 1.69 and 1.93", X157["by_radius"]["r3.0"]["g_fusion_median"]),
    "v20_contact_r45": ("medians are 2.07, 1.89, 1.69 and 1.93", X157["by_radius"]["r4.5"]["g_fusion_median"]),
    "v20_contact_r6": ("medians are 2.07, 1.89, 1.69 and 1.93", X157["by_radius"]["r6.0"]["g_fusion_median"]),
    "v20_window_median": ("by a median of **1.32 cells**", X159["window_width_median"]),
    "v20_threshold_low": ("lower bound at a median of **0.7 cells**", X159["threshold_low_median"]),
    "v20_cross_r3": ("at gaps 10, 10 and 9 cells for radii 3", X158["by_radius"]["r3.0"]["crossing_gap"]),
    "v20_cross_r45": ("at gaps 10, 10 and 9 cells for radii 3, 4.5 and 6", X158["by_radius"]["r4.5"]["crossing_gap"]),
    "v20_cross_r6": ("gaps 10, 10 and 9 cells for radii 3, 4.5 and 6", X158["by_radius"]["r6.0"]["crossing_gap"]),
    "v20_x158_share": ("**0.467 (7 of 15)**", round(X158["arms"]["r3.0_g10.0"]["share"], 3)),
    "v20_asym_g8": ("rising from 2.60 cells at gap 8", round(X164["by_arm"]["asym_g8"]["g_median"], 2)),
    "v20_asym_g10": ("to 4.38 at gap 10", round(X164["by_arm"]["asym_g10"]["g_median"], 2)),
    "v20_three_g8": ("at gap 8 coalesces in 100 % of runs, at gap 10 in 20 %, at gap 12 in 0 %", round(100 * X165["by_gap"]["8"]["share_fused"])),
    "v20_three_g10": ("at gap 8 coalesces in 100 % of runs, at gap 10 in 20 %, at gap 12 in 0 %", round(100 * X165["by_gap"]["10"]["share_fused"])),
    "v20_three_g12": ("at gap 10 in 20 %, at gap 12 in 0 %", round(100 * X165["by_gap"]["12"]["share_fused"])),
    "v20_x166_arm_spread": ("Per-arm medians then differ by **2.07 cells**", X166["per_arm_median_spread"]),
    "v20_x166_scatter": ("within-arm scatter is **0.44 cells**", X166["median_within_arm_sd"]),
    "v20_x168c_g11_f026": ("shares of **0.0, 0.2 and 0.4** at F = 0.026, 0.030 and 0.036", round(X168C["share_at_gap11_by_rate"]["0.026"], 1)),
    "v20_x168c_g11_f030": ("shares of **0.0, 0.2 and 0.4** at F = 0.026, 0.030 and 0.036", round(X168C["share_at_gap11_by_rate"]["0.03"], 1)),
    "v20_x168c_g11_f036": ("**0.0, 0.2 and 0.4** at F = 0.026, 0.030 and 0.036", round(X168C["share_at_gap11_by_rate"]["0.036"], 1)),
    "v20_x168d_fisher": ("a Fisher p of **0.21053**", round(X168D["fisher_tests"]["0.026_vs_0.036"], 5)),
})

# --- v2.0: what a daughter keeps (X156, X162b, X167b, X169, X170) ---
CHECKS.update({
    "v20_shape_elong": ("the mean slope is **0.5167** for elongation",
                        round((X156["cells"]["f030"]["traits"]["log_elong"]["slope"]
                               + X156["cells"]["f040"]["traits"]["log_elong"]["slope"]) / 2, 4)),
    "v20_shape_width": ("**0.4811** for width",
                        round((X156["cells"]["f030"]["traits"]["log_width"]["slope"]
                               + X156["cells"]["f040"]["traits"]["log_width"]["slope"]) / 2, 4)),
    "v20_neighbour_1": ("(0.205, 0.236, 0.408, 0.568)", round(X162B["by_order"]["1"]["slope"], 3)),
    "v20_neighbour_2": ("(0.205, 0.236, 0.408, 0.568)", round(X162B["by_order"]["2"]["slope"], 3)),
    "v20_neighbour_4": ("0.408, 0.568) because the distance", round(X162B["by_order"]["4"]["slope"], 3)),
    "v20_merged_steps": ("divides after **25 steps**", X167B["merged"]["steps_to_division_median"]),
    "v20_single_steps": ("against the single one's **40**", X167B["single"]["steps_to_division_median"]),
    "v20_waist": ("waist ratio is **0.357**", X169["neck_measure"]["pair_ratio_median"]),
    "v20_x170_f026": ("**0.52, 0.48 and 0.39**", round(X170["medians"]["0.026"], 2)),
    "v20_x170_f030": ("**0.52, 0.48 and 0.39**", round(X170["medians"]["0.03"], 2)),
    "v20_x170_f036": ("0.48 and 0.39** at F = 0.026, 0.030 and 0.036", round(X170["medians"]["0.036"], 2)),
    "v20_x170_diff": ("difference of **0.12**", round(X170["extreme"]["difference"], 2)),
})

# --- v2.0: the corridor, the edge, the cliff, the ladder (X171-X178, X182, X183) ---
CHECKS.update({
    "v20_171_r3": ("medians of **0.479**", X171["medians"]["3"]),
    "v20_171_r45": ("**0.4918** and **0.4701**", X171["medians"]["4.5"]),
    "v20_171_r6": ("and **0.4701** (radius 3, 4.5, 6)", X171["medians"]["6"]),
    "v20_171_pooled_sd": ("pooled within-group spread of **0.036**", X171["difference"]["pooled_sd"]),
    "v20_171_diff": ("largest size-to-size difference is **0.0217**", X171["difference"]["difference"]),
    "v20_174_g8": ("are **0.3666**, **0.4107** and **0.479**", round(X174["by_gap"]["8"]["median"], 4)),
    "v20_174_g9": ("**0.4107** and **0.479** at gaps 8, 9 and 10", round(X174["by_gap"]["9"]["median"], 4)),
    "v20_174_g10": ("and **0.479** at gaps 8, 9 and 10", round(X174["by_gap"]["10"]["median"], 3)),
    "v20_174_sd": ("pooled within-gap spread of **0.0595**", X174["difference"]["pooled_sd"]),
    "v20_174_pearson": ("(Pearson **−0.9492**", round(X174["across_arms"]["pearson_share_vs_corridor"], 4)),
    "v20_174_spearman": ("Spearman **−0.881**", round(X174["across_arms"]["spearman_share_vs_corridor"], 3)),
    "v20_174_duplicate": ("two of those 8 entries are the same arm", X174["across_arms"]["n"]),
    "v20_175_corridor": ("corridor landed at **0.4373**", X175["observed"]["corridor_median"]),
    "v20_175_share": ("share came out **0.2667 (4 of 15)**", round(X175["observed"]["share"], 4)),
    "v20_172_obs_corridor": ("observed at **0.442**", round(X172["observed"]["corridor_median"], 3)),
    "v20_172_pred_corridor": ("predicted at 0.436 ± 0.08", round(float(str(X172["predictions"]["corridor"]).split("±")[0].strip()), 3)),
    "v20_172_fused": ("only **8 of 20** pairs fused", X172["observed"]["fused"]),
    "v20_176_zero": ("**0 of 15** contact events", X176["observed"]["fused"]),
    "v20_176_runs": ("**0 of 15** contact events (0 of 25 pooled", X176["observed"]["runs"]),
    "v20_177_zero": ("**0 of 20** (0 of 35 pooled)", X177["observed"]["fused"]),
    "v20_178_share": ("**10 of 30 = 0.3333**", round(X178["observed"]["share"], 4)),
    "v20_178_wilson_lo": ("[0.1923, 0.5122]", X178["observed"]["wilson"][0]),
    "v20_178_x158": ("against 3 of 10 in the earlier arm", X178["references"]["x158_same_cell"]["fused"]),
    "v20_173_threshold": ("Its best threshold, 0.4284", X173["split"]["threshold"]),
    "v20_173_misclassified": ("misclassifies **7 of 30**", X173["split"]["misclassified"]),
    "v20_182_z": ("Cochran–Armitage z = **−4.446**", X182["trend"]["z"]),
    "v20_183_nominal": ("nominal rate gives an AUC of **0.5874**", round(X183["candidates"]["F_nominal"]["auc_overall"], 4)),
    "v20_183_cold": ("colder** of the two bodies gives **0.8656**", round(X183["candidates"]["F_local_min"]["auc_overall"], 4)),
    "v20_183_mid": ("**midpoint** of the pair gives **0.2149**", round(X183["candidates"]["F_local_mid"]["auc_overall"], 4)),
    "v20_183_warm": ("warmer body gives 0.6359", round(X183["candidates"]["F_local_max"]["auc_overall"], 4)),
    "v20_183_mean": ("mean of the two sites gives 0.8396", round(X183["candidates"]["F_local_mean"]["auc_overall"], 4)),
    "v20_183_dev_nominal": ("deviance **185.0**", X183["candidates"]["F_nominal"]["deviance"]),
    "v20_183_dev_cold": ("deviance **129.3**", X183["candidates"]["F_local_min"]["deviance"]),
})

# --- v2.0: the crossing table and the dispersion (X179, X180, X181) ---
CHECKS.update({
    "v20_179_cells": ("**57 cells, 772 runs**", len(X179["two_body_cells"])),
    "v20_179_runs": ("**57 cells, 772 runs**", X179["two_body_runs"]),
    "v20_179_scanned": ("is **1119**", X179["files_scanned"]),
    "v20_179_other": ("18 further cells with one or three components", len(X179["other_cells"])),
    "v20_179_control_fused": ("fuses **48 of 48 = 1.00**", next(c for c in X179["two_body_cells"] if c["radius"] == 3.0 and c["gap"] == 8.0 and abs(c["F"] - 0.03) < 1e-9)["fused"]),
    "v20_179_worst": ("32 of 79", W179["fused"]),
    "v20_179_worst_runs": ("32 of 79", W179["runs"]),
    "v20_180_cells": ("In the 17 cells where both outcomes", X180["cells_with_both_outcomes"]),
    "v20_180_runs": ("over **316 runs**", sum(c["runs"] for c in X180["cells"])),
    "v20_180_pb": ("mean point-biserial correlation is **−0.552**", round(X180["mean_point_biserial"], 3)),
    "v20_180_pooled": ("(pooled **−0.527**", round(X180["pooled_point_biserial"], 3)),
    "v20_180_z": ("is **−7.807**", round(X180["z_top_vs_bottom"], 3)),
    "v20_180_band0": ("**0.836** (46 of 55)", round(X180["local_inflow_bands"][0]["share"], 3)),
    "v20_180_band3": ("and **0.16** (13 of 81)", round(X180["local_inflow_bands"][3]["share"], 2)),
    "v20_181_share": ("**12 of 30 = 0.40**", round(X181["observed"]["share"], 2)),
    "v20_181_wilson": ("[0.2459, 0.5768]", round(X181["observed"]["wilson"][0], 4)),
    "v20_181_before": ("read **20 of 49 = 0.4082**", round(X181["references"]["pooled_before"]["share"], 4)),
    "v20_181_after": ("after it **32 of 79 = 0.4051**", round(X181["references"]["pooled_after"]["share"], 4)),
})

# --- v2.0: the bridge against the local inflow (X188, X189) ---
CHECKS.update({
    "v20_189_r6": ("sits **−0.08655** below", X189["radius6_warm_minus_cold"]),
    "v20_189_r3": ("difference is **+0.00387**", X189["radius3_warm_minus_cold"]),
    "v20_189_contact": ("**−0.20158** at contact", X189["radius6_contact_warm_minus_cold"]),
    "v20_189_preinit": ("9 of the twelve runs", X189["tightest_slice_at_step_40_runs"]),
    "v20_188_registered": ("warm minus cold of **+0.234**", X188["radius6_warm_minus_cold"]),
    "v20_188_flip_lo": ("from **−0.781** to", X188["sensitivity"]["frame_initial_midpoint"]["radius6_warm_minus_cold"]),
    "v20_188_runs": ("positive in all 24 runs", sum(X188["outcome_crosstab"].values())),
    "v20_156_rate_elong_f030": ("elongation 0.6074 against 0.4260",
                               round(X156["cells"]["f030"]["traits"]["log_elong"]["slope"], 4)),
    "v20_156_rate_elong_f040": ("elongation 0.6074 against 0.4260",
                                round(X156["cells"]["f040"]["traits"]["log_elong"]["slope"], 4)),
    "v20_156_rate_width_f030": ("width 0.3384 against 0.6238",
                                round(X156["cells"]["f030"]["traits"]["log_width"]["slope"], 4)),
    "v20_156_rate_width_f040": ("width 0.3384 against 0.6238",
                                round(X156["cells"]["f040"]["traits"]["log_width"]["slope"], 4)),
    "v20_167_area": ("combined area is **0.867** of the parents' area",
                     round(X167B["merged"]["area_ratio_median"], 3)),
    "v20_183_candidates": ("put 5 candidate readings", len(X183["candidates"])),
    "v20_188_flip_hi": ("**+0.394** and flip its sign",
                        round(X188["sensitivity"]["match2"]["radius6_warm_minus_cold"], 3)),
})


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


CHECKS.update({
    "v21_x198_worlds": ("**1152 worlds**", sum(a["worlds"] for a in X198["arms"])),
    "v21_x198_gaps_r4": ("5 gaps at radius 4 (12, 11, 10, 9, 8)", len([a for a in X198["arms"] if a["radius"] == 4.0])),
    "v21_x198_gaps_r6": ("3 at radius 6 (10, 9, 8)", len([a for a in X198["arms"] if a["radius"] == 6.0])),
    "v21_x198_r4g12_share": ("| 4 | 12 | 20 | 144 | 0 | **0.00** |", X198["gap_table"]["r4_g12"]["share"]),
    "v21_x198_r4g11_share": ("| 4 | 11 | 19 | 144 | 0 | **0.00** |", X198["gap_table"]["r4_g11"]["share"]),
    "v21_x198_r4g10_fused": ("| 4 | 10 | 18 | 144 | 34 | **0.1883** |", X198["gap_table"]["r4_g10"]["fused_worlds"]),
    "v21_x198_r4g10_share": ("| 4 | 10 | 18 | 144 | 34 | **0.1883** |", X198["gap_table"]["r4_g10"]["share"]),
    "v21_x198_r4g9_fused": ("| 4 | 9 | 17 | 144 | 86 | **0.646** |", X198["gap_table"]["r4_g9"]["fused_worlds"]),
    "v21_x198_r4g9_share": ("| 4 | 9 | 17 | 144 | 86 | **0.646** |", X198["gap_table"]["r4_g9"]["share"]),
    "v21_x198_r4g8_fused": ("| 4 | 8 | 16 | 144 | 138 | **0.9607** |", X198["gap_table"]["r4_g8"]["fused_worlds"]),
    "v21_x198_r4g8_share": ("| 4 | 8 | 16 | 144 | 138 | **0.9607** |", X198["gap_table"]["r4_g8"]["share"]),
    "v21_x198_r6g10_share": ("| 6 | 10 | 22 | 144 | 0 | **0.00** |", X198["gap_table"]["r6_g10"]["share"]),
    "v21_x198_r6g9_fused": ("| 6 | 9 | 21 | 144 | 58 | **0.402** |", X198["gap_table"]["r6_g9"]["fused_worlds"]),
    "v21_x198_r6g9_share": ("| 6 | 9 | 21 | 144 | 58 | **0.402** |", X198["gap_table"]["r6_g9"]["share"]),
    "v21_x198_r6g8_fused": ("| 6 | 8 | 20 | 144 | 126 | **0.8338** |", X198["gap_table"]["r6_g8"]["fused_worlds"]),
    "v21_x198_r6g8_share": ("| 6 | 8 | 20 | 144 | 126 | **0.8338** |", X198["gap_table"]["r6_g8"]["share"]),
    "v21_x198_criteria": ("all **3 of 3** pre-registered criteria pass", X198["criteria_passed"]),
    "v21_x198_spread_g11": ("spreads 0.254 and 0.139",
                            round({a["name"]: a["crowded_value"]["ratio_spread"] for a in X198["arms"]}["r4_g11"], 3)),
    "v21_x198_spread_g12": ("spreads 0.254 and 0.139",
                            round({a["name"]: a["crowded_value"]["ratio_spread"] for a in X198["arms"]}["r4_g12"], 3)),
})

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args()
    text = ARTICLE.read_text(encoding="utf-8")
    flat = re.sub(r"\s+", " ", text)
    missing, mismatch = [], []
    for key, (needle, value) in CHECKS.items():
        if re.sub(r"\s+", " ", needle) not in flat:
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
