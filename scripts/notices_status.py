#!/usr/bin/env python
"""Статус запросов в lab/notices.md: что отправлено, что висит, что закрыто.

Соглашение: запрос — строка, начинающаяся с `ЗАПРОС:` внутри блока заметки
(блок начинается с `### ГГГГ-ММ-ДД, ЧЧ:ММ — библиотекарь → **адресат**`).

Закрытым считается запрос, если после него в файле есть:
  * `ОТВЕТ:` (любой адресат), или
  * строка с тем же `B-###` в статусе accepted/declined доски, или
  * закрытый пункт очереди `W<n>`, если запрос на него ссылается.

Запуск: python scripts/notices_status.py [--max-hours 24] [--json]
Выход 1, если есть запросы старше порога.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOTICES = REPO / "lab" / "notices.md"
PATHS = {"notices": NOTICES}
BOARD = REPO / "lab" / "lit-board.json"
QUEUE = REPO / "library" / "work-queue.json"
HEAD = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2}),\s*(\d{2}:\d{2})\s*—\s*библиотекарь\s*→\s*(.+)$")
REQUEST = re.compile(r"^\s*(?:[-*•·]\s*)?ЗАПРОС[:：]\s*(.+)$", re.I)
TAG = re.compile(r"(B-\d{3}|W\d+|Q\d+)")


def board_status() -> dict[str, str]:
    if not BOARD.exists():
        return {}
    data = json.loads(BOARD.read_text(encoding="utf-8"))
    items = data.get("items", data if isinstance(data, list) else [])
    return {i.get("id"): i.get("status", "") for i in items if i.get("id")}


def queue_done() -> set[str]:
    if not QUEUE.exists():
        return set()
    data = json.loads(QUEUE.read_text(encoding="utf-8"))
    return {i["id"] for i in data.get("items", []) if i.get("status") == "done"}


def parse() -> list[dict]:
    path = PATHS["notices"]
    if not path.exists():
        return [], {}
    requests, block = [], None
    answered_after = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        head = HEAD.match(line)
        if head:
            block = {"date": head.group(1), "time": head.group(2), "to": head.group(3).strip()}
            continue
        if block and REQUEST.match(line):
            text = REQUEST.match(line).group(1).strip()
            requests.append({**block, "text": text, "tags": TAG.findall(text)})
        elif line.strip().upper().startswith("ОТВЕТ") and requests:
            # ОТВЕТ закрывает запросы по ссылке (B-###/W<n>/Q<n>), иначе — последний запрос
            tags = TAG.findall(line)
            matched = [r for r in requests if tags and set(r["tags"]) & set(tags)]
            for req in (matched or [requests[-1]]):
                answered_after[req["text"]] = True
    return requests, answered_after


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--max-hours", type=float, default=24.0)
    ap.add_argument("--json", default=None)
    ap.add_argument("--notices", default=None, help="файл notices (тесты)")
    args = ap.parse_args(argv)
    if args.notices:
        PATHS["notices"] = Path(args.notices)

    parsed = parse()
    if isinstance(parsed, tuple):
        requests, answered = parsed
    else:  # обратная совместимость на случай старого возврата
        requests, answered = parsed, {}

    status_board = board_status()
    done_queue = queue_done()
    now = datetime.now()
    rows, stale = [], []
    for req in requests:
        when = datetime.strptime(f"{req['date']} {req['time']}", "%Y-%m-%d %H:%M")
        age_h = (now - when).total_seconds() / 3600
        state = "open"
        if req["text"] in answered:
            state = "answered"
        for tag in req["tags"]:
            # доска НЕ закрывает запрос: B-### часто упомянут как контекст, а не как условие
            if tag.startswith("W") and tag in done_queue:
                state = "closed(очередь)"
        row = {**req, "age_hours": round(age_h, 1), "state": state}
        rows.append(row)
        if state == "open" and age_h > args.max_hours:
            stale.append(row)

    print(f"запросов: {len(rows)} | открытых: {sum(1 for r in rows if r['state'] == 'open')} "
          f"| старше {args.max_hours:g} ч: {len(stale)}")
    for row in rows[-12:]:
        mark = "!" if row in stale else " "
        print(f" {mark} {row['date']} {row['time']} → {row['to'][:28]:28} [{row['state']}] "
              f"{row['text'][:70]}")
    if args.json:
        Path(args.json).write_text(json.dumps({"requests": rows, "stale": stale},
                                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
