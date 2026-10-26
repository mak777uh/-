#!/usr/bin/env python
"""check_determinism.py — эталон для новой ветки кода: два прогона с одним конфигом и сидом.

Зачем (26.10): правка «добавить цикл по родителям» сломала семантику, и оба якоря
остались бит-в-бит, потому что шли по `colony`-ветке, где новый цикл вырождается в один
элемент. Для новых веток исторического эталона нет, поэтому эталон — детерминизм: тот же
конфиг и сид дважды дают один и тот же `summary`.

Правило сравнения (записано в AGENTS §4):
  * игнорируется `wall_seconds` (время) и `config.git_commit` (метаданные коммита);
  * допускается расхождение **в одном** поле, если оно укладывается в
    `max(--abs-tol, --rel-tol × |значение|)`: абсолютный допуск 1e-4 сам по себе
    неверен для сумм порядка 1e4 (там округление float даёт 1e-3), поэтому
    используется комбинация: 1e-4 абсолютно ИЛИ 1e-6 относительно;
  * любое иное расхождение — «не детерминизм», а не «почти совпало».

Запуск:
    python scripts/check_determinism.py <путь_A.json> <путь_B.json> [--tol 1e-4]
Код возврата: 0 — детерминизм, 1 — расхождение.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

IGNORE_KEYS = {"wall_seconds"}
IGNORE_PREFIXES = ("config.git_commit",)


def flatten(node, prefix=""):
    """Плоский словарь: 'a.b.c' -> значение."""
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten(v, key))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = node
    return out


def summarise(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    flat = flatten(summary)
    return {k: v for k, v in flat.items()
            if k not in IGNORE_KEYS and not k.startswith(IGNORE_PREFIXES)}


def close(va, vb, abs_tol: float, rel_tol: float) -> tuple[bool, float]:
    """Сравнение чисел: допуск абсолютный ИЛИ относительный."""
    diff = abs(float(va) - float(vb))
    scale = max(abs(float(va)), abs(float(vb)), 1e-12)
    return diff <= max(abs_tol, rel_tol * scale), diff


def compare(a: dict, b: dict, abs_tol: float, rel_tol: float) -> tuple[list[str], list[str]]:
    hard: list[str] = []     # несовместимые расхождения
    soft: list[str] = []     # в пределах допуска (округление)
    schema: list[str] = []   # поле есть только в одном файле — эволюция схемы, не провал
    for key in sorted(set(a) | set(b)):
        if key not in a:
            # Поле появилось в новой версии кода: это эволюция схемы, а не недетерминизм.
            # Иначе сравнение артефактов разных версий всегда «провал» (замечание учёного 26.10).
            schema.append(f"{key}: только в B ({b[key]!r})")
            continue
        if key not in b:
            schema.append(f"{key}: только в A ({a[key]!r})")
            continue
        va, vb = a[key], b[key]
        if va == vb:
            continue
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            ok, diff = close(va, vb, abs_tol, rel_tol)
            if ok:
                soft.append(f"{key}: {va} против {vb} (разница {diff:.2e}) — округление")
                continue
        hard.append(f"{key}: {va!r} против {vb!r}")
    return hard, soft, schema


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="проверка детерминизма двух прогонов")
    ap.add_argument("a", help="артефакт A (например, пилот)")
    ap.add_argument("b", help="артефакт B (например, первый прогон серии)")
    ap.add_argument("--abs-tol", type=float, default=1e-4, help="абсолютный допуск округления (1e-4)")
    ap.add_argument("--rel-tol", type=float, default=1e-6, help="относительный допуск для больших сумм (1e-6)")
    args = ap.parse_args(argv)

    pa, pb = Path(args.a), Path(args.b)
    for p in (pa, pb):
        if not p.exists():
            print(f"[det] нет файла: {p}")
            return 1

    a, b = summarise(pa), summarise(pb)
    hard, soft, schema = compare(a, b, args.abs_tol, args.rel_tol)
    print(f"[det] сравниваются {pa.name} и {pb.name}: полей {len(set(a) | set(b))}")
    for s in soft:
        print(f"[det] округление: {s}")
    if schema:
        print(f"[det] новых/отсутствующих полей схемы: {len(schema)} (не считается расхождением)")
        for s in schema[:5]:
            print(f"       {s}")
    if hard:
        print(f"[det] РАСХОЖДЕНИЕ в {len(hard)} поле(ях):")
        for h in hard[:15]:
            print(f"       {h}")
        if len(hard) > 15:
            print(f"       … ещё {len(hard) - 15}")
        print("[det] вывод: НЕ детерминизм — искать, где код читает состояние или ГПСЧ иначе")
        return 1
    if len(soft) > 1:
        print(f"[det] вывод: формально в допуске, но расхождений {len(soft)} — "
              f"правило разрешает не больше одного; проверьте руками")
        return 1
    print("[det] вывод: детерминизм подтверждён (различия только метаданные и округление)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
