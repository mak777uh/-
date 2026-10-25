#!/usr/bin/env python
"""invader_death_matrix.py — режим гибели инвайдера: рывком или постепенно.

Вопрос (H-ALIVE-35, пре-регистрация `reports/2026-10-25-invader-death-mode-plan.md`):
способ гибели редкой линии зависит от правила слияния — при `merge=keep` рывками, при
`majority` постепенно, или он одинаков?

ОПРЕДЕЛЕНИЯ (формулами):

    inv_t      = round((1 - a_share_t) * alive_cells_t)   — клетки инвайдера на шаге t
    peak       = max_t inv_t
    drop_t     = (inv_{t-1} - inv_t) / peak               — падение за шаг в долях пика
    max_drop   = max_t drop_t
    рывок      : max_drop >= 0.50  (одномоментная потеря половины пика)
    стёрт сразу: peak == 0 при inj_actual > 0 — инвайдер исчез МЕЖДУ строками лога
                 (в пределах одного шага после подсадки); это тоже одномоментная смерть,
                 но отдельная категория: доля 0 в первой же строке после инъекции
    постепенно : max_drop <  0.25  на всём пути к гибели
    иначе      : смешанный режим
    невалидно  : 0 < peak < 10 клеток (пик слишком мал, чтобы говорить о режиме)

Данные берутся из существующего лога (`a_share`, `alive_cells`) — отдельный логгер не нужен.

Запуск (из корня):

    python scripts/invader_death_matrix.py \
        --src morphogenesis/experiments/E09_pond/invdeath \
        --out morphogenesis/experiments/E09_pond/invader_death_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
from pathlib import Path

NAME = re.compile(r"invdeath_(?P<arm>keep|majority)_seed(?P<seed>\d+)\.json$")
ABRUPT = 0.50
GRADUAL = 0.25


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    log = data.get("log") or []
    series = []
    for row in log:
        share = row.get("a_share")
        alive = row.get("alive_cells")
        if share is None or alive is None:
            continue
        series.append((int(row.get("step", 0)), round((1.0 - float(share)) * float(alive))))
    if not series:
        return None
    peak = max(v for _, v in series)
    peak_step = next(s for s, v in series if v == peak)
    drops = [(s, (v0 - v1) / peak) for (s, v0), (s2, v1) in zip(series, series[1:])
             for s in [s2] if peak > 0]
    max_drop = max((d for _, d in drops), default=0.0)
    final = series[-1][1]
    injected = int(data.get("summary", {}).get("invader_cells_actual") or 0)
    if peak == 0 and injected > 0:
        mode = "wiped_within_one_step"
    elif 0 < peak < 10:
        mode = "invalid_peak"
    elif max_drop >= ABRUPT:
        mode = "abrupt"
    elif max_drop < GRADUAL:
        mode = "gradual"
    else:
        mode = "mixed"
    return {
        "artifact": str(path).replace("\\", "/"),
        "arm": match.group("arm"),
        "seed": int(match.group("seed")),
        "peak_cells": peak,
        "peak_step": peak_step,
        "final_cells": final,
        "survived": final > 0,
        "max_drop_share_of_peak": round(max_drop, 3),
        "mode": mode,
        "steps_to_extinction": (next((s for s, v in series if v == 0), None)
                                if final == 0 else None),
        "injected_cells": injected,
        "valid": peak >= 10 or mode == "wiped_within_one_step",
        "invalid_reason": (None if (peak >= 10 or mode == "wiped_within_one_step")
                           else f"пик {peak} < 10 клеток"),
    }


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ("keep", "majority"):
        group = [r for r in rows if r["arm"] == arm]
        if not group:
            continue
        valid = [r for r in group if r["valid"]]
        out.append({
            "arm": arm,
            "runs": len(group),
            "valid_runs": len(valid),
            "peak_cells_median": round(statistics.median([r["peak_cells"] for r in group]), 1),
            "survived_k": sum(1 for r in group if r["survived"]),
            "abrupt_k": sum(1 for r in group if r["mode"] in ("abrupt",
                                                              "wiped_within_one_step")),
            "wiped_within_one_step_k": sum(
                1 for r in group if r["mode"] == "wiped_within_one_step"),
            "gradual_k": sum(1 for r in group if r["mode"] == "gradual"),
            "mixed_k": sum(1 for r in group if r["mode"] == "mixed"),
            "max_drop_median": round(statistics.median(
                [r["max_drop_share_of_peak"] for r in group]), 3),
            "final_cells_median": round(statistics.median(
                [r["final_cells"] for r in group]), 1),
        })
    return out


def criteria(table: list[dict]) -> dict:
    by = {item["arm"]: item for item in table}
    keep = by.get("keep") or {}
    majority = by.get("majority") or {}
    return {
        "keep_abrupt_7_of_10": bool((keep.get("abrupt_k") or 0) >= 7),
        "majority_gradual_7_of_10": bool((majority.get("gradual_k") or 0) >= 7),
        "mode_depends_on_merge": bool(
            (keep.get("abrupt_k") or 0) >= 7 and (majority.get("gradual_k") or 0) >= 7),
        "invalid_by_data": bool(min(keep.get("valid_runs") or 0,
                                    majority.get("valid_runs") or 0) < 7),
        "note": ("рывок: max падение за шаг >= 50 % пика; постепенно: < 25 % на всём пути; "
                 "невалидно: пик < 10 клеток в >= 4/10 прогонов плеча"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/invdeath")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / "invdeath_*.json")))
    rows = [r for r in (analyse(Path(f)) for f in files) if r is not None]
    table = by_arm(rows)
    payload = {
        "kind": "invader_death_runs",
        "world": "W1 (pond), merge_rule keep vs majority, пропагул 20 клеток",
        "metric": {
            "inv_t": "round((1 - a_share_t) * alive_cells_t) — клетки инвайдера по шагам",
            "peak": "max_t inv_t",
            "max_drop": "max_t (inv_{t-1} - inv_t) / peak",
            "abrupt": f"max_drop >= {ABRUPT}",
            "gradual": f"max_drop < {GRADUAL}",
        },
        "rows": rows,
        "by_arm": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'плечо':>9} {'сид':>3} {'пик':>4} {'конец':>5} {'max_drop':>8} {'режим':>8}")
    for r in sorted(rows, key=lambda x: (x["arm"], x["seed"])):
        print(f"{r['arm']:>9} {r['seed']:>3} {r['peak_cells']:>4} {r['final_cells']:>5} "
              f"{r['max_drop_share_of_peak']:>8} {r['mode']:>8}")
    print()
    for item in table:
        print(f"{item['arm']:>9}: n={item['runs']} пик мед.={item['peak_cells_median']} "
              f"выжило={item['survived_k']} рывок={item['abrupt_k']} "
              f"постепенно={item['gradual_k']} смешанно={item['mixed_k']} "
              f"max_drop мед.={item['max_drop_median']}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
