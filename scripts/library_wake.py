"""Пробуждение библиотекаря по событию, а не только по календарю.

Зачем. Дежурство по cron слепо между тиками, а самое ценное окно — момент, когда
эксперимент только закрылся (числа уже есть, интерпретация ещё нет). Этот скрипт
считает отпечаток интересующего состояния и умеет ждать его изменения.

Режимы:
  --check            сравнить с прошлым снимком, напечатать, что изменилось
  --wait             ждать изменения (таймаут и интервал задаются), код 2 — таймаут
  --show             напечатать текущий отпечаток без сравнения
  --reset            перезаписать снимок текущим состоянием

Что отслеживается (только то, что мне действительно нужно):
  journal      — число строк и хеш последней строки канонического журнала;
  runs         — закрытые манифесты lab/runs/*.json (finished/failed/aborted): сколько и последний;
  polish       — артефакты серий в `_hourly/polish` (вне репозитория): сколько, последний, mtime;
  experiments  — артефакты в `morphogenesis/experiments/**`: сколько и самый свежий mtime;
  reports      — список файлов и самая поздняя mtime в reports/;
  articles     — то же для articles/;
  manuscript   — версия и число заголовков paper.md (правки разделов);
  lit_queue    — открытые пункты очереди литературы;
  board        — замечания на доске в текущей волне (id+status);
  cycle        — идентификатор и фаза волны, если lab/cycle.json есть;
  head         — HEAD репозитория (последний случай).

Снимок хранится вне репозитория: `_hourly/.lib-wake-state.json`.
"""
from __future__ import annotations

import argparse
import os
import hashlib
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE = ROOT.parent / "_hourly" / ".lib-wake-state.json"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _journal(root: pathlib.Path) -> dict:
    path = root / "morphogenesis" / "logs" / "journal.jsonl"
    if not path.exists():
        return {"lines": 0, "last": None}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"lines": len(lines), "last": _sha(lines[-1]) if lines else None}


def _dir_state(path: pathlib.Path) -> dict:
    if not path.is_dir():
        return {"count": 0, "max_mtime": 0.0, "latest": None}
    files = sorted(p for p in path.glob("*.md") if p.is_file())
    if not files:
        return {"count": 0, "max_mtime": 0.0, "latest": None}
    latest = max(files, key=lambda p: p.stat().st_mtime)
    return {
        "count": len(files),
        "max_mtime": round(max(p.stat().st_mtime for p in files), 3),
        "latest": latest.name,
    }


def _notices_to_me(root: pathlib.Path) -> dict:
    """Просьбы, адресованные библиотекарю: блоки notices с «библиотекарю» и их `ЗАПРОС:`."""
    path = root / "lab" / "notices.md"
    if not path.exists():
        return {"blocks": 0, "requests": 0, "digest": None}
    import hashlib
    import re
    blocks = 0
    requests: list[str] = []
    current_for_me = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("### "):
            current_for_me = "библиотекар" in line.lower()
            if current_for_me:
                blocks += 1
            continue
        if current_for_me:
            match = re.match(r"^\s*(?:[-*•·]\s*)?ЗАПРОС[:：]\s*(.+)$", line, re.I)
            if match:
                requests.append(re.sub(r"\s+", " ", match.group(1)).strip())
    digest = hashlib.sha1("\n".join(requests).encode("utf-8")).hexdigest()[:12] if requests else None
    return {"blocks": blocks, "requests": len(requests), "digest": digest}


def _lead_queue(root: pathlib.Path) -> dict:
    """Очередь задач ведущего (lab/queue.json) — его просьбы ко мне приходят и туда."""
    path = root / "lab" / "queue.json"
    if not path.exists():
        return {"exists": False, "size": 0, "digest": None}
    import hashlib
    data = path.read_bytes()
    return {"exists": True, "size": len(data),
            "digest": hashlib.sha1(data).hexdigest()[:12]}


def _manuscript(root: pathlib.Path) -> dict:
    path = root / "manuscript" / "paper.md"
    if not path.exists():
        return {"version": None, "headings": 0}
    text = path.read_text(encoding="utf-8", errors="replace")
    version = None
    for line in text.splitlines()[:20]:
        low = line.strip().lower()
        if "version" in low or low.startswith("**v") or low.startswith("v0."):
            version = line.strip()[:80]
            break
    return {"version": version, "headings": text.count("\n## ")}


