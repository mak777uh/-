"""
test_train_contract.py — контракт обучения §12.1.5 и структура лосса §12.6.3.

Смысл теста: «числа спеки должны быть числами конфига». раньше в репозитории
конфиг хранил два набора имён (Rev.7/8 и Rev.11), и агент крутил ключи, которые
train.py не читал. Проверка фиксирует:

- значения TRAIN_* из §12.1.5;
- лосс = взвешенная сумма членов LOSS_WEIGHTS, а не ad-hoc MSE+L1;
- смена веса реально меняет лосс (значит агент может влиять на обучение);
- attractor_divergence существует ТОЛЬКО в фазе 3;
- curriculum BPTT, расписание LR (warmup + косинус), границы фаз;
- alive_fraction считается по каноническому предикату.
"""

import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from nca_core import NeuralCellularAutomaton, run_steps
from target_patterns import create_target
from topo_proxy import TopologicalProxy
from train import (
    alive_fraction_of,
    build_lr_scheduler,
    compute_loss,
    get_current_unroll,
    resolve_phase,
)


class TestSpecNumbers(unittest.TestCase):
    """§12.1.5 — буквально."""

    def test_train_contract_values(self):
        self.assertEqual(config.TRAIN_BPTT_STEPS, 64)
        self.assertEqual(config.TRAIN_SAMPLE_POOL_SIZE, 256)
        self.assertEqual(config.TRAIN_BATCH_SIZE, 8)
        self.assertEqual(config.TRAIN_MAX_STEPS, 20000)
        self.assertAlmostEqual(config.TRAIN_LR, 1e-3)
        self.assertAlmostEqual(config.TRAIN_WEIGHT_DECAY, 1e-4)
        self.assertEqual(config.TRAIN_WARMUP_STEPS, 500)
        self.assertAlmostEqual(config.TRAIN_GRAD_CLIP_NORM, 1.0)
        self.assertEqual(config.TRAIN_LOG_INTERVAL, 50)
        self.assertEqual(config.TRAIN_EVAL_INTERVAL, 200)
        self.assertEqual(config.TRAIN_SAVE_INTERVAL, 1000)

    def test_loss_weights_values(self):
        w = config.LOSS_WEIGHTS
        self.assertAlmostEqual(w["visible_mse"], 1.0)
        self.assertAlmostEqual(w["alive_policy"], 0.5)
        self.assertAlmostEqual(w["hidden_regularization"], 0.05)
        self.assertAlmostEqual(w["stress_proxy"], 0.1)
        self.assertAlmostEqual(w["topo_proxy"], 0.1)
        self.assertAlmostEqual(w["attractor_divergence"], 0.2)

    def test_no_legacy_duplicate_names(self):
        """Старые имена (Rev.7/8) удалены: две правды о LR быть не может."""
        for legacy in ("LEARNING_RATE", "WEIGHT_DECAY", "TOTAL_TRAIN_ITERS",
                       "STATE_POOL_SIZE", "BATCH_SIZE", "UNROLL_STEPS",
                       "L1_REG_WEIGHT", "GRAD_CLIP"):
            self.assertFalse(
                hasattr(config, legacy),
                f"config.{legacy} вернулся — агент снова будет крутить мёртвый ключ",
            )


