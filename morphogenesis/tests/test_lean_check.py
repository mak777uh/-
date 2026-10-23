"""test_lean_check.py — инвентарь формальных гипотез разбирается корректно.

Зачем: Lean — третий инструмент (рядом с CPU и GPU), и формальные гипотезы должны
попадать в отчёты автоматически. Тест держит разбор имён теорем и идентификаторов
гипотез, на котором строится `lab/formal.json`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import lean_check as lc  # noqa: E402

SAMPLE = """
/-
F-BUDGET-1 (один шаг): сумма сохраняется.
F-BUDGET-2 (любая последовательность): доказано индукцией.
-/

structure World where
  resource : Int

theorem budget_conserved (w : World) (rate : Int) :
    True := by
  trivial

theorem run_conserves (w : World) (rates : List Int) :
    True := by
  trivial
"""


def test_parse_theorems():
    names = lc.parse_theorems(SAMPLE)
    assert names == ["budget_conserved", "run_conserves"]


def test_parse_hypotheses_unique_and_ordered():
    ids = lc.parse_hypotheses(SAMPLE)
    assert ids == ["F-BUDGET-1", "F-BUDGET-2"]


def test_parse_handles_empty():
    assert lc.parse_theorems("") == []
    assert lc.parse_hypotheses("") == []


def test_real_budget_file_is_parsed():
    path = ROOT / "formal" / "Budget.lean"
    if not path.exists():
        return
    source = path.read_text(encoding="utf-8")
    theorems = lc.parse_theorems(source)
    assert "run_conserves" in theorems
    assert "no_free_energy" in theorems
    assert "F-BUDGET-1" in lc.parse_hypotheses(source)
