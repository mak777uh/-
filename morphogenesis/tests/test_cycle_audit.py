"""test_cycle_audit.py — тест, что цикл движется всеми тремя ногами.

Владелец: «сделай тест, что в новых циклах ты движешься вместе с чтением гипотез и
библиотеки». Тест держит две вещи:

1) классификация файлов по ногам работает (эксперименты / чтение / гипотезы);
2) если хотя бы одна нога пустая — скрипт это называет узким местом и падает в --ci.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "cycle_audit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cycle_audit_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_classify_splits_three_legs():
    module = load_module()
    files = [
        "morphogenesis/experiments/E09_pond/sense_noise_matrix.json",
        "lab/insights.json",
        "library/board.md",
        "lab/registry.json",
        "README.md",
    ]
    legs = module.classify(files)
    assert set(legs) == {"эксперименты", "чтение", "гипотезы"}
    assert legs["эксперименты"], "артефакт прогона должен попасть в ногу экспериментов"
    assert "lab/insights.json" in legs["чтение"]
    assert "library/board.md" in legs["чтение"]
    assert "lab/registry.json" in legs["гипотезы"]
    # файл вне ног не приписывается никуда
    assert all("README.md" not in hit for hit in legs.values())


def test_empty_leg_is_named(monkeypatch, capsys):
    module = load_module()
    monkeypatch.setattr(
        module, "changed_files",
        lambda days: ["morphogenesis/experiments/E09_pond/x.json", "lab/registry.json"],
    )
    code = module.main(["--days", "1", "--ci"])
    out = capsys.readouterr().out
    assert code == 1
    assert "чтение" in out and "узкое место" in out, out


def test_all_legs_pass(monkeypatch, capsys):
    module = load_module()
    monkeypatch.setattr(
        module, "changed_files",
        lambda days: [
            "morphogenesis/experiments/E09_pond/x.json",
            "lab/insights.json",
            "lab/registry.json",
        ],
    )
    code = module.main(["--days", "1", "--ci"])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "все три ноги" in out
