"""
test_loss_plateaus.py — аналитические «бесструктурные» плато visible_mse (WP4).

Зачем. Волны 1-4 аблаций E02 (experiments/E02_pattern/wp4_ablations.json)
останавливаются ровно на двух числах, и оба выводятся аналитически, без
обучения:

    конфигурация прогона                 visible_mse     что это значит
    маска живости включена, ткань мертва 0.24985-0.24995 поле обнулено -> sigmoid(0)=0.5
    маска выключена (H-K1/H-K2/H-N1)      0.1393-0.1405   поле почти чёрное

Первое — тождество: MSE между константой 0.5 и БИНАРНОЙ целью равно 0.25 при
любой плотности цели, потому что (0.5-1)^2 = (0.5-0)^2 = 0.25. Второе — минимум
MSE по константному полю: для v и плотности p
    MSE(v) = p(1-v)^2 + (1-p)v^2,
достигаемый при v = p со значением p(1-p) = 0.12914 (p = 0.15234 у цели ring);
«всё чёрное» (v=0) даёт ровно p = 0.15234.

Смысл для диагностики: пока visible_mse стоит на одном из этих уровней, сеть
не выучила НИКАКОЙ пространственной структуры — она выучила константу. Это
позволяет отличить «ткань умерла» (0.25) от «ткань жива, но цель не выучена»
(0.13-0.15) по одному числу, и именно это различие сломало вывод волны 1.

Числа в тесте — промеры и тождества: если формула visible_mse или правило
бинаризации изменятся, тест обязан упасть, потому что изменится и вся
интерпретация логов WP4.
"""

import unittest

import numpy as np

import torch

import config

P_RING = 0.15234375  # плотность цели ring, измерено (NEG-08/NEG-09)


def _ring_target():
    from target_patterns import create_target

    return create_target(device="cpu")


class TestDeadFieldIdentity(unittest.TestCase):
    def test_dead_field_mse_is_exactly_quarter(self):
        """Мёртвая клетка обнуляется целиком (§5.2 + AliveSTE), её видимый
        канал становится 0, а sigmoid(0) = 0.5. MSE против бинарной цели при
        этом НЕ зависит от формы цели и равен 0.25."""
        target = _ring_target()
        image = torch.full((1, 1, config.GRID_SIZE, config.GRID_SIZE), 0.5)
        expanded = target.expand(image.shape)
        mse = float(torch.mean((image - expanded) ** 2))
        self.assertAlmostEqual(mse, 0.25, places=6)

    def test_quarter_holds_for_any_density(self):
        """Тождество не про ring: любое бинарное поле даёт 0.25 от константы 0.5."""
        for p in (0.0, 0.13, 0.5, 1.0):
            binary = (torch.rand(1, 1, 64, 64) < p).float()
            mse = float(torch.mean((0.5 - binary) ** 2))
            self.assertAlmostEqual(mse, 0.25, places=6, msg=f"p={p}")

    def test_zero_channel_maps_to_half(self):
        """Якорь цепочки «обнулённая клетка -> 0.5»: visible_image = sigmoid(ch0)
        без маски (nca_core.visible_image), поэтому нулевой канал и есть 0.5."""
        self.assertAlmostEqual(float(torch.sigmoid(torch.zeros(1))), 0.5, places=7)


