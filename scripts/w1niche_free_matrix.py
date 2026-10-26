#!/usr/bin/env python
"""w1niche_free_matrix.py — агрегат серии «наследование вне плотной зоны» (H-ALIVE-52).

Читает `morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_<arm>_seed<N>.json`
и собирает парное сравнение плеч по сидам.

**Метрика и фильтр подписаны явно** (правило §3c: корреляция/доля подписывается
коэффициентом, фильтром линий и знаменателем):

* доля `same_share_filtered` = подготовленные клетки, занятые позже **той же** линией,
  делённая на число подготовленных клеток **после фильтра**;
* фильтр: 4-связная компонента **мёртвых** клеток, содержащая подготовленную клетку,
  **≥ `niche_free_min`** (по умолчанию 15); медиана свободной компоненты в мире ~7,
  поэтому фильтр отбрасывает основную массу плотной зоны;
* `underpowered` = `prepared_cells_filtered < 100` (порог §10ay, сохранён).

Запуск (из корня):

    python scripts/w1niche_free_matrix.py --out morphogenesis/experiments/E09_pond/w1niche_free_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"w1nichefree_(?P<arm>legacy|adjacency_exact)_seed(?P<seed>\d+)\.json$")
UNDERPOWERED = 100


def sign_p(k: int, n: int) -> float:
    """Односторонний знаковый тест: P(X >= k) при X ~ Bin(n, 0.5)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w1niche_free")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows: list[dict] = []
    for path in sorted(glob.glob(str(Path(args.src) / "w1nichefree_*.json"))):
        match = NAME.search(Path(path).name)
        if not match:
            continue
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        summary = data.get("summary") or {}
        cfg = summary.get("config") or {}
        filtered = summary.get("prepared_cells_filtered")
        rows.append({
            "artifact": str(path).replace("\\", "/"),
            "arm": match.group("arm"),
            "seed": int(match.group("seed")),
            "git_code_commit": cfg.get("git_code_commit"),
            "git_dirty": cfg.get("git_dirty"),
            "niche_free_min": summary.get("niche_free_min"),
            "prepared_all": summary.get("prepared_cells_total_all"),
            "prepared_filtered": filtered,
            "same_share_filtered": summary.get("same_share_filtered"),
            "any_share_filtered": summary.get("any_share_filtered"),
            "free_comp_median": summary.get("free_comp_median"),
            "free_comp_q90": summary.get("free_comp_q90"),
            "underpowered": (filtered is None or filtered < UNDERPOWERED),
        })

    by_arm: dict[str, dict[int, dict]] = {}
    for r in rows:
        by_arm.setdefault(r["arm"], {})[r["seed"]] = r

    paired = []
    for seed in sorted(set(by_arm.get("legacy", {})) & set(by_arm.get("adjacency_exact", {}))):
        a = by_arm["legacy"][seed]
        b = by_arm["adjacency_exact"][seed]
        ok = (not a["underpowered"]) and (not b["underpowered"]) \
            and a["same_share_filtered"] is not None and b["same_share_filtered"] is not None
        paired.append({
            "seed": seed,
            "legacy": a["same_share_filtered"],
            "adjacency_exact": b["same_share_filtered"],
            "diff": (round(a["same_share_filtered"] - b["same_share_filtered"], 4) if ok else None),
            "prepared_legacy": a["prepared_filtered"],
            "prepared_exact": b["prepared_filtered"],
            "underpowered": not ok,
        })

    diffs = [p["diff"] for p in paired if p["diff"] is not None]
    positive = sum(1 for d in diffs if d > 0)
    n = len(diffs)
    commits = sorted({r["git_code_commit"] for r in rows if r["git_code_commit"]})
    dirty = sorted({str(r["git_dirty"]) for r in rows})

    payload = {
        "kind": "w1niche_free_runs",
        "world": "W1-niche, наследование среды вне плотной зоны (свободная компонента >= niche_free_min)",
        "metric": {
            "same_share_filtered": "подготовленных клеток, занятых позже ТОЙ ЖЕ линией / подготовленные "
                                   "клетки после фильтра",
            "filter": "4-связная компонента мёртвых клеток, содержащая подготовленную клетку, "
                      ">= niche_free_min (15); медиана компоненты в мире ~7",
            "underpowered": f"prepared_cells_filtered < {UNDERPOWERED}",
            "sign_test": "односторонний, P(X >= k) при X ~ Bin(n, 0.5), только пригодные сиды",
        },
        "provenance": {
            "git_code_commit": commits,
            "homogeneous_code": len(commits) == 1,
            "git_dirty_values": dirty,
            "note": "все прогоны серии обязаны иметь один git_code_commit; "
                    "dirty одинаков у всех = одно незакоммиченное состояние",
        },
        "rows": rows,
        "paired": paired,
        "summary": {
            "runs": len(rows),
            "paired_seeds": len(paired),
            "evaluable": n,
            "legacy_median": round(statistics.median(
                [p["legacy"] for p in paired if p["diff"] is not None]), 4) if diffs else None,
            "adjacency_exact_median": round(statistics.median(
                [p["adjacency_exact"] for p in paired if p["diff"] is not None]), 4) if diffs else None,
            "diff_median": round(statistics.median(diffs), 4) if diffs else None,
            "legacy_gt_exact": positive,
            "sign_p": round(sign_p(positive, n), 4) if n else None,
            "dropped_share_median": round(statistics.median(
                [1 - (r["prepared_filtered"] or 0) / r["prepared_all"]
                 for r in rows if r["prepared_all"]]), 4),
        },
        "criteria": {
            "verdict_bar": "legacy > adjacency_exact в >=7/10 пригодных сидов",
            "not_evaluable": "если пригодных < 7 — серия не оценивается",
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}")
    s = payload["summary"]
    print(f"{'сид':>3} {'legacy':>8} {'exact':>8} {'diff':>8} {'prep L':>7} {'prep E':>7} {'пригоден':>9}")
    for p in paired:
        print(f"{p['seed']:>3} {str(p['legacy']):>8} {str(p['adjacency_exact']):>8} "
              f"{str(p['diff']):>8} {str(p['prepared_legacy']):>7} {str(p['prepared_exact']):>7} "
              f"{'нет' if p['underpowered'] else 'да':>9}")
    print(f"\nпригодных {s['evaluable']}/{s['paired_seeds']} | legacy > exact: "
          f"{s['legacy_gt_exact']}/{s['evaluable']} | медиана diff {s['diff_median']} | "
          f"знаковый p = {s['sign_p']}")
    print(f"код: {payload['provenance']['git_code_commit']} | однороден: "
          f"{payload['provenance']['homogeneous_code']} | dirty: {payload['provenance']['git_dirty_values']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
