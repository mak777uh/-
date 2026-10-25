#!/usr/bin/env python
"""w2bud_metric_variants.py — инвариантность эффекта к устройству метрики.

Зачем (внешняя критика 25.10): «решающим будет не обнаружение отбора в W2-bud, а
проверка того, что эффект не объясняется устройством метрик». Этот скрипт пересчитывает
два ключевых заявления на существующих артефактах ТРЕМЯ вариантами метрики каждый:

  A. w = споры / живые клетки   (основной)
     w = споры                  (сырое число)
     w = floor(споры / клетки)  (дискретизация)

  B. множество линий:  клеток >= 5 и спор >= 1  (основной)
                        клеток >= 3 и спор >= 1
                        все линии со спорами

  C. нуль-модель: rate = sum(споры)/sum(клетки)  (основной, консервативный)
                   rate = mean(споры/клетки)

Вердикт: заявление считается инвариантным, если ВСЕ комбинации дают один и тот же знак
(для отбора — I_obs > I_null(95 %) в >= 7/10 сидов; для цены — отрицательная медиана ρ).
Иначе печатается «зависит от определения» — и это публикуется как есть.

Запуск (из корня):  python scripts/w2bud_metric_variants.py
Выход:              reports/2026-10-25-w2bud-metric-variants.json (+ печать таблицы)
"""
from __future__ import annotations

import json
import math
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "reports" / "2026-10-25-w2bud-metric-variants.json"

W_VARIANTS = {
    "spores_per_cell": lambda spores, cells: spores / cells,
    "raw_spores": lambda spores, cells: float(spores),
    "floor_spores_per_cell": lambda spores, cells: float(math.floor(spores / cells)),
}
LINEAGE_SETS = {
    "cells_ge5_spores_ge1": lambda cells, spores: cells >= 5 and spores >= 1,
    "cells_ge3_spores_ge1": lambda cells, spores: cells >= 3 and spores >= 1,
    "all_with_spores": lambda cells, spores: spores >= 1,
}
NULL_RATES = ("sum_sum", "mean")


def crow(w: np.ndarray) -> float:
    if w.size < 2:
        return 0.0
    m = float(w.mean())
    if m <= 0:
        return 0.0
    return float(w.var() / (m * m))


def i_null_95(cells: np.ndarray, rate: float, draws: int = 2000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    lam = np.maximum(rate * cells, 1e-12)
    vals = np.empty(draws)
    for i in range(draws):
        x = rng.poisson(lam).astype(float)
        vals[i] = crow(x / np.maximum(cells, 1))
    return float(np.percentile(vals, 95))


def load_run(path: Path) -> tuple[dict, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("summary") or {}, data


def series(u_arm: str) -> list[dict]:
    out = []
    for f in sorted((POND / "w2bud3").glob(f"w2bud3_{u_arm}_seed*.json")):
        s, _ = load_run(f)
        cells_raw = {k[1:]: v for k, v in (s.get("type_counts") or {}).items()}
        spores_raw = s.get("lineage_spores") or {}
        traits_raw = {k[1:]: v for k, v in (s.get("type_traits") or {}).items()}
        cells_all = {k: float(v) for k, v in cells_raw.items()}
        spores_all = {k: float(spores_raw.get(k, 0)) for k in cells_all}
        traits = {k: float(traits_raw.get(k, 0.0)) for k in cells_all}
        out.append({"file": f.name, "cells": cells_all, "spores": spores_all, "traits": traits})
    return out


def evaluate(runs: list[dict], w_name: str, set_name: str, rate_name: str) -> dict:
    wf = W_VARIANTS[w_name]
    setf = LINEAGE_SETS[set_name]
    above, ratios, rhos = 0, [], []
    for i, run in enumerate(runs):
        keys = [k for k in run["cells"] if setf(run["cells"][k], run["spores"][k])]
        if len(keys) < 2:
            continue
        cells = np.array([run["cells"][k] for k in keys])
        spores = np.array([run["spores"][k] for k in keys])
        w = np.array([wf(sp, c) for sp, c in zip(spores, cells)], dtype=float)
        i_obs = crow(w)
        if rate_name == "sum_sum":
            rate = float(spores.sum() / max(cells.sum(), 1e-12))
        else:
            rate = float(np.mean(spores / np.maximum(cells, 1)))
        i_null = i_null_95(cells, rate, seed=i)
        ratios.append(i_obs / i_null if i_null > 0 else float("inf"))
        above += 1 if i_obs > i_null else 0
        # цена: rho(признак, w) по Спирмену
        tr = np.array([run["traits"][k] for k in keys])
        rhos.append(spearman(tr, w))
    return {
        "w": w_name, "lineages": set_name, "null_rate": rate_name,
        "seeds_scored": len(rhos), "i_above_null_k": above,
        "i_ratio_median": round(st.median(ratios), 3) if ratios else None,
        "rho_median": round(st.median(rhos), 3) if rhos else None,
        "rho_negative_k": sum(1 for r in rhos if r < 0),
    }


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    def rank(v: np.ndarray) -> np.ndarray:
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    rx -= rx.mean(); ry -= ry.mean()
    den = math.sqrt(float((rx ** 2).sum()) * float((ry ** 2).sum()))
    return float((rx * ry).sum() / den) if den else 0.0


def main() -> int:
    runs = series("cell")
    if len(runs) < 3:
        print("нет артефактов w2bud3_cell — нечего проверять")
        return 1
    rows = [evaluate(runs, w, ls, rn) for w in W_VARIANTS for ls in LINEAGE_SETS for rn in NULL_RATES]

    print(f"{'w':22s} {'линии':22s} {'нуль':8s} {'I>null':>7s} {'I_ratio':>8s} {'rho мед':>8s} {'rho<0':>6s}")
    for r in rows:
        print(f"{r['w']:22s} {r['lineages']:22s} {r['null_rate']:8s} "
              f"{r['i_above_null_k']:>3d}/{r['seeds_scored']:<3d} {str(r['i_ratio_median']):>8s} "
              f"{str(r['rho_median']):>8s} {r['rho_negative_k']:>6d}")

    i_ok = {r["i_above_null_k"] >= 7 for r in rows}
    i_ratios = [r["i_ratio_median"] for r in rows if r["i_ratio_median"] not in (None, float("inf"))]
    rho_signs = {(r["rho_median"] or 0) < 0 for r in rows}
    verdict = {
        "i_above_null_in_all_variants": all(i_ok),
        "i_ratio_median_range": [min(i_ratios), max(i_ratios)] if i_ratios else None,
        "rho_sign_invariant": len(rho_signs) == 1,
        "rho_negative_share": sum(1 for r in rows if (r["rho_median"] or 0) < 0) / len(rows),
        "variants": rows,
        "note": ("инвариантно, если все комбинации дают один знак; иначе публикуется как "
                 "«эффект зависит от определения», а не выбирается удобный вариант"),
    }
    print("\nвердикт:")
    print(f"  I_obs > I_null(95 %) в >=7/10 сидов — во всех вариантах: {verdict['i_above_null_in_all_variants']}")
    print(f"  диапазон медианы I_ratio: {verdict['i_ratio_median_range']}")
    print(f"  знак rho одинаков во всех вариантах: {verdict['rho_sign_invariant']} "
          f"(отрицательных медиан: {verdict['rho_negative_share']:.0%})")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\nзаписано: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
