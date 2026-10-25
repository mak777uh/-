#!/usr/bin/env python
"""phase_matrix.py — фазовая развёртка majority: сколько шагов живёт инвайдер до переписывания.

Вопрос (H-ALIVE-38, пре-регистрация `reports/2026-10-25-phase-sweep-plan.md`): период
`enforce_colony_types()` = 5 шагов — это параметр мира, а не свойство правила слияния. При
`invade_at`, кратном 5, инвайдер переписывается в том же шаге и невидим в логе.

ОПРЕДЕЛЕНИЯ:

    state_after_injection = round(invader_share_after * colony_cells_at_invasion)
                            (считается внутри _invade — это состояние сразу после подсадки)
    inv_t                 = round((1 - a_share_t) * alive_cells_t)
    steps_visible         = #{t >= invasion_step : inv_t >= 1}
    time_to_rewrite       = t_first_zero - invasion_step (null, если инвайдер не исчез)
    peak_cells            = max_t inv_t

Запуск (из корня):

    python scripts/phase_matrix.py \
        --src morphogenesis/experiments/E09_pond/phase \
        --out morphogenesis/experiments/E09_pond/phase_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
from pathlib import Path

NAME = re.compile(r"phase_at(?P<at>\d+)_seed(?P<seed>\d+)\.json$")


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    log = data.get("log") or []
    invasion = int(summary.get("invade_at") or summary.get("invasion_step") or 0)
    state_after = round(float(summary.get("invader_share_after") or 0)
                        * float(summary.get("colony_cells_at_invasion") or 0))
    series = []
    for row in log:
        step = int(row.get("step", 0))
        share = row.get("a_share")
        alive = row.get("alive_cells")
        if share is None or alive is None or step < invasion:
            continue
        series.append((step, round((1.0 - float(share)) * float(alive))))
    visible = [(s, v) for s, v in series if v >= 1]
    first_zero = next((s for s, v in series if v == 0), None)
    return {
        "artifact": str(path).replace("\\", "/"),
        "invade_at_requested": int(match.group("at")),
        "invade_at_actual": invasion,
        "seed": int(match.group("seed")),
        "state_after_injection": state_after,
        "invader_cells_actual": summary.get("invader_cells_actual"),
        "peak_cells": max((v for _, v in series), default=0),
        "steps_visible": len(visible),
        "time_to_rewrite": (first_zero - invasion) if first_zero is not None else None,
        "survived": bool(series) and series[-1][1] > 0,
        "a_share_final": summary.get("a_share_final"),
        "valid": state_after >= 15,
        "invalid_reason": None if state_after >= 15 else f"состояние {state_after} < 15",
    }


def by_phase(rows: list[dict]) -> list[dict]:
    out = []
    for at in sorted({r["invade_at_requested"] for r in rows}):
        group = [r for r in rows if r["invade_at_requested"] == at]
        valid = [r for r in group if r["valid"]]
        tt = [r["time_to_rewrite"] for r in valid if r["time_to_rewrite"] is not None]
        out.append({
            "invade_at": at,
            "runs": len(group),
            "valid_runs": len(valid),
            "state_after_median": round(statistics.median(
                [r["state_after_injection"] for r in group]), 1),
            "steps_visible_median": round(statistics.median(
                [r["steps_visible"] for r in group]), 1),
            "time_to_rewrite_median": round(statistics.median(tt), 1) if tt else None,
            "time_to_rewrite_max": max(tt) if tt else None,
            "time_to_rewrite_le5_k": sum(1 for v in tt if v <= 5),
            "survived_k": sum(1 for r in group if r["survived"]),
        })
    return out


def criteria(table: list[dict]) -> dict:
    ok = [item for item in table
          if (item["time_to_rewrite_le5_k"] or 0) >= 9 and (item["valid_runs"] or 0) >= 9]
    return {
        "structure_period_le5_all_phases": bool(len(ok) == len(table) and table),
        "any_phase_gt5_in_3": bool(any(
            (item["valid_runs"] or 0) - (item["time_to_rewrite_le5_k"] or 0) >= 3
            for item in table)),
        "note": ("структурное свойство: time_to_rewrite <= 5 в >= 9/10 каждой фазы => режим гибели "
                 "в majority неопределим по построению (период enforce = 5 шагов); иначе нужен "
                 "мир с enforce_every = 1 (пул D-48)"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/phase")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / "phase_*.json")))
    rows = [r for r in (analyse(Path(f)) for f in files) if r is not None]
    table = by_phase(rows)
    payload = {
        "kind": "phase_runs",
        "world": "W1 (pond), majority, пропагул 20 клеток, сдвиг фазы подсадки",
        "metric": {
            "state_after_injection": "round(invader_share_after * colony_cells_at_invasion) — "
                                     "состояние сразу после _invade (до первого enforce)",
            "inv_t": "round((1 - a_share_t) * alive_cells_t)",
            "steps_visible": "#{t : inv_t >= 1}",
            "time_to_rewrite": "t_first_zero - invasion_step (null если не исчез)",
            "valid": "state_after_injection >= 15",
        },
        "rows": rows,
        "by_phase": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'фаза':>5} {'сид':>3} {'состояние':>9} {'пик':>4} {'видно':>5} {'до перепис.':>11}")
    for r in sorted(rows, key=lambda x: (x["invade_at_requested"], x["seed"])):
        print(f"{r['invade_at_requested']:>5} {r['seed']:>3} {r['state_after_injection']:>9} "
              f"{r['peak_cells']:>4} {r['steps_visible']:>5} {str(r['time_to_rewrite']):>11}")
    print()
    for item in table:
        print(f"фаза {item['invade_at']}: n={item['runs']} вал={item['valid_runs']} "
              f"состояние мед.={item['state_after_median']} видно мед.={item['steps_visible_median']} "
              f"до перепис. мед.={item['time_to_rewrite_median']} max={item['time_to_rewrite_max']} "
              f"<=5 в {item['time_to_rewrite_le5_k']}/{item['valid_runs']}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
