"""Регрессия: один и тот же сид даёт один и тот же pop_time (CPU, короткий прогон).

Найдено 24.10 при настройке CI-канарейки: два прогона `run_pond.py --seed 7` расходились
на шагах 30-40. Причина — часть случайности шла через глобальные ГПСЧ, не засеянные сидом
прогона. Патч: `run_pond.main()` сеет torch/random/numpy, а `torch.rand` в шаге с
`update_probability < 1` получает генератор прогона.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MORPH = Path(__file__).resolve().parents[1]


def run_once(out: Path) -> int:
    cmd = [sys.executable, "world/run_pond.py", "--device", "cpu", "--steps", "60",
           "--grid", "32", "--seed", "7", "--out", str(out)]
    proc = subprocess.run(cmd, cwd=MORPH, capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stderr[-1500:]
    return json.loads(out.read_text(encoding="utf-8"))["summary"]["pop_time"]


def test_same_seed_same_pop_time(tmp_path):
    first = run_once(tmp_path / "a.json")
    second = run_once(tmp_path / "b.json")
    assert first == second, f"один и тот же сид дал разные pop_time: {first} и {second}"
    assert first > 0
