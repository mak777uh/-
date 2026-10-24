"""test_trait_metrics.py — метрики условия B: производственная реализация и согласие с библиотекой.

Зачем: две независимые реализации (`scripts/trait_metrics.py` и
`library/tools/trait_metrics.py`) полезны как перекрёстная проверка, но расхождение
в ОПРЕДЕЛЕНИИ — баг, а не «два мнения». Тест требует одинаковых чисел на одних и тех
же fixtures из `library/tools/fixtures/`.

Проверяется:
- `valid_mut.json` даёт одинаковые shannon/novelty/spearman в обеих реализациях;
- `missing_fields.json` — `invalid` с причиной, а не ноль (спецификация §1/§3);
- определения Shannon, потока новизны и Спирмена на синтетике.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "trait_metrics.py"
LIB_TOOL = ROOT / "library" / "tools" / "trait_metrics.py"
FIXTURES = ROOT / "library" / "tools" / "fixtures"
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prod():
    return load(SCRIPT, "trait_metrics_prod")


def test_agrees_with_library_on_valid_fixture():
    ours, theirs = prod(), load(LIB_TOOL, "trait_metrics_lib")
    path = FIXTURES / "valid_mut.json"
    assert path.is_file(), f"нет fixture {path}"
    a, b = ours.analyse(path), theirs.analyse(path)
    for key in ("valid", "shannon_median", "shannon_first", "shannon_last",
                "types_total", "spearman_trait_births"):
        assert a.get(key) == b.get(key), f"{key}: production {a.get(key)} != library {b.get(key)}"
    # Новизна тоже обязана совпадать: предковая метка (живёт с первого шага) — не
    # новизна, иначе при m=0 novelty = 1 и контроль «новизна строго 0» ломается
    # (criteria §3 п.4). Библиотека этот баг исправила; тест держит согласие.
    assert a["novelty_ancestral_excluded"], "в fixture есть предковая метка"
    assert a["novelty_flux"] == b["novelty_flux"], \
        f"новизна: production {a['novelty_flux']} != library {b['novelty_flux']}"


def test_missing_fields_are_invalid_not_zero():
    ours, theirs = prod(), load(LIB_TOOL, "trait_metrics_lib2")
    path = FIXTURES / "missing_fields.json"
    a, b = ours.analyse(path), theirs.analyse(path)
    assert a["valid"] is False and b["valid"] is False
    assert a["invalid_reason"] and b["invalid_reason"]
    assert "shannon_median" not in a, "нет данных — не ноль"


def test_shannon_bounds():
    ours = prod()
    assert ours.shannon({"A": 10}) == 0.0
    assert abs(ours.shannon({"A": 5, "B": 5}) - 0.693147) < 1e-5
    assert abs(ours.shannon({"A": 7, "B": 3}) - 0.610864) < 1e-5


def test_spearman_handles_ties_and_small_n():
    ours = prod()
    assert ours.spearman([(1.0, 2.0)]) is None
    assert ours.spearman([(0.0, 1.0), (1.0, 2.0)]) is None
    assert ours.spearman([(0.0, 1.0), (1.0, 2.0), (2.0, 3.0)]) == 1.0
    assert ours.spearman([(0.0, 3.0), (1.0, 2.0), (2.0, 1.0)]) == -1.0
    assert ours.spearman([(0.0, 1.0), (0.0, 2.0), (1.0, 3.0)]) is not None


def test_novelty_counts_only_long_lived_tags(tmp_path):
    ours = prod()
    artifact = tmp_path / "mut_x.json"
    # серия как в серии B: каждые 5 шагов, с полем step — окно новизны 50 ШАГОВ = 10 строк
    rows = []
    for step in range(0, 80, 5):
        counts = {"T0": 10 - step // 20}
        if step >= 5:
            counts["T1"] = 2 + step // 20
        if step >= 75:
            counts["T2"] = 1       # появился в конце: не выжил 50 шагов
        rows.append({"step": step, "counts": counts})
    artifact.write_text(json.dumps({
        "summary": {
            "type_counts_series": rows,
            "births_by_type": {"T0": 20, "T1": 9, "T2": 1},
            "type_traits": {"T0": 0.0, "T1": 0.01, "T2": 0.02},
        }
    }, ensure_ascii=False), encoding="utf-8")
    res = ours.analyse(artifact)
    assert res["valid"] is True
    assert res["series_interval_steps"] == 5
    assert res["novelty_window_rows"] == 10
    assert res["novelty_flux"] == 1, "новизна: только T1 прожил >= 50 шагов"
    assert res["types_total"] == 3
    assert res["spearman_trait_births"] is not None
