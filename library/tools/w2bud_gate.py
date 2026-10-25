#!/usr/bin/env python
"""Гейт полноты для серии W2-bud (клеточное почкование против W1).

Зачем: агрегатор `scripts/w2bud_matrix.py` при неполной серии печатает
`I_positive_in_w2bud: false`, что читается как отрицательный результат, хотя данные не добраны.
Этот гейт проверяет полноту ДО чтения критериев и не даёт вынести вердикт на неполной серии.

Правило (B-077): по каждому плечу (`cell`, `colony`) должно быть >= `--min-seeds` прогонов.
Если меньше — «ВЕРДИКТ: серия неполная — вердикт не выносится», код 2.

Запуск:
  python library/tools/w2bud_gate.py --src morphogenesis/experiments/E09_pond/w2bud
"""
from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARMS = ("cell", "colony")
NAME = re.compile(r"w2bud2?_(?P<arm>cell|colony)_seed(?P<seed>\d+)\.json$")


def counts(src: Path) -> dict[str, int]:
    out = {arm: 0 for arm in ARMS}
    for path in glob.glob(str(src / "w2bud*_*.json")):
        match = NAME.search(Path(path).name)
        if match:
            out[match.group("arm")] += 1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Гейт полноты серии W2-bud")
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud")
    ap.add_argument("--min-seeds", type=int, default=10)
    ap.add_argument("--matrix", default="scripts/w2bud_matrix.py")
    args = ap.parse_args(argv)

    src = REPO / args.src
    if not src.exists():
        print(f"нет каталога {args.src} — серия не начата")
        return 2
    got = counts(src)
    short = [f"{arm} {n}/{args.min_seeds}" for arm, n in got.items() if n < args.min_seeds]
    print("прогонов: " + ", ".join(f"{arm} {n}" for arm, n in got.items()))
    if short:
        print("ВЕРДИКТ: серия неполная (" + ", ".join(short) + ") — вердикт не выносится")
        return 2

    matrix = REPO / args.matrix
    if not matrix.exists():
        print(f"нет агрегатора {args.matrix}")
        return 2
    proc = subprocess.run([sys.executable, str(matrix), "--src", str(src)],
                          cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=180)
    print(proc.stdout.rstrip())
    if proc.returncode != 0:
        print(proc.stderr.rstrip()[-400:])
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
