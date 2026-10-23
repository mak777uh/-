#!/usr/bin/env python
"""Информационная индивидуальность: I(S(t); S(t+1)) с контролем на тривиальность.

Из литературы (Rajpal et al., 2025): «индивидуальность» можно мерить взаимной
информацией между текущим и следующим состоянием системы, а высший уровень
организации — тем, что группа предсказуема лучше, чем отдельные её части.

Осторожно: у ДЕТЕРМИНИРОВАННОЙ системы I(S(t); S(t+1)) максимальна всегда —
следующее состояние есть функция текущего. Поэтому абсолютное значение метрики
ничего не говорит; нужны контроли:

1. **суррогат** (перестановка во времени) — если MI на суррогате такой же, значит
   временной структуры нет (это шум);
2. **периодичность** — цикл даёт максимум MI, но он тривиален;
3. **сравнение группа vs индивиды** — вот здесь и появляется «higher-order
   individuality», если группа предсказуемее своих частей.

Запуск:
    python scripts/individuality.py
"""
from __future__ import annotations

import numpy as np


def discretize(values: np.ndarray, bins: int = 8) -> np.ndarray:
    """Привести непрерывный сигнал к бинам (для оценки MI по гистограммам)."""
    v = np.asarray(values, dtype=float).reshape(-1)
    if v.size == 0:
        return np.zeros(0, dtype=int)
    lo, hi = float(np.min(v)), float(np.max(v))
    if hi - lo < 1e-12:
        return np.zeros(v.size, dtype=int)
    edges = np.linspace(lo, hi, bins + 1)
    idx = np.clip(np.digitize(v, edges) - 1, 0, bins - 1)
    return idx


def mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 8) -> float:
    """MI между двумя рядами (в битах) по совместной гистограмме."""
    xi, yi = discretize(x, bins), discretize(y, bins)
    if xi.size < 2:
        return 0.0
    joint, _, _ = np.histogram2d(xi, yi, bins=(bins, bins))
    p = joint / joint.sum()
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = (p > 0) & (expected > 0)
    return float(np.sum(p[mask] * np.log2(p[mask] / expected[mask])))


def individuality(series: np.ndarray) -> float:
    """I(S(t); S(t+1)) — «индивидуальность» по временной предсказуемости."""
    s = np.asarray(series, dtype=float).reshape(-1)
    if s.size < 4:
        return 0.0
    return mutual_information(s[:-1], s[1:])


def surrogate_individuality(series: np.ndarray, seed: int = 0) -> float:
    """Контроль: та же серия, но перемешанная во времени (структура разрушена)."""
    rng = np.random.default_rng(seed)
    s = np.asarray(series, dtype=float).reshape(-1).copy()
    rng.shuffle(s)
    return individuality(s)


def periodicity(series: np.ndarray) -> float:
    """Насколько ряд периодичен: максимум нормированной автокорреляции (lag > 0)."""
    s = np.asarray(series, dtype=float).reshape(-1)
    if s.size < 4 or np.std(s) == 0:
        return 0.0
    s = s - s.mean()
    ac = np.correlate(s, s, mode="full")[s.size - 1 :] / (np.dot(s, s))
    return float(np.max(np.abs(ac[1:])))


