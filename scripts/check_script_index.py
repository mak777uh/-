"""check_script_index.py — индекс всех скриптов обязан быть полным и свежим.

Зачем. Индекс скриптов — это то, по чему внешний читатель находит команду за числом. 31.10 он покрывал 59 из 160
скриптов (37 %), а 20 скриптов не упоминались нигде. Гейт закрывает три способа, которыми индекс портится:

1. **забыли**: новый скрипт появился, в индексе его нет;
2. **устарел**: docstring изменился, индекс показывает старое;
3. **без описания**: скрипт без первой строки docstring — по нему нечего показать.

Индекс генерируется (`make_scripts_index.py`), поэтому проверка простая: пересобрать в памяти и сравнить с файлом.

Запуск:
    python scripts/check_script_index.py
    python scripts/check_script_index.py --ci
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script_names() -> set[str] | None:
    """Scripts **tracked in git** — the same set CI sees.

    02.11: this gate used to scan the working directory. Two new runners (`x81_series.py`, `x86_series.py`) sat untracked, the index
    built from disk listed them, the check passed locally and CI failed on a clean checkout. A gate whose source of truth is the
    local disk cannot catch a file that was never committed; the index ships in git, so the truth is what git tracks.
    """
    try:
        out = subprocess.run(["git", "ls-files", "scripts"], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    names = set()
    for line in out.stdout.splitlines():
        parts = line.split("/")
        # only the direct children of scripts/ (scripts/archive/*.py is archived code, not part of the index)
        if len(parts) == 2 and parts[0] == "scripts" and parts[1].endswith(".py"):
            names.add(parts[1][:-3])
    return names or None


def _load_maker():
    spec = importlib.util.spec_from_file_location("_mk", ROOT / "scripts" / "make_scripts_index.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="полнота и свежесть индекса скриптов")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    maker = _load_maker()
    problems: list[str] = []

    on_disk = _script_names()
    if on_disk is None:
        problems.append("не удалось прочитать список скриптов из git — гейт должен сравнивать индекс с тем, что уедет наружу")
        on_disk = set()
    current = maker.build()
    out = ROOT / "docs" / "scripts-index.md"
    if not out.is_file():
        problems.append("нет docs/scripts-index.md — соберите: python scripts/make_scripts_index.py --write")
    else:
        stored = out.read_text(encoding="utf-8")
        if stored != current:
            problems.append("индекс отстал от скриптов — пересоберите: python scripts/make_scripts_index.py --write")

    # каждый скрипт обязан быть в индексе и иметь непустое описание
    for name in sorted(on_disk):
        if f"`{name}.py`" not in current:
            problems.append(f"скрипт {name}.py не попал в индекс")
        desc = maker.first_line(ROOT / "scripts" / f"{name}.py")
        if desc in ("(без описания)", "(синтаксическая ошибка)"):
            problems.append(f"у {name}.py нет первой строки docstring — по нему нечего показать")

    for msg in problems[:20]:
        print("  ВНИМАНИЕ:", msg)
    if len(problems) > 20:
        print(f"  … и ещё {len(problems) - 20}")
    if problems:
        print(f"[scripts-index] проблем: {len(problems)} | скриптов {len(on_disk)}")
        return 1 if args.ci else 0
    print(f"[scripts-index] индекс полон и свеж: {len(on_disk)} скриптов")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
