"""index_report.py — add a report row to reports/README.md, or check which reports lack one.

Why this exists. Three times on 1 November a report was written and its row in the index was forgotten; twice that made CI
red and once the local gate caught it. A rule that has to be remembered is not a rule, so the row is written by a command
in the same breath as the report:

    python scripts/index_report.py --file reports/2026-11-01-thing.md --status сводка --verdict "one line, from the artifact"

`--status` is the index's own vocabulary: `план`, `сводка`, `статья`, `разбор`. `--verdict` must contain no newline; it is
the cell that tells a reader what the report concluded.

    python scripts/index_report.py --missing     # list reports with no row

Exit codes: 0 written or clean, 1 when `--missing` finds gaps.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
INDEX = REPORTS / "README.md"
ALLOWED = ("план", "сводка", "статья", "разбор")


def reports() -> list[Path]:
    return sorted(p for p in REPORTS.glob("*.md") if p.name != "README.md")


def missing() -> list[str]:
    text = INDEX.read_text(encoding="utf-8")
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", text))
    return [p.name for p in reports() if p.name not in linked]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="index a report, or list the gaps")
    ap.add_argument("--file", help="report path, absolute or relative to the repo")
    ap.add_argument("--status", default="сводка", choices=ALLOWED)
    ap.add_argument("--verdict", help="one-line conclusion for the index cell")
    ap.add_argument("--title", help="label for the link (default: file stem)")
    ap.add_argument("--date", default="2026-11-01")
    ap.add_argument("--missing", action="store_true", help="list reports with no row")
    args = ap.parse_args(argv)

    if args.missing:
        gaps = missing()
        for name in gaps:
            print("НЕТ В ИНДЕКСЕ", name)
        print(f"[index] отчётов: {len(reports())}, без строки в индексе: {len(gaps)}")
        return 1 if gaps else 0

    if not args.file or not args.verdict:
        ap.print_help()
        return 2

    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path
    name = path.name
    if name in missing() is False and f"({name})" in INDEX.read_text(encoding="utf-8"):
        print(f"[index] уже есть строка для {name}")
        return 0
    if not path.exists():
        print(f"[index] нет файла: {path}")
        return 1

    title = args.title or path.stem
    verdict = " ".join(args.verdict.split())
    row = f"| {args.date} | [{title}]({name}) | {args.status} | {verdict} |\n"
    with open(INDEX, "ab") as f:
        f.write(row.encode("utf-8"))
    print(f"[index] строка добавлена: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
