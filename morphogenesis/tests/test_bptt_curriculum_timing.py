"""
test_bptt_curriculum_timing.py — горизонт diagnostics-прогона обязан включать
переход куррикулума BPTT, иначе «выжила» означает «не дожила до удара» (WP4).

Измеренная причина (§7.7, experiments/E02_pattern/wp4_ablations.json):
первая волна абляций (200 шагов) дала единственный «выживший» arm H-D2
(TRAIN_LR=1e-4) с alive_fraction 0.349 на итерации 200. Тот же arm на 400
шагах умирает: 0.349 (it 200) -> 0.149 -> 0.009 -> 0.0014, а grad_norm на той
же итерации 200 подскакивает с 1.4 до 21.4. Итерация 200 — это
TRAIN_BPTT_CURRICULUM_AT, где длина раскрутки становится 32 вместо 16. То есть
вывод «низкий LR лечит коллапс» был артефактом горизонта: прогон обрывался за
шаг до пускового события.

Тесты ниже не обучают ничего: они проверяют, что (1) расписание перехода
действительно стоит там, где его показывают логи, (2) метаданные прогона
хранят горизонт, (3) summarizer из wp4_ablations досталяет именно те поля, по которым артефакт
стал виден.
"""

import unittest

import config
from train import get_current_unroll
from wp4_ablations import _summarize

# Точка перехода из логов: до 200 unroll=16, начиная с 200 — 32.
TRANSITION_ITERATION = 200
# Измеренная плотность цели ring; от неё считается относительный порог коллапса.
RING_DENSITY = 0.15234375


class TestCurriculumTransition(unittest.TestCase):
    def test_unroll_jumps_at_the_measured_iteration(self):
        self.assertEqual(get_current_unroll(TRANSITION_ITERATION - 1), 16)
        self.assertEqual(get_current_unroll(TRANSITION_ITERATION), 32)

    def test_collapse_guard_arms_exactly_at_the_transition(self):
        # Совпадение не случайное, но опасное: предохранитель (§5.7) начинает
        # срабатывать только с COLLAPSE_GUARD_MIN_ITERATIONS, и этот же номер —
        # момент первого удара. Значит «предохранитель не сработал» на коротком
        # прогоне логически не может означать «ткань живуча».
        self.assertEqual(config.COLLAPSE_GUARD_MIN_ITERATIONS, TRANSITION_ITERATION)

    def test_schedule_is_shorter_than_the_training_contract(self):
        # Единственный способ не увидеть переход — обрезанный горизонт. При
        # полном TRAIN_MAX_STEPS переходов два, и оба внутри обучения.
        self.assertLess(TRANSITION_ITERATION, config.TRAIN_MAX_STEPS)
        self.assertEqual(
            len(config.TRAIN_BPTT_CURRICULUM), len(config.TRAIN_BPTT_CURRICULUM_AT)
        )
        self.assertEqual(config.TRAIN_BPTT_CURRICULUM[0], 16)
        self.assertGreater(config.TRAIN_BPTT_CURRICULUM[1], config.TRAIN_BPTT_CURRICULUM[0])


