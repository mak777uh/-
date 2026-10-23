#!/usr/bin/env python
"""Один экран состояния цикла: вместо чтения девяти файлов руками.

Печатает: контракт, открытые инсайты (с возрастом), очередь литературы, доску
замечаний, пул с наступившими условиями возврата, замки, диск, незакоммиченное.

Запуск:
    python scripts/cycle.py            # кратко
    python scripts/cycle.py --full     # с содержимым пунктов
"""
from __future__ import annotations

import glob
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _age(ts: str) -> str:
    try:
        created = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return "?"
    delta = datetime.now(timezone.utc) - created
    hours = delta.total_seconds() / 3600
    return f"{hours:.1f} ч"


def main() -> int:
    print("=" * 70)
    print("СОСТОЯНИЕ ЦИКЛА")
    print("=" * 70)

    # 1) инсайты
    insights = _load(ROOT / "lab" / "insights.json").get("items", [])
    open_ins = [i for i in insights if i.get("status") == "open"]
    print(f"\nИнсайты: всего {len(insights)}, открытых {len(open_ins)}")
    for item in open_ins:
        print(f"  • {item['id']} [{item['action']}] {item['insight'][:60]} (возраст {_age(item.get('created_at'))})")

    # 2) очередь литературы
    lit = _load(ROOT / "lab" / "lit-queue.json").get("items", [])
    open_lit = [i for i in lit if i.get("status") != "done"]
    print(f"\nОчередь литературы: открытых {len(open_lit)} из {len(lit)}")
    for item in open_lit[:5]:
        print(f"  • {item['id']} [{','.join(item.get('kinds', []))}] {item['text'][:60]}")

    # 3) доска замечаний
    board_path = ROOT / "lab" / "lit-board.json"
    board = _load(board_path).get("items", [])
    if board:
        by_status: dict[str, int] = {}
        for item in board:
            by_status[item.get("status", "?")] = by_status.get(item.get("status", "?"), 0) + 1
        print(f"\nДоска литературы: {by_status}")
        for item in board:
            if item.get("status") == "new":
                print(f"  • {item['id']} [{item.get('type')}] {item.get('statement', '')[:60]}")
    else:
        print("\nДоска литературы: пусто или файла нет")

    # 4) пул отложенного: наступившие условия
    pool = _load(ROOT / "lab" / "pool.json").get("items", [])
    due = [p for p in pool if p.get("status") == "deferred" and p.get("trigger")]
    print(f"\nПул отложенного: {len(pool)} пунктов, из них с условием возврата {len(due)}")

    # 5) прогоны и замки
    locks = glob.glob(str(ROOT / "lab" / "locks" / "*.lock"))
    running = [l for l in _load(ROOT / "lab" / "state.json").get("runs", []) if l.get("status") == "running"]
    print(f"\nЗамки: {len(locks)} | прогонов в статусе running: {len(running)}")

    # 6) диск
    free_gb = shutil.disk_usage(ROOT).free / 1024**3
    flag = " (< 10 ГБ — тяжёлые прогоны нельзя)" if free_gb < 10 else ""
    print(f"Диск: {free_gb:.1f} ГБ свободно{flag}")

    # 7) незакоммиченное
    print("\nНезакоммиченное: см. `git status --short` (в этом скрипте не считаем)")

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
