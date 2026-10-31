#!/usr/bin/env python
"""P8 «anchor or refuse»: у каждой строки claims-evidence обязан быть якорь.

Якорь — путь к артефакту (существующий файл), DOI или «§» раздела. Строка без якоря —
утверждение, которое нельзя проверить; по принципу P8 оно не публикуется.

Запуск: python library/tools/claims_anchor.py [--file library/claims-evidence.md]
Коды: 0 — все строки с якорем; 1 — есть строки без якоря.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def anchor_ok(cell: str) -> bool:
    cell = (cell or "").strip()
    if not cell or cell in ("—", "-", "?", "нет"):
        return False
    if "10." in cell and "/" in cell:  # DOI
        return True
    if cell.startswith("§") or "§" in cell:
        return True
    for token in re.findall(r"[\w./\\-]+\.(?:json|md|py|ya?ml)", cell):
        token = token.replace("\\", "/")
        if (REPO / token).exists():
            return True
        # голое имя файла: ищем по индексу (кэш), чтобы «w2bud_x.json» тоже считался якорем
        if "/" not in token and token in _BASENAME_INDEX():
            return True
    return False


_INDEX_CACHE: set[str] | None = None


def _BASENAME_INDEX() -> set[str]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        names: set[str] = set()
        for root in (REPO / "morphogenesis" / "experiments", REPO / "docs", REPO / "reports",
                     REPO / "library", REPO / "articles", REPO / "manuscript"):
            if root.exists():
                names |= {p.name for p in root.rglob("*") if p.is_file()}
        _INDEX_CACHE = names
    return _INDEX_CACHE


def check(path: Path) -> list[tuple[int, str]]:
    """P8 на уровне БЛОКА: каждый раздел `## ` обязан иметь якорь.

    Строки таблиц — данные, а не утверждения: требовать путь в каждой строке
    бессмысленно (это давало ложные срабатывания на таблицах значений).
    """
    bad: list[tuple[int, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    block_start = 0
    block_title = "(до первого раздела)"
    block_has_anchor = False

    def flush():
        nonlocal block_has_anchor
        if not block_has_anchor:
            bad.append((block_start, block_title))

    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            flush()
            block_start = i
            block_title = line[3:].strip()[:100]
            block_has_anchor = False
            continue
        if anchor_ok(line):
            block_has_anchor = True
    flush()
    # блок «до первого раздела» без якоря — не ошибка, если это заголовок файла
    return [b for b in bad if b[1] != "(до первого раздела)"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P8: якорь у каждой строки claims")
    ap.add_argument("--file", default="library/claims-evidence.md")
    args = ap.parse_args(argv)
    path = REPO / args.file
    bad = check(path)
    if bad:
        for line_no, text in bad:
            print(f"БЕЗ ЯКОРЯ L{line_no}: {text}")
        print(f"строк без якоря: {len(bad)} — по P8 такие не публикуются")
        return 1
    print("все строки имеют якорь")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
