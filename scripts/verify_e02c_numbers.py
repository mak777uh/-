#!/usr/bin/env python
"""Пересчёт опубликованных чисел E02c из артефактов, лежащих в репозитории.

Зачем: числа в отчётах и рукописи должны пересчитываться на **чужой машине**, а
не только на той, где считались. Скрипт берёт `census_*.json` (сырые строки: класс
каждого старта) и парную `summary_*.json`, независимо пересчитывает распределение
классов и число «устойчивых struct_2» по правилу протокола (устойчивость
последней четверти ≥ 0.80) и падает, если сводка расходится с сырыми данными.

Это не проверка научного вывода, а проверка арифметики: «сводка честно
описывает то, что лежит в артефакте».

Запуск (из корня репозитория):

    python scripts/verify_e02c_numbers.py          # все переписи в каталоге
    python scripts/verify_e02c_numbers.py --strict # падать, если нет сводки

Код выхода: 0 — всё сошлось, 1 — есть расхождения или пропавшие артефакты.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02c_replication"
STABILITY_MIN = 0.80


def pairs() -> list[tuple[str, Path, Path]]:
    """Все пары (census, summary) в каталоге переписей E02c."""
    found: list[tuple[str, Path, Path]] = []
    if not EXP.is_dir():
        return found
    for census in sorted(EXP.glob("census_*.json")):
        stem = census.stem[len("census_"):]
        summary = EXP / f"summary_{stem}.json"
        found.append((stem, census, summary))
    return found


def recount(runs: list[dict]) -> dict[str, dict]:
    """Пересчёт по сырым строкам: классы и устойчивые struct_2 на семейство."""
    out: dict[str, dict] = {}
    for family in sorted({row.get("family") for row in runs}):
        rows = [row for row in runs if row.get("family") == family]
        counts = collections.Counter(row.get("frozen_class") for row in rows)
        stable_frozen = sum(
            1
            for row in rows
            if row.get("frozen_class") == "struct_2"
            and (row.get("stability_frozen_last_quarter") or 0.0) >= STABILITY_MIN
        )
        stable_fit = sum(
            1
            for row in rows
            if row.get("frozen_class") == "struct_2"
            and (row.get("stability_last_quarter") or 0.0) >= STABILITY_MIN
        )
        out[family] = {
            "n": len(rows),
            "classes": dict(counts),
            "stable_frozen": stable_frozen,
            "stable_fit": stable_fit,
        }
    return out


def check_one(stem: str, census: Path, summary: Path, strict: bool) -> tuple[int, int]:
    problems = 0
    checked = 0
    try:
        runs = json.loads(census.read_text(encoding="utf-8")).get("runs", [])
    except (OSError, ValueError) as exc:
        print(f"[{stem}] НЕ ЧИТАЕТСЯ census: {exc}")
        return 1, 0
    if not summary.exists():
        msg = f"[{stem}] нет сводки {summary.name}"
        print(msg + (" (строгий режим — ошибка)" if strict else " — пропуск"))
        return (1 if strict else 0), 0
    try:
        stats = json.loads(summary.read_text(encoding="utf-8")).get("stats", {})
    except (OSError, ValueError) as exc:
        print(f"[{stem}] НЕ ЧИТАЕТСЯ summary: {exc}")
        return 1, 0

    print(f"[{stem}] сырых строк: {len(runs)}")
    for family, found in recount(runs).items():
        claimed = stats.get(family)
        if not claimed:
            print(f"  {family}: n={found['n']} — в сводке строки нет (контроль или вне stats)")
            continue
        checked += 1
        ok_n = claimed.get("n") == found["n"]
        ok_cls = claimed.get("frozen_class_counts") == found["classes"]
        # Исторические сводки (до появления замороженной метрики) хранят
        # fit-относительную устойчивость в struct_2_stable; новые — frozen.
        if "struct_2_stable_frozen" in claimed:
            metric, expected, got = "frozen", found["stable_frozen"], claimed["struct_2_stable_frozen"]
        else:
            metric, expected, got = "fit", found["stable_fit"], claimed.get("struct_2_stable")
        ok_st = got == expected
        status = "OK" if (ok_n and ok_cls and ok_st) else "РАСХОЖДЕНИЕ"
        print(
            f"  {family}: n={found['n']} классы={found['classes']} "
            f"устойчивых({metric})={expected} -> {status}"
        )
        if status != "OK":
            problems += 1
            print(
                "    сводка: "
                f"n={claimed.get('n')}, классы={claimed.get('frozen_class_counts')}, "
                f"устойчивых({metric})={got}"
            )
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="отсутствие сводки — ошибка")
    args = ap.parse_args(argv)

    targets = pairs()
    if not targets:
        print(f"нет ни одной пары census/summary в {EXP}")
        return 1

    problems = 0
    checked = 0
    for stem, census, summary in targets:
        p, c = check_one(stem, census, summary, args.strict)
        problems += p
        checked += c

    if problems:
        print(f"ИТОГ: расхождений {problems} (семейств сверено {checked})")
        return 1
    print(f"ИТОГ: все числа сходятся с артефактами (семейств сверено {checked})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
