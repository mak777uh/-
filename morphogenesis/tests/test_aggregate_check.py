"""test_aggregate_check.py — агрегат обязан совпадать с артефактами.

Проверяем три вещи:
1. все агрегаты в morphogenesis/experiments/E09_pond проходят проверку;
2. чекер ловит перепутанное направление (инвайдер B, а доля записана как доля A);
3. чекер ловит неверное стартовое значение (резидент A, а старт 0.0).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "aggregate_check.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("aggregate_check_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_all_aggregates_consistent():
    module = load_checker()
    agg_dir = ROOT / "morphogenesis" / "experiments" / "E09_pond"
    errors = []
    for path in sorted(agg_dir.glob("*.json")):
        errs, _ = module.check_file(path)
        errors += errs
    assert not errors, errors[:5]


def test_checker_catches_swapped_direction():
    module = load_checker()
    row = {
        "direction": "invade-B-into-A-resident",
        "invader_share_final": 0.9984,   # это доля A (резидента), а не инвайдера B
        "a_share_final": 0.9984,
        "a_share_start": 0.0,
    }
    errors, _ = module.check_row(row, strict=False)
    assert any("invader_share_final" in e for e in errors)


def test_checker_catches_wrong_start():
    module = load_checker()
    row = {
        "direction": "invade-A-into-B-resident",
        "invader_share_final": 0.015,
        "a_share_final": 0.015,
        "a_share_start": 1.0,   # резидент B должен стартовать с ~0.0
    }
    errors, _ = module.check_row(row, strict=False)
    assert any("a_share_start" in e for e in errors)
