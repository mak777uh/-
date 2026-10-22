"""test_lab_regime_fields.py — контракт v1.1 в раннере: regime и хеш весов.

Зачем: карточка и индекс должны получать режим и sha256 весов от раннера, а не
от памяти человека. Старые манифесты при этом не меняются: поля пишутся только
для новых прогонов и только если флаг задан.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "scripts" / "lab.py"


def load_lab():
    spec = importlib.util.spec_from_file_location("lab_under_test", LAB)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_no_mode_returns_empty():
    lab = load_lab()
    assert lab.weights_hashes(["a.pt"], None) == {"weights_sha256": None, "outputs_sha256": {}}
    assert lab.weights_hashes(["a.pt"], "none") == {"weights_sha256": None, "outputs_sha256": {}}


def test_explicit_hex_is_kept():
    lab = load_lab()
    hex64 = "a" * 64
    out = lab.weights_hashes([], hex64)
    assert out["weights_sha256"] == hex64


def test_bad_hex_is_rejected():
    lab = load_lab()
    try:
        lab.weights_hashes([], "не-хеш")
    except SystemExit as exc:
        assert "64" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("ожидался SystemExit на неверный хеш")


def test_auto_hashes_existing_pt_only(tmp_path):
    lab = load_lab()
    weights = tmp_path / "nca_final.pt"
    weights.write_bytes(b"x" * 1024)
    other = tmp_path / "summary.json"
    other.write_text("{}", encoding="utf-8")
    missing = tmp_path / "nope.pt"
    out = lab.weights_hashes([str(weights), str(other), str(missing)], "auto")
    expected = hashlib.sha256(b"x" * 1024).hexdigest()
    assert out["weights_sha256"] == expected
    assert out["outputs_sha256"] == {str(weights): expected}


def test_run_command_accepts_new_flags():
    """Флаги должны быть в CLI, иначе их нельзя передать в прогон."""
    proc = subprocess.run(
        [sys.executable, str(LAB), "run", "--help"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert "--regime" in proc.stdout
    assert "--weights-sha256" in proc.stdout
