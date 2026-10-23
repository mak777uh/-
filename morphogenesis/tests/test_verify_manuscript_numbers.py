"""test_verify_manuscript_numbers.py — числа рукописей сверяются с источниками.

Скрипт `scripts/verify_manuscript_numbers.py` замыкает цепочку
«артефакт → отчёт → текст»: пересчитывает величину из JSON и ищет её в разделе.
Тест держит две вещи: (1) на текущей рукописи проверка проходит; (2) если
подменить одно число в тексте, проверка падает именно на нём — иначе скрипт
ничего не проверяет.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_manuscript_numbers.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_numbers_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def test_repository_manuscript_numbers_match_artifacts(capsys):
    module = load_module()
    assert module.main() == 0
    out = capsys.readouterr().out
    assert "ошибок: 0" in out
    assert "проверено чисел: " in out


def test_wrong_number_in_text_is_caught(tmp_path, monkeypatch, capsys):
    """Порча числа в замороженной рукописи обязана валить проверку."""
    module = load_module()
    text = (ROOT / "manuscript" / "archive" / "paper-v1-morphology.md").read_text(encoding="utf-8")
    assert "0.434" in text
    broken = tmp_path / "paper.md"
    broken.write_text(text.replace("0.434", "0.499", 1), encoding="utf-8")
    monkeypatch.setattr(module, "PAPER", broken)
    assert module.main() == 1
    out = capsys.readouterr().out
    assert "0.434" in out


def test_v2_numbers_come_from_world_doc(tmp_path, monkeypatch, capsys):
    """Число новой рукописи без источника в docs/world-design.md — ошибка."""
    module = load_module()
    world = module.WORLD_DOC.read_text(encoding="utf-8")
    broken_world = tmp_path / "world-design.md"
    broken_world.write_text(world.replace("76711", "70000"), encoding="utf-8")
    monkeypatch.setattr(module, "WORLD_DOC", broken_world)
    assert module.main() == 1
    assert "76711" in capsys.readouterr().out


def test_missing_section_fails_loudly(tmp_path, monkeypatch):
    module = load_module()
    broken = tmp_path / "paper.md"
    broken.write_text("# Paper\n\nнет разделов\n", encoding="utf-8")
    monkeypatch.setattr(module, "PAPER", broken)
    with pytest.raises(SystemExit):
        module.main()
