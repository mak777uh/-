"""test_closure.py — организационное замыкание: без производства мембраны не выжить.

Зачем: линия Матурана/Варела → Mossio/Moreno говорит, что живое поддерживает себя,
производя ограничения, через которые идёт поток энергии. Мы реализовали минимальную
версию: мембрана распадается, гейтирует приток ресурса и восстанавливается за
энергию. Тест держит главное различие: если производство мембраны выключено, обмен
прекращается и клетка гибнет; если включено — живёт.
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


def probe(rebuild: float, steps: int = 3000) -> int:
    cfg = PondConfig(
        grid=16,
        resource_regen=0.05,
        baseline_income=0.02,
        update_cost=0.01,
        repair_cost=0.0,
        damage_rate=0.0,
        membrane_gated=True,
        membrane_decay=0.05,
        membrane_rebuild=rebuild,
        membrane_rebuild_cost=0.01,
        noise=0.0,
    )
    pond = Pond(cfg, seed=0)
    mask = torch.zeros((16, 16), dtype=torch.bool)
    mask[7:9, 7:9] = True
    pond.seed_life(mask, energy=1.0)
    for step in range(steps):
        pond.regenerate()
        pond.step_cells()
        if not pond.state.alive.any():
            return step + 1
    return steps


def test_without_membrane_production_cells_starve():
    assert probe(0.0) < 1000, "без производства мембраны обмен должен прекратиться"


def test_with_membrane_production_cells_survive():
    assert probe(0.10) >= 2000, "с производством мембраны клетка должна выживать"


def test_gate_actually_blocks_uptake():
    cfg = PondConfig(grid=8, resource_regen=0.0, baseline_income=0.5, update_cost=0.0,
                     repair_cost=0.0, damage_rate=0.0, membrane_gated=True,
                     membrane_decay=0.0, membrane_rebuild=0.0, noise=0.0)
    pond = Pond(cfg, seed=0)
    mask = torch.zeros((8, 8), dtype=torch.bool)
    mask[3, 3] = True
    pond.seed_life(mask, energy=1.0)
    pond.state.membrane[3, 3] = 0.0     # мембраны нет
    before = float(pond.state.energy[3, 3])
    pond.step_cells()
    assert float(pond.state.energy[3, 3]) <= before, "без мембраны притока быть не должно"
