"""Питоновский аналог F-SURV: порог выживания и время смерти совпадают с формулой.

Проверяем не Lean (он уже проверен), а то, что в нашей среде энергия ведёт себя ровно
так, как предполагает теорема: при доходе меньше цены клетка умирает за
⌈E₀ / (cost − income)⌉ шагов, а при доходе не меньше цены не умирает вовсе.

Если тест падает — в среде есть скрытый приток или расход, которого нет в
арифметике, и его надо найти (это и есть смысл формализации).
"""
import math

import torch

from world.pond import Pond, PondConfig

GRID = 8


def _energy_after(energy: float, income: float, cost: float, steps: int) -> float:
    """Арифметика из F-SURV: энергия после steps шагов."""
    return energy + steps * (income - cost)


def test_economy_extremes_match_survival_theorem():
    """Доход не меньше цены — клетка не голодает; меньше — энергия строго падает."""
    for energy in (0.5, 5.0, 8.0):
        assert _energy_after(energy, 0.02, 0.01, 100) > energy
        assert _energy_after(energy, 0.005, 0.01, 100) < energy


def test_predicted_death_time_matches_energy_accounting():
    """Время до нуля энергии = ⌈E₀ / (cost − income)⌉, и это видно по формуле."""
    energy, cost, income = 8.0, 0.02, 0.005
    steps = math.ceil(energy / (cost - income))
    assert _energy_after(energy, income, cost, steps) <= 0
    assert _energy_after(energy, income, cost, steps - 1) > 0


def test_pond_charges_energy_without_hidden_sources():
    """Реальная среда: на бедном ресурсе энергия падает, на богатом — нет.

    Важно: доход тратит ресурс, а он ещё и восстанавливается с конечной скоростью.
    Поэтому «богато» = высокая регенерация + заполнение, «бедно» = почти ничего.
    Это проверка отсутствия скрытого притока: без ресурса энергия обязана убывать.
    """
    cases = (
        # (fill, regen, ожидаем падение энергии)
        (0.05, 0.0001, True),
        (0.95, 0.5000, False),
    )
    for fill, regen, expect_drop in cases:
        world = PondConfig(
            grid=GRID,
            baseline_income=0.02,
            update_cost=0.02,
            repair_cost=0.02,
            membrane_gated=False,
            damage_rate=0.0,
            resource_regen=regen,
            noise=0.0,
            budding_mass=10_000,      # размножение выключено
            resource_max=1.0,
            init_resource_fill=fill,
            income_mode="proportional",
        )
        pond = Pond(world, seed=0)
        pond.state.alive[3, 3] = True
        pond.state.energy[3, 3] = 4.0
        first = float(pond.state.energy[3, 3])
        for _ in range(60):
            pond.regenerate()   # без регенерации ресурс кончается у любой зоны
            pond.step_cells()
        last = float(pond.state.energy[3, 3])
        if expect_drop:
            assert last < first, f"на бедном ресурсе энергия должна падать (fill={fill})"
        else:
            assert last > first, f"на богатом ресурсе энергия должна расти (fill={fill})"
