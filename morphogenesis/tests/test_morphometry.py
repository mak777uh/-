"""test_morphometry.py — периметр, размерность границы и случайный базлайн.

Зачем: у `struct_2` бинарная маска совпала с маской живости, поэтому вопрос «где
хранится форма» сводится к геометрии маски. Тест держит три чистые функции,
которые считают эту геометрию без GPU: периметр, box-counting размерность и
статистику случайной маски той же плотности.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import morphometry as mm  # noqa: E402


def test_perimeter_of_empty_and_full_mask():
    empty = np.zeros((8, 8), dtype=bool)
    full = np.ones((8, 8), dtype=bool)
    assert mm.mask_perimeter(empty) == 0
    # у полной маски граница — только внешняя рамка, 4*8 = 32 ребра
    assert mm.mask_perimeter(full) == 32


def test_perimeter_of_single_pixel():
    mask = np.zeros((8, 8), dtype=bool)
    mask[4, 4] = True
    # 4 стороны одного пикселя — внутри поля, край не задет
    assert mm.mask_perimeter(mask) == 4


def test_perimeter_grows_with_islands():
    mask = np.zeros((16, 16), dtype=bool)
    mask[4, 4] = True
    one = mm.mask_perimeter(mask)
    mask[10, 10] = True
    two = mm.mask_perimeter(mask)
    assert two == 2 * one


def test_boundary_pixels_of_square():
    mask = np.zeros((8, 8), dtype=bool)
    mask[2:6, 2:6] = True  # квадрат 4x4
    boundary = mm.boundary_pixels(mask)
    assert boundary.sum() == 12  # периметр квадрата в пикселях
    assert boundary[2, 2] and boundary[3, 2]
    assert not boundary[3, 3]


def test_box_dimension_of_line_like_and_area_like():
    line = np.zeros((64, 64), dtype=bool)
    line[32, :] = True
    area = np.zeros((64, 64), dtype=bool)
    area[8:56, 8:56] = True
    d_line = mm.box_counting_dimension(line)
    d_area = mm.box_counting_dimension(area)
    assert 0.7 < d_line < 1.4
    assert 1.5 < d_area < 2.2


def test_random_baseline_is_between_extremes():
    stats = mm.random_mask_baseline((64, 64), 0.5, draws=20, seed=3)
    assert stats["perimeter_mean"] > 0
    assert 1.0 < stats["box_dim_mean"] < 2.2
    assert stats["perimeter_std"] > 0


def test_random_baseline_density_changes_perimeter():
    sparse = mm.random_mask_baseline((64, 64), 0.1, draws=10, seed=1)
    dense = mm.random_mask_baseline((64, 64), 0.5, draws=10, seed=1)
    assert dense["perimeter_mean"] > sparse["perimeter_mean"]


def test_isoperimetric_ratio_circle_vs_fractal():
    # квадрат 4x4: площадь 16, периметр 16 -> 4*pi*16/256 = 0.785
    assert abs(mm.isoperimetric_ratio(16, 16) - 0.7854) < 0.01
    # изрезанная граница при той же площади даёт меньшее значение
    assert mm.isoperimetric_ratio(16, 64) < 0.2
    assert mm.isoperimetric_ratio(0, 0) != mm.isoperimetric_ratio(0, 0)  # nan


def test_expected_random_perimeter_matches_simulation():
    shape = (64, 64)
    for density in (0.1, 0.5):
        analytic = mm.expected_random_perimeter(shape, density)
        simulated = mm.random_mask_baseline(shape, density, draws=40, seed=7)["perimeter_mean"]
        assert abs(analytic - simulated) / analytic < 0.05


def test_local_density_is_fraction_of_alive_neighbours():
    mask = np.zeros((5, 5), dtype=bool)
    mask[2, 2] = True
    dens = mm.local_density(mask)
    # у самой клетки все 8 соседей мертвы
    assert dens[2, 2] == 0.0
    # у соседа сверху ровно один живой сосед из 8
    assert abs(dens[1, 2] - 1 / 8) < 1e-9
    # вдали — ноль
    assert dens[0, 0] == 0.0
