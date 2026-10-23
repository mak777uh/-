"""Пул отложенного: идеи, снятые с плана, но не выброшенные.

Зачем: убирая что-то из текущего плана (проверено в литературе, не ко времени,
слишком дорого), мы не стираем это — кладём в `lab/pool.json` с **условием
возврата**: при каком результате или вопросе к этому стоит вернуться.

Использование:
    python scripts/pool.py                 # показать пул таблицей
    python scripts/pool.py --status deferred
    python scripts/pool.py --doc           # переписать docs/pool-deferred.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "lab" / "pool.json"
DOC = ROOT / "docs" / "pool-deferred.md"

STATUSES = ("deferred", "rejected_by_us", "known_in_literature", "blocked_by_owner")


def load() -> dict:
    return json.loads(POOL.read_text(encoding="utf-8"))


def render_table(items: list[dict]) -> str:
    lines = [
        "| id | идея | статус | почему не сейчас | условие возврата | цена |",
        "|---|---|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item['id']} | {item['title']} | {item['status']} | "
            f"{item['why']} | {item['trigger']} | {item['cost']} |"
        )
    return "\n".join(lines)


def render_doc(pool: dict) -> str:
    items = pool["items"]
    by_status: dict[str, list[dict]] = {}
    for item in items:
        by_status.setdefault(item["status"], []).append(item)

    parts = [
        "# Пул отложенного: что сняли с плана и при каких условиях вернём",
        "",
        "Правило: **убираем из плана — не стираем**. Каждая идея лежит здесь с условием",
        "возврата: при каком результате или вопросе к ней стоит вернуться. Пул — не свалка:",
        "если у пункта нет условия возврата, он не нужен.",
        "",
        "Машинная версия: [`lab/pool.json`](../lab/pool.json); команда `python scripts/pool.py`.",
        "",
    ]
    titles = {
        "deferred": "## Отложено (вернёмся при условии)",
        "rejected_by_us": "## Проверено нами и закрыто (отрицательный результат)",
        "known_in_literature": "## Известно из литературы (повторять не нужно)",
        "blocked_by_owner": "## Ждёт решения владельца",
    }
    for status in STATUSES:
        if status not in by_status:
            continue
        parts.append(titles[status])
        parts.append("")
        parts.append(render_table(by_status[status]))
        parts.append("")
    parts.append(f"Всего в пуле: **{len(items)}**.")
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--status", choices=STATUSES, default=None)
    ap.add_argument("--doc", action="store_true", help="переписать docs/pool-deferred.md")
    args = ap.parse_args(argv)

    pool = load()
    items = pool["items"]
    if args.status:
        items = [i for i in items if i["status"] == args.status]

    if args.doc:
        DOC.write_text(render_doc(pool), encoding="utf-8")
        print(f"обновлено: {DOC.relative_to(ROOT)} ({len(pool['items'])} пунктов)")
        return 0

    print(render_table(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
