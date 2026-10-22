"""test_analyze_grid_failures.py — какие старты выпадают в клетках сетки.

Скрипт `scripts/analyze_grid_failures.py` отвечает на узкий вопрос: остаточные
1–4 промаха `struct_2` в клетках (42,202) и (42,303) — это одни и те же шумовые
старты (свойство стартов) или разные (свойство модели)? Ответ «общих нет»
попадает в §4.13, поэтому проверяется тестом, а не глазами.

Тест на фальшивой переписи: доминирующий класс считается голосованием, выпавшие
старты перечислены поимённо, пересечение между клетками считается отдельно.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "analyze_grid_failures.py"


def load_module():
    spec = importlib.util.spec_from_file_location("analyze_grid_failures_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def fake_census(path: Path) -> Path:
    runs = []
    for seed in range(10):
        runs.append({"seed": seed, "family": "E02c_seeddec_init42_data202",
                     "frozen_class": "struct_2" if seed != 3 else "struct_1"})
        runs.append({"seed": seed, "family": "E02c_seeddec_init42_data303",
                     "frozen_class": "struct_2" if seed not in (3, 7) else "struct_1"})
        runs.append({"seed": seed, "family": "E02c_seeddec_init101_data202",
                     "frozen_class": "death" if seed < 6 else "struct_1"})
        runs.append({"seed": seed, "family": "E02c_seeddec_init101_data303",
                     "frozen_class": "uniform_dark"})
    path.write_bytes(json.dumps({"runs": runs}).encode("utf-8"))
    return path


def test_failures_and_overlap(tmp_path, monkeypatch, capsys):
    module = load_module()
    census = fake_census(tmp_path / "census.json")
    out = tmp_path / "failures.json"
    monkeypatch.setattr(module, "CENSUS", census)
    monkeypatch.setattr(module, "OUT", out)

    assert module.main() == 0
    result = json.loads(out.read_text(encoding="utf-8"))

    cell = result["cells"]["init42_data202"]
    assert cell["dominant_class"] == "struct_2"
    assert cell["dominant_count"] == 9
    assert cell["failed_starts"] == [3]

    # (42,202) выпал только старт 3, (42,303) — 3 и 7: общих 1.
    overlap = result["failed_start_overlap"]["init42_data202_vs_data303"]
    assert overlap["intersection"] == [3]
    assert overlap["n_intersection"] == 1

    # (101,202) доминирует death (6 против 4), выпавшие — 6..9.
    cell101 = result["cells"]["init101_data202"]
    assert cell101["dominant_class"] == "death"
    assert cell101["failed_starts"] == [6, 7, 8, 9]

    # Полностью однородная клетка: выпавших нет.
    assert result["cells"]["init101_data303"]["failed_starts"] == []
    assert result["cells"]["init101_data303"]["dominant_count"] == 10

    out_text = capsys.readouterr().out
    assert "общих выпавших стартов 1" in out_text
