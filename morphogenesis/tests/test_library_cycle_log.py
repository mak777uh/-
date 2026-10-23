"""Лог циклов библиотекаря: окна фаз, сводка событий, рендер."""
from __future__ import annotations

import datetime as dt
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import library_cycle_log as logmod  # noqa: E402


def _history():
    return [
        {"phase": "run", "at": "2026-10-23T15:35:00+03:00", "by": "lead", "note": "старт"},
        {"phase": "interpret", "at": "2026-10-23T18:55:00+03:00", "by": "lead", "note": "числа есть"},
    ]


def test_windows_sorted_and_last_open_ended():
    now = dt.datetime(2026, 10, 23, 20, 0, tzinfo=dt.timezone.utc)
    items = logmod.windows(_history(), now=now)
    assert [w["phase"] for w in items] == ["run", "interpret"]
    assert items[0]["end"] == items[1]["start"]
    assert items[1]["end"] == now


def test_windows_skips_entries_without_time():
    items = logmod.windows([{"phase": "run", "at": None}, {"phase": "close", "at": "2026-10-23T16:00:00Z"}])
    assert [w["phase"] for w in items] == ["close"]


def test_summarize_empty_and_full():
    empty = {"files": [], "board": [], "insights": [], "git_ok": True}
    assert logmod.summarize(empty) == "—"
    full = {
        "files": ["library/answers.md", "library/synthesis/x.md"],
        "board": [{"id": "B-001", "status": "accepted"}],
        "insights": [{"id": "I-001"}],
        "git_ok": True,
    }
    text = logmod.summarize(full)
    assert "answers.md" in text and "B-001" in text and "I-001" in text


def test_render_contains_phases_and_notes(monkeypatch, tmp_path):
    monkeypatch.setattr(
        logmod,
        "events_for",
        lambda window, root: {"files": ["library/answers.md"], "board": [], "insights": [], "git_ok": True},
    )
    cycle = {
        "id": "W-2026-10-23-p1",
        "wave": "P1",
        "type": "research",
        "phase": "interpret",
        "hypothesis_ids": ["H33"],
        "phase_history": _history(),
    }
    text = logmod.render(cycle, tmp_path)
    assert "W-2026-10-23-p1" in text
    assert "`run`" in text and "`interpret`" in text
    assert "старт" in text
    assert "answers.md" in text


def test_render_without_history(tmp_path):
    cycle = {"id": "W-2026-10-23-x", "phase": "prepare", "wave": "-", "hypothesis_ids": []}
    text = logmod.render(cycle, tmp_path)
    assert "истории фаз нет" in text
