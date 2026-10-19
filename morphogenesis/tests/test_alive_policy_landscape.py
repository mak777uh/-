"""
test_alive_policy_landscape.py — фиксирует диагноз WP4 (гипотеза H-A) как
тест, а не как заметку в логе.

Суть измерения — ландшафт цели на пяти рукотворных состояниях (см.
wp4_collapse_probe.candidates). Числа ниже считаются БЕЗ топологического
члена; в experiments/E02_pattern/collapse_probe.json те же состояния оценены
с ним и отличаются ровно на его вклад (~0.39).

При ALIVE_POLICY_MODE="supervised_mse" — буквальном прочтении §12.6.3
«супервизия альфа-канала» как MSE(sigmoid(alpha), цель>0) — лосс правильной
мёртвой точки (0.3882) НИЖЕ, чем лосс любой ткани, в которую можно попасть из
неё одним однородным шагом: живое серое поле 0.6929, живое чёрное 0.5808,
собранное кольцо при всеобщей живости 0.4182. Мёртвая клетка обнуляется
AliveSTE целиком, поэтому всё состояние мёртвой ткани — константа, и выход
из неё тоже обязан быть константным по всему полю. Отсюда и death-spiral:
спуск приводит в точку, из которой любой шаг вверх по склону.

При ALIVE_POLICY_MODE="death_penalty" (штрафуется только смерть ТАМ, где
цель требует ткани; жизнь вне цели не наказывается — форму паттерна задаёт
канал 0 по §3.3) порядок становится физически правильным: мёртвое поле
0.3012 дороже живого чёрного 0.1631, а градиент по alpha не толкает ни одну
клетку в смерть.

Третий режим — "survival" («не убий»: mean(relu(-d_alpha)·sigmoid(alpha))) —
зафиксирован здесь отдельно, потому что у него есть измеренная особенность,
о которой иначе потом забудут:

* на модели в покое (§12.2.2: последний слой CellBrain инициализирован
  нулями, значит delta тождественно 0) член survival РОВЕН НОЛЮ. Он физически
  не может спасти инициализацию — у него нет сигнала до тех пор, пока динамика
  не появилась из других членов.
* когда динамика всё-таки есть (проверено на модели со случайными весами
  последнего слоя, seed 1, sigma 0.05), член выходит порядка 1e-4 —
  на три порядка меньше visible_mse (~0.25). С весом 0.5 по §12.6.3 это
  означает, что «не убий» не является силой, способной удержать ткань
  против остальных членов; он годится лишь как страховка, если основной член
  уже стал односторонним.

Тест ничего не «чинит» — он запрещает молча сменить формулу alive_policy и
потерять этот результат.
"""

import unittest

import config

import torch

# Пешечные константы измерения. Держим CPU: результат не должен зависеть от
# того, на каком железе гоняют тест (CUDA-ядро в этом файле не нужен).
# Числа считаются БЕЗ топологического члена (topo_proxy=None); в
# experiments/E02_pattern/collapse_probe.json те же состояния оценены С ним,
# поэтому там все значения выше ровно на его вклад (~0.39).
BATCH = 2
DEAD_SUPERVISED = 0.3882
GREY_SUPERVISED = 0.6929
BLACK_SUPERVISED = 0.5808
RING_ALL_ALIVE_SUPERVISED = 0.4182
DEAD_DEATH_PENALTY = 0.3012
BLACK_DEATH_PENALTY = 0.1631
DEAD_SURVIVAL = 0.2632
RING_SURVIVAL = 0.0001
TOL = 0.02


