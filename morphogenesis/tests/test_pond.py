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
                          invade_at=2, invade_share=0.5, invade_type=1, invade_min_cells=1)
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


def _colony_invasion_pond(**over):
    """Пруд с типом на колонии: инвазия — новая редкая колония (дизайн 3)."""
    cfg = dict(freq_dep=0.0, type_mode="mixfixed", type_start="a", type_level="colony",
               invade_at=2, invade_type=1, invade_min_cells=1, resource_layout="uniform")
    cfg.update(over)
    return _two_type_pond(**cfg)


def test_invader_cells_one_places_single_cell():
    """Доза 1 — ровно то, что делала серия 24.10: одна клетка, одна новая колония."""
    pond = _colony_invasion_pond(invader_cells=1)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    before = int(pond.state.alive.sum())
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    after = int(pond.state.alive.sum())
    # подсажена одна клетка (плюс, возможно, родившиеся за шаг — их считаем отдельно)
    assert pond.invader_cells_requested == 1
    assert pond.invader_cells_actual == 1
    share = float((pond.state.cell_type[pond.state.alive] == 1).float().mean())
    assert abs(pond.injection_share_actual - share) < 1e-3
    assert after >= before + 1, "клетка инокулята должна быть живой"
    assert pond.injection_share_actual < 0.5


def test_invader_cells_five_places_connected_blob():
    """Доза 5 — пять клеток ОДНОЙ 4-компонентой (иначе это пять колоний по одной)."""
    pond = _colony_invasion_pond(invader_cells=5)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    assert pond.invader_cells_requested == 5
    assert pond.invader_cells_actual == 5
    sizes, labels = Pond._components(pond.state.alive)
    invader = pond.state.cell_type == 1
    assert int(pond.state.cell_type[invader].numel()) >= 5
    # все клетки инокулята лежат в одной компоненте
    labs = {int(labels[y, x]) for y, x in invader.nonzero(as_tuple=False).tolist()}
    assert len(labs) == 1, f"инокулят распался на {len(labs)} компонент"
    assert sizes[list(labs)[0]] >= 5


def test_invader_cells_capped_by_free_space():
    """Свободных клеток меньше дозы — ставится сколько влезает, факт в summary-поле."""
    pond = _colony_invasion_pond(invader_cells=10)
    mask = torch.ones((8, 8), dtype=torch.bool)
    mask[0, 0] = False
    mask[0, 1] = False
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    assert pond.invader_cells_requested == 10
    assert 1 <= pond.invader_cells_actual < 10, "пятно не может быть больше свободного места"


def test_config_block_records_run_parameters():
    """`summary["config"]` несёт параметры, которых раньше в артефакте не было."""
    from world.run_pond import config_block
    cfg = PondConfig(grid=8, freq_dep=1.0, type_mode="mixfixed", type_level="colony",
                     invade_at=200, invade_share=0.05, invade_type=1,
                     invade_min_cells=30, invader_cells=5)
    block = config_block(cfg)
    assert block["freq_dep"] == 1.0
    assert block["type_level"] == "colony"
    assert block["type_mode"] == "mixfixed"
    assert block["invader_cells"] == 5
    assert block["invade_at"] == 200
    assert block["layout"] == cfg.resource_layout
    assert block["income"] == cfg.baseline_income
    assert block["update_cost"] == cfg.update_cost
    assert block["repair_cost"] == cfg.repair_cost


def test_cli_defaults_match_pond_config():
    """Дефолт CLI обязан совпадать с `PondConfig`: иначе прогон без флага — не тот прогон.

    Инцидент 24.10: `--invade-min-cells` имел дефолт 50 при `PondConfig` 30, и
    серия, запущенная без явного флага, шла бы по другой постановке.
    """
    from world.run_pond import build_parser
    ap = build_parser()
    cfg = PondConfig()
    pairs = {
        "invade_at": cfg.invade_at,
        "invade_share": cfg.invade_share,
        "invade_type": cfg.invade_type,
        "invade_min_cells": cfg.invade_min_cells,
        "invader_cells": cfg.invader_cells,
        "type_level": cfg.type_level,
        "type_mode": cfg.type_mode,
        "type_inherit": cfg.type_inherit,
        "freq_dep": cfg.freq_dep,
        "layout": cfg.resource_layout,
    }
    for flag, want in pairs.items():
        got = ap.get_default(flag)
        assert got == want, f"--{flag.replace('_', '-')}: CLI {got!r} != PondConfig {want!r}"


