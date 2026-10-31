"""Тесты гейта снимков: он обязан поймать класс ошибки «снимок обещает то, чего нет».

Основание: 31.10 `lab/checkpoints.json` заявлял ready 12 из 12, а на диске лежал один вес. Гейты этого не видели.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_snapshots.py"


def _repo(tmp: Path, *, declared_ready: int, files_present: int, active: list[str] | None = None) -> Path:
    lab = tmp / "lab"
    (lab / "runs").mkdir(parents=True, exist_ok=True)
    (lab / "locks").mkdir(parents=True, exist_ok=True)
    items = []
    for i in range(declared_ready):
        rel = f"morphogenesis/checkpoints/run{i}/nca_final.pt"
        path = tmp / rel
        if i < files_present:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x")
            items.append({"family": f"run{i}", "file": "nca_final.pt", "ready": True, "path": rel})
        else:
            items.append({"family": f"run{i}", "file": "nca_final.pt", "ready": True, "path": None})
    (lab / "checkpoints.json").write_text(json.dumps({
        "requirements": {"E02b": {"required": declared_ready, "ready": declared_ready,
                                  "missing": [], "items": items}}
    }), encoding="utf-8")
    (lab / "state.json").write_text(json.dumps({"active_runs": active or []}), encoding="utf-8")
    return tmp


def _run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--ci"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_snapshot_promising_absent_files_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path, declared_ready=3, files_present=1)
    r = _run(root)
    assert r.returncode == 1, r.stdout
    assert "обещает то, чего нет" in r.stdout


def test_snapshot_truthful_passes(tmp_path: Path) -> None:
    root = _repo(tmp_path, declared_ready=2, files_present=2)
    r = _run(root)
    assert r.returncode == 0, r.stdout


def test_active_run_without_lock_or_manifest_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path, declared_ready=1, files_present=1, active=["ghost_run_42"])
    r = _run(root)
    assert r.returncode == 1
    assert "числится активным" in r.stdout


def test_orphan_lock_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path, declared_ready=1, files_present=1)
    (root / "lab" / "locks" / "stale.lock").write_text("{}", encoding="utf-8")
    r = _run(root)
    assert r.returncode == 1
    assert "без записи в state.active_runs" in r.stdout
