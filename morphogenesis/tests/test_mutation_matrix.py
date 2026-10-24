"""test_mutation_matrix.py — агрегат серии B: разбор дозы, сводка по дозе, вердикт.

Зачем: критерий условия B считается машинно (новизна 0 при m=0, рост Shannon,
монотонность, сохранение населения). Если агрегатор ошибётся в разборе дозы или в
вердикте, «срабатывание» будет ложным. Тест на синтетике, без прогонов.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "mutation_matrix.py"
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load():
    spec = importlib.util.spec_from_file_location("mutation_matrix_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact(tmp: Path, dose_tag: str, seed: int, *, tags_series, mutations, pop, alive,
             mutation_rate) -> Path:
    path = tmp / f"mut_{dose_tag}_seed{seed}.json"
    path.write_text(json.dumps({
        "summary": {
            "mutation_rate": mutation_rate,
            "mutation_events": mutations,
            "types_alive": len(tags_series[-1]) if tags_series else 0,
            "type_counts_series": [{"step": i * 5, "counts": c} for i, c in enumerate(tags_series)],
            "births_by_type": {k: 1 for k in (tags_series[-1] if tags_series else {})},
            "type_traits": {k: 0.0 for k in (tags_series[-1] if tags_series else {})},
            "pop_time": pop,
            "final": {"alive_cells": alive},
            "generation_length": 20.0,
            "generation_divisions": 100,
            "lineage_generation": {"0": 0},
            "lineage_fitness": {"0": 10},
        }
    }, ensure_ascii=False), encoding="utf-8")
    return path


def test_dose_parsing():
    module = load()
    assert module.dose_of("m0") == 0.0
    assert module.dose_of("m0001") == 0.001
    assert module.dose_of("m001") == 0.01
    assert module.dose_of("m005") == 0.05
    assert module.dose_of("m02") == 0.2


def test_zero_mutation_gives_zero_novelty(tmp_path):
    module = load()
    series = [{"T0": 10}] * 20
    path = artifact(tmp_path, "m0", 1, tags_series=series, mutations=0, pop=80000,
                    alive=500, mutation_rate=0.0)
    row = module.analyse(path)
    assert row["dose"] == 0.0
    assert row["mutation_events"] == 0
    assert row["novelty_flux"] == 0, "при m=0 новизна строго 0"
    assert row["shannon_median"] == 0.0


def test_verdict_requires_monotone_novelty_and_population(tmp_path):
    module = load()
    zero = [{"T0": 10}] * 20
    rows = []
    # m=0: одна метка, население 80000; положительные дозы: новизна растёт
    rows.append(module.analyse(artifact(tmp_path, "m0", 1, tags_series=zero, mutations=0,
                                        pop=80000, alive=500, mutation_rate=0.0)))
    for tag, rate, pop in (("m001", 0.01, 78000), ("m005", 0.05, 76000)):
        series = [{"T0": 50}, {"T0": 40, "T1": 10}, {"T0": 30, "T1": 20}]
        series += [{"T0": 25, "T1": 25}] * 17
        rows.append(module.analyse(artifact(tmp_path, tag, 1, tags_series=series,
                                            mutations=40, pop=pop, alive=500,
                                            mutation_rate=rate)))
    table = module.by_dose(rows)
    verdict = module.verdict(table)
    assert verdict["novelty_zero_at_m0"] is True
    assert verdict["shannon_above_0.1_all_positive_doses"] is True
    assert verdict["population_preserved_m0.05_vs_m0"] is True
    assert verdict["novelty_monotone"] is True


def test_population_loss_blocks_criterion(tmp_path):
    module = load()
    zero = [{"T0": 10}] * 20
    rows = [module.analyse(artifact(tmp_path, "m0", 1, tags_series=zero, mutations=0,
                                    pop=80000, alive=500, mutation_rate=0.0))]
    for tag, rate, pop in (("m001", 0.01, 70000), ("m005", 0.05, 30000)):
        series = [{"T0": 20}, {"T0": 15, "T1": 5}] + [{"T0": 10, "T1": 10}] * 18
        rows.append(module.analyse(artifact(tmp_path, tag, 1, tags_series=series,
                                            mutations=40, pop=pop, alive=500,
                                            mutation_rate=rate)))
    verdict = module.verdict(module.by_dose(rows))
    assert verdict["population_preserved_m0.05_vs_m0"] is False, \
        "падение населения — деградация, а не изменчивость"
    assert verdict["criterion_b_satisfied"] is False
