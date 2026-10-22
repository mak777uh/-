"""test_validate_runs.py — контракт артефактов должен падать на битом JSON.

Смысл: снаружи (депозит, заявки, рецензент) числа берутся из машиночитаемых
карточек `lab/science/<run_id>.json`, а не из текста отчётов. Если карточка
сломана или поле вне enum, это должно ловиться в CI, а не глазами рецензента.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import validate_runs as vr  # noqa: E402


def setup_tree(tmp_path: Path) -> None:
    (tmp_path / "schema").mkdir()
    for name in ("run.schema.json", "runs_index.schema.json"):
        shutil.copy(ROOT / "lab" / "schema" / name, tmp_path / "schema" / name)
    (tmp_path / "science").mkdir()
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "demo_run.json").write_text("{}", encoding="utf-8")


def point_module_at(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(vr, "SCHEMA_DIR", tmp_path / "schema")
    monkeypatch.setattr(vr, "SCIENCE_DIR", tmp_path / "science")
    monkeypatch.setattr(vr, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(vr, "INDEX", tmp_path / "runs.index.json")


def card(run_id: str = "demo_run") -> dict:
    return {
        "run_id": run_id,
        "experiment_id": "E02c",
        "seed": 42,
        "regime": "fp32",
        "steps": 2000,
        "class": "struct_1",
        "metrics": {"best_loss": 1.1, "struct_2": 0},
        "preregistered": "unknown",
        "created_at": "2026-10-22T15:37:00Z",
        "source": "converted",
        "notes": "",
    }


def test_valid_card_passes(tmp_path, monkeypatch):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    (tmp_path / "science" / "demo_run.json").write_text(
        json.dumps(card()), encoding="utf-8"
    )
    assert vr.main([]) == 0


def test_unknown_class_fails(tmp_path, monkeypatch, capsys):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    bad = card()
    bad["class"] = "struct_3"
    (tmp_path / "science" / "demo_run.json").write_text(json.dumps(bad), encoding="utf-8")
    assert vr.main([]) == 1
    out = capsys.readouterr().out
    assert "enum" in out


def test_missing_required_field_fails(tmp_path, monkeypatch):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    bad = card()
    bad.pop("preregistered")
    (tmp_path / "science" / "demo_run.json").write_text(json.dumps(bad), encoding="utf-8")
    assert vr.main([]) == 1


def test_broken_json_fails(tmp_path, monkeypatch):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    (tmp_path / "science" / "demo_run.json").write_text("{не json", encoding="utf-8")
    assert vr.main([]) == 1


def test_run_id_must_match_filename(tmp_path, monkeypatch):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    (tmp_path / "science" / "demo_run.json").write_text(
        json.dumps(card(run_id="other_run")), encoding="utf-8"
    )
    assert vr.main([]) == 1


def test_strict_requires_cards(tmp_path, monkeypatch):
    setup_tree(tmp_path)
    point_module_at(tmp_path, monkeypatch)
    assert vr.main(["--strict"]) == 1
    assert vr.main([]) == 0
