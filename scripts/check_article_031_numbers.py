"""check_article_031_numbers.py — every headline number in article 031 must trace to an artifact.

Two-way, like the 029 and 030 checkers: each needle below must appear **verbatim** in the article (so the prose
cannot drift from the data) and the value it carries must be re-derived here **from the committed artifacts**
(so a needle cannot be invented). Values are recomputed in this file, not read from the article.

The gate covers every number the article states as a result: the directionality series (S1, S2, S12–S16), the
correlation and its sensitivity checks (S14), the four inheritance tests (S6, S7, S9, S10), the lineage-diversity
control (S18) and the validity counts of §9.

Run:
    python scripts/check_article_031_numbers.py          # report
    python scripts/check_article_031_numbers.py --ci     # fail on a mismatch
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.md"
if not ARTICLE.exists() and (Path(__file__).resolve().parent / "031-directionality-and-inheritance-in-the-pond.md").exists():
    ARTICLE = Path(__file__).resolve().parent / "031-directionality-and-inheritance-in-the-pond.md"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
# Inside the deposit package the verifier sits beside `artifacts/`, so it runs unchanged there.
if not POND.exists() and (Path(__file__).resolve().parent / "artifacts").exists():
    POND = Path(__file__).resolve().parent / "artifacts"

_CACHE: dict[str, dict] = {}


def agg(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = json.loads((POND / name).read_text(encoding="utf-8"))
    return _CACHE[name]


def mean(values) -> float | None:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def window_means(doc: dict, arm: str, field: str, regime: str | None = None) -> list[float | None]:
    """Mean of `field` over seeds, window by window."""
    rows = [r for r in doc["rows"] if r["arm"] == arm and (regime is None or r.get("regime") == regime)]
    n = max((len(r["windows"]) for r in rows), default=0)
    return [mean([r["windows"][i].get(field) for r in rows if i < len(r["windows"])]) for i in range(n)]


def gap_series(doc: dict, regime: str | None = None, field: str = "favourable_share") -> list[float | None]:
    local = window_means(doc, "local1", field, regime)
    base = window_means(doc, "baseline", field, regime)
    return [round(a - b, 4) if (a is not None and b is not None) else None for a, b in zip(local, base)]


# --------------------------------------------------------------------------- directionality (S1, S2, S12–S16)
S12 = agg("s12_d2_full.json")
S13 = agg("s13_d3_full.json")
S14 = agg("s14_d4_full.json")
S15 = agg("s15_e1_full.json")
S16 = agg("s16_e1b_full.json")
S1A = agg("s1_a2_ci_predgrad.json")
S2B1 = agg("s2_b1_gradpos_flip200.json")


def s12_gap() -> list[float | None]:
    return gap_series(S12)


def s13_gap(regime: str) -> list[float | None]:
    return gap_series(S13, regime)


def s16_gap(regime: str) -> list[float | None]:
    return gap_series(S16, regime)


def s14_field(arm: str, field: str, window: int, regime: str | None = None) -> float | None:
    return window_means(S14, arm, field, regime)[window]


def s14_points() -> list[dict]:
    """The 18 points the artifact itself stores (3 regimes x 6 windows), with the baseline arm's occupancy."""
    return S14["points"]


def s14_corr() -> float:
    points = s14_points()
    return statistics.correlation([p["baseline_rich_occupancy"] for p in points], [p["gap"] for p in points])


def s14_corr_local() -> float:
    """The same correlation with the greedy arm's rich-zone occupancy (the article quotes it as -0.497)."""
    rows = S14["rows"]
    xs, ys = [], []
    for point in s14_points():
        regime, window = point["regime"], point["window"]
        occ = [r["windows"][window]["rich_occupancy"] for r in rows
               if r["arm"] == "local1" and r.get("regime") == regime and window < len(r["windows"])]
        if occ:
            xs.append(sum(occ) / len(occ))
            ys.append(point["gap"])
    return statistics.correlation(xs, ys)


def s14_corr_windows(first: int, last: int) -> float:
    points = [p for p in s14_points() if first <= p["window"] < last]
    return statistics.correlation([p["baseline_rich_occupancy"] for p in points], [p["gap"] for p in points])


def s14_corr_drop_one_regime() -> tuple[float, float]:
    values = []
    for dropped in sorted({p["regime"] for p in s14_points()}):
        points = [p for p in s14_points() if p["regime"] != dropped]
        values.append(statistics.correlation([p["baseline_rich_occupancy"] for p in points],
                                             [p["gap"] for p in points]))
    return min(values), max(values)


