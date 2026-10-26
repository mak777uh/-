"""Агрегат серии пилотов `w2bud_lines` — поиск маневра, дающего ≥12 линий с данными.

Зачем отдельный агрегатор: серия — не проверка гипотезы, а **поиск конструкции**. Каждый пилот меняет
один параметр (`steps`, `grid`, `mutation_trait_sigma`, `eps`, число стартовых компонент), поэтому
сравнивать надо не «плечи», а **пары «маневр → число линий»**. Ровно эту таблицу и собирает скрипт:
она — доказательство утверждения «конструкция W2-bud не даёт ≥12 линий, поэтому цена остаётся
направлением, а не величиной».

Пилоты — exploratory (по одному сиду): в вердикт не входят, входят только в описание конструкции.
"""

from __future__ import annotations

import json
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "w2bud_lines"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "w2bud_lines_matrix.json"
MIN_CELLS = 5


def norm(key: object) -> str:
    return str(key).lstrip("T")


def pilot_stats(path: Path) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    cfg = (data.get("config") or {}) | (summary.get("config") or {})
    cells = {norm(k): float(v) for k, v in (summary.get("type_counts") or {}).items()}
    spores = {norm(k): float(v) for k, v in (summary.get("lineage_spores") or {}).items()}
    steps = {norm(k): float(v) for k, v in (summary.get("lineage_cell_steps") or {}).items()}
    if not cells:
        return None
    lines = [k for k in cells if cells[k] >= MIN_CELLS and spores.get(k, 0) >= 1 and steps.get(k, 0) > 0]
    total = sum(cells.values()) or 1.0
    exposure = st.median([steps[k] for k in lines]) if lines else None
    return {
        "artifact": str(path.relative_to(ROOT)).replace("\\", "/"),
        "params": {
            "steps": cfg.get("steps"),
            "width": cfg.get("width"),
            "mutation_trait_sigma": cfg.get("mutation_trait_sigma"),
            "eps": cfg.get("eps"),
            "start_components": cfg.get("components") or cfg.get("start_components") or cfg.get("n_components"),
        },
        "lineages_with_data": len(lines),
        "labels": len(cells),
        "top1_share": round(max(cells.values()) / total, 4),
        "cells_total": int(total),
        "median_cell_steps_per_line": exposure,
    }


def main(argv: list[str] | None = None) -> int:
    files = sorted(SRC.glob("pilot_*.json"))
    rows = [r for r in (pilot_stats(f) for f in files) if r]
    if not rows:
        print(f"[w2bud-lines] нет пилотов в {SRC}")
        return 1
    rows.sort(key=lambda r: (-r["lineages_with_data"], r["artifact"]))
    best = rows[0]
    out = {
        "metric": {
            "unit": "lineage с >= 5 клетками, >= 1 споры и cell_steps > 0",
            "lineages_with_data": "число линий, проходящих фильтр (по ним считается rho)",
            "top1_share": "доля клеток самой крупной линии от всех живых клеток",
            "median_cell_steps_per_line": "медиана клетко-шагов на линию — экспозиция, по которой считается связь",
        },
        "design_search": True,
        "exploratory": True,
        "note": (
            "Поиск маневра, дающего >= 12 линий на прогон (порог, при котором 95 % ДИ медианы rho перестаёт "
            "содержать -0.3). 14 пилотов по одному сиду: каждый меняет один параметр. Серия не запускалась: "
            "максимум 9 линий, причина — доминирующая линия занимает 69–90 % клеток, и чем длиннее прогон, "
            "тем сильнее вытеснение. В вердикт по цене не входит (он остаётся «знак твёрд, величина не "
            "определена»), входит в описание конструкции."
        ),
        "target_lines": 12,
        "best": {
            "artifact": best["artifact"],
            "lineages_with_data": best["lineages_with_data"],
            "params": best["params"],
        },
        "rows": rows,
        "criteria": {
            "target_met": best["lineages_with_data"] >= 12,
            "construction_allows_verdict": best["lineages_with_data"] >= 12,
            "best_lines": best["lineages_with_data"],
        },
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"записано: {OUT.relative_to(ROOT)} | пилотов: {len(rows)} | максимум линий: {best['lineages_with_data']}")
    for row in rows[:6]:
        print(f"  {row['artifact']:34s} линий={row['lineages_with_data']:2d} топ-1={row['top1_share']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
