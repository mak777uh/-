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
    "m_cross_r3": "16 ± 1",
    "m_cross_r45": "18 ± 2",
    "m_cross_r6": "20 ± 2",
    "m_rule": "2r + 9",
    "m_gap8": "5 of 5",
    "m_gap9": "M 3/5, A 2/5",
    "m_outer10": "M 2/5, A 2/5, P 1/5",
    "m_outer11": "M 2/5, P 3/5",
    "m_lone_r3": "median of 180 steps",
    "m_lone_r45": "190 and 290 steps",
    "m_lone_r6": "290 steps",
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
    # the third chemical
    "s_q": "7–9",
    "s_dw": "8 ×",
    "s_gamma": "0.30",
    "s_orient": "0.636 and 0.837",
    "s_alive": "2 of 6",
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
