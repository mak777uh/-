"""Доска литературы: схема, сроки решений и человеческий вид (AGENTS §3a.3b, §6.7a)."""
from __future__ import annotations

import datetime as dt
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import lit_board  # noqa: E402


def _item(**over) -> dict:
    base = {
        "id": "B-001",
        "type": "known_fact",
        "target": {"kind": "hypothesis", "id": "H-X-1", "ref": ""},
        "statement": "что-то известно науке",
        "evidence": [{"library": "hypotheses/nca-frontier.md#F1", "note": ""}],
        "action": {"kind": "text", "detail": "поправить формулировку"},
        "status": "new",
        "wave": "current",
        "owner": "librarian",
        "created_at": dt.date.today().isoformat(),
        "decided_at": None,
        "why": None,
        "links": {"insights": [], "tasks": [], "reports": []},
    }
    base.update(over)
    return base


def test_next_id_continues_sequence():
    assert lit_board.next_id([]) == "B-001"
    assert lit_board.next_id([_item(id="B-002"), _item(id="B-007")]) == "B-008"


def test_valid_item_passes():
    errors, warnings = lit_board.validate_items([_item()])
    assert errors == []
    assert warnings == []


def test_unknown_type_and_status_are_errors():
    errors, _ = lit_board.validate_items([_item(type="мнение", status="done?")])
    assert any("type" in e for e in errors)
    assert any("status" in e for e in errors)


def test_evidence_must_point_to_existing_library_entry():
    errors, _ = lit_board.validate_items(
        [_item(evidence=[{"library": "hypotheses/no-such-file.md#X", "note": ""}])]
    )
    assert any("несуществующий" in e for e in errors)


def test_empty_evidence_is_error():
    errors, _ = lit_board.validate_items([_item(evidence=[])])
    assert any("evidence" in e for e in errors)


def test_accepted_requires_link_and_reason():
    errors, _ = lit_board.validate_items([_item(status="accepted", decided_at=None)])
    text = " ".join(errors)
    assert "причина" in text or "why" in text
    assert "ссылки" in text


def test_accepted_with_insight_passes():
    errors, _ = lit_board.validate_items(
        [
            _item(
                status="accepted",
                decided_at=(dt.date.today() - dt.timedelta(days=1)).isoformat(),
                why="меняем формулировку",
                links={"insights": ["I-013"], "tasks": [], "reports": []},
            )
        ]
    )
    assert errors == []


def test_stale_new_item_is_error_after_two_weeks():
    old = (dt.date.today() - dt.timedelta(days=20)).isoformat()
    errors, _ = lit_board.validate_items([_item(created_at=old)])
    assert any("без решения" in e for e in errors)


def test_deferred_moves_to_paused_wave_and_keeps_reason():
    data = {"schema_version": 1, "items": [_item()]}
    item = lit_board._transition(data, "B-001", "deferred", "линия на паузе")
    assert item["wave"] == "paused"
    assert item["why"] == "линия на паузе"
    assert item["decided_at"]


def test_render_lists_current_and_paused():
    data = {
        "schema_version": 1,
        "items": [
            _item(id="B-001"),
            _item(
                id="B-002",
                status="deferred",
                wave="paused",
                why="вернуть позже",
                decided_at=(dt.date.today() - dt.timedelta(days=1)).isoformat(),
            ),
        ],
    }
    text = lit_board.render(data)
    assert "Доска литературы" in text
    assert "B-001" in text and "B-002" in text
    assert "Отложено" in text
