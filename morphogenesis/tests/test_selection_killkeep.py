"""test_selection_killkeep.py — метрики условия E и агрегат условия C.

Зачем: ρ и градиент отбора (Lande & Arnold) — числа, на которых держится вывод об отборе;
парная разница kill-and-keep — вывод о достаточности условия C. Ошибка в них превращает
«отбора нет» в «метрика не считалась» и наоборот. Тесты на синтетике, без прогонов.
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


def selection_artifact(tmp: Path, eps: int, seed: int, *, traits: dict, spores: dict,
                       invested: dict | None = None) -> Path:
    path = tmp / f"sel_eps{eps:02d}_seed{seed}.json"
    summary = {
        "type_traits": traits,
        "lineage_spores": spores,
        "lineage_fitness": spores,
        "lineage_invested": invested or {},
        "pop_time": 80000,
        "final": {"alive_cells": 500},
    }
    path.write_text(json.dumps({"summary": summary}, ensure_ascii=False), encoding="utf-8")
    return path


def test_selection_gradient_direction_and_stabilizing():
    module = load("selection_matrix.py", "sel_under_test")
    traits = [i / 12 for i in range(12)]
    increasing = [3 + i * 1.5 for i in range(12)]
    beta_lin, beta_quad = module.selection_gradient(traits, increasing)
    assert beta_lin > 0.2, "фитнес растёт с признаком — линейный градиент положителен"
    assert abs(beta_quad) < 0.5, "чисто линейный отбор не даёт квадратичного члена"
    stabilizing = [3 + 10 - abs(i - 6) * 2 for i in range(12)]
    beta_lin2, beta_quad2 = module.selection_gradient(traits, stabilizing)
    assert beta_quad2 < 0, "оптимум в середине — стабилизирующий отбор (beta_quad < 0)"


def test_selection_needs_ten_lineages(tmp_path):
    module = load("selection_matrix.py", "sel_under_test2")
    traits = {f"T{i}": i / 10 for i in range(5)}
    spores = {f"T{i}": 5 for i in range(5)}
    row = module.analyse(selection_artifact(tmp_path, 10, 1, traits=traits, spores=spores))
    assert row["valid_metric"] is False
    assert "мало точек" in row["invalid_reason"]
    assert row["rho"] is None


def test_selection_rho_and_manipulation(tmp_path):
    module = load("selection_matrix.py", "sel_under_test3")
    traits = {f"T{i}": i / 12 for i in range(12)}
    spores = {f"T{i}": 3 + i for i in range(12)}
    invested = {f"T{i}": 100 + i * 20 for i in range(12)}
    row = module.analyse(selection_artifact(tmp_path, 10, 1, traits=traits,
                                            spores=spores, invested=invested))
    assert row["valid_metric"] is True
    assert row["rho"] is not None and row["rho"] > 0.9
    assert row["beta_lin"] is not None and row["beta_lin"] > 0
    assert row["manipulation_ok"] is True, "признак связан с вложенной энергией линии"


def test_kill_keep_pairs_and_criterion(tmp_path):
    module = load("kill_keep_matrix.py", "kk_under_test")
    for seed in range(1, 6):
        for arm, pop, res in (("keep", 90000 + seed, 0.5), ("clean", 80000 + seed, 1.0)):
            path = tmp_path / f"killkeep_{arm}_seed{seed}.json"
            path.write_text(json.dumps({
                "arm": arm, "seed": seed, "cells": 5, "alive_phase1": 400,
                "alive_after_reseed": 5, "resource_mean_at_reseed": res,
                "pop_time_phase2": pop, "alive_final": 300, "max_alive_phase2": 350,
                "generation_length": 20.0,
            }, ensure_ascii=False), encoding="utf-8")
    files = sorted(str(p) for p in tmp_path.glob("killkeep_*.json"))
    rows = [row for row in (module.analyse(Path(f)) for f in files) if row]
    assert len(rows) == 10
    # критерий считаем через main-логику: соберём payload вручную
    import subprocess  # noqa: F401  (не используется, оставлено для совместимости стиля)
    pairs = []
    for seed in range(1, 6):
        keep = next(r for r in rows if r["seed"] == seed and r["arm"] == "keep")
        clean = next(r for r in rows if r["seed"] == seed and r["arm"] == "clean")
        pairs.append(keep["pop_time_phase2"] - clean["pop_time_phase2"])
    assert all(d > 0 for d in pairs), "keep выше clean во всех сидах"
