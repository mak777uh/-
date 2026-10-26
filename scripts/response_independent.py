"""Отклик признака, проверенный величиной, независимой от `w`.

Зачем: вывод «отклик не заявляется» держался на двух блокерах — мало линий и не пройденный гейт
манипуляции. Но оба блокера — про **определение** `w` (споры / клетки). Здесь отклик пересчитывается
величиной, которая не использует ни споры, ни `w`:

    скорость = births_by_type[t] / lineage_cell_steps[t]   (рождения линии на её клетко-шаги)

и сравнивается с `rho(признак, w)`. Если знаки совпадают — кажущаяся связь на `w` не артефакт
определения. Если нет — отклик на `w` есть свойство определения.

Метод подписан (AGENTS §3c): **чистый Спирмен** (ранги по линиям, средние ранги при совпадениях),
**без контроля энергии**; фильтр линий: `cells >= 5` и `cell_steps > 0` (гейт по спорам в этой серии
инертен — проверено); знаменатель величины — клетко-шаги.
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "w2bud_onebud"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "analysis" / "response_independent.json"
MIN_CELLS = 5


def rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def pearson(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sxx * syy) ** 0.5


def spearman(x: list[float], y: list[float]) -> float | None:
    return pearson(rank(x), rank(y))


def main(argv: list[str] | None = None) -> int:
    rows: list[dict] = []
    for path in sorted(SRC.glob("w2bud_onebud_cell_seed*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary") or {}
        cells = {str(k).lstrip("T"): float(v) for k, v in (summary.get("type_counts") or {}).items()}
        births = {str(k).lstrip("T"): float(v) for k, v in (summary.get("births_by_type") or {}).items()}
        spores = {str(k).lstrip("T"): float(v) for k, v in (summary.get("lineage_spores") or {}).items()}
        steps = {str(k).lstrip("T"): float(v) for k, v in (summary.get("lineage_cell_steps") or {}).items()}
        traits = {k: float((summary.get("type_traits") or {}).get(f"T{k}", 0.0)) for k in cells}
        keys = [k for k in cells if cells[k] >= MIN_CELLS and steps.get(k, 0) > 0 and k in births]
        if len(keys) < 3:
            continue
        rate = [births[k] / steps[k] for k in keys]
        trait = [traits[k] for k in keys]
        w = [spores.get(k, 0.0) / cells[k] for k in keys]
        r_rate = spearman(trait, rate)
        r_w = spearman(trait, w)
        if r_rate is None:
            continue
        rows.append({
            "seed": int(path.stem.split("seed")[-1]),
            "lines": len(keys),
            "rho_trait_birth_rate": round(r_rate, 4),
            "rho_trait_w": round(r_w, 4) if r_w is not None else None,
            "sign_match": (r_w is not None and (r_rate > 0) == (r_w > 0)),
        })
    if not rows:
        print("[response] нет пригодных прогонов")
        return 1
    rates = [r["rho_trait_birth_rate"] for r in rows]
    ws = [r["rho_trait_w"] for r in rows if r["rho_trait_w"] is not None]
    out = {
        "metric": {
            "quantity": "births_by_type / lineage_cell_steps (рождения линии на её клетко-шаги)",
            "coefficient": "чистый Спирмен, без контроля энергии",
            "line_filter": f"cells >= {MIN_CELLS} и cell_steps > 0",
            "denominator": "клетко-шаги линии",
            "does_not_use": ["spores", "w"],
        },
        "note": ("Проверка «отклик не заявляется» величиной, независимой от определения w. "
                 "Совпадение знака с rho(признак, w) считалось по тем же прогонам."),
        "response_independent_median": round(st.median(rates), 4),
        "independent_positive": sum(1 for r in rates if r > 0),
        "runs": len(rows),
        "quartiles": [round(q, 4) for q in st.quantiles(rates, n=4)] if len(rates) >= 4 else None,
        "w_median": round(st.median(ws), 4) if ws else None,
        "w_positive": sum(1 for x in ws if x > 0),
        "sign_match": sum(1 for r in rows if r["sign_match"]),
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"записано: {OUT.relative_to(ROOT)}")
    print(f"  медиана независимой величины: {out['response_independent_median']} "
          f"| положительных: {out['independent_positive']}/{out['runs']}")
    print(f"  rho(признак, w): {out['w_median']} | положительных: {out['w_positive']}/{out['runs']}")
    print(f"  совпадение знака: {out['sign_match']}/{out['runs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
