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
