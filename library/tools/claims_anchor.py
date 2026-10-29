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
    return False


def check(path: Path) -> list[tuple[int, str]]:
    bad: list[tuple[int, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set("".join(cells)) <= set("-: "):
            continue
        if cells[0].upper() in ("ID", "C1", "ПАКЕТ") or cells[0].startswith("---"):
            continue
        row_id = cells[0]
        if not re.match(r"^[A-Za-z]?\d+", row_id) and not row_id.startswith("C"):
            continue
        if not any(anchor_ok(c) for c in cells[1:]):
            bad.append((i, line[:110]))
    return bad


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
