"""test_run_seed_grid_censuses.py — драйвер переписей второй волны H-E02C-6.

Драйвер — то место, где цена ошибки измеряется в GPU-минутах: если он не узнает
уже посчитанную клетку, перепись пойдёт второй раз (~7-10 мин на клетку), а если
потеряет клетку из плана, вердикт H-E02C-6 не соберётся.

Проверяется:

- клетка считается готовой **по имени семейства внутри сводки**, поэтому первая
  волна (`summary_e02c_seeddec_A/_B.json`) не переписывается повторно;
- `ready` требует `nca_final.pt`; незавершённый чекпоинт попадает в `waiting` с
  причиной и не валит план;
- имена выходов совпадают с протоколом (`census_/summary_e02c_seeddec_init<A>_data<B>.json`);
- запуск идёт через `lab.py run` с `--`, то есть с замком, манифестом и журналом;
- `--dry-run` ничего не запускает, а `--only` с неизвестной клеткой падает явно.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "scripts" / "run_seed_grid_censuses.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_seed_grid_censuses_under_test", DRIVER)
    assert spec and spec.loader, f"не удалось загрузить {DRIVER}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_summary(dirpath: Path, family: str, filename: str) -> Path:
    payload = {
        "stats": {
            family: {
                "family": family,
                "n": 64,
                "struct_2": 0,
                "frozen_class_counts": {"struct_1": 64},
            }
        }
    }
    path = dirpath / filename
    path.write_bytes(json.dumps(payload).encode("utf-8"))
    return path


def touch_final(checkpoints: Path, family: str) -> Path:
    d = checkpoints / family
    d.mkdir(parents=True, exist_ok=True)
    final = d / "nca_final.pt"
    final.write_bytes(b"fake")
    return final


def test_legacy_summary_counts_as_complete(tmp_path):
    module = load_module()
    checkpoints, summaries = tmp_path / "ckpt", tmp_path / "exp"
    summaries.mkdir()
    touch_final(checkpoints, "E02c_seeddec_init42_data101")
    write_summary(summaries, "E02c_seeddec_init42_data101", "summary_e02c_seeddec_A.json")

    plan = module.build_plan([(42, 101)], checkpoints=checkpoints, summaries=summaries)
    assert [x["family"] for x in plan["complete"]] == ["E02c_seeddec_init42_data101"]
    assert plan["ready"] == []
    assert plan["waiting"] == []


def test_ready_needs_final_checkpoint(tmp_path):
    module = load_module()
    checkpoints, summaries = tmp_path / "ckpt", tmp_path / "exp"
    summaries.mkdir()
    touch_final(checkpoints, "E02c_seeddec_init42_data202")

    plan = module.build_plan([(42, 202)], checkpoints=checkpoints, summaries=summaries)
    assert [x["family"] for x in plan["ready"]] == ["E02c_seeddec_init42_data202"]
    assert plan["complete"] == []


def test_unfinished_and_absent_checkpoints_are_waiting(tmp_path):
    module = load_module()
    checkpoints, summaries = tmp_path / "ckpt", tmp_path / "exp"
    summaries.mkdir()
    unfinished = checkpoints / "E02c_seeddec_init101_data202"
    unfinished.mkdir(parents=True)
    (unfinished / "nca_best.pt").write_bytes(b"fake")

    plan = module.build_plan(
        [(101, 202), (101, 303)], checkpoints=checkpoints, summaries=summaries
    )
    reasons = {x["family"]: x["reason"] for x in plan["waiting"]}
    assert reasons["E02c_seeddec_init101_data202"].startswith("чекпоинт не завершён")
    assert reasons["E02c_seeddec_init101_data303"] == "чекпоинта нет"
    assert plan["ready"] == []


def test_census_command_uses_protocol_filenames(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "EXP", tmp_path)
    item = {"init": 42, "data": 202, "family": "E02c_seeddec_init42_data202"}
    cmd = module.census_command(item)
    assert cmd[1] == "e02c_census.py"
    assert cmd[cmd.index("--families") + 1] == "E02c_seeddec_init42_data202"
    assert cmd[cmd.index("--out") + 1].endswith("census_e02c_seeddec_init42_data202.json")
    assert cmd[cmd.index("--summary-out") + 1].endswith(
        "summary_e02c_seeddec_init42_data202.json"
    )
    # Контроль серии запускается по умолчанию: WP4 seed42 лежит локально, и
    # флаг --allow-missing-control здесь не нужен.
    assert "--allow-missing-control" not in cmd


def test_wrapped_command_uses_lab_run_and_separator(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "EXP", tmp_path)
    item = {"init": 101, "data": 42, "family": "E02c_seeddec_init101_data42"}
    cmd = module.wrapped_command(item, "lead")
    assert cmd[1].endswith("lab.py")
    assert cmd[2] == "run"
    assert cmd[cmd.index("--experiment") + 1] == "E02c_seeddec_init101_data42_census"
    assert cmd[cmd.index("--experiment-id") + 1] == "E02c"
    assert cmd[cmd.index("--arm") + 1] == "R-9"
    assert cmd[cmd.index("--seed") + 1] == "101"
    assert cmd[cmd.index("--steps") + 1] == "2000"
    assert cmd[cmd.index("--owner") + 1] == "lead"
    assert "--" in cmd
    assert cmd[cmd.index("--") + 1 :] == module.census_command(item)


def test_dry_run_does_not_execute_anything(monkeypatch, capsys):
    module = load_module()
    item = {"init": 42, "data": 202, "family": "E02c_seeddec_init42_data202"}
    # План подменяем: тест не должен зависеть от того, какие клетки уже посчитаны
    # в рабочем репозитории (после закрытия волны все шесть готовы).
    monkeypatch.setattr(
        module, "build_plan", lambda cells: {"ready": [item], "waiting": [], "complete": []}
    )
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("не должно запускать")),
    )
    assert module.main(["--dry-run", "--only", "init42_data202"]) == 0
    out = capsys.readouterr().out
    assert "DRY" in out and "E02c_seeddec_init42_data202" in out


def test_only_with_unknown_cell_fails(monkeypatch):
    module = load_module()
    with pytest.raises(SystemExit):
        module.main(["--dry-run", "--only", "init999_data999"])
