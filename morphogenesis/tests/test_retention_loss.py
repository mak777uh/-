"""
test_retention_loss.py — член удержания §14.2 («вырастить из шума И удержать»).

WP4 измерил, что блокер E02 — не ёмкость: из пула-цели модель удерживает кольцо
(f1=1.0000, H-P1), а из шума форма локализуется, но после 200 автономных шагов
лучший gated f1 падает с 0.4747 до 0.2783 (NEG-10), и на постановке без удержания
ткань умирает на итерации 200 у 5 сидов из 5 (NEG-17). Причина структурная:
supervised_mse наказывает расхождение с ОДНИМ целевым кадром, и его оптимум
достижим полем, которое дальше не эволюционирует. Отсюда решение владельца спеки
— перенести «удержать» из текста гейта в целевую функцию: дифференцируемый
roll-out на K автономных шагов.

Тесты закрепляют то, что делает такой перенос честным.

  1. По умолчанию члена нет, и лосс совпадает со спекой §12.6.3 (контракт молча
     не меняется); включается только явным конфигом.
  2. RETENTION_ENABLED=True при нулевом весе запрещён validate(): иначе прогон
     подписывался бы retention-прогоном, не будучи им.
  3. Через roll-out действительно идёт градиент — иначе «удержание» было бы
     наблюдателем, а не членом лосса.
  4. Survival-штраф наказывает потерю живости, а не любое изменение альфа-канала:
     без него retention-MSE путает «держит кольцо» и «замершее мёртвое поле».
  5. Гейты RETENTION_EVERY и RETENTION_START_ITER работают предсказуемо — это
     экономия VRAM, и она не должна зависеть от номера итерации «на глаз».
  6. Две формы survival-члена (transition/level) ведут себя по-разному на
     поглощающей смерти, и разница измерена (NEG-18): transition на мёртвом
     поле тождественно 0, level видит её как число, но градиент nonzero только
     пока клетка ещё живая. То есть член — предотвращение, а не воскрешение.
  7. Парный quiet-член (налог на живость ВНЕ цели на той же roll-out
     траектории) закрывает вторую половину полосы: без неё level-survival даёт
     «живо всё» — R-8 дожил до 1000-й итерации при f1 ≤ 0.211 (NEG-20). quiet
     молчит на мёртвом фоне (наказывать не за что), говорит числами на живом,
     не трогает клетки цели, и при весе 0.0 оставляет сумму прежней — прогоны
     R-1…R-8 должны и дальше означать ровно то, что записано.
"""

import os

import sys

import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from nca_core import NeuralCellularAutomaton

from target_patterns import create_target

from train import compute_loss, retention_rollout_loss


SPEC_TERM_KEYS = (
    "visible_mse",
    "alive_policy",
    "hidden_regularization",
    "stress_proxy",
    "topo_proxy",
)


class _StubModel:
    """Шаг = state + delta, где delta — обучаемый вектор каналов.

    Нужна, чтобы проверить смысл survival-штрафа изолированно: у настоящей NCA за
    один шаг нельзя гарантированно получить «была жива — стала мертва», а
    утверждать «штраф положительный» по одному случайному прогону нельзя.
    """

    def __init__(self, kill):
        self.kill = bool(kill)
        self.delta = torch.zeros(config.N_CHANNELS, requires_grad=True)

    def __call__(self, state):
        step = self.delta.view(1, -1, 1, 1).clone()
        if self.kill:
            # Сдвиг альфа-канала вниз на 20·sigmoid(delta): знак штрафа зависит от
            # параметра, поэтому градиент через roll-out остаётся нетривиальным.
            step[0, config.ALIVE_CHANNEL] = -20.0 * torch.sigmoid(self.delta[0])
        return state + step

    def visible_image(self, state):
        return torch.sigmoid(state[:, 0 : config.VISIBLE_CHANNEL + 1])


def _small_state(alive=3.0, visible=3.0):
    state = torch.zeros(1, config.N_CHANNELS, 4, 4)
    state[:, config.ALIVE_CHANNEL] = alive
    state[:, config.VISIBLE_CHANNEL] = visible
    return state


