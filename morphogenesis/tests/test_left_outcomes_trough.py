"""test_left_outcomes_trough.py — правило «два пика с провалом» (H-AB-10).

Критерий H-AB-10 формальный: два локальных максимума (счёт бина больше обоих
соседей), между ними бин-провал со счётом ≤ 50 % меньшего пика, и каждый пик
≥ 6 развёрток. Такой критерий легко «подогнать» после прогона, поэтому он
проверяется тестом на синтетических гистограммах — до и независимо от прогона.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "morphogenesis" / "experiments" / "E02b_morphospace" / "scripts" / "e02b_left_outcomes.py"


def load_module():
    spec = importlib.util.spec_from_file_location("left_outcomes_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_two_peaks_with_deep_trough_confirms():
    module = load_module()
    counts = [0, 0, 8, 2, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    found = module.find_trough(counts)
    assert found is not None
    assert found["peak_bins"] == [2, 5]
    assert found["peak_counts"] == [8, 7]
    # между пиками бины 3 и 4 со счётом 2 и 0: провал — минимум, то есть бин 4
    assert found["trough_bin"] == 4
    assert found["trough_count"] == 0


def test_unimodal_is_refuted():
    module = load_module()
    counts = [0, 1, 3, 6, 9, 7, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert module.find_trough(counts) is None


def test_shallow_trough_is_refuted():
    module = load_module()
    # между пиками 8 и 7 бины 5 и 6: 5 > 0.5*7, значит «провал» неглубокий
    counts = [0, 0, 8, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert module.find_trough(counts) is None


def test_small_peaks_are_ignored():
    module = load_module()
    # пики по 5 < PEAK_MIN=6 — шум, а не режимы
    counts = [0, 0, 5, 1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert module.find_trough(counts) is None


def test_adjacent_bins_are_not_a_trough():
    module = load_module()
    # два соседних пика без бина между ними — не два режима
    counts = [0, 7, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert module.find_trough(counts) is None


def test_ties_are_not_peaks():
    module = load_module()
    # равенство соседей: бин не считается пиком (правило зафиксировано до прогона)
    counts = [0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0]
    assert module.find_trough(counts) is None


def test_histogram_covers_zero_and_one():
    module = load_module()
    counts, edges = module.histogram([0.0, 1.0, 0.5], bins=20)
    assert len(counts) == 20 and len(edges) == 21
    assert counts[0] == 1 and counts[-1] == 1
    assert sum(counts) == 3
