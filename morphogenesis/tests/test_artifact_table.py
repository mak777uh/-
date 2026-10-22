"""test_artifact_table.py — приложение с хешами не расходится с диском.

`manuscript/SUPPLEMENT.md` — машинно-проверяемый список артефактов. Если файл
переименовали, дописали или забыли обновить таблицу после нового прогона, тест
падает: таблица собирается обходом каталогов, а не по памяти.

Проверяется:
- таблица в SUPPLEMENT.md совпадает с тем, что даёт render();
- в таблице есть канонические артефакты и рисунки;
- пути в таблице — относительные ссылки, а не абсолютные;
- sha256 в таблице совпадает с фактическим хешем файла.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_artifact_table.py"
SUPPLEMENT = ROOT / "manuscript" / "SUPPLEMENT.md"


def load_module():
    spec = importlib.util.spec_from_file_location("artifact_table_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    module.OUT = SUPPLEMENT
    return module


def table_block(text: str, start: str, end: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    match = pattern.search(text)
    assert match, "нет маркеров таблицы"
    return match.group(0)


def test_supplement_matches_disk():
    module = load_module()
    text = SUPPLEMENT.read_text(encoding="utf-8")
    assert table_block(text, module.START, module.END) == module.render()


def test_table_covers_canonical_and_figures():
    module = load_module()
    table = module.render()
    assert "census.json" in table
    assert "class_centroids_frozen.json" in table
    assert "perturbations.json" in table
    assert ".png" in table
    assert "lab/checkpoints.json" in table


def test_paths_are_relative():
    module = load_module()
    table = module.render()
    assert "C:/" not in table and "C:\\" not in table
    assert "(../morphogenesis/experiments/" in table


def test_hashes_match_files():
    module = load_module()
    table = module.render()
    rows = [
        line
        for line in table.splitlines()
        if line.startswith("| [`")
    ]
    assert len(rows) > 20, f"подозрительно мало артефактов: {len(rows)}"
    for row in rows[:10]:
        link = re.search(r"\]\(\.\./([^)]+)\)", row)
        sha = re.search(r"`([0-9a-f]{64})`", row)
        assert link and sha, row
        path = ROOT / link.group(1)
        assert path.is_file(), path
        assert module.sha256(path) == sha.group(1), path