class TestRetentionDefaultOff(unittest.TestCase):
    def test_defaults_keep_spec_loss(self):
        """Состояние «как в спеке»: член выключен, вес нулевой."""
        self.assertFalse(config.RETENTION_ENABLED)
        self.assertAlmostEqual(float(config.LOSS_WEIGHTS["retention"]), 0.0)

    def test_enabled_flag_with_zero_weight_changes_nothing(self):
        """Вес — единственный источник истины для суммы; флажок лишь разрешает
        работу, и при нулевом весе он не должен ни добавлять член, ни менять
        лосс: иначе «выключенный» retention всё-таки влиял бы на обучение."""
        device = torch.device(config.DEVICE)
        torch.manual_seed(config.SEED)
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
        model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        model.train()
        target = create_target(device=device)
        state = torch.randn(
            2, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=device
        )
        state[:, config.ALIVE_CHANNEL] = 1.0
        original = config.RETENTION_ENABLED
        try:
            config.RETENTION_ENABLED = True
            config.LOSS_WEIGHTS["retention"] = 0.0
            _total, loss_dict, weighted = compute_loss(
                state, target, model, iteration=7, return_terms=True
            )
            self.assertNotIn("retention", weighted)
            self.assertEqual(loss_dict["retention_mse"], 0.0)
            self.assertAlmostEqual(
                loss_dict["total"],
                sum(float(weighted[k]) for k in SPEC_TERM_KEYS),
                places=6,
            )
        finally:
            config.RETENTION_ENABLED = original
            config.LOSS_WEIGHTS["retention"] = 0.0

    def test_validate_rejects_enabled_with_zero_weight(self):
        original = (config.RETENTION_ENABLED, float(config.LOSS_WEIGHTS["retention"]))
        try:
            config.RETENTION_ENABLED = True
            config.LOSS_WEIGHTS["retention"] = 0.0
            with self.assertRaises(AssertionError):
                config.validate()
            config.LOSS_WEIGHTS["retention"] = 0.5
            config.validate()
        finally:
            config.RETENTION_ENABLED = original[0]
            config.LOSS_WEIGHTS["retention"] = original[1]
            config.validate()


class TestRetentionActive(unittest.TestCase):
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
        self.saved = {
            "enabled": config.RETENTION_ENABLED,
            "weight": float(config.LOSS_WEIGHTS["retention"]),
            "steps": config.RETENTION_ROLLOUT_STEPS,
            "survival": config.RETENTION_SURVIVAL_WEIGHT,
            "every": config.RETENTION_EVERY,
            "start": config.RETENTION_START_ITER,
        }

    def tearDown(self):
        config.RETENTION_ENABLED = self.saved["enabled"]
        config.LOSS_WEIGHTS["retention"] = self.saved["weight"]
        config.RETENTION_ROLLOUT_STEPS = self.saved["steps"]
        config.RETENTION_SURVIVAL_WEIGHT = self.saved["survival"]
        config.RETENTION_EVERY = self.saved["every"]
        config.RETENTION_START_ITER = self.saved["start"]

    def test_total_equals_spec_sum_plus_retention(self):
        config.RETENTION_ENABLED = True
        config.LOSS_WEIGHTS["retention"] = 1.0
        config.RETENTION_ROLLOUT_STEPS = 2
        _total, loss_dict, weighted = compute_loss(
            self.state, self.target, self.model, iteration=3, return_terms=True
        )
        self.assertIn("retention", weighted)
        self.assertGreater(loss_dict["retention_mse"], 0.0)
        self.assertAlmostEqual(
            loss_dict["total"],
            sum(float(v) for v in weighted.values()),
            places=6,
            msg="retention вошёл в сумму, но не в weighted — атрибуция лосса разъедется",
        )

    def test_gradient_reaches_params_through_rollout(self):
        config.RETENTION_ENABLED = True
        config.LOSS_WEIGHTS["retention"] = 1.0
        target_expanded = self.target.expand(self.state.shape[0], -1, -1, -1)
        mse, survival, _quiet = retention_rollout_loss(
            self.model, self.state, target_expanded, steps=2
        )
        self.assertTrue(mse.requires_grad, "roll-out без градиента — это наблюдатель")
        self.assertTrue(survival.requires_grad)
        (mse + survival).backward()
        total_grad = sum(
            float(p.grad.abs().sum()) for p in self.model.parameters() if p.grad is not None
        )
        self.assertGreater(total_grad, 0.0, "через roll-out не идёт градиент")

    def test_gates_by_iteration(self):
        config.RETENTION_ENABLED = True
        config.LOSS_WEIGHTS["retention"] = 1.0
        config.RETENTION_EVERY = 2
        _t, _d, weighted = compute_loss(
            self.state, self.target, self.model, iteration=3, return_terms=True
        )
        self.assertNotIn("retention", weighted, "roll-out считается вне RETENTION_EVERY")
        _t, loss_dict, weighted = compute_loss(
            self.state, self.target, self.model, iteration=4, return_terms=True
        )
        self.assertIn("retention", weighted)
        self.assertGreater(loss_dict["retention_mse"], 0.0)
        # Старт раньше RETENTION_START_ITER запрещён: до warmup alive-маски
        # «потеря живости» не имеет смысла.
        config.RETENTION_EVERY = 1
        config.RETENTION_START_ITER = 50
        _t, _d, weighted = compute_loss(
            self.state, self.target, self.model, iteration=49, return_terms=True
        )
        self.assertNotIn("retention", weighted)


