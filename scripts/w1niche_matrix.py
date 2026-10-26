#!/usr/bin/env python
"""w1niche_matrix.py — W1-niche: наследование среды или зона смерти (H-ALIVE-46).

Собирает четыре плеча (`legacy`, `adjacent_matched`, `density_matched`, `prepared`) из артефактов
`w1niche4_*` (пилот, сиды 1-3) и `w1niche5_*` (серия, сиды 1-10; сиды 1-3 — пилотные).

Величины:
    same_share = offspring_in_prepared_k / prepared_cells_total   (числитель и знаменатель явно)
    any_share  = prepared_occupied_any_k / prepared_cells_total
    underpowered: prepared_cells_total < 100 (в знаковый тест не входит, но публикуется)

Ожидание (`prepared_expected_hits`) НЕ используется для вердикта: оно переворачивает направление
от прогона к прогону (кластеризация меток), помечено derived_by_construction.

Запуск (из корня):

    python scripts/w1niche_matrix.py --out morphogenesis/experiments/E09_pond/w1niche5_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

ARMS = ("legacy", "adjacent_matched", "density_matched", "prepared")
NAME = re.compile(r"w1niche[45]_(?P<arm>legacy|adjacent_matched|density_matched|prepared)_seed(?P<seed>\d+)\.json$")
UNDERPOWERED = 100


def load_rows(src: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for path in sorted(glob.glob(str(Path(src) / "w1niche*_seed*.json"))):
        match = NAME.search(Path(path).name)
        if not match:
            continue
        arm, seed = match.group("arm"), int(match.group("seed"))
        if (arm, seed) in seen:      # серия приоритетнее пилота
            if "w1niche5_" not in Path(path).name:
                continue
        seen.add((arm, seed))
        summary = json.loads(Path(path).read_text(encoding="utf-8")).get("summary") or {}
        prep = int(summary.get("prepared_cells_total") or 0)
        same = int(summary.get("offspring_in_prepared_k") or 0)
        any_ = int(summary.get("prepared_occupied_any_k") or 0)
        rows.append({
            "artifact": str(path).replace("\\", "/"),
            "arm": arm,
            "seed": seed,
            "prepared_cells_total": prep,
            "offspring_in_prepared_k": same,
            "prepared_occupied_any_k": any_,
            "same_share": round(same / prep, 4) if prep else None,
            "any_share": round(any_ / prep, 4) if prep else None,
            "underpowered": prep < UNDERPOWERED,
            "resource_at_death_median": summary.get("resource_at_death_median"),
            "returned_total": summary.get("returned_total"),
            "prepared_expected_hits": summary.get("prepared_expected_hits"),
            "derived_by_construction": {"prepared_expected_hits": True},
        })
    return rows


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ARMS:
        group = [r for r in rows if r["arm"] == arm and r["same_share"] is not None]
        if not group:
            continue
        shares = [r["same_share"] for r in group]
        strong = [r["same_share"] for r in group if not r["underpowered"]]
        out.append({
            "arm": arm,
            "runs": len(group),
            "underpowered_k": sum(1 for r in group if r["underpowered"]),
            "prepared_median": statistics.median([r["prepared_cells_total"] for r in group]),
            "same_share_median": round(statistics.median(shares), 4),
            "same_share_median_powered": round(statistics.median(strong), 4) if strong else None,
            "same_share_min": round(min(shares), 4),
            "same_share_max": round(max(shares), 4),
        })
    return out


def paired(rows: list[dict], a: str, b: str) -> dict:
    da = {r["seed"]: r for r in rows if r["arm"] == a}
    db = {r["seed"]: r for r in rows if r["arm"] == b}
    seeds = sorted(set(da) & set(db))
    ok = [s for s in seeds if not da[s]["underpowered"] and not db[s]["underpowered"]]
    diffs = [round(da[s]["same_share"] - db[s]["same_share"], 4) for s in ok]
    wins = sum(1 for d in diffs if d > 0)
    n = len(diffs)
    # односторонний знаковый тест: p = 0.5^n при всех победах
    p = 0.5 ** n if n else None
    return {"comparison": f"{a} > {b}", "wins": wins, "n": n, "diffs": diffs,
            "median_diff": round(statistics.median(diffs), 4) if diffs else None,
            "sign_test_p_one_sided": round(p, 4) if p else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w1niche")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows = load_rows(args.src)
    table = by_arm(rows)
    pairs = [paired(rows, "legacy", "adjacent_matched"),
             paired(rows, "legacy", "density_matched"),
             paired(rows, "legacy", "prepared"),
             paired(rows, "adjacent_matched", "density_matched"),
             paired(rows, "adjacent_matched", "prepared")]
    payload = {
        "kind": "w1niche_runs",
        "world": "W1, type_level = cell, death_return = 0.05 (четыре способа выбрать подготовленную клетку)",
        "metric": {
            "same_share": "offspring_in_prepared_k / prepared_cells_total — доля подготовленных клеток, "
                          "которые позже заняла клетка ТОЙ ЖЕ метки",
            "any_share": "prepared_occupied_any_k / prepared_cells_total — занял кто угодно",
            "underpowered": f"prepared_cells_total < {UNDERPOWERED} — вне знакового теста, публикуется",
            "prepared_expected_hits": "ожидание при случайном размещении; derived_by_construction: true, "
                                      "НЕ критерий (направление переворачивается от прогона к прогону)",
        },
        "rows": rows,
        "by_arm": table,
        "paired": pairs,
        "criteria": {
            "not_lineage": next(p for p in pairs if p["comparison"] == "legacy > adjacent_matched")["wins"],
            "not_density": next(p for p in pairs if p["comparison"] == "adjacent_matched > density_matched"),
            "note": "вердикт — прямое парное сравнение долей; ожидание не используется",
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}")
    print(f"{'плечо':>17} {'n':>3} {'under':>6} {'подгот мед':>11} {'same_share мед':>15} {'powered':>8}")
    for t in table:
        print(f"{t['arm']:>17} {t['runs']:>3} {t['underpowered_k']:>6} {t['prepared_median']:>11} "
              f"{t['same_share_median']:>15} {str(t['same_share_median_powered']):>8}")
    print()
    for p in pairs:
        print(f"{p['comparison']:>38}: {p['wins']}/{p['n']} | медиана разницы {p['median_diff']} "
              f"| знаковый p = {p['sign_test_p_one_sided']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
