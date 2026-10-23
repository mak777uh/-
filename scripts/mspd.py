#!/usr/bin/env python
"""MSPD: расхождение локальных законов перехода в разных временных окнах.

Смысл (по arXiv:2606.17091): система сложна, если её локальная динамика меняется
от окна к окну. Здесь закон перехода оценивается как совместное распределение
«плотность блока сейчас → плотность того же блока через шаг», окна — по времени.

Важно: окно должно быть КОРОЧЕ времени памяти среды (у пруда это ~120–140 шагов,
измерено отдельно), иначе окна независимы и метрика обнулится.

Sanity check (обязателен, иначе метрика не идёт в статью):
  шум          -> низкое расхождение (законы одинаковы и тривиальны);
  цикл         -> низкое расхождение (один закон повторяется);
  нестационар  -> высокое расхождение (законы реально меняются).

Запуск:
    python scripts/mspd.py            # самопроверка на синтетике
"""
from __future__ import annotations

import numpy as np


def block_density(mask: np.ndarray, block: int = 8) -> np.ndarray:
    m = np.asarray(mask, dtype=float)
    h, w = m.shape
    h2, w2 = (h // block) * block, (w // block) * block
    return m[:h2, :w2].reshape(h2 // block, block, w2 // block, block).mean(axis=(1, 3))


def transition_law(dens: np.ndarray, t0: int, t1: int, bins: int = 8) -> np.ndarray:
    """Совместное распределение (density_t, density_t+1) в окне [t0, t1)."""
    x = dens[t0 : t1 - 1].reshape(-1)
    y = dens[t0 + 1 : t1].reshape(-1)
    joint, _, _ = np.histogram2d(x, y, bins=bins, range=[[0, 1], [0, 1]])
    total = joint.sum()
    return joint / total if total else joint


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Расхождение Дженсена–Шеннона между двумя распределениями (в битах)."""
    p = np.asarray(p, dtype=float).reshape(-1)
    q = np.asarray(q, dtype=float).reshape(-1)
    p = p / p.sum() if p.sum() else p
    q = q / q.sum() if q.sum() else q
    m = 0.5 * (p + q)
    eps = 1e-12

    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log2((a[mask] + eps) / (b[mask] + eps))))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def mspd(dens_series: np.ndarray, window: int = 40, bins: int = 8) -> dict:
    """MSPD по серии блочных плотностей (T, n_blocks).

    Возвращает среднее попарное JS-расхождение между законами соседних окон
    и полную таблицу для диагностики.
    """
    dens = np.asarray(dens_series, dtype=float)
    t_count = dens.shape[0]
    starts = list(range(0, max(t_count - window, 1), window))
    laws = [transition_law(dens, s, min(s + window, t_count), bins) for s in starts]
    laws = [law for law in laws if law.sum() > 0]
    if len(laws) < 2:
        return {"mspd": float("nan"), "windows": len(laws), "pairs": 0}
    values = [js_divergence(laws[i], laws[i + 1]) for i in range(len(laws) - 1)]
    return {
        "mspd": float(np.mean(values)),
        "windows": len(laws),
        "pairs": len(values),
        "values": [float(v) for v in values],
    }


def _synth(kind: str, n_steps: int = 240, grid: int = 32, seed: int = 0) -> np.ndarray:
    """Синтетические траектории масок для проверки метрики."""
    rng = np.random.default_rng(seed)
    out = np.zeros((n_steps, grid, grid), dtype=bool)
    if kind == "noise":
        for t in range(n_steps):
            out[t] = rng.random((grid, grid)) < 0.5
    elif kind == "cycle":
        # стабильный узор, который мягко пульсирует по площади
        for t in range(n_steps):
            radius = 10 + 3 * np.sin(2 * np.pi * t / 20)
            yy, xx = np.ogrid[:grid, :grid]
            out[t] = (yy - grid / 2) ** 2 + (xx - grid / 2) ** 2 < radius**2
    elif kind == "nonstationary":
        # «чирп»: частота пульсаций растёт со временем, закон перехода меняется
        # непрерывно (у стационарного цикла закон был бы одинаковым во всех окнах)
        yy, xx = np.ogrid[:grid, :grid]
        phase = 0.0
        for t in range(n_steps):
            period = 24.0 - 18.0 * t / max(n_steps - 1, 1)   # от 24 к 6 шагам
            phase += 2 * np.pi / period
            radius = 10 + 4 * np.sin(phase)
            out[t] = (yy - grid / 2) ** 2 + (xx - grid / 2) ** 2 < radius**2
    else:
        raise SystemExit(f"неизвестный тип {kind}")
    return out


def main() -> int:
    results: dict[str, float] = {}
    print(f"{'тип':15s} {'MSPD':>7s} {'окон':>5s}")
    for kind in ("noise", "cycle", "nonstationary"):
        values = []
        for seed in range(3):
            traj = _synth(kind, seed=seed)
            dens = np.array([block_density(m).reshape(-1) for m in traj])
            values.append(mspd(dens, window=40)["mspd"])
        mean = float(np.mean(values))
        results[kind] = mean
        print(f"{kind:15s} {mean:7.4f} {3:5d}")
    # критерий не «абсолютный порог», а порядок: нестационарное должно быть
    # заметно выше стационарных контролей
    baseline = max(results.get("noise", 0.0), results.get("cycle", 0.0))
    check = results.get("nonstationary", 0.0) > max(3.0 * baseline, 0.02)
    print()
    print(f"порядок: нестационар {results.get('nonstationary', 0):.4f} против "
          f"контролей {baseline:.4f} -> {'ОК' if check else 'ПРОВАЛ'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
