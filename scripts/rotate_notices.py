#!/usr/bin/env python
"""Ротация доски notices.md: текущее — на доске, история — в архив.

Проблема (аудит A2): notices.md вырос до 1670 строк и 49 разделов, стал логом.
Контракт: notices — указания и договорённости; история — в архив, append-only.

Правило: на доске остаются последние KEEP разделов (по умолчанию 12) и заголовок;
всё старше уезжает в lab/notices-archive.md (дописывается, не перезаписывается).

Запуск:
    python scripts/rotate_notices.py            # план, ничего не меняет
    python scripts/rotate_notices.py --apply    # выполнить
"""
from __future__ import annotations

import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD = ROOT / "lab" / "notices.md"
ARCHIVE = ROOT / "lab" / "notices-archive.md"
KEEP = 12


def split_sections(text: str) -> tuple[str, list[str]]:
    lines = text.splitlines(keepends=True)
    head: list[str] = []
    sections: list[str] = []
    current: list[str] | None = None
    for line in lines:
        if line.startswith("### "):
            if current is not None:
                sections.append("".join(current))
            current = [line]
        elif current is None:
            head.append(line)
        else:
            current.append(line)
    if current is not None:
        sections.append("".join(current))
    return "".join(head), sections


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--keep", type=int, default=KEEP)
    args = ap.parse_args(argv)

    text = BOARD.read_text(encoding="utf-8")
    head, sections = split_sections(text)
    print(f"разделов на доске: {len(sections)} (оставляем {args.keep})")
    if len(sections) <= args.keep:
        print("ротация не нужна")
        return 0

    old, keep = sections[: -args.keep], sections[-args.keep :]
    of = "архив дополняется" if ARCHIVE.exists() else "архив создаётся"
    print(f"в архив уйдёт {len(old)} разделов, {of}, на доске останется {len(keep)}")
    if not args.apply:
        print("режим плана: ничего не изменено (--apply чтобы применить)")
        return 0

    header = "# Архив доски notices (append-only)\n\nПолная история указаний и договорённостей. Текущее — в [notices.md](notices.md).\n\n"
    if ARCHIVE.exists():
        existing = ARCHIVE.read_text(encoding="utf-8")
    else:
        existing = header
    ARCHIVE.write_text(existing.rstrip() + "\n\n" + "\n".join(old), encoding="utf-8")

    note = (
        "\n---\n\n_Архив: разделы старше последних "
        f"{args.keep} перенесены в [`notices-archive.md`](notices-archive.md). "
        "Скрипт: `scripts/rotate_notices.py`._\n"
    )
    BOARD.write_text(head + "\n".join(keep) + note, encoding="utf-8")
    print(f"готово: на доске {len(keep)} разделов, в архиве {len(old)} новых")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
