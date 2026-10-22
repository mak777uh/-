"""Проверить внутренние ссылки на разделы (`§4.7`, `§5.6`) в рукописи.

Зачем: рукопись живёт версиями, разделы вставляются в середину (T4-результат стал
§4.12, а не §4.13; синтез — §5.6), и ссылка на несуществующий раздел читается как
утверждение о тексте. `lab.py validate` проверяет маркеры карты, но не ссылки
внутри текста.

Правила:

- разделы берутся из заголовков `## N.`, `### N.M.`, `#### N.M.K.`;
- ссылка `§N(.M(.K))` обязана указывать на существующий раздел;
- ссылка, помеченная как внешняя (`spec §9.2`, «спецификация §9.2»), не
  проверяется по разделам рукописи: это номер раздела спецификации, а не статьи;
- диапазон `§4.7-§4.11` или `§4.7–§4.11` проверяется по обоим концам;
- ссылки на несуществующий раздел — ошибка (код 1), а не предупреждение;
- проверяется только текст рукописи (по умолчанию `manuscript/paper.md`).

Запуск:

    python scripts/check_section_refs.py
    python scripts/check_section_refs.py manuscript/paper.md another.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT = REPO / "manuscript" / "paper.md"

HEADING_RE = re.compile(r"^(#{1,4})\s+(\d+(?:\.\d+)*)\.?\s")
REF_RE = re.compile(r"§\s?(\d+(?:\.\d+)*)(?:\s?[-–—]\s?§?\s?(\d+(?:\.\d+)*))?")
# «spec §9.2» / «спецификация §9.2» — номер раздела спецификации, не статьи.
EXTERNAL_HINT_RE = re.compile(
    r"(spec\w*|спецификаци\w*)(?:['’]s)?\W{0,3}$", re.IGNORECASE
)


def sections(text: str) -> set[str]:
    found = set()
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            found.add(match.group(2))
    return found


def refs(text: str):
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in REF_RE.finditer(line):
            prefix = line[: match.start()]
            if EXTERNAL_HINT_RE.search(prefix):
                continue  # ссылка на раздел другого документа
            yield lineno, match.group(1), match.group(2)


def check(paths: list[Path]) -> tuple[int, list[str]]:
    total_refs, problems = 0, []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        known = sections(text)
        if not known:
            problems.append(f"{path.name}: не найдено ни одного нумерованного раздела")
            continue
        for lineno, first, second in refs(text):
            total_refs += 1
            for ref in (first, second):
                if ref and ref not in known:
                    problems.append(
                        f"{path.name}:{lineno}: ссылка на §{ref}, такого раздела нет"
                    )
    return total_refs, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="файлы (по умолчанию manuscript/paper.md)")
    args = ap.parse_args(argv)

    paths = [Path(p) if Path(p).is_absolute() else REPO / p for p in args.paths] or [DEFAULT]
    for path in paths:
        if not path.is_file():
            print(f"нет файла: {path}")
            return 2

    total, problems = check(paths)
    print(f"файлов: {len(paths)}, ссылок на разделы: {total}, проблем: {len(problems)}")
    for item in problems:
        print(f"ПРОБЛЕМА {item}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
