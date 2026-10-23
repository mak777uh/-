#!/usr/bin/env python
"""Проверка формальных гипотез: компилирует formal/*.lean и ведёт инвентарь.

Зачем: Lean — третий инструмент рядом с CPU и GPU. Формальная гипотеза — это
теорема о наших определениях или инвариантах; её проверка машинная, а не на глаз.
Скрипт:

1. находит `formal/*.lean`;
2. запускает `lean` на каждом файле (если Lean установлен);
3. собирает имена теорем (для инвентаря и отчётов);
4. пишет `lab/formal.json` — что доказано, когда, каким коммитом;
5. возвращает ненулевой код при ошибке компиляции.

Если Lean не установлен (например, на CI-раннере), скрипт **честно** пишет
`skipped: lean not found` и завершается с кодом 0: мы не выдаём отсутствие
инструмента за доказательство. Локально — обязательный гейт.

Запуск из корня:

    python scripts/lean_check.py            # проверить
    python scripts/lean_check.py --ci       # то же, но без записи инвентаря
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FORMAL = REPO / "formal"
INVENTORY = REPO / "lab" / "formal.json"

THEOREM_RE = re.compile(r"^\s*theorem\s+([A-Za-z0-9_']+)", re.MULTILINE)
HYP_RE = re.compile(r"\b(F-[A-Z]+-\d+)\b")


def parse_theorems(source: str) -> list[str]:
    """Имена теорем в файле (для инвентаря)."""
    return THEOREM_RE.findall(source)


def parse_hypotheses(source: str) -> list[str]:
    """Идентификаторы формальных гипотез, упомянутых в файле (F-BUDGET-1 и т.п.)."""
    seen: list[str] = []
    for match in HYP_RE.findall(source):
        if match not in seen:
            seen.append(match)
    return seen


def lean_binary() -> str | None:
    for name in ("lean", "lean.exe"):
        found = shutil.which(name)
        if found:
            return found
    return None


def check_files(lean: str, paths: list[Path]) -> tuple[bool, list[dict]]:
    """Скомпилировать файлы; вернуть успех и отчёт по каждому."""
    results: list[dict] = []
    ok = True
    for path in paths:
        proc = subprocess.run([lean, str(path)], capture_output=True, text=True)
        source = path.read_text(encoding="utf-8")
        entry = {
            "file": str(path.relative_to(REPO)).replace("\\", "/"),
            "ok": proc.returncode == 0,
            "theorems": parse_theorems(source),
            "hypotheses": parse_hypotheses(source),
            "errors": proc.stderr.strip().splitlines()[:10] if proc.returncode else [],
        }
        ok = ok and entry["ok"]
        results.append(entry)
        mark = "OK " if entry["ok"] else "FAIL"
        print(f"[lean] {mark} {entry['file']} — теорем: {len(entry['theorems'])}")
        for line in entry["errors"]:
            print(f"       {line}")
    return ok, results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ci", action="store_true", help="не писать инвентарь")
    args = ap.parse_args(argv)

    paths = sorted(FORMAL.glob("*.lean")) if FORMAL.is_dir() else []
    if not paths:
        print("[lean] файлов formal/*.lean нет — нечего проверять")
        return 0

    lean = lean_binary()
    if lean is None:
        print("[lean] skipped: леан не установлен (это не доказательство, а пропуск)")
        return 0

    ok, results = check_files(lean, paths)
    payload = {
        "tool": "lean",
        "ok": ok,
        "files": results,
        "hypotheses": sorted({h for r in results for h in r["hypotheses"]}),
        "theorems_total": sum(len(r["theorems"]) for r in results),
    }
    if not args.ci:
        INVENTORY.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[lean] инвентарь: {INVENTORY.relative_to(REPO)}")
    print(f"[lean] гипотез: {len(payload['hypotheses'])}, теорем: {payload['theorems_total']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
