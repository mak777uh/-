"""test_lab_lock_clean.py — замок мёртвого прогона не должен держать серию 8 часов.

Зачем: инцидент 25.10. Первый запуск kill-and-keep не стартовал ни одного прогона, а
выглядел как «10 падений подряд»: `lab.py run` снимает замок в `finally`, но убийство
процесса-обёртки этого не делает, и замок живёт до TTL (480 минут). `lab.py lock-clean`
снимает только замки с мёртвым pid на этом хосте и не трогает живые.
"""
from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "lab.py"
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load():
    spec = importlib.util.spec_from_file_location("lab_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.LOCKS = ROOT / "lab" / "locks"
    return module


def write_lock(path: Path, pid: int, host: str | None = None) -> Path:
    path.write_text(json.dumps({
        "run_id": "20261025T000000Z-test",
        "experiment": path.stem,
        "owner": "test",
        "host": host or socket.gethostname(),
        "pid": pid,
        "started_at": "2026-10-25T00:00:00Z",
        "heartbeat_at": "2026-10-25T00:00:00Z",
        "ttl_minutes": 480,
    }, ensure_ascii=False), encoding="utf-8")
    return path


def test_pid_alive_detects_own_process():
    module = load()
    import os
    assert module._pid_alive(os.getpid()) is True


def test_dead_pid_lock_is_removed_but_live_lock_kept(tmp_path, monkeypatch):
    module = load()
    monkeypatch.setattr(module, "LOCKS", tmp_path)
    dead = write_lock(tmp_path / "dead_case.lock", 999999)
    import os
    live = write_lock(tmp_path / "live_case.lock", os.getpid())
    module.lock_clean(dry_run=False)
    assert not dead.exists(), "замок мёртвого pid должен быть снят"
    assert live.exists(), "живой замок трогать нельзя"


def test_foreign_host_lock_is_not_removed(tmp_path, monkeypatch):
    module = load()
    monkeypatch.setattr(module, "LOCKS", tmp_path)
    foreign = write_lock(tmp_path / "foreign.lock", 999999, host="another-host")
    module.lock_clean(dry_run=False)
    assert foreign.exists(), "замок с другого хоста не проверяем и не удаляем"


def test_dry_run_keeps_files(tmp_path, monkeypatch):
    module = load()
    monkeypatch.setattr(module, "LOCKS", tmp_path)
    dead = write_lock(tmp_path / "dry.lock", 999999)
    module.lock_clean(dry_run=True)
    assert dead.exists(), "dry-run ничего не удаляет"
