"""
test_coverage_endpoint.py — эндпоинт покрытий для E02 (WP4).

Причина появления — измеренная слепота нормированного симметричного Chamfer к
перекрытию ткани (experiments/E02_pattern/collapse_probe.json + прямой замер
полей на цели ring):

    поле                 chamfer    f1
    всё белое            0.0362     0.2644
    случайное p=0.5      0.0385     0.2356
    идеальное кольцо     0.0000     1.0000
    всё чёрное           0.7664     0.0000

Chamfer различает «нет ткани» и «ткань не там», но почти не различает «ткани
слишком много» — поэтому гейт слоя 1 по убыванию Chamfer выполним раздутой
лужей. Эндпоинт покрытий наказывает лишнюю ткань через precision напрямую.

Значения в тесте — промеры, а не ожидания: если формула изменится, числа
обязаны измениться вместе с ней и это должно быть видно в diff.
"""

import unittest

import numpy as np

import config

GRID = config.GRID_SIZE
RING_DENSITY = 0.15234375


def _ring_mask():
    from target_patterns import create_target

    target = create_target(device="cpu")
    return (target[0, 0] > 0.5).numpy()


class TestCoverageEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target = _ring_mask()

    def _ep(self, pred):
        from evaluate import compute_coverage_endpoints

        return compute_coverage_endpoints(pred, self.target)

    def test_perfect_match_is_one(self):
        e = self._ep(self.target.copy())
        self.assertEqual((e["recall"], e["precision"], e["f1"]), (1.0, 1.0, 1.0))
        self.assertEqual((e["over_coverage"], e["missed"]), (0.0, 0.0))

    def test_empty_prediction_kills_recall_and_f1(self):
        e = self._ep(np.zeros((GRID, GRID), dtype=bool))
        self.assertEqual(e["recall"], 0.0)
        self.assertEqual(e["f1"], 0.0)
        self.assertTrue(e["pred_empty"])
        # missed = вся цель как доля поля — это и есть плотность цели.
        self.assertAlmostEqual(e["missed"], RING_DENSITY, places=4)

    def test_all_white_is_penalised_by_precision(self):
        """
        Ключевой тест: всё белое поле Chamfer почти не трогает (0.0362), а
        эндпоинт обязан показать, что ткани в 6.5 раза больше требуемого.
        """
        e = self._ep(np.ones((GRID, GRID), dtype=bool))
        self.assertEqual(e["recall"], 1.0)
        self.assertAlmostEqual(e["precision"], RING_DENSITY, places=4)
        self.assertAlmostEqual(e["f1"], 0.2644, delta=1e-3)
        self.assertAlmostEqual(e["over_coverage"], 1.0 - RING_DENSITY, places=4)
        self.assertLess(e["f1"], 0.5, "лужа на всё поле не может считаться собирающим успехом")

    def test_chamfer_is_blind_where_coverage_is_not(self):
        """
        Фиксация мотива: для «всё белое» Chamfer меньше 0.05 (почти идеал),
        f1 при этом 0.264. Разрыв метрик — задокументированное свойство
        Chamfer, а не ошибка реализации.
        """
        from evaluate import compute_symmetric_chamfer_error

        white = np.ones((GRID, GRID), dtype=bool)
        chamfer = float(
            compute_symmetric_chamfer_error(white.astype("uint8"), self.target.astype("uint8"))
        )
        f1 = self._ep(white)["f1"]
        self.assertLess(chamfer, 0.05)
        self.assertLess(f1, 0.3)
        self.assertGreater(1.0 - f1, chamfer * 5.0)

    def test_random_field_scores_worse_than_perfect_and_below_one(self):
        gen = np.random.default_rng(0)
        e = self._ep(gen.random((GRID, GRID)) < 0.5)
        self.assertGreater(e["f1"], 0.0)
        self.assertLess(e["f1"], 0.5)
        self.assertAlmostEqual(e["precision"], RING_DENSITY, delta=0.02)

    def test_bool_and_uint8_inputs_agree(self):
        from evaluate import compute_symmetric_chamfer_error

        e_bool = self._ep(self.target)
        e_uint = self._ep(self.target.astype("uint8"))
        e_float = self._ep((self.target.astype(float) * 0.7))
        self.assertEqual(e_bool, e_uint)
        self.assertEqual(e_bool["f1"], e_float["f1"])
        self.assertEqual(len(e_bool), 9)
        # sanity: chamfer жив и не сломан нашим соседом по модулю
        self.assertEqual(
            compute_symmetric_chamfer_error(self.target.astype("uint8"), self.target.astype("uint8")),
            0.0,
        )

    def test_mismatched_shapes_are_rejected(self):
        with self.assertRaises(ValueError):
            self._ep(np.ones((GRID // 2, GRID // 2), dtype=bool))

    def test_empty_target_does_not_divide_by_zero(self):
        from evaluate import compute_coverage_endpoints

        e = compute_coverage_endpoints(self.target, np.zeros((GRID, GRID), dtype=bool))
        self.assertEqual(e["recall"], 0.0)
        self.assertEqual(e["f1"], 0.0)
        self.assertTrue(e["target_empty"])


if __name__ == "__main__":
    unittest.main()