def _synth(kind: str, n: int = 512, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if kind == "noise":
        return rng.normal(size=n)
    if kind == "periodic":
        return np.sin(np.arange(n) * 2 * np.pi / 7.0)
    if kind == "logistic":
        x = np.empty(n)
        x[0] = 0.4
        for i in range(1, n):
            x[i] = 3.99 * x[i - 1] * (1 - x[i - 1])
        return x
    if kind == "slow_structure":
        base = 0.0
        out = np.empty(n)
        for i in range(n):
            base = 0.98 * base + 0.02 * rng.normal()
            out[i] = base + 0.3 * np.sin(i / 40.0)
        return out
    raise SystemExit(f"неизвестный тип {kind}")


def main() -> int:
    print(f"{'тип':15s} {'MI':>7s} {'суррогат':>9s} {'периодичность':>14s}  вывод")
    for kind in ("noise", "periodic", "logistic", "slow_structure"):
        mi = float(np.mean([individuality(_synth(kind, seed=s)) for s in range(3)]))
        sur = float(np.mean([surrogate_individuality(_synth(kind, seed=s), seed=s) for s in range(3)]))
        per = float(np.mean([periodicity(_synth(kind, seed=s)) for s in range(3)]))
        if mi - sur < 0.05:
            verdict = "нет временной структуры (шум)"
        elif per > 0.9:
            verdict = "тривиальный цикл"
        else:
            verdict = "структура есть (нетривиальная)"
        print(f"{kind:15s} {mi:7.3f} {sur:9.3f} {per:14.3f}  {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

def block_density_grid(mask, block: int = 8):
    """Плотность живого в блоках block x block (для временной MI)."""
    m = np.asarray(mask, dtype=float)
    h, w = m.shape
    h2, w2 = (h // block) * block, (w // block) * block
    return m[:h2, :w2].reshape(h2 // block, block, w2 // block, block).mean(axis=(1, 3))


def temporal_individuality(snapshots, block: int = 8, deltas=(1, 2, 4), bins: int = 8):
    """I(S(t); S(t+dt)) по блочным плотностям, с контролем во времени.

    snapshots: (T, H, W) маски живого. Для каждого dt берём пары (t, t+dt) и считаем
    MI между векторами блочных плотностей. Контроль — перестановка снимков во
    времени: если MI на контроле тот же, временной структуры нет.
    """
    snap = np.asarray(snapshots)
    t_count = snap.shape[0]
    dens = np.array([block_density_grid(s, block).reshape(-1) for s in snap])
    result = {}
    for dt in deltas:
        if t_count <= dt:
            continue
        x = dens[: t_count - dt].reshape(-1)
        y = dens[dt:].reshape(-1)
        mi = mutual_information(x, y, bins)
        order = np.random.default_rng(0).permutation(t_count)
        shuffled = dens[order]
        xs = shuffled[: t_count - dt].reshape(-1)
        ys = shuffled[dt:].reshape(-1)
        result[dt] = {"mi": mi, "control": mutual_information(xs, ys, bins)}
    return result

def group_vs_individual(snapshots, block: int = 8, bins: int = 2) -> dict:
    """Группа предсказуемее своих частей? (Rajpal et al., 2025)

    Индивид = клетка: MI между «жива ли клетка сейчас» и «жива ли через шаг».
    Группа = блок block x block: MI между плотностью блока сейчас и через шаг.
    Оба значения считаем на одних и тех же снимках, поэтому сравнение честное.

    Оговорка: блок — прокси группы; для строгого теста нужны компоненты с
    отслеживанием идентичности. Но если даже по блокам группа не предсказуемее,
    гипотеза о higher-order individuality не поддерживается.
    """
    snap = np.asarray(snapshots).astype(float)
    t_count = snap.shape[0]
    if t_count < 2:
        return {"mi_cell": 0.0, "mi_block": 0.0, "delta": 0.0, "snapshots": t_count}
    # уровень клетки: пары соседних снимков, все клетки
    cell_x = snap[:-1].reshape(-1)
    cell_y = snap[1:].reshape(-1)
    mi_cell = mutual_information(cell_x, cell_y, bins=2)
    # уровень группы: блочные плотности
    dens = np.array([block_density_grid(m, block).reshape(-1) for m in snap])
    block_x = dens[:-1].reshape(-1)
    block_y = dens[1:].reshape(-1)
    # ВАЖНО: сравнение только при одинаковом числе бинов, иначе MI несравнима
    # (у 8 бинов потолок 3 бита, у бинарной клетки 1 бит). По умолчанию — 2 бина.
    mi_block = mutual_information(block_x, block_y, bins=bins)
    return {
        "mi_cell": mi_cell,
        "mi_block": mi_block,
        "delta": mi_block - mi_cell,
        "snapshots": t_count,
    }
