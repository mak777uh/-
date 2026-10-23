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
        "reports": _dir_state(root / "reports"),
        "articles": _dir_state(root / "articles"),
        "manuscript": _manuscript(root),
        "lit_queue": _open_lit(root),
        "board": _board(root),
        "cycle": _cycle(root),
        "head": _head(root),
    }


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


def wait(root: pathlib.Path, timeout: float, interval: float, state_path: pathlib.Path | None = None) -> int:
    deadline = time.monotonic() + timeout
    base = load_state(state_path)
    while time.monotonic() < deadline:
        current = fingerprint(root)
        changes = diff(base, current)
        if changes:
            save_state(current, state_path)
            print("changed: " + ", ".join(changes))
            return 0
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
    args = ap.parse_args(argv)

    if args.wait:
        return wait(args.root, args.timeout, args.interval, args.state)
    if args.show:
        print(json.dumps(fingerprint(args.root), ensure_ascii=False, indent=2))
        return 0
    if args.reset:
        save_state(fingerprint(args.root), args.state)
        print("снимок обновлён")
        return 0
    changes = check(args.root, args.state)
    if changes:
        print("changed: " + ", ".join(changes))
    else:
        print("нет изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
