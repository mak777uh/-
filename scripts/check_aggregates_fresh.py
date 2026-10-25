#!/usr/bin/env python
"""check_aggregates_fresh.py — агрегаты в git обязаны совпадать с пересборкой.

Зачем: 25.10 три раза подряд код обновляли, а агрегат не пересобирали, и в отчёте
число расходилось с файлом («derived_by_construction в коде есть, в файле нет»).
Класс ошибки не в арифметике, а в устаревании: артефакт отстаёт от кода.

Как работает: для каждого агрегата из `BUILDERS` скрипт пересобирает его во
временный файл теми же командами, что и вручную, и сравнивает JSON по существу
(а не по форматированию). Расхождение — ошибка CI.

Запуск (из корня):

    python scripts/check_aggregates_fresh.py            # проверить
    python scripts/check_aggregates_fresh.py --write    # пересобрать на месте
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# агрегат -> (скрипт, доп. аргументы, команда сборки известна)
# `known=False` — файл собран командой, которая не зафиксирована в репозитории
# (например, merge_keep содержит 5 плеч, а сборка по умолчанию даёт 2), поэтому
# сверять его пересборкой нельзя: сначала надо записать команду в `metric`.
BUILDERS: dict[str, tuple[str, list[str], bool]] = {
    "w2bud_matrix.json": ("scripts/w2bud_matrix.py", [], True),
    "w2bud2_matrix.json": ("scripts/w2bud_matrix.py", [], True),
    "w2bud3_matrix.json": ("scripts/w2bud_matrix.py", [], True),
    "v8_matrix.json": ("scripts/v8_matrix.py", [], True),
    "merge_keep_matrix.json": ("scripts/v8_matrix.py", [], False),
    "founding_matrix.json": ("scripts/founding_matrix.py", [], True),
}

# поля, которые обязаны совпадать: это содержание, а не метаданные
SUBSTANCE = ("rows", "by_arm", "criteria")

# поля, которые меняются по построению (время сборки) и не должны считаться расхождением
VOLATILE = {"generated_at", "built_at", "timestamp"}


def strip_volatile(node):
    if isinstance(node, dict):
        return {k: strip_volatile(v) for k, v in node.items() if k not in VOLATILE}
    if isinstance(node, list):
        return [strip_volatile(v) for v in node]
    return node


def build(script: str, extra: list[str], out: Path) -> tuple[bool, str]:
    cmd = [PY, str(ROOT / script), "--out", str(out), *extra]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip().splitlines()[-1:] and \
            (proc.stderr or proc.stdout).strip().splitlines()[-1] or f"exit {proc.returncode}"
    return True, ""


def main(argv: list[str]) -> int:
    write = "--write" in argv
    problems: list[str] = []
    checked = 0
    skipped: list[str] = []

    warnings: list[str] = []
    for name, (script, extra, known) in sorted(BUILDERS.items()):
        target = POND / name
        if not target.exists():
            if not write:
                skipped.append(name)
            continue
        if not known:
            warnings.append(
                f"{name}: команда сборки не зафиксирована — сверка пересборкой пропущена, "
                f"запишите её в `metric` агрегата"
            )
            continue
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / name
            ok, err = build(script, extra, fresh)
            if not ok:
                problems.append(f"{name}: пересборка упала — {err}")
                continue
            if not fresh.exists():
                problems.append(f"{name}: пересборка не создала файл")
                continue
            old = strip_volatile(json.loads(target.read_text(encoding="utf-8")))
            new = strip_volatile(json.loads(fresh.read_text(encoding="utf-8")))
            if write:
                target.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
                continue
            checked += 1
            diff_substance = [k for k in SUBSTANCE if old.get(k) != new.get(k)]
            if diff_substance:
                problems.append(
                    f"{name}: содержание в git расходится с пересборкой по {diff_substance} — "
                    f"пересоберите: python {script} --out {target.relative_to(ROOT)}"
                )
            elif old != new:
                meta = sorted(set(old) ^ set(new))
                warnings.append(
                    f"{name}: устарели только метаданные {meta[:6]} (числа совпадают) — "
                    f"не критично, но пересоберите при следующей правке"
                )

    print(f"[fresh] проверено: {checked}, отложено (нет файла): {len(skipped)}")
    for s in skipped:
        print(f"[fresh] SKIP (ещё не собран): {s}")
    for w in warnings:
        print(f"[fresh] ВНИМАНИЕ: {w}")
    if problems:
        for p in problems:
            print(f"[fresh] ОШИБКА: {p}")
        return 1
    if write:
        print("[fresh] агрегаты пересобраны на месте")
        return 0
    print("[fresh] OK — агрегаты в git совпадают с пересборкой")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
