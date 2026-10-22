"""test_tf32_switch.py — переменная MORPH_TF32 выключает TF32, дефолт не меняется.

Зачем: на Ampere+ свёртки по умолчанию идут в TF32 (19 бит мантиссы), а на
Turing (Tesla T4) TF32 нет вовсе — там честный FP32. Значит «тот же рецепт и
тот же сид» на двух стеках считает свёртки с разной точностью, и это первый
подозреваемый в расхождении классов (H-REPRO-4). Чтобы проверить это, нужен
переключатель, который не меняет поведение по умолчанию, — он и тестируется.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import torch  # noqa: E402

import config  # noqa: E402


@pytest.fixture(autouse=True)
def restore_flags():
    saved = (
        torch.backends.cudnn.allow_tf32,
        torch.backends.cuda.matmul.allow_tf32,
    )
    saved_env = os.environ.get("MORPH_TF32")
    yield
    torch.backends.cudnn.allow_tf32, torch.backends.cuda.matmul.allow_tf32 = saved
    if saved_env is None:
        os.environ.pop("MORPH_TF32", None)
    else:
        os.environ["MORPH_TF32"] = saved_env


def test_default_keeps_framework_behaviour():
    os.environ.pop("MORPH_TF32", None)
    report = config.set_seed(42, assert_ready=False)
    assert report["tf32_forced_off"] is False
    assert report["tf32_cudnn"] is True


def test_morph_tf32_zero_disables_tf32():
    os.environ["MORPH_TF32"] = "0"
    report = config.set_seed(42, assert_ready=False)
    assert report["tf32_forced_off"] is True
    assert report["tf32_env"] == "0"
    assert report["tf32_cudnn"] is False
    assert torch.backends.cudnn.allow_tf32 is False
    assert torch.backends.cuda.matmul.allow_tf32 is False


def test_morph_tf32_one_keeps_it_enabled():
    os.environ["MORPH_TF32"] = "1"
    report = config.set_seed(42, assert_ready=False)
    assert report["tf32_forced_off"] is False
    assert torch.backends.cudnn.allow_tf32 is True
