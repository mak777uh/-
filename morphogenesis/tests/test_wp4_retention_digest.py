"""
test_wp4_retention_digest.py — дайджест wave 7 в отчёте WP4 (§14.2 «удержание»).

Зачем отдельный тест. Дайджест — единственный уровень отчёта, где различие
«ткань умерла» и «ткань живая, но бесформенная» перестаёт быть буквой True/False
в колонке survived. Замерено в WP4b: R-7 (level-член, множитель 10) дожил до
конца горизонта (alive_min 0.810 при пороге 0.0762) с f1_max 0.1886, то есть
ниже потолка поля без структуры 0.2644, а R-4/R-5 умерли с НАСЫЩЕННЫМ штрафом
(survival_final = margin) — большим по значению и нулевым по градиенту. Если
инструмент не различает эти три случая, wave 7 можно прочитать как «удержание
получилось» там, где получилось только выживание.

Отдельно закреплено: overrides содержит только изменённые arm'ом ключи, поэтому
пропущенные поля дайджест обязан брать из дефолтов config, а не показывать None
(R-1 прогонялся с survival_mode=transition по умолчанию, и «None» читалось бы
как «члена не было»).
"""

import os

import sys

import unittest

# §9.2: config раньше torch.
import config

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _record(arm, overrides, *, mode=None, margin=None, survival_final=0.0, **kw):
    base = {
        "arm": arm,
        "seed": 42,
        "steps": 400,
        "description": f"синтетический {arm}",
        "overrides": overrides,
        "retention_enabled_by_overrides": True,
        "retention_survival_mode": mode,
        "retention_alive_margin": margin,
        "retention_survival_final": survival_final,
        "retention_quiet_final": None,
        "retention_mse_final": 0.25,
        "retention_mse_first": 0.26,
        "survived": False,
        "alive_fraction_min": 0.0,
        "collapse_iteration": 150,
        "visible_mse_final": 0.2498,
        "f1_max": 0.18,
        # Замерено в wave 9 (NEG-21): у всех плеч с удержанием на 400 итерациях
        # argmax f1 — первая же точка после сброса маски.
        "f1_max_iteration": 50,
        "truncated": False,
    }
    base.update(kw)
    return base


