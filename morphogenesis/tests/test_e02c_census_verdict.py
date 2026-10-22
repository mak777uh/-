"""Вердикт переписи E02c: H-R1/R2/H-R3 применимы только к полному дизайну.

Узкая перепись (фильтр `--families`, например повтор одного seed42) не должна
получать метку гипотезы: «одно подтверждённое семейство из одного» — это не H-R2.
Иначе артефакт, честный по числам, врёт про своё место в протоколе.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS_PY = ROOT / "morphogenesis" / "e02c_census.py"


def load_census():
    morph = ROOT / "morphogenesis"
    if str(morph) not in sys.path:
        sys.path.insert(0, str(morph))
    spec = importlib.util.spec_from_file_location("e02c_census_module", CENSUS_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_partial_census_has_no_hypothesis_label() -> None:
    census = load_census()
    verdict, applicable = census.census_verdict(["E02c_R-9_s2000_seed42"], 1)
    assert verdict == "n/a_partial_census"
    assert applicable is False


def test_full_design_three_of_three_gives_h_r1() -> None:
    census = load_census()
    verdict, applicable = census.census_verdict(["a", "b", "c"], 3)
    assert applicable is True
    assert verdict.startswith("H-R1")


def test_full_design_one_of_three_gives_h_r2() -> None:
    census = load_census()
    verdict, applicable = census.census_verdict(["a"], 3)
    assert applicable is True
    assert verdict.startswith("H-R2")


def test_full_design_none_gives_h_r3() -> None:
    census = load_census()
    verdict, applicable = census.census_verdict([], 3)
    assert applicable is True
    assert verdict.startswith("H-R3")


def test_family_stats_separates_fit_relative_and_frozen_stability() -> None:
    """Две метрики устойчивости считаются отдельно и не подменяют друг друга."""
    census = load_census()

    def run(stability_fit: float, stability_frozen: float) -> dict:
        return {
            "family": "fam",
            "frozen_class": "struct_2",
            "final": {"alive_fraction": 0.5},
            "stability_last_quarter": stability_fit,
            "stability_frozen_last_quarter": stability_frozen,
        }

    rows = [
        run(1.0, 0.9),
        run(0.9, 0.85),
        run(0.6, 0.95),
        run(0.1, 0.2),
    ]
    stats = census.family_stats(rows, "fam")
    assert stats["struct_2"] == 4
    assert stats["struct_2_stable"] == 2  # fit-relative >= 0.80
    assert stats["struct_2_stable_frozen"] == 3  # замороженная >= 0.80
