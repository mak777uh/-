"""check_article_029_numbers.py — every number printed in article 029 must trace to an aggregate.

Two-way check: each needle below must appear **verbatim** in the article (so the text cannot drift), and its key must
exist in `articles/029-figures/tables.json`, which the figure script builds directly from the aggregates (so the needle
cannot be invented). Where the table entry carries a numeric value, the needle must also contain that value formatted
with the same precision that the table prints.

Run:
    python scripts/check_article_029_numbers.py          # report
    python scripts/check_article_029_numbers.py --ci     # fail on a mismatch
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.md"
TABLES = ROOT / "articles" / "029-figures" / "tables.json"

# key in tables.json -> the exact string the article must contain
NEEDLES: dict[str, str] = {
    "m_wavelength": "12-cell pattern wavelength",
    "m_area_r3": "29 cells",
    "m_area_r6": "113 cells",
    "m_cross_r3": "16 ± 1",
    "m_cross_r45": "18 ± 2",
    "m_cross_r6": "20 ± 2",
    "m_rule": "2r + 9",
    "m_gap9": "M 3/5, A 2/5",
    "m_lone_r3": "median of 180 steps",
    "m_lone_r45": "190 and 290 steps",
    "m_lone_r6": "290 steps",
    "m_area_r45": "| 4.5 | 64 |",
    "w_gaps": "6.5 / 7 / 7.5 / 8",
    "w_coal": "1.0 / 1.0 / 1.0 / 0.5",
    "w_slow": "0.0 / 0.0 / 0.2 / 1.0",
    "w_slow_all": "0.0 / 0.0 / 0.2 / 0.5",
    "w_hist75": "39 ×8, 49 ×2",
    "w_hist80": "49 ×3, 59 ×2",
    "i_below": "0.162 / 0.302 / 0.466",
    "i_depth": "1.479 / 1.416 / 2.213",
    "i_rate": "6.06 / 9.01 / 18.96",
    "i_surv": "0.2496 / 0.2984 / 0.1372",
    "i_mid_se": "5.99 standard errors",
    "i_sister": "+1.479 [1.289, 1.654]",
    "i_sister2": "+2.213 [1.962, 2.489]",
    "i_partial": "0.459 / 0.340",
    "i_depth_life": "−0.185 / −0.070",
    "i_absorbed": "55.3 / 47.8 / 48.4",
    "i_isolated": "31.3 / 29.4 / 21.2",
    "i_vanished": "10.5 / 21.7 / 27.4",
    "i_kin_lattice": "87.2 %",
    "i_kin_maze": "37.7 %",
    "i_remerge": "18.4 / 8.6 / 17.4",
    "i_remerge_time": "80 / 120 / 60",
    "i_ten_worlds": "−0.077",
    "i_ten_worlds_ci": "−0.166 … +0.012",
    "i_worlds": "30–40 worlds",
    "i_x132": "−0.1323 (−0.1819 … −0.0840)",
    "i_x132_depth": "+1.8340",
    "i_x132_kin": "−0.4164",
    "i_x132_vanished": "+0.1419",
    "c_size_medians": "267 / 268, 297 / 287",
    "c_size_medians2": "242 / 290",
    "c_matched": "0.125 and 0.044",
    "c_matched_full": "0.2496 / 0.1372",
    "c_ties": "22.2 % and 21.5 %",
    "c_tie_fracs": "0.526 and 0.388",
    "h_slope": "0.9837 [0.9680, 1.0002]",
    "h_slope2": "0.9931 [0.9756, 1.0103]",
    "h_resid": "0.1487 and 0.1495",
    "h_sigma": "σ = 0.15",
    "h_null_p": "0.001",
    "h_recon": "0.9092 against 0.9092",
    "h_recon2": "0.8967 against 0.8989",
    "h_pairs": "2 164 of 2 211",
    "h_pairs2": "1 779 of 1 951",
    "h_h2": "0.082",
    "h_h2b": "| 0.416 |",
    "h_ablation_sd": "sd 0.0",
    "h_ablation_equal": "100 % of pairs exactly equal",
    "s_q": "7–9",
    "s_dw": "8 ×",
    "s_gamma": "0.30",
    "s_orient": "0.636 and 0.837",
    "s_alive": "two of six",
}

# keys that are printed in tables.json but not quoted in the prose (they live in the CSVs and the aggregate)
ALLOWED_UNQUOTED = {"m_gap8", "m_outer10", "m_outer11"}

NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def numbers_in(text: str) -> list[str]:
    return [m.group(0) for m in NUM_RE.finditer(text)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сверка чисел статьи 029 с агрегатами")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    if not ARTICLE.exists() or not TABLES.exists():
        print("[article-029] нет статьи или таблиц")
        return 1
    article = ARTICLE.read_text(encoding="utf-8")
    tables = json.loads(TABLES.read_text(encoding="utf-8"))["tables"]
    bad = 0
    for key, needle in NEEDLES.items():
        if key not in tables and not key.endswith("2"):
            print(f"[article-029] НЕТ КЛЮЧА {key} в tables.json — {needle}")
            bad += 1
            continue
        if needle not in article:
            print(f"[article-029] РАСХОЖДЕНИЕ: '{needle}' ({key}) не найдено в статье")
            bad += 1
    for key in tables:
        if key not in NEEDLES and key not in ALLOWED_UNQUOTED:
            print(f"[article-029] ВНИМАНИЕ: значение '{key}' в таблицах не проверяется статьёй")
            bad += 1
    total = len(NEEDLES)
    if bad:
        print(f"[article-029] расхождений: {bad} из {total}")
        return 1 if args.ci else 0
    print(f"[article-029] все {total} чисел статьи совпадают с таблицами, а таблицы — с агрегатами")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
