"""test_field_metrics.py — общее измерительное кодо линии поля считает то, что заявлено.

Зачем: 02.11 один и тот же дефект жил в двух анализах — клетка глоббилась одним префиксом, и «двадцать миров» (восемь X85 плюс
двенадцать X87) читались как двенадцать. `cell_files()` введён именно против этого класса: клетка описывается **списком**
префиксов, и тест фиксирует, что число миров совпадает с зарегистрированным.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import field_metrics as fm  # noqa: E402


def test_cell_files_counts_the_registered_worlds():
    """Решёточная клетка — двадцать миров, и её префиксы нельзя схлопнуть в один."""
    both = fm.cell_files(("x85", "x87"), 0.025)
    only_x85 = fm.cell_files("x85", 0.025)
    only_x87 = fm.cell_files("x87", 0.025)
    assert len(both) == len(only_x85) + len(only_x87)
    assert len(only_x85) == 8 and len(only_x87) == 12, (len(only_x85), len(only_x87))
    assert len(both) == 20
    assert len(fm.cell_files(("x88",), 0.040)) == 20


def test_angular_separates_forcing_from_morphology():
    """Чистая шахматка 12 клеток: мощность на диагоналях, период — по осям."""
    g, q = 96, 8
    y = np.arange(g)[:, None]
    x = np.arange(g)[None, :]
    checker = (np.sin(2 * np.pi * q * y / g) * np.cos(2 * np.pi * q * x / g) + 1.0) / 2.0
    got = fm.angular(checker)
    assert got["symmetry"] is not None and got["symmetry"] > 0.5, got
    assert got["field_std"] > 0.01


def test_angular_refuses_a_dead_field():
    """Мёртвое поле не даёт числа: иначе шум прибора читается как морфология."""
    assert fm.angular(np.zeros((96, 96)))["symmetry"] is None


def test_half_life_is_the_geometric_ratio():
    """Известная геометрия: rho падает вдвое за лаг, значит полураспад равен одному делению."""
    got = fm.half_life([0.5, 0.25, 0.125])
    assert got["fittable"] and got["lambda"] == pytest.approx(0.5, abs=1e-9)
    assert got["half_life"] == pytest.approx(1.0, abs=1e-6)


def test_half_life_is_unfittable_without_positive_ratios():
    assert fm.half_life([0.4, -0.02, 0.01])["fittable"] is False