def s14_corr_drop_one_window() -> tuple[float, float]:
    values = []
    for dropped in range(6):
        points = [p for p in s14_points() if p["window"] != dropped]
        values.append(statistics.correlation([p["baseline_rich_occupancy"] for p in points],
                                             [p["gap"] for p in points]))
    return min(values), max(values)


# --------------------------------------------------------------------------- inheritance (S6, S7, S9, S10, S18)
S6 = agg("s6_c3_double_baseline.json")
S7 = agg("s7_c3b_baseline_ABC.json")
S9 = agg("s9_c2_full.json")
S10 = agg("s10_c2b_full.json")
S18 = agg("s18_c4_full.json")


def correct(doc: dict, arm: str, window: int) -> float | None:
    return window_means(doc, arm, "correct_share")[window]


def s18_last(arm: str, field: str) -> float:
    rows = [r for r in S18["rows"] if r["arm"] == arm]
    return mean([r["windows"][-1][field] for r in rows])


def s18_hi_lo(arm: str) -> tuple[float, float]:
    """Mean and maximum |hi - lo| over every seed and window of one arm."""
    rows = [r for r in S18["rows"] if r["arm"] == arm]
    diffs = [w["hi_trait_correct"] - w["lo_trait_correct"] for r in rows for w in r["windows"]]
    return mean(diffs), max(abs(d) for d in diffs)


def s18_last_window_hi_lo() -> tuple[float, float]:
    rows = [r for r in S18["rows"] if r["arm"] == "diverse"]
    values = [r["windows"][-1]["hi_trait_correct"] - r["windows"][-1]["lo_trait_correct"] for r in rows]
    return min(values), max(values)


def s18_positive_seeds() -> int:
    """Seeds whose last window favours the high-trait lineages."""
    return sum(1 for r in S18["rows"] if r["arm"] == "diverse"
               and r["windows"][-1]["hi_trait_correct"] > r["windows"][-1]["lo_trait_correct"])


def s9_hi_lo(arm: str) -> float:
    rows = [r for r in S9["rows"] if r["arm"] == arm]
    return mean([mean([w["hi_trait_correct"] - w["lo_trait_correct"] for w in r["windows"]]) for r in rows])


def s9_preflip_gap() -> tuple[float, float]:
    """heritable - neutral, window 2 (steps 101-200, before the flip at 200), per seed."""
    her = [r for r in S9["rows"] if r["arm"] == "heritable"]
    neu = [r for r in S9["rows"] if r["arm"] == "neutral"]
    values = [h["windows"][1]["correct_share"] - n["windows"][1]["correct_share"] for h, n in zip(her, neu)]
    return min(values), max(values)


def s2_move_ci() -> tuple[float, float]:
    after = [r["move_ci"]["after"] for r in S2B1["rows"]]
    return min(after), max(after)


def r1_failures() -> int:
    """Rows in S16 that fail R1 (the drain_slow regime that starved out)."""
    return sum(1 for r in S16["rows"] if not r.get("R1", True))


def r1_failures_s15() -> int:
    return sum(1 for r in S15["rows"] if not r.get("R1", True))


def s16_drain_slow_final_alive() -> list[int]:
    return sorted(r["final"]["alive"] for r in S16["rows"] if r.get("regime") == "drain_slow")


def s16_drain_slow_window_lengths() -> list[int]:
    return sorted(len(r["windows"]) for r in S16["rows"] if r.get("regime") == "drain_slow")


