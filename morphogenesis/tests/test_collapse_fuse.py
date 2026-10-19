"""
test_collapse_fuse.py — порог предохранителя коллапса обязан быть
относительным плотности цели (WP4).

Причина не умозрительная, а измеренная: у цели ring доля клеток с тканью
0.1523 (experiments/E02_pattern/collapse_probe.json, target_density), а
абсолютный COLLAPSE_ALIVE_FRACTION_MIN был 0.15 — то есть порог стоял впритык
к плотности здоровой ткани. Такой предохранитель отличает смерть ткани не от
здоровой ткани, а от собственного числа: здоровое кольцо проходит с запасом
0.0023, и любой шум бинаризации уже роняет его под порог. Плюс константа
перестала бы быть переносимой: для цели другой плотности (E03/E04) то же самое
число значит совершенно другое.

Заодно фиксируем, что train.py и gate_layer1.py берут один и тот же порог из
одной функции — иначе гейт слоя и обучение проверяют разными линейками.
"""

import unittest

import config

# Измеренная плотность цели ring (64x64, кольцо из target_patterns).
RING_TARGET_DENSITY = 0.15234375


class TestCollapseThreshold(unittest.TestCase):
    def test_absolute_behaviour_preserved_without_density(self):
        """Старый вызов без плотности цели возвращает спецификационный абсолютный порог."""
        self.assertEqual(
            config.collapse_alive_fraction_min(),
            float(config.COLLAPSE_ALIVE_FRACTION_MIN),
        )
        self.assertEqual(
            config.collapse_alive_fraction_min(None),
            float(config.COLLAPSE_ALIVE_FRACTION_MIN),
        )

    def test_ring_density_is_strictly_below_the_absolute_threshold(self):
        """
        Главное следствие измерения: для ring относительный порог (0.5 · 0.1523
        = 0.0762) обязан лежать ниже абсолютного 0.15, иначе здоровая ткань
        density 0.1523 не прошла бы прежний предохранитель вообще никогда.
        """
        threshold = config.collapse_alive_fraction_min(RING_TARGET_DENSITY)
        self.assertLess(threshold, config.COLLAPSE_ALIVE_FRACTION_MIN)
        self.assertAlmostEqual(threshold, 0.5 * RING_TARGET_DENSITY, places=6)
        self.assertLess(threshold, RING_TARGET_DENSITY, "порог обязан быть ниже плотности живой цели")

    def test_measured_ring_density_matches_the_target(self):
        """
        Число в тесте должно оставаться числом ИЗ ЦЕЛИ, а не выученной
        константой: перевычисляем плотность по mask-канала цели.
        """
        from target_patterns import create_target

        target = create_target(device="cpu")
        density = float((target > 0).float().mean().item())
        self.assertAlmostEqual(density, RING_TARGET_DENSITY, delta=1e-4)

    def test_threshold_is_monotonic_in_density(self):
        prev = -1.0
        for density in (0.02, 0.05, 0.1523, 0.3, 0.5, 1.0):
            value = config.collapse_alive_fraction_min(density)
            self.assertGreaterEqual(value, prev)
            prev = value

    def test_floor_protects_sparse_targets(self):
        """На очень разреженной цели порог не имеет права схлопнуться в ноль."""
        self.assertEqual(
            config.collapse_alive_fraction_min(0.001),
            float(config.COLLAPSE_ALIVE_FRACTION_FLOOR),
        )

    def test_nonsense_density_is_rejected(self):
        for bad in (0.0, -0.1, 1.5):
            with self.assertRaises(ValueError, msg=f"density={bad}"):
                config.collapse_alive_fraction_min(bad)

    def test_validate_bounds_the_ratio_and_floor(self):
        original = (config.COLLAPSE_ALIVE_FRACTION_RATIO, config.COLLAPSE_ALIVE_FRACTION_FLOOR)
        try:
            config.COLLAPSE_ALIVE_FRACTION_RATIO = 0.0
            with self.assertRaises(AssertionError):
                config.validate()
            config.COLLAPSE_ALIVE_FRACTION_RATIO = original[0]
            config.COLLAPSE_ALIVE_FRACTION_FLOOR = 1.0
            with self.assertRaises(AssertionError):
                config.validate()
        finally:
            config.COLLAPSE_ALIVE_FRACTION_RATIO, config.COLLAPSE_ALIVE_FRACTION_FLOOR = original
        config.validate()


if __name__ == "__main__":
    unittest.main()
