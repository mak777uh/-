"""
test_wp4_reach_probe.py — зонд «достичь» против «удержать» (WP4b, §14.2).

Зачем отдельный тест. Зонд — единственный инструмент в полосе, который различает
два утверждения, до сих пор записанных одним числом f1: «кольцо не достигается из
шума» и «кольцо достигается, но в нём не удерживаются». Различает их не модель, а
точка принятия решения: reach стартует из шума, поэтому кольцу достаточно побывать
на траектории (МАКСИМУМ), а hold стартует ИЗ КОЛЬЦА (target_conditioned_state),
поэтому argmax по такой траектории равен 1.0 по построению и мерит начальное
состояние, а не динамику.

Этот дефект был пойман первым же прогоном зонда и записан как NEG-21/NEG-23:
первая версия решала по максимуму и выдавала «удерживается у всех» — включая H-A0
и H-N1, у которых последняя точка развёртки 0.0000. Тест ниже фиксирует, что для
hold решение берётся ПОСЛЕДНЯЯ точка, а не максимум, иначе правка откатится молча.
"""

import os

import sys

import unittest

# §9.2: config раньше torch.
import config

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wp4_reach_probe as probe  # noqa: E402


def _row(step, f1):
    return {"step": step, "f1_gated_best": f1, "f1_default": f1}


class TestDecisionPoint(unittest.TestCase):
    def test_reach_decides_on_max(self):
        """reach: старт — шум, поэтому «бывало кольцо на траектории» достаточно."""
        rows = [_row(10, 0.10), _row(20, 0.55), _row(30, 0.20)]
        self.assertEqual(probe.DECISION_POINT["reach"], "best")
        self.assertEqual(probe._decision_point("reach", rows)
                         ["f1_gated_best"], 0.55)

    def test_hold_decides_on_last_not_max(self):
        """hold: старт и есть цель, поэтому максимум тривиален и непригоден."""
        rows = [_row(10, 1.00), _row(20, 0.30), _row(30, 0.00)]
        self.assertEqual(probe.DECISION_POINT["hold"], "last")
        self.assertEqual(probe._decision_point("hold", rows)["f1_gated_best"], 0.00)
        # и ровно поэтому первая версия зонда давала ложный вердикт:
        self.assertGreater(
            probe._decision_point("reach", rows)["f1_gated_best"],
            probe._decision_point("hold", rows)["f1_gated_best"],
        )

    def test_empty_rollout_has_no_decision(self):
        self.assertIsNone(probe._decision_point("hold", []))
        self.assertIsNone(probe._decision_point("reach", []))

    def test_every_probe_names_a_decision_point(self):
        """Новый прогон без явной точки решения молча унаследовал бы «best».

        Ключи DECISION_POINT должны покрывать оба прогона зонда — иначе в
        артефакте появится запись без объяснённого правила.
        """
        for name in ("reach", "hold"):
            self.assertIn(name, probe.DECISION_POINT)
            self.assertIn(probe.DECISION_POINT[name], ("best", "last"))


class TestAliveMaskRestoration(unittest.TestCase):
    """Маска живости — часть динамики, а не весов: её надо восстанавливать по
    overrides прогона, иначе зонд меряет другую модель (§5.8)."""

    def test_mask_on_only_after_warmup(self):
        self.assertFalse(probe._alive_mask_enabled({"ALIVE_WARMUP_ITERS": 500}, 400, True))
        self.assertTrue(probe._alive_mask_enabled({"ALIVE_WARMUP_ITERS": 50}, 400, False))

    def test_missing_record_falls_back_to_config(self):
        self.assertTrue(probe._alive_mask_enabled({}, 400, True))
        self.assertFalse(probe._alive_mask_enabled({}, 400, False))

    def test_fallback_matches_config_default_at_gate_horizon(self):
        """Дефолт обязан совпадать с правилом train.py на гейтном горизонте."""
        warmup = int(config.ALIVE_WARMUP_ITERS)
        steps = int(config.RETENTION_GATE_STEPS)
        self.assertEqual(
            probe._alive_mask_enabled({}, steps, warmup <= steps),
            warmup <= steps,
        )


class TestCeilingGap(unittest.TestCase):
    def test_gap_is_the_layer1_rule(self):
        """Зазор над потолком бесструктурного поля — тот же, что у гейта слоя 1,
        иначе «всё яркое» (f1 = 2p/(1+p)) засчиталось бы структурой."""
        self.assertGreaterEqual(probe.CEILING_GAP, 0.05)


class TestReportDigest(unittest.TestCase):
    """Сводка в отчёте обязана брать готовое решение зонда, а не пересчитывать
    максимум по траектории: иначе ловушка NEG-21 возвращается уже в отчёте."""

    def _payload(self, rollout, decision_f1, last_f1, best_f1, probe_name):
        return {
            "rollout_steps": rollout,
            "device": "cpu",
            "verdict": {
                "threshold": 0.3144,
                "ceiling": 0.2644,
                "reachable_arms": [],
                "holdable_arms": [],
            },
            "runs": [
                {
                    "arm": "R-9",
                    "steps_trained": 2000,
                    "seed": 42,
                    "probe": probe_name,
                    "decision_point": "last" if probe_name == "hold" else "best",
                    "first": {"f1_default": 1.0},
                    "best": {"f1_gated_best": best_f1, "step": 10},
                    "last": {"f1_gated_best": last_f1},
                    "decision": {
                        "f1_gated_best": decision_f1,
                        "gated_precision": 0.5,
                        "gated_pred_fraction": 0.4,
                        "n_gated_thresholds": 60,
                    },
                    "alive_fraction_min": 0.5,
                    "beyond_ceiling": decision_f1 > 0.3144,
                }
            ],
        }

    def test_empty_input_returns_none(self):
        import wp4_report

        self.assertIsNone(wp4_report._reach_digest(None))
        self.assertIsNone(wp4_report._reach_digest([]))

    def test_digest_keeps_probe_decision_not_max(self):
        import wp4_report

        digest = wp4_report._reach_digest(
            [self._payload(1000, 0.0, 0.0, 1.0, "hold")]
        )
        run = digest["horizons"][0]["runs"][0]
        # start = цель, поэтому best = 1.0; решение обязано быть 0.0 (last).
        self.assertEqual(run["best_f1"], 1.0)
        self.assertEqual(run["decision_f1"], 0.0)
        self.assertFalse(run["beyond_ceiling"])
        self.assertIn("оптимистично", digest["note"])

    def test_horizons_are_sorted(self):
        import wp4_report

        digest = wp4_report._reach_digest(
            [
                self._payload(2000, 0.3, 0.3, 0.3, "reach"),
                self._payload(200, 0.1, 0.1, 0.1, "reach"),
            ]
        )
        self.assertEqual([h["rollout_steps"] for h in digest["horizons"]], [200, 2000])


if __name__ == "__main__":
    unittest.main()
