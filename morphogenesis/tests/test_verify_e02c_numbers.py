"""test_verify_e02c_numbers.py — пересчёт чисел из артефактов держится тестом.

Смысл: числа в отчётах и рукописи должны пересчитываться из того, что лежит в
репозитории. Скрипт `scripts/verify_e02c_numbers.py` сверяет сводки с сырыми
строками переписей; здесь проверяется сама арифметика — подсчёт классов и
«устойчивых struct_2» по правилу протокола (последняя четверть ≥ 0.80).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import verify_e02c_numbers as v  # noqa: E402


def row(family: str, cls: str, stable: float, stable_frozen: float | None = None) -> dict:
    out = {"family": family, "frozen_class": cls, "stability_last_quarter": stable}
    if stable_frozen is not None:
        out["stability_frozen_last_quarter"] = stable_frozen
    return out


def test_recount_counts_classes_and_stable_struct2():
    rows = [
        row("fam", "struct_2", 0.95, 0.95),
        row("fam", "struct_2", 0.60, 0.60),   # не устойчив по порогу 0.80
        row("fam", "struct_1", 1.00, 1.00),
        row("other", "uniform_dark", 1.00, 1.00),
    ]
    out = v.recount(rows)
    assert out["fam"]["n"] == 3
    assert out["fam"]["classes"] == {"struct_2": 2, "struct_1": 1}
    assert out["fam"]["stable_fit"] == 1
    assert out["fam"]["stable_frozen"] == 1
    assert out["other"]["classes"] == {"uniform_dark": 1}


def test_recount_without_frozen_field_does_not_fail():
    rows = [row("fam", "struct_2", 1.0)]  # старая перепись: поля frozen нет
    out = v.recount(rows)
    assert out["fam"]["stable_frozen"] == 0
    assert out["fam"]["stable_fit"] == 1


def test_pairs_found_in_repository():
    found = v.pairs()
    assert found, "в каталоге E02c_replication должны быть пары census/summary"
    for stem, census, summary in found:
        assert census.exists()
        assert stem and summary.name.startswith("summary_")


def test_script_passes_on_current_repository():
    """На текущем состоянии репозитория пересчёт обязан сходиться."""
    assert v.main([]) == 0
