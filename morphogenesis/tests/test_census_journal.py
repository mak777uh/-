"""test_census_journal.py — перепись обязана оставлять пару start/finish.

Почему это тест, а не пожелание: в 2026-10-21 шесть exploratory-прогонов и
перепись E02c закрылись с манифестом и stdout, но без пары start/finish в
каноническом журнале (`lab/state.json` → `blockers`). Дописать журнал задним
числом нельзя (AGENTS §2), поэтому чинится **процесс**: `e02c_census.py` сам
пишет start и finish (или error), а тест держит это поведение.

Здесь не гоняется настоящая перепись: `e02b.run_census` и `_preflight`
подменены, поэтому тест не трогает GPU, чекпоинты и каноническую перепись.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import config  # noqa: E402
import e02c_census  # noqa: E402


def load_journal(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fake_spec(family: str, arm: str = "R-9") -> SimpleNamespace:
    return SimpleNamespace(family=family, arm=arm, path=None, seed=42, steps_trained=2000)


@pytest.fixture()
def patched(monkeypatch, tmp_path):
    """Изолировать перепись: свой журнал, свои артефакты, без GPU."""
    monkeypatch.setattr(config, "LOG_DIR", str(tmp_path / "logs"))
    (tmp_path / "logs").mkdir(parents=True, exist_ok=True)

    spec = fake_spec("E02c_R-9_s2000_seed1")
    monkeypatch.setattr(e02c_census, "discover_specs", lambda families=None: [spec])
    monkeypatch.setattr(e02c_census.e02b, "_preflight", lambda *a, **kw: None)
    monkeypatch.setattr(
        e02c_census.e02b,
        "run_census",
        lambda specs, seeds, steps, every, device, pilot=False, **_kwargs: (
            {"runs": [], "steps": steps, "device": str(device)},
            {},
        ),
    )
    monkeypatch.setattr(e02c_census.e02b, "_device_from_arg", lambda arg: "cpu")
    monkeypatch.setattr(e02c_census, "sha256_file", lambda path: "0" * 64)
    return tmp_path


def test_main_writes_start_and_finish(patched):
    out = patched / "census.json"
    summary = patched / "summary_e02c_unit.json"
    code = e02c_census.main(
        ["--seeds", "0-1", "--out", str(out), "--summary-out", str(summary)]
    )
    assert code == 0
    assert out.is_file() and summary.is_file()

    events = load_journal(Path(config.LOG_DIR) / "journal.jsonl")
    kinds = [event["event"] for event in events]
    assert kinds == ["start", "finish"], kinds
    assert {event["experiment"] for event in events} == {"E02c_census_e02c_unit"}
    start, finish = events
    assert start["seeds"] == 2 and start["steps"] == 2000
    assert start["families"] == ["E02c_R-9_s2000_seed1"]
    assert start["emits_run_finish"] is True
    assert finish["stop_reason"] == "finished"
    assert finish["n_runs"] == 0
    assert finish["census"] == str(out)


def test_journal_label_derives_variant_from_summary_name():
    args = SimpleNamespace(summary_out="experiments/E02c_replication/summary_e02c_seed42repro.json")
    assert e02c_census.journal_label(args) == "E02c_census_e02c_seed42repro"

    default = SimpleNamespace(summary_out="experiments/E02c_replication/summary_e02c.json")
    assert e02c_census.journal_label(default) == "E02c_census_e02c"

    odd = SimpleNamespace(summary_out="census_summary.json")
    assert e02c_census.journal_label(odd) == "E02c_census_census_summary"


def test_failure_writes_error_instead_of_silent_start(patched, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("cuda oom")

    monkeypatch.setattr(e02c_census.e02b, "run_census", boom)
    with pytest.raises(RuntimeError):
        e02c_census.main(
            [
                "--seeds",
                "0-1",
                "--out",
                str(patched / "census.json"),
                "--summary-out",
                str(patched / "summary_e02c_boom.json"),
            ]
        )
    events = load_journal(Path(config.LOG_DIR) / "journal.jsonl")
    kinds = [event["event"] for event in events]
    assert kinds == ["start", "error"], kinds
    assert events[1]["error_type"] == "RuntimeError"
    assert "cuda oom" in events[1]["error"]
