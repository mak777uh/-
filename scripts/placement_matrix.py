#!/usr/bin/env python
"""placement_matrix.py — V1c: гарантированная подсадка (H-ALIVE-37).

Пре-регистрация `reports/2026-10-25-placement-guarantee-plan.md`. Проверяет, что починка
геометрии подсадки работает и что серия годна по постановке:

    placement_ok   : rejected_by_placement == false и invader_cells_state_after_injection >= 15
    free_cells_at_injection        : 1024 − живых в момент подсадки
    max_free_component_at_injection: размер максимальной СВОБОДНОЙ компоненты
    placement_attempts_used        : сколько перерисовок понадобилось

Критерий годности (пре-регистрация): rejected <= 1/10 И state >= 15 в >= 9/10.
Если годна — публикуется режим гибели по полным подсадкам (как описание, n мало) и доля полных
подсадок рядом с вердиктом.

Запуск (из корня):

    python scripts/placement_matrix.py --src morphogenesis/experiments/E09_pond/placement \
        --out morphogenesis/experiments/E09_pond/placement_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
from pathlib import Path

NAME = re.compile(r"placement_(?:patches_)?(?P<arm>keep|majority)_seed(?P<seed>\d+)\.json$")


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    log = data.get("log") or []
    invasion = int(summary.get("invade_at") or summary.get("invasion_step") or 0)
    series = []
    for row in log:
        step = int(row.get("step", 0))
        share, alive = row.get("a_share"), row.get("alive_cells")
        if share is None or alive is None or step < invasion:
            continue
        series.append((step, round((1.0 - float(share)) * float(alive))))
    peak = max((v for _, v in series), default=0)
    first_zero = next((s for s, v in series if v == 0), None)
    state = summary.get("invader_cells_state_after_injection")
    return {
        "artifact": str(path).replace("\\", "/"),
        "arm": match.group("arm"),
        "seed": int(match.group("seed")),
        "rejected_by_placement": bool(summary.get("rejected_by_placement")),
        "placement_attempts_used": summary.get("placement_attempts_used"),
        "free_cells_at_injection": summary.get("free_cells_at_injection"),
        "max_free_component_at_injection": summary.get("max_free_component_at_injection"),
        "invader_cells_actual": summary.get("invader_cells_actual"),
        "invader_cells_state_after_injection": state,
        "peak_cells": peak,
        "final_cells": series[-1][1] if series else None,
        "time_to_rewrite": (first_zero - invasion) if first_zero is not None else None,
        "placement_ok": bool(not summary.get("rejected_by_placement")
                             and (state or 0) >= 15),
    }


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ("keep", "majority"):
        group = [r for r in rows if r["arm"] == arm]
        if not group:
            continue
        ok = [r for r in group if r["placement_ok"]]
        tt = [r["time_to_rewrite"] for r in ok if r["time_to_rewrite"] is not None]
        out.append({
            "arm": arm,
            "runs": len(group),
            "placement_ok_k": len(ok),
            "rejected_k": sum(1 for r in group if r["rejected_by_placement"]),
            "state_median": round(statistics.median(
                [r["invader_cells_state_after_injection"] or 0 for r in group]), 1),
            "free_cells_median": round(statistics.median(
                [r["free_cells_at_injection"] or 0 for r in group]), 1),
            "max_free_component_median": round(statistics.median(
                [r["max_free_component_at_injection"] or 0 for r in group]), 1),
            "attempts_median": round(statistics.median(
                [r["placement_attempts_used"] or 0 for r in group]), 1),
            "peak_cells_median": round(statistics.median([r["peak_cells"] for r in group]), 1),
            "survived_k": sum(1 for r in group if (r["final_cells"] or 0) > 0),
            "time_to_rewrite_values": tt,
        })
    return out


def criteria(table: list[dict]) -> dict:
    ok = all((item["placement_ok_k"] or 0) >= 9 and (item["rejected_k"] or 0) <= 1
             for item in table)
    return {
        "placement_series_valid": bool(table and ok),
        "note": ("серия годна по постановке, если в каждом плече rejected <= 1/10 И "
                 "state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/placement")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / "placement_*.json")))
    rows = [r for r in (analyse(Path(f)) for f in files) if r is not None]
    table = by_arm(rows)
    payload = {
        "kind": "placement_runs",
        "world": "W1 (pond), require_placement 15, invade_at 201, пропагул 20 клеток",
        "metric": {
            "free_cells_at_injection": "1024 − живых в момент подсадки",
            "max_free_component_at_injection": "размер максимальной свободной 4-компоненты",
            "placement_attempts_used": "перерисовок точки до успеха (до 5)",
            "rejected_by_placement": "пятно не встало за 5 попыток — не выживание и не гибель",
            "invader_cells_state_after_injection": "клеток инвайдера в состоянии сразу после _invade",
            "placement_ok": "rejected == false И state >= 15",
        },
        "rows": rows,
        "by_arm": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'плечо':>9} {'сид':>3} {'rejected':>9} {'попыток':>8} {'свободно':>9} "
          f"{'макс.комп':>10} {'state':>6} {'пик':>4} {'ok':>3}")
    for r in sorted(rows, key=lambda x: (x["arm"], x["seed"])):
        print(f"{r['arm']:>9} {r['seed']:>3} {str(r['rejected_by_placement']):>9} "
              f"{str(r['placement_attempts_used']):>8} {str(r['free_cells_at_injection']):>9} "
              f"{str(r['max_free_component_at_injection']):>10} "
              f"{str(r['invader_cells_state_after_injection']):>6} {r['peak_cells']:>4} "
              f"{str(r['placement_ok']):>3}")
    print()
    for item in table:
        print(f"{item['arm']:>9}: n={item['runs']} годных={item['placement_ok_k']} "
              f"rejected={item['rejected_k']} state мед.={item['state_median']} "
              f"свободно мед.={item['free_cells_median']} "
              f"макс.комп мед.={item['max_free_component_median']} "
              f"попыток мед.={item['attempts_median']} пик мед.={item['peak_cells_median']} "
              f"выжило={item['survived_k']}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
