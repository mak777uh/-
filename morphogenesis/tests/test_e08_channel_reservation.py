"""
test_e08_channel_reservation.py — резервирование каналов 12–14 (§3.5, §12.6.9).

Гипотеза E08 требует, чтобы скрытые каналы были НЕЗАВИСИМЫМ ресурсом памяти:
если базовое обучение «оккупирует» их под целевую форму, эксперимент E08
нечем измерять. Отсюда три проверяемых требования:

1. системный код (морфоген, старческий шум) не пишет в 12–14;
2. во время обучения 12–14 проходят dropout+шум, а на инференсе состояние
   детерминировано (стохастика обучения не имеет права проникать в эксперимент);
3. при наличии обученного чекпоинта — нулевая проверка: форма, посчитанная с
   обнулёнными 12–14, деградирует не более чем на 20% (иначе каналы уже
   «забиты» целью и E08 будет артефактом). Тест помечен skip, пока чекпоинта
   нет: это гейт WP3, а не проверка кода.
"""

import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from nca_core import NeuralCellularAutomaton, init_state, run_steps_no_grad
from target_patterns import create_target


CKPT = os.path.join(config.CHECKPOINT_DIR, "nca_best.pt")


class TestConfigReservation(unittest.TestCase):
    def test_reserved_channels_are_12_13_14_15(self):
        self.assertEqual(config.ENTRAINMENT_CHANNELS, [12, 13, 14])
        self.assertEqual(config.RESERVED_HIDDEN_CHANNELS, [12, 13, 14, 15])

    def test_morphogen_range_excludes_reserved(self):
        for channel in range(config.MORPHOGEN_MIN_CHANNEL, config.MORPHOGEN_MAX_CHANNEL + 1):
            self.assertNotIn(channel, config.RESERVED_HIDDEN_CHANNELS)

    def test_aging_noise_excludes_reserved(self):
        for channel in config.AGING_NOISE_CHANNELS:
            self.assertNotIn(channel, config.RESERVED_HIDDEN_CHANNELS)

    def test_reservation_parameters_in_range(self):
        self.assertTrue(0.0 <= config.ENTRAINMENT_CHANNEL_DROPOUT_PROB <= 1.0)
        self.assertGreaterEqual(config.ENTRAINMENT_CHANNEL_NOISE_STD, 0.0)
        self.assertLessEqual(config.ENTRAINMENT_CHANNEL_IMPORTANCE_MAX, 0.2)

    def test_channel_dropout_touches_only_hidden_working_memory(self):
        """§12.1.6: dropout восприятия не касается служебных и зарезервированных."""
        for channel in config.CHANNEL_DROPOUT_CHANNELS:
            self.assertNotIn(channel, config.RESERVED_HIDDEN_CHANNELS)
            self.assertNotIn(channel, (config.ALIVE_CHANNEL, config.VISIBLE_CHANNEL))


class TestForwardBehaviour(unittest.TestCase):
    def setUp(self):
        self.device = torch.device(config.DEVICE)
        torch.manual_seed(config.SEED)
        self.model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(self.device)
        self.model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        self.model.alive_mask_enabled = False

    def _state(self):
        return init_state(
            batch_size=2,
            device=self.device,
            generator=torch.Generator(device="cpu").manual_seed(config.SEED),
        )

    def test_training_applies_reservation_dropout(self):
        """На обучении 12–14 хотя бы иногда зануляются целиком."""
        self.model.train()
        zeros = 0
        for _ in range(12):
            out = self.model(self._state(), noise_key=id(self) + _)
            for channel in config.ENTRAINMENT_CHANNELS:
                if float(out[:, channel].abs().max()) == 0.0:
                    zeros += 1
        self.assertGreater(zeros, 0, "dropout резервированных каналов не срабатывает ни разу")

    def test_eval_mode_is_deterministic_and_untouched(self):
        """§3.5/§12.1.6: на инференсе ни dropout, ни шум резервирования."""
        self.model.eval()
        state = self._state()
        with torch.no_grad():
            a = run_steps_no_grad(self.model, state.clone(), steps=3)
            b = run_steps_no_grad(self.model, state.clone(), steps=3)
        self.assertTrue(torch.allclose(a, b), "инференс недетерминирован")
        # Занулённые каналы на инференсе появляются только из-за alive-политики,
        # которая здесь выключена — значит резервные каналы сохранены.
        for channel in config.ENTRAINMENT_CHANNELS:
            self.assertGreater(float(a[:, channel].abs().max()), 0.0)


class TestBridgeDoesNotWriteReserved(unittest.TestCase):
    """
    Резервные каналы (§3.5) недоступны агенту: действие либо отвергается
    валидатором, либо клампится ниже 12. «Молча записать в 13» — не вариант.
    """

    def test_morphogen_on_reserved_channel_never_writes_it(self):
        import cognition.bridge as bridge

        parsed = {
            "action": "INJECT_MORPHOGEN",
            "params": {"channel": 13, "value": 1.0, "x": 4, "y": 4, "radius": 2},
            "valid": True,
        }
        result = bridge.apply_action(parsed, budget_remaining=100.0, current_report_number=5)
        injection = (result.get("changes") or {}).get("morphogen")
        if injection is None:
            # Отвергнуто — приемлемо, но отказ обязан быть объяснён.
            self.assertTrue(
                result.get("reason") or result.get("note"),
                "действие пропало без причины — это и есть «агент делает вид»",
            )
            return
        self.assertLess(int(injection["channel"]), min(config.ENTRAINMENT_CHANNELS))


@unittest.skipUnless(os.path.exists(CKPT), "гейт WP3: нужен обученный чекпоинт E02")
class TestE08Measurability(unittest.TestCase):
    def test_zeroing_reserved_channels_costs_at_most_20_percent(self):
        from evaluate import compute_symmetric_chamfer_error
        from topology import get_binary_mask

        device = torch.device(config.DEVICE)
        ckpt = torch.load(CKPT, map_location=device, weights_only=False)
        config.assert_checkpoint_compatible(ckpt, context="test_e08")
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()
        state = ckpt["state"].to(device)
        target = create_target(device=device)[0, 0].detach().cpu().numpy() > 0.5

        baseline = compute_symmetric_chamfer_error(get_binary_mask(state), target)
        ablated = state.clone()
        ablated[:, config.ENTRAINMENT_CHANNELS] = 0.0
        with torch.no_grad():
            rolled = run_steps_no_grad(model, ablated, steps=32)
        degraded = compute_symmetric_chamfer_error(get_binary_mask(rolled), target)

        self.assertLess(
            degraded,
            baseline * 1.2 + 1e-6,
            f"E08 неизмерим: обнуление 12–14 ухудшило Chamfer с {baseline:.3f} "
            f"до {degraded:.3f} (> 20%) — каналы уже несут целевую форму",
        )


if __name__ == "__main__":
    unittest.main()
