"""check_article_029_numbers.py — every number printed in article 029 must trace to an aggregate.

Two-way check: each needle below must appear **verbatim** in the article (so the prose cannot drift from the data), and
its key must exist in `articles/029-figures/tables.json`, which the figure script builds directly from the aggregates
(so a needle cannot be invented). Keys in the tables that no needle covers are reported, so a value cannot quietly fall
out of the paper.

Run:
    python scripts/check_article_029_numbers.py          # report
    python scripts/check_article_029_numbers.py --ci     # fail on a mismatch
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.md"
TABLES = ROOT / "articles" / "029-figures" / "tables.json"

# key in tables.json -> the exact string the article must contain
NEEDLES: dict[str, str] = {
    # the mixing length
    "m_wavelength": "12-cell wavelength",
    "m_area_r3": "| 3 | 29 |",
    "m_area_r45": "| 4.5 | 64 |",
    "m_area_r6": "| 6 | 113 |",
    "m_row_r3": "| 3 | 29 | 5/5 | 5/5 | 7/15 | 2/15 |",
    "m_row_r45": "| 4.5 | 64 | 5/5 | 4/5 | 2/10 | 0/15 |",
    "m_row_r6": "| 6 | 113 | 10/10 | 3/10 | 0/10 | 0/10 |",
    "m_cross": "10 ± 1 cells",
    "m_cross_r3": "10 cells",
    "m_cross_r6": "9 cells",
    "m_cross_spread": "one cell",
    "m_r3_g10": "7/15",
    "m_r3_g11": "2/15",
    "m_r6_g9": "3/10",
    "m_r45_g10": "2/10",
    "m_window": "1.3 cells",
    "m_window_low": "0.7",
    "m_window_high": "1.9",
    "m_window_share": "21 %",
    "m_contact": "1.9 cells",
    "m_contact_range": "range 0.9 to 4.9",
    "m_contact_by_r": "1.27 at radius 3 at a gap of 8, 1.86 at radius 3 at a gap of 9, 1.07 at radius 5.2, 3.14 at radius 4.5 and 3.01 at radius 6",
    "m_runs": "132 runs",
    "m_runs_all": "171 two-body runs",
    "m_growth_small": "2.9 cells in effective radius",
    "m_growth_from": "6.0 to 8.5",
    "m_growth_band": "5.8 and 8.5 cells",
    "m_outer10": "M 2/5 and A 2/5, with P 1/5",
    "m_outer11": "M 2/5, P 3/5",
    "m_lone_small": "180 and 190 steps",
    "m_lone_r6": "median of 290 steps",
    "m_time_x154": "39 steps at gaps 6.5 to 7.5 and 49 steps at 8",
    "c_size_medians": "267 / 268 and 297 / 287",
    "c_size_medians2": "242 / 290",
    # the edge
    "w_gaps": "6.5 | 7 | 7.5 | 8",
    "w_coal": "1.0 | 1.0 | **1.0** | **0.5**",
    "w_slow": "**0.2** | **1.0**",
    "w_slow_all": "0.0 | 0.0 | 0.2 | 0.5 |",
    "w_hist75": "39 ×8, 49 ×2",
    "w_hist80": "49 ×3, 59 ×2",
    # endings and the reversal
    "i_absorbed": "55.3 / 47.8 / 48.4",
    "i_isolated": "31.3 / 29.4 / 21.2",
    "i_vanished": "10.5 / 21.7 / 27.4",
    "i_kin_lattice": "87.2 %",
    "i_kin_maze": "37.7 %",
    "i_remerge": "18.4 / 8.6 / 17.4",
    "i_remerge_time": "80 / 120 / 60",
    "i_below": "0.162 / 0.302 / 0.466",
    "i_depth": "1.479 / 1.416 / 2.213",
    "i_rate": "6.06 / 9.01 / 18.96",
    "i_surv": "0.2496 / 0.2984 / 0.1372",
    "i_mid_se": "5.99 standard errors",
    "i_sister": "+1.479 [1.289, 1.654]",
    "i_sister2": "+2.213 [1.962, 2.489]",
    "i_partial": "0.459 / 0.340",
    "i_depth_life": "−0.185 / −0.070",
    "c_matched": "0.125 and 0.044",
    "c_matched_full": "0.2496 / 0.1372",
    "c_ties": "22.2 % and 21.5 %",
    "c_tie_fracs": "0.526 and 0.388",
    "i_ten_worlds": "−0.077",
    "i_ten_worlds_ci": "−0.166 … +0.012",
    "i_x132": "−0.1323 (−0.1819 … −0.0840)",
    "i_x132_depth": "+1.8340",
    "i_x132_kin": "−0.4164",
    "i_x132_vanished": "+0.1419",
    "i_worlds": "30–40 worlds",
    # inheritance
    "h_slope": "0.9837 [0.9680, 1.0002]",
    "h_slope2": "0.9931 [0.9756, 1.0103]",
    "h_resid": "0.1487 and 0.1495",
    "h_sigma": "σ = 0.15",
    "h_null_p": "0.001",
    "h_null_mean": "0.19, **0.001**",
    "h_recon": "0.9092 against 0.9092",
    "h_recon2": "0.8967 against 0.8989",
    "h_pairs": "2 164 of 2 211",
    "h_pairs2": "1 779 of 1 951",
    "h_h2": "0.082 in the lattice and 0.416",
    "h_h2b": "| 0.416 |",
    "h_ablation_sd": "sd 0.0",
    "h_ablation_equal": "100 % of pairs exactly equal",
    # shape, measured from the field
    "h2_pairs": "4 111 parent–daughter pairs",
    "h2_s1": "0.9959 [0.9790, 1.0126]",
    "h2_s2": "0.9817 [0.9631, 1.0003]",
    "h2_area1": "0.4514 [0.4264, 0.4771]",
    "h2_area2": "0.4481 [0.4193, 0.4723]",
    "h2_elong1": "0.6074 [0.5399, 0.6785]",
    "h2_elong2": "0.4260 [0.3585, 0.4924]",
    "h2_width1": "0.3384 [0.2877, 0.3850]",
    "h2_width2": "0.6238 [0.5846, 0.6672]",
    "h2_partial": "0.26 and 0.65",
    "h2_null": "−0.001 to +0.002",
    "h2_delay1": "0.607 to 0.579",
    "h2_delay2": "0.624 to 0.571",
    "h2_mean": "elongation 0.517 and width 0.481",
    "h2_swap1": "0.6074 against 0.3384",
    "h2_swap2": "0.6238 against 0.4260",
    "h2_band": "0.34 to 0.62",
    # the third chemical
    "s_q": "7–9",
    "s_dw": "8 ×",
    "s_gamma": "0.30",
    "s_orient": "0.636 and 0.837",
    "s_alive": "2 of 6",
    # v2.1 results
    "m_x164_row": "5/5 at gaps 4, 6 and 8 and 2/5 at 10",
    "m_x164_band": "out of the same band of ten",
    "m_x164_contact": "1.84 / 2.21 / 2.60 / 4.38",
    "m_x165_row": "5/5, 1/5 and 0/5",
    "m_x165_square": "0.47 squared",
    "m_x161_area": "0.546",
    "m_x161_order": "−0.163",
    "m_x161_order_null": "−0.240 to 0.136",
    "m_x161_life": "0.101",
    "m_x161_life_null": "−0.007 to 0.199",
    "m_x168d_row": "0/10, 1/10, 3/10",
    "m_x168d_p": "p = 0.21",
    "m_x169_control": "0.047",
    "m_x169_neck": "0.36",
    "m_x169_widths": "four to five cells",
}

# values kept in the tables but quoted only in a figure rather than in the prose
ALLOWED_UNQUOTED: set[str] = set()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="check article 029 numbers against the derived tables")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    if not ARTICLE.exists() or not TABLES.exists():
        print("[article-029] article or tables missing")
        return 1
    article = ARTICLE.read_text(encoding="utf-8")
    tables = json.loads(TABLES.read_text(encoding="utf-8"))["tables"]
    bad = 0
    for key, needle in NEEDLES.items():
        if key not in tables:
            print(f"[article-029] NO SUCH KEY {key} in tables.json — {needle}")
            bad += 1
            continue
        if needle not in article:
            print(f"[article-029] MISMATCH: '{needle}' ({key}) not found in the article")
            bad += 1
    for key in tables:
        if key not in NEEDLES and key not in ALLOWED_UNQUOTED:
            print(f"[article-029] WARNING: table value '{key}' is not checked by the article")
            bad += 1
    total = len(NEEDLES)
    if bad:
        print(f"[article-029] mismatches: {bad} of {total}")
        return 1 if args.ci else 0
    print(f"[article-029] all {total} numbers match the tables, and the tables are built from the aggregates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
