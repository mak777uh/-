"""test_e02c_seed_grid.py — сборка 2×2-сетки «init × data» и критерий H-E02C-6.

Скрипт `scripts/e02c_seed_grid.py` — единственное место, где клетки второй волны
складываются в один артефакт и где применяется замороженный критерий
(`reports/2026-10-22-e02c-seed-grid-plan.md`). Он не делает измерений: только
сводки переписей плюс пять якорных сидов из закрытых отчётов.

Что проверяется:

- клетка опознаётся **по имени семейства внутри сводки**, поэтому первая волна
  (`summary_e02c_seeddec_A.json` / `_B.json`) не теряется;
- доминирующий класс — самый частый в `frozen_class_counts`, а не первый ключ;
- пять якорей на месте, ключи ячеек `init<A>_data<B>`, `n_measured` без якорей;
- критерий: (1) все клетки init=101 дают `struct_1` >= 52/64, (2) среди клеток
  init=42 есть >= 2 доминирующих класса и `struct_2` нигде не >= 52/64;
- неполная перепись (n != 64) в критерий не входит и помечается;
- сводка без `stats` или с чужим именем семейства падает явно.
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


def write_summary(exp: Path, init: int, data: int, counts: dict, *, n: int | None = None,
                  filename: str | None = None, family: str | None = None):
    family = family or f"E02c_seeddec_init{init}_data{data}"
    n = sum(counts.values()) if n is None else n
    stat = {
        "family": family,
        "n": n,
        "struct_2": counts.get("struct_2", 0),
        "struct_2_fraction": round(counts.get("struct_2", 0) / n, 4) if n else 0.0,
        "struct_2_stable": 0,
        "struct_2_stable_fraction": 0.0,
        "struct_2_stable_frozen": 0,
        "struct_2_stable_frozen_fraction": 0.0,
        "frozen_class_counts": counts,
        "ward_class_counts": {},
    }
    payload = {"stats": {family: stat}, "finished_at": "2026-10-22T07:00:00Z"}
    path = exp / (filename or f"summary_e02c_seeddec_init{init}_data{data}.json")
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


def read_grid(exp: Path) -> dict:
    return json.loads((exp / "seed_grid.json").read_text(encoding="utf-8"))


def test_grid_assembles_cells_and_anchors(grid):
    module, exp = grid
    write_summary(exp, 42, 202, {"uniform_dark": 59, "struct_2": 5})
    write_summary(exp, 101, 303, {"struct_1": 64})

    assert module.main() == 0
    payload = read_grid(exp)

    assert payload["schema_version"] == 1
    assert payload["n_measured"] == 2
    assert payload["n_anchor"] == 5
    assert payload["inits"] == [42, 101, 142, 242, 342]
    assert payload["datas"] == [42, 101, 142, 202, 242, 303, 342]

    cell = payload["cells"]["init42_data202"]
    assert cell["kind"] == "measured"
    assert cell["dominant_class"] == "uniform_dark", "доминирует самый частый, а не первый ключ"
    assert cell["struct_2"] == 5 and cell["n"] == 64
    assert cell["complete"] is True
    assert cell["source"] == "summary_e02c_seeddec_init42_data202.json"

    anchor = payload["cells"]["init42_data42"]
    assert anchor["kind"] == "anchor"
    assert anchor["dominant_class"] == "struct_2"
    assert anchor["struct_2_fraction"] == 1.0
    assert "2026-10-20-e02b-results.md" in anchor["source"]

    assert payload["cells"]["init101_data303"]["dominant_class"] == "struct_1"


def test_legacy_A_B_filenames_are_picked_up_by_family_name(grid):
    """Первая волна: имена файлов A/B, init/data — только внутри сводки."""
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")

    assert module.main() == 0
    payload = read_grid(exp)
    assert payload["n_measured"] == 2
    assert payload["cells"]["init42_data101"]["dominant_class"] == "uniform_dark"
    assert payload["cells"]["init101_data42"]["dominant_class"] == "struct_1"


def test_verdict_confirmed(grid):
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")
    write_summary(exp, 42, 202, {"struct_2": 20, "uniform_dark": 44})
    write_summary(exp, 42, 303, {"struct_1": 64})
    write_summary(exp, 101, 202, {"struct_1": 60, "uniform_dark": 4})
    write_summary(exp, 101, 303, {"struct_1": 64})

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "H-E02C-6_confirmed"
    assert verdict["cond1_struct1_fixed_at_init101"] is True
    assert verdict["cond2_init42_data_changes_class"] is True
    assert verdict["init42_dominant_classes"] == ["struct_1", "uniform_dark"]
    assert verdict["init42_struct2_at_or_above_threshold"] == []
    assert verdict["failed_conditions"] == []


def test_verdict_refuted_when_init101_is_not_struct1(grid):
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")
    write_summary(exp, 101, 202, {"struct_2": 64})
    write_summary(exp, 101, 303, {"struct_1": 64})
    write_summary(exp, 42, 202, {"uniform_dark": 64})
    write_summary(exp, 42, 303, {"struct_1": 64})

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "H-E02C-6_refuted"
    assert verdict["cond1_struct1_fixed_at_init101"] is False
    assert "cond1_init101_not_fixed_struct1" in verdict["failed_conditions"]
    assert any(not c["ok"] for c in verdict["cond1_cells"])


def test_verdict_refuted_when_init42_has_one_dominant_class(grid):
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")
    write_summary(exp, 42, 202, {"uniform_dark": 64})
    write_summary(exp, 42, 303, {"uniform_dark": 60, "struct_1": 4})
    write_summary(exp, 101, 202, {"struct_1": 64})
    write_summary(exp, 101, 303, {"struct_1": 64})

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "H-E02C-6_refuted"
    assert verdict["cond2_init42_data_changes_class"] is False
    assert verdict["init42_dominant_classes"] == ["uniform_dark"]


def test_verdict_refuted_when_struct2_reaches_threshold_at_init42(grid):
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")
    write_summary(exp, 42, 202, {"struct_2": 60, "uniform_dark": 4})
    write_summary(exp, 42, 303, {"struct_1": 64})
    write_summary(exp, 101, 202, {"struct_1": 64})
    write_summary(exp, 101, 303, {"struct_1": 64})

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "H-E02C-6_refuted"
    assert "cond2_init42_data_does_not_change_class" in verdict["failed_conditions"]
    assert verdict["struct2_substitute_candidates"] == ["init42_data202"]


def test_incomplete_census_is_excluded_and_recorded(grid):
    module, exp = grid
    write_summary(exp, 101, 202, {"struct_1": 64})
    # n = 32 при сумме счётчиков 32: перепись неполная
    write_summary(exp, 42, 202, {"uniform_dark": 32}, n=32)

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["incomplete_cells_excluded"] == ["summary_e02c_seeddec_init42_data202.json"]
    # Критерий описывает полный дизайн: на частичной сетке вердикта нет.
    assert verdict["verdict"] == "n/a_design_incomplete"
    assert "init42_data202" in verdict["missing_cells"]
    assert verdict["failed_conditions"] == []


def test_partial_grid_is_not_applicable_not_refuted(grid):
    """Две клетки первой волны: A (42/101) и B (101/42) — этого мало для вердикта."""
    module, exp = grid
    write_summary(exp, 42, 101, {"uniform_dark": 64}, filename="summary_e02c_seeddec_A.json")
    write_summary(exp, 101, 42, {"struct_1": 64}, filename="summary_e02c_seeddec_B.json")

    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "n/a_design_incomplete"
    assert set(verdict["missing_cells"]) == {
        "init42_data202",
        "init42_data303",
        "init101_data202",
        "init101_data303",
    }
    # Предварительные числа видны, но вердикт не выносится.
    assert verdict["cond1_struct1_fixed_at_init101"] is True
    assert verdict["cond2_init42_data_changes_class"] is False
    assert verdict["failed_conditions"] == []


def test_no_cells_yields_not_applicable(grid):
    module, exp = grid
    assert module.main() == 0
    verdict = read_grid(exp)["verdict"]
    assert verdict["verdict"] == "n/a_design_incomplete"
    assert len(verdict["missing_cells"]) == 6
    assert verdict["incomplete_cells_excluded"] == []


def test_combined_wave_summary_yields_all_cells(grid):
    """Одна волна на четыре клетки: в stats четыре семейства — берутся все."""
    module, exp = grid
    stats = {}
    for init, data, counts in (
        (42, 202, {"uniform_dark": 64}),
        (42, 303, {"struct_1": 64}),
        (101, 202, {"struct_1": 64}),
        (101, 303, {"uniform_dark": 64}),
    ):
        family = f"E02c_seeddec_init{init}_data{data}"
        stats[family] = {
            "family": family,
            "n": 64,
            "struct_2": 0,
            "struct_2_fraction": 0.0,
            "frozen_class_counts": counts,
        }
    (exp / "summary_e02c_seeddec_wave2.json").write_bytes(
        json.dumps({"stats": stats}).encode("utf-8")
    )

    assert module.main() == 0
    payload = read_grid(exp)
    assert payload["n_measured"] == 4
    for key in ("init42_data202", "init42_data303", "init101_data202", "init101_data303"):
        assert payload["cells"][key]["kind"] == "measured"
        assert payload["cells"][key]["source"] == "summary_e02c_seeddec_wave2.json"
    assert payload["cells"]["init42_data303"]["dominant_class"] == "struct_1"


def test_summary_without_stats_fails_loudly(grid):
    module, exp = grid
    (exp / "summary_e02c_seeddec_init42_data202.json").write_text(
        json.dumps({"stats": {}}), encoding="utf-8"
    )
    with pytest.raises(SystemExit):
        module.main()


def test_foreign_family_name_fails_loudly(grid):
    module, exp = grid
    write_summary(exp, 42, 202, {"struct_2": 64}, family="E02c_seed42repro")
    with pytest.raises(SystemExit):
        module.main()


def test_unrelated_files_are_ignored(grid):
    module, exp = grid
    write_summary(exp, 42, 202, {"struct_2": 64})
    (exp / "summary_e02c.json").write_text("{}", encoding="utf-8")
    (exp / "summary_colab_seed42.json").write_text("{}", encoding="utf-8")
    assert module.main() == 0
    assert read_grid(exp)["n_measured"] == 1