FINISHED_STATUSES = ("finished", "failed", "aborted")


def _dir_recursive(path: pathlib.Path, pattern: str = "*") -> dict:
    """Сколько файлов и самый свежий mtime (рекурсивно) — для артефактов экспериментов и серий."""
    if not path.exists():
        return {"count": 0, "max_mtime": 0.0, "latest": None}
    files = [p for p in path.rglob(pattern) if p.is_file()]
    if not files:
        return {"count": 0, "max_mtime": 0.0, "latest": None}
    latest = max(files, key=lambda p: p.stat().st_mtime)
    return {
        "count": len(files),
        "max_mtime": round(latest.stat().st_mtime, 3),
        "latest": latest.name,
    }


def _polish(root: pathlib.Path) -> dict:
    return _dir_recursive(root.parent / "_hourly" / "polish", "*.json")


def _runs(root: pathlib.Path) -> dict:
    """Закрытые прогоны: сколько манифестов закрыто и какой последний (по mtime)."""
    runs_dir = root / "lab" / "runs"
    if not runs_dir.is_dir():
        return {"closed": 0, "latest": None, "max_mtime": 0.0}
    closed: list[pathlib.Path] = []
    for path in runs_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if str(data.get("status")) in FINISHED_STATUSES:
            closed.append(path)
    if not closed:
        return {"closed": 0, "latest": None, "max_mtime": 0.0}
    latest = max(closed, key=lambda p: p.stat().st_mtime)
    return {
        "closed": len(closed),
        "latest": latest.name,
        "max_mtime": round(latest.stat().st_mtime, 3),
    }


def _open_lit(root: pathlib.Path) -> list[str]:
    path = root / "lab" / "lit-queue.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return sorted(str(i.get("id")) for i in data.get("items", []) if i.get("status") != "done")


def _board(root: pathlib.Path) -> list[str]:
    path = root / "lab" / "lit-board.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return sorted(
        f"{i.get('id')}:{i.get('status')}"
        for i in data.get("items", [])
        if i.get("wave") == "current"
    )


def _cycle(root: pathlib.Path) -> dict:
    path = root / "lab" / "cycle.json"
    if not path.exists():
        return {"id": None, "phase": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"id": None, "phase": None}
    return {"id": data.get("id"), "phase": data.get("phase")}


