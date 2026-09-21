"""

test_budget_edge_cases.py — Тесты граничных случаев бюджета.

[v5.5-EXP FINAL Rev.7]

Проверяет:

- бюджет = 0 -> все платные действия отклоняются;

- бюджет = 0.5 -> INJECT_MORPHOGEN с полной стоимостью > 0.5 отклоняется;

- APPLY_INJURY не списывается с бюджета;

- CONTINUE_TRAINING бесплатен.

"""

import sys

import os

import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from cognition.action_validator import validate_action, compute_action_cost

class TestBudgetEdgeCases(unittest.TestCase):

    def test_zero_budget_rejects_paid_actions(self):

        """Бюджет = 0 -> все платные действия отклоняются."""

        paid_actions = [

            ("MODIFY_DT", {"new_value": 0.1}),

            ("MODIFY_LR", {"new_value": 1e-3}),

            ("MODIFY_L1_REG", {"new_value": 0.001}),

            ("MODIFY_TARGET_B0", {"new_value": 3}),

        ]

        for action, params in paid_actions:

            parsed = {

                "valid": True,

                "action": action,

                "params": params,

            }

            result = validate_action(

                parsed,

                budget_remaining=0.0,

                current_report_number=10,

                last_morphogen_report=-10,

                last_injury_report=-10,

            )

            self.assertFalse(

                result["allowed"],

                f"{action} should be rejected with zero budget",

            )

    def test_partial_budget_rejects_expensive_morphogen(self):

        """Бюджет = 0.5 -> морфоген с полной стоимостью > 0.5 отклоняется."""

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

        if cost > 0.5:

            result = validate_action(

                parsed,

                budget_remaining=0.5,

                current_report_number=10,

                last_morphogen_report=-10,

                last_injury_report=-10,

            )

            self.assertFalse(result["allowed"])

    def test_injury_not_from_budget(self):

        """APPLY_INJURY не списывается с бюджета."""

        parsed = {

            "valid": True,

            "action": "APPLY_INJURY",

            "params": {"size": 16},

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

    def test_continue_training_free(self):

        """CONTINUE_TRAINING бесплатен."""

        parsed = {

            "valid": True,

            "action": "CONTINUE_TRAINING",

            "params": {"steps": 10},

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

    def test_stop_free(self):

        """STOP бесплатен."""

        parsed = {

            "valid": True,

            "action": "STOP",

            "params": {},

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

    def test_budget_exactly_equals_cost(self):

        """Бюджет точно равен стоимости -> действие разрешено."""

        parsed = {

            "valid": True,

            "action": "MODIFY_DT",

            "params": {"new_value": 0.1},

        }

        cost = compute_action_cost(parsed)

        result = validate_action(

            parsed,

            budget_remaining=cost,

            current_report_number=10,

            last_morphogen_report=-10,

            last_injury_report=-10,

        )

        self.assertTrue(result["allowed"])

        self.assertAlmostEqual(result["budget_remaining"], 0.0, places=6)

if __name__ == "__main__":

    unittest.main()