"""Какие шумовые старты не дают доминирующий класс в клетках сетки H-E02C-6.

Читает `census_e02c_seeddec_wave2.json` и для каждой клетки показывает:
доминирующий класс, его счёт, и *какие именно старты* выпали. Если выпадают
одни и те же сиды в разных клетках — это свойство стартов; если разные —
свойство клетки. Никаких новых измерений: только уже посчитанные переписи.

Запуск (из корня):

    python scripts/analyze_grid_failures.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CENSUS = REPO / "morphogenesis" / "experiments" / "E02c_replication" / "census_e02c_seeddec_wave2.json"
OUT = REPO / "morphogenesis" / "experiments" / "E02c_replication" / "seed_grid_failures.json"
CELLS = [
    (42, 202, "E02c_seeddec_init42_data202"),
    (42, 303, "E02c_seeddec_init42_data303"),
    (101, 202, "E02c_seeddec_init101_data202"),
    (101, 303, "E02c_seeddec_init101_data303"),
]


def main() -> int:
    data = json.loads(CENSUS.read_text(encoding="utf-8"))
    runs = data["runs"]
    result = {"source": CENSUS.name, "cells": {}, "failed_start_overlap": {}}
    failed_by_cell = {}
    for init, datas, family in CELLS:
        rows = [r for r in runs if r.get("family") == family]
        counts = Counter(r["frozen_class"] for r in rows)
        dominant, n = counts.most_common(1)[0]
        failed = sorted(r["seed"] for r in rows if r["frozen_class"] != dominant)
        failed_by_cell[(init, datas)] = failed
        result["cells"][f"init{init}_data{datas}"] = {
            "n": len(rows),
            "dominant_class": dominant,
            "dominant_count": n,
            "class_counts": dict(counts),
            "failed_starts": failed,
            "failed_count": len(failed),
        }
        print(f"init{init}_data{datas}: {dominant} {n}/{len(rows)}; выпали старты {failed}")

    # Пересечения между клетками с одинаковой инициализацией.
    pairs = defaultdict(dict)
    for (init, datas), failed in failed_by_cell.items():
        pairs[init][datas] = set(failed)
    for init, by_data in sorted(pairs.items()):
        keys = sorted(by_data)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                inter = sorted(by_data[a] & by_data[b])
                result["failed_start_overlap"][f"init{init}_data{a}_vs_data{b}"] = {
                    "a_failed": sorted(by_data[a]),
                    "b_failed": sorted(by_data[b]),
                    "intersection": inter,
                    "n_intersection": len(inter),
                }
                print(f"init{init}: data{a} vs data{b} — общих выпавших стартов {len(inter)} {inter}")

    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"записано: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
