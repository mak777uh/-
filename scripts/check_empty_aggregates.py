#!/usr/bin/env python
"""check_empty_aggregates.py — агрегат с нулём строк при живых данных — ошибка, а не результат.

Зачем (26.10): шаблон имени в агрегаторе не пропускал подчёркивания
(`w2bud[a-z0-9]*_` против `w2budd2_rep_n3_cell_seed101.json`), файлы молча выпадали,
и агрегат выдавал `invalid_by_data: true` — то есть **«эффекта нет» вместо «данных не видно»**.
Тот же баг нашёлся вторым экземпляром в `metric_variants.py`.

Правило: агрегат обязан либо содержать строки, либо объяснить, почему их ноль.
Проверка: для каждого `*_matrix.json` с `rows: []` ищем каталог-источник по префиксу имени;
если в каталоге есть `*.json` — это ошибка.

Запуск: python scripts/check_empty_aggregates.py [--strict]
Код выхода 1 при найденных пустых агрегатах с живыми данными.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# агрегаты, у которых строки по построению могут быть нулевыми (например, сводки вариантов)
ALLOW_EMPTY = {
    "provenance-legacy.json",
    "farm-status.json",
}


def source_dirs_for(stem: str) -> list[Path]:
    """Каталоги-источники: точное имя, затем по убыванию длины префикса."""
    out = []
    exact = POND / stem
    if exact.is_dir():
        out.append(exact)
    if not out:
        for d in sorted((p for p in POND.iterdir() if p.is_dir()), key=lambda p: -len(p.name)):
            if stem.startswith(d.name):
                out.append(d)
                break
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="пустые агрегаты при живых данных")
    ap.add_argument("--strict", action="store_true", help="код 1 при находках (для CI)")
    args = ap.parse_args(argv)

    if not POND.exists():
        print("[empty-agg] каталога экспериментов нет — пропускаю")
        return 0

    bad, ok = [], 0
    for agg in sorted(POND.glob("*_matrix.json")):
        if agg.name in ALLOW_EMPTY:
            continue
        try:
            data = json.loads(agg.read_text(encoding="utf-8"))
        except Exception as exc:
            bad.append(f"{agg.name}: не читается ({exc})")
            continue
        rows = data.get("rows")
        by_arm = data.get("by_arm")
        if isinstance(rows, list) and rows and isinstance(by_arm, list) and not by_arm:
            # 26.10: в w2bud_matrix.py by_arm перечислял плечи жёстко ("colony","cell"),
            # и новое плечо pair не попадало в срез. Строки были, срез пустой — снаружи
            # это выглядело как «эффекта нет». Проверяем явно.
            bad.append(f"{agg.name}: строк {len(rows)}, но by_arm пуст — плечо не объявлено "
                       f"в списке агрегатора (жёсткий список плеч)")
            continue
        if not isinstance(rows, list) or rows:
            ok += 1
            continue
        stem = agg.name[: -len("_matrix.json")]
        dirs = source_dirs_for(stem)
        n_src = sum(len(list(d.glob("*.json"))) for d in dirs)
        if n_src:
            bad.append(f"{agg.name}: 0 строк, но в {dirs[0].name}/ лежит {n_src} файлов — "
                       f"проверьте шаблон имени и отбор строк (не «эффекта нет», а «данных не видно»)")
        else:
            ok += 1  # пусто и источника нет — это просто черновик

    print(f"[empty-agg] агрегатов со строками или без источника: {ok}")
    for b in bad:
        print(f"[empty-agg] ОШИБКА: {b}")
    if bad:
        return 1
    print("[empty-agg] OK — пустых агрегатов при живых данных нет")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
