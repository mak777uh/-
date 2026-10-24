#!/usr/bin/env python
"""Входящие библиотеки: что появилось и что я ещё не прочитал.

Проблема, которую решает скрипт: библиотекарь пишет в `library/`, `lab/lit-board.json`,
`lab/lit-queue.json` и `lab/insights.json`, а ведущий в цикле смотрит на артефакты
прогонов. Работа библиотекаря при этом делается, но не попадает в решения — она
«прочитана, когда владелец сказал».

Как работает: хранит в `_hourly/library_state.json` коммит, до которого библиотека
прочитана. Показывает:
  * изменённые файлы библиотеки после этой отметки;
  * новые замечания доски со статусом new и их возраст;
  * открытые инсайты без действия;
  * пункты очереди литературы без ответа.

Команды:
    python scripts/library_inbox.py            # что нового
    python scripts/library_inbox.py --ack      # отметить прочитанным до HEAD
    python scripts/library_inbox.py --ci       # код 1, если есть new старше 1 дня
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT.parent / "_hourly" / "library_state.json"
WATCHED = ("library/", "lab/lit-board.json", "lab/lit-queue.json", "lab/insights.json")


def git(*args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), *args],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def baseline_sha() -> str:
    """Если отметки нет — берём старейший коммит за последние 3 дня."""
    out = git("log", "--since=3 days ago", "--format=%h")
    lines = [line for line in out.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def changed_since(sha: str) -> list[str]:
    if not sha:
        return []
    out = git("diff", "--name-only", f"{sha}..HEAD")
    return [line for line in out.splitlines() if line.startswith(WATCHED)]


READABLE = (
    "library/answers.md",
    "library/lit-questions.md",
    "library/search-log.md",
    "library/synthesis/",
    "library/hypotheses/",
)


def new_sections(sha: str) -> list[str]:
    """Заголовки, добавленные в читаемые файлы библиотеки после отметки."""
    if not sha:
        return []
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "diff", f"{sha}..HEAD", "--no-color", "--"]
            + [p for p in ("library",)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    sections: list[str] = []
    current_file = ""
    for line in out.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if line.startswith("+#") and any(current_file.startswith(p) for p in READABLE):
            title = line[1:].strip()
            if title and title not in sections:
                sections.append(title)
    return sections


def board_new() -> list[dict]:
    path = ROOT / "lab" / "lit-board.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in data.get("items", []) if item.get("status") == "new"]


def insights_without_action(hours: int = 24) -> list[dict]:
    path = ROOT / "lab" / "insights.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    now = datetime.now(timezone.utc)
    stale = []
    for item in data.get("items", []):
        if item.get("status") != "open":
            continue
        created = item.get("created_at") or ""
        try:
            age = now - datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            stale.append(item)
            continue
        if age > timedelta(hours=hours):
            stale.append(item)
    return stale


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ack", action="store_true", help="отметить прочитанным до HEAD")
    ap.add_argument("--ci", action="store_true", help="код 1, если есть new старше 1 дня")
    ap.add_argument("--force", action="store_true", help="отметить прочитанным без проверки разделов")
    args = ap.parse_args(argv)

    state = load_state()
    seen = state.get("read_sha", "") or baseline_sha()
    head = git("rev-parse", "--short", "HEAD")

    files = changed_since(seen)
    readable = [f for f in files if any(f.startswith(p) for p in READABLE)]
    print(f"библиотека прочитана до: {seen or '—'} | сейчас: {head}")
    print(f"изменённых файлов библиотеки после отметки: {len(files)} "
          f"(читаемых: {len(readable)})")
    for name in files[:12]:
        print(f"  · {name}")
    if len(files) > 12:
        print(f"  · … ещё {len(files) - 12}")

    sections = new_sections(seen)
    print(f"\nнепрочитанных новых разделов: {len(sections)}")
    for title in sections[:20]:
        print(f"  → {title}")
    if len(sections) > 20:
        print(f"  → … ещё {len(sections) - 20}")

    news = board_new()
    print(f"\nзамечаний доски со статусом new: {len(news)}")
    stale_days = 1
    stale = 0
    for item in news:
        created = item.get("created_at") or ""
        age_days = None
        try:
            age_days = (datetime.now(timezone.utc)
                        - datetime.fromisoformat(created.replace("Z", "+00:00"))).days
        except ValueError:
            pass
        marker = ""
        if age_days is not None and age_days >= stale_days:
            marker = f"  <-- висит {age_days} дн."
            stale += 1
        print(f"  · {item.get('id')}: {(item.get('statement') or '')[:80]}{marker}")

    pending = insights_without_action()
    print(f"\nинсайтов open без действия >24 ч: {len(pending)}")
    for item in pending:
        print(f"  · {item.get('id')}: {(item.get('insight') or '')[:70]}")

    if args.ack:
        if sections and not args.force:
            print(f"\nОТКАЗ: {len(sections)} новых разделов не отмечены как прочитанные. "
                  "Прочитайте их и передайте --force, если уверены.")
            return 1
        state["read_sha"] = head
        state["read_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nотмечено прочитанным до {head}")

    if args.ci and stale:
        print(f"\nОШИБКА: {stale} замечаний new висят больше {stale_days} дня")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