class TestLossComposition(unittest.TestCase):
    def setUp(self):
        self.device = torch.device(config.DEVICE)
        torch.manual_seed(config.SEED)
        self.model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(self.device)
        self.model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        self.model.train()
        self.target = create_target(device=self.device)
        self.state = torch.randn(
            2, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=self.device
        )
        self.state[:, config.ALIVE_CHANNEL] = 1.0
        self.state.requires_grad_(True)

    def test_all_weight_keys_appear_in_loss_dict(self):
        _, loss_dict = compute_loss(self.state, self.target, self.model, iteration=1)
        for key in ("visible_mse", "alive_policy", "hidden_reg", "stress_proxy", "topo_proxy"):
            self.assertIn(key, loss_dict)
        self.assertIn("alive_fraction", loss_dict)

    def test_weight_change_moves_total(self):
        """Вес из config обязан влиять на лосс — иначе действие агента пустышка."""
        original = float(config.LOSS_WEIGHTS["visible_mse"])
        try:
            _, base = compute_loss(self.state, self.target, self.model, iteration=1)
            config.LOSS_WEIGHTS["visible_mse"] = original + 1.0
            _, boosted = compute_loss(self.state, self.target, self.model, iteration=1)
            self.assertGreater(boosted["total"], base["total"])
            self.assertAlmostEqual(boosted["visible_mse"], base["visible_mse"], places=6)
        finally:
            config.LOSS_WEIGHTS["visible_mse"] = original

    def test_gradient_flows_to_state_and_params(self):
        """
        Градиент обязан доходить до параметров ЧЕРЕЗ раскатку: CellBrain
        инициализирован нулями (§12.2.2 «система стартует из покоя»), поэтому
        |delta| в нуле имеет поддифференциал 0, и единственная цепочка, которая
        учит сеть, — это влияние delta на состояние по всему unroll-у.
        """
        state = self.state.detach()
        rolled = run_steps(self.model, state, steps=2)
        total, _ = compute_loss(rolled, self.target, self.model, iteration=1)
        total.backward()
        grads = [p.grad for p in self.model.parameters() if p.grad is not None]
        self.assertTrue(grads, "параметры CellBrain не получили градиент")
        self.assertGreater(float(sum(g.abs().sum() for g in grads)), 0.0)
        last = list(self.model.brain.net)[-1]
        self.assertGreater(
            float(last.weight.grad.abs().sum()),
            0.0,
            "нулевой последний слой не обучается — сеть навсегда в покое",
        )

    def test_topo_term_only_on_stride_steps(self):
        proxy = TopologicalProxy(self.target)
        stride = max(2, proxy.stride)
        _, off = compute_loss(self.state, self.target, self.model, topo_proxy=proxy, iteration=1)
        _, on = compute_loss(
            self.state, self.target, self.model, topo_proxy=proxy, iteration=stride
        )
        self.assertEqual(off["topo_proxy"], 0.0)
        self.assertGreater(on["topo_proxy"], 0.0)

    def test_attractor_only_in_phase_three(self):
        with self.assertRaises(RuntimeError):
            compute_loss(self.state, self.target, self.model, phase=3, iteration=1)
        _, loss_dict = compute_loss(self.state, self.target, self.model, phase=1, iteration=1)
        self.assertEqual(loss_dict["attractor_divergence"], 0.0)
        attractor = torch.tensor(0.5, device=self.state.device)
        total, loss_dict = compute_loss(
            self.state, self.target, self.model, phase=3, iteration=1, attractor_loss=attractor
        )
        self.assertAlmostEqual(
            loss_dict["attractor_divergence"],
            config.LOSS_WEIGHTS["attractor_divergence"] * 0.5,
            places=5,
        )


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.device = torch.device(config.DEVICE)

    def test_curriculum_boundaries(self):
        self.assertEqual(get_current_unroll(0), config.TRAIN_BPTT_CURRICULUM[0])
        last = config.TRAIN_BPTT_CURRICULUM_AT[-1]
        self.assertEqual(get_current_unroll(last), config.TRAIN_BPTT_CURRICULUM[-1])

    def test_warmup_then_cosine(self):
        optimizer = torch.optim.SGD([torch.nn.Parameter(torch.zeros(1))], lr=config.TRAIN_LR)
        scheduler = build_lr_scheduler(optimizer)
        lrs = []
        for _ in range(config.TRAIN_MAX_STEPS):
            lrs.append(optimizer.param_groups[0]["lr"])
            optimizer.step()
            scheduler.step()
        # Warmup: линейный рост до TRAIN_LR на границе.
        self.assertLess(lrs[0], config.TRAIN_LR)
        self.assertAlmostEqual(lrs[config.TRAIN_WARMUP_STEPS - 1], config.TRAIN_LR, places=9)
        # Косинус: спад почти до нуля к концу.
        self.assertLess(lrs[-1], 0.02 * config.TRAIN_LR)
        self.assertGreater(lrs[config.TRAIN_WARMUP_STEPS + 100], lrs[-100])

    def test_phase_boundaries(self):
        self.assertEqual(resolve_phase(1, ae_available=False), 1)
        self.assertEqual(resolve_phase(config.PHASE1_STEPS, ae_available=False), 1)
        # За границей фазы 1 без AE — честная остановка (фаза 0), а не продолжение.
        self.assertEqual(resolve_phase(config.PHASE1_STEPS + 1, ae_available=False), 0)
        self.assertIn(
            resolve_phase(config.PHASE1_STEPS + 1, ae_available=True),
            (2, 3),
        )

    def test_alive_fraction_predicate(self):
        state = torch.zeros(1, config.N_CHANNELS, 4, 4, device=self.device)
        state[0, config.ALIVE_CHANNEL, :2, :2] = 10.0  # 4 из 16 живых
        self.assertAlmostEqual(alive_fraction_of(state), 0.25, places=6)


if __name__ == "__main__":
    unittest.main()