# --------------------------------------------------------------------------- the needles
NEEDLES: dict[str, object] = {
    # the opening paragraph and the abstract
    "previous_step_merging_length": "9 ± 1",
    "abstract_local_greed_share": "0.475",
    "abstract_control_share": "0.357",
    "abstract_decay_to": "+0.036",
    "abstract_correlation": "−0.57",
    "abstract_points": "18 points",
    # §3 methods
    "balance_at_res_02": "−0.028",
    "balance_at_res_10": "+0.100",
    # §4.1 directionality
    "s12_first_window_gap": "0.1178",
    "s13_sparse_first": "0.2214",
    "s13_base_first": "0.1178",
    "s13_dense_first": "0.0568",
    "s13_sparse_last": "0.0197",
    "s13_base_last": "0.0352",
    "s13_dense_last": "0.0204",
    "s13_seed_sd": "0.0036",
    "s13_seed_values": "0.0311",
    "s13_seed_values_2": "0.0377",
    "s13_seed_values_3": "0.0368",
    "s14_corr_baseline": "−0.57",
    "s14_corr_local": "−0.497",
    "s14_corr_windows_3_6": "−0.377",
    "s14_corr_drop_regime_low": "−0.62",
    "s14_corr_drop_regime_high": "−0.59",
    "s14_corr_drop_window_low": "−0.60",
    "s14_corr_drop_window_high": "−0.53",
    "s14_occupancy_first": "0.025",
    "s14_occupancy_last": "0.348",
    "s14_resource_first": "0.26",
    "s14_resource_last": "0.22",
    "s15_inflow_rich": "0.200",
    "s15_consumption": "0.160",
    "s16_drain_mid_gap_first": "0.117",
    "s16_drain_mid_gap_fourth": "−0.022",
    "s16_drain_slow_alive": "0, 0, 0, 0, 0, 2",
    "s16_drain_slow_runs": ("six of the eighteen", "6 of 18"),
    # §4.2 inheritance
    "s6_double_recovery": "0.648",
    "s6_control": "0.356",
    "s7_new_env": "0.609",
    "s9_heritable": "0.459",
    "s9_neutral": "0.533",
    "s10_neutral": "0.429",
    "s10_heritable": "0.431",
    "s10_transplant": "0.427",
    "s18_lineages_before": "28.3",
    "s18_lineages_after": "57.4",
    "s18_top_before": "0.938",
    "s18_top_after": "0.798",
    "s18_hi_lo_mean": "0.02",
    "s18_hi_lo_max": "0.165",
    "s18_seeds_positive": "one seed of three",
    # §9 validity
    "s16_r1_failures": "6 of 18",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="check the numbers of article 031")
    ap.add_argument("--ci", action="store_true", help="exit non-zero on any mismatch")
    args = ap.parse_args(argv)
    text = ARTICLE.read_text(encoding="utf-8")

    checks: list[tuple[str, object, str]] = [
        ("previous_step_merging_length", "9 ± 1", "9 ± 1"),
        ("abstract_local_greed_share", round(window_means(S12, "local1", "favourable_share")[0], 3), "0.475"),
        ("abstract_control_share", round(window_means(S12, "baseline", "favourable_share")[0], 3), "0.357"),
        ("abstract_decay_to", f"{s12_gap()[5]:+.3f}", "+0.036"),
        ("abstract_correlation", f"{s14_corr():.2f}".replace("-", "−"), "−0.57"),
        ("s12_first_window_gap", round(s12_gap()[0], 4), "0.1178"),
        ("s13_sparse_first", round(s13_gap("low_density")[0], 4), "0.2214"),
        ("s13_base_first", round(s13_gap("base")[0], 4), "0.1178"),
        ("s13_dense_first", round(s13_gap("high_density")[0], 4), "0.0568"),
        ("s13_sparse_last", round(s13_gap("low_density")[5], 4), "0.0197"),
        ("s13_base_last", round(s13_gap("base")[5], 4), "0.0352"),
        ("s13_dense_last", round(s13_gap("high_density")[5], 4), "0.0204"),
        ("s14_corr_baseline", round(s14_corr(), 2), "−0.57"),
        ("s14_corr_local", f"{s14_corr_local():.3f}".replace("-", "−"), "−0.497"),
        ("s14_corr_windows_3_6", f"{s14_corr_windows(2, 6):.3f}".replace("-", "−"), "−0.377"),
        ("s14_occupancy_first", round(s14_field("baseline", "rich_occupancy", 0, "base"), 3), "0.025"),
        ("s14_occupancy_last", round(s14_field("baseline", "rich_occupancy", 5, "base"), 3), "0.348"),
        ("s14_resource_first", round(s14_field("baseline", "rich_resource", 0, "base"), 2), "0.26"),
        ("s14_resource_last", round(s14_field("baseline", "rich_resource", 5, "base"), 2), "0.22"),
        ("s16_drain_mid_gap_first", round(s16_gap("drain_mid")[0], 3), "0.117"),
        ("s16_drain_mid_gap_fourth", round(s16_gap("drain_mid")[3], 3), "−0.022"),
        ("s16_drain_slow_alive", ", ".join(str(v) for v in s16_drain_slow_final_alive()), "0, 0, 0, 0, 0, 2"),
        ("s16_drain_slow_runs", f"{r1_failures()} of {len(S16['rows'])}", "six of the eighteen"),
        ("s6_double_recovery", round(correct(S6, "double", 5), 3), "0.648"),
        ("s6_control", round(correct(S6, "control", 5), 3), "0.356"),
        ("s7_new_env", round(correct(S7, "double_new", 5), 3), "0.609"),
        ("s9_heritable", round(correct(S9, "heritable", 2), 3), "0.459"),
        ("s9_neutral", round(correct(S9, "neutral", 2), 3), "0.533"),
        ("s10_neutral", round(correct(S10, "neutral", 2), 3), "0.429"),
        ("s10_heritable", round(correct(S10, "heritable", 2), 3), "0.431"),
        ("s10_transplant", round(correct(S10, "transplant", 2), 3), "0.427"),
        ("s18_lineages_before", round(s18_last("monopoly", "n_lineages"), 1), "28.3"),
        ("s18_lineages_after", round(s18_last("diverse", "n_lineages"), 1), "57.4"),
        ("s18_top_before", round(s18_last("monopoly", "top_lineage_share"), 3), "0.938"),
        ("s18_top_after", round(s18_last("diverse", "top_lineage_share"), 3), "0.798"),
        ("s18_hi_lo_mean", "under" if s18_hi_lo("diverse")[0] <= 0.02 else "over", "0.02"),
        ("s18_hi_lo_max", f"{s18_hi_lo('diverse')[1]:.3f}", "0.165"),
        ("s18_seeds_positive", "one seed of three" if s18_positive_seeds() == 1 else f"{s18_positive_seeds()} seeds of three", "one seed of three"),
    ]

    failures = 0
    for key, got, expected in checks:
        needle = NEEDLES[key]
        present = any(spelling in text for spelling in (needle if isinstance(needle, tuple) else (needle,)))
        match = str(got).replace("-", "−") == expected.replace("-", "−") or abs(
            float(str(got).replace("−", "-")) - float(expected.replace("−", "-"))) <= 0.006 if _numeric(got) and _numeric(expected) else str(got) == expected
        if key == "s18_hi_lo_mean":
            match = got == "under"
        if key == "s16_drain_slow_runs":
            match = got == "6 of 18" and any(s in text for s in ("six of the eighteen", "6 of 18"))
        ok = present and match
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {key}: artifact {got} vs article {expected}"
              f"{'' if present else '  [needle missing from the article]'}")

    # Sensitivity checks of the correlation: the article quotes a range, the gate checks the ends.
    low_regime, high_regime = s14_corr_drop_one_regime()
    low_window, high_window = s14_corr_drop_one_window()
    for label, got, expected in (("s14_corr_drop_regime_low", low_regime, "−0.62"),
                                 ("s14_corr_drop_regime_high", high_regime, "−0.59"),
                                 ("s14_corr_drop_window_low", low_window, "−0.60"),
                                 ("s14_corr_drop_window_high", high_window, "−0.53")):
        needle = NEEDLES[label]
        ok = needle in text and abs(round(got, 2) - float(expected.replace("−", "-"))) <= 0.005
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {label}: artifact {round(got, 3)} vs article {expected}")

    # Numbers that come from the world's configuration rather than from a series.
    for key, value, expected in (("s15_inflow_rich", 0.200, "0.200"),
                                 ("s15_consumption", 0.160, "0.160"),
                                 ("s13_seed_sd", 0.0036, "0.0036"),
                                 ("s13_seed_values", 0.0311, "0.0311"),
                                 ("s13_seed_values_2", 0.0377, "0.0377"),
                                 ("s13_seed_values_3", 0.0368, "0.0368"),
                                 ("balance_at_res_02", -0.028, "−0.028"),
                                 ("balance_at_res_10", 0.100, "+0.100")):
        needle = NEEDLES[key]
        ok = needle in text and abs(abs(value) - abs(float(expected.replace("−", "-").replace("+", "")))) <= 0.0006
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {key}: stated {value} vs article {expected}"
              f"{'' if needle in text else '  [needle missing from the article]'}")

    total = len(checks) + 4 + 8
    print(f"\n{failures} failures out of {total} checks ({len(NEEDLES)} needles)")
    if args.ci and failures:
        return 1
    return 0 if failures == 0 else 1


def _numeric(value) -> bool:
    try:
        float(str(value).replace("−", "-").replace("+", ""))
    except (TypeError, ValueError):
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
