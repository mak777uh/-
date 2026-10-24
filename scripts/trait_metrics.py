#!/usr/bin/env python
"""trait_metrics.py — метрики условия B по артефактам серии (производственный путь).

Зачем: результаты серии B (мутация метки линии) должны проверяться машинно и по тем
же определениям, что у библиотеки. Библиотека сделала независимую реализацию
(`library/tools/trait_metrics.py` + `library/conditions-B-criteria.md`); здесь —
вторая, и тест `tests/test_trait_metrics.py` требует, чтобы обе давали ОДНИ числа на
одних fixtures. Расхождение определений — баг, а не «два мнения».

Определения (совпадают с `library/conditions-B-criteria.md`):

* **Shannon** `H = -Σ p_i ln p_i` по `type_counts` шага; отчёт — медиана и
  первая/последняя точка серии;
* **поток новизны** — число меток, впервые появившихся и проживших ≥ 50 шагов
  (окно в единицах серии, серия пишется каждые 5 шагов);
* **дифференциальное воспроизводство** — Спирмен(признак метки, число рождений);
  без `type_traits` метрика не считается (это «нет данных», а не «нет отбора»);
* если поля нет — `valid: false` с причиной, **не** ноль.

Запуск (из корня):

    python scripts/trait_metrics.py --src morphogenesis/experiments/E09_pond --glob "mut_*.json"
    python scripts/trait_metrics.py --src ... --glob "mut_*.json" --json mutation_metrics.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOVELTY_WINDOW = 50


def shannon(counts: dict) -> float:
    """Энтропия по счётчикам (натуральный логарифм)."""
    total = sum(v for v in counts.values() if v > 0)
    if total <= 0:
        return 0.0
    h = 0.0
    for value in counts.values():
        if value > 0:
            p = value / total
            h -= p * math.log(p)
    return h


def series_from(data: dict) -> list[dict] | None:
    """Достать серию счётчиков по шагам в виде [{метка: клеток}, ...]."""
    for holder in (data, data.get("summary") or {}):
        for key in ("type_counts_series", "types_series", "type_counts_steps"):
            rows = holder.get(key)
            if isinstance(rows, list):
                out = []
                for row in rows:
                    if isinstance(row, dict):
                        out.append(row.get("counts", row.get("type_counts", row)))
                    else:
                        out.append({})
                return out
    return None


def births_from(data: dict) -> dict:
    """Суммарные рождения по меткам (поле может быть и по шагам)."""
    out: dict[str, float] = {}
    for holder in (data, data.get("summary") or {}):
        value = holder.get("births_by_type")
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, (int, float)):
                    out[key] = out.get(key, 0.0) + float(item)
                elif isinstance(item, dict):
                    out[key] = out.get(key, 0.0) + sum(
                        float(v) for v in item.values() if isinstance(v, (int, float))
                    )
    return out


def traits_from(data: dict) -> dict:
    for holder in (data, data.get("summary") or {}):
        if isinstance(holder.get("type_traits"), dict):
            return holder["type_traits"]
    return {}


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    """Спирмен с поправкой на равные ранги; меньше 3 пар — None (не считаем)."""
    n = len(pairs)
    if n < 3:
        return None

    def ranks(values: list[float]) -> list[float]:
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

    xs = ranks([float(p[0]) for p in pairs])
    ys = ranks([float(p[1]) for p in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return (num / den) if den else None


def sampling_interval(data: dict) -> int:
    """Шаг между строками серии в единицах времени (1, если шаг не записан).

    Серия условия B пишется каждые 5 шагов, а окно новизны задано в ШАГАХ (50), поэтому
    окно в строках = 50 / интервал. На fixtures библиотеки строки идут по шагам
    (интервал 1), и обе реализации считают одинаково.
    """
    for holder in (data, data.get("summary") or {}):
        for key in ("type_counts_series", "types_series", "type_counts_steps"):
            rows = holder.get(key)
            if isinstance(rows, list) and len(rows) >= 2:
                steps = [row.get("step") for row in rows if isinstance(row, dict)]
                steps = [int(s) for s in steps if isinstance(s, (int, float))]
                if len(steps) >= 2:
                    diffs = sorted(b - a for a, b in zip(steps, steps[1:]) if b > a)
                    if diffs:
                        return max(1, int(diffs[len(diffs) // 2]))
    return 1


def analyse(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    res: dict = {"artifact": path.name, "valid": True, "invalid_reason": None}
    series = series_from(data)
    if not series:
        res.update(valid=False,
                   invalid_reason="нет type_counts_series (поле не логировалось)")
        return res
    res["steps"] = len(series)
    hs = [shannon(step) for step in series]
    res["shannon_median"] = round(sorted(hs)[len(hs) // 2], 4)
    res["shannon_first"] = round(hs[0], 4)
    res["shannon_last"] = round(hs[-1], 4)
    # медиана за вторую половину серии — описательное уточнение «окна» (спецификация
    # говорит «медиана H за окно и тренд»); критерий при этом остаётся за всей серией
    tail = hs[len(hs) // 2:]
    res["shannon_second_half_median"] = round(sorted(tail)[len(tail) // 2], 4) if tail else None

    first_seen: dict[str, int] = {}
    last_seen: dict[str, int] = {}
    for idx, step in enumerate(series):
        for key, value in step.items():
            if isinstance(value, (int, float)) and value > 0:
                first_seen.setdefault(key, idx)
                last_seen[key] = idx
    interval = sampling_interval(data)
    window_rows = max(1, math.ceil(NOVELTY_WINDOW / interval))
    # Предковые метки (присутствуют в первой строке) — НЕ новизна: иначе при m=0
    # novelty = 1, и контроль «при m=0 новизна строго 0» (criteria §3, п.4) ломается.
    ancestral = {k for k, v in (series[0] or {}).items()
                 if isinstance(v, (int, float)) and v > 0}
    novelty = [k for k, start in first_seen.items()
               if k not in ancestral and last_seen[k] - start >= window_rows]
    res["types_total"] = len(first_seen)
    res["novelty_ancestral_excluded"] = sorted(ancestral)
    res["novelty_flux"] = len(novelty)
    res["novelty_window_steps"] = NOVELTY_WINDOW
    res["novelty_window_rows"] = window_rows
    res["series_interval_steps"] = interval

    births = births_from(data)
    traits = traits_from(data)
    if births and traits:
        pairs = [(float(traits[k]), float(births[k])) for k in traits if k in births]
        rho = spearman(pairs)
        res["spearman_trait_births"] = round(rho, 3) if rho is not None else None
        if rho is None:
            res["spearman_reason"] = "меньше 3 меток с признаком и рождениями"
    else:
        res["spearman_trait_births"] = None
        res["spearman_reason"] = "нужны births_by_type и type_traits"
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default=str(REPO / "morphogenesis" / "experiments" / "E09_pond"))
    ap.add_argument("--glob", default="*.json")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    results = [analyse(Path(f)) for f in files]
    usable = [r for r in results if r["valid"]]
    print(f"артефактов: {len(results)} | с данными: {len(usable)}")
    for res in results[:20]:
        if res["valid"]:
            print(f"  {res['artifact'][:46]:46} H_med={res['shannon_median']:.3f} "
                  f"novelty={res['novelty_flux']} rho={res['spearman_trait_births']}")
        else:
            print(f"  {res['artifact'][:46]:46} invalid: {res['invalid_reason']}")
    payload = {
        "files": len(results),
        "usable": len(usable),
        "novelty_window": NOVELTY_WINDOW,
        "shannon_median_range": (
            [min(r["shannon_median"] for r in usable),
             max(r["shannon_median"] for r in usable)] if usable else None),
        "novelty_total": sum(r["novelty_flux"] for r in usable),
        "results": results,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        print(f"записано: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
