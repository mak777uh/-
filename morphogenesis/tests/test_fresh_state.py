"""

test_fresh_state.py — Тесты инварианта живого свежнего состояния.

[v5.5-EXP FINAL Rev.7] ПРАВИЛО 31

Проверяет:

- replace_all_fresh создаёт >= 20% живых клеток;

- replace_with_fresh создаёт >= 20% живых клеток;

- канал 15 в свежем состоянии равен 0.

"""

import sys

import os

import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from nca_core import StatePool, init_state

class TestFreshState(unittest.TestCase):

    def setUp(self):

        self.device = torch.device(config.DEVICE)

    def test_replace_all_fresh_alive(self):

        """replace_all_fresh создаёт >= 20% живых клеток."""

        pool = StatePool(size=2, device=self.device)

        pool.replace_all_fresh()

        for state in pool.states:

            alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

            alive_fraction = float(

                (alpha_prob > config.ALIVE_THRESHOLD).float().mean().item()

            )

            self.assertGreaterEqual(

                alive_fraction,

                config.FRESH_MIN_ALIVE_FRACTION,

                f"Fresh state has {alive_fraction:.2%} alive cells, "

                f"need >= {config.FRESH_MIN_ALIVE_FRACTION:.2%}",

            )

    def test_replace_with_fresh_alive(self):

        """replace_with_fresh создаёт >= 20% живых клеток."""

        pool = StatePool(size=2, device=self.device)

        for index in range(pool.size):

            pool.replace_with_fresh(index)

            state = pool.states[index]

            alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

            alive_fraction = float(

                (alpha_prob > config.ALIVE_THRESHOLD).float().mean().item()

            )

            self.assertGreaterEqual(

                alive_fraction,

                config.FRESH_MIN_ALIVE_FRACTION,

            )

    def test_stress_channel_zero_in_fresh(self):

        """Канал 15 в свежем состоянии равен 0."""

        pool = StatePool(size=1, device=self.device)

        pool.replace_all_fresh()

        state = pool.states[0]

        stress_max = float(state[:, config.STRESS_CHANNEL].abs().max().item())

        self.assertLessEqual(

            stress_max,

            1e-6,

            f"Stress channel not zero in fresh state: max={stress_max}",

        )

    def test_init_state_alive(self):

        """init_state создаёт >= 20% живых клеток."""

        state = init_state(device=self.device)

        alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

        alive_fraction = float(

            (alpha_prob > config.ALIVE_THRESHOLD).float().mean().item()

        )

        self.assertGreaterEqual(

            alive_fraction,

            config.FRESH_MIN_ALIVE_FRACTION,

        )

    def test_init_state_stress_zero(self):

        """init_state инициализирует канал 15 нулями."""

        state = init_state(device=self.device)

        stress_max = float(state[:, config.STRESS_CHANNEL].abs().max().item())

        self.assertLessEqual(stress_max, 1e-6)

if __name__ == "__main__":

    unittest.main()