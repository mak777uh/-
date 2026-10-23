#!/usr/bin/env python
"""Проверка, что цикл движется всеми тремя ногами, а не только прогонами.

Владелец: «сделай тест, что в новых циклах ты движешься вместе с чтением гипотез и
библиотеки». Этот скрипт и есть такой тест.

Цикл по AGENTS §3a имеет три ноги:
  1) **эксперименты** — новые артефакты прогонов;
  2) **чтение** — работа с библиотекой/гипотезами: новые инсайты, записи библиотеки,
     закрытые пункты очереди литературы, решения по доске;
  3) **гипотезы** — изменения в lab/registry.json (next_hypotheses, статусы).

Проверка: за последние N дней (по git log) каждая нога должна иметь хотя бы одно
изменение. Если нога пустая — она и есть узкое место: обычно это «гоним прогоны, а
читаем и обновляем гипотезы задним числом».

Запуск:
    python scripts/cycle_audit.py              # отчёт за 1 день
    python scripts/cycle_audit.py --days 3
    python scripts/cycle_audit.py --ci         # код 1, если какая-то нога пустая
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEGS = {
    "эксперименты": [
        "morphogenesis/experiments/",
        "morphogenesis/logs/",
        "lab/runs/",
    ],
    "чтение": [
        "library/",
        "lab/insights.json",
        "lab/lit-queue.json",
        "lab/lit-board.json",
        "docs/prior-art",
    ],
    "гипотезы": [
        "lab/registry.json",
        "docs/plan-alive.md",
        "docs/world-design.md",
    ],
}


def changed_files(days: int) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", f"--since={days} days ago", "--name-only", "--pretty=format:"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def classify(files: list[str]) -> dict[str, list[str]]:
    """Разложить изменённые файлы по трём ногам цикла (для тестов и отчёта)."""
    return {
        leg: sorted({f for f in files if f.startswith(tuple(prefixes))})
        for leg, prefixes in LEGS.items()
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    files = changed_files(args.days)
    if not files:
        print(f"за {args.days} дн. изменений в git нет — цикл не двигался")
        return 1 if args.ci else 0

    print(f"изменённых файлов за {args.days} дн.: {len(files)}")
    empty: list[str] = []
    legs = classify(files)
    for leg, hits in legs.items():
        status = "OK" if hits else "ПУСТО"
        print(f"\n[{status}] {leg}: {len(hits)} файлов")
        for path in hits[:6]:
            print(f"   · {path}")
        if len(hits) > 6:
            print(f"   · … ещё {len(hits) - 6}")
        if not hits:
            empty.append(leg)

    if empty:
        print("\nузкое место: " + ", ".join(empty))
        print("это значит: цикл шёл не по всем трём ногам (AGENTS §3a)")
        return 1 if args.ci else 0

    print("\nвсе три ноги цикла двигались")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