class TestSurvivalPenalty(unittest.TestCase):
    """Штраф за переход живая->мёртвая, а не за любое изменение альфа-канала."""

    def _run(self, kill):
        saved = (config.GRAD_CHECKPOINTING, config.RETENTION_ROLLOUT_STEPS)
        try:
            config.GRAD_CHECKPOINTING = False
            config.RETENTION_ROLLOUT_STEPS = 2
            stub = _StubModel(kill=kill)
            mse, survival, quiet = retention_rollout_loss(
                stub, _small_state(), torch.zeros(1, 1, 4, 4), steps=2
            )
            return mse, survival, quiet, stub
        finally:
            config.GRAD_CHECKPOINTING, config.RETENTION_ROLLOUT_STEPS = saved

    def test_death_is_penalized(self):
        _mse, survival, _quiet, _stub = self._run(kill=True)
        self.assertGreater(float(survival), 0.0)

    def test_stable_alive_field_is_not_penalized(self):
        _mse, survival, _quiet, _stub = self._run(kill=False)
        self.assertAlmostEqual(float(survival), 0.0, places=6)

    def test_rollout_is_differentiable_through_stub_parameter(self):
        _mse, survival, _quiet, stub = self._run(kill=True)
        survival.backward()
        self.assertIsNotNone(stub.delta.grad)
        self.assertGreater(float(stub.delta.grad.abs().sum()), 0.0)

    def test_quiet_is_the_other_half_on_the_same_trajectory(self):
        """Две половины одного roll-out ловят разные вырождения.

        Здесь цель — пустая (torch.zeros), значит live_required пуст, и вся
        ткань «вне цели». Стаб с kill=False оставляет живые клетки живыми
        (alpha = sigmoid(3.0) = 0.95): survival (transition) молчит, потому что
        никто не умирает, а quiet шумит, потому что живость вне цели = 0.45 над
        порогом. Это ровно форма «живо всё» из R-8, которую survival не видит
        НИКАКИМ весом. С kill=True клетки выключаются: quiet падает в 0,
        survival становится положительным. То есть члены не дублируют друг
        друга, а закрывают два разных конца полосы.
        """
        _mse, surv_alive, quiet_alive, _stub = self._run(kill=False)
        _mse, surv_dead, quiet_dead, _stub = self._run(kill=True)
        self.assertAlmostEqual(float(surv_alive), 0.0, places=6)
        self.assertGreater(float(quiet_alive), 0.0)
        self.assertGreater(float(surv_dead), 0.0)
        self.assertAlmostEqual(float(quiet_dead), 0.0, places=6)


