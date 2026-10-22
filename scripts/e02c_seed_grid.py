"""Собрать 2×2-сетку «инициализация × порядок данных» из сводок переписей.

Читает `summary_e02c_seeddec_*.json` (и якорные сводки E02b/E02c, если есть) и
складывает клетки в один артефакт `seed_grid.json` рядом с переписями. Никаких
GPU и новых измерений: только сводки, которые уже посчитаны.

Запуск (из корня репозитория):

    python scripts/e02c_seed_grid.py

Файл клетки: `summary_e02c_seeddec_init<A>_data<B>.json`; имя разбирается
регуляркой, поэтому новые клетки подхватываются без правки скрипта.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02c_replication"
OUT = EXP / "seed_grid.json"
PATTERN = re.compile(r"summary_e02c_seeddec_init(?P<init>\d+)_data(?P<data>\d+)\.json$")

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


def cell_from_summary(path: Path, init: int, data: int) -> dict:
    summary = json.loads(path.read_text(encoding="utf-8"))
    stats = list((summary.get("stats") or {}).values())
    if not stats:
        raise SystemExit(f"{path.name}: нет stats")
    stat = stats[0]
    # Название класса — самый частый в frozen_class_counts.
    counts = stat.get("frozen_class_counts") or {}
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else "unknown"
    return {
        "init_seed": init,
        "data_seed": data,
        "source": path.name,
        "kind": "measured",
        "family": stat.get("family"),
        "n": stat.get("n"),
        "struct_2": stat.get("struct_2"),
        "struct_2_fraction": stat.get("struct_2_fraction"),
        "struct_2_stable_fraction": stat.get("struct_2_stable_fraction"),
        "struct_2_stable_frozen_fraction": stat.get("struct_2_stable_frozen_fraction"),
        "dominant_class": dominant,
        "class_counts": counts,
        "finished_at": summary.get("finished_at"),
    }


def main() -> int:
    cells = []
    for path in sorted(EXP.glob("summary_e02c_seeddec_init*_data*.json")):
        match = PATTERN.search(path.name)
        if not match:
            continue
        init, data = int(match.group("init")), int(match.group("data"))
        cells.append(cell_from_summary(path, init, data))

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
        "note": (
            "2x2-сетка «инициализация весов x порядок данных»; measured — прогоны "
            "этой серии, anchor — известные полные сиды из опубликованных отчётов"
        ),
        "inits": inits,
        "datas": datas,
        "n_measured": len(cells),
        "n_anchor": len(anchors),
        "cells": grid,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[grid] {OUT} : measured={len(cells)} anchors={len(anchors)}")
    for key, cell in grid.items():
        print(
            f"[grid] {key:24s} {cell['dominant_class']:14s} "
            f"struct_2 {cell['struct_2']}/{cell['n']} ({cell['kind']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
