#!/usr/bin/env python
"""check_aggregate_coverage.py — каждый научный артефакт обязан входить хотя бы в один агрегат.

Зачем (26.10, третий раз за сутки один и тот же класс):
  1. `w2bud[a-z0-9]*` не пропускал подчёркивания → 20 живых прогонов выпали из агрегата;
  2. тот же шаблон в `metric_variants.py` → «0 вариантов» при живых данных;
  3. `w1niche[45]` не знал волну 6 → точный контроль соседства не попал в агрегат, а гейт
     «хвосты серий» ругался «агрегат старше артефакта» вместо «агрегат не видит файлов».

Все три раза ошибка была в шаблоне имени, и все три раза её находил человек. Проверка ниже
не знает шаблонов: она берёт все файлы с `summary` (то есть настоящие артефакты прогонов) и
смотрит, ссылается ли на них хоть один агрегат. Непокрытый артефакт — ошибка.

Запуск: python scripts/check_aggregate_coverage.py [--strict] [--limit N]
Код выхода 1 при непокрытых артефактах (только со `--strict`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# Файлы, которые артефактами прогонов не являются (служебные/сводные).
SKIP_NAMES = {
    "farm-status.json", "provenance-legacy.json", "census.json", "results.json",
    "class_centroids_frozen.json", "perturbations.json",
}


def aggregates() -> list[Path]:
    return sorted(POND.glob("*.json"))


def referenced(files: list[Path]) -> tuple[set[str], set[str]]:
    """Имена артефактов, на которые ссылаются агрегаты (по basename и по пути)."""
    names: set[str] = set()
    paths: set[str] = set()
    for agg in files:
        try:
            data = json.loads(agg.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data.get("rows")
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            art = row.get("artifact")
            if not isinstance(art, str):
                continue
            art = art.replace("\\", "/")
            names.add(Path(art).name)
            paths.add(art)
    return names, paths


def is_run_artifact(path: Path) -> bool:
    if path.name in SKIP_NAMES or path.name.endswith("_matrix.json"):
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return isinstance(data, dict) and isinstance(data.get("summary"), dict)


def family_key(path: Path) -> str:
    """Семейство прогонов: каталог + имя без номера сида.

    Одиночные пробы (диагностика, пилоты) агрегата не требуют — иначе гейт краснеет всегда
    и перестаёт читаться (правило §0.2). Сигнал — только СЕМЕЙСТВО из >=3 файлов без агрегата.
    """
    import re as _re
    name = _re.sub(r"_seed\d+$", "", path.stem)
    name = _re.sub(r"\d+$", "", name)
    return f"{path.parent.name}/{name}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="покрытие артефактов агрегатами")
    ap.add_argument("--strict", action="store_true", help="код 1 при непокрытых артефактах")
    ap.add_argument("--limit", type=int, default=12, help="сколько примеров печатать")
    args = ap.parse_args(argv)

    if not POND.exists():
        print("[coverage] каталога экспериментов нет — пропускаю")
        return 0

    aggs = aggregates()
    names, paths = referenced(aggs)
    if not names:
        print("[coverage] агрегатов со ссылками на артефакты нет — пропускаю")
        return 0

    artifacts, missing = 0, []
    for path in POND.rglob("*.json"):
        if not is_run_artifact(path):
            continue
        artifacts += 1
        rel = path.relative_to(ROOT).as_posix()
        if path.name in names or rel in paths:
            continue
        missing.append(rel)

    missing.sort()
    # реестр исключений: семейства, которым агрегат не положен (с причиной)
    exempt: dict[str, str] = {}
    ex_path = ROOT / "lab" / "coverage-exemptions.json"
    if ex_path.exists():
        try:
            exempt = (json.loads(ex_path.read_text(encoding="utf-8")) or {}).get("families") or {}
        except Exception:
            exempt = {}

    def is_exempt(rel: str) -> bool:
        return any(key and key in rel for key in exempt)

    missing = [m for m in missing if not is_exempt(m)]
    groups: dict[str, list[str]] = {}
    for rel in missing:
        groups.setdefault(family_key(Path(rel)), []).append(rel)
    families = {k: v for k, v in groups.items() if len(v) >= 3}
    singles = sum(len(v) for v in groups.values() if len(v) < 3)
    print(f"[coverage] агрегатов {len(aggs)}, артефактов {artifacts}, без агрегата: {len(missing)} "
          f"(из них одиночных проб, это норма: {singles})")
    if families:
        for key, rels in sorted(families.items(), key=lambda kv: -len(kv[1]))[: args.limit]:
            print(f"[coverage]   СЕРИЯ БЕЗ АГРЕГАТА {key}: {len(rels)} файлов, напр. {rels[0]}")
        print("[coverage] ОШИБКА: семейство из >=3 артефактов не входит ни в один агрегат — "
              "проверьте шаблон имени в агрегаторе")
        return 1 if args.strict else 0
    print("[coverage] OK — серий без агрегата нет (одиночные пробы не считаются)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