class TestLevelSurvivalSeesAbsorbingDeath(unittest.TestCase):
    """Замеренное различие двух форм survival-члена (NEG-18).

    Мёртвая клетка по AliveSTE имеет обнулённое состояние (§5.2), значит
    alpha = sigmoid(0) = 0.5 = ALIVE_THRESHOLD ровно. Отсюда два следствия,
    которые здесь закреплены числами, а не рассуждением:

      1. transition-форма relu(alpha_prev − alpha)·alpha_prev на таком поле
         тождественно 0 — она не видит смерть, и в прогоне R-1 дала 1.9e-4…8.5e-4
         при visible_mse 0.25 (вклад в total ~5e-5, траектория не изменилась);
      2. level-форма relu(threshold + margin − alpha) даёт ровно margin — но
         ГРАДИЕНТ у неё nonzero только пока клетка ещё живая (alpha в полосе
         (0.5, 0.6)). На уже мёртвой клетке градиент обеих форм ровно 0:
         поглощающую смерть не может отменить НИКАКОЙ член лосса.

   Второе — это честная граница метода: retention-член может только помешать
    умереть, он не умеет воскрешать. Тест закрепляет границу числами, чтобы
    следующая интерпретация прогона не приписала члену силу, которой нет.
    """

    def setUp(self):
        self.device = torch.device("cpu")
        torch.manual_seed(config.SEED)
        self.model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(self.device)
        self.model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        self.model.eval()
        self.target = create_target(device=self.device).expand(2, -1, -1, -1)
        self.saved = (
            config.RETENTION_ALIVE_MARGIN,
            config.RETENTION_SURVIVAL_MODE,
            config.RETENTION_QUIET_MARGIN,
        )

    def tearDown(self):
        (
            config.RETENTION_ALIVE_MARGIN,
            config.RETENTION_SURVIVAL_MODE,
            config.RETENTION_QUIET_MARGIN,
        ) = self.saved

    def _state_with_alpha_logit(self, logit):
        state = torch.zeros(2, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE)
        state[:, config.ALIVE_CHANNEL] = float(logit)
        return state

    def _survival(self, logit, mode):
        _mse, surv, _quiet = retention_rollout_loss(
            self.model,
            self._state_with_alpha_logit(logit),
            self.target,
            steps=1,
            mode=mode,
        )
        return surv

    def _quiet(self, logit, margin=0.0, mode="level"):
        config.RETENTION_QUIET_MARGIN = margin
        _mse, _surv, quiet = retention_rollout_loss(
            self.model,
            self._state_with_alpha_logit(logit),
            self.target,
            steps=1,
            mode=mode,
        )
        return quiet

    def _grad_norm(self, loss):
        self.model.zero_grad(set_to_none=True)
        loss.backward(retain_graph=True)
        total = sum(
            float(p.grad.norm().item()) ** 2
            for p in self.model.parameters()
            if p.grad is not None
        ) ** 0.5
        self.model.zero_grad(set_to_none=True)
        return total

    def test_transition_is_exactly_zero_on_dead_field(self):
        """alpha = 0.5 (поглощающая смерть): transition-член = 0 — он слеп."""
        surv = self._survival(0.0, "transition")
        self.assertAlmostEqual(float(surv), 0.0, places=12)

    def test_level_sees_dead_field_value_but_without_gradient(self):
        """Тот же мёртвый уровень: level-член = margin, то есть смерть ВИДНА
        в лоссе, но воскресить её он не может (градиент — следующий тест).
        transition же не видит её даже как число."""
        config.RETENTION_ALIVE_MARGIN = 0.1
        surv = self._survival(0.0, "level")
        self.assertAlmostEqual(float(surv), 0.1, places=6)

    def test_level_has_gradient_only_while_cells_are_alive(self):
        """Градиент level-члена есть в полосе (threshold, threshold+margin) и нет
        на мёртвом поле — воскрешать член не умеет, только не давать умереть."""
        config.RETENTION_ALIVE_MARGIN = 0.1
        alive_border = self._survival(0.2, "level")  # alpha=0.55, живая, ниже пола 0.6
        dead = self._survival(0.0, "level")  # alpha=0.5, не живая
        self.assertTrue(alive_border.requires_grad, "level-член без графа — наблюдатель")
        self.assertGreater(self._grad_norm(alive_border), 0.0)
        self.assertEqual(self._grad_norm(dead), 0.0)

    def test_level_is_silent_well_above_the_floor(self):
        """alpha = 0.73 > threshold+margin: удержание уже выполняется, штраф 0."""
        config.RETENTION_ALIVE_MARGIN = 0.1
        surv = self._survival(1.0, "level")
        self.assertAlmostEqual(float(surv), 0.0, places=8)

    def test_compute_loss_honours_level_mode(self):
        """Режим доходит до суммы: total = spec-члены + retention(level), и
        survival-часть nonzero на поле, где transition дал бы ноль."""
        config.RETENTION_ENABLED = True
        config.RETENTION_SURVIVAL_MODE = "level"
        config.RETENTION_ALIVE_MARGIN = 0.1
        config.LOSS_WEIGHTS["retention"] = 1.0
        config.RETENTION_ROLLOUT_STEPS = 1
        self.model.train()
        try:
            _t, loss_dict, weighted = compute_loss(
                self._state_with_alpha_logit(0.2),
                self.target,
                self.model,
                iteration=3,
                return_terms=True,
            )
        finally:
            config.RETENTION_ENABLED = False
            config.LOSS_WEIGHTS["retention"] = 0.0
            config.RETENTION_SURVIVAL_MODE = "transition"
            config.RETENTION_ROLLOUT_STEPS = 8
            self.model.eval()
        self.assertGreater(loss_dict["retention_survival"], 0.0)
        self.assertIn("retention", weighted)
        self.assertAlmostEqual(
            loss_dict["total"], sum(float(v) for v in weighted.values()), places=6
        )

    def test_validate_rejects_level_without_margin(self):
        """level при margin=0 снова слеп (alpha=0.5 ровно на полу) — конфиг-ошибка."""
        saved = (
            config.RETENTION_ENABLED,
            config.RETENTION_SURVIVAL_MODE,
            config.RETENTION_ALIVE_MARGIN,
            float(config.LOSS_WEIGHTS["retention"]),
        )
        try:
            config.RETENTION_ENABLED = True
            config.LOSS_WEIGHTS["retention"] = 1.0
            config.RETENTION_SURVIVAL_MODE = "level"
            config.RETENTION_ALIVE_MARGIN = 0.0
            with self.assertRaises(AssertionError):
                config.validate()
        finally:
            (
                config.RETENTION_ENABLED,
                config.RETENTION_SURVIVAL_MODE,
                config.RETENTION_ALIVE_MARGIN,
                config.LOSS_WEIGHTS["retention"],
            ) = saved


