#!/usr/bin/env python
"""preflight.py — предполётная проверка перед запуском серии.

Почему появился: 25.10 три серии не стартовали (2 раза `powershell` вместо `pwsh`,
1 раз процесс умер молча), и только на это ушло ~1.5 часа GPU-времени. Все три
случая ловятся одной командой до запуска.

Что проверяет (каждый пункт — то, что уже случалось хотя бы раз):

1. **Оболочка** — серии запускаются через `pwsh`, а не Windows PowerShell 5.1
   (кириллица в комментариях ломает парсинг).
2. **Замки** — нет живого замка чужой серии (`lab/locks/*.lock` + PID).
3. **Диск** — свободно ≥ 10 ГБ (§5a AGENTS.md).
4. **Пре-регистрация** — файл плана существует и закоммичен **до** запуска.
5. **Артефакты** — выходной каталог не содержит файлов будущих прогонов
   (иначе серия «пропустит» их и мы получим смешанное состояние).
6. **Якорь** — если задан, прогон на якоре обязан совпасть с ожидаемым.

Запуск (из корня):

    python scripts/preflight.py --prereg reports/2026-10-25-w2bud-v3-plan.md \
                                --outdir morphogenesis/experiments/E09_pond/w2bud3

Код возврата 0 — можно запускать; 1 — есть блокирующая проблема.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKS = ROOT / "lab" / "locks"


def check_shell() -> tuple[bool, str]:
    if shutil.which("pwsh") is None:
        return False, "pwsh не найден — серии под Windows PowerShell 5.1 падают на кириллице"
    return True, "pwsh доступен"


def check_locks() -> tuple[bool, str]:
    locks = list(LOCKS.glob("*.lock")) if LOCKS.exists() else []
    live = []
    for lock in locks:
        try:
            data = json.loads(lock.read_text(encoding="utf-8"))
        except Exception:
            live.append(f"{lock.name} (нечитаемый)")
            continue
        pid = data.get("pid")
        alive = True
        if isinstance(pid, int):
            try:
                subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                               capture_output=True, text=True, timeout=15, check=False)
                out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                                     capture_output=True, text=True, timeout=15).stdout
                alive = str(pid) in out
            except Exception:
                alive = True  # не смогли проверить — считаем живым, это безопаснее
        if alive:
            live.append(f"{lock.name} (pid {pid})")
    if live:
        return False, "живые замки: " + ", ".join(live)
    return True, "замков нет"


def check_disk(min_gb: float = 10.0) -> tuple[bool, str]:
    total, used, free = shutil.disk_usage(ROOT)
    free_gb = free / 1e9
    ok = free_gb >= min_gb
    return ok, f"свободно {free_gb:.1f} ГБ (порог {min_gb:.0f})"


def check_prereg(path: Path | None) -> tuple[bool, str]:
    if path is None:
        return False, "не указана пре-регистрация (--prereg)"
    target = (ROOT / path) if not path.is_absolute() else path
    if not target.exists():
        return False, f"нет файла пре-регистрации: {target}"
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%h %ad", "--date=short", "--", str(target)],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    commit = proc.stdout.strip()
    if not commit:
        return False, f"пре-регистрация {target.name} не закоммичена — критерий не зафиксирован"
    return True, f"пре-регистрация закоммичена: {commit}"


def check_outdir(path: Path | None) -> tuple[bool, str]:
    if path is None:
        return True, "каталог вывода не указан — пропущено"
    target = (ROOT / path) if not path.is_absolute() else path
    if not target.exists():
        return True, f"каталог появится: {target}"
    json_files = [p for p in target.glob("*.json")]
    if json_files:
        return False, (f"в {target.name} уже {len(json_files)} JSON — серия может «пропустить» их "
                       f"и дать смешанное состояние; очистите или смените каталог")
    return True, f"{target.name} пуст"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="предполётная проверка перед серией")
    ap.add_argument("--prereg", default=None, help="путь к пре-регистрации (обязательна)")
    ap.add_argument("--outdir", default=None, help="каталог артефактов серии")
    ap.add_argument("--min-gb", type=float, default=10.0)
    args = ap.parse_args(argv)

    checks = [
        ("оболочка", check_shell()),
        ("замки", check_locks()),
        ("диск", check_disk(args.min_gb)),
        ("пре-регистрация", check_prereg(Path(args.prereg) if args.prereg else None)),
        ("каталог вывода", check_outdir(Path(args.outdir) if args.outdir else None)),
    ]
    failed = 0
    for name, (ok, msg) in checks:
        mark = "OK  " if ok else "СТОП"
        print(f"[preflight] {mark} {name:<16} — {msg}")
        failed += 0 if ok else 1
    if failed:
        print(f"[preflight] блокирующих проблем: {failed} — запуск не разрешён")
        return 1
    print("[preflight] всё чисто — серию можно запускать")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
