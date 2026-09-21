"""

test_death_invariant.py — Тесты смерть-инварианта.

[v5.5-EXP FINAL Rev.7]

Проверяет:

- мёртвое поле не оживает за 500 шагов;

- стресс не оживляет мёртвые клетки;

- пост-тренировочный тест смерти проходит.

"""

import sys

import os

import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from nca_core import NeuralCellularAutomaton, init_state

class TestDeathInvariant(unittest.TestCase):

    def setUp(self):

        self.device = torch.device(config.DEVICE)

    def test_dead_field_does_not_revive(self):

        """Мёртвое поле не оживает за 500 шагов."""

        model = NeuralCellularAutomaton().to(self.device)

        model.eval()

        model.alive_mask_enabled = True

        dead_state = torch.zeros(

            1,

            config.N_CHANNELS,

            config.GRID_SIZE,

            config.GRID_SIZE,

            device=self.device,

        )

        dead_state[:, config.ALIVE_CHANNEL, :, :] = config.DEAD_ALPHA_VALUE

        with torch.no_grad():

            state = dead_state

            for _ in range(500):

                state = model(state)

        alive_count = int(

            (

                torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

                > config.ALIVE_THRESHOLD

            )

            .sum()

            .item()

        )

        self.assertEqual(

            alive_count,

            0,

            f"ZOMBIE APOCALYPSE: {alive_count} cells resurrected from dead field",

        )

    def test_stress_does_not_revive_dead(self):

        """Стресс не оживляет мёртвые клетки."""

        was_enabled = config.STRESS_ENABLED

        config.STRESS_ENABLED = True

        model = NeuralCellularAutomaton().to(self.device)

        model.eval()

        model.alive_mask_enabled = True

        dead_state = torch.zeros(

            1,

            config.N_CHANNELS,

            config.GRID_SIZE,

            config.GRID_SIZE,

            device=self.device,

        )

        dead_state[:, config.ALIVE_CHANNEL, :, :] = config.DEAD_ALPHA_VALUE

        with torch.no_grad():

            state = dead_state

            for _ in range(100):

                state = model(state)

        alive_count = int(

            (

                torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

                > config.ALIVE_THRESHOLD

            )

            .sum()

            .item()

        )

        config.STRESS_ENABLED = was_enabled

        self.assertEqual(

            alive_count,

            0,

            f"Stress revived {alive_count} dead cells",

        )

    def test_zero_state_remains_dead(self):

        """Полностью нулевое состояние остаётся мёртвым."""

        model = NeuralCellularAutomaton().to(self.device)

        model.eval()

        model.alive_mask_enabled = True

        zero_state = torch.zeros(

            1,

            config.N_CHANNELS,

            config.GRID_SIZE,

            config.GRID_SIZE,

            device=self.device,

        )

        with torch.no_grad():

            state = zero_state

            for _ in range(100):

                state = model(state)

        alive_count = int(

            (

                torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

                > config.ALIVE_THRESHOLD

            )

            .sum()

            .item()

        )

        self.assertEqual(alive_count, 0)

    def test_stress_channel_zero_in_dead_field(self):

        """Стресс-канал в мёртвом поле остаётся нулевым."""

        was_enabled = config.STRESS_ENABLED

        config.STRESS_ENABLED = True

        model = NeuralCellularAutomaton().to(self.device)

        model.eval()

        model.alive_mask_enabled = True

        zero_state = torch.zeros(

            1,

            config.N_CHANNELS,

            config.GRID_SIZE,

            config.GRID_SIZE,

            device=self.device,

        )

        with torch.no_grad():

            state = zero_state

            for _ in range(50):

                state = model(state)

        stress_max = float(state[:, config.STRESS_CHANNEL].abs().max().item())

        config.STRESS_ENABLED = was_enabled

        self.assertLessEqual(

            stress_max,

            1e-5,

            f"Stress channel not zero in dead field: {stress_max}",

        )

if __name__ == "__main__":

    unittest.main()
