"""Инсайт → действие: учёт того, что прочитанное сразу встроено в работу.

Проблема, которую решает: чтение даёт идеи, но без привязки к действию они остаются в
тексте. Здесь у каждого инсайта обязательное поле `action`:
  - `param`   — новая опция/параметр в коде (какой файл, какое имя);
  - `hypothesis` — гипотеза с критерием в очереди реестра;
  - `task`    — задача исполнителю (id на доске);
  - `experiment_change` — изменить уже запланированный эксперимент (что и как);
  - `reprioritize` — переставить очередь/задачи в более оптимальный порядок;
  - `none`    — осознанно не применяем (обязательно `why`).

Для `experiment_change` и `reprioritize` поле `--change` обязательно: что именно
меняется и почему это оптимальнее. Поле `--expect` — какого эффекта ждём (число/знак).

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
ACTION_KINDS = ("param", "hypothesis", "task", "experiment_change", "reprioritize", "none")
MAX_OPEN = 5  # больше — журнал чтения, а не работа


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> dict:
    if REG.exists():
        return json.loads(REG.read_text(encoding="utf-8"))
    return {"updated_at": None, "items": []}


def save(data: dict) -> None:
    data["updated_at"] = _now()
    REG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add(data: dict, source: str, insight: str, action: str, ref: str, why: str,
        change: str = "", expect: str = "") -> dict:
    if action not in ACTION_KINDS:
        raise SystemExit(f"action должен быть одним из {ACTION_KINDS}")
    if action == "none" and not why:
        raise SystemExit("для action=none нужен --why: почему не применяем")
    if action in ("experiment_change", "reprioritize") and not change:
        raise SystemExit("для experiment_change/reprioritize нужен --change: что меняется")
    item = {
        "id": f"I-{len(data['items']) + 1:03d}",
        "source": source,
        "insight": insight.strip(),
        "action": action,
        "ref": ref,
        "change": change or None,
        "expect": expect or None,
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
    ap.add_argument("--change", default="", help="что именно меняется (для experiment_change/reprioritize)")
    ap.add_argument("--expect", default="", help="какого эффекта ждём")
    ap.add_argument("--apply", default=None)
    ap.add_argument("--decline", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    data = load()
    if args.add:
        open_now = [i for i in data["items"] if i.get("status") == "open"]
        if len(open_now) >= MAX_OPEN:
            print(f"ОТКАЗ: открытых инсайтов {len(open_now)} (предел {MAX_OPEN}).")
            print("Сначала закройте один: --apply ID или --decline ID --why \"...\"")
            print("Открытые: " + ", ".join(i["id"] for i in open_now))
            return 1
        item = add(data, args.source, args.insight, args.action, args.ref, args.why,
                   args.change, args.expect)
        save(data)
        print(f"{item['id']}: {item['insight'][:60]}… -> {item['action']} {item['ref']}"
              + (f" | {item['change'][:60]}" if item.get("change") else ""))
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
        extra = f" | {item['change'][:50]}" if item.get("change") else ""
        print(f"{mark} {item['id']} [{item['action']}] {item['insight'][:60]}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