class TestRetentionDigest(unittest.TestCase):
    def setUp(self):
        from wp4_report import _retention_digest

        self.digest = _retention_digest

    def test_non_retention_arms_are_excluded(self):
        """H-плечи без retention-члена не должны попадать в wave 7: иначе
        «выживание базлайна» попадёт в ряд удержания."""
        runs = [_record("H-A0", {}, retention_enabled_by_overrides=False)]
        self.assertEqual(self.digest(runs), [])

    def test_defaults_are_filled_from_config_not_left_none(self):
        """R-1 менял только вес: mode/множитель/K он не задавал, и дайджест
        обязан показать дефолты, а не None."""
        runs = [
            _record(
                "R-1",
                {"RETENTION_ENABLED": True, "LOSS_WEIGHTS": {"retention": 0.5}},
                survival_final=6.6e-06,
            )
        ]
        e = self.digest(runs)[0]
        self.assertEqual(e["survival_mode"], str(config.RETENTION_SURVIVAL_MODE))
        self.assertAlmostEqual(e["survival_weight"], float(config.RETENTION_SURVIVAL_WEIGHT))
        self.assertEqual(e["rollout_steps"], 8)
        self.assertFalse(e["flat_curriculum"])
        # transition-член на мёртвом поле = 0, и «насыщения» у него быть не
        # может по построению — поле должно это различать.
        self.assertFalse(e["survival_saturated"])

    def test_saturated_level_penalty_is_flagged(self):
        """R-4: survival_final = margin при мёртвой цели. Это не «удержание
        работает», а «штраф упёрся в потолок, градиента нет» (NEG-18/NEG-19)."""
        runs = [
            _record(
                "R-4",
                {
                    "RETENTION_ENABLED": True,
                    "RETENTION_SURVIVAL_MODE": "level",
                    "RETENTION_ALIVE_MARGIN": 0.1,
                    "LOSS_WEIGHTS": {"retention": 1.0},
                },
                mode="level",
                margin=0.1,
                survival_final=0.09996691346168518,
            )
        ]
        e = self.digest(runs)[0]
        self.assertEqual(e["survival_mode"], "level")
        self.assertAlmostEqual(e["alive_margin"], 0.1)
        self.assertTrue(e["survival_saturated"])
        self.assertFalse(e["survived"])

    def test_survival_without_form_is_visible(self):
        """R-7: выжил И не насыщается, но f1 ниже потолка — дайджест обязан
        показать все три числа одновременно, чтобы вывод «удержание удалось»
        нельзя было сделать по одному выживанию."""
        runs = [
            _record(
                "R-7",
                {
                    "RETENTION_ENABLED": True,
                    "RETENTION_ROLLOUT_STEPS": 16,
                    "RETENTION_SURVIVAL_MODE": "level",
                    "RETENTION_ALIVE_MARGIN": 0.1,
                    "RETENTION_SURVIVAL_WEIGHT": 10.0,
                    "LOSS_WEIGHTS": {"retention": 1.0},
                    "TRAIN_BPTT_CURRICULUM": [16, 16, 16],
                },
                mode="level",
                margin=0.1,
                survival_final=1.1975858797086403e-05,
                survived=True,
                alive_fraction_min=0.81011962890625,
                collapse_iteration=None,
                f1_max=0.18857043266126436,
            )
        ]
        e = self.digest(runs)[0]
        self.assertTrue(e["survived"])
        self.assertFalse(e["survival_saturated"])
        self.assertTrue(e["flat_curriculum"])
        self.assertAlmostEqual(e["survival_weight"], 10.0)
        self.assertGreater(e["alive_fraction_min"], 0.0762)
        self.assertLess(e["f1_max"], 0.2644)

    def test_background_pair_weight_is_reported(self):
        """R-8 отличается от R-7 только весом alive_policy — в дайджесте это
        должно быть видно, иначе пару R-7/R-8 нечем различить при чтении
        results.json."""
        runs = [
            _record(
                "R-8",
                {
                    "RETENTION_ENABLED": True,
                    "RETENTION_SURVIVAL_MODE": "level",
                    "LOSS_WEIGHTS": {"retention": 1.0, "alive_policy": 2.0},
                },
                mode="level",
                margin=0.1,
            )
        ]
        self.assertAlmostEqual(self.digest(runs)[0]["alive_policy_weight"], 2.0)

    def test_quiet_half_defaults_to_off(self):
        """Прогоны R-1…R-8 прогонялись без quiet: в дайджесте у них обязан быть
        нулевой вес (из config), а не None — «None» читалось бы как «данные
        потеряны», хотя члена просто не было."""
        e = self.digest(
            [_record("R-7", {"RETENTION_ENABLED": True}, mode="level", margin=0.1)]
        )[0]
        self.assertAlmostEqual(e["quiet_weight"], float(config.RETENTION_QUIET_WEIGHT))
        self.assertAlmostEqual(e["quiet_weight"], 0.0)
        self.assertAlmostEqual(e["quiet_margin"], float(config.RETENTION_QUIET_MARGIN))
        self.assertIsNone(
            e["background_at_quiet_floor"],
            "при выключенном quiet вердикт о фоне должен быть None, а не False: "
            "False читалось бы как «фон живой», хотя член его не мерил",
        )

    def test_live_background_is_visible_in_quiet_fields(self):
        """Пара R-7/R-9 различается ровно включением quiet. Если у R-9 фон живой
        (quiet_final 0.43 >> margin 0.0), дайджест обязан показать
        background_at_quiet_floor=False: это и есть «удержание с парой ещё не
        починило форму», и оно не должно теряться в колонке survived."""
        e = self.digest(
            [
                _record(
                    "R-9",
                    {
                        "RETENTION_ENABLED": True,
                        "RETENTION_SURVIVAL_MODE": "level",
                        "RETENTION_QUIET_WEIGHT": 10.0,
                        "LOSS_WEIGHTS": {"retention": 1.0},
                    },
                    mode="level",
                    margin=0.1,
                    survived=True,
                    alive_fraction_min=0.8,
                    retention_quiet_final=0.43,
                    f1_max=0.19,
                )
            ]
        )[0]
        self.assertAlmostEqual(e["quiet_weight"], 10.0)
        self.assertAlmostEqual(e["quiet_final"], 0.43)
        self.assertFalse(e["background_at_quiet_floor"])

    def test_dead_background_sits_on_the_quiet_floor(self):
        """quiet_final = 0 при margin = 0 означает «живости вне цели не
        зафиксировано». Поле не должно врать в обе стороны: ноль — это пол, а не
        доказанная мёртвость клеток, поэтому оно называется именно floor."""
        e = self.digest(
            [
                _record(
                    "R-9",
                    {
                        "RETENTION_ENABLED": True,
                        "RETENTION_SURVIVAL_MODE": "level",
                        "RETENTION_QUIET_WEIGHT": 10.0,
                        "LOSS_WEIGHTS": {"retention": 1.0},
                    },
                    mode="level",
                    margin=0.1,
                    retention_quiet_final=0.0,
                )
            ]
        )[0]
        self.assertTrue(e["background_at_quiet_floor"])

    def test_f1_max_iteration_is_carried_and_defaults_to_none(self):
        """NEG-21: на горизонте 400 argmax f1 у всех retention-плеч = итерация 50,
        то есть f1_max измеряет начальное состояние модели, а не результат
        обучения. Дайджест обязан нести, ГДЕ достигнут максимум, иначе «f1_max
        0.1886» читается как измеренный эндпоинт. Для записей волн 7/8, где поля
        ещё не считали, — None, а не 0: «0» выглядело бы как «максимум до
        начала обучения», чего никто не измерял."""
        runs = [
            _record(
                "R-9", {"RETENTION_ENABLED": True, "LOSS_WEIGHTS": {"retention": 1.0}},
                f1_max_iteration=50,
            ),
            _record(
                "R-8", {"RETENTION_ENABLED": True, "LOSS_WEIGHTS": {"retention": 1.0}},
                f1_max_iteration=1200,
                steps=2000,
            ),
        ]
        e = {x["arm"]: x for x in self.digest(runs)}
        self.assertEqual(e["R-9"]["f1_max_iteration"], 50)
        self.assertEqual(e["R-8"]["f1_max_iteration"], 1200)
        legacy = _record(
            "R-7", {"RETENTION_ENABLED": True, "LOSS_WEIGHTS": {"retention": 1.0}}
        )
        legacy.pop("f1_max_iteration")
        self.assertIsNone(self.digest([legacy])[0]["f1_max_iteration"])


if __name__ == "__main__":
    unittest.main()
