"""Тесты линтера матрицы утверждений: проверяем саму проверку.

Зачем: линтер — это гейт, на который опирается рукопись (тип основания, ссылки на артефакты).
Если он молча пропускает нарушение, все «подтверждено» снова становятся одинаковыми.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

claims_lint = importlib.import_module("claims_lint")

HEADER = "| Утверждение | Статус | Основание | Допущения | Что остаётся обосновать | Доказательство | Раздел | Допустимая формулировка |\n"
SEP = "| --- | --- | --- | --- | --- | --- | --- | --- |\n"


def _run(tmp_path, rows: str, monkeypatch) -> int:
    claims = tmp_path / "CLAIMS.md"
    claims.write_text("# CLAIMS\n\n" + HEADER + SEP + rows, encoding="utf-8")
    elim = tmp_path / "eliminations.md"
    elim.write_text("# eliminations\n", encoding="utf-8")
    monkeypatch.setattr(claims_lint, "CLAIMS", claims)
    monkeypatch.setattr(claims_lint, "ELIMINATIONS", elim)
    return claims_lint.main()


def _row(claim, status, kind, assume, evidence, allowed="в пределах указанных сидов и параметров"):
    return f"| {claim} | {status} | {kind} | {assume} | — | {evidence} | v2 §4h | «{allowed}» |\n"


def test_valid_new_row_passes(tmp_path, monkeypatch):
    rows = _row("Утверждение 2026-10-25", "подтверждено", "наблюдение", "один прогон",
                "раздел 10ak")
    assert _run(tmp_path, rows, monkeypatch) == 0


def test_new_row_without_assumptions_fails(tmp_path, monkeypatch):
    rows = _row("Утверждение 2026-10-25", "подтверждено", "статистика", "—", "aggregate.json")
    assert _run(tmp_path, rows, monkeypatch) == 1


def test_statistics_without_existing_artifact_fails_for_new_row(tmp_path, monkeypatch):
    rows = _row("Утверждение 2026-10-25", "подтверждено", "статистика", "10 сидов",
                "нет_такого_файла.json")
    assert _run(tmp_path, rows, monkeypatch) == 1


def test_statistics_without_path_is_warning_for_legacy_row(tmp_path, monkeypatch):
    rows = _row("Старое утверждение", "подтверждено", "статистика", "—", "прогоны 23.10")
    assert _run(tmp_path, rows, monkeypatch) == 0


def test_unknown_kind_fails(tmp_path, monkeypatch):
    rows = _row("Утверждение", "подтверждено", "магия", "—", "x.json")
    assert _run(tmp_path, rows, monkeypatch) == 1


def test_proof_without_formal_link_fails(tmp_path, monkeypatch):
    rows = _row("Утверждение", "подтверждено", "доказательство", "модель", "текст без ссылки")
    assert _run(tmp_path, rows, monkeypatch) == 1


def test_bad_header_fails(tmp_path, monkeypatch):
    claims = tmp_path / "CLAIMS.md"
    claims.write_text("| Утверждение | Статус |\n| --- | --- |\n", encoding="utf-8")
    monkeypatch.setattr(claims_lint, "CLAIMS", claims)
    monkeypatch.setattr(claims_lint, "ELIMINATIONS", tmp_path / "e.md")
    assert claims_lint.main() == 1