def _head(root: pathlib.Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fingerprint(root: pathlib.Path) -> dict:
    return {
        "journal": _journal(root),
        "runs": _runs(root),
        "polish": _polish(root),
        "experiments": _dir_recursive(root / "morphogenesis" / "experiments"),
        "reports": _dir_state(root / "reports"),
        "articles": _dir_state(root / "articles"),
        "manuscript": _manuscript(root),
        "lit_queue": _open_lit(root),
        "board": _board(root),
        "cycle": _cycle(root),
        "notices_to_me": _notices_to_me(root),
        "lead_queue": _lead_queue(root),
        "head": _head(root),
    }


# Не будить на собственных состояниях: доска, цикл и очередь литературы меняются мной же,
# и пробуждение на них — само-триггер (измерено 24.10: 119 коммитов за день, 73 в два часа).
SIGNIFICANT_MINUS = {"head", "board", "cycle", "lit_queue"}


# Прогресс серии: во время прогона меняются journal и runs (манифесты), а артефакты
# появляются в polish/experiments только в конце. Без journal/runs сторож будил на каждом
# прогоне (24.10: пробуждения каждые ~2 мин при серии V8).
SERIES_KEYS = {"polish", "experiments", "journal", "runs"}


def is_series_only(changes: list[str]) -> bool:
    """Только прогресс серии? Тогда применяем settle; всё остальное будит сразу."""
    return bool(changes) and set(changes) <= SERIES_KEYS


def is_significant(changes: list[str]) -> bool:
    """Есть ли среди изменений что-то, кроме HEAD (коммит ради коммита — не событие)."""
    return bool(set(changes) - SIGNIFICANT_MINUS)


def diff(old: dict, new: dict) -> list[str]:
    changes: list[str] = []
    for key in new:
        if old.get(key) != new.get(key):
            changes.append(key)
    return changes


def load_state(path: pathlib.Path | None = None) -> dict:
    path = path or STATE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(data: dict, path: pathlib.Path | None = None) -> None:
    path = path or STATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check(root: pathlib.Path, state_path: pathlib.Path | None = None, update: bool = True) -> list[str]:
    old = load_state(state_path)
    new = fingerprint(root)
    changes = diff(old, new) if old else list(new.keys())
    if update:
        save_state(new, state_path)
    return changes


def wait(root: pathlib.Path, timeout: float, interval: float,
         state_path: pathlib.Path | None = None, settle: float = 0.0,
         max_settle: float = 0.0) -> int:
    deadline = time.monotonic() + timeout
    base = load_state(state_path)
    while time.monotonic() < deadline:
        current = fingerprint(root)
        changes = diff(base, current)
        if changes and is_significant(changes):
            if not is_series_only(changes):
                # коммит/рукопись/доска/очередь — будим сразу, серия тут ни при чём
                save_state(current, state_path)
                print("changed: " + ", ".join(changes))
                return 0
            # только прогресс серии: ждём тишины `settle` секунд,
            # чтобы проснуться на конце серии, а не на каждом прогоне
            quiet_since = time.monotonic()
            settle_started = quiet_since
            while (settle > 0 and time.monotonic() - quiet_since < settle
                   and time.monotonic() < deadline
                   and (max_settle <= 0 or time.monotonic() - settle_started < max_settle)):
                time.sleep(max(1.0, min(interval, settle / 4)))
                nxt = fingerprint(root)
                if diff(current, nxt):
                    current = nxt
                    quiet_since = time.monotonic()
            save_state(current, state_path)
            print("changed: " + ", ".join(diff(base, current)))
            return 0
        if changes:
            # только HEAD: свой или чужой коммит без изменений в интересующих файлах
            base = current
            save_state(current, state_path)
        lock = ROOT / "library" / ".wake.pid"
        try:
            if lock.exists():
                lock.touch()
        except OSError:
            pass
        time.sleep(interval)
    print("timeout: изменений нет")
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Пробуждение библиотекаря по событию")
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    ap.add_argument("--state", type=pathlib.Path, default=STATE)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--timeout", type=float, default=3600.0)
    ap.add_argument("--interval", type=float, default=30.0)
    ap.add_argument("--settle", type=float, default=0.0,
                    help="после изменения ждать тишины N секунд (серия пишет файлы каждые ~70 с)")
    ap.add_argument("--force", action="store_true",
                    help="снять чужой/устаревший файл-замок сторожа и запуститься")
    ap.add_argument("--max-settle", type=float, default=0.0,
                    help="дольше N секунд не ждать тишины: длинная серия не должна блокировать пробуждение")
    args = ap.parse_args(argv)

    if args.wait:
        lock = args.root / "library" / ".wake.pid"
        lock.parent.mkdir(parents=True, exist_ok=True)
        fresh = 0.0
        if lock.exists():
            try:
                fresh = time.time() - lock.stat().st_mtime
            except OSError:
                fresh = 0.0
        ttl = 300.0  # 5 мин: замок обновляется каждые `interval` (15 с), значит 300 с — уже труп
        if getattr(args, "force", False) and lock.exists():
            lock.unlink()
            fresh = 1e9
        if lock.exists() and fresh < ttl:
            print(f"сторож уже работает (файл-замок обновлялся {fresh:.0f} с назад) — второй не запускаю")
            return 3
        lock.write_text(str(os.getpid()), encoding="utf-8")
        try:
            return wait(args.root, args.timeout, args.interval, args.state,
                        args.settle, args.max_settle)
        finally:
            try:
                if lock.exists() and lock.read_text(encoding="utf-8").strip() == str(os.getpid()):
                    lock.unlink()
            except OSError:
                pass
    if args.show:
        print(json.dumps(fingerprint(args.root), ensure_ascii=False, indent=2))
        return 0
    if args.reset:
        save_state(fingerprint(args.root), args.state)
        print("снимок обновлён")
        return 0
    changes = check(args.root, args.state)
    if changes and is_significant(changes):
        print("changed: " + ", ".join(changes))
    elif changes:
        print("нет значимых изменений (только head)")
    else:
        print("нет изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
