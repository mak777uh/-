"""Ритмичность β и доминирующий период по логу активности пруда.

Из литературы (Doering et al., 2024): коллективное поведение характеризуется
доминирующим периодом и «ритмичностью» β = высота главного пика спектра / средняя
амплитуда. Здесь считаем по ряду активности (рождения + смерти на шаг) из уже
сохранённых прогонов — без новых запусков.

Запуск:
    python scripts/rhythmicity.py <файл с логом pond_*.json>
"""
from __future__ import annotations

import json
import sys

import numpy as np


def activity_series(log: list[dict]) -> np.ndarray:
    """Активность на шаг: рождения + смерти (что-то произошло)."""
    return np.array([float(d.get("births_this_step", 0) + d.get("died", 0) * 0) for d in log])


def died_series(log: list[dict]) -> np.ndarray:
    """Кумулятивные смерти, переведённые в прирост за шаг (по журналу)."""
    deaths = [int(d.get("died", 0)) for d in log]
    if not deaths:
        return np.zeros(0)
    deltas = np.diff([0] + deaths)
    return np.maximum(deltas, 0).astype(float)


def rhythmicity(series: np.ndarray) -> dict:
    """Доминирующий период и β = пик / среднее по амплитудному спектру."""
    s = np.asarray(series, dtype=float).reshape(-1)
    if s.size < 16 or np.std(s) == 0:
        return {"period": None, "beta": 0.0, "n": int(s.size)}
    s = s - s.mean()
    spec = np.abs(np.fft.rfft(s))
    freqs = np.fft.rfftfreq(s.size, d=1.0)
    if spec.size < 3:
        return {"period": None, "beta": 0.0, "n": int(s.size)}
    # игнорируем нулевую частоту (постоянная составляющая)
    idx = int(np.argmax(spec[1:]) + 1)
    peak = float(spec[idx])
    mean_amp = float(spec[1:].mean()) or 1e-12
    period = float(1.0 / freqs[idx]) if freqs[idx] > 0 else None
    return {"period": period, "beta": peak / mean_amp, "n": int(s.size)}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    data = json.loads(open(argv[1], encoding="utf-8").read())
    log = data.get("log", [])
    if not log:
        print("в файле нет лога")
        return 1
    act = activity_series(log)
    deaths = died_series(log)
    print(f"шагов в логе: {len(log)}")
    for name, series in (("активность (рождения)", act), ("смерти за шаг", deaths)):
        r = rhythmicity(series)
        period = "—" if r["period"] is None else f"{r['period']:.1f}"
        print(f"  {name:22s} β={r['beta']:6.2f}  период={period}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
