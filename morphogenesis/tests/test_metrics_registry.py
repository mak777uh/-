"""Тесты реестра величин: гейт обязан падать на каждом из трёх сегодняшних классов.

Правило лаборатории: у каждого гейта есть тест, который его валит. Иначе гейт
превращается в декорацию (как `if paths and not found` в claims_lint и как
`"{:.0f}"` в гейте чисел, дававший строку "0", которая есть в любом тексте).

Проверяем три класса ошибок 25.10:
1. величина без определения (подмена знаменателя была именно этим);
2. имя `_all` при знаменателе `valid` (молчаливая подмена знаменателя);
3. `derived_by_construction` без формулы (тавтология, выданная за свидетельство).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "metrics_registry.py"


def load_module():
    spec = importlib.util.spec_from_file_location("metrics_registry", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def registry_module():
    return load_module()


def write_registry(tmp_path: Path, metrics: dict, verdicts: dict | None = None) -> Path:
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({
        "note": "тестовый реестр",
        "rules": {},
        "metrics": metrics,
        "verdicts": verdicts or {},
        "undeclared_ok": {"by_aggregate": {}},
    }, ensure_ascii=False), encoding="utf-8")
    return path


def test_current_registry_is_green(registry_module):
    """Текущий `lab/metrics.json` проходит проверку (иначе CI красный)."""
    assert registry_module.check(registry_module.REGISTRY, quiet=True) == 0


def test_metric_without_definition_fails(registry_module, tmp_path):
    reg = write_registry(tmp_path, {"foo_median": {"denominator": "runs"}})
    assert registry_module.check(reg, quiet=True) == 1


def test_all_suffix_with_valid_denominator_fails(registry_module, tmp_path):
    reg = write_registry(tmp_path, {
        "crow_I_positive_k_all": {
            "definition": "число прогонов с I > 0",
            "fields": ["summary.type_counts"],
            "denominator": "valid",  # подмена: имя говорит `_all`
        },
    })
    assert registry_module.check(reg, quiet=True) == 1


def test_derived_by_construction_without_formula_fails(registry_module, tmp_path):
    reg = write_registry(tmp_path, {
        "manipulation_rho_per_step": {
            "definition": "rho(признак, вложение/клетко-шаги)",
            "fields": ["summary.type_traits"],
            "denominator": "valid",
            "derived_by_construction": True,
            # formula отсутствует — тавтология не объяснена
        },
    })
    assert registry_module.check(reg, quiet=True) == 1


def test_undeclared_metric_in_aggregate_fails(registry_module, tmp_path, monkeypatch):
    """Величина, которую агрегат выдаёт, но реестр не объявляет → гейт красный."""
    (tmp_path / "w2bud3_matrix.json").write_text(json.dumps({
        "by_arm": [{"arm": "cell", "mystery_median": 1.0}],
        "criteria": {},
    }), encoding="utf-8")
    reg = write_registry(tmp_path, {})
    monkeypatch.setattr(registry_module, "POND", tmp_path)
    monkeypatch.setattr(registry_module, "SOURCES", ["w2bud3_matrix.json"])
    assert registry_module.check(reg, quiet=True) == 1


def test_service_fields_are_not_treated_as_metrics(registry_module):
    """`arm`, `placement`, `merge_rule` — подписи, а не величины."""
    keys = registry_module.numeric_keys({"arm": "cell", "placement": "random",
                                        "mystery_k": 3, "survival": 0.2})
    assert keys == {"mystery_k", "survival"}
