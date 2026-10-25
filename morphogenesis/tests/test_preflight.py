"""Тесты предполётной проверки: она обязана блокировать каждый из трёх отказов 25.10.

Правило лаборатории: у каждого гейта есть тест, который его валит. `preflight.py`
появился после трёх отказов запуска серии подряд (дважды `powershell` вместо `pwsh`,
один раз процесс умер молча), поэтому проверяем именно те условия, которые тогда
не были проверены:

1. пре-регистрация не закоммичена → блок;
2. в каталоге вывода уже есть артефакты будущих прогонов → блок (смешанное состояние);
3. диск меньше порога → блок.

Живую проверку замков не тестируем: она зависит от `tasklist` и от реальных процессов.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "preflight.py"


@pytest.fixture(scope="module")
def pf():
    spec = importlib.util.spec_from_file_location("preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_prereg_blocks(pf, tmp_path):
    ok, msg = pf.check_prereg(tmp_path / "no-such-plan.md")
    assert ok is False
    assert "пре-регистрации" in msg


def test_uncommitted_prereg_blocks(pf, tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text("# план\n", encoding="utf-8")
    ok, msg = pf.check_prereg(plan)
    assert ok is False
    assert "не закоммичена" in msg


def test_committed_prereg_passes(pf):
    ok, msg = pf.check_prereg(Path("AGENTS.md"))  # закоммиченный файл репозитория
    assert ok is True, msg


def test_nonempty_outdir_blocks(pf, tmp_path):
    (tmp_path / "w2bud3_cell_seed1.json").write_text("{}", encoding="utf-8")
    ok, msg = pf.check_outdir(tmp_path)
    assert ok is False
    assert "смешанное состояние" in msg


def test_empty_outdir_passes(pf, tmp_path):
    ok, msg = pf.check_outdir(tmp_path / "new-series")
    assert ok is True, msg


def test_disk_threshold_is_checked(pf):
    ok, msg = pf.check_disk(min_gb=0.0)
    assert ok is True, msg
    ok_huge, msg_huge = pf.check_disk(min_gb=1_000_000.0)
    assert ok_huge is False