def test_generation_block_needs_twenty_divisions():
    """Длина поколения — медиана по делениям; меньше 20 делений — null, а не оценка."""
    from world.run_pond import generation_block
    assert generation_block([])["generation_length"] is None
    assert generation_block(list(range(1, 20)))["generation_length"] is None
    block = generation_block(list(range(1, 21)))
    assert block["generation_length"] == 10.5
    assert block["generation_divisions"] == 20


def test_bud_records_parent_age_at_division():
    """Почкование пишет возраст родителя: поколение измерено, а не оценено косвенно."""
    pond = _two_type_pond(freq_dep=0.0, type_mode="fixed", type_start="a")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    parent_age_before = int(round(float(pond.state.age[pond.state.alive].float().mean())))
    child = pond.bud(pond.state.alive)
    assert child is not None and int(child.sum()) > 0, "почкование должно дать потомков"
    ages = pond.division_parent_ages
    assert len(ages) == int(child.sum()), "по одной записи на каждого потомка"
    assert ages[0] == parent_age_before, "записан возраст родителя на момент деления"


def _mutation_pond(rate: float, **over):
    cfg = dict(grid=8, resource_regen=0.0, baseline_income=0.2, update_cost=0.0,
               repair_cost=0.0, damage_rate=0.0, noise=0.0, income_mode="proportional",
               freq_dep=0.0, type_mode="mixfixed", resource_layout="uniform",
               init_resource_fill=0.0, mutation_rate=rate)
    cfg.update(over)
    return Pond(PondConfig(**cfg), seed=3)


