"""test_journal_import_dedup.py — один прогон = один манифест, даже если имена разные.

Ловушка, которую этот тест держит: `lab.py run --experiment X` пишет манифест
обёртки, а скрипт пишет в журнал своё имя (`e02c_census.py` выводит его из имени
сводки). Если имена расходятся, старый `import_journal` не узнавал «свой» прогон
и каждый запуск импорта плодил второй манифест `journal-reconstructed`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_PY = ROOT / "scripts" / "lab.py"


def load_lab():
    spec = importlib.util.spec_from_file_location("lab_module_dedup", LAB_PY)
    assert spec and spec.loader, f"не удалось загрузить {LAB_PY}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def journal_row(event: str, **fields) -> dict:
    row = {"ts": fields.pop("ts"), "event": event, "level": "info"}
    row.update(fields)
    return row


def test_reconstructed_manifest_is_skipped_when_wrapper_used_other_name(tmp_path, monkeypatch):
    lab = load_lab()
    runs = tmp_path / "runs"
    runs.mkdir()
    journal = tmp_path / "journal.jsonl"
    rows = [
        journal_row(
            "start",
            ts="2026-10-22T01:14:01.000000+00:00",
            experiment="E02c_census_e02c_seed42repro_frozen",
            out="experiments/E02c_replication/census_x.json",
            emits_run_finish=True,
        ),
        journal_row(
            "finish",
            ts="2026-10-22T01:33:11.000000+00:00",
            experiment="E02c_census_e02c_seed42repro_frozen",
            stop_reason="finished",
            n_runs=192,
        ),
    ]
    journal.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    # Манифест обёртки: другое имя эксперимента, но тот же скрипт и то же окно.
    write_json(
        runs / "20261022T011352Z-E02c_census_seed42repro_frozen.json",
        {
            "schema_version": 1,
            "run_id": "20261022T011352Z-E02c_census_seed42repro_frozen",
            "experiment": "E02c_census_seed42repro_frozen",
            "status": "finished",
            "provenance": "runner",
            "started_at": "2026-10-22T01:13:52Z",
            "finished_at": "2026-10-22T01:33:11Z",
            "command": ["python.exe", "run_exploratory.py", "--script", "e02c_census.py"],
            "outputs": {"declared": [], "log": "morphogenesis/logs/x.log"},
        },
    )

    monkeypatch.setattr(lab, "RUNS", runs)
    monkeypatch.setattr(lab, "JOURNAL", journal)
    result = lab.import_journal()

    assert result["written"] == 0, result
    assert result["skipped"] == 1, result
    manifests = sorted(p.name for p in runs.glob("*.json"))
    assert manifests == ["20261022T011352Z-E02c_census_seed42repro_frozen.json"]


def test_unrelated_run_is_still_reconstructed(tmp_path, monkeypatch):
    """Единственная защита — совпадение скрипта и окна; чужие прогоны не склеиваются."""
    lab = load_lab()
    runs = tmp_path / "runs"
    runs.mkdir()
    journal = tmp_path / "journal.jsonl"
    rows = [
        journal_row(
            "start",
            ts="2026-10-22T03:00:00.000000+00:00",
            experiment="E02b_channel_memory",
            runner="e02b_channel_memory.py",
            emits_run_finish=True,
        ),
        journal_row(
            "finish",
            ts="2026-10-22T03:05:00.000000+00:00",
            experiment="E02b_channel_memory",
            stop_reason="finished",
        ),
    ]
    journal.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    write_json(
        runs / "20261021T184756Z-E02c_R-9_s2000_seed42.json",
        {
            "schema_version": 1,
            "run_id": "20261021T184756Z-E02c_R-9_s2000_seed42",
            "experiment": "E02c_R-9_s2000_seed42",
            "status": "finished",
            "provenance": "runner",
            "started_at": "2026-10-21T18:47:56Z",
            "command": ["python.exe", "e02c_replication.py"],
            "outputs": {"declared": [], "log": "morphogenesis/logs/y.log"},
        },
    )

    monkeypatch.setattr(lab, "RUNS", runs)
    monkeypatch.setattr(lab, "JOURNAL", journal)
    result = lab.import_journal()

    assert result["written"] == 1, result
    assert any("E02b_channel_memory" in p.name for p in runs.glob("*.json"))


def test_runner_in_a_different_window_does_not_swallow_the_run(tmp_path, monkeypatch):
    lab = load_lab()
    runs = tmp_path / "runs"
    runs.mkdir()
    journal = tmp_path / "journal.jsonl"
    rows = [
        journal_row(
            "start",
            ts="2026-10-22T03:00:00.000000+00:00",
            experiment="E02b_channel_memory",
            emits_run_finish=True,
        ),
        journal_row(
            "finish",
            ts="2026-10-22T03:05:00.000000+00:00",
            experiment="E02b_channel_memory",
            stop_reason="finished",
        ),
    ]
    journal.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    write_json(
        runs / "20261021T184756Z-E02c_R-9_s2000_seed42.json",
        {
            "schema_version": 1,
            "run_id": "20261021T184756Z-E02c_R-9_s2000_seed42",
            "experiment": "E02c_R-9_s2000_seed42",
            "status": "finished",
            "provenance": "runner",
            "started_at": "2026-10-21T18:47:56Z",
            "finished_at": "2026-10-21T19:34:00Z",
            "command": ["python.exe", "e02c_replication.py"],
            "outputs": {"declared": [], "log": "morphogenesis/logs/y.log"},
        },
    )

    monkeypatch.setattr(lab, "RUNS", runs)
    monkeypatch.setattr(lab, "JOURNAL", journal)
    result = lab.import_journal()
    assert result["written"] == 1, result
