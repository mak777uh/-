#!/usr/bin/env python
"""Литдавление: нужен ли литературный слот прямо сейчас (триггер вместо календаря).

Сигналы (каждый = 1 балл):
  1) пункты доски со статусом `new` — их ещё никто не разобрал;
  2) открытые вопросы `library/lit-questions.md` (status open);
  3) записи сканера результатов за 24 ч, на которые нет мини-обзора в work-queue;
  4) «сухие» ответы: строки answers.md за 48 ч без P-/G-ссылки (эвристика по тексту).

Порог по умолчанию 3: при >= 3 литературный слот идёт вперёд обычного пункта.
Пол по времени: если литслот не было 24+ ч и давление >= 1 — тоже идти.

Запуск: python scripts/lit_pressure.py [--threshold 3] [--json out.json]
Выход 0 — слот не нужен; 1 — нужен.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOARD = REPO / "lab" / "lit-board.json"
QUESTIONS = REPO / "library" / "lit-questions.md"
QUEUE = REPO / "library" / "work-queue.json"
ANSWERS = REPO / "library" / "answers.md"
INBOX = REPO / "library" / "result-inbox.jsonl"
LOG = REPO / "library" / "cycle-log.md"


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=30).stdout
    except Exception:
        return ""


def board_new() -> list[str]:
    if not BOARD.exists():
        return []
    items = json.loads(BOARD.read_text(encoding="utf-8")).get("items", [])
    return [i["id"] for i in items if i.get("status") == "new"]


def questions_open() -> list[str]:
    if not QUESTIONS.exists():
        return []
    ids = []
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^##\s*(Q\d+)\.", line)
        if match:
            ids.append(match.group(1))
    # открытым считаем вопрос, у которого в файле нет статуса searched-1 рядом
    text = QUESTIONS.read_text(encoding="utf-8")
    return [q for q in ids if f"{q} (searched-1" not in text and f"{q}: searched-1" not in text
            and f"{q}. searched-1" not in text]


def pending_mini_reviews() -> int:
    """Открытые пункты очереди вида «мини-обзор:» — реальный долг литературы по переходам."""
    if not QUEUE.exists():
        return 0
    items = json.loads(QUEUE.read_text(encoding="utf-8")).get("items", [])
    return sum(1 for i in items if i.get("title", "").startswith("мини-обзор:")
               and i.get("status") != "done")


def open_lit_items() -> list[str]:
    """Открытые пункты с kind=lit — литература, которая уже признана нужной."""
    if not QUEUE.exists():
        return []
    items = json.loads(QUEUE.read_text(encoding="utf-8")).get("items", [])
    return [i["id"] for i in items if i.get("kind") == "lit" and i.get("status") != "done"]


def unanswered_assignments(hours: int = 24) -> int:
    """Задания библиотекарю (из notices), после которых я ещё ничего не написал.

    Прокси «не отвечено»: блок с адресатом «библиотекарю» и словами про литературу, после которого
    нет ни одного моего блока. Если мой блок идёт следом — считаем, что задание отработано.
    """
    path = REPO / "lab" / "notices.md"
    if not path.exists():
        return 0
    keywords = ("задани", "найти", "найди", "проверь", "проверить", "литератур", "doi",
                "источник", "прецедент", "канон", "обзор")
    cutoff = datetime.now() - timedelta(hours=hours)
    blocks, current, is_mine, is_task = [], None, False, False
    for line in path.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^###\s+(\d{4}-\d{2}-\d{2}),\s*(\d{2}:\d{2})\s*—\s*(.+)$", line)
        if head:
            if current is not None:
                blocks.append({"when": current, "mine": is_mine, "task": is_task})
            try:
                when = datetime.strptime(f"{head.group(1)} {head.group(2)}", "%Y-%m-%d %H:%M")
            except ValueError:
                when = datetime.now()
            addressee = head.group(3).lower()
            current = when
            is_mine = "библиотекарь →" in addressee or addressee.startswith("библиотекарь")
            is_task = ("библиотекар" in addressee and not is_mine
                       and any(k in addressee for k in keywords)) or False
        elif current is not None and any(k in line.lower() for k in keywords):
            if not is_mine:
                is_task = True
    if current is not None:
        blocks.append({"when": current, "mine": is_mine, "task": is_task})
    blocks = [b for b in blocks if b["when"] >= cutoff]
    last_mine = max((i for i, b in enumerate(blocks) if b["mine"]), default=-1)
    return sum(1 for i, b in enumerate(blocks) if b["task"] and not b["mine"] and i > last_mine)


def answers_without_source(hours: int = 48) -> int:
    if not ANSWERS.exists():
        return 0
    since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d")
    blocks = ANSWERS.read_text(encoding="utf-8").split(chr(10) + "## ")
## ")
    count = 0
    for block in blocks:
        if "уточнено" in block[:200].lower():
            continue
        if re.search(r"\|\s*P\d+|\|\s*G\d+|10\.\d{4}/", block):
            continue
        if since and since in block[:400]:
            count += 1
    return count


def last_lit_slot_hours() -> float | None:
    if not LOG.exists():
        return None
    for line in reversed(LOG.read_text(encoding="utf-8").splitlines()):
        if "lit" in line or "обзор" in line.lower():
            match = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})", line)
            if match:
                when = datetime.strptime(" ".join(match.groups()), "%Y-%m-%d %H:%M")
                return (datetime.now() - when).total_seconds() / 3600
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=int, default=3)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    new_items = board_new()          # контекст: решения, а не литдолг
    open_q = questions_open()
    mini = pending_mini_reviews()
    lit_items = open_lit_items()
    dry_answers = answers_without_source()
    assignments = unanswered_assignments()
    pressure = len(open_q) + mini + len(lit_items) + dry_answers + assignments
    age = last_lit_slot_hours()

    need = pressure >= args.threshold or (pressure >= 1 and age is not None and age >= 24)
    print(f"литдавление: {pressure} (порог {args.threshold})")
    print(f"  открытые вопросы: {len(open_q)} {open_q[:6]}")
    print(f"  мини-обзоры к переходам (долг): {mini}")
    print(f"  открытые lit-пункты очереди: {len(lit_items)} {lit_items[:6]}")
    print(f"  (контекст) пунктов доски new, ждут решения ведущего: {len(new_items)}")
    print(f"  ответы без источника: {dry_answers}")
    print(f"  неотработанные задания по литературе: {assignments}")
    print(f"  часов с последнего литслота: {'—' if age is None else round(age, 1)}")
    print("ВЕРДИКТ:", "литературный слот нужен" if need else "слот не нужен — идём по очереди")
    if args.json:
        Path(args.json).write_text(json.dumps({
            "pressure": pressure, "threshold": args.threshold, "need": need,
            "board_new": new_items, "questions_open": open_q, "mini_reviews_pending": mini,
            "lit_items_open": lit_items, "answers_without_source": dry_answers,
            "assignments_open": assignments,
            "hours_since_lit": age}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if need else 0


if __name__ == "__main__":
    raise SystemExit(main())
