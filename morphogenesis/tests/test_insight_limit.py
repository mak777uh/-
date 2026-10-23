"""Предел открытых инсайтов: не свалка, но и не блок своевременной регистрации."""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import insight  # noqa: E402


def _open(n: int) -> list[dict]:
    return [{"id": f"I-{i:03d}", "status": "open"} for i in range(1, n + 1)]


def test_limit_allows_normal_flow():
    assert insight.MAX_OPEN >= 10
    assert insight.can_add(_open(3))
    assert insight.can_add(_open(11))


def test_limit_still_stops_a_pile():
    assert not insight.can_add(_open(insight.MAX_OPEN))
    assert not insight.can_add(_open(insight.MAX_OPEN + 3))
