"""Тесты гейта дизайна: он обязан ловить наш главный провал и не мешать нормальным данным.

Основание: 31.10 пять невалидных постановок подряд, ~110 прогонов впустую. Три из них были невалидны потому, что
манипуляция не доходила до динамики (X46: плечи идентичны), одна — потому что отклик не писался (X49: splits = None).
Эти тесты фиксируют, что гейт такие случаи ловит.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_design.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _write(tmp_path: Path, name: str, components: list[int], splits=None) -> Path:
    series = []
    for i, c in enumerate(components):
        row = {"components": c}
        if splits is not None:
            row["splits"] = splits[i]
        series.append(row)
    p = tmp_path / name
    p.write_text(json.dumps({"series": series}), encoding="utf-8")
    return p


def test_identical_arms_fail(tmp_path: Path) -> None:
    """X46: одинаковые плечи — гейт обязан упасть."""
    a = _write(tmp_path, "a.json", [1, 2, 3, 4, 5, 6])
    b = _write(tmp_path, "b.json", [1, 2, 3, 4, 5, 6])
    r = _run("--pair", str(a), str(b), "--key", "series[].components", "--ci")
    assert r.returncode == 1
    assert "идентична" in r.stdout


def test_different_arms_pass(tmp_path: Path) -> None:
    a = _write(tmp_path, "a.json", [1, 2, 3, 4, 5, 6])
    b = _write(tmp_path, "b.json", [1, 2, 3, 9, 5, 6])
    r = _run("--pair", str(a), str(b), "--key", "series[].components", "--ci")
    assert r.returncode == 0
    assert "связность есть" in r.stdout


def test_missing_readout_fails(tmp_path: Path) -> None:
    """X49: поля отклика нет — гейт обязан упасть."""
    a = _write(tmp_path, "a.json", [1, 2, 3, 4, 5, 6])
    r = _run("--readout", str(a), "--key", "series[].splits", "--ci")
    assert r.returncode == 1
    assert "нет в артефакте" in r.stdout


def test_constant_readout_fails(tmp_path: Path) -> None:
    a = _write(tmp_path, "a.json", [0] * 8, splits=[0] * 8)
    r = _run("--readout", str(a), "--key", "series[].splits", "--ci")
    assert r.returncode == 1
    assert "постоянно" in r.stdout


def test_varying_readout_passes(tmp_path: Path) -> None:
    a = _write(tmp_path, "a.json", [1, 2, 3, 4, 5, 6], splits=[0, 1, 0, 2, 3, 1])
    r = _run("--readout", str(a), "--key", "series[].splits", "--ci")
    assert r.returncode == 0
    assert "отклик есть" in r.stdout


def test_prereg_structure_requires_five_sections(tmp_path: Path) -> None:
    p = tmp_path / "prereg.md"
    p.write_text("# Только начало\n\nничего нет\n", encoding="utf-8")
    r = _run("--prereg", str(p), "--structure", "--ci")
    assert r.returncode == 1
    assert "нет раздела" in r.stdout


def test_prereg_full_requires_ticks(tmp_path: Path) -> None:
    p = tmp_path / "prereg.md"
    p.write_text(
        "\n".join([
            "## 1. Manipulation is connected — REQUIRED",
            "## 2. Positive control fires — REQUIRED",
            "## 3. Readout exists and varies — REQUIRED",
            "## 4. Sensitivity arithmetic — REQUIRED",
            "## 5. Refusal rule — REQUIRED",
        ]),
        encoding="utf-8",
    )
    structure = _run("--prereg", str(p), "--structure", "--ci")
    assert structure.returncode == 0, structure.stdout
    full = _run("--prereg", str(p), "--ci")
    assert full.returncode == 1
    assert "не отмечен пункт" in full.stdout