class TestAlivePolicyLandscape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from target_patterns import create_target
        from wp4_collapse_probe import candidates

        cls.original_mode = config.ALIVE_POLICY_MODE
        cls.original_device = config.DEVICE
        config.DEVICE = "cpu"
        cls.target = create_target(device="cpu")
        cls.target_bin = (cls.target > 0).float()
        cls.cands = candidates(cls.target, BATCH)
        # Фиксированные веса: лоссы выше — это измерение на СОВСЕМ этом же
        # инициализированном модели, а не «среднее по случайным».
        torch.manual_seed(0)
        from nca_core import NeuralCellularAutomaton

        cls.model = NeuralCellularAutomaton()
        cls.model.eval()

    @classmethod
    def tearDownClass(cls):
        config.ALIVE_POLICY_MODE = cls.original_mode
        config.DEVICE = cls.original_device

    def _totals(self, mode):
        from train import compute_loss

        config.ALIVE_POLICY_MODE = mode
        out = {}
        with torch.no_grad():
            for name, state in self.cands.items():
                # topo_proxy=None: сравниваем геометрическую часть цели,
                # топологический член здесь только шум добавляет (§2.10).
                _, parts = compute_loss(
                    state, self.target, self.model, phase=1, topo_proxy=None, iteration=1
                )
                out[name] = parts["total"]
        return out

    def _descent(self, mode, state):
        from wp4_collapse_probe import gradient_direction

        config.ALIVE_POLICY_MODE = mode
        return gradient_direction(self.model, self.target, state, self.target_bin)

    def _parts(self, state, model):
        """compute_loss без топологического члена (см. шапку модуля)."""
        from train import compute_loss

        with torch.no_grad():
            _, parts = compute_loss(state, self.target, model, phase=1, topo_proxy=None, iteration=1)
        return parts

    def _alive_term(self, mode, model, state):
        config.ALIVE_POLICY_MODE = mode
        parts = self._parts(state, model)
        return parts["alive_policy"], parts["visible_mse"]

    def _randomized_model(self):
        """
        Копия модели в покое со случайными весами последнего слоя CellBrain.
        Нужна ровно для одного: у обнулённого слоя delta тождественно 0, и
        любой член, зависящий от delta, на ней молчит. Seed фиксирован — числа
        воспроизводимы.
        """
        import copy

        model = copy.deepcopy(self.model)
        gen = torch.Generator().manual_seed(1)
        with torch.no_grad():
            model.brain.net[-1].weight.normal_(0.0, 0.05, generator=gen)
            model.brain.net[-1].bias.normal_(0.0, 0.05, generator=gen)
        model.eval()
        return model

    # --- 1. ловушка смерти при MSE-супервизии -------------------------------

    def test_supervised_mse_death_is_a_local_trap(self):
        """
        Из мёртвого поля все достижимые живые состояния ДОРОЖЕ смерти —
        значит градиентный спуск не может из него выбраться.
        """
        t = self._totals("supervised_mse")
        self.assertAlmostEqual(t["dead_zero_state"], DEAD_SUPERVISED, delta=TOL)
        self.assertAlmostEqual(t["alive_blank_grey"], GREY_SUPERVISED, delta=TOL)
        self.assertAlmostEqual(t["alive_blank_black"], BLACK_SUPERVISED, delta=TOL)
        self.assertAlmostEqual(t["ring_alive_everywhere"], RING_ALL_ALIVE_SUPERVISED, delta=TOL)
        for name in ("alive_blank_grey", "alive_blank_black", "ring_alive_everywhere"):
            self.assertGreater(
                t[name],
                t["dead_zero_state"],
                f"{name} не должно быть дешевле смерти, иначе ловушки нет",
            )

    def test_supervised_mse_pushes_background_cells_to_death(self):
        d = self._descent("supervised_mse", self.cands["alive_blank_grey"])
        self.assertLess(d["descent_dalpha_outside_target"], 0.0)
        self.assertGreater(d["frac_cells_pushed_to_death"], 0.5)

    # --- 2. лечение: односторонний штраф ------------------------------------

    def test_death_penalty_makes_alive_cheaper_than_death(self):
        t = self._totals("death_penalty")
        self.assertAlmostEqual(t["dead_zero_state"], DEAD_DEATH_PENALTY, delta=TOL)
        self.assertAlmostEqual(t["alive_blank_black"], BLACK_DEATH_PENALTY, delta=TOL)
        for name in ("alive_blank_black", "ring_alive_everywhere", "ring_alive_only_in_target"):
            self.assertLess(t[name], t["dead_zero_state"], name)

    def test_death_penalty_never_pushes_cells_to_death(self):
        for state_name in ("alive_blank_grey", "dead_zero_state"):
            d = self._descent("death_penalty", self.cands[state_name])
            self.assertEqual(
                d["frac_cells_pushed_to_death"],
                0.0,
                f"из {state_name}: ни одна клетка не должна получать градиент к смерти",
            )

    def test_death_penalty_still_requires_the_pattern(self):
        """
        Односторонний штраф не должен превращаться в «живи где хочешь и ничего
        не собирай»: собранная цель обязана быть строго дешевле пустой ткани.
        """
        t = self._totals("death_penalty")
        self.assertLess(t["ring_alive_everywhere"], t["alive_blank_grey"])
        self.assertLess(t["ring_alive_only_in_target"], t["alive_blank_black"])

    # --- 3. третий режим: «не убий» ------------------------------------------

    def test_survival_makes_alive_states_cheaper_than_death(self):
        """
        Порядок при survival (измерено, seed 0, модель в покое): кольцо 0.0001,
        чёрное поле 0.1626, мёртвое 0.2632, серое 0.2748. Ловушки «смерть
        дешевле любой ткани», как в supervised_mse, здесь нет: собранное кольцо
        строго дешевле смерти, и в него можно попасть спуском.
        """
        t = self._totals("survival")
        self.assertAlmostEqual(t["dead_zero_state"], DEAD_SURVIVAL, delta=TOL)
        self.assertAlmostEqual(t["ring_alive_everywhere"], RING_SURVIVAL, delta=TOL)
        self.assertLess(t["ring_alive_everywhere"], t["dead_zero_state"])
        self.assertLess(t["ring_alive_only_in_target"], t["alive_blank_black"])

    def test_survival_ignores_the_dead_but_punishes_losing_life(self):
        """
        Смерть абсорбирующая (§5.2), а вес члена — sigmoid(alpha): у мёртвой
        ткани штрафовать некого, член практически 0. Это осознанное свойство
        («не убий» ничего не требует от трупов), но оно же означает, что
        survival никогда не вытащит ткань из вымершего состояния — для этого
        нужен член, который делает ЖИВОЕ состояние дешевле мёртвого.

        Проверка сделана на модели со случайными весами последнего слоя,
        потому что на обнулённом (см. test_survival_term_is_silent_at_rest)
        член равен нулю тривиально и тест ничего бы не проверял.
        """
        model = self._randomized_model()
        delta = model.get_delta(self.cands["alive_blank_grey"])
        self.assertFalse(bool(torch.all(delta == 0)), "случайный слой обязан давать delta != 0")

        dead_terms = [
            self._alive_term("survival", model, self.cands[name])[0]
            for name in ("dead_zero_state", "dead_alpha_minus5")
        ]
        for name, value in zip(
            ("dead_zero_state", "dead_alpha_minus5"), dead_terms, strict=True
        ):
            self.assertLessEqual(value, 1e-9, f"{name}: мёртвых штрафовать нельзя")

        alive_terms = {name: self._alive_term("survival", model, state)[0] for name, state in self.cands.items()}
        self.assertGreater(
            max(alive_terms.values()),
            1e-6,
            f"член обязан включаться там, где живая клетка теряет живость: {alive_terms}",
        )

    def test_survival_term_is_silent_at_rest(self):
        """
        §12.2.2: последний слой CellBrain обнулён, поэтому на модели в покое
        delta == 0 и relu(-0) == 0 -> survival-член равен нулю на ЛЮБОМ
        состоянии. Режим нельзя продавать как лечение инициализации: он
        начинает что-то значить только после того, как динамика выучится по
        другим членам. Проверка держит это как контракт, а не как случайность.
        """
        config.ALIVE_POLICY_MODE = "survival"
        delta = self.model.get_delta(self.cands["alive_blank_grey"])
        self.assertTrue(bool(torch.all(delta == 0)), "ожидание §12.2.2: обнулённый слой -> delta = 0")
        for name, state in self.cands.items():
            parts = self._parts(state, self.model)
            self.assertEqual(parts["alive_policy"], 0.0, f"{name}: в покое член должен молчать")

    def test_survival_term_is_tiny_next_to_visible_mse(self):
        """
        Масштабная проверка (модель со случайными весами последнего слоя):
        когда член ненулевой, он на ~3 порядка меньше visible_mse. Если кто-то
        решит, что survival «решил коллапс», этот тест заставит показать, за
        счёт какого веса именно это произошло.
        """
        model = self._randomized_model()
        pairs = [self._alive_term("survival", model, state) for state in self.cands.values()]
        for value, _ in pairs:
            self.assertGreaterEqual(value, 0.0)
        biggest = max(value for value, _ in pairs)
        # Ориентир — visible_mse самого «дорогого» кандидата (пустое поле,
        # ~0.25). Относительно конкретной формы относить нельзя: на собранном
        # кольце visible_mse сам стремится к нулю.
        reference = max(visible for _, visible in pairs)
        self.assertGreater(biggest, 0.0, "на случайных весах член обязан хоть где-то включиться")
        self.assertLess(
            biggest,
            0.02 * float(reference),
            "survival-член вырос относительно visible_mse — пересмотреть вес/формулу",
        )

    def test_survival_mode_keys_match_spec(self):
        """Контракт §12.6.3 не зависит от режима: набор членов тот же."""
        from train import compute_loss

        config.ALIVE_POLICY_MODE = "survival"
        with torch.no_grad():
            _, parts = compute_loss(
                self.cands["alive_blank_grey"],
                self.target,
                self.model,
                phase=1,
                topo_proxy=None,
                iteration=1,
            )
        self.assertEqual(
            set(parts),
            {
                "total",
                "visible_mse",
                "alive_policy",
                "hidden_reg",
                "stress_proxy",
                "topo_proxy",
                "attractor_divergence",
                "alive_fraction",
                "frac_delta_nonzero",
            },
        )

    # --- 4. контракт §12.6.3 соблюдается во всех режимах ----------------------

    def test_both_modes_keep_loss_weight_contract(self):
        from train import compute_loss

        for mode in config.ALIVE_POLICY_MODES:
            config.ALIVE_POLICY_MODE = mode
            with torch.no_grad():
                _, parts = compute_loss(
                    self.cands["alive_blank_grey"],
                    self.target,
                    self.model,
                    phase=1,
                    topo_proxy=None,
                    iteration=1,
                )
            for key in ("total", "visible_mse", "alive_policy", "hidden_reg", "stress_proxy", "topo_proxy"):
                self.assertIn(key, parts, f"{mode}: потерян член {key}")
            self.assertGreaterEqual(parts["alive_policy"], 0.0)

    def test_invalid_mode_is_rejected(self):
        config.ALIVE_POLICY_MODE = "bogus"
        try:
            with self.assertRaises(AssertionError):
                config.validate()
        finally:
            config.ALIVE_POLICY_MODE = self.original_mode


if __name__ == "__main__":
    unittest.main()
