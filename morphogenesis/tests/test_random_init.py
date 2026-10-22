"""test_random_init.py — базлайн random-init должен ломать структуру, не масштаб.

Зачем: `untrained_current_arch` отделяет «архитектуру без обучения», но не
отделяет «масштаб весов». Второй контроль — та же архитектура со случайными
весами в том же масштабе (протокол v1.1, §5). Тест держит два свойства: режим
`shuffle` сохраняет распределение значений, режим `rms` сохраняет среднее и СКО.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import make_random_init as mri  # noqa: E402


def make_state():
    torch.manual_seed(0)
    return {
        "conv.weight": torch.randn(8, 4, 3, 3) * 0.2,
        "dense.weight": torch.randn(16, 64) * 0.05,
        "dense.bias": torch.randn(16) * 0.01,
        "counter": torch.tensor([5], dtype=torch.int64),
    }


def test_shuffle_preserves_multiset_and_shapes():
    sd = make_state()
    gen = torch.Generator().manual_seed(1)
    out = mri.randomize_state_dict(sd, "shuffle", gen)
    for name, value in sd.items():
        assert out[name].shape == value.shape
        if torch.is_floating_point(value) and value.numel() >= 2:
            assert not torch.equal(out[name], value), f"{name}: значения не перемешаны"
            assert torch.allclose(
                torch.sort(out[name].reshape(-1)).values.sort().values,
                torch.sort(value.reshape(-1)).values,
            ), f"{name}: распределение изменилось"
        else:
            assert torch.equal(out[name], value), f"{name}: служебный тензор изменён"


def test_rms_keeps_mean_and_std():
    sd = make_state()
    gen = torch.Generator().manual_seed(2)
    out = mri.randomize_state_dict(sd, "rms", gen)
    for name in ("conv.weight", "dense.weight"):
        value, new = sd[name], out[name]
        assert new.shape == value.shape
        # среднее нового тензора — случайная величина со стандартной ошибкой
        # std/sqrt(n); поэтому сравниваем не жёстко, а в пределах 3 сигм.
        n = value.numel()
        se = float(value.std()) / (n**0.5)
        assert abs(float(new.mean()) - float(value.mean())) <= 3 * se + 1e-6
        assert abs(float(new.std()) - float(value.std())) / float(value.std()) < 0.05


def test_integer_tensors_untouched():
    sd = make_state()
    gen = torch.Generator().manual_seed(3)
    out = mri.randomize_state_dict(sd, "rms", gen)
    assert torch.equal(out["counter"], sd["counter"])


def test_bad_mode_rejected():
    sd = make_state()
    gen = torch.Generator().manual_seed(4)
    try:
        mri.randomize_state_dict(sd, "nonsense", gen)
    except SystemExit as exc:
        assert "shuffle" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("ожидался SystemExit на неизвестный режим")