class TestSummarizeExposesTiming(unittest.TestCase):
    # Траектория, повторяющая измеренный профиль H-D2 на 400 шагах: плато,
    # удар на переходе куррикулума, затем поглощающий мёртвый бассейн.
    ROWS = [
        {
            "iteration": it,
            "total": 0.49,
            "visible_mse": 0.27,
            "alive_policy": 0.33,
            "hidden_reg": 0.0,
            "alive_fraction": af,
            "grad_norm": gn,
            "lr": 1e-4,
            "unroll": 16 if it < TRANSITION_ITERATION else 32,
            "phase": 1,
            "alive_mask_enabled": True,
            "chamfer": 0.04,
            "coverage": {"f1": f1},
            "b0": 1.0,
            "b1": 1.0,
            "density": 0.2,
        }
        for it, af, gn, f1 in [
            (50, 0.5023, 1.02, 0.30),
            (100, 0.4865, 1.14, 0.31),
            (150, 0.4698, 1.40, 0.32),
            (200, 0.3492, 21.41, 0.30),
            (250, 0.1486, 29.60, 0.20),
            (300, 0.0090, 26.90, 0.05),
            (350, 0.0014, 9.02, 0.0),
            (400, 0.0014, 2.08, 0.0),
        ]
    ]

    def test_horizon_200_and_400_disagree_about_survival(self):
        threshold = 0.0762  # относительный порог для ring (0.5 * 0.1523)
        first_200 = self.ROWS[:4]
        s200 = _summarize(first_200, "H-D2", 200, 42, threshold, "", {})
        s400 = _summarize(self.ROWS, "H-D2", 400, 42, threshold, "", {})
        self.assertTrue(s200["survived"], "на 200 шагах траектория выглядит выжившей")
        self.assertFalse(s400["survived"])
        self.assertIsNone(s200["collapse_iteration"])
        self.assertEqual(s400["collapse_iteration"], 300)

    def test_aborted_run_is_marked_truncated(self):
        # Тот же набор точек, но заявленный горизонт 400: прогон оборван, и
        # запись обязана это говорить вслух, а не выдавать 200 итераций за 400.
        s = _summarize(self.ROWS[:4], "H-M2", 400, 42, 0.0762, "", {})
        self.assertTrue(s["truncated"])
        self.assertEqual(s["logged_final_iteration"], 200)
        self.assertFalse(_summarize(self.ROWS, "H-M2", 400, 42, 0.0762, "", {})["truncated"])

    def test_collapse_is_attributed_to_the_unroll_transition(self):
        threshold = config.collapse_alive_fraction_min(RING_DENSITY)
        s400 = _summarize(self.ROWS, "H-D2", 400, 42, threshold, "", {})
        # Переход найден по самим логам: it=200, unroll 16 -> 32.
        self.assertEqual(s400["transition_iteration"], TRANSITION_ITERATION)
        self.assertEqual(s400["unroll_before_transition"], 16)
        self.assertEqual(s400["unroll_after_transition"], 32)
        # До перехода — плато: живая ткань и нормальный масштаб градиента.
        self.assertAlmostEqual(s400["alive_fraction_before_transition"], 0.4698)
        self.assertAlmostEqual(s400["grad_norm_median_before_transition"], 1.14)
        # На переходе — удар (21.41 против медианы 1.14), пик чуть позже (it 250).
        self.assertAlmostEqual(s400["grad_norm_at_transition"], 21.41)
        self.assertGreater(s400["grad_norm_at_transition"], 10 * s400["grad_norm_median_before_transition"])
        self.assertEqual(s400["grad_norm_at"], 250)
        self.assertEqual(s400["unroll_at_collapse"], 32)

    def test_constant_unroll_arm_reports_no_transition(self):
        # H-I* идут с curriculum [16,16,16]: у них перехода нет, и summarizer
        # обязан вернуть None, а не выдуманную границу.
        rows = [dict(r, unroll=16) for r in self.ROWS]
        s = _summarize(rows, "H-I1", 400, 42, 0.0762, "", {})
        self.assertIsNone(s["transition_iteration"])
        self.assertIsNone(s["grad_norm_at_transition"])
        self.assertIsNone(s["alive_fraction_before_transition"])

    def test_coverage_endpoints_are_carried_into_the_summary(self):
        s = _summarize(self.ROWS, "H-D2", 400, 42, 0.0762, "", {})
        self.assertEqual(s["f1_max"], 0.32)
        self.assertEqual(s["f1_final"], 0.0)

    def test_missing_coverage_degrades_to_none_instead_of_crashing(self):
        rows = [dict(r, coverage=None) for r in self.ROWS]
        s = _summarize(rows, "H-A0", 400, 42, 0.0762, "", {})
        self.assertIsNone(s["f1_max"])
        self.assertIsNone(s["f1_final"])


if __name__ == "__main__":
    unittest.main()
