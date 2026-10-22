"""test_make_seed_grid_figure.py — Figure 4 строится из артефакта, а не из рук.

Рисунок §4.13 должен воспроизводиться одной командой из `seed_grid.json`: если
клетки нет в артефакте, скрипт обязан упасть с внятным сообщением, а не нарисовать
красивую пустоту. Тест держит обе стороны: рендер в tmp-файл и падение без сетки.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_seed_grid_figure.py"


def load_module():
    spec = importlib.util.spec_from_file_location("make_seed_grid_figure_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def grid_payload() -> dict:
    cells = {}
    for init in (42, 101):
        for data in (42, 101, 202, 303):
            dominant = "struct_2" if init == 42 and data != 101 else "uniform_dark"
            cells[f"init{init}_data{data}"] = {
                "init_seed": init,
                "data_seed": data,
                "kind": "anchor" if init == data else "measured",
                "n": 64,
                "struct_2": 64 if dominant == "struct_2" else 0,
                "dominant_class": dominant,
                "class_counts": {dominant: 64},
            }
    return {"cells": cells}


def test_figure_is_rendered_from_artifact(tmp_path, monkeypatch):
    module = load_module()
    grid = tmp_path / "seed_grid.json"
    grid.write_bytes(json.dumps(grid_payload()).encode("utf-8"))
    out = tmp_path / "fig.png"
    monkeypatch.setattr(module, "GRID", grid)
    monkeypatch.setattr(module, "OUT", out)

    assert module.main() == 0
    assert out.is_file() and out.stat().st_size > 10_000


def test_missing_grid_fails_loudly(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "GRID", tmp_path / "nope.json")
    monkeypatch.setattr(module, "OUT", tmp_path / "fig.png")
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert "сначала соберите сетку" in str(exc.value)


def test_empty_cell_is_drawn_as_dash_not_crash(tmp_path, monkeypatch):
    """Если клетки нет в артефакте, рисунок остаётся, но клетка пустая."""
    module = load_module()
    payload = grid_payload()
    del payload["cells"]["init42_data202"]
    grid = tmp_path / "seed_grid.json"
    grid.write_bytes(json.dumps(payload).encode("utf-8"))
    out = tmp_path / "fig.png"
    monkeypatch.setattr(module, "GRID", grid)
    monkeypatch.setattr(module, "OUT", out)
    assert module.main() == 0
    assert out.stat().st_size > 10_000
