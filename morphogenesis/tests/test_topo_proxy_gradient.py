"""
test_topo_proxy_gradient.py — дифференцируемость топологического прокси (§2.10).

Проверяет главное требование §2.10.1/§12.1.13: член топологии обязан быть
дифференцируемым и проходить тест градиента, а не «выглядеть похоже».

Дополнительно:

- соft_chi воспроизводит β₀ − β₁ дискретных целей из каталога §12.5
  (это проверка осмысленности прокси, а НЕ замена дискретной топологии §2.4);
- §2.10.4: деградация (ноль градиента / NaN) переводит бэкенд в disabled;
- §2.10.3: stride — прокси считается не каждый шаг;
- §12.6.8: потолок вклада монотонен и не создаёт мёртвой зоны.
"""

import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from target_patterns import create_target
from topo_proxy import TopologicalProxy, soft_chi, topo_term_cap


def _chi_units(mask):
    """χ в «единицах нарушения» (soft_chi нормирована на число клеток)."""
    area = float(mask.shape[-2] * mask.shape[-1])
    return soft_chi(mask) * area


class TestSoftChiMatchesDiscreteTopology(unittest.TestCase):
    """χ прокси на бинарных целях должен совпасть с β₀ − β₁ из topology.py."""

    def setUp(self):
        self.device = torch.device("cpu")

    def test_targets_match_registry(self):
        from topology import count_connected_components, count_holes, remove_small_clusters

        for name, topo in sorted(config.TARGET_PATTERN_TOPOLOGY.items()):
            target = create_target(name, device=self.device)
            hard = (target[0, 0] > 0.5).float().unsqueeze(0).unsqueeze(0)
            chi_proxy = float(_chi_units(hard).item())
            # Дискретная истина — по образцу §2.4 (scipy.label), без градиентов.
            binary = remove_small_clusters(hard[0, 0].numpy().astype(bool))
            b0 = count_connected_components(binary)
            b1 = count_holes(binary)
            self.assertEqual(
                (b0, b1),
                (topo["b0"], topo["b1"]),
                f"{name}: дискретная топология {b0}/{b1} не совпала с каталогом {topo}",
            )
            self.assertAlmostEqual(
                chi_proxy,
                float(b0 - b1),
                delta=0.25,
                msg=f"{name}: soft_chi={chi_proxy:.3f}, β₀−β₁={b0 - b1}",
            )


class TestGradientCheckpoint(unittest.TestCase):
    def setUp(self):
        self.device = torch.device(config.DEVICE)

    def test_grad_test_passes_for_every_catalogued_target(self):
        for name in sorted(config.TARGET_PATTERN_TOPOLOGY):
            target = create_target(name, device=self.device)
            proxy = TopologicalProxy(target)
            report = proxy.grad_test(device=self.device)
            self.assertTrue(
                report["passed"],
                f"{name}: градиентный чекпоинт не пройден — {report}",
            )
            self.assertFalse(proxy.degraded)
            self.assertGreater(report["grad_norm"], 0.0)

    def test_gradient_finite_and_nonzero_on_soft_field(self):
        target = create_target("ring", device=self.device)
        proxy = TopologicalProxy(target)
        field = torch.rand(1, 1, config.GRID_SIZE, config.GRID_SIZE, device=self.device)
        field.requires_grad_(True)
        loss = proxy.compute_loss(field)
        self.assertTrue(torch.is_tensor(loss))
        loss.backward()
        self.assertTrue(bool(torch.isfinite(field.grad).all()))
        self.assertGreater(float(field.grad.abs().sum()), 0.0)

    def test_disabled_backend_returns_zero_without_crash(self):
        target = create_target("ring", device=self.device)
        proxy = TopologicalProxy(target, backend="disabled")
        field = torch.rand(1, 1, 8, 8, device=self.device, requires_grad=True)
        self.assertEqual(proxy.compute_loss(field), 0.0)
        self.assertIsNone(proxy.observe(0.0, 0.0, 10))


class TestDegradation(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cpu")

    def _proxy(self):
        return TopologicalProxy(create_target("ring", device=self.device))

    def test_zero_gradient_for_grace_steps_degrades(self):
        proxy = self._proxy()
        event = None
        for step in range(1, config.TOPO_PROXY_GRACE_STEPS + 2):
            event = proxy.observe(loss_value=0.5, grad_norm=0.0, step=step)
            if event is not None:
                break
        self.assertIsNotNone(event, "прокси не деградировал при нулевом градиенте")
        self.assertEqual(proxy.backend, "disabled")
        self.assertTrue(proxy.degraded)

    def test_nan_three_times_degrades(self):
        proxy = self._proxy()
        events = [proxy.observe(float("nan"), 1.0, step) for step in range(1, 4)]
        self.assertIsNotNone(events[-1], "NaN-лосс не привёл к деградации")
        self.assertEqual(proxy.backend, "disabled")

    def test_healthy_gradient_resets_counter(self):
        proxy = self._proxy()
        for step in range(1, 20):
            self.assertIsNone(proxy.observe(0.5, 1.0 if step % 2 else 0.0, step))
        self.assertEqual(proxy.backend, "soft_topological_proxy")
        self.assertLess(proxy.steps_without_gradient, 2)


class TestStrideAndCap(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cpu")
        self.proxy = TopologicalProxy(create_target("ring", device=self.device))

    def test_stride_gating(self):
        stride = self.proxy.stride
        self.assertTrue(self.proxy.next_step_ok(stride))
        if stride > 1:
            self.assertFalse(self.proxy.next_step_ok(1))

    def test_cap_is_monotone_and_differentiable_everywhere(self):
        """Потолок вклада не должен создавать мёртвую зону (в отличие от clamp)."""
        cap = float(config.TOPO_PROXY_GRAD_CLIP)
        raw = torch.tensor([0.0, cap, 10 * cap, 1000 * cap], requires_grad=True)
        capped = topo_term_cap(raw, cap)
        self.assertTrue(bool((capped.diff() > 0).all()), "потолок не монотонен")
        self.assertTrue(bool((capped <= cap + 1e-6).all()), "потолок превышен")
        capped.sum().backward()
        self.assertGreater(float(raw.grad.abs().min()), 0.0, "есть точки с нулевым градиентом")


if __name__ == "__main__":
    unittest.main()
