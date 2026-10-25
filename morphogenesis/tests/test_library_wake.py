"""Сторож библиотекаря: отпечаток состояния и пробуждение по изменению."""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import library_wake  # noqa: E402


def _tree(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "morphogenesis" / "logs").mkdir(parents=True)
    (tmp_path / "morphogenesis" / "logs" / "journal.jsonl").write_text(
        '{"event":"start"}\n', encoding="utf-8"
    )
    (tmp_path / "reports").mkdir()
    (tmp_path / "articles").mkdir()
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "manuscript" / "paper.md").write_text("# Paper\n\n**v0.1**\n\n## 1. Intro\n", encoding="utf-8")
    (tmp_path / "lab").mkdir()
    (tmp_path / "lab" / "lit-queue.json").write_text(
        json.dumps({"items": [{"id": "L-001", "status": "new"}]}), encoding="utf-8"
    )
    (tmp_path / "lab" / "lit-board.json").write_text(
        json.dumps({"items": [{"id": "B-001", "status": "accepted", "wave": "current"}]}),
        encoding="utf-8",
    )
    return tmp_path


def test_first_check_reports_all_keys_and_second_is_quiet(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    first = library_wake.check(root, state)
    assert "journal" in first and "reports" in first
    second = library_wake.check(root, state)
    assert second == []


def test_new_journal_line_wakes(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    library_wake.check(root, state)
    journal = root / "morphogenesis" / "logs" / "journal.jsonl"
    journal.write_text(journal.read_text(encoding="utf-8") + '{"event":"finish"}\n', encoding="utf-8")
    assert library_wake.check(root, state) == ["journal"]


def test_new_report_wakes(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    library_wake.check(root, state)
    (root / "reports" / "2026-10-23-new.md").write_text("# новый отчёт\n", encoding="utf-8")
    assert "reports" in library_wake.check(root, state)


def test_queue_and_board_changes_wake(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    library_wake.check(root, state)
    (root / "lab" / "lit-queue.json").write_text(
        json.dumps({"items": [{"id": "L-002", "status": "new"}]}), encoding="utf-8"
    )
    changes = library_wake.check(root, state)
    assert "lit_queue" in changes


def test_cycle_appears_wakes(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    library_wake.check(root, state)
    (root / "lab" / "cycle.json").write_text(
        json.dumps({"id": "W-1", "phase": "run"}), encoding="utf-8"
    )
    assert "cycle" in library_wake.check(root, state)


def test_closed_run_wakes(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    (root / "lab" / "runs").mkdir()
    library_wake.check(root, state)
    (root / "lab" / "runs" / "R1.json").write_text(
        json.dumps({"id": "R1", "status": "finished"}), encoding="utf-8"
    )
    assert "runs" in library_wake.check(root, state)
    # тот же закрытый прогон второй раз не будит
    assert library_wake.check(root, state) == []


def test_running_manifest_does_not_count_as_finished(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    (root / "lab" / "runs").mkdir()
    library_wake.check(root, state)
    (root / "lab" / "runs" / "R2.json").write_text(
        json.dumps({"id": "R2", "status": "running"}), encoding="utf-8"
    )
    assert "runs" not in library_wake.check(root, state)


def test_experiment_artifact_wakes(tmp_path):
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    (root / "morphogenesis" / "experiments").mkdir(parents=True)
    library_wake.check(root, state)
    (root / "morphogenesis" / "experiments" / "x.json").write_text("{}", encoding="utf-8")
    assert "experiments" in library_wake.check(root, state)


def test_series_only_changes():
    assert library_wake.is_series_only(["polish"]) is True
    assert library_wake.is_series_only(["polish", "experiments"]) is True
    assert library_wake.is_series_only(["polish", "manuscript"]) is False
    assert library_wake.is_series_only(["board"]) is False
    assert library_wake.is_series_only([]) is False


def test_head_alone_is_not_a_wake_reason():
    assert library_wake.is_significant([]) is False
    assert library_wake.is_significant(["head"]) is False
    assert library_wake.is_significant(["head", "reports"]) is True
    assert library_wake.is_significant(["runs"]) is True


def test_wait_returns_timeout_without_changes(tmp_path, capsys):
    """Истёкший таймаут — не ошибка: код возврата 0, признак — строка в stdout.

    До 25.10 тест ждал 2, хотя wait() намеренно возвращает 0 («ночной прогон без
    изменений не должен выглядеть падением»). Тест не успели обновить вместе с
    кодом — поймано полным прогоном 605 тестов.
    """
    root = _tree(tmp_path)
    state = tmp_path / "state.json"
    library_wake.check(root, state)
    code = library_wake.wait(root, timeout=0.2, interval=0.05, state_path=state)
    assert code == 0
    assert "timeout" in capsys.readouterr().out
