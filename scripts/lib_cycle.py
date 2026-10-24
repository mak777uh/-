#!/usr/bin/env python
"""Цикл библиотеки: состояние, выбор следующей полезной работы, учёт.

Задачи: цикл не «осматривается», а берёт ОДИН пункт из приоритетной очереди
(library/work-queue.json), доводит его до артефакта и записывает результат.
Приоритет = impact / effort; заблокированные (blocked_by) пропускаются.

Команды:
  --status            что изменилось, состояние пакетов/условий, следующая работа
  --next              печатать следующую задачу (без записи)
  --done ID --note "…"  отметить выполненной и добавить строку в library/cycle-log.md
  --add  kind title [--impact N --effort N --target T --action A --blocked-by "x,y"]
  --list              вся очередь
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUEUE = REPO / "library" / "work-queue.json"
LOG = REPO / "library" / "cycle-log.md"
STATE = REPO / "library" / ".cycle-state.json"
KINDS = ("condition", "claim", "metric", "review", "lit", "hygiene")


def load() -> dict:
    if QUEUE.exists():
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    return {"items": []}


def save(data: dict) -> None:
    QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=30).stdout.strip()
    except Exception:
        return ""


def state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"last_commit": ""}


def save_state(data: dict) -> None:
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_item(data: dict) -> dict | None:
    done_ids = {i["id"] for i in data["items"] if i.get("status") == "done"}
    best = None
    for item in data["items"]:
        if item.get("status") == "done":
            continue
        blockers = [b for b in item.get("blocked_by", []) if b not in done_ids]
        if blockers:
            continue
        score = item.get("impact", 3) / max(item.get("effort", 3), 1)
        if best is None or score > best[0]:
            best = (score, item)
    return best[1] if best else None


def cmd_status(args) -> int:
    st = state()
    since = st.get("last_commit") or ""
    print("== события ==")
    log = git("log", "--oneline", f"{since}..HEAD") if since else git("log", "--oneline", "-5")
    print(log or "нет новых коммитов")
    print("\n== пакеты доказательств ==")
    try:
        out = subprocess.run(["python", "scripts/claim_audit.py"], cwd=REPO, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=60).stdout
        print("\n".join(out.strip().splitlines()[:8]))
    except Exception as exc:
        print(f"claim_audit недоступен: {exc}")
    data = load()
    todo = [i for i in data["items"] if i.get("status") != "done"]
    print(f"\n== очередь: {len(todo)} открытых, {len(data['items']) - len(todo)} закрытых ==")
    item = next_item(data)
    if item:
        print(f"СЛЕДУЮЩАЯ РАБОТА: {item['id']} [{item['kind']}] {item['title']}")
        print(f"  действие: {item.get('action', '—')}")
        print(f"  target: {item.get('target', '—')} | impact {item.get('impact')} / effort {item.get('effort')}")
        if item.get("blocked_by"):
            print(f"  ждёт: {', '.join(item['blocked_by'])}")
    else:
        print("очередь пуста — добавить пункт через --add")
    return 0


def cmd_next(args) -> int:
    item = next_item(load())
    print(json.dumps(item, ensure_ascii=False, indent=2) if item else "очередь пуста")
    return 0


def cmd_done(args) -> int:
    data = load()
    item = next((i for i in data["items"] if i["id"] == args.id), None)
    if not item:
        print(f"нет пункта {args.id}")
        return 1
    item["status"] = "done"
    item["done_at"] = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    item["result"] = args.note or ""
    save(data)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Журнал циклов\n\n| Когда | Пункт | Вид | Результат |\n|---|---|---|---|\n",
                       encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"| {item['done_at']} | {item['id']} | {item['kind']} | {(args.note or '').replace('|', '/')} |\n")
    save_state({**state(), "last_commit": git("rev-parse", "HEAD")})
    print(f"{item['id']} закрыт")
    return 0


def cmd_add(args) -> int:
    data = load()
    data["items"].append({
        "id": args.id or f"W{len(data['items']) + 1}",
        "kind": args.kind, "title": args.title, "target": args.target or "",
        "action": args.action or "", "impact": args.impact, "effort": args.effort,
        "blocked_by": [b.strip() for b in (args.blocked_by or "").split(",") if b.strip()],
        "status": "open",
    })
    save(data)
    print("добавлено")
    return 0


def cmd_list(args) -> int:
    for item in load()["items"]:
        mark = "x" if item.get("status") == "done" else " "
        print(f"[{mark}] {item['id']:4} {item['kind']:10} i{item.get('impact')}/e{item.get('effort')} "
              f"{item['title'][:70]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("next").set_defaults(func=cmd_next)
    p = sub.add_parser("done"); p.add_argument("id"); p.add_argument("--note", default=""); p.set_defaults(func=cmd_done)
    p = sub.add_parser("add")
    p.add_argument("kind", choices=KINDS); p.add_argument("title")
    p.add_argument("--id"); p.add_argument("--target"); p.add_argument("--action")
    p.add_argument("--impact", type=int, default=3); p.add_argument("--effort", type=int, default=3)
    p.add_argument("--blocked-by"); p.set_defaults(func=cmd_add)
    sub.add_parser("list").set_defaults(func=cmd_list)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
