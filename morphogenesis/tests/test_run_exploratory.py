"""test_run_exploratory.py — exploratory-скрипт обязан оставлять пару start/finish.

Семь exploratory-прогонов 2026-10-21 закрылись без пары в каноническом журнале
(`lab/state.json` → `blockers`). Чинится процесс, а не журнал (§2): лаунчер
`run_exploratory.py` оборачивает скрипт в `Journal`. Тест держит три вещи:

1. успешный скрипт даёт ровно `start` + `finish`;
2. падение даёт `start` + `error` (с типом и текстом), а не тихий обрыв;
3. отсутствующий скрипт — отказ без записи в журнал (нельзя «стартовать» то,
   чего нет).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import config  # noqa: E402
import run_exploratory  # noqa: E402


@pytest.fixture()
def journal_dir(monkeypatch, tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    monkeypatch.setattr(config, "LOG_DIR", str(logs))
    return logs


def events(logs: Path) -> list[dict]:
    path = logs / "journal.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_success_writes_start_and_finish(journal_dir, tmp_path):
    script = tmp_path / "probe.py"
    script.write_text("print('[probe] ok')\n", encoding="utf-8")
    code = run_exploratory.main(
        ["--script", str(script), "--experiment", "E02b_probe_unit", "--note", "unit"]
    )
    assert code == 0
    rows = events(journal_dir)
    assert [row["event"] for row in rows] == ["start", "finish"]
    start, finish = rows
    assert start["experiment"] == "E02b_probe_unit"
    assert start["script"] == str(script)
    assert start["note"] == "unit"
    assert start["emits_run_finish"] is True
    assert finish["stop_reason"] == "finished"
    assert isinstance(finish["wall_seconds"], float)


def test_script_sees_its_own_file(journal_dir, tmp_path):
    """runpy даёт скрипту __file__ — иначе относительные пути внутри сломаются."""
    script = tmp_path / "writes.py"
    out = tmp_path / "seen.txt"
    script.write_text(
        f"import pathlib\npathlib.Path({str(out)!r}).write_text(__file__, encoding='utf-8')\n",
        encoding="utf-8",
    )
    run_exploratory.main(["--script", str(script), "--experiment", "E02b_probe_file"])
    assert Path(out).read_text(encoding="utf-8") == str(script)


def test_failure_writes_error(journal_dir, tmp_path):
    script = tmp_path / "boom.py"
    script.write_text("raise RuntimeError('cuda oom')\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        run_exploratory.main(["--script", str(script), "--experiment", "E02b_probe_boom"])
    rows = events(journal_dir)
    assert [row["event"] for row in rows] == ["start", "error"]
    assert rows[1]["error_type"] == "RuntimeError"
    assert "cuda oom" in rows[1]["error"]


def test_missing_script_does_not_touch_journal(journal_dir, tmp_path):
    code = run_exploratory.main(
        ["--script", str(tmp_path / "nope.py"), "--experiment", "E02b_probe_missing"]
    )
    assert code == 2
    assert events(journal_dir) == []

def test_clean_system_exit_zero_is_finish_not_error(journal_dir, tmp_path):
    """`raise SystemExit(main())` в скрипте — нормальный выход, а не ошибка.

    Этот баг поймал прогон E02b_lesion_minimal: скрипт отработал, записал
    артефакт и вышел через SystemExit(0), а обёртка записала `error` с
    `error_type: SystemExit, error: "0"` — успешный прогон выглядел проваленным.
    """
    script = tmp_path / "main_like.py"
    script.write_text(
        "import sys\n\ndef main():\n    return 0\n\nraise SystemExit(main())\n",
        encoding="utf-8",
    )
    code = run_exploratory.main(["--script", str(script), "--experiment", "E02b_probe_exit0"])
    assert code == 0
    rows = events(journal_dir)
    assert [row["event"] for row in rows] == ["start", "finish"]
    assert rows[1]["stop_reason"] == "finished"


def test_system_exit_nonzero_is_error(journal_dir, tmp_path):
    """Ненулевой код выхода остаётся ошибкой, а не «успехом с кодом 3»."""
    script = tmp_path / "exit3.py"
    script.write_text("raise SystemExit(3)\n", encoding="utf-8")
    code = run_exploratory.main(["--script", str(script), "--experiment", "E02b_probe_exit3"])
    assert code == 3
    rows = events(journal_dir)
    assert [row["event"] for row in rows] == ["start", "error"]
    assert rows[1]["error_type"] == "SystemExit"
