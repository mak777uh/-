#!/usr/bin/env python
"""transition_gate.py — каждый переход из данных обязан быть закрыт: обзор или «не влияет».

Зачем: третий день подряд `self_review` писал «переходы есть, а мини-обзоры не закрывались». Обещание в
правилах не работало, поэтому проверка стала механической: журнал `library/transitions.md` (append-only) и
этот гейт.

Запуск: python library/tools/transition_gate.py [--file library/transitions.md]
Коды: 0 — все переходы закрыты; 1 — есть `pending` или строка без статуса.
"""
from __future__ import annotations

import argparse
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="гейт закрытия переходов")
    ap.add_argument("--file", default="library/transitions.md")
    args = ap.parse_args(argv)
    path = REPO / args.file
    if not path.exists():
        print(f"нет файла {args.file}")
        return 1

    bad, total = [], 0
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("`") or line.startswith("---"):
            continue
        if not line[:4].isdigit():
            continue
        total += 1
        parts = [p.strip() for p in line.split("|")]
        status = parts[3] if len(parts) > 3 else ""
        if not status or status.startswith("pending"):
            bad.append((i, line[:110]))
        elif status.startswith("review:"):
            target = REPO / status.split(":", 1)[1].strip()
            if not target.exists():
                bad.append((i, f"обзор не найден: {target.name}"))

    if bad:
        print(f"переходов: {total} | незакрытых: {len(bad)}")
        for line_no, text in bad:
            print(f"  L{line_no}: {text}")
        print("\nзакрыть: мини-обзор по шаблону `library/reviews/_mini-template.md` либо строка «не влияет: <причина>».")
        return 1
    print(f"переходов: {total} | все закрыты")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
