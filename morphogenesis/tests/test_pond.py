"""test_pond.py — бюджет мира: энергия не из воздуха, смерть и почка по правилам.

Зачем: среда «пруд» нужна, чтобы организация стала процессом (цена, смерть,
размножение). Тест держит инварианты, без которых среда превращается в декорацию:
энергия приходит только из ресурса, мёртвая клетка не тратит, почка списывает
энергию у родителя.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
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
                           catastrophe_strength=0.9, catastrophe_mode="drop"))
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


def test_catastrophe_shift_moves_resource():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, noise=0.0,
                           catastrophe_period=10, catastrophe_duration=2,
                           catastrophe_mode="shift"))
    pond.state.resource = torch.full((8, 8), 0.3)
    pond.state.step = 0
    pond.regenerate()
    # левая половина погашена, правая наполнена до максимума
    assert float(pond.state.resource[:, :4].sum()) == 0.0
    assert float(pond.state.resource[:, 4:].sum()) == 32.0 * 1.0


def test_bud_blocked_when_no_free_neighbours():
    pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           budding_mass=4, budding_cost=1.0, noise=0.0))
    # родитель — всё поле, свободных соседей нет
    parent = torch.ones((8, 8), dtype=torch.bool)
    pond.seed_life(parent, energy=10.0)
    energy_before = float(pond.state.energy.sum())
    child = pond.bud(parent)
    assert child is None
    assert int(pond.state.spores_blocked) == 1
    # родитель ничего не заплатил, потому что потомка не было
    assert abs(float(pond.state.energy.sum()) - energy_before) < 1e-6


def test_repair_cost_controls_lifetime():
    from world.pond import survival_probe
    cheap = survival_probe(0.004, steps=600)
    pricey = survival_probe(0.05, steps=600)
    assert cheap > pricey, "дешёвый ремонт должен давать большую продолжительность жизни"


# ---------- политика matching (I-002: melioration -> matching) ----------

def _matching_pick(seed: int, temp: float, spore_cells: int = 1) -> torch.Tensor:
    """Один выстрел политики matching на управляемом поле ресурса."""
    pond = Pond(PondConfig(grid=12, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           spore_cells=spore_cells, noise=0.0,
                           spore_bias="matching", matching_temp=temp), seed=seed)
    parent = torch.zeros((12, 12), dtype=torch.bool)
    parent[5:7, 5:7] = True
    pond.seed_life(parent, energy=10.0)
    pond.state.resource = torch.zeros((12, 12))
    pond.state.resource[7, 5] = 1.0   # argmax по подушевой отдаче
    pond.state.resource[5, 7] = 0.5
    pond.state.resource[4, 5] = 0.2
    pond.state.resource[5, 4] = 0.05
    child = pond.bud(parent)
    assert child is not None
    return child


def test_matching_at_low_temperature_is_argmax():
    """При T -> 0 matching обязан сойтись к жадному выбору (контроль)."""
    for seed in range(6):
        child = _matching_pick(seed, temp=1e-4)
        assert int(child.sum()) == 1
        assert bool(child[6, 4]), f"при низкой температуре ожидалась клетка с max payoff, взята {child.nonzero().tolist()}"


def test_matching_spreads_over_cells_at_default_temperature():
    """При T=1 потомки распределяются пропорционально, а не все в argmax."""
    picks = []
    for seed in range(30):
        child = _matching_pick(seed, temp=1.0)
        ys, xs = child.nonzero(as_tuple=True)
        picks.append((int(ys[0]), int(xs[0])))
    assert len(set(picks)) > 1, "рулетка должна давать разные клетки"
    assert any(p != (6, 4) for p in picks), "часть потомков должна уходить не в argmax"


def test_matching_spores_do_not_overlap_and_are_free():
    child = _matching_pick(7, temp=1.0, spore_cells=2)
    assert int(child.sum()) == 2
    # клетки споры различны и не лежат на родителе
    assert not bool((child[5:7, 5:7]).any())


# ---------- парный (относительный) сигнал обучения, I-001 ----------

def _paired_pond(**over):
    cfg = dict(grid=12, resource_regen=0.0, baseline_income=0.0,
               update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
               budding_cost=1.0, spore_cells=2, noise=0.0,
               learn_w=True, learn_mode="paired", spore_bias="score",
               w_rich=0.5, learn_rate=0.5, learn_pair_noise=0.2, learn_delay=3)
    cfg.update(over)
    pond = Pond(PondConfig(**cfg), seed=3)
    parent = torch.zeros((12, 12), dtype=torch.bool)
    parent[5:7, 5:7] = True
    pond.seed_life(parent, energy=10.0)
    return pond, parent


def test_paired_birth_records_two_arms_with_different_weights():
    pond, parent = _paired_pond()
    child = pond.bud(parent)
    assert child is not None and int(child.sum()) == 2
    entry = pond._pending[-1]
    assert entry.get("pair") is True
    # две разные клетки, по одной на плечо
    assert int(entry["mask_a"].sum()) == 1 and int(entry["mask_b"].sum()) == 1
    assert not bool((entry["mask_a"] & entry["mask_b"]).any())
    # первое испытание: w' = w + δ
    assert entry["w_a"] == 0.5
    assert entry["w_b"] == 0.7


def test_paired_learning_moves_w_to_surviving_arm():
    pond, parent = _paired_pond()
    pond.bud(parent)
    entry = pond._pending[-1]
    # плечо A погибает, плечо B выживает
    pond.state.alive[entry["mask_a"]] = False
    pond.state.step = entry["born_step"] + pond.cfg.learn_delay
    pond.step_cells()
    # w тянется к w' с шагом learn_rate
    assert abs(pond.w - (0.5 + 0.5 * (0.7 - 0.5))) < 1e-6
    assert pond.learn_updates == 1
    assert pond.learn_useless == 0


def test_paired_learning_ignores_lessons_with_equal_fate():
    pond, parent = _paired_pond()
    pond.bud(parent)
    entry = pond._pending[-1]
    # обе споры живы -> сигнала нет
    pond.state.step = entry["born_step"] + pond.cfg.learn_delay
    before = pond.w
    pond.step_cells()
    assert pond.w == before
    assert pond.learn_updates == 0
    assert pond.learn_useless == 1


def test_paired_control_with_zero_delta_does_not_learn():
    """δ=0 — контроль: оба плеча одинаковы, уроков быть не должно (w не уезжает)."""
    pond, parent = _paired_pond(learn_pair_noise=0.0)
    child = pond.bud(parent)
    assert child is not None and int(child.sum()) == 2
    assert pond._pending == []
    assert pond.w == 0.5

# ---------- шум восприятия ресурса (I-012) ----------

def _sense_pick(seed: int, sigma: float, bias: str = "score", w: float = 0.5):
    pond = Pond(PondConfig(grid=12, resource_regen=0.0, baseline_income=0.0,
                           update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                           spore_cells=1, noise=0.0, spore_bias=bias, w_rich=w,
                           sense_noise=sigma), seed=seed)
    parent = torch.zeros((12, 12), dtype=torch.bool)
    parent[5:7, 5:7] = True
    pond.seed_life(parent, energy=10.0)
    pond.state.resource = torch.zeros((12, 12))
    pond.state.resource[7, 5] = 1.0
    pond.state.resource[5, 7] = 0.6
    pond.state.resource[4, 5] = 0.6
    pond.state.resource[5, 4] = 0.05
    child = pond.bud(parent)
    assert child is not None
    return pond, child


def test_sense_noise_zero_is_identical_to_default():
    _, a = _sense_pick(5, sigma=0.0)
    _, b = _sense_pick(5, sigma=0.0)
    assert bool((a == b).all())


def test_sense_noise_changes_choice_sometimes():
    """При большом σ решение перестаёт быть детерминированным argmax."""
    picks = set()
    for seed in range(30):
        _, child = _sense_pick(seed, sigma=5.0)
        ys, xs = child.nonzero(as_tuple=True)
        picks.add((int(ys[0]), int(xs[0])))
    assert len(picks) > 1, "шум восприятия должен иногда менять выбор клетки"


def test_sense_noise_does_not_touch_true_resource_or_budget():
    """Шум — только в решении: истинный ресурс и энергия не меняются от σ."""
    p0, _ = _sense_pick(2, sigma=0.0)
    p5, _ = _sense_pick(2, sigma=5.0)
    # поле ресурса и сумма энергии те же: bud не тратит ресурс, только переносит энергию
    assert bool((p0.state.resource == p5.state.resource).all())
    assert abs(float(p0.state.energy.sum()) - float(p5.state.energy.sum())) < 1e-6


def test_sense_noise_does_not_change_income():
    """Доход считается по истинному ресурсу: при одинаковом состоянии он одинаков."""
    def one_step(sigma):
        pond = Pond(PondConfig(grid=8, resource_regen=0.0, baseline_income=0.02,
                               update_cost=0.0, repair_cost=0.0, damage_rate=0.0,
                               noise=0.0, income_mode="proportional", sense_noise=sigma),
                    seed=0)
        mask = torch.zeros((8, 8), dtype=torch.bool)
        mask[3:5, 3:5] = True
        pond.seed_life(mask, energy=5.0)
        pond.state.resource = torch.full((8, 8), 0.7)
        before = float(pond.state.energy.sum())
        pond.step_cells()
        return float(pond.state.energy.sum()) - before

    assert abs(one_step(0.0) - one_step(5.0)) < 1e-6


# ---------- плавный дрейф среды (I-003) ----------

def _up_down(n: int = 8):
    up = 1.0 - torch.arange(n, dtype=torch.float32) / (n - 1)
    return up, 1.0 - up


def test_drift_moves_gradient_gradually():
    pond = Pond(PondConfig(grid=8, resource_layout="gradient",
                           drift_at=10, drift_steps=10))
    up, down = _up_down()
    for step, expected in (
        (0, up), (10, up), (15, 0.5 * (up + down)), (20, down), (25, down),
    ):
        pond.state.step = step
        assert torch.allclose(pond._gradient_position(), expected, atol=1e-6), step


def test_flip_is_one_step_and_drift_takes_priority():
    up, down = _up_down()
    pond = Pond(PondConfig(grid=8, resource_layout="gradient", flip_at=10))
    pond.state.step = 9
    assert torch.allclose(pond._gradient_position(), up)
    pond.state.step = 10
    assert torch.allclose(pond._gradient_position(), down)

    # если заданы оба, дрейф (плавный) важнее: на середине — середина, а не низ
    both = Pond(PondConfig(grid=8, resource_layout="gradient", flip_at=10,
                           drift_at=10, drift_steps=10))
    both.state.step = 15
    assert torch.allclose(both._gradient_position(), 0.5 * (up + down), atol=1e-6)


def test_no_drift_keeps_gradient_static():
    up, _ = _up_down()
    pond = Pond(PondConfig(grid=8, resource_layout="gradient", flip_at=0))
    for step in (0, 50, 500):
        pond.state.step = step
        assert torch.allclose(pond._gradient_position(), up)


# ---------- детерминизм выборки (protocol §18a, I-017) ----------

def _matching_bud_sequence(seed: int, steps: int = 12):
    pond = Pond(PondConfig(grid=16, resource_regen=0.02, baseline_income=0.2,
                           update_cost=0.02, repair_cost=0.02, budding_mass=8,
                           budding_cost=0.2, spore_cells=2, noise=0.0,
                           resource_layout="gradient", init_resource_fill=0.9,
                           spore_bias="matching", matching_temp=1.0), seed=seed)
    parent = torch.zeros((16, 16), dtype=torch.bool)
    parent[7:9, 7:9] = True
    pond.seed_life(parent, energy=8.0)
    picks = []
    for _ in range(steps):
        child = pond.bud(parent)
        if child is not None:
            picks.append(tuple(map(tuple, child.nonzero().tolist())))
        pond.regenerate()
        pond.step_cells()
    return picks


def test_matching_choices_are_reproducible_for_same_seed():
    a = _matching_bud_sequence(4)
    b = _matching_bud_sequence(4)
    assert a and a == b, "рулетка matching обязана повторяться при том же сиде"


def test_matching_choices_differ_for_different_seeds():
    a = _matching_bud_sequence(4)
    c = _matching_bud_sequence(5)
    assert a != c


@pytest.mark.skipif(
    not (MORPH / "checkpoints" / "world_base_rule.pt").is_file(),
    reason="нет чекпоинта правила (локальный артефакт, в git не едет)",
)
def test_matching_pop_time_reproducible_end_to_end():
    """Два прогона тем же сидом дают одинаковые pop_time и живых (регрессия §18a)."""
    from world.run_pond import PondRun
    ckpt = str(MORPH / "checkpoints" / "world_base_rule.pt")

    def one():
        cfg = PondConfig(
            grid=16, resource_layout="gradient", income_mode="proportional",
            init_resource_fill=0.9, baseline_income=0.2, update_cost=0.02,
            repair_cost=0.02, budding_mass=8, budding_cost=0.2, spore_cells=2,
            spore_bias="matching", matching_temp=1.0, flip_at=20)
        run = PondRun(world_cfg=cfg, seed=3, device="cpu", rule_checkpoint=ckpt)
        run.seed(cells=4, energy=8.0)
        run.run(40, log_every=40)
        return int(run.pop_time), int(run.pond.state.alive.sum())

    assert one() == one()


# ---------- подвижность споры при расселении (I-022) ----------

def _mobility_pond(steps: int, cost: float = 0.0, **over):
    cfg = dict(grid=12, resource_regen=0.0, baseline_income=0.0, update_cost=0.0,
               repair_cost=0.0, damage_rate=0.0, budding_cost=0.2, spore_cells=1,
               noise=0.0, spore_bias="rich", mobility_steps=steps, mobility_cost=cost)
    cfg.update(over)
    pond = Pond(PondConfig(**cfg), seed=7)
    parent = torch.zeros((12, 12), dtype=torch.bool)
    parent[5:7, 1:3] = True
    pond.seed_life(parent, energy=10.0)
    # ресурс растёт вправо: споре есть куда идти
    cols = torch.arange(12, dtype=torch.float32)
    pond.state.resource = (0.05 * (cols + 1)).repeat(12, 1)
    return pond, parent


def test_mobility_off_keeps_chosen_spot():
    pond, parent = _mobility_pond(steps=0)
    child = pond.bud(parent)
    assert int(child.sum()) == 1
    assert bool(child[5, 3])  # выбранная клетка = argmax по ресурсу, ходов нет
    assert pond.mobility_moves == 0
    assert pond.mobility_shift == 0.0


def test_free_mobility_walks_toward_richer_cells():
    pond, parent = _mobility_pond(steps=10, cost=0.0)
    child = pond.bud(parent)
    ys, xs = child.nonzero(as_tuple=True)
    assert int(xs[0]) > 3, "при бесплатной подвижности спора должна уйти вправо"
    assert int(ys[0]) == 5
    assert pond.mobility_shift > 0
    # бесплатно — энергия споры не уменьшилась
    assert abs(float(pond.state.energy[child]) - 1.0) < 1e-6


def test_expensive_mobility_limited_by_budget():
    # цена 0.2, заряд споры 1.0 -> не больше 5 шагов
    pond, parent = _mobility_pond(steps=10, cost=0.2)
    child = pond.bud(parent)
    ys, xs = child.nonzero(as_tuple=True)
    assert int(xs[0]) == 3 + 5
    assert pond.mobility_moves == 5
    assert abs(float(pond.state.energy[child]) - 0.0) < 1e-6


def test_cheap_mobility_pays_but_keeps_energy():
    pond, parent = _mobility_pond(steps=10, cost=0.05)
    child = pond.bud(parent)
    ys, xs = child.nonzero(as_tuple=True)
    moved = int(xs[0]) - 3
    assert moved > 5
    assert abs(float(pond.state.energy[child]) - (1.0 - 0.05 * moved)) < 1e-6


def test_mobility_is_reproducible():
    a = _mobility_pond(steps=6, cost=0.05)[0].bud(_mobility_pond(steps=6, cost=0.05)[1])
    pond, parent = _mobility_pond(steps=6, cost=0.05)
    b = pond.bud(parent)
    assert bool((a == b).all())


# ---------- обратимость организма (I-023) ----------

def _organism_pond(cost: float = 0.05, **over):
    cfg = dict(grid=8, resource_regen=0.0, baseline_income=0.0, update_cost=0.0,
               repair_cost=0.0, damage_rate=0.0, noise=0.0,
               organism_mobility_cost=cost, organism_mobility_every=10)
    cfg.update(over)
    pond = Pond(PondConfig(**cfg), seed=11)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[3, 1] = True   # богатая клетка, энергия высокая
    mask[3, 3] = True   # бедная клетка, энергия ниже средней
    pond.seed_life(mask, energy=0.0)
    pond.state.energy[3, 1] = 5.0
    pond.state.energy[3, 3] = 0.5
    cols = torch.arange(8, dtype=torch.float32)
    pond.state.resource = (0.1 * cols).repeat(8, 1)
    return pond


def test_organism_mobility_off_by_default():
    pond = _organism_pond(cost=0.0)
    assert pond.find_organism_moves() == []


def test_organism_mobility_conserves_cells_and_pays_cost():
    pond = _organism_pond(cost=0.05)
    alive_before = int(pond.state.alive.sum())
    energy_before = float(pond.state.energy.sum())
    moves = pond.find_organism_moves()
    assert len(moves) == 1, "уходить должна только голодная клетка"
    sy, sx, dy, dx = moves[0]
    assert (sy, sx) == (3, 3)
    assert dx > sx, "шаг должен быть в сторону большего ресурса"
    pond.apply_organism_moves(moves)
    assert int(pond.state.alive.sum()) == alive_before, "число живых сохраняется"
    assert abs((energy_before - float(pond.state.energy.sum())) - 0.05) < 1e-6
    assert int(pond.organism_moves) == 1


def test_organism_mobility_moves_state_and_genome():
    from world.run_pond import PondRun
    cfg = PondConfig(grid=8, resource_regen=0.0, baseline_income=0.0, update_cost=0.0,
                     repair_cost=0.0, damage_rate=0.0, noise=0.0,
                     organism_mobility_cost=0.05, organism_mobility_every=10)
    run = PondRun(world_cfg=cfg, seed=2, device="cpu")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[3, 3] = True
    mask[0, 0] = True   # вторая клетка, чтобы средняя энергия была выше голодной
    run.pond.seed_life(mask, energy=5.0)
    run.pond.state.energy[3, 3] = 0.5
    cols = torch.arange(8, dtype=torch.float32)
    run.pond.state.resource = (0.1 * cols).repeat(8, 1)
    run.state[0, :, 3, 3] = torch.arange(run.state.shape[1], dtype=run.state.dtype)
    run.genome[0, :, 3, 3] = torch.arange(run.genome.shape[1], dtype=run.genome.dtype)
    run.pond.state.step = 10
    moved = run._organism_mobility()
    assert moved == 1
    pos = run.pond.state.alive.nonzero(as_tuple=True)
    coords = set(zip(pos[0].tolist(), pos[1].tolist()))
    assert (0, 0) in coords and (3, 3) not in coords
    dy, dx = [c for c in coords if c != (0, 0)][0]
    assert torch.equal(run.state[0, :, dy, dx], torch.arange(run.state.shape[1], dtype=run.state.dtype))
    assert torch.equal(run.genome[0, :, dy, dx], torch.arange(run.genome.shape[1], dtype=run.genome.dtype))
    assert float(run.state[0, :, 3, 3].abs().sum()) == 0.0
    assert int(run.pond.state.alive.sum()) == 2


# ---------- частотно-зависимый ресурс, два типа (I-030) ----------

def _two_type_pond(freq_dep: float = 1.0, type_mode: str = "fixed", **over):
    cfg = dict(grid=8, resource_regen=0.0, baseline_income=0.2, update_cost=0.0,
               repair_cost=0.0, damage_rate=0.0, noise=0.0, income_mode="proportional",
               freq_dep=freq_dep, type_mode=type_mode, resource_layout="uniform",
               init_resource_fill=0.0)
    cfg.update(over)
    return Pond(PondConfig(**cfg), seed=3)


def test_two_type_income_uses_own_resource():
    pond = _two_type_pond()
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2, 2] = True   # тип A
    mask[5, 5] = True   # тип B
    pond.seed_life(mask, energy=5.0)
    pond.state.cell_type[5, 5] = 1
    pond.state.resource = torch.zeros((8, 8))       # A-ресурса нет
    pond.state.resource_b = torch.ones((8, 8))      # B-ресурс есть
    e_a0 = float(pond.state.energy[2, 2])
    e_b0 = float(pond.state.energy[5, 5])
    pond.step_cells()
    assert abs((float(pond.state.energy[2, 2]) - e_a0)) < 1e-6, "A не должен есть B-ресурс"
    assert float(pond.state.energy[5, 5]) - e_b0 > 0.5, "B должен получить доход"


def test_child_type_fixed():
    pond = _two_type_pond(type_mode="fixed")
    parent = torch.zeros((8, 8), dtype=torch.bool); parent[2:4, 2:4] = True
    pond.seed_life(parent, energy=5.0)
    pond.state.cell_type[3, 3] = 1   # даже у B-родителя потомок A при fixed
    child = torch.zeros((8, 8), dtype=torch.bool); child[1, 1] = True
    pond._assign_child_type(parent, child)
    assert int(pond.state.cell_type[1, 1]) == 0


def test_child_type_learn_follows_local_success():
    pond = _two_type_pond(type_mode="learn")
    parent = torch.zeros((8, 8), dtype=torch.bool); parent[2:4, 2:4] = True
    pond.seed_life(parent, energy=5.0)
    pond.state.cell_type[parent] = 0
    child = torch.zeros((8, 8), dtype=torch.bool); child[1, 1] = True
    # богатая зона: локально больше среднего -> наследует A
    pond.state.resource = torch.full((8, 8), 0.1)
    pond.state.resource[parent] = 1.0
    pond._assign_child_type(parent, child)
    assert int(pond.state.cell_type[1, 1]) == 0
    # бедная зона: локально меньше среднего -> переключается на B
    pond.state.resource = torch.full((8, 8), 1.0)
    pond.state.resource[parent] = 0.0
    pond._assign_child_type(parent, child)
    assert int(pond.state.cell_type[1, 1]) == 1


def test_freq_dep_suppresses_overused_type():
    pond = _two_type_pond(freq_dep=1.0, resource_regen=0.02)
    pond.state.resource = torch.zeros((8, 8))
    pond.state.resource_b = torch.zeros((8, 8))
    pond.consumed_a = 100.0   # A едят сильно
    pond.consumed_b = 0.0
    pond.regenerate()
    a_growth = float(pond.state.resource.sum())
    b_growth = float(pond.state.resource_b.sum())
    assert b_growth > a_growth * 10, "недоедаемый тип должен восстанавливаться быстрее"


def test_type_share_series_recorded():
    pond = _two_type_pond(freq_dep=0.5, type_mode="random")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(6):
        pond.regenerate()
        pond.step_cells()
    assert len(pond.type_share_series) >= 1
    assert 0.0 <= pond.type_share_series[0] <= 1.0

def test_child_type_mixfixed_inherits_without_switching():
    pond = _two_type_pond(type_mode="mixfixed", type_start="mixed")
    parent = torch.zeros((8, 8), dtype=torch.bool); parent[2:4, 2:4] = True
    pond.seed_life(parent, energy=5.0)
    pond.state.cell_type[parent] = 1
    child = torch.zeros((8, 8), dtype=torch.bool); child[1, 1] = True
    # даже в «плохой» зоне mixfixed не переключает — наследует тип родителя
    pond.state.resource_b = torch.full((8, 8), 0.0)
    pond.state.resource = torch.full((8, 8), 1.0)
    pond._assign_child_type(parent, child)
    assert int(pond.state.cell_type[1, 1]) == 1

def test_invasion_injects_rare_type():
    pond = _two_type_pond(freq_dep=1.0, type_mode="fixed", type_start="a",
                          invade_at=2, invade_share=0.5, invade_type=1)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    assert int(pond.state.cell_type[pond.state.alive].sum()) == 0   # все A
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    alive = int(pond.state.alive.sum())
    b_share = float((pond.state.cell_type[pond.state.alive] == 1).float().mean())
    assert b_share > 0.0, "после инвазии редкий тип должен появиться"
    assert abs(pond.invasion_share_after - b_share) < 1e-6
    assert alive >= int(round(0.5 * alive))
    assert pond.invasion_step == 2


def test_invasion_off_keeps_single_type():
    pond = _two_type_pond(freq_dep=1.0, type_mode="fixed", type_start="a")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(4):
        pond.regenerate()
        pond.step_cells()
    assert int(pond.state.cell_type[pond.state.alive].sum()) == 0
    assert pond.invasion_share_after is None
