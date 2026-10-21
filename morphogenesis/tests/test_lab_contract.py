"""Контракт машинного контура lab/: реестр, дескриптор, журнал, README, рукопись.

Эти тесты не запускают обучение и не читают веса: они проверяют, что агент,
пришедший в репозиторий, получает согласованные метаданные, что журнал в README
и карта рукописи не расходятся с реестром, и что он не наступит на отслеживаемые
артефакты.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "lab"
REGISTRY = LAB / "registry.json"
DESCRIPTOR = LAB / "experiments" / "E02b_morphospace.json"
LAB_PY = ROOT / "scripts" / "lab.py"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_lab_module():
    spec = importlib.util.spec_from_file_location("lab_contract_module", LAB_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_lab(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(LAB_PY), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
    )


def git_tracked() -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.skip("git недоступен")
    return [part for part in proc.stdout.decode("utf-8", "replace").split("\0") if part]


def test_lab_validate_ci_passes() -> None:
    proc = run_lab("validate", "--ci")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ОШИБКИ" not in proc.stdout


def test_registry_and_descriptor_are_consistent() -> None:
    registry = load_json(REGISTRY)
    descriptor = load_json(DESCRIPTOR)

    schema_files = sorted((LAB / "schemas").glob("*.json"))
    assert schema_files, "нет JSON-схем lab/"
    for path in schema_files:
        schema = load_json(path)
        assert schema["$schema"].startswith("https://json-schema.org/")

    ids = [item["id"] for item in registry["experiments"]]
    assert len(ids) == len(set(ids))
    for item in registry["experiments"]:
        assert item["status"] in {"planned", "running", "closed", "blocked", "not_run"}
        assert item["kind"] in {"experiment", "diagnostic", "gate", "series"}

    protocol = ROOT / descriptor["protocol"]
    assert protocol.is_file()
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    assert digest == descriptor["protocol_sha256"], "протокол E02b изменён после фиксации"

    requirements = descriptor["checkpoint_requirements"]
    families = [item["family"] for item in requirements]
    assert len(families) == len(set(families)) == 12
    assert {item["file"] for item in requirements} == {"nca_final.pt"}
    assert descriptor["checkpoint_policy"]["canonical_kind"] == "final"


def test_scientific_loop_is_declared_and_enforced() -> None:
    """Научный цикл (AGENTS.md §3a) объявлен и проверяем машинно.

    Восемь стадий, очередь гипотез лаборатории и правило «статья закрывается
    следующими гипотезами» — всё это должно быть в реестре, иначе validate
    падает. Тест фиксирует контракт, чтобы правило не размылось.
    """
    registry = load_json(REGISTRY)
    program = registry["program"]

    stages = [item["stage"] for item in program["loop"]]
    assert stages == [
        "sources",
        "review",
        "hypothesis",
        "test",
        "writeup",
        "readme",
        "manuscript",
        "sources_next",
    ]
    for item in program["loop"]:
        assert item["title"] and item["where"] and item["output"]

    hypotheses = program["next_hypotheses"]
    assert hypotheses, "очередь следующих гипотез пуста"
    ids = [item["id"] for item in hypotheses]
    assert len(ids) == len(set(ids)), "повторяющиеся id гипотез"
    for item in hypotheses:
        assert item["statement"].strip(), f"{item['id']}: пустое утверждение"
        assert item["test"].strip(), f"{item['id']}: нет критерия проверки"
        assert item["status"] in {"planned", "running", "confirmed", "rejected", "blocked"}

    for item in registry["experiments"]:
        if item.get("article"):
            assert item.get("next_hypotheses"), (
                f"{item['id']}: есть статья, но не записаны следующие гипотезы"
            )


def test_readme_ledger_matches_registry() -> None:
    """Журнал экспериментов в README.md покрывает registry (AGENTS.md §6a).

    README — витрина и карта: одна строка на experiment_id, статус по-русски
    совпадает с машинным статусом. Проверку делает сам lab.py, тест лишь
    требует, чтобы она проходила на реальном README.
    """
    lab = load_lab_module()
    registry = load_json(REGISTRY)
    errors, count = lab.check_readme_ledger(registry)
    assert not errors, "журнал README расходится с registry:\n" + "\n".join(errors)
    experiments = registry["experiments"]
    assert count == len(experiments), (
        f"в журнале README {count} экспериментов, в registry {len(experiments)}"
    )


def test_manuscript_map_covers_closed_experiments() -> None:
    """Карта рукописи покрывает закрытые эксперименты со статьёй (AGENTS.md §6a).

    Закрытый результат без места в manuscript/ — незакрытый результат; id в
    карте обязаны существовать в registry, а статус вклада быть одним из
    внесено / частично / ожидает.
    """
    lab = load_lab_module()
    registry = load_json(REGISTRY)
    errors, count = lab.check_manuscript_map(registry)
    assert not errors, "карта рукописи расходится с registry:\n" + "\n".join(errors)

    required = {
        item["id"]
        for item in registry["experiments"]
        if item.get("status") == "closed" and item.get("article")
    }
    assert required == {"E02_pattern", "WP4_R9", "E02b_morphospace"}
    assert count >= len(required), f"в карте рукописи {count} записей, нужно минимум {len(required)}"

    map_text = (ROOT / "manuscript" / "README.md").read_text(encoding="utf-8")
    map_block = map_text.split("<!-- map:start -->")[1].split("<!-- map:end -->")[0]
    for exp_id in sorted(required):
        assert exp_id in map_block, f"{exp_id} не попал в карту рукописи"


def test_journal_finish_status_mapping() -> None:
    lab = load_lab_module()
    assert lab._status_from_finish({"event": "finish", "stop_reason": "max_steps"}) == "finished"
    assert lab._status_from_finish({"event": "finish", "stop_reason": "collapse_fuse"}) == "finished"
    assert lab._status_from_finish({"event": "finish", "stop_reason": "aborted"}) == "aborted"
    assert lab._status_from_finish({"event": "error", "stop_reason": "nan"}) == "failed"
    assert lab._status_from_finish({"event": "finish", "stop_reason": "oom"}) == "failed"


def test_cli_run_dispatches_without_touching_files(monkeypatch) -> None:
    lab = load_lab_module()
    captured = {}

    def fake_run(args):
        captured["experiment"] = args.experiment
        captured["command"] = args.command
        return 37

    monkeypatch.setattr(lab, "run_command", fake_run)
    code = lab.main(["run", "--experiment", "TEST_ONLY", "--", "echo", "ok"])
    assert code == 37
    assert captured["experiment"] == "TEST_ONLY"
    # argparse REMAINDER сохраняет разделитель; run_command снимает его первым.
    assert captured["command"] == ["--", "echo", "ok"]


def test_git_does_not_track_runtime_artifacts() -> None:
    tracked = git_tracked()
    bad_pyc = [path for path in tracked if path.endswith((".pyc", ".pyo"))]
    bad_weights = [path for path in tracked if path.endswith((".pt", ".pth", ".ckpt"))]
    bad_logs = [
        path
        for path in tracked
        if path.startswith("morphogenesis/logs/") and path != "morphogenesis/logs/journal.jsonl"
    ]
    assert not bad_pyc, f"в git попали .pyc: {bad_pyc[:5]}"
    assert not bad_weights, f"в git попали веса: {bad_weights[:5]}"
    assert not bad_logs, f"в git попали runtime-логи: {bad_logs[:5]}"
