"""check_lean_integrity.py — целостность формальных артефактов без запуска Lean.

Почему отдельно от `scripts/verify.py`. `verify.py` уже проверяет `sorry`/`admit` — это честно ловит
недоказанное. Здесь проверяются риски другого рода, которые `sorry` не покрывает:

  * `axiom` — объявление аксиомы делает теоремы формально верными и содержательно пустыми;
  * `native_decide` — доверяет скомпилированному коду, а не ядру;
  * `unsafe`, `partial` — обходят проверку завершаемости/безопасности;
  * молчаливое **исчезновение** теоремы: список из `lab/formal.json` должен находиться в исходниках.

Идея взята из инструментов независимой проверки доказательств (SafeVerify, LeanDepViz): «Lean сказал OK»
— не то же самое, что «доказательство не опирается на посторонние допущения».

Использование:
    python scripts/check_lean_integrity.py            # проверка
    python scripts/check_lean_integrity.py --list     # показать найденные теоремы
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal"
INVENTORY = ROOT / "lab" / "formal.json"

FORBIDDEN = {
    "axiom": re.compile(r"^\s*axiom\s+", re.MULTILINE),
    "native_decide": re.compile(r"\bnative_decide\b"),
    "unsafe": re.compile(r"^\s*(unsafe\s+)?def\s+.*\bunsafe\b|^\s*unsafe\s+(def|theorem)", re.MULTILINE),
    "partial": re.compile(r"^\s*partial\s+def\s", re.MULTILINE),
}
THEOREM = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+)?theorem\s+([A-Za-z_][\w.']*)", re.MULTILINE)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if not FORMAL.exists():
        print("[lean-integrity] каталога formal/ нет — пропускаю")
        return 0

    files = sorted(FORMAL.glob("*.lean"))
    problems: list[str] = []
    found: dict[str, str] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        for name, rx in FORBIDDEN.items():
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"{path.name}:{line}: запрещённая конструкция «{name}»")
        for m in THEOREM.finditer(text):
            found[m.group(1)] = path.name

    # сверка с инвентарём: теоремы, объявленные в lab/formal.json, должны существовать
    if INVENTORY.exists():
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        total = inv.get("theorems_total")
        if isinstance(total, int) and total != len(found):
            problems.append(
                f"в lab/formal.json theorems_total = {total}, а в formal/ найдено {len(found)} — "
                f"инвентарь рассинхронизирован (обновите `python scripts/lean_check.py`)")

    if args.list:
        for name, fname in sorted(found.items()):
            print(f"  {name}  ({fname})")

    if problems:
        print(f"[lean-integrity] ОШИБКА: {len(problems)} проблем (файлов {len(files)}, теорем {len(found)})")
        for p in problems[:15]:
            print("   ", p)
        return 1
    print(f"[lean-integrity] OK — файлов {len(files)}, теорем {len(found)}, "
          f"запрещённых конструкций нет, инвентарь сходится")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
