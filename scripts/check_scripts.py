"""P2: какие скрипты никто не вызывает — профилактика мёртвого кода.

Мёртвый скрипт — не просто мусор: он создаёт ложное впечатление, что механизм есть.
Проверка: для каждого `scripts/*.py` считаем упоминания в документации, тестах,
CI и других скриптах вне самого файла. Ноль упоминаний — кандидат в архив.

Запуск:
    python scripts/check_scripts.py            # отчёт
    python scripts/check_scripts.py --ci       # код 1, если есть мёртвые
"""
from __future__ import annotations

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def references(name: str) -> int:
    stem = name[:-3]  # без .py
    pattern = re.compile(re.escape(stem))
    count = 0
    targets = (
        list(ROOT.glob("*.md"))
        + list((ROOT / "docs").rglob("*.md"))
        + list((ROOT / "lab").glob("*.md"))
        + list((ROOT / "morphogenesis" / "tests").glob("*.py"))
        + list(SCRIPTS.glob("*.py"))
        + list((ROOT / ".github" / "workflows").glob("*.yml"))
        + [ROOT / "run_tests.py", ROOT / "Makefile"]
    )
    for path in targets:
        if not path.exists() or path.name == name:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count += len(pattern.findall(text))
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    rows = []
    for path in sorted(SCRIPTS.glob("*.py")):
        rows.append((path.name, references(path.name)))

    dead = [name for name, count in rows if count == 0]
    print(f"{'скрипт':34s} упоминаний")
    for name, count in sorted(rows, key=lambda r: r[1]):
        mark = "  <-- мёртвый" if count == 0 else ""
        print(f"{name:34s} {count:3d}{mark}")

    if dead:
        print(f"\nкандидаты в архив ({len(dead)}): {', '.join(dead)}")
        return 1 if args.ci else 0
    print("\nвсе скрипты кем-то вызываются")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
