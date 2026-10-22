"""test_artifact_lock.py — замок на артефакт обязан ловить второй писатель.

Почему это тест: 22.10.2026 две обёртки стартовали одну перепись одновременно
с разными `--experiment` (у `lab.py` замок ключуется именем прогона), поэтому
оба процесса писали один `--out`. Дубль убили, вместе с ним умер и рабочий
процесс — 55 минут GPU без артефакта. Замок ниже ключуется путём результата,
так что такой сценарий становится отказом на старте, а не потерей прогона.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import artifact_lock  # noqa: E402


def test_guard_creates_and_releases_lock(tmp_path):
    out = tmp_path / "census_x.json"
    summary = tmp_path / "summary_x.json"
    with artifact_lock.artifact_guard(out, summary) as held:
        assert len(held) == 2
        for path in (out, summary):
            lock = Path(str(path) + ".lock")
            assert lock.exists()
            payload = json.loads(lock.read_text(encoding="utf-8"))
            assert payload["pid"] == os.getpid()
            assert payload["artifact"] == str(path)
    assert not Path(str(out) + ".lock").exists()
    assert not Path(str(summary) + ".lock").exists()


def test_second_process_is_refused_while_holder_alive(tmp_path):
    out = tmp_path / "census_x.json"
    script = (
        "import sys; sys.path.insert(0, r'%s')\n"
        "import artifact_lock\n"
        "try:\n"
        "    with artifact_lock.artifact_guard(r'%s'):\n"
        "        pass\n"
        "except SystemExit as exc:\n"
        "    print('refused:', exc)\n"
        "    raise SystemExit(3)\n"
        "raise SystemExit(0)\n" % (MORPH, out)
    )
    with artifact_lock.artifact_guard(out):
        proc = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
        )
    assert proc.returncode == 3, proc.stdout + proc.stderr
    # Кодировка консоли на Windows не UTF-8, поэтому проверяем ASCII-маркеры.
    assert "[lock]" in proc.stdout
    assert "pid=" in proc.stdout


def test_stale_lock_of_dead_process_is_taken_over(tmp_path):
    out = tmp_path / "census_x.json"
    lock = Path(str(out) + ".lock")
    # pid, которого нет: заведомо мёртвый номер процесса.
    lock.write_text(json.dumps({"pid": 999999, "artifact": str(out)}), encoding="utf-8")
    with artifact_lock.artifact_guard(out) as held:
        assert held
        payload = json.loads(lock.read_text(encoding="utf-8"))
        assert payload["pid"] == os.getpid()
    assert not lock.exists()


def test_empty_argument_is_ignored(tmp_path):
    with artifact_lock.artifact_guard(None, "") as held:
        assert held == []


def test_pid_alive_sees_current_process():
    assert artifact_lock._pid_alive(os.getpid()) is True
    assert artifact_lock._pid_alive(0) is False


def test_pid_alive_sees_dead_process():
    # Гасим дочерний процесс и проверяем, что он читается как мёртвый:
    # именно на этом держится перехват брошенного замка.
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    pid = proc.pid
    proc.wait(timeout=60)
    try:
        assert artifact_lock._pid_alive(pid) is False
    except PermissionError:  # pragma: no cover - Windows-специфика
        pytest.skip("процесс уже переиспользован системой")