def test_mutation_zero_creates_no_new_tags():
    """m=0 — прежнее поведение: одна метка линии, ни одной мутации."""
    pond = _mutation_pond(0.0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    newly = pond.bud(pond.state.alive)
    assert newly is not None
    assert pond.mutation_events == 0
    tags = torch.unique(pond.state.tag[pond.state.alive])
    assert int(tags.max()) == 0, "новых меток при m=0 быть не должно"
    assert pond.births_by_type, "рождения считаются и без мутации"


def test_mutation_one_gives_every_child_a_new_tag():
    """m=1 — каждый потомок получает новую метку линии (и признак от родителя)."""
    pond = _mutation_pond(1.0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    child = pond.bud(pond.state.alive)
    assert child is not None
    n_children = int(child.sum())
    assert pond.mutation_events == n_children >= 1
    child_tags = torch.unique(pond.state.tag[child])
    assert int(child_tags.min()) >= 1, "у потомков новые метки"
    assert int(pond.state.tag.min()) == 0, "предковая метка остаётся у родителя"


def test_mutation_trait_inherits_with_noise():
    """Признак линии наследуется; при мутации сдвигается на шум заданного масштаба."""
    pond = _mutation_pond(1.0, mutation_trait_sigma=0.5)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    child = pond.bud(pond.state.alive)
    assert child is not None
    traits = pond.state.tag_trait[child].tolist()
    assert any(abs(t) > 0.0 for t in traits), "признак потомка сдвинут шумом"
    assert abs(sum(traits) / len(traits)) < 2.0, "сдвиг в масштабе sigma, а не в разы"


def test_tag_series_and_counts():
    """Серия по меткам: шаги каждые 5, счётчики в сумме равны живым."""
    pond = _mutation_pond(0.05)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(5):
        pond.regenerate()
        pond.step_cells()
    snap = pond.snapshot()
    assert "types_alive" in snap and "mutation_events" in snap
    assert snap["types_alive"] >= 1
    counts = {}
    for key, value in snap.get("type_counts", {}).items():
        counts[key] = value
    if counts:
        assert sum(counts.values()) == int(pond.state.alive.sum())


def test_lineage_depth_and_fitness_without_mutation():
    """Родословная: при m=0 глубина 0, а фитнес линии равен числу рождений."""
    pond = _mutation_pond(0.0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    child = pond.bud(pond.state.alive)
    assert child is not None
    assert pond.generation_depth.get(0) == 0, "основатель — нулевая глубина"
    births_total = sum(pond.births_by_type.values())
    assert sum(pond.lineage_offspring.values()) == births_total, \
        "каждое рождение приписано ровно одной линии"


def test_mutation_creates_lineage_of_depth_one():
    """Мутация создаёт линию первого поколения от основателя."""
    pond = _mutation_pond(1.0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    child = pond.bud(pond.state.alive)
    assert child is not None
    new_tags = [t for t in pond.generation_depth if t != 0]
    assert new_tags, "мутация должна создать новые линии"
    assert all(pond.generation_depth[t] == 1 for t in new_tags), \
        "мутант — поколение 1 от основателя"
    assert all(pond.lineage_offspring.get(t, 0) == 0 for t in new_tags), \
        "у новой линии пока нет своих рождений"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="нет CUDA")
def test_mutation_works_on_cuda_generator():
    """Мутация на CUDA: `gen_sel` — CPU-генератор, розыгрыш тянется на CPU.

    Инцидент 24.10 (серия B): `torch.rand(..., generator=cpu_gen, device='cuda')` давал
    `RuntimeError: Expected a 'cuda' device type for generator` — 12 прогонов упали за
    секунды, а CPU-тесты этого не видели.
    """
    cfg = PondConfig(grid=8, resource_regen=0.0, baseline_income=0.2, update_cost=0.0,
                     repair_cost=0.0, damage_rate=0.0, noise=0.0, income_mode="proportional",
                     freq_dep=0.0, type_mode="mixfixed", resource_layout="uniform",
                     init_resource_fill=0.0, mutation_rate=1.0)
    pond = Pond(cfg, device="cuda", seed=3)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    child = torch.zeros((8, 8), dtype=torch.bool)
    child[4, 4] = True
    pond.register_births(child, mask)
    assert pond.mutation_events == 1, "мутация должна сработать без ошибки генератора"
    assert int(pond.state.tag[4, 4]) >= 1


def _v8_pond(**over):
    cfg = dict(grid=8, resource_regen=0.0, baseline_income=0.2, update_cost=0.0,
               repair_cost=0.0, damage_rate=0.0, noise=0.0, income_mode="proportional",
               freq_dep=0.0, type_mode="mixfixed", resource_layout="uniform",
               init_resource_fill=0.0, type_level="colony", invade_at=2, invade_type=1,
               invade_min_cells=1, invader_cells=1)
    cfg.update(over)
    return _two_type_pond(**cfg)


def test_merge_rule_majority_keeps_majority():
    """Дефолтное правило: тип компоненты — большинство (как в §10ab)."""
    pond = _v8_pond(merge_rule="majority")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    pond.state.cell_type[2, 2] = 1          # 1 из 4 — меньшинство
    pond.enforce_colony_types()
    assert int(pond.state.cell_type[2:4, 2:4].min()) == 0, "меньшинство переписано большинством"


def test_merge_rule_mass_weighted_gives_minority_a_chance():
    """Стохастическое слияние: меньшинство выигрывает с вероятностью своей доли массы."""
    wins = 0
    trials = 200
    for seed in range(trials):
        pond = _v8_pond(merge_rule="mass_weighted")
        pond.gen_sel = torch.Generator(device="cpu").manual_seed(seed * 31 + 7)
        mask = torch.zeros((8, 8), dtype=torch.bool)
        mask[2:4, 2:4] = True
        pond.seed_life(mask, energy=5.0)
        pond.state.cell_type[2, 2] = 1      # 1 из 4 = 25% массы
        pond.enforce_colony_types()
        if int(pond.state.cell_type[2, 2]) == 1:
            wins += 1
    assert 20 <= wins <= 80, f"доля побед меньшинства {wins}/200 при 25% массы — вне 10–40%"


def test_gap_placement_puts_invader_far_from_resident():
    """Плечо into_gap: инокулят садится в клетку, максимально далёкую от резидента."""
    pond = _v8_pond(invade_placement="gap", invader_cells=1)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[0, 0] = True                       # резидент в углу
    pond.seed_life(mask, energy=5.0)
    pond.regenerate()
    pond.step_cells()                        # шаг 1 — инвазии нет
    pond.regenerate()
    pond.step_cells()                        # шаг 2 — инвазия
    invader = pond.state.cell_type == 1
    assert bool(invader.any()), "инокулят должен появиться"
    ys, xs = invader.nonzero(as_tuple=True)
    dist = max(abs(int(y)) + abs(int(x)) for y, x in zip(ys.tolist(), xs.tolist()))
    assert dist >= 6, f"пятно село близко к резиденту (расстояние {dist})"


def test_invade_on_empty_founds_colony():
    """Плечо resident_free: на пустом поле инокулят основывает колонию сам."""
    pond = _v8_pond(invade_on_empty=True, invader_cells=3)
    pond.regenerate()
    pond.step_cells()
    pond.regenerate()
    pond.step_cells()
    assert int(pond.state.alive.sum()) >= 3, "колония-основатель должна существовать"
    assert int(pond.state.cell_type.sum()) >= 3, "все клетки основателя — инвайдер"


def test_ignition_gate_keeps_empty_field_empty():
    """Гейт зажигания: без живого соседа правило не зажигает — пустое поле остаётся пустым.

    Без гейта обученное правило из нулевого поля зажигает весь мир (1024 из 1024 на шаге 1,
    §10ae), и вопрос «основывает ли колонию N клеток» не задаётся.
    """
    from world.run_pond import PondRun
    cfg = PondConfig(grid=8, resource_layout="uniform", income_mode="proportional",
                     init_resource_fill=0.9, baseline_income=0.2, update_cost=0.02,
                     repair_cost=0.02, budding_mass=8, spore_bias="score", w_rich=0.1,
                     ignition_gate=True)
    run = PondRun(world_cfg=cfg, seed=1, device="cpu")
    pond = run.pond
    # имитируем «правило зажгло всё поле»: гейт должен погасить всё, кроме уже живого
    alive_now = torch.ones((8, 8), dtype=torch.bool)
    gated = run._gate_ignition(alive_now)
    assert int(gated.sum()) == 0, "на пустом поле гейт не даёт зажечь ни одной клетки"
    # и с живой клеткой: зажигаются только её 4-соседи
    pond.state.alive[3, 3] = True
    gated = run._gate_ignition(alive_now)
    assert int(gated.sum()) == 5, "живая клетка + её 4 соседа"


def test_final_alive_map_matches_world():
    """Карта финального живого: размер и число единиц совпадают с миром."""
    from world.run_pond import final_map_block
    pond = _two_type_pond(freq_dep=0.0, type_mode="mixfixed")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    block = final_map_block(pond)
    rows = block["final_alive_map"].split("/")
    assert block["alive_map_shape"] == [8, 8]
    assert len(rows) == 8 and all(len(r) == 8 for r in rows)
    assert sum(r.count("1") for r in rows) == int(pond.state.alive.sum())


def test_merge_rule_keep_preserves_minority():
    """H-ALIVE-28: при merge=keep никто не переписывается — тип остаётся на клетке."""
    pond = _v8_pond(merge_rule="keep")
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    pond.state.cell_type[2, 2] = 1
    pond.enforce_colony_types()
    assert int(pond.state.cell_type[2, 2]) == 1, "меньшинство сохранило тип"
    assert int(pond.state.cell_type[2:4, 2:4].sum()) == 1


def test_lineage_spores_count_only_budding():
    """Фитнес линии для условия E — споры (почкование), а не клетки роста правила."""
    pond = _mutation_pond(0.0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    child = pond.bud(pond.state.alive)
    assert child is not None
    spores = sum(pond.lineage_spores.values())
    assert spores == int(child.sum()), "каждая спора засчитана линии родителя"
    assert spores <= sum(pond.lineage_offspring.values()), \
        "спор не может быть больше, чем всех потомков (клетки роста тоже считаются)"


def test_trait_effect_default_off_and_invested_counted():
    """eps по умолчанию 0 (признак не читается), но вложенная энергия по линиям считается."""
    from world.run_pond import build_parser
    ap = build_parser()
    assert ap.get_default("trait_effect") == 0.0
    assert ap.get_default("merge_rule") == "majority"
    pond = _mutation_pond(0.05, invest_rate=0.02, invest_mode="fixed", trait_effect=0.5)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=8.0)
    for _ in range(6):
        pond.regenerate()
        pond.step_cells()
    assert pond.lineage_invested, "хотя бы одна линия должна быть в словаре вложений"


def _type_run(start: str, fd: float, steps: int = 40, grid: int = 16, seed: int = 1):
    from world.run_pond import PondRun
    cfg = PondConfig(grid=grid, resource_layout="gradient", income_mode="proportional",
                     init_resource_fill=0.9, baseline_income=0.2, update_cost=0.02,
                     repair_cost=0.02, budding_mass=8, budding_cost=0.2, spore_cells=2,
                     spore_bias="score", w_rich=0.1, freq_dep=fd, type_mode="mixfixed",
                     type_start=start, noise=0.002, resource_regen=0.02)
    run = PondRun(world_cfg=cfg, seed=seed, device="cpu",
                  rule_checkpoint=str(MORPH / "checkpoints" / "world_base_rule.pt"))
    run.seed(cells=4, energy=8.0)
    for _ in range(steps):
        run.step()
    s = run.pond.state
    return float((s.cell_type[s.alive] == 0).float().mean()), int(s.alive.sum())


@pytest.mark.skipif(
    not (MORPH / "checkpoints" / "world_base_rule.pt").is_file(),
    reason="нет чекпоинта правила",
)
def test_pure_a_colony_stays_a():
    a_share, alive = _type_run("a", fd=1.0, steps=90)
    assert alive > 10
    assert a_share == 1.0


@pytest.mark.skipif(
    not (MORPH / "checkpoints" / "world_base_rule.pt").is_file(),
    reason="нет чекпоинта правила",
)
def test_pure_b_colony_stays_b():
    a_share, alive = _type_run("b", fd=1.0, steps=90)
    assert alive > 10
    assert a_share == 0.0


@pytest.mark.skipif(
    not (MORPH / "checkpoints" / "world_base_rule.pt").is_file(),
    reason="нет чекпоинта правила",
)
def test_neutral_mixed_fixates_via_voter_dynamics():
    """fd=0: тип копируется локально при росте, это боруновский процесс - он
    фиксирует тип, а не держит 50/50. Фиксируем это как свойство модели."""
    early, _ = _type_run("mixed", fd=0.0, steps=10)
    late, alive = _type_run("mixed", fd=0.0, steps=100)
    assert 0.05 < early < 0.95
    assert alive > 10
    assert late < 0.2 or late > 0.8

def test_invasion_does_not_touch_energy_age_damage():
    pond = _two_type_pond(freq_dep=1.0, type_mode="mixfixed", type_start="a",
                          invade_at=2, invade_share=0.5, invade_type=1, invade_min_cells=1)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[2:4, 2:4] = True
    pond.seed_life(mask, energy=5.0)
    for _ in range(2):
        pond.regenerate()
        pond.step_cells()
    e = pond.state.energy.clone()
    a = pond.state.age.clone()
    d = pond.state.damage.clone()
    pond._invade()
    assert torch.equal(pond.state.energy, e), "инвазия не должна менять энергию"
    assert torch.equal(pond.state.age, a), "инвазия не должна менять возраст"
    assert torch.equal(pond.state.damage, d), "инвазия не должна менять повреждения"
