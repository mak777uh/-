"""test_check_section_refs.py — ссылки на разделы рукописи (`§4.7`, `§5.6`).

Разделы вставляются в середину и нумерация сдвигается (T4-результат стал §4.12,
синтез — §5.6), поэтому ссылка на несуществующий раздел — это утверждение о
тексте, которого нет. `lab.py validate` проверяет карту рукописи, но не ссылки
внутри текста; этот тест держит линтер и сам текст.

Проверяется: существующая ссылка, битая ссылка с номером строки, диапазон по
обоим концам, пропуск ссылок на разделы спецификации («spec §9.2»), игнор блоков
кода, код возврата 1 и 2.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_section_refs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_section_refs_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


MANUSCRIPT = """# Title

## 1. Introduction

See §1 and §2.

## 2. Methods

### 2.1. Determinism

As in the specification §9.2, see §2.1.

## 4. Results

### 4.7. Carriers

### 4.11. Last

Range §4.7–§4.11 is fine.
"""


def test_sections_are_parsed():
    module = load_module()
    assert module.sections(MANUSCRIPT) == {"1", "2", "2.1", "4", "4.7", "4.11"}


def test_valid_refs_pass(tmp_path):
    module = load_module()
    doc = write(tmp_path / "paper.md", MANUSCRIPT)
    total, problems = module.check([doc])
    assert total >= 4
    assert problems == []


def test_missing_section_is_reported_with_line(tmp_path):
    module = load_module()
    doc = write(tmp_path / "paper.md", "## 4. Results\n\n### 4.7. X\n\nno §4.13 yet\n")
    total, problems = module.check([doc])
    assert total == 1
    assert len(problems) == 1 and ":5:" in problems[0] and "§4.13" in problems[0]


def test_range_checks_both_ends(tmp_path):
    module = load_module()
    doc = write(tmp_path / "paper.md", "## 4. Results\n\n### 4.7. X\n\nсм. §4.7–§4.12\n")
    total, problems = module.check([doc])
    assert total == 1
    assert "§4.12" in problems[0]


def test_spec_refs_are_skipped(tmp_path):
    module = load_module()
    doc = write(
        tmp_path / "paper.md",
        "## 1. Intro\n\nContract of spec §9.2 and спецификация §9.2 hold.\n",
    )
    total, problems = module.check([doc])
    assert (total, problems) == (0, [])


def test_code_fences_are_not_scanned(tmp_path):
    module = load_module()
    doc = write(tmp_path / "paper.md", "## 1. Intro\n\n```\n§9.9 is code\n```\nсм. §1\n")
    total, problems = module.check([doc])
    assert (total, problems) == (1, [])


def test_main_codes(tmp_path, capsys):
    module = load_module()
    good = write(tmp_path / "good.md", MANUSCRIPT)
    bad = write(tmp_path / "bad.md", "## 1. Intro\n\n§1.5 missing\n")
    assert module.main([str(good)]) == 0
    assert module.main([str(bad)]) == 1
    assert module.main([str(tmp_path / "nope.md")]) == 2


def test_repository_manuscripts_have_no_orphan_refs():
    """Плотная сеть §-ссылок живёт в замороженной статье; в новой их меньше, но нет битых."""
    module = load_module()
    archived = ROOT / "manuscript" / "archive" / "paper-v1-morphology.md"
    total, problems = module.check([archived])
    assert total > 20, f"подозрительно мало ссылок на разделы в архиве: {total}"
    assert problems == []

    current = ROOT / "manuscript" / "paper.md"
    total_v2, problems_v2 = module.check([current])
    assert total_v2 >= 3, f"в новой рукописи почти нет ссылок на разделы: {total_v2}"
    assert problems_v2 == []
