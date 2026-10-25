#!/usr/bin/env python
"""metrics_registry.py — величины агрегатов обязаны быть объявлены с формулой и знаменателем.

Зачем (25.10, слой 1): сегодняшние потери были не арифметическими, а семантическими —
«подмена знаменателя» (9/10 против 2/10) и «величина, равная своей же формуле».
Определения жили в переписке. Теперь они живут в `lab/metrics.json`, и проверка ниже
делает две вещи машинно:

1. **Каждая величина**, которую агрегат выдаёт в `by_arm` / `criteria`, обязана быть
   объявлена (или стоять в переходном списке `undeclared_ok`, который обязан сокращаться).
2. **Имя величины обязано говорить о знаменателе**: если имя кончается на `_all` или
   `_valid`, поле `denominator` должно быть `all` / `valid` соответственно. Это правило
   §3c AGENTS.md, которое раньше держалось на дисциплине.
3. **Монотонное по построению** обязано иметь `derived_by_construction: true` и записанную
   `formula` — иначе величина выдаёт себя за свидетельство.

Запуск (из корня):

    python scripts/metrics_registry.py --check      # проверка (CI)
    python scripts/metrics_registry.py --list       # таблица величин
    python scripts/metrics_registry.py --todo       # что осталось объявить
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "lab" / "metrics.json"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# агрегаты, у которых проверяются ключи by_arm и criteria
SOURCES = [
    "w2bud_matrix.json",
    "w2bud2_matrix.json",
    "w2bud3_matrix.json",
    "v8_matrix.json",
    "merge_keep_matrix.json",
    "founding_matrix.json",
]

SKIP_KEYS = {"arm", "placement", "merge_rule", "kind", "experiment", "metric", "note"}


def numeric_keys(node) -> set[str]:
    """Скалярные ключи строки агрегата (числа и bool), без служебных подписей."""
    if not isinstance(node, dict):
        return set()
    out = set()
    for k, v in node.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, (int, float, bool)) and not isinstance(v, str):
            out.add(k)
    return out


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def check(registry_path: Path | None = None, quiet: bool = False) -> int:
    reg = json.loads((registry_path or REGISTRY).read_text(encoding="utf-8"))
    metrics: dict = reg["metrics"]
    allowed: dict = reg.get("undeclared_ok", {}).get("by_aggregate", {})
    verdicts: dict = reg.get("verdicts", {})
    problems: list[str] = []
    todo: dict[str, list[str]] = {}
    seen_keys = 0

    # --- правило 2: знаменатель в имени -------------------------------------------------
    for name, meta in metrics.items():
        if not meta.get("definition"):
            problems.append(f"{name}: нет definition")
        denom = meta.get("denominator")
        if not denom:
            problems.append(f"{name}: нет denominator")
        for suffix, expected in (("_all", "all"), ("_valid", "valid")):
            if name.endswith(suffix) and denom != expected:
                problems.append(
                    f"{name}: имя требует denominator='{expected}', а стоит '{denom}'"
                )
        # --- правило 3: тавтология обязана быть помечена и объяснена ----------------
        if meta.get("derived_by_construction") and not meta.get("formula"):
            problems.append(f"{name}: derived_by_construction без formula")

    # --- правило 1: каждая величина агрегата объявлена ---------------------------------
    for agg_name in SOURCES:
        path = POND / agg_name
        if not path.exists():
            continue
        agg = json.loads(path.read_text(encoding="utf-8"))
        keys: set[str] = set()
        for field in ("by_arm", "by_n"):
            for row in agg.get(field, []) or []:
                keys |= numeric_keys(row)
        # criteria — вердикты (bool), а не измерения: у них отдельное правило
        verdict_keys = set((agg.get("criteria") or {}).keys())
        seen_keys += len(keys)
        declared = set(metrics)
        allowed_here = set(allowed.get(agg_name, []))
        missing = sorted(keys - declared - allowed_here)
        if missing:
            todo[agg_name] = missing
            problems.append(
                f"{agg_name}: не объявлены и не в переходном списке: {', '.join(missing)}"
            )
        verdict_keys = {k for k in verdict_keys if k != "note"}
        undeclared_verdicts = sorted(verdict_keys - set(verdicts) - allowed_here)
        if undeclared_verdicts:
            problems.append(
                f"{agg_name}: вердикты не объявлены в verdicts: {', '.join(undeclared_verdicts)}"
            )
        for k, v in (agg.get("criteria") or {}).items():
            if k == "note" or k not in verdicts:
                continue
            kind = verdicts[k].get("kind", "bool")
            if v is None and verdicts[k].get("nullable"):
                continue
            ok = (isinstance(v, bool) if kind == "bool"
                  else isinstance(v, str) if kind == "label"
                  else isinstance(v, (int, float)) if kind == "number"
                  else isinstance(v, (dict, list)))
            if not ok:
                problems.append(
                    f"{agg_name}: criteria[{k}] объявлен как {kind}, а значение "
                    f"{type(v).__name__}"
                )
        stale = sorted(allowed_here - keys)
        if stale:
            problems.append(
                f"{agg_name}: переходный список содержит лишнее (величин уже нет): {', '.join(stale)}"
            )

    if not quiet:
        print(f"[metrics] величин: {len(metrics)}, вердиктов: {len(verdicts)}, ключей в агрегатах: {seen_keys}, "
              f"агрегатов проверено: {sum(1 for a in SOURCES if (POND / a).exists())}")
        for name, meta in sorted(metrics.items()):
            mark = " (по построению)" if meta.get("derived_by_construction") else ""
            print(f"[metrics]   {name}{mark} — {meta.get('definition', '')[:70]}")
    if todo:
        print(f"[metrics] осталось объявить: {sum(len(v) for v in todo.values())} "
              f"в {len(todo)} агрегатах")
    if problems:
        for p in problems:
            print(f"[metrics] ОШИБКА: {p}")
        return 1
    if not quiet:
        print("[metrics] OK — все величины объявлены, знаменатели и пометки согласованы")
    return 0


def list_metrics() -> int:
    reg = load_registry()
    metrics = reg["metrics"]
    width = max((len(k) for k in metrics), default=10)
    for name, meta in sorted(metrics.items()):
        flag = "!" if meta.get("derived_by_construction") else " "
        print(f"{flag} {name:<{width}} | {meta.get('denominator', '?'):<11} | "
              f"{meta.get('definition', '')[:80]}")
    print(f"\nвсего: {len(metrics)}  («!» — монотонно по построению, не свидетельство)")
    return 0


def todo() -> int:
    reg = load_registry()
    allowed = reg.get("undeclared_ok", {}).get("by_aggregate", {})
    total = sum(len(v) for v in allowed.values())
    for agg, names in sorted(allowed.items()):
        print(f"{agg}: {', '.join(sorted(names))}")
    print(f"\nпереходный список: {total} величин")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="реестр величин и их определений")
    ap.add_argument("--check", action="store_true", help="проверить (по умолчанию)")
    ap.add_argument("--list", action="store_true", help="таблица величин")
    ap.add_argument("--todo", action="store_true", help="что осталось объявить")
    ap.add_argument("--registry", default=None, help="путь к реестру (по умолчанию lab/metrics.json)")
    args = ap.parse_args(argv)
    if args.list:
        return list_metrics()
    if args.todo:
        return todo()
    return check(Path(args.registry) if args.registry else None)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
