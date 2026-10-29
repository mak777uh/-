#!/usr/bin/env python
"""check_series_followthrough.py — серия закончилась, а агрегат не собран?

Зачем (26.10): серия `W2bud_d2` закрылась в 02:46 (10 из 10 артефактов), а агрегата,
§-раздела и строки README не было до 03:15 — и заметил это владелец, а не мы. Причина та
же, что и с библиотекой: **файлы не приходят событием**. Прогоны закончились молча.

Проверка: для каждого каталога прогонов в `morphogenesis/experiments/E09_pond/` смотрим
  * есть ли артефакты (`*.json`, не агрегат);
  * есть ли агрегат (`*_matrix.json` или `*_summary.json`) в родительском каталоге E09_pond;
  * если агрегата нет ИЛИ он старше последнего артефакта — предупреждение.

Код выхода 1 только при `--strict` (для CI). По умолчанию печатает и выходит 0,
потому что «серия ещё идёт» — нормальное состояние, а не ошибка.

Запуск:
    python scripts/check_series_followthrough.py
    python scripts/check_series_followthrough.py --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# каталоги, которые не являются сериями прогонов
SKIP_DIRS = {"analysis", "quarantine", "__pycache__"}
EXEMPT_FILE = ROOT / "lab" / "series-exemptions.json"


def _exempt() -> dict:
    """Серии, которым агрегат не нужен, с причиной и §-ссылкой."""
    if not EXEMPT_FILE.exists():
        return {}
    try:
        data = json.loads(EXEMPT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {e["series"]: e for e in data.get("exempt", []) if e.get("series")}


EXEMPT = _exempt()

# Серия, которая ЕЩЁ ИДЁТ, — не «забытая». Признаки: живой замок с её именем или
# свежий артефакт (< RUNNING_MIN). Иначе гейт краснеет на каждой идущей серии и
# превращается в фон, который перестают читать (26.10).
# 29.10: было 20 минут — меньше, чем длится один прогон на 1900 шагов (~40 мин), поэтому идущая
# серия успевала «состариться» и гейт краснел на ней (K2b, первый прогон). Ставим 90 минут.
RUNNING_MIN = 90
LOCK_DIR = ROOT / "lab" / "locks"


def _series_dirs() -> set[str]:
    """Имена каталогов-серий (по наличию артефактов JSON)."""
    root = ROOT / "morphogenesis" / "experiments"
    names = set()
    if root.exists():
        for d in root.rglob("*"):
            if d.is_dir() and any(d.glob("*.json")):
                names.add(d.name)
    return names


def _lock_alive(dirname: str) -> bool:
    """Живой замок этой серии: имя замка равно имени каталога или начинается с него + «_».

    Подстроку не используем: `w2budd2_rep_n3_...` содержит `w2budd2`, и проверка по вхождению ложно
    помечала закрытые серии идущими (это и было причиной, почему раньше замки не смотрели вообще).
    """
    if not LOCK_DIR.exists():
        return False
    # Замок принадлежит САМОМУ ДЛИННОМУ каталогу-серии, который является его префиксом: иначе
    # зонтичный каталог `w2bud` перехватывает замки `w2bud_k2b_*` и ложно считается идущим.
    dirs = _series_dirs()
    for lock in LOCK_DIR.glob("*.lock"):
        stem = lock.stem
        owners = [d for d in dirs if stem == d or stem.startswith(d + "_")]
        if not owners:
            continue
        if max(owners, key=len) == dirname:
            return True
    return False


def _is_running(dirname: str, newest_mtime: float) -> bool:
    """Серия идёт, если жив её замок или последний артефакт свежий."""
    import time
    if _lock_alive(dirname):
        return True
    return (time.time() - newest_mtime) < RUNNING_MIN * 60


def aggregates_for(dirname: str) -> list[Path]:
    """Агрегаты, которые покрывают эту серию.

    Имена агрегатов у нас исторические (`invdeath` → `invader_death_matrix.json`,
    `w2bud3` → `w2bud3_matrix.json`), поэтому угадывать по имени нельзя: ищем по
    содержимому — строки агрегата ссылаются на файлы внутри каталога серии.
    Плюс явные совпадения по имени, чтобы не зависеть только от содержимого.
    """
    found: list[Path] = []
    for cand in (POND / f"{dirname}_matrix.json", POND / f"{dirname}_summary.json", POND / f"{dirname}.json"):
        if cand.exists():
            found.append(cand)
    prefix = f"{dirname}/"
    for agg in POND.glob("*.json"):
        if agg in found or agg.parent != POND:
            continue
        try:
            data = json.loads(agg.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        rows = data.get("rows")
        if not isinstance(rows, list):
            continue
        for row in rows[:50]:
            if not isinstance(row, dict):
                continue
            ref = str(row.get("artifact") or row.get("file") or "")
            if f"/{prefix}" in ref.replace("\\", "/"):
                found.append(agg)
                return found
    return found


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="серия закрылась, а агрегат не собран?")
    ap.add_argument("--strict", action="store_true", help="код 1 при найденных расхождениях (для CI)")
    ap.add_argument("--json", action="store_true", help="машинный вывод")
    args = ap.parse_args(argv)

    if not POND.exists():
        print(f"[followthrough] нет каталога {POND.relative_to(ROOT)}")
        return 0

    problems, ok, running = [], [], []
    for d in sorted(p for p in POND.iterdir() if p.is_dir()):
        if d.name in SKIP_DIRS or d.name.startswith("_"):
            continue
        arts = [f for f in d.glob("*.json") if "_matrix" not in f.name and "_summary" not in f.name]
        if not arts:
            continue
        newest_art = max(arts, key=lambda f: f.stat().st_mtime)
        if _is_running(d.name, newest_art.stat().st_mtime):
            ok.append(d.name)
            running.append(d.name)
            continue
        if d.name in EXEMPT:
            ok.append(d.name)
            continue
        candidates = aggregates_for(d.name)
        agg = max(candidates, key=lambda a: a.stat().st_mtime) if candidates else None
        if agg is None:
            problems.append({
                "series": d.name, "artifacts": len(arts),
                "reason": "агрегата нет",
                "hint": f"собрать {d.name}_matrix.json и записать §-раздел",
            })
        elif agg.stat().st_mtime < newest_art.stat().st_mtime:
            problems.append({
                "series": d.name, "artifacts": len(arts),
                "reason": f"агрегат старше последнего артефакта ({agg.name})",
                "hint": "пересобрать агрегат из свежих прогонов",
            })
        else:
            ok.append(d.name)

    if running and not args.json:
        print(f"[followthrough] идёт прямо сейчас (не считается проблемой): {', '.join(running)}")
    if args.json:
        print(json.dumps({"problems": problems, "ok": ok}, ensure_ascii=False, indent=2))
    else:
        print(f"[followthrough] серий с артефактами: {len(ok) + len(problems)}; "
              f"в порядке: {len(ok) - len(running)}; идёт: {len(running)}")
        for p in problems:
            print(f"[followthrough] ВНИМАНИЕ: {p['series']} — {p['reason']} ({p['artifacts']} артефактов); {p['hint']}")

    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
