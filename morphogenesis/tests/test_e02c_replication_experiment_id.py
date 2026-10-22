"""test_e02c_replication_experiment_id.py — переопределение каталога чекпоинта.

Зачем: чтобы отделить точность обучения от других факторов, один и тот же
рецепт и сид прогоняются дважды (TF32 и FP32). Без переопределения имени второй
прогон писал бы в тот же каталог `E02c_R-9_s<steps>_seed<seed>` и затирал первый —
то есть сравнивать было бы нечего. Тест держит флаг `--experiment-id`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"


def run_dry(extra: list[str]) -> str:
    proc = subprocess.run(
        [sys.executable, "e02c_replication.py", "--seed", "42", "--steps", "4000", "--dry-run", *extra],
        cwd=MORPH,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def test_default_experiment_id_unchanged():
    out = run_dry([])
    assert "experiment_id=E02c_R-9_s4000_seed42" in out


def test_experiment_id_override():
    out = run_dry(["--experiment-id", "E02c_R-9_s4000_seed42_tf32"])
    assert "experiment_id=E02c_R-9_s4000_seed42_tf32" in out
    assert "checkpoint_dir=checkpoints\\E02c_R-9_s4000_seed42_tf32" in out or (
        "checkpoint_dir=checkpoints/E02c_R-9_s4000_seed42_tf32" in out
    )
