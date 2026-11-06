#!/usr/bin/env python
"""lib_auto.py — ОДИН вход: вся автоматическая работа библиотекаря за такт.

Зачем: до этого шаги были разбросаны (result_scan -> result_lit -> lit_comment -> transition_gate ->
slots), и часть из них я запускал руками, часть забывал. Здесь они собраны в конвейер, который можно
звать по расписанию и который сам решает, что делать.

Конвейер (каждый шаг пропускается, если нечего делать):

  1. `result_scan.py`        — переходы из данных -> result-inbox.jsonl
  2. `result_lit.py`         — литература под СВЕЖИЕ результаты -> блок в lab/notices.md
  3. `transition_gate.py`    — каждый переход обязан быть закрыт (обзор или «не влияет»)
  4. `slots.py`              — какие слоты пропущены
  5. `claim_audit.py`        — проверка утверждений
  6. `lab.py validate`       — контракт лаборатории
  7. отчёт одной строкой + код возврата 1, если что-то красное

Запуск:
  python library/tools/lib_auto.py            # полный такт
  python library/tools/lib_auto.py --dry      # показать план, ничего не писать
  python library/tools/lib_auto.py --no-lit   # без поиска литературы (быстро, без сети)
Коды: 0 — всё зелёное; 1 — есть красное (см. отчёт).
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
PY = sys.executable


def run(name: str, cmd: list[str], dry: bool = False) -> tuple[str, int, str]:
    if dry:
        return name, 0, "(dry)"
    p = subprocess.run([PY] + cmd, capture_output=True, text=True, encoding="utf-8", cwd=REPO)
    tail = (p.stdout or "").strip().splitlines()
    return name, p.returncode, (tail[-1] if tail else "")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="автоматический такт библиотекаря")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-lit", action="store_true", help="без поиска литературы (без сети)")
    args = ap.parse_args(argv)

    steps: list[tuple[str, list[str], bool]] = [
        ("сканер результатов", ["scripts/result_scan.py"], True),
        ("литература под результаты", ["library/tools/result_lit.py"], not args.no_lit),
        ("гейт переходов", ["library/tools/transition_gate.py"], True),
        ("слоты", ["library/tools/slots.py", "--days", "1"], False),  # информативно, не краснит
        ("аудит утверждений", ["scripts/claim_audit.py"], True),
        ("контракт лаборатории", ["scripts/lab.py", "validate"], True),
    ]

    red = []
    print("=" * 60)
    for name, cmd, blocking in steps:
        n, rc, tail = run(name, cmd, args.dry)
        mark = "ok " if rc == 0 else ("!! " if blocking else ".. ")
        print(f"  {mark}{n}: {tail[:110]}")
        if rc != 0 and blocking:
            red.append(n)
    print("=" * 60)
    if red:
        print(f"красное: {', '.join(red)}")
        return 1
    print("всё зелёное")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
