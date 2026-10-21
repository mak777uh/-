"""Очередь пунктов lab/queue.json: claim до запуска и один GPU-лейн.

Замок появляется в момент запуска, поэтому два агента успевают одновременно
запланировать один эксперимент. Тесты фиксируют контракт очереди: чужой живой
claim не перебивается, просроченный — перехватывается, второй `running`
запрещён, а validate ловит ссылку на несуществующую гипотезу.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LAB_PY = ROOT / "scripts" / "lab.py"


def load_lab():
    spec = importlib.util.spec_from_file_location("lab_queue_module", LAB_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_queue(tmp_path: Path, items: list[dict]) -> Path:
    path = tmp_path / "queue.json"
    path.write_text(
        json.dumps({"schema_version": 1, "items": items}, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def item(
    item_id: str,
    status: str = "planned",
    owner: str | None = None,
    heartbeat_at: str | None = None,
    hypothesis: str | None = None,
) -> dict:
    return {
        "id": item_id,
        "status": status,
        "owner": owner,
        "claimed_at": heartbeat_at,
        "heartbeat_at": heartbeat_at,
        "ttl_minutes": 240,
        "hypothesis": hypothesis,
    }


def test_real_queue_is_consistent() -> None:
    """Очередь репозитория проходит проверку контракта."""
    lab = load_lab()
    registry = json.loads((ROOT / "lab" / "registry.json").read_text(encoding="utf-8"))
    errors, _warnings, count = lab._check_queue(registry)
    assert not errors, "\n".join(errors)
    assert count >= 1


def test_second_running_item_is_rejected(tmp_path: Path) -> None:
    """GPU-лейн один: второй пункт в статусе running не занимается."""
    lab = load_lab()
    path = make_queue(
        tmp_path,
        [
            item("a", "running", "lead", lab.now_utc()),
            item("b"),
        ],
    )
    with pytest.raises(SystemExit):
        lab.item_claim("b", "other", status="running", path=path)


def test_foreign_live_claim_blocks_claim(tmp_path: Path) -> None:
    """Живой чужой claim не перебивается даже без статуса running."""
    lab = load_lab()
    path = make_queue(tmp_path, [item("a", "claimed", "lead", lab.now_utc())])
    with pytest.raises(SystemExit):
        lab.item_claim("a", "other", path=path)


def test_stale_claim_can_be_taken(tmp_path: Path) -> None:
    """Просроченный claim перехватывается: владелец не подаёт признаков жизни."""
    lab = load_lab()
    path = make_queue(tmp_path, [item("a", "claimed", "lead", "2020-01-01T00:00:00Z")])
    claimed = lab.item_claim("a", "other", path=path)
    assert claimed["owner"] == "other"
    assert claimed["status"] == "claimed"


def test_validate_flags_unknown_hypothesis_and_two_running(tmp_path: Path) -> None:
    """validate ловит ссылку на несуществующую гипотезу и два running."""
    lab = load_lab()
    registry = {"program": {"next_hypotheses": [{"id": "H-X"}]}}
    path = make_queue(
        tmp_path,
        [
            item("a", "running", "lead", lab.now_utc(), hypothesis="H-NOPE"),
            item("b", "running", "lead", lab.now_utc()),
        ],
    )
    errors, _warnings, _count = lab._check_queue(registry, path=path)
    text = "\n".join(errors)
    assert "H-NOPE" in text
    assert "running" in text


def test_claim_requires_owner_and_heartbeat(tmp_path: Path) -> None:
    """Статус claimed без owner или heartbeat — ошибка контракта."""
    lab = load_lab()
    registry = {"program": {"next_hypotheses": []}}
    path = make_queue(tmp_path, [{"id": "a", "status": "claimed"}])
    errors, _warnings, _count = lab._check_queue(registry, path=path)
    text = "\n".join(errors)
    assert "без owner" in text
    assert "без heartbeat_at" in text
