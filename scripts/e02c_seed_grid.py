"""Собрать 2×2-сетку «инициализация × порядок данных» и применить критерий H-E02C-6.

Читает сводки переписей `summary_e02c_seeddec_*.json` и складывает клетки в
`seed_grid.json` рядом с переписями. Никаких GPU и новых измерений: только
сводки, которые уже посчитаны.

Клетка опознаётся **по имени семейства внутри сводки**
(`stats[*].family = E02c_seeddec_init<A>_data<B>`), а не по имени файла: первая
волна писала `summary_e02c_seeddec_A.json` / `_B.json`, и по файлу её клетки
потерялись бы. Именно они нужны критерию: A = (42, 101), B = (101, 42).

Критерий H-E02C-6 заморожен до переписей в
`reports/2026-10-22-e02c-seed-grid-plan.md`; здесь он применяется кодом, чтобы
вердикт не зависел от того, кто читает числа:

1. все измеренные клетки с init=101 дают `struct_1` >= 52/64 каждая;
2. среди измеренных клеток с init=42 есть минимум два разных доминирующих
   класса, и ни в одной `struct_2` не набирает 52/64.

Неполные переписи (n != 64) в критерий не входят и помечаются.

Запуск (из корня репозитория):

    python scripts/e02c_seed_grid.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02c_replication"
OUT = EXP / "seed_grid.json"

# Имя семейства: E02c_seeddec_init<A>_data<B> (внутри сводки, не имя файла).
FAMILY_PATTERN = re.compile(r"^E02c_seeddec_init(?P<init>\d+)_data(?P<data>\d+)$")
FULL_N = 64
STRUCT1_MIN = 52
STRUCT2_MIN = 52

# Полный дизайн критерия (план H-E02C-6): шесть клеток, без которых вердикт не
# применяется. Частичная сетка — это «пока нельзя», а не «опровергнуто».
EXPECTED_CELLS = (
    (42, 101),
    (42, 202),
    (42, 303),
    (101, 42),
    (101, 202),
    (101, 303),
)

# Якоря: известные полные сиды (обе части совпадают).
ANCHORS = {
    (42, 42): "reports/2026-10-20-e02b-results.md (WP4 R-9 seed42: struct_2 64/64)",
    (101, 101): "reports/2026-10-20-e02b-results.md (WP4 R-9 seed101: struct_1 64/64)",
    (142, 142): "reports/2026-10-21-e02c-results.md (E02c seed142: struct_1 64/64)",
    (242, 242): "reports/2026-10-21-e02c-results.md (E02c seed242: uniform_dark 64/64)",
    (342, 342): "reports/2026-10-21-e02c-results.md (E02c seed342: uniform_dark 64/64)",
}
ANCHOR_VALUES = {
    (42, 42): {"n": 64, "struct_2": 64, "class": "struct_2"},
    (101, 101): {"n": 64, "struct_2": 0, "class": "struct_1"},
    (142, 142): {"n": 64, "struct_2": 0, "class": "struct_1"},
    (242, 242): {"n": 64, "struct_2": 0, "class": "uniform_dark"},
    (342, 342): {"n": 64, "struct_2": 0, "class": "uniform_dark"},
}


def cell_from_summary(path: Path) -> dict:
    summary = json.loads(path.read_text(encoding="utf-8"))
    stats = list((summary.get("stats") or {}).values())
    if not stats:
        raise SystemExit(f"{path.name}: нет stats")
    stat = stats[0]
    family = str(stat.get("family") or "")
    match = FAMILY_PATTERN.match(family)
    if not match:
        raise SystemExit(
            f"{path.name}: семейство '{family}' не по шаблону "
            "E02c_seeddec_init<A>_data<B> — клетку не из чего собрать"
        )
    init, data = int(match.group("init")), int(match.group("data"))
    # Название класса — самый частый в frozen_class_counts.
    counts = stat.get("frozen_class_counts") or {}
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else "unknown"
    n = stat.get("n")
    return {
        "init_seed": init,
        "data_seed": data,
        "source": path.name,
        "kind": "measured",
        "family": family,
        "n": n,
        "complete": bool(n == FULL_N),
        "struct_1": counts.get("struct_1", 0),
        "struct_2": stat.get("struct_2"),
        "struct_2_fraction": stat.get("struct_2_fraction"),
        "struct_2_stable_fraction": stat.get("struct_2_stable_fraction"),
        "struct_2_stable_frozen_fraction": stat.get("struct_2_stable_frozen_fraction"),
        "dominant_class": dominant,
        "class_counts": counts,
        "finished_at": summary.get("finished_at"),
    }


def build_verdict(cells: list[dict]) -> dict:
    """Применить критерий H-E02C-6 (см. модульный docstring)."""
    complete = [c for c in cells if c.get("complete")]
    incomplete = [c["source"] for c in cells if not c.get("complete")]
    init101 = [c for c in complete if c["init_seed"] == 101]
    init42 = [c for c in complete if c["init_seed"] == 42]

    cond1_cells = [
        {
            "cell": f"init{c['init_seed']}_data{c['data_seed']}",
            "struct_1": c["struct_1"],
            "ok": bool(c["struct_1"] >= STRUCT1_MIN),
        }
        for c in init101
    ]
    cond1 = bool(init101) and all(x["ok"] for x in cond1_cells)

    struct2_hits = [
        f"init{c['init_seed']}_data{c['data_seed']}"
        for c in init42
        if int(c["struct_2"] or 0) >= STRUCT2_MIN
    ]
    dominant = sorted({c["dominant_class"] for c in init42})
    cond2 = bool(init42) and len(dominant) >= 2 and not struct2_hits

    have = {(c["init_seed"], c["data_seed"]) for c in complete}
    missing = [
        f"init{init}_data{data}"
        for init, data in EXPECTED_CELLS
        if (init, data) not in have
    ]

    if missing:
        # Критерий описывает полный дизайн; на частичной сетке честный ответ —
        # «неприменимо», даже если уже видимые клетки выглядят как опровержение.
        verdict = "n/a_design_incomplete"
    elif cond1 and cond2:
        verdict = "H-E02C-6_confirmed"
    else:
        verdict = "H-E02C-6_refuted"

    failed = []
    if not cond1:
        failed.append("cond1_init101_not_fixed_struct1")
    if not cond2:
        failed.append("cond2_init42_data_does_not_change_class")

    return {
        "criterion": (
            f"(1) все клетки init=101 дают struct_1 >= {STRUCT1_MIN}/{FULL_N}; "
            f"(2) клетки init=42 дают >= 2 доминирующих класса и struct_2 < "
            f"{STRUCT2_MIN}/{FULL_N} в каждой"
        ),
        "verdict": verdict,
        "failed_conditions": failed if verdict.endswith("_refuted") else [],
        "missing_cells": missing,
        "cond1_struct1_fixed_at_init101": cond1,
        "cond1_cells": cond1_cells,
        "cond2_init42_data_changes_class": cond2,
        "init42_dominant_classes": dominant,
        "init42_struct2_at_or_above_threshold": struct2_hits,
        "incomplete_cells_excluded": incomplete,
        # Не критерий, а отдельная заметка из плана: struct_2 >= 52/64 у клетки
        # с init=42 означал бы, что «данные» заменяют данные 42, — это новая
        # гипотеза, а не подтверждение старой.
        "struct2_substitute_candidates": struct2_hits,
    }


def main() -> int:
    cells = []
    for path in sorted(EXP.glob("summary_e02c_seeddec_*.json")):
        cells.append(cell_from_summary(path))

    anchors = []
    for key, value in sorted(ANCHOR_VALUES.items()):
        anchors.append(
            {
                "init_seed": key[0],
                "data_seed": key[1],
                "kind": "anchor",
                "family": None,
                "n": value["n"],
                "struct_2": value["struct_2"],
                "struct_2_fraction": value["struct_2"] / value["n"],
                "dominant_class": value["class"],
                "source": ANCHORS[key],
            }
        )

    inits = sorted({c["init_seed"] for c in cells + anchors})
    datas = sorted({c["data_seed"] for c in cells + anchors})
    grid = {}
    for init in inits:
        for data in datas:
            hit = next(
                (c for c in cells + anchors if c["init_seed"] == init and c["data_seed"] == data),
                None,
            )
            if hit:
                grid[f"init{init}_data{data}"] = hit

    payload = {
        "schema_version": 1,
        "experiment": "E02c_seed_decomposition",
        "kind": "seed_grid",
        "protocol": "reports/2026-10-22-e02c-seed-grid-plan.md",
        "note": (
            "2x2-сетка «инициализация весов x порядок данных»; measured — прогоны "
            "этой серии (клетка опознаётся по имени семейства внутри сводки), "
            "anchor — известные полные сиды из опубликованных отчётов"
        ),
        "inits": inits,
        "datas": datas,
        "n_measured": len(cells),
        "n_anchor": len(anchors),
        "cells": grid,
        "verdict": build_verdict(cells),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[grid] {OUT} : measured={len(cells)} anchors={len(anchors)}")
    for key, cell in grid.items():
        print(
            f"[grid] {key:24s} {cell['dominant_class']:14s} "
            f"struct_2 {cell['struct_2']}/{cell['n']} ({cell['kind']})"
        )
    verdict = payload["verdict"]
    print(f"[grid] вердикт: {verdict['verdict']} {verdict['failed_conditions'] or ''}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
