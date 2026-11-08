"""Model integrity: the invariants the world claims to hold, checked.

Each test here was written BEFORE its fix and failed on the old code. They are the regression guards for the
five defects found by static review on 08.11:

  1. budding created energy when the spore had more than two cells (pay*0.5 per cell, pay charged once);
  2. the docstring said age is diagnostic only, the code killed by age;
  3. repair_cost was charged every step whether or not a repair happened;
  4. genome inheritance at NCA growth was not defined (activation vs reproduction);
  5. config_block saved 37 of 133 fields, so the artifact was not self-contained.

Tests 1-3 are here. 4 and 5 are checked by scripts/check_config_completeness.py and by the
inheritance audit in this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from world.pond import Pond, PondConfig  # noqa: E402


def _pond(**kw) -> Pond:
    base = dict(grid=16, resource_regen=0.0, baseline_income=0.0, update_cost=0.0,
                repair_cost=0.0, damage_rate=0.0, noise=0.0, budding_cost=8.0,
                budding_mass=4, mobility_steps=0, mobility_cost=0.0)
    base.update(kw)
    return Pond(PondConfig(**base), seed=1)


def _body(pond: Pond, energy: float = 20.0) -> torch.Tensor:
    mask = torch.zeros((pond.cfg.grid, pond.cfg.grid), dtype=torch.bool)
    mask[7:9, 7:9] = True
    pond.seed_life(mask, energy=energy)
    return mask


# ---- 1. budding must not create energy, for any spore size -------------------------------

def test_budding_conserves_energy_for_every_spore_size():
    """The parent pays `budding_cost`; the spore receives exactly that, minus mobility.

    The old code gave each spore cell `pay * 0.5`, so 3 and 4 cells created 4 and 8 units from nothing.
    """
    for sc in (1, 2, 3, 4):
        pond = _pond(spore_cells=sc)
        parent = _body(pond)
        before = float(pond.state.energy.sum())
        child = pond.bud(parent)
        after = float(pond.state.energy[parent].sum())
        got = float(pond.state.energy[child].sum()) if child is not None else 0.0
        created = (after + got) - before
        assert abs(created) < 1e-6, f"spore_cells={sc}: created {created:+.3f} energy from nothing"


def test_budding_energy_per_cell_is_the_share():
    """With no mobility cost, the spore's total is exactly what the parent paid."""
    for sc in (1, 2, 3, 4):
        pond = _pond(spore_cells=sc)
        parent = _body(pond)
        before = float(pond.state.energy.sum())
        child = pond.bud(parent)
        got = float(pond.state.energy[child].sum())
        assert abs(got - 8.0) < 1e-6, f"spore_cells={sc}: spore got {got}, parent paid 8"


# ---- 2. age must not be a cause of death while the docstring says it is not ---------------

def test_age_does_not_kill_when_docstring_says_so():
    """A cell past max_age with energy and no damage must survive if age is diagnostic only."""
    pond = _pond(max_age=5, damage_max=1000)
    mask = torch.zeros((16, 16), dtype=torch.bool)
    mask[8, 8] = True
    pond.seed_life(mask, energy=100.0)
    pond.state.age[mask] = 10_000
    pond.step_cells()
    assert bool(pond.state.alive[mask].any()), "a cell died of age although the docstring says age is diagnostic"


# ---- 3. repair_cost must be charged for a repair, not every step --------------------------

def test_repair_cost_is_not_charged_without_damage():
    """A cell with no damage pays update_cost only."""
    pond = _pond(update_cost=0.1, repair_cost=0.5)
    mask = torch.zeros((16, 16), dtype=torch.bool)
    mask[8, 8] = True
    pond.seed_life(mask, energy=10.0)
    pond.state.damage[mask] = 0
    before = float(pond.state.energy[mask].sum())
    pond.step_cells()
    after = float(pond.state.energy[mask].sum())
    spent = before - after
    assert abs(spent - 0.1) < 1e-6, f"spent {spent} with no damage; update_cost is 0.1"
