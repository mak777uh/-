"""test_library_digest.py — дайджест библиотеки должен видеть пункты и цитаты.

Зачем: конспекты растут быстрее, чем мы их читаем (29 пунктов, 15 не
использованы на 22.10). Дайджест нужен, чтобы перед каждой волной видеть, что
ещё не прочитано, и не читать одно и то же дважды. Тест держит разбор формата
и определение «процитировано».
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import library_digest as ld  # noqa: E402

SAMPLE = """# Конспект

## C. Порядок данных и точность

### R5. Порядок примеров как фактор

**[Curriculum Learning](https://doi.org/10.1145/1553374.1553380)** —
Bengio Y., 2009.

`Что даёт:` порядок примеров влияет на локальный минимум.

### R6. Пониженная точность

**[A Study of BFLOAT16](https://arxiv.org/abs/1905.12322)** — Kalamkar D.
"""


def test_parse_entries_extracts_id_title_section_url(tmp_path):
    doc = tmp_path / "repro.md"
    doc.write_text(SAMPLE, encoding="utf-8")
    entries = ld.parse_entries(doc)
    assert [e["id"] for e in entries] == ["R5", "R6"]
    assert entries[0]["title"] == "Порядок примеров как фактор"
    assert entries[0]["section"] == "C. Порядок данных и точность"
    assert entries[0]["url"] == "https://doi.org/10.1145/1553374.1553380"
    assert entries[1]["url"] == "https://arxiv.org/abs/1905.12322"


def test_usage_detected_by_id_title_and_doi(tmp_path):
    doc = tmp_path / "repro.md"
    doc.write_text(SAMPLE, encoding="utf-8")
    entries = ld.parse_entries(doc)
    text = "В отчёте сослались на R6 и на 10.1145/1553374.1553380."
    marked = ld.mark_usage(entries, text)
    assert marked[0]["cited"] is True   # DOI внутри текста
    assert marked[1]["cited"] is True   # по id


def test_unused_entry_is_flagged(tmp_path):
    doc = tmp_path / "repro.md"
    doc.write_text(SAMPLE, encoding="utf-8")
    entries = ld.mark_usage(ld.parse_entries(doc), "ничего не цитируется")
    assert all(e["cited"] is False for e in entries)


def test_report_mentions_counts(tmp_path):
    doc = tmp_path / "repro.md"
    doc.write_text(SAMPLE, encoding="utf-8")
    entries = ld.mark_usage(ld.parse_entries(doc), "R5")
    report = ld.build_report(entries)
    assert "Пунктов всего: **2**" in report
    assert "R6" in report
