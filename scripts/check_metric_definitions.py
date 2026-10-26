#!/usr/bin/env python
"""check_metric_definitions.py — реализация метрики обязана совпадать с её определением.

Зачем (26.10): в `w2bud_matrix.py` «частная корреляция Спирмена» считалась как
«линейно исключить z из СЫРЫХ значений, затем Спирмен по остаткам». Это не частная
корреляция Спирмена (стандарт: ранги → исключить z → корреляция остатков) и не частный
Пирсон — гибрид. Числа расходились с определением на 0.2–0.5, а вердикт «цена измерима»
держался на них.

Скрипт пересчитывает `rho_partial` по СТАНДАРТНОМУ определению прямо из сырых артефактов
и сравнивает со значением, записанным в агрегате. Расхождение > `--tol` — сигнал, что
реализация и определение разошлись.

Запуск:
    python scripts/check_metric_definitions.py                # проверить все агрегаты с этим полем
    python scripts/check_metric_definitions.py --strict       # код 1 при расхождениях
    python scripts/check_metric_definitions.py --series onebud
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# серия → (маска артефактов, агрегат)
SERIES = {
    "w2bud3": ("w2bud3/w2bud3_cell_seed*.json", "w2bud3_matrix.json"),
    "w2bud4s": ("w2bud4s/w2bud4s_cell_seed*.json", "w2bud4s_matrix.json"),
    "w2budd2": ("w2budd2/w2budd2_cell_seed*.json", "w2budd2_matrix.json"),
    "w2budd2_rep": ("w2budd2_rep/w2budd2_rep_n3_cell_seed*.json", "w2budd2_rep_matrix.json"),
    "w2bud_onebud": ("w2bud_onebud/w2bud_onebud_cell_seed*.json", "w2bud_onebud_matrix.json"),
}


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def _resid(a: list[float], b: list[float]) -> list[float]:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sbb = sum((v - mb) ** 2 for v in b)
    if sbb <= 0:
        return [v - ma for v in a]
    beta = sum((u - ma) * (v - mb) for u, v in zip(a, b)) / sbb
    return [u - ma - beta * (v - mb) for u, v in zip(a, b)]


def pearson(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    syy = sum((v - my) ** 2 for v in y)
    if sxx <= 0 or syy <= 0:
        # Вырожденный прогон: частная корреляция не определена. Это НЕ ноль —
        # считать его нулём значит молча сдвигать медиану (поймано 26.10).
        return None
    return sum((u - mx) * (v - my) for u, v in zip(x, y)) / (sxx * syy) ** 0.5


def rho_partial_standard(x, y, z) -> float | None:
    """СТАНДАРТ: ранги → исключить z из рангов → корреляция остатков."""
    rx, ry, rz = ranks(x), ranks(y), ranks(z)
    return pearson(_resid(rx, rz), _resid(ry, rz))


def rho_partial_hybrid(x, y, z) -> float | None:
    """То, что раньше было в агрегаторе: исключить z из сырых значений, затем ранги остатков."""
    rx, ry = ranks(_resid(x, z)), ranks(_resid(y, z))
    return pearson(rx, ry)


def per_run(pattern: str, kind: str = "standard") -> dict[int, float]:
    out: dict[int, float] = {}
    for f in sorted(glob.glob(str(POND / pattern))):
        seed = int(f.split("seed")[-1].split(".")[0])
        s = (json.loads(Path(f).read_text(encoding="utf-8")) or {}).get("summary") or {}
        cells = {k[1:]: float(v) for k, v in (s.get("type_counts") or {}).items()}
        spores = {k: float((s.get("lineage_spores") or {}).get(k, 0)) for k in cells}
        traits = {k: float((s.get("type_traits") or {}).get(f"T{k}", 0.0)) for k in cells}
        steps = {k: float((s.get("lineage_cell_steps") or {}).get(k, 0)) for k in cells}
        em = {str(k): float(v) for k, v in (s.get("lineage_energy_mean_sum") or {}).items()}
        es = {str(k): int(v) for k, v in (s.get("lineage_energy_samples") or {}).items()}
        ept = {k: em[k] / es[k] for k in em if es.get(k)}
        keys = [k for k in cells if cells[k] >= 5 and spores.get(k, 0) >= 1
                and k in ept and k in steps and steps[k] > 0]
        if len(keys) < 4:
            continue
        x = [traits[k] for k in keys]
        y = [steps[k] for k in keys]
        z = [ept[k] for k in keys]
        value = rho_partial_standard(x, y, z) if kind == "standard" else rho_partial_hybrid(x, y, z)
        if value is not None:
            out[seed] = value
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="реализация метрики против её определения")
    ap.add_argument("--tol", type=float, default=0.05, help="допустимое расхождение (по умолчанию 0.05)")
    ap.add_argument("--strict", action="store_true", help="код 1 при расхождениях")
    ap.add_argument("--series", help="только одна серия")
    args = ap.parse_args(argv)

    problems, checked = [], 0
    names = [args.series] if args.series else list(SERIES)
    for name in names:
        if name not in SERIES:
            print(f"[metric-def] неизвестная серия: {name}")
            return 1
        pattern, agg_name = SERIES[name]
        agg_path = POND / agg_name
        if not agg_path.exists():
            continue
        agg = json.loads(agg_path.read_text(encoding="utf-8"))
        stored = {r["seed"]: r.get("rho_partial_energy") for r in agg.get("rows", [])
                  if r.get("arm") == "cell" and r.get("rho_partial_energy") is not None}
        if not stored:
            continue
        mine = per_run(pattern)
        checked += 1
        bad = [(seed, stored[seed], mine[seed]) for seed in sorted(stored)
               if seed in mine and abs(stored[seed] - mine[seed]) > args.tol]
        med_stored = st.median(list(stored.values()))
        med_mine = st.median(list(mine.values())) if mine else float("nan")
        flag = "✗" if bad else "✓"
        q1, q3 = (st.quantiles(list(mine.values()), n=4)[0], st.quantiles(list(mine.values()), n=4)[2]) \
            if len(mine) >= 4 else (float("nan"), float("nan"))
        print(f"{flag} {name}: n(агрегат)={len(stored)}, n(стандарт)={len(mine)}, расхождений > {args.tol}: {len(bad)}; "
              f"медиана {med_stored:.3f} → {med_mine:.3f}; Q1–Q3 {q1:.2f}…{q3:.2f}")
        for seed, a, b in bad[:4]:
            print(f"    сид {seed}: агрегат {a:+.3f} против стандарта {b:+.3f}")
        if bad:
            problems.append(f"{name}: {len(bad)} прогонов расходятся с определением")

    if not checked:
        print("[metric-def] нечего проверять (нет агрегатов с ρ_partial)")
        return 0
    if problems:
        for p in problems:
            print(f"[metric-def] ОШИБКА: {p}")
        print("[metric-def] реализация и определение разошлись — правьте агрегатор, а не определение")
        return 1 if args.strict else 0
    print("[metric-def] OK — реализация совпадает с определением в пределах допуска")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
