"""Проверить, что каждый отчёт попал в индекс `reports/README.md`.

Зачем: индекс журнала — человеческая точка входа в отчёты, а `lab.py validate`
сверяет только строку README-журнала и карту рукописи. Дважды оказывалось, что
отчёт лежит на диске и закоммичен, но в индексе его нет (T4-результат и
пре-регистрация lesion-minimal), и найти его можно было только через git.

Правила:

- проверяются все `reports/*.md`, кроме `README.md`, `TEMPLATE.md`;
- достаточно, чтобы имя файла встречалось в индексе как ссылка `(имя.md)`;
- отчёт без строки в индексе — ошибка (код 1), а не предупреждение;
- битые ссылки в индексе ловит `scripts/check_links.py`, здесь только полнота.

Запуск:

    python scripts/check_reports_index.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REPORTS = REPO / "reports"
INDEX = REPORTS / "README.md"
SKIP = {"README.md", "TEMPLATE.md"}


def check(reports: Path = REPORTS, index: Path = INDEX) -> tuple[int, list[str]]:
    text = index.read_text(encoding="utf-8")
    linked = set(re.findall(r"\(([^)\s]+\.md)\)", text))
    names = sorted(p.name for p in reports.glob("*.md") if p.name not in SKIP)
    missing = [name for name in names if name not in linked]
    return len(names), missing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reports", default=str(REPORTS))
    ap.add_argument("--index", default=str(INDEX))
    args = ap.parse_args(argv)

    reports = Path(args.reports) if Path(args.reports).is_absolute() else REPO / args.reports
    index = Path(args.index) if Path(args.index).is_absolute() else REPO / args.index
    for path in (reports, index):
        if not path.exists():
            print(f"нет пути: {path}")
            return 2

    total, missing = check(reports, index)
    print(f"отчётов: {total}, без строки в индексе: {len(missing)}")
    for name in missing:
        print(f"НЕТ В ИНДЕКСЕ {name}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
