"""

test_action_validator.py — Тесты единого валидатора действий.

[v5.5-EXP FINAL Rev.7] ПРАВИЛО 34

Проверяет:

- бюджет не уходит в минус;

- кулдаун морфогена соблюдается;

- кулдаун травмы соблюдается;

- инъекция в канал 15 отклоняется;

- инъекция в каналы 0 и 1 отклоняется;

- MORPHOGEN_MAX_INJECTIONS_PER_REPORT соблюдается;

- полная стоимость морфогена не превышает бюджет.

"""

import sys

import os

import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from cognition.action_validator import (

    validate_action,

    compute_action_cost,

    estimate_normalized_dose,

)

class TestActionValidator(unittest.TestCase):

    def setUp(self):

        self.budget = float(config.INTERVENTION_BUDGET_PER_REPORT)

    def test_budget_never_negative(self):

        """Бюджет не должен уходить в минус."""

        parsed = {

            "valid": True,

            "action": "MODIFY_DT",

            "params": {"new_value": 0.1},

        }

        result = validate_action(

            parsed,

            budget_remaining=0.05,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        if result["allowed"]:

            self.assertGreaterEqual(result["budget_remaining"], 0.0)

        else:

            self.assertIn("бюджет", result["reason"].lower())

    def test_morphogen_cooldown(self):

        """Кулдаун морфогена соблюдается."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 5,

                "value": 0.1,

                "radius": 4,

            },

        }

        # Кулдаун = 1, последняя инъекция была на предыдущем отчёте.

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=9,

            last_injury_report=-10,

        )

        self.assertFalse(result["allowed"])

        self.assertIn("кулдаун", result["reason"].lower())

    def test_morphogen_cooldown_expired(self):

        """Кулдаун истёк — инъекция разрешена."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 5,

                "value": 0.1,

                "radius": 4,

            },

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=8,

            last_injury_report=-10,

        )

        self.assertTrue(result["allowed"])

    def test_injury_cooldown(self):

        """Кулдаун травмы соблюдается."""

        parsed = {

            "valid": True,

            "action": "APPLY_INJURY",

            "params": {"size": 16},

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=6,

        )

        self.assertFalse(result["allowed"])

        self.assertIn("кулдаун", result["reason"].lower())

    def test_injury_cooldown_expired(self):

        """Кулдаун травмы истёк — травма разрешена."""

        parsed = {

            "valid": True,

            "action": "APPLY_INJURY",

            "params": {"size": 16},

        }

        # last_injury_report=4 -> reports_since = 10-4 = 6 > 5 (кулдаун истёк)

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=4,

        )

        self.assertTrue(result["allowed"])

        self.assertEqual(result["cost"], 0.0)

    def test_inject_into_channel_15_rejected(self):

        """Инъекция в канал 15 отклоняется."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 15,

                "value": 0.1,

            },

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        self.assertFalse(result["allowed"])

        # Канал 15 вне диапазона [2, 14], поэтому ошибка о диапазоне допустима

        self.assertTrue(

            "reserved" in result["reason"].lower() or "out of range" in result["reason"].lower(),

            f"Ожидалось упоминание 'reserved' или 'out of range', получено: {result['reason']}"

        )

    def test_inject_into_channel_0_rejected(self):

        """Инъекция в канал 0 отклоняется."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 0,

                "value": 0.1,

            },

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        self.assertFalse(result["allowed"])

    def test_inject_into_channel_1_rejected(self):

        """Инъекция в канал 1 отклоняется."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 1,

                "value": 0.1,

            },

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        self.assertFalse(result["allowed"])

    def test_max_injections_per_report(self):

        """MORPHOGEN_MAX_INJECTIONS_PER_REPORT соблюдается."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 5,

                "value": 0.1,

                "radius": 4,

            },

        }

        result = validate_action(

            parsed,

            budget_remaining=2.0,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

            morphogen_injections_this_report=config.MORPHOGEN_MAX_INJECTIONS_PER_REPORT,

        )

        self.assertFalse(result["allowed"])

        self.assertIn("лимит инъекций", result["reason"].lower())

    def test_morphogen_full_cost(self):

        """Полная стоимость морфогена не превышает бюджет."""

        parsed = {

            "valid": True,

            "action": "INJECT_MORPHOGEN",

            "params": {

                "channel": 5,

                "value": 3.0,

                "radius": 16,

            },

        }

        cost = compute_action_cost(parsed)

        self.assertLessEqual(cost, 1.0)

        result = validate_action(

            parsed,

            budget_remaining=0.4,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        self.assertFalse(result["allowed"])

        self.assertIn("бюджет", result["reason"].lower())

    def test_free_actions(self):

        """CONTINUE_TRAINING и STOP бесплатны."""

        for action in ("CONTINUE_TRAINING", "STOP"):

            parsed = {

                "valid": True,

                "action": action,

                "params": {} if action == "STOP" else {"steps": 10},

            }

            result = validate_action(

                parsed,

                budget_remaining=0.0,

                current_report_number=10,

                last_morphogen_report=-10,

                last_injury_report=-10,

            )

            self.assertTrue(result["allowed"])

            self.assertEqual(result["cost"], 0.0)

if __name__ == "__main__":

    unittest.main()