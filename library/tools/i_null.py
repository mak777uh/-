#!/usr/bin/env python
"""Нуль-модель для I Кроу (B-080): I > 0 ожидаемо при демографическом шуме.

`I = Var(w)/mean(w)^2`, где `w` — относительная приспособленность линий (число потомков).
Для случайного числа потомков `I` положительна почти всегда, поэтому `I > 0` не является
свидетельством отбора (Waples & Reed 2023, 10.1086/723889; Waples 2020, 10.1111/evo.14061).

Скрипт отвечает на вопрос: **насколько наблюдённое `I` выше нуль-модели?**

Модель: `n` линий, у каждой потомков ~ Пуассон(`lam`) (базовый вариант) или отрицательно
биномиальное с дисперсией `lam*(1+lam/k)`; `w_i = x_i / mean(x)`;
`I = Var(w)/mean(w)^2`. Считается Монте-Карло; печатаются медиана, 95-й процентиль и
p-значение наблюдённого `I`.

Запуск:
  python library/tools/i_null.py --lines 54 --mean-spores 2.4 --obs-I 0.20
  python library/tools/i_null.py --lines 54 --mean-spores 2.4 --obs-I 0.20 --model nb --k 1.0
"""
from __future__ import annotations

import argparse
import random
import statistics


def simulate(n: int, lam: float, draws: int, model: str, k: float, seed: int) -> list[float]:
    rnd = random.Random(seed)
    out: list[float] = []
    for _ in range(draws):
        if model == "poisson":
            xs = [rnd.poissonvariate(lam) if hasattr(rnd, "poissonvariate") else _poisson(rnd, lam)
                  for _ in range(n)]
        else:
            xs = [_negbin(rnd, lam, k) for _ in range(n)]
        mean = sum(xs) / n if n else 0.0
        if mean <= 0:
            continue
        ws = [x / mean for x in xs]
        mw = sum(ws) / n
        if mw <= 0:
            continue
        var = sum((w - mw) ** 2 for w in ws) / (n - 1) if n > 1 else 0.0
        out.append(var / (mw * mw))
    return out


def _poisson(rnd: random.Random, lam: float) -> int:
    # Для больших lam Кнут под 0-й степенью переполняется: нормальное приближение.
    if lam > 30:
        import math
        u1 = max(rnd.random(), 1e-12)
        u2 = rnd.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return max(0, int(round(lam + math.sqrt(lam) * z)))
    # Кнутовский метод: достаточен для малых lam
    limit, k, p = 2.718281828459045 ** (-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= limit:
            return k
        k += 1


def _negbin(rnd: random.Random, lam: float, k: float) -> int:
    # гамма-пуассон: смесь Пуассона с гамма-параметром
    shape = k
    scale = lam / k if k > 0 else 0.0
    # семплируем гамму через сумму экспонент (только для целых k) или приближение
    if k >= 1 and abs(k - round(k)) < 1e-9:
        g = sum(-scale * (1.0 + 0.0) * _log(rnd) for _ in range(int(round(k))))
    else:
        g = max(1e-9, lam * (1.0 + (rnd.random() - 0.5) / max(k, 1e-9)))
    return _poisson(rnd, max(g, 0.0))


def _log(rnd: random.Random) -> float:
    import math
    return math.log(max(rnd.random(), 1e-12))




def simulate_conditional(cells: list[int], rate: float, draws: int, seed: int) -> list[float]:
    """Нуль с условием на размер линий: X_i ~ Poisson(rate * cells_i), w_i = X_i / cells_i.

    Это правильная нуль-модель для `w = споры/клетки`: шум только в счёте потомков при
    фиксированном размере линии. Без условия шум распределения потомков по линиям
    смешивается с различием размеров.
    """
    rnd = random.Random(seed)
    out: list[float] = []
    n = len(cells)
    if n < 2:
        return out
    for _ in range(draws):
        ws = [_poisson(rnd, max(rate * c, 1e-9)) / c for c in cells]
        mw = sum(ws) / n
        if mw <= 0:
            continue
        var = sum((w - mw) ** 2 for w in ws) / (n - 1)
        out.append(var / (mw * mw))
    return out

def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Нуль-модель I Кроу")
    ap.add_argument("--lines", type=int, required=True, help="число линий с данными")
    ap.add_argument("--mean-spores", type=float, required=True, help="среднее число потомков")
    ap.add_argument("--obs-I", type=float, default=None, help="наблюдённое I (если есть)")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--model", choices=["poisson", "nb"], default="poisson")
    ap.add_argument("--k", type=float, default=1.0, help="параметр формы для nb")
    ap.add_argument("--cells", default=None,
                    help="размеры линий через запятую (условная нуль-модель: шум только в счёте)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    if args.cells:
        cells = [int(x) for x in args.cells.split(",") if x.strip()]
        rate = args.mean_spores
        vals = simulate_conditional(cells, rate, args.draws, args.seed)
        label = f"условная (cells={len(cells)}, rate={rate})"
    else:
        vals = simulate(args.lines, args.mean_spores, args.draws, args.model, args.k, args.seed)
        label = args.model
    if not vals:
        print("нуль-модель вырождена (среднее <= 0) — проверьте --mean-spores")
        return 2
    med = statistics.median(vals)
    p95 = percentile(vals, 0.95)
    print(f"нуль-модель ({label}): линий {args.lines}, среднее {args.mean_spores}, "
          f"розыгрышей {len(vals)}")
    print(f"  I_null: медиана {med:.3f}, 95-й процентиль {p95:.3f}, "
          f"максимум {max(vals):.3f}")
    if args.obs_I is not None:
        p = sum(1 for v in vals if v >= args.obs_I) / len(vals)
        verdict = "ВЫШЕ нуля" if args.obs_I > p95 else "в пределах нуля"
        print(f"  I_obs {args.obs_I:.3f} -> p = {p:.4f}; {verdict} "
              f"(порог 95 %: {p95:.3f})")
        return 0 if args.obs_I > p95 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
