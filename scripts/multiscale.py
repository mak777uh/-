#!/usr/bin/env python
"""Мультимасштабная метрика: насколько «разная» структура на разных масштабах.

Зачем: в литературе (MSPD, arXiv:2606.17091) сложность предлагается мерить тем,
насколько организация различается на разных масштабах наблюдения. Здесь — дешёвый
прокси для статических масок: усредняем локальную плотность блоками разного размера
и смотрим, насколько статистика меняется от масштаба к масштабу.

Важно: это ПРОКСИ, а не MSPD. Настоящий MSPD считает расхождение локальных законов
перехода во времени (окна наблюдения), для него нужны серии состояний, а не одна
маска. Прокси нужен, чтобы (а) проверить, что идея вообще различает известные типы,
(б) не тащить в код непроверенную метрику как «главную».

Запуск:
    python scripts/multiscale.py            # самопроверка на синтетических масках
"""
from __future__ import annotations

import numpy as np


def block_density(mask: np.ndarray, block: int) -> np.ndarray:
    """Плотность живого в блоках block×block (среднее, поле обрезается по кратности)."""
    m = np.asarray(mask, dtype=float)
    h, w = m.shape
    h2, w2 = (h // block) * block, (w // block) * block
    m = m[:h2, :w2]
    return m.reshape(h2 // block, block, w2 // block, block).mean(axis=(1, 3))


def scale_divergence(mask: np.ndarray, scales=(2, 4, 8, 16)) -> float:
    """Насколько разброс локальной плотности меняется с масштабом.

    Для каждого масштаба считаем стандартное отклонение плотности по блокам.
    Метрика = нормированный разброс этих std между масштабами:
      0 — структура выглядит одинаково на всех масштабах (тривиально/случайно),
      >0 — организация масштабно-зависима.
    """
    stats = []
    for block in scales:
        dens = block_density(mask, block)
        if dens.size < 2:
            continue
        stats.append(float(np.std(dens)))
    if len(stats) < 2:
        return 0.0
    arr = np.asarray(stats)
    mean = float(arr.mean())
    if mean == 0.0:
        return 0.0
    return float(np.std(arr) / mean)


def _synth(kind: str, n: int = 64, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if kind == "random":
        return rng.random((n, n)) < 0.53
    if kind == "dust":
        mask = np.zeros((n, n), dtype=bool)
        idx = rng.integers(0, n, size=(400, 2))
        mask[idx[:, 0], idx[:, 1]] = True
        return mask
    if kind == "blob":
        mask = np.zeros((n, n), dtype=bool)
        mask[16:48, 16:48] = True
        return mask
    if kind == "sponge":
        # плотное тело с одиночными порами: шахматный шум внутри области
        mask = np.zeros((n, n), dtype=bool)
        mask[8:56, 8:56] = True
        holes = rng.random((n, n)) < 0.15
        mask = mask & ~holes
        return mask
    raise SystemExit(f"неизвестный тип {kind}")


def main() -> int:
    print(f"{'тип':10s} {'расхождение по масштабам':>24s}")
    for kind in ("random", "dust", "blob", "sponge"):
        values = [scale_divergence(_synth(kind, seed=s)) for s in range(5)]
        print(f"{kind:10s} {np.mean(values):24.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Результат самопроверки (23.10): прокси НЕ различает шум и структуру как надо —
# random 0.725, dust 0.732, sponge 0.232, blob 0.000. То есть белый шум получает
# МАКСИМАЛЬНОЕ значение, а настоящая губка — среднее. Это отрицательный результат
# и важное ограничение: любая метрика сложности обязана давать шуму низкий балл.
# Следствие: MSPD надо считать по ВРЕМЕННЫМ сериям (расхождение локальных законов
# перехода в разных окнах наблюдения), а не по статичной маске; для этого в пруду
# нужно логировать снимки состояний.
