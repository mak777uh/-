"""test_founding_map_metrics.py — агрегатор порога основания и метрики по картам.

Зачем: критерий «среда поддерживает основание» и метрики формы (β0/β1/rugosity) должны
считаться машинно и одинаково; ошибка в них превращает «порог основания» в произвольное
число. Тесты на синтетике, без прогонов.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load(script: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def founding_artifact(tmp: Path, n: int, seed: int, *, alive1: int, alive_final: int,
                      gate: bool = True, max_alive: int | None = None) -> Path:
    path = tmp / f"found_n{n}_seed{seed}.json"
    log = [{"step": 1, "alive_cells": alive1},
           {"step": 2, "alive_cells": max_alive if max_alive is not None else alive_final},
           {"step": 300, "alive_cells": alive_final}]
    path.write_text(json.dumps({
        "summary": {
            "config": {"ignition_gate": gate, "git_code_commit": "abc123",
                       "rule_sha256": "deadbeef"},
            "pop_time": 50000,
            "final": {"alive_cells": alive_final},
            "generation_length": 20.0,
        },
        "log": log,
    }, ensure_ascii=False), encoding="utf-8")
    return path


def test_grew_requires_exceeding_both_start_and_n(tmp_path):
    module = load("founding_matrix.py", "founding_under_test")
    # вырос: финал больше и N, и стартового размера
    row = module.analyse(founding_artifact(tmp_path, 5, 1, alive1=5, alive_final=300))
    assert row["grew"] is True and row["survived"] is True
    # не вырос: финал равен старту
    row = module.analyse(founding_artifact(tmp_path, 5, 2, alive1=5, alive_final=5))
    assert row["grew"] is False and row["survived"] is True
    # погиб
    row = module.analyse(founding_artifact(tmp_path, 5, 3, alive1=5, alive_final=0))
    assert row["grew"] is False and row["survived"] is False


def test_gate_off_or_ignition_makes_run_invalid(tmp_path):
    module = load("founding_matrix.py", "founding_under_test2")
    off = module.analyse(founding_artifact(tmp_path, 5, 1, alive1=5, alive_final=100, gate=False))
    assert off["invalid_reason"] and "гейт" in off["invalid_reason"]
    ignited = module.analyse(founding_artifact(tmp_path, 5, 2, alive1=1024, alive_final=100))
    assert ignited["invalid_reason"] and "гейт не сработал" in ignited["invalid_reason"]


def test_criteria_supports_and_threshold(tmp_path):
    module = load("founding_matrix.py", "founding_under_test3")
    rows = []
    for n, (alive1, final) in ((1, (1, 0)), (2, (2, 0)), (5, (5, 400)),
                               (10, (10, 500)), (20, (20, 600))):
        for seed in range(1, 11):
            rows.append(module.analyse(founding_artifact(tmp_path, n, seed,
                                                         alive1=alive1, alive_final=final)))
    table = module.by_n(rows)
    crit = module.criteria(table)
    assert crit["supports_founding"] is True, "при N=20 выживание и рост 10/10, при N=1 — 0/10"
    assert crit["no_founding_up_to_20"] is False


def test_map_metrics_betti_and_rugosity():
    module = load("map_metrics.py", "map_under_test")
    # кольцо 5x5: одна компонента, одна дырка
    ring = ["11111", "10001", "10001", "10001", "11111"]
    grid = module.parse_map("/".join(ring))
    assert module.betti1(grid) == 1
    assert len(module.components(grid, 1)) == 1
    # две отдельные точки: две компоненты, дырок нет
    two = ["10000", "00000", "00000", "00000", "00001"]
    grid2 = module.parse_map("/".join(two))
    assert len(module.components(grid2, 1)) == 2
    assert module.betti1(grid2) == 0
    # плотный квадрат компактнее изрезанной формы при той же площади
    solid = module.parse_map("/".join(["11100", "11100", "11100", "00000", "00000"]))
    branchy = module.parse_map("/".join(["10100", "11100", "10100", "00100", "00000"]))
    assert module.perimeter(solid) < module.perimeter(branchy)


def test_map_metrics_skips_artifacts_without_map(tmp_path):
    module = load("map_metrics.py", "map_under_test2")
    path = tmp_path / "x.json"
    path.write_text(json.dumps({"summary": {"final": {"alive_cells": 10}}}, ensure_ascii=False),
                    encoding="utf-8")
    assert module.analyse(path) is None
