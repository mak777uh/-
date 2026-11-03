#!/usr/bin/env python
"""pairwise_audit.py — где сравниваются плечи, но не названа поправка на множественные сравнения.

Основание: preprint 2025 (10.1101/2025.05.01.651705) — при малом числе реплик (5–10) поправка Тьюки не держит
число ложных срабатываний, а Бонферрони держит. Значит в любом месте, где сравниваются пары плеч, поправка
должна быть **названа** (или явно сказано «без поправки, описательно»).

Запуск:
  python library/tools/pairwise_audit.py [--paths articles,reports,library] [--limit 40]
Коды: 0 — все сравнения сопровождаются названной поправкой; 1 — есть сравнения без поправки.
"""
from __future__ import annotations

import argparse
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]

# Требуем НАЗВАННЫЙ тест и p-значение вида 0.0x / <0.05, иначе «p = 0.15» — это плотность, а не значение.
TEST_RE = re.compile(r"(mann[–\-]whitney|fisher|wilcoxon|kruskal|chi[–\-]?square|χ²|знаковый тест)", re.I)
PVAL_RE = re.compile(r"\bp\s*[=<>≤≥]\s*(\.|0\.)\d", re.I)
CORRECTION_WORDS = ("бонферрони", "bonferroni", "holm", "холма", "fdr", "benjamini", "поправк",
                    "без поправки", "множественн", "family-wise", "fwer", "скорректир")


def audit(roots: list[pathlib.Path]) -> list[tuple[str, int, str]]:
    bad: list[tuple[str, int, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            low = text.lower()
            if not any(w in low for w in CORRECTION_WORDS):
                for i, line in enumerate(text.splitlines(), 1):
                    if TEST_RE.search(line) and PVAL_RE.search(line) and "плотност" not in line.lower():
                        bad.append((str(path.relative_to(REPO)), i, line.strip()[:110]))
                        break
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="поправка на множественные сравнения")
    ap.add_argument("--paths", default="articles,reports,library")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args(argv)
    roots = [REPO / p.strip() for p in args.paths.split(",") if p.strip()]
    bad = audit(roots)
    if not bad:
        print("во всех файлах с попарными тестами названа поправка (или сказано «без поправки»)")
        return 0
    print(f"файлов со сравнениями БЕЗ названной поправки: {len(bad)}")
    for path, line_no, text in bad[: args.limit]:
        print(f"  {path}:{line_no} — {text}")
    if len(bad) > args.limit:
        print(f"  … и ещё {len(bad) - args.limit}")
    print("\nВАЖНО: это КАНДИДАТЫ, а не приговор.")
    print("  • одиночный пре-регистрированный тест (например, знаковый на 8/8 парах) поправки НЕ требует;")
    print("  • серия сравнений (таблица амплитуд, плечи, несколько пар) — требует названной поправки")
    print("    (Бонферрони/Holm/FDR) либо явной фразы «без поправки, описательно».")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
