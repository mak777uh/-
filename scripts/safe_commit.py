#!/usr/bin/env python
"""safe_commit.py — коммит только при зелёном verify.

Почему появился: 25.10 я дважды подряд запушил красное состояние (сначала контракт
требовал гипотезу в registry, потом — `heartbeat_at` у `running`-пункта). Оба раза
я «собирался» проверить verify, и оба раза не проверил. Намерение — не механизм,
поэтому проверка встроена в сам коммит:

    python scripts/safe_commit.py -m "сообщение" [--no-push]

Что делает: запускает `scripts/verify.py`; при провале печатает причины и **не
коммитит**; при успехе — `git add -A`, `git commit`, `git diff --cached --stat`
печатается до коммита (правило §8 про общий индекс).

Флаг `--paths-only` ограничивает коммит перечисленными путями (когда в общем
индексе лежит чужая работа).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="коммит только при зелёном verify")
    ap.add_argument("-m", "--message", required=True)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="коммитить только эти пути (по умолчанию git add -A)")
    args = ap.parse_args(argv)

    verify = run([sys.executable, "scripts/verify.py"])
    last = [ln for ln in verify.stdout.strip().splitlines() if ln.startswith("verify")]
    print(last[-1] if last else "verify: нет вывода")
    if verify.returncode != 0:
        print("--- причины ---")
        print(verify.stdout.strip()[-2000:])
        print("[safe-commit] СТОП: verify красный, коммит не сделан")
        return 1

    add = run(["git", "add", *args.paths] if args.paths else ["git", "add", "-A"])
    if add.returncode != 0:
        print(add.stderr.strip()[:1000])
        return 1

    staged = run(["git", "diff", "--cached", "--stat"])
    if not staged.stdout.strip():
        print("[safe-commit] нечего коммитить")
        return 0
    print("--- в индекс попадает ---")
    print(staged.stdout.strip()[-1500:])

    commit = run(["git", "commit", "-m", args.message])
    print((commit.stdout + commit.stderr).strip()[:800])
    if commit.returncode != 0:
        return 1

    if not args.no_push:
        push = run(["git", "push", "origin", "main"])
        print((push.stdout + push.stderr).strip()[:400])
        if push.returncode != 0:
            return 1
    print("[safe-commit] готово")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
