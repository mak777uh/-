"""
test_pool_init_mode.py — диагностический режим пула WP4 (TRAIN_POOL_INIT_MODE).

Разделяет два вопроса, которые волны 1-5 путали:

  «архитектура не способна представить и удержать кольцо» (ёмкость) vs
  «нельзя вырасти из шума за горизонт BPTT» (постановка E02, §14.2).

В режиме "target" пул наполняется состоянием, где видимый канал уже равен цели,
а живы все клетки, — поэтому остаётся только удержать форму (второй критерий
§14.2). Проверки ниже закрепляют, что это состояние действительно ИДЕАЛЬНОЕ
стартовое (f1=1, MSE~0), что оно проходит ПРАВИЛО 31 и что дефолт остаётся
"noise" — контракт §14.2 по умолчанию не меняется.
"""

import unittest

import torch

import config


class TestConfigContract(unittest.TestCase):
    def test_default_is_noise_contract(self):
        """Дефолт — рост из шума (§14.2); диагностический режим включается явно."""
        self.assertEqual(config.TRAIN_POOL_INIT_MODE, "noise")

    def test_validate_accepts_both_modes(self):
        original = config.TRAIN_POOL_INIT_MODE
        try:
            for mode in ("noise", "target"):
                config.TRAIN_POOL_INIT_MODE = mode
                config.validate()
        finally:
            config.TRAIN_POOL_INIT_MODE = original

    def test_validate_rejects_unknown_mode(self):
        original = config.TRAIN_POOL_INIT_MODE
        try:
            config.TRAIN_POOL_INIT_MODE = "blur"
            with self.assertRaises(AssertionError):
                config.validate()
        finally:
            config.TRAIN_POOL_INIT_MODE = original


class TestTargetConditionedState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from nca_core import target_conditioned_state
        from target_patterns import create_target

        cls.target = create_target(device="cpu")
        cls.state = target_conditioned_state(
            cls.target, batch_size=2, channels=config.N_CHANNELS, device="cpu"
        )

    def _alive_fraction(self):
        alpha = torch.sigmoid(self.state[:, config.ALIVE_CHANNEL, :, :])
        return float((alpha > config.ALIVE_THRESHOLD).float().mean())

    def test_all_cells_alive(self):
        """Живы ВСЕ клетки: у цели ring плотность 0.1523 < FRESH_MIN_ALIVE_FRACTION
        0.20, поэтому «живой только контур цели» нарушил бы ПРАВИЛО 31."""
        self.assertAlmostEqual(self._alive_fraction(), 1.0, places=6)

    def test_passes_fresh_state_rule(self):
        from nca_core import _validate_fresh_state

        self.assertTrue(_validate_fresh_state(self.state))

    def test_visible_channel_equals_target(self):
        """Бинаризация видимого канала воспроизводит цель точно: f1 = 1.0 и
        visible_mse близок к нулю, то есть старт — оптимум, а не половина."""
        from evaluate import compute_coverage_endpoints

        image = torch.sigmoid(self.state[:, config.VISIBLE_CHANNEL : config.VISIBLE_CHANNEL + 1])
        target_b = (self.target[:, 0] > 0.5)
        mse = float(((image[:, 0] - target_b.float()) ** 2).mean())
        self.assertLess(mse, 0.001)
        target_np = target_b[0].numpy().astype("uint8")
        pred_np = (image[0, 0] > 0.5).numpy().astype("uint8")
        self.assertEqual(compute_coverage_endpoints(pred_np, target_np)["f1"], 1.0)

    def test_stress_channel_zero(self):
        self.assertEqual(float(self.state[:, config.STRESS_CHANNEL].abs().max()), 0.0)

    def test_hidden_channels_zero(self):
        hidden = self.state[:, 2:12]
        self.assertEqual(float(hidden.abs().max()), 0.0)

    def test_is_deterministic(self):
        """Без генератора: повторный вызов даёт тот же тензор (§9.2)."""
        from nca_core import target_conditioned_state

        again = target_conditioned_state(
            self.target, batch_size=2, channels=config.N_CHANNELS, device="cpu"
        )
        self.assertTrue(torch.equal(self.state, again))


class TestPoolUsesFreshFn(unittest.TestCase):
    def test_fresh_fn_drives_reset(self):
        """Сброс пула (ПРАВИЛО 29) обязан брать состояние из fresh_fn, иначе
        периодический сброс молча вернул бы шум и диагноз «не может» перепутался
        бы с «не успела вырасти»."""
        from nca_core import StatePool, target_conditioned_state
        from target_patterns import create_target

        target = create_target(device="cpu")
        calls = {"n": 0}

        def fresh():
            calls["n"] += 1
            return target_conditioned_state(target, batch_size=1, device="cpu")

        pool = StatePool(size=3, device="cpu", batch_size=1, fresh_fn=fresh)
        # Конструктор тоже наполняет через fresh_fn.
        self.assertGreaterEqual(calls["n"], 3)
        for s in pool.states:
            alpha = torch.sigmoid(s[:, config.ALIVE_CHANNEL, :, :])
            self.assertAlmostEqual(float((alpha > config.ALIVE_THRESHOLD).float().mean()), 1.0)
        before = calls["n"]
        pool.replace_all_fresh()
        self.assertGreater(calls["n"], before)

    def test_default_pool_is_noise(self):
        """Без fresh_fn поведение пула не меняется (§14.2)."""
        from nca_core import StatePool

        pool = StatePool(size=2, device="cpu", batch_size=1)
        self.assertIsNone(pool.fresh_fn)
        alpha = torch.sigmoid(pool.states[0][:, config.ALIVE_CHANNEL, :, :])
        # Шум: живых клеток много, но не все 100%.
        self.assertGreater(float((alpha > config.ALIVE_THRESHOLD).float().mean()), 0.0)
        self.assertLess(float((alpha > config.ALIVE_THRESHOLD).float().mean()), 1.0)


if __name__ == "__main__":
    unittest.main()
