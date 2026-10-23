"""Инсайт → действие: учёт того, что прочитанное сразу встроено в работу.

Проблема, которую решает: чтение даёт идеи, но без привязки к действию они остаются в
тексте. Здесь у каждого инсайта обязательное поле `action`:
  - `param`   — новая опция/параметр в коде (какой файл, какое имя);
  - `hypothesis` — гипотеза с критерием в очереди реестра;
  - `task`    — задача исполнителю (id на доске);
  - `none`    — осознанно не применяем (обязательно `why`).

Команды:
  --add --source P6 --insight "..." --action task --ref task-3
  --apply ID --ref <что именно>     (пометить применённым, с датой)
  --decline ID --why "..."          (осознанно отклонить)
  --check                           (показать открытые; код 1, если есть старше 24 ч)
  --list
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "lab" / "insights.json"
ACTION_KINDS = ("param", "hypothesis", "task", "none")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> dict:
    if REG.exists():
        return json.loads(REG.read_text(encoding="utf-8"))
    return {"updated_at": None, "items": []}


def save(data: dict) -> None:
    data["updated_at"] = _now()
    REG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add(data: dict, source: str, insight: str, action: str, ref: str, why: str) -> dict:
    if action not in ACTION_KINDS:
        raise SystemExit(f"action должен быть одним из {ACTION_KINDS}")
    if action == "none" and not why:
        raise SystemExit("для action=none нужен --why: почему не применяем")
    item = {
        "id": f"I-{len(data['items']) + 1:03d}",
        "source": source,
        "insight": insight.strip(),
        "action": action,
        "ref": ref,
        "why": why or None,
        "status": "open",
        "created_at": _now(),
        "applied_at": None,
    }
    data["items"].append(item)
    return item


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--source", default="?")
    ap.add_argument("--insight", default="")
    ap.add_argument("--action", default="task")
    ap.add_argument("--ref", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--apply", default=None)
    ap.add_argument("--decline", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    data = load()
    if args.add:
        item = add(data, args.source, args.insight, args.action, args.ref, args.why)
        save(data)
        print(f"{item['id']}: {item['insight'][:70]}… -> {item['action']} {item['ref']}")
        return 0
    for key, status in (("apply", "applied"), ("decline", "declined")):
        target = getattr(args, key)
        if target:
            for item in data["items"]:
                if item["id"] == target:
                    item["status"] = status
                    item["applied_at"] = _now()
                    item["ref"] = args.ref or item["ref"]
                    save(data)
                    print(f"{target}: {status}")
                    return 0
            print(f"{target}: не найдено")
            return 1
    if args.check:
        stale = []
        now = datetime.now(timezone.utc)
        for item in data["items"]:
            if item["status"] != "open":
                continue
            created = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age = now - created
            mark = "!" if age > timedelta(hours=24) else " "
            print(f"{mark} {item['id']} [{item['action']}] {item['insight'][:70]} (возраст {age})")
            if age > timedelta(hours=24):
                stale.append(item["id"])
        if stale:
            print(f"просрочено без действия: {stale}")
            return 1
        return 0
    for item in data["items"]:
        mark = {"open": "•", "applied": "✓", "declined": "×"}[item["status"]]
        print(f"{mark} {item['id']} [{item['action']}] {item['insight'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
