"""test_verify_sections_numbers.py — проверка, что гейт «числа разделов из агрегатов» работает.

Зачем: 25.10 три пересчёта одного результата дали три числа (см. `lab/notices.md`). Гейт
`scripts/verify_sections_numbers.py` должен ловить расхождение «рукопись ↔ агрегат», и сам
гейт обязан быть проверен — иначе он молча пропускает (как это было с `claims_lint`, где
`if paths and not found` не срабатывало при пустом списке путей).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_sections_numbers.py"


def load():
    spec = importlib.util.spec_from_file_location("sections_numbers", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_resolve_plain_nested_and_index():
    module = load()
    agg = {"a": {"b": 5}, "seq": [{"arm": "x", "k": 1}, {"arm": "y", "k": 2}]}
    assert module.resolve(agg, "a.b") == 5
    assert module.resolve(agg, "seq[1].k") == 2
    assert module.resolve(agg, "seq{arm=y}.k") == 2


def test_resolve_unknown_key_raises():
    module = load()
    agg = {"seq": [{"arm": "x"}]}
    try:
        module.resolve(agg, "seq{arm=zzz}")
    except KeyError:
        return
    raise AssertionError("неизвестный элемент должен давать KeyError")


def test_variants_cover_float_formatting():
    module = load()
    forms = module.variants(13.5)
    assert "13.5" in forms
    assert any(f.startswith("13.50") or f == "14" or f == "13" for f in forms)


def test_gate_fails_on_wrong_number(monkeypatch, tmp_path):
    """Если в разделе стоит не то число, гейт обязан упасть."""
    module = load()
    paper = tmp_path / "paper.md"
    paper.write_text("## 4i. Проверка\n\nЗдесь сказано 7/10 и 13.5.\n", encoding="utf-8")
    agg = tmp_path / "agg.json"
    agg.write_text(json.dumps({"by_arm": [{"arm": "cell", "crow_I_positive_k_all": 9,
                                           "runs": 10}]}), encoding="utf-8")
    monkeypatch.setattr(module, "PAPER", paper)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CHECKS", [{
        "section": "4i", "aggregate": "agg.json",
        "values": {"k": "by_arm{arm=cell}.crow_I_positive_k_all",
                   "n": "by_arm{arm=cell}.runs"},
        "template": "{k}/{n}", "note": "тест",
    }])
    code = module.main([])
    assert code == 1, "гейт должен упасть: в тексте 7/10, в агрегате 9/10"


def test_gate_passes_on_correct_number(monkeypatch, tmp_path):
    module = load()
    paper = tmp_path / "paper.md"
    paper.write_text("## 4i. Проверка\n\nЗдесь сказано 9/10 и медиана 13.5.\n", encoding="utf-8")
    agg = tmp_path / "agg.json"
    agg.write_text(json.dumps({"by_arm": [{"arm": "cell", "crow_I_positive_k_all": 9,
                                           "runs": 10, "tags_ge2_median": 13.5}]}),
                   encoding="utf-8")
    monkeypatch.setattr(module, "PAPER", paper)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CHECKS", [{
        "section": "4i", "aggregate": "agg.json",
        "values": {"k": "by_arm{arm=cell}.crow_I_positive_k_all",
                   "n": "by_arm{arm=cell}.runs"},
        "template": "{k}/{n}", "note": "тест",
    }])
    assert module.main([]) == 0
