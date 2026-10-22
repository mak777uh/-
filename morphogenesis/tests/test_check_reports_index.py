"""test_check_reports_index.py — каждый отчёт обязан быть строкой в индексе.

Индекс журнала (`reports/README.md`) — человеческая точка входа: отчёт, которого
там нет, существует только для тех, кто читает git. `lab.py validate` сверяет
строку README-журнала и карту рукописи, но не полноту индекса отчётов, поэтому
эта дырка закрывается здесь.

Тест проверяет: пропуск README/TEMPLATE, обнаружение отчёта без строки, код
возврата, и — отдельным тестом — что в самом репозитории индекс полон.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_reports_index.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_reports_index_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def test_missing_report_is_detected(tmp_path):
    module = load_module()
    reports = tmp_path / "reports"
    write(reports / "2026-10-22-a.md", "# a\n")
    write(reports / "2026-10-22-b.md", "# b\n")
    write(reports / "README.md", "# index\n")
    write(reports / "TEMPLATE.md", "# template\n")
    index = write(reports / "README.md", "- [a](2026-10-22-a.md)\n")

    total, missing = module.check(reports, index)
    assert total == 2, "README и TEMPLATE не считаются отчётами"
    assert missing == ["2026-10-22-b.md"]


def test_complete_index_passes(tmp_path, capsys):
    module = load_module()
    reports = tmp_path / "reports"
    write(reports / "2026-10-22-a.md", "# a\n")
    index = write(reports / "README.md", "- [a](2026-10-22-a.md)\n")
    assert module.main(["--reports", str(reports), "--index", str(index)]) == 0
    assert "без строки в индексе: 0" in capsys.readouterr().out


def test_main_returns_one_when_report_missing(tmp_path, capsys):
    module = load_module()
    reports = tmp_path / "reports"
    write(reports / "2026-10-22-a.md", "# a\n")
    index = write(reports / "README.md", "пусто\n")
    assert module.main(["--reports", str(reports), "--index", str(index)]) == 1
    assert "2026-10-22-a.md" in capsys.readouterr().out


def test_main_returns_two_for_missing_paths(tmp_path):
    module = load_module()
    assert module.main(["--reports", str(tmp_path / "nope"), "--index", str(tmp_path / "nope.md")]) == 2


def test_repository_reports_index_is_complete():
    module = load_module()
    total, missing = module.check(ROOT / "reports", ROOT / "reports" / "README.md")
    assert total > 30, f"подозрительно мало отчётов: {total}"
    assert missing == []
