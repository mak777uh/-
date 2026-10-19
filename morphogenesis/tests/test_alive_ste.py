"""
test_alive_ste.py — смерть-инвариант и суррогатный градиент (§5.7–5.8, §12.2.8).

Проверяет:

- жёсткий forward: мёртвая клетка обнуляется ЦЕЛИКОМ, включая стресс-канал;
- воскресение невозможно: из полностью мёртвой клетки не появляется ни одна
  живая (ни напрямую, ни через скрытые каналы);
- backward: градиент по alive-каналу НЕ нулевой (суррогат sigmoid(alpha/tau)),
  т.е. оптимизатор не попадает в мёртвую зону;
- при alive_mask_enabled шаг модели сохраняет смерть мёртвых клеток.
"""

import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from nca_core import (
    AliveSTE,
    NeuralCellularAutomaton,
    alive_hard_mask,
    enforce_alive_policy,
)


def _dead_cell_state(device, alive_value=-10.0):
    """Состояние из одной клетки: alpha ниже порога => клетка мертва."""
    state = torch.zeros(1, config.N_CHANNELS, 1, 1, device=device)
    state[:, config.ALIVE_CHANNEL] = alive_value
    # Заполним «тело» клетки ненулевыми значениями, чтобы обнуление было видно.
    for channel in range(config.N_CHANNELS):
        if channel != config.ALIVE_CHANNEL:
            state[:, channel] = 1.0
    state[:, config.STRESS_CHANNEL] = 3.0
    return state


class TestAliveSTE(unittest.TestCase):
    def setUp(self):
        self.device = torch.device(config.DEVICE)

    def test_dead_cell_zeroed_entirely_including_stress(self):
        """§5.7 [Rev.11]: обнуляется всё состояние клетки, включая стресс."""
        state = _dead_cell_state(self.device).requires_grad_(True)
        out = enforce_alive_policy(state)
        self.assertTrue(torch.all(out == 0.0), "мёртвая клетка не обнулена целиком")

    def test_alive_cell_untouched(self):
        state = _dead_cell_state(self.device, alive_value=10.0)
        out = enforce_alive_policy(state)
        self.assertTrue(torch.allclose(out, state), "живая клетка пострадала без причины")

    def test_no_resurrection_of_dead_field(self):
        """Полностью мёртвое поле не может ожить через скрытые каналы."""
        state = torch.zeros(1, config.N_CHANNELS, 4, 4, device=self.device)
        state[:, config.ALIVE_CHANNEL] = -10.0
        state[:, 2:12] = 5.0  # скрытые каналы «кричат», но живости не дают
        current = state
        for _ in range(3):
            current = enforce_alive_policy(current)
        self.assertTrue(torch.all(current == 0.0))
        self.assertEqual(float(alive_hard_mask(current).sum()), 0.0)

    def test_surrogate_gradient_nonzero_on_dead_cells(self):
        """§5.8: backward обязан давать ненулевой градиент по мёртвым клеткам."""
        state = _dead_cell_state(self.device).requires_grad_(True)
        out = AliveSTE.apply(state, state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1], config.ALIVE_THRESHOLD)
        loss = out[:, config.STRESS_CHANNEL].sum() + out[:, 0].sum()
        loss.backward()
        self.assertIsNotNone(state.grad)
        self.assertTrue(torch.isfinite(state.grad).all())
        alive_grad = state.grad[:, config.ALIVE_CHANNEL]
        self.assertGreater(
            float(alive_grad.abs().sum()),
            0.0,
            "суррогатный градиент по alive-каналу нулевой — death spiral вернётся",
        )

    def test_hard_forward_and_soft_backward_are_consistent_signs(self):
        """Чем ближе alpha к порогу, тем больше суррогатный градиент."""
        grads = []
        for alpha in (-4.0, -0.5, 0.0, 0.5, 4.0):
            state = _dead_cell_state(self.device, alive_value=alpha).requires_grad_(True)
            alive = state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1]
            out = AliveSTE.apply(state, alive, config.ALIVE_THRESHOLD)
            out.sum().backward()
            grads.append(float(state.grad[:, config.ALIVE_CHANNEL].abs().sum()))
        # Максимум около порога (alpha=0), спад на фарад-значениях.
        self.assertGreater(grads[2], grads[0])
        self.assertGreater(grads[2], grads[4])

    def test_model_step_keeps_dead_cells_dead(self):
        """Шаг NCA с alive-маской не воскрешает мёртвые клетки."""
        torch.manual_seed(config.SEED)
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(self.device)
        model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        model.eval()
        model.alive_mask_enabled = True
        state = torch.zeros(1, config.N_CHANNELS, 8, 8, device=self.device)
        state[:, config.ALIVE_CHANNEL] = -10.0  # всё мертво
        out = model(state)
        self.assertTrue(torch.all(out == 0.0), "шаг модели воскресил мёртвое поле")

    def test_run_steps_replay_keeps_masks_stable(self):
        """
        Градиентный чекпоинтинг не должен перерисовывать стохастику: два
        прогона с одинаковым noise_key дают идентичный forward.
        """
        torch.manual_seed(config.SEED)
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(self.device)
        gen = torch.Generator(device="cpu").manual_seed(config.SEED)
        model.set_generator(gen)
        model.train()
        state = torch.zeros(2, config.N_CHANNELS, 8, 8, device=self.device)
        state[:, config.ALIVE_CHANNEL] = 1.0
        a = model(state, noise_key=123)
        b = model(state, noise_key=123)
        self.assertTrue(torch.allclose(a, b), "replay по noise_key рассинхронизирован")
        c = model(state, noise_key=124)
        self.assertFalse(torch.allclose(a, c), "разные ключи дают identical шум — кэш сломан")


if __name__ == "__main__":
    unittest.main()
