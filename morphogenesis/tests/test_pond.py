"""test_pond.py — бюджет мира: энергия не из воздуха, смерть и почка по правилам.

Зачем: среда «пруд» нужна, чтобы организация стала процессом (цена, смерть,
размножение). Тест держит инварианты, без которых среда превращается в декорацию:
энергия приходит только из ресурса, мёртвая клетка не тратит, почка списывает
энергию у родителя.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

from world.pond import Pond, PondConfig  # noqa: E402


def test_energy_comes_only_from_resource():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.1, update_cost=0.0,
                   repair_cost=0.0, damage_rate=0.0, noise=0.0))
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[3, 3] = True
    pond.seed_life(mask, energy=0.5)
    before_res = float(pond.state.resource.sum())
    before_energy = float(pond.state.energy.sum())
    pond.step_cells()
    after_res = float(pond.state.resource.sum())
    after_energy = float(pond.state.energy.sum())
    # энергия выросла ровно на столько, сколько ушло из ресурса
    assert abs((after_energy - before_energy) - (before_res - after_res)) < 1e-6


def test_dead_cells_do_not_spend():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.0, update_cost=0.5,
                   repair_cost=0.0, damage_rate=0.0, noise=0.0))
    pond.seed_life(torch.zeros((8, 8), dtype=torch.bool), energy=1.0)  # никто не жив
    before = float(pond.state.energy.sum())
    pond.step_cells()
    assert float(pond.state.energy.sum()) == before
    assert pond.state.alive.sum() == 0


def test_starved_cell_dies_and_returns_energy_to_zero():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.0, update_cost=0.5,
                   repair_cost=0.0, damage_rate=0.0, noise=0.0))
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2, 2] = True
    pond.seed_life(mask, energy=0.2)
    pond.step_cells()
    assert not bool(pond.state.alive[2, 2])
    assert float(pond.state.energy[2, 2]) == 0.0


def test_old_cell_dies_of_age():
    pond = Pond(PondConfig(grid=8, resource_regen=1.0, baseline_income=0.01,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           max_age=3, noise=0.0))
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[1, 1] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(6):
        pond.regenerate()
        pond.step_cells()
    assert not bool(pond.state.alive[1, 1])


def test_budding_requires_mass_and_energy():
    pond = Pond(PondConfig(grid=16, resource_regen=1.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           budding_mass=64, budding_cost=2.0, noise=0.0))
    small = torch.zeros((16, 16), dtype=torch.bool)
    small[4:6, 4:6] = True          # 4 клетки
    pond.seed_life(small, energy=10.0)
    assert pond.find_buds() == []

    big = torch.zeros((16, 16), dtype=torch.bool)
    big[4:12, 4:12] = True          # 64 клетки
    pond.seed_life(big, energy=10.0)
    buds = pond.find_buds()
    assert len(buds) == 1


def test_bud_transfers_energy_and_spawns_alive_cell():
    pond = Pond(PondConfig(grid=16, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           budding_mass=64, budding_cost=4.0, spore_cells=1, noise=0.0))
    parent = torch.zeros((16, 16), dtype=torch.bool)
    parent[4:12, 4:12] = True
    pond.seed_life(parent, energy=10.0)
    energy_before = float(pond.state.energy.sum())
    child = pond.bud(parent)
    assert int(child.sum()) == 1
    assert int(pond.state.born) == 1
    # бюджет мира не вырос: энергия только переехала
    assert float(pond.state.energy.sum()) <= energy_before + 1e-6
    assert bool(pond.state.alive[child])


def test_snapshot_has_expected_fields():
    pond = Pond(PondConfig(grid=8, noise=0.0))
    snap = pond.snapshot()
    for key in ("step", "alive_cells", "energy_total", "resource_total", "born", "died"):
        assert key in snap


def test_spore_does_not_overlap_parent_and_is_adjacent():
    pond = Pond(PondConfig(grid=16, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, budding_mass=64, budding_cost=4.0,
                           spore_cells=2, damage_rate=0.0, noise=0.0))
    parent = torch.zeros((16, 16), dtype=torch.bool)
    parent[4:12, 4:12] = True
    pond.seed_life(parent, energy=10.0)
    child = pond.bud(parent)
    assert child is not None
    assert int(child.sum()) == 2
    # спора не занимает клетку родителя
    assert not bool((child & parent).any())
    # и стоит рядом с ним
    neigh = torch.zeros_like(parent)
    padded = torch.zeros((18, 18), dtype=torch.bool)
    padded[1:-1, 1:-1] = parent
    neigh |= padded[:-2, 1:-1] | padded[2:, 1:-1] | padded[1:-1, :-2] | padded[1:-1, 2:]
    assert bool((child & neigh).any())


def test_damage_accumulates_and_kills_without_age():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=1.0,
                           damage_max=3, max_age=10**6, noise=0.0))
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[3, 3] = True
    pond.seed_life(mask, energy=100.0)
    for _ in range(3):
        pond.step_cells()
    assert not bool(pond.state.alive[3, 3])


def test_catastrophe_drops_resource():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, noise=0.0,
                           catastrophe_period=10, catastrophe_duration=2,
                           catastrophe_strength=0.9))
    pond.state.resource = torch.full((8, 8), 1.0)
    pond.state.step = 0
    pond.regenerate()
    assert float(pond.state.resource.sum()) < 10.0
    pond.state.step = 5
    pond.regenerate()
    assert float(pond.state.resource.sum()) == 64.0 * 0.1 + 0.0 or float(pond.state.resource.sum()) < 64.0 * 0.5


def test_throughput_counter_grows():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.1,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0, noise=0.0))
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=1.0)
    pond.step_cells()
    assert pond.state.consumed_total > 0.0
    snap = pond.snapshot()
    assert "consumed_total" in snap and "damage_mean" in snap
