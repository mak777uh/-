#!/usr/bin/env python
"""Метрики условия B (изменчивость): разнообразие, поток новизны, дифференциальное воспроизводство.

Читает артефакты серии и считает по данным, ничего не додумывая. Если поля нет — пишет
`invalid` с причиной, а не ноль.

Ожидаемые поля в артефакте (см. library/metrics-spec.md):
  * `type_counts_series` — список {шаг: {тип: клеток}} (или `summary.type_counts_series`);
  * `births_by_type` — {тип: делений} (или по шагам, тогда суммируется);
  * `type_traits` — {тип: число} для дифференциального воспроизводства (без него метрика
    помечается как невычислимая).

Запуск:
  python library/tools/trait_metrics.py --src morphogenesis/experiments/E09_pond --glob "mut_*.json"
  python library/tools/trait_metrics.py --src ... --json out.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

NOVELTY_WINDOW = 50  # тип считается новизной, если прожил >= стольких шагов


def shannon(counts: dict) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for value in counts.values():
        if value > 0:
            p = value / total
            h -= p * math.log(p)
    return h


def series_from(data: dict) -> list[dict] | None:
    for holder in (data, data.get("summary") or {}):
        for key in ("type_counts_series", "types_series", "type_counts_steps"):
            if isinstance(holder.get(key), list):
                return [row.get("type_counts", row) if isinstance(row, dict) else {} for row in holder[key]]
    return None


def births_from(data: dict) -> dict:
    out: dict[str, float] = {}
    for holder in (data, data.get("summary") or {}):
        value = holder.get("births_by_type")
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, (int, float)):
                    out[key] = out.get(key, 0) + float(item)
                elif isinstance(item, dict):  # по шагам
                    out[key] = out.get(key, 0) + sum(v for v in item.values() if isinstance(v, (int, float)))
    return out


def traits_from(data: dict) -> dict:
    for holder in (data, data.get("summary") or {}):
        if isinstance(holder.get("type_traits"), dict):
            return holder["type_traits"]
    return {}


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    n = len(pairs)
    if n < 3:
        return None

    def ranks(values):
        order = sorted(range(n), key=lambda i: values[i])
        result = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and values[order[j + 1]] == values[order[i]]:
                j += 1
            rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                result[order[k]] = rank
            i = j + 1
        return result

    xs = ranks([p[0] for p in pairs])
    ys = ranks([p[1] for p in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return (num / den) if den else None


def analyse(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    res = {"artifact": path.name, "valid": True, "invalid_reason": None}
    series = series_from(data)
    if not series:
        res.update(valid=False, invalid_reason="нет type_counts_series (поле не логировалось)")
        return res
    res["steps"] = len(series)
    hs = [shannon(step) for step in series]
    res["shannon_median"] = round(sorted(hs)[len(hs) // 2], 4)
    res["shannon_first"] = round(hs[0], 4)
    res["shannon_last"] = round(hs[-1], 4)

    first_seen: dict[str, int] = {}
    last_seen: dict[str, int] = {}
    for idx, step in enumerate(series):
        for key, value in step.items():
            if value and value > 0:
                first_seen.setdefault(key, idx)
                last_seen[key] = idx
    # предковые метки (присутствуют в первом срезе) новизной не являются:
    # иначе при m=0 инструмент даёт novelty>0 и не ловит ошибку логгера (критерий B, п.3)
    ancestral = {k for k, v in (series[0] or {}).items() if v and v > 0}
    novelty = [key for key, start in first_seen.items()
               if key not in ancestral and last_seen[key] - start >= NOVELTY_WINDOW]
    res["types_total"] = len(first_seen)
    res["novelty_flux"] = len(novelty)
    res["novelty_ancestral_excluded"] = sorted(ancestral)
    res["novelty_window"] = NOVELTY_WINDOW

    births = births_from(data)
    traits = traits_from(data)
    if births and traits:
        pairs = [(float(traits[key]), births[key]) for key in traits if key in births]
        res["spearman_trait_births"] = (round(spearman(pairs), 3) if spearman(pairs) is not None else None)
    else:
        res["spearman_trait_births"] = None
        res["spearman_reason"] = "нужны births_by_type и type_traits"
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="*.json")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    results = [analyse(Path(f)) for f in files]
    usable = [r for r in results if r["valid"]]
    print(f"артефактов: {len(results)} | с данными: {len(usable)}")
    for res in results[:12]:
        if res["valid"]:
            print(f"  {res['artifact'][:44]:44} H_med={res['shannon_median']:.3f} "
                  f"novelty={res['novelty_flux']} spearman={res['spearman_trait_births']}")
        else:
            print(f"  {res['artifact'][:44]:44} invalid: {res['invalid_reason']}")
    summary = {
        "files": len(results),
        "usable": len(usable),
        "shannon_median_range": (
            [min(r["shannon_median"] for r in usable), max(r["shannon_median"] for r in usable)]
            if usable else None),
        "novelty_total": sum(r["novelty_flux"] for r in usable),
        "results": results,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    return 0 if usable or not results else 1


if __name__ == "__main__":
    raise SystemExit(main())
