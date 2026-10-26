#!/usr/bin/env python
"""zenodo_link.py — вставить DOI депозита во все места репозитория одной командой.

Зачем: DOI фигурирует минимум в четырёх файлах (CITATION.cff, README, lab/checkpoints.json,
docs/checkpoints-v1.1.json, docs/deposit.md). Вставлять вручную — гарантированно забыть одно
место, и тогда часть репозитория будет ссылаться на «будет опубликовано» спустя месяцы.

Запуск:
    python scripts/zenodo_link.py --weights-doi 10.5281/zenodo.1234567
    python scripts/zenodo_link.py --weights-doi ... --concept-doi ...
    python scripts/zenodo_link.py --check          # только показать, где остались TODO

Код выхода: 0 — все заглушки заменены (или их не было), 1 — остались TODO_ после замены.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_TODO = "TODO_WEIGHTS_DOI"
CONCEPT_TODO = "TODO_WEIGHTS_CONCEPT_DOI"

TEXT_TARGETS = [
    ROOT / "CITATION.cff",
    ROOT / "README.md",
    ROOT / "docs" / "deposit.md",
]


def find_todos() -> dict[str, list[str]]:
    """Где ещё остались заглушки (по всем текстовым и json-файлам репозитория)."""
    hits: dict[str, list[str]] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in str(path):
            continue
        if path.suffix.lower() not in {".md", ".json", ".cff", ".yml", ".yaml", ".py", ".toml"}:
            continue
        if path.name == "zenodo_link.py":  # свои же константы заглушками не считаем
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        found = [t for t in (WEIGHTS_TODO, CONCEPT_TODO) if t in text]
        if found:
            hits[str(path.relative_to(ROOT)).replace("\\", "/")] = found
    return hits


def replace_in_text(path: Path, weights: str | None, concept: str | None) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    before = text
    if weights:
        text = text.replace(WEIGHTS_TODO, weights)
    if concept:
        text = text.replace(CONCEPT_TODO, concept)
    if text != before:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def replace_in_json(path: Path, weights: str | None, concept: str | None) -> bool:
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    raw = json.dumps(data, ensure_ascii=False)
    if weights and WEIGHTS_TODO in raw:
        raw = raw.replace(WEIGHTS_TODO, weights)
        changed = True
    if concept and CONCEPT_TODO in raw:
        raw = raw.replace(CONCEPT_TODO, concept)
        changed = True
    if changed:
        path.write_text(json.dumps(json.loads(raw), ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
    return changed


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="вставить DOI депозита в репозиторий")
    ap.add_argument("--weights-doi", help="DOI записи с весами (dataset)")
    ap.add_argument("--concept-doi", help="concept DOI записи с весами")
    ap.add_argument("--check", action="store_true", help="только показать, где остались заглушки")
    args = ap.parse_args(argv)

    if args.check or not (args.weights_doi or args.concept_doi):
        hits = find_todos()
        if not hits:
            print("[zenodo] заглушек TODO_ не осталось")
            return 0
        print("[zenodo] где ещё остались заглушки:")
        for path, todos in sorted(hits.items()):
            print(f"  {path}: {', '.join(todos)}")
        return 0 if args.check else 1

    for doi in (args.weights_doi, args.concept_doi):
        if doi and not re.match(r"^10\.\d{4,9}/\S+$", doi):
            print(f"[zenodo] ОШИБКА: «{doi}» не похоже на DOI (ожидается 10.xxxx/xxxx)")
            return 1

    changed = []
    for path in TEXT_TARGETS:
        if replace_in_text(path, args.weights_doi, args.concept_doi):
            changed.append(path.relative_to(ROOT))
    for rel in ("lab/checkpoints.json", "docs/checkpoints-v1.1.json", "lab/state.json"):
        p = ROOT / rel
        if p.exists() and replace_in_json(p, args.weights_doi, args.concept_doi):
            changed.append(Path(rel))

    for c in changed:
        print(f"[zenodo] обновлён: {c}")

    left = find_todos()
    if left:
        print("[zenodo] ВНИМАНИЕ: заглушки остались:")
        for path, todos in sorted(left.items()):
            print(f"  {path}: {', '.join(todos)}")
        return 1
    print("[zenodo] готово: DOI вставлен, заглушек не осталось")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