class TestQuietMember(unittest.TestCase):
    """Вторая половина полосы удержания: налог на живость ВНЕ цели (NEG-20).

    Прогон R-8 (level-survival ×10, flat curriculum, alive_policy вес 2.0)
    дожил до 1000-й итерации при af 0.87…1.00 и f1 ≤ 0.211 с precision ~0.15:
    ткань живая, но это «живо всё». Причина не в весе: survival требует alpha
    ВЫШЕ пола только по клеткам цели и молчит про фон, а односторонний штраф
    проигрывает члену, который считается на том же автономном roll-out. quiet
    закрывает именно этот провал, и здесь закреплены его смысл и его границы.
    """

    def setUp(self):
        self.saved = {
            "enabled": config.RETENTION_ENABLED,
            "weight": float(config.LOSS_WEIGHTS["retention"]),
            "quiet_weight": config.RETENTION_QUIET_WEIGHT,
            "quiet_margin": config.RETENTION_QUIET_MARGIN,
            "survival_weight": config.RETENTION_SURVIVAL_WEIGHT,
            "mode": config.RETENTION_SURVIVAL_MODE,
            "alive_margin": config.RETENTION_ALIVE_MARGIN,
            "steps": config.RETENTION_ROLLOUT_STEPS,
            "checkpointing": config.GRAD_CHECKPOINTING,
        }
        config.GRAD_CHECKPOINTING = False
        config.RETENTION_ROLLOUT_STEPS = 1
        config.RETENTION_QUIET_MARGIN = 0.0

    def tearDown(self):
        config.RETENTION_ENABLED = self.saved["enabled"]
        config.LOSS_WEIGHTS["retention"] = self.saved["weight"]
        config.RETENTION_QUIET_WEIGHT = self.saved["quiet_weight"]
        config.RETENTION_QUIET_MARGIN = self.saved["quiet_margin"]
        config.RETENTION_SURVIVAL_WEIGHT = self.saved["survival_weight"]
        config.RETENTION_SURVIVAL_MODE = self.saved["mode"]
        config.RETENTION_ALIVE_MARGIN = self.saved["alive_margin"]
        config.GRAD_CHECKPOINTING = self.saved["checkpointing"]
        config.RETENTION_ROLLOUT_STEPS = self.saved["steps"]

    def _quiet(self, alive_logit, margin=None, target=None):
        """quiet на стабе с нулевым шагом: alpha = sigmoid(alive_logit) ровно.

        margin=None означает «не трогать конфиг», потому что часть тестов
        выставляет RETENTION_QUIET_MARGIN напрямую: параметр, который молча
        игнорируется, — это тест, проверяющий не то, что написано.
        """
        if margin is not None:
            config.RETENTION_QUIET_MARGIN = margin
        stub = _StubModel(kill=False)
        state = _small_state(alive=alive_logit)
        tgt = torch.zeros(1, 1, 4, 4) if target is None else target
        _mse, _surv, quiet = retention_rollout_loss(stub, state, tgt, steps=1)
        return quiet

    def test_quiet_is_exactly_zero_on_dead_background(self):
        """Фон мёртв (alpha = 0.5 при обнулённом состоянии) и margin = 0: quiet = 0.

        Это НЕ слепота survival-члена из NEG-18, а корректное поведение: мёртвый
        фон наказывать не за что. Если бы здесь было число, quiet платил бы за
        смерть, которую он не мог бы отменить.
        """
        quiet = self._quiet(0.0)
        self.assertAlmostEqual(float(quiet), 0.0, places=12)

    def test_quiet_penalizes_alive_background_by_exactly_the_excess(self):
        """alpha = 0.55 вне цели, потолок 0.5: quiet = 0.05 ровно, а не «что-то
        положительное». Числовая фиксация нужна, чтобы масштаб члена можно было
        калибровать по градиенту, а не по вкусу."""
        quiet = self._quiet(0.2007)  # sigmoid(0.2007) = 0.55
        alpha = 1.0 / (1.0 + float(torch.exp(torch.tensor(-0.2007))))
        self.assertAlmostEqual(float(quiet), alpha - 0.5, places=6)

    def test_quiet_ignores_target_cells(self):
        """Клетка ЦЕЛИ живая и яркая — quiet обязан молчать: за неё отвечает
        survival, а не налог на фон. Иначе два члена дрались бы за одно и то же
        место, и «удержание с парой» означало бы двойной штраф по рисунку."""
        target = torch.ones(1, 1, 4, 4)
        quiet = self._quiet(3.0, target=target)
        self.assertAlmostEqual(float(quiet), 0.0, places=12)

    def test_quiet_margin_raises_the_ceiling_above_absorbing_death(self):
        """margin > 0 требует от фона определённой мёртвости, и у поглощающе
        мёртвой клетки (alpha = 0.5) quiet == margin ПОСТОЯННО: опустить ниже
        некуда. Проверено числами, чтобы это не читалось как «фон жив».
        """
        alpha_at_3 = 1.0 / (1.0 + float(torch.exp(torch.tensor(-3.0))))
        self.assertAlmostEqual(float(self._quiet(0.0, margin=0.1)), 0.1, places=7)
        # Живая клетка вне цели при том же margin: потолок 0.4, член считает
        # превышение alpha − 0.4, а не стоит константой, как на мёртвом фоне.
        self.assertAlmostEqual(
            float(self._quiet(3.0, margin=0.1)), alpha_at_3 - 0.4, places=6
        )

    def _quiet_with_stub(self, alive_logit, margin=0.0, target=None):
        stub = _StubModel(kill=False)
        state = _small_state(alive=alive_logit)
        tgt = torch.zeros(1, 1, 4, 4) if target is None else target
        _mse, _surv, quiet = retention_rollout_loss(stub, state, tgt, steps=1)
        return quiet, stub

    def test_quiet_has_gradient_on_live_cells_outside_target(self):
        """quiet — член, а не наблюдатель: на живом фоне у него есть градиент по
        параметру стаба, и нет его на мёртвом фоне (там наказывать не за что).
        Именно это отличает его от survival-уровня: у того градиент нулевой ровно
        там, где клетка уже мертва — и это его граница, а не сила."""
        live, stub = self._quiet_with_stub(3.0)
        self.assertTrue(live.requires_grad, "quiet без графа — это метрика, не член")
        live.backward()
        self.assertIsNotNone(stub.delta.grad)
        self.assertGreater(float(stub.delta.grad[config.ALIVE_CHANNEL].abs()), 0.0)
        dead, stub_dead = self._quiet_with_stub(0.0)
        dead.backward()
        self.assertEqual(float(stub_dead.delta.grad[config.ALIVE_CHANNEL].abs()), 0.0)

    def test_zero_quiet_weight_leaves_retention_term_unchanged(self):
        """Р-прогоны 1…8 зафиксированы с quiet, которого не было. При весе 0.0
        член не входит в сумму ни на единицу: иначе уже записанные числа
        перестали бы описывать то, что реально обучалось (§7.7)."""
        config.RETENTION_ENABLED = True
        config.LOSS_WEIGHTS["retention"] = 1.0
        config.RETENTION_SURVIVAL_MODE = "level"
        config.RETENTION_ALIVE_MARGIN = 0.1
        config.RETENTION_SURVIVAL_WEIGHT = 10.0
        config.RETENTION_QUIET_WEIGHT = 0.0
        device = torch.device(config.DEVICE)
        torch.manual_seed(config.SEED)
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
        model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        model.train()
        target = create_target(device=device)
        state = torch.randn(
            2, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=device
        )
        state[:, config.ALIVE_CHANNEL] = 1.0
        _t, loss_dict, weighted = compute_loss(
            state, target, model, iteration=3, return_terms=True
        )
        self.assertIn("retention", weighted)
        self.assertIn("retention_quiet", loss_dict)
        self.assertGreaterEqual(loss_dict["retention_quiet"], 0.0)
        self.assertAlmostEqual(
            float(weighted["retention"]),
            loss_dict["retention_mse"]
            + 10.0 * loss_dict["retention_survival"]
            + 0.0 * loss_dict["retention_quiet"],
            places=6,
            msg="нулевой вес quiet всё-таки вошёл в сумму",
        )

    def test_quiet_weight_adds_its_own_term(self):
        """При весе > 0 quiet входит в retention ровно своим множителем — сумма
        членов остаётся атрибутируемой (wp4_collapse_probe спрашивает «кто
        толкает», и спрашивает по отдельным членам)."""
        config.RETENTION_ENABLED = True
        config.LOSS_WEIGHTS["retention"] = 1.0
        config.RETENTION_SURVIVAL_MODE = "level"
        config.RETENTION_ALIVE_MARGIN = 0.1
        config.RETENTION_SURVIVAL_WEIGHT = 10.0
        config.RETENTION_QUIET_WEIGHT = 5.0
        device = torch.device(config.DEVICE)
        torch.manual_seed(config.SEED)
        model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
        model.set_generator(torch.Generator(device="cpu").manual_seed(config.SEED))
        model.train()
        target = create_target(device=device)
        state = torch.randn(
            2, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=device
        )
        state[:, config.ALIVE_CHANNEL] = 1.0
        _t, loss_dict, weighted = compute_loss(
            state, target, model, iteration=3, return_terms=True
        )
        self.assertAlmostEqual(
            float(weighted["retention"]),
            loss_dict["retention_mse"]
            + 10.0 * loss_dict["retention_survival"]
            + 5.0 * loss_dict["retention_quiet"],
            places=6,
        )

    def test_validate_rejects_quiet_weight_without_rollout(self):
        """quiet считается только внутри roll-out: вес > 0 при
        RETENTION_ENABLED=False подписывал бы прогон как «удержание с парой»."""
        saved = (config.RETENTION_ENABLED, float(config.LOSS_WEIGHTS["retention"]))
        try:
            config.RETENTION_ENABLED = False
            config.RETENTION_QUIET_WEIGHT = 1.0
            with self.assertRaises(AssertionError):
                config.validate()
        finally:
            config.RETENTION_QUIET_WEIGHT = self.saved["quiet_weight"]
            config.RETENTION_ENABLED, config.LOSS_WEIGHTS["retention"] = saved

    def test_validate_rejects_quiet_margin_above_threshold(self):
        """margin >= ALIVE_THRESHOLD дал бы отрицательный потолок alpha — член
        стал бы невыполнимой константой (у мёртвой клетки alpha = 0.5 ниже некуда)."""
        try:
            config.RETENTION_QUIET_MARGIN = float(config.ALIVE_THRESHOLD)
            with self.assertRaises(AssertionError):
                config.validate()
            config.RETENTION_QUIET_MARGIN = 0.49
            config.validate()
        finally:
            config.RETENTION_QUIET_MARGIN = self.saved["quiet_margin"]


if __name__ == "__main__":
    unittest.main()
