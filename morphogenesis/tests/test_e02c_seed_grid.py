"""test_e02c_seed_grid.py — сборка 2×2-сетки «init × data» из сводок.

Скрипт `scripts/e02c_seed_grid.py` — единственное место, где клетки H-E02C-6
складываются в один артефакт. Он не делает измерений: только сводки переписей
плюс пять якорных сидов из закрытых отчётов. Поэтому тест проверяет именно
агрегацию:

- измеренная клетка берётся из сводки, доминирующий класс — самый частый в
  `frozen_class_counts` (а не первый по порядку);
- якоря (42/42, 101/101, 142/142, 242/242, 342/342) на месте с посчитанной
  долей `struct_2`;
- сетка адресуется ключами `init<A>_data<B>`, а `n_measured` не считает якоря;
- сводка без `stats` — явная ошибка, а не пустая клетка.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GRID_PY = ROOT / "scripts" / "e02c_seed_grid.py"


def load_module():
    spec = importlib.util.spec_from_file_location("e02c_seed_grid_under_test", GRID_PY)
    assert spec and spec.loader, f"не удалось загрузить {GRID_PY}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_summary(exp: Path, init: int, data: int, counts: dict, family: str | None = None):
    family = family or f"E02c_seeddec_init{init}_data{data}"
    n = sum(counts.values())
    stat = {
        "family": family,
        "n": n,
        "struct_2": counts.get("struct_2", 0),
        "struct_2_fraction": round(counts.get("struct_2", 0) / n, 4),
        "struct_2_stable": 0,
        "struct_2_stable_fraction": 0.0,
        "struct_2_stable_frozen": 0,
        "struct_2_stable_frozen_fraction": 0.0,
        "frozen_class_counts": counts,
        "ward_class_counts": {},
    }
    payload = {"stats": {family: stat}, "finished_at": "2026-10-22T07:00:00Z"}
    path = exp / f"summary_e02c_seeddec_init{init}_data{data}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.fixture()
def grid(tmp_path, monkeypatch):
    module = load_module()
    exp = tmp_path / "E02c_replication"
    exp.mkdir()
    monkeypatch.setattr(module, "EXP", exp)
    monkeypatch.setattr(module, "OUT", exp / "seed_grid.json")
    return module, exp


def test_grid_assembles_cells_and_anchors(grid, capsys):
    module, exp = grid
    write_summary(exp, 42, 202, {"uniform_dark": 59, "struct_2": 5})
    write_summary(exp, 101, 303, {"struct_1": 64})

    assert module.main() == 0
    payload = json.loads((exp / "seed_grid.json").read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["n_measured"] == 2
    assert payload["n_anchor"] == 5
    assert payload["inits"] == [42, 101, 142, 242, 342]
    assert payload["datas"] == [42, 101, 142, 202, 242, 303, 342]

    cell = payload["cells"]["init42_data202"]
    assert cell["kind"] == "measured"
    assert cell["dominant_class"] == "uniform_dark", "доминирует самый частый, а не первый ключ"
    assert cell["struct_2"] == 5 and cell["n"] == 64
    assert cell["source"] == "summary_e02c_seeddec_init42_data202.json"

    anchor = payload["cells"]["init42_data42"]
    assert anchor["kind"] == "anchor"
    assert anchor["dominant_class"] == "struct_2"
    assert anchor["struct_2_fraction"] == 1.0
    assert "2026-10-20-e02b-results.md" in anchor["source"]

    other = payload["cells"]["init101_data303"]
    assert other["dominant_class"] == "struct_1" and other["struct_2"] == 0

    # Пустых клеток в сетке нет: попадают только измеренные и якорные.
    assert set(payload["cells"]) >= {"init42_data42", "init101_data101", "init101_data303"}


def test_summary_without_stats_fails_loudly(grid):
    module, exp = grid
    (exp / "summary_e02c_seeddec_init42_data202.json").write_text(
        json.dumps({"stats": {}}), encoding="utf-8"
    )
    with pytest.raises(SystemExit):
        module.main()


def test_unrelated_files_are_ignored(grid):
    module, exp = grid
    write_summary(exp, 42, 202, {"struct_2": 64})
    (exp / "summary_e02c.json").write_text("{}", encoding="utf-8")
    (exp / "summary_colab_seed42.json").write_text("{}", encoding="utf-8")
    assert module.main() == 0
    payload = json.loads((exp / "seed_grid.json").read_text(encoding="utf-8"))
    assert payload["n_measured"] == 1
