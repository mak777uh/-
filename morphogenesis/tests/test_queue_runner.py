"""Тесты конвейера очереди: он обязан не запускать неподготовленное и не закрывать сам.

Правило лаборатории: у каждого гейта есть тест, который его валит. Конвейер опасен именно
тем, что может «поехать» без критерия или сам себя принять, поэтому проверяем ровно это:

1. приоритет = импакт / стоимость (а не номер в файле);
2. пункт без `prereg` не готов к запуску;
3. пункт без `launch.command` не исполним — это идея, а не работа;
4. `gated_by` не даёт обогнать зависимость;
5. сухой прогон не меняет статус и не ставит `closed`.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "queue_runner.py"


@pytest.fixture(scope="module")
def qr():
    spec = importlib.util.spec_from_file_location("queue_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def item(id_, **kw):
    base = {"id": id_, "status": "planned", "cost_gpu_h": 1.0}
    base.update(kw)
    return base


def test_priority_is_impact_over_cost(qr):
    cheap_important = item("a", impact=5, cost_gpu_h=0.5)
    costly_useful = item("b", impact=3, cost_gpu_h=5.0)
    assert qr.priority(cheap_important) > qr.priority(costly_useful)


def test_missing_prereg_is_not_ready(qr):
    ok, why = qr.prereg_ready(item("a"))
    assert ok is False
    assert "prereg" in why


def test_missing_launch_is_not_executable(qr):
    ok, why = qr.launch_ready(item("a", prereg="reports/x.md"))
    assert ok is False
    assert "launch.command" in why


def test_gate_not_closed_blocks(qr):
    data = {"items": [item("dep", status="planned"), item("x", gated_by=["dep"])]}
    assert qr.gates_closed(data["items"][0], data) is True
    assert qr.gates_closed(data["items"][1], data) is False


def test_dry_run_does_not_change_status(qr, tmp_path, monkeypatch):
    data = {
        "items": [item("a", impact=5, cost_gpu_h=0.1, prereg="reports/x.md",
                       launch={"command": "echo hi", "outdir": "tmp"})],
    }
    queue_path = tmp_path / "queue.json"
    queue_path.write_text(__import__("json").dumps(data), encoding="utf-8")
    monkeypatch.setattr(qr, "save_queue", lambda d, p=None: None)
    monkeypatch.setattr(qr, "live_locks", lambda: [])
    monkeypatch.setattr(qr, "prereg_ready", lambda i: (True, "ok"))
    qr.run_once(data, dry_run=True, confirmed=False)
    assert data["items"][0]["status"] == "planned"  # сухой прогон ничего не тронул