class TestConstantFieldPlateau(unittest.TestCase):
    def test_formula_matches_direct_mse(self):
        """MSE константного поля против цели = p(1-v)^2 + (1-p)v^2."""
        target = _ring_target()
        density = float((target > 0).float().mean())
        self.assertAlmostEqual(density, P_RING, places=6)
        for c in (-4.0, -2.0, 0.0, 1.0, 3.0):
            v = float(torch.sigmoid(torch.tensor(c)))
            image = torch.full((1, 1, config.GRID_SIZE, config.GRID_SIZE), v)
            mse = float(torch.mean((image - target.expand(image.shape)) ** 2))
            self.assertAlmostEqual(mse, density * (1 - v) ** 2 + (1 - density) * v**2, places=6)

    def test_constant_optimum_is_density(self):
        """Лучшее константное предсказание — v = p, значение p(1-p)."""
        vs = np.linspace(0.0, 1.0, 100001)
        mse = P_RING * (1 - vs) ** 2 + (1 - P_RING) * vs**2
        best = int(np.argmin(mse))
        self.assertAlmostEqual(vs[best], P_RING, places=4)
        self.assertAlmostEqual(float(mse[best]), P_RING * (1 - P_RING), places=5)
        # Значение пола, с которым сравниваем измеренные плато H-K*/H-N1.
        self.assertAlmostEqual(P_RING * (1 - P_RING), 0.129135, places=5)

    def test_measured_plateau_is_near_black_constant(self):
        """Измеренные 0.1393-0.1405 лежат МЕЖДУ «всё чёрное» (p=0.15234) и
        оптимальной константой (0.12914): это почти чёрное поле, а не выученное
        кольцо. Проверяем, что соответствующая константа v < 0.1."""
        vs = np.linspace(0.0, P_RING, 20001)
        mse = P_RING * (1 - vs) ** 2 + (1 - P_RING) * vs**2
        for measured in (0.1393, 0.1397, 0.1405):
            v = float(vs[int(np.argmin(np.abs(mse - measured)))])
            self.assertLess(v, 0.1, msg=f"mse={measured} -> v={v}")

    def test_f1_ceiling_of_structureless_predictor(self):
        """Всё-белое поле (максимальный recall без структуры) имеет
        f1 = 2p/(1+p) = 0.2644 — потолок бесструктурного предсказателя.
        Измеренный f1_max по всем arm'ам ~0.19 ниже него, т.е. даже «лужа»
        не собрана."""
        from evaluate import compute_coverage_endpoints

        white = np.ones((config.GRID_SIZE, config.GRID_SIZE), dtype="uint8")
        target = _ring_target()
        target_np = (target[0, 0] > 0.5).numpy().astype("uint8")
        cov = compute_coverage_endpoints(white, target_np)
        self.assertAlmostEqual(cov["f1"], 2 * P_RING / (1 + P_RING), places=4)
        self.assertAlmostEqual(cov["recall"], 1.0, places=6)

    def test_dead_field_f1_is_zero(self):
        """Мёртвое (всё чёрное) поле даёт f1 = 0 при Chamfer 0.7664: Chamfer
        видит отсутствие ткани, но не видит перепокрытие — отсюда и первичный
        эндпоинт coverage, а не Chamfer."""
        from evaluate import compute_coverage_endpoints, compute_symmetric_chamfer_error

        black = np.zeros((config.GRID_SIZE, config.GRID_SIZE), dtype="uint8")
        target = _ring_target()
        target_np = (target[0, 0] > 0.5).numpy().astype("uint8")
        self.assertEqual(compute_coverage_endpoints(black, target_np)["f1"], 0.0)
        self.assertAlmostEqual(float(compute_symmetric_chamfer_error(black, target_np)), 0.7664, places=3)

    def test_dead_cells_look_bright_without_gating(self):
        """Артефакт, из-за которого скан порогов gated (§5.8): мёртвая клетка
        обнулена ЦЕЛИКОМ, её видимый канал = 0, а sigmoid(0) = 0.5. Без условия
        живости все мёртвые клетки при пороге < 0.5 считаются яркими, и скан
        возвращает потолок «всё яркое» даже там, где ткани нет (измерено на
        H-K1: ungated 0.2649 против gated 0.0064)."""
        from evaluate import best_threshold_coverage

        target = _ring_target()
        target_np = (target[0, 0] > 0.5).numpy().astype("uint8")
        # ~99% поля мертво (видимый канал = 0 -> sigmoid = 0.5), живая ткань
        # осталась маленьким тёмным квадратом в ДЫРКЕ кольца (там цель = 0):
        # именно так выглядит поле H-K1.
        c = config.GRID_SIZE // 2
        soft = np.full((config.GRID_SIZE, config.GRID_SIZE), 0.5)
        alive = np.zeros((config.GRID_SIZE, config.GRID_SIZE), dtype=bool)
        soft[c - 4 : c + 4, c - 4 : c + 4] = 0.2
        alive[c - 4 : c + 4, c - 4 : c + 4] = True
        self.assertEqual(int(target_np[alive].sum()), 0, "живой квадрат не должен пересекать цель")

        ungated = best_threshold_coverage(soft, target_np)
        gated = best_threshold_coverage(np.where(alive, soft, 0.0), target_np)
        self.assertLess(abs(ungated["best"]["f1"] - 2 * P_RING / (1 + P_RING)), 0.02)
        self.assertEqual(gated["best"]["f1"], 0.0)
        self.assertGreater(ungated["best"]["f1"] - gated["best"]["f1"], 0.15)

    def test_scan_finds_perfect_field_at_default_threshold(self):
        """Положительный контроль инструмента (ср. H-P1): на заведомо выученном
        поле лучший f1 = 1.0 и достигается он при штатном пороге 0.5, а не на
        выбранном постфактум."""
        from evaluate import best_threshold_coverage

        target = _ring_target()
        target_np = (target[0, 0] > 0.5).numpy().astype("uint8")
        perfect = np.where(target_np > 0, 0.9, 0.1)
        alive = np.ones_like(target_np, dtype=bool)
        scan = best_threshold_coverage(np.where(alive, perfect, 0.0), target_np)
        self.assertAlmostEqual(scan["best"]["f1"], 1.0, places=6)
        self.assertAlmostEqual(scan["f1_at_default_threshold"], 1.0, places=6)
        self.assertAlmostEqual(scan["gain_over_default"], 0.0, places=9)


if __name__ == "__main__":
    unittest.main()
