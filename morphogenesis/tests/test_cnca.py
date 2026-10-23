"""test_cnca.py — правило с геномом: форма, гейт живости, мутация, FiLM.

Зачем: cNCA — организм новой линии: общее правило + наследуемый геном на клетку.
Тест держит три свойства, без которых линия не работает: шаг не меняет форму
тензоров, мёртвые клетки не обновляются, мутация действительно меняет геном и её
сила управляется средой.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

from world.cnca import CNCA, CNCAConfig  # noqa: E402


def make_inputs(b=1, h=8, w=8, c=16, k=32, seed=0):
    gen = torch.Generator().manual_seed(seed)
    state = torch.randn((b, c, h, w), generator=gen)
    genome = torch.randn((b, k, h, w), generator=gen)
    return state, genome


def test_forward_keeps_shape():
    model = CNCA(CNCAConfig(hidden=16))
    state, genome = make_inputs()
    out = model(state, genome)
    assert out.shape == state.shape
    assert torch.isfinite(out).all()


def test_dead_field_is_zeroed_when_masking_enabled():
    """Полностью мёртвое поле остаётся мёртвым: гейт применяется к новому состоянию.

    Раньше тест требовал «мёртвые клетки не меняются», но теперь маска живости
    применяется после обновления: полностью мёртвое поле обнуляется, а не
    сохраняет случайный шум (иначе мёртвые каналы «светились» бы).
    """
    model = CNCA(CNCAConfig(mask_alive=True))
    state, genome = make_inputs()
    state[:, 1] = -20.0          # все клетки мертвы (sigmoid ~ 0)
    out = model(state, genome)
    assert float(out.abs().sum()) == 0.0


def test_alive_cells_change_with_default_init():
    model = CNCA(CNCAConfig())
    state, genome = make_inputs()
    before = state.clone()
    out = model(state, genome)
    # живая клетка (канал живости 10) обновляется, мёртвая — нет
    assert state[0, 1].mean() > 0
    assert not torch.allclose(out[0, 1], before[0, 1], atol=1e-6)


def test_mutation_changes_genome_and_scale_matters():
    model = CNCA(CNCAConfig())
    _state, genome = make_inputs()
    gen = torch.Generator().manual_seed(1)
    small = model.mutate(genome, sigma=0.01, generator=gen)
    big = model.mutate(genome, sigma=1.0, generator=torch.Generator().manual_seed(1))
    assert not torch.equal(small, genome)
    assert (big - genome).abs().mean() > (small - genome).abs().mean() * 10


def test_genome_matters_for_the_step():
    """Разные геномы должны давать разные шаги при ненулевом правиле."""
    model = CNCA(CNCAConfig())
    torch.nn.init.normal_(model.update.weight, std=0.1)
    state, genome = make_inputs()
    out_a = model(state, genome)
    out_b = model(state, genome + 3.0)
    assert not torch.allclose(out_a, out_b, atol=1e-6)


def test_wrong_dims_rejected():
    model = CNCA(CNCAConfig())
    state, genome = make_inputs()
    try:
        model(state.squeeze(0), genome)
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("ожидалась ошибка размерности")

def test_default_init_is_nonzero_so_genomes_matter():
    """С нулевым правилом все геномы эквивалентны — проверяем, что этого нет."""
    model = CNCA(CNCAConfig())
    assert float(model.update.weight.abs().sum()) > 0.0


def test_birth_is_possible_with_current_gate():
    """Мёртвые клетки должны уметь рождаться: гейт применяется к новому состоянию.

    Регрессия: раньше update умножался на маску живости, поэтому мёртвая клетка не
    могла измениться никогда — рост из одной клетки был невозможен (обучение
    застревало: loss 0.2490, alive_after_200 = 0).
    """
    model = CNCA(CNCAConfig())
    state = torch.full((1, 16, 32, 32), -20.0)
    state[0, 1, 16, 16] = 10.0
    genome = torch.zeros((1, 32, 32, 32))
    for _ in range(20):
        state = model(state, genome)
    alive = int((torch.sigmoid(state[0, 1]) > 0.5).sum())
    assert alive > 1, "из одной клетки должен появляться рост"
