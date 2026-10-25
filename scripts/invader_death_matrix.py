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
    стёрт в интервале логирования: max_drop >= 0.999 — от пика до нуля за ОДИН интервал
                 логирования (не «за один шаг»: лог пишется раз в log_every шагов)
    подсадка не отразилась: peak == 0 при actual > 0 — ни в одной строке доля A не отличалась
                 от 1, то есть инвайдер не попал в состояние (не путать со стиранием)

    ВАЖНО: «отразилась ли подсадка» определяется по a_share (доля типа A среди типизированных
    клеток), а НЕ по types_alive: types_alive в логе — число живых МЕТОК линий
    (tag_metrics_block: len(finals)), а не число типов ресурса, поэтому при одной линии оно
    равно 1 даже когда инвайдер присутствует.
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
MIN_PLACEMENT = 15   # подсадка считается полной, если легло >= 15 клеток из 20
LOG_EVERY = 1        # шаг логирования (поле config.log_every, если есть)


def analyse(path: Path, pattern: re.Pattern = NAME,
            min_placement: int = MIN_PLACEMENT) -> dict | None:
    match = pattern.search(path.name)
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
    shares = [float(r["a_share"]) for r in log if r.get("a_share") is not None]
    reflected = bool(shares) and min(shares) < 1.0 - 1e-9
    types_max = max((int(r.get("types_alive") or 1) for r in log), default=1)
    log_every = int(data.get("summary", {}).get("config", {}).get("log_every") or 1)
    placement_ok = injected >= min_placement
    if peak == 0 and injected > 0 and not placement_ok:
        mode = "incomplete_placement"
    elif peak == 0 and injected > 0 and not reflected:
        mode = "placement_not_reflected"
    elif 0 < peak < 10:
        mode = "invalid_peak"
    elif max_drop >= 0.999:
        mode = "wiped_within_log_interval"
    elif max_drop >= ABRUPT:
        mode = "abrupt"
    elif max_drop < GRADUAL:
        mode = "gradual"
    else:
        mode = "mixed"
    return {
        "artifact": str(path).replace("\\", "/"),
        "arm": (match.groupdict().get("arm")
                or (match.group(1) if match.groups() else "unknown")),
        "seed": int(match.groupdict().get("seed")
                    or (match.group(2) if len(match.groups()) >= 2 else 0)),
        "peak_cells": peak,
        "peak_step": peak_step,
        "final_cells": final,
        "survived": final > 0,
        "max_drop_share_of_peak": round(max_drop, 3),
        "mode": mode,
        "steps_to_extinction": (next((s for s, v in series if v == 0), None)
                                if final == 0 else None),
        "injected_cells": injected,
        "types_alive_max": types_max,
        "placement_reflected": reflected,
        "placement_ok": placement_ok,
        "valid": (placement_ok and (peak >= 10 or mode == "wiped_within_log_interval")),
        "invalid_reason": (None if (placement_ok and (peak >= 10 or
                                                      mode == "wiped_within_log_interval"))
                           else (f"подсадка {injected} < {min_placement}" if not placement_ok
                                 else f"пик {peak} < 10 клеток")),
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
                                                              "wiped_within_log_interval")),
            "wiped_within_log_interval_k": sum(
                1 for r in group if r["mode"] == "wiped_within_log_interval"),
            "incomplete_placement_k": sum(1 for r in group if not r["placement_ok"]),
            "placement_not_reflected_k": sum(
                1 for r in group if r["mode"] == "placement_not_reflected"),
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
        "invalid_by_placement": bool((keep.get("incomplete_placement_k") or 0) >= 3
                                     or (majority.get("incomplete_placement_k") or 0) >= 3),
        "note": ("рывок: max падение за шаг >= 50 % пика; постепенно: < 25 % на всём пути; "
                 "невалидно: пик < 10 клеток в >= 4/10 прогонов плеча"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/invdeath")
    ap.add_argument("--out", default=None)
    ap.add_argument("--name-regex", default=None,
                    help="свой шаблон имён (для пересчёта пилота тем же кодом)")
    ap.add_argument("--min-placement", type=int, default=MIN_PLACEMENT,
                    help="порог полной подсадки (для пилота с 5 клетками — 5)")
    args = ap.parse_args(argv)

    pattern = re.compile(args.name_regex) if args.name_regex else NAME
    glob_pat = args.name_regex.replace("\\", "") if False else "*"
    files = sorted(glob.glob(str(Path(args.src) / glob_pat)))
    rows = [r for r in (analyse(Path(f), pattern, args.min_placement) for f in files)
            if r is not None]
    table = by_arm(rows)
    payload = {
        "kind": "invader_death_runs",
        "world": "W1 (pond), merge_rule keep vs majority, пропагул 20 клеток",
        "metric": {
            "inv_t": "round((1 - a_share_t) * alive_cells_t) — клетки инвайдера по шагам",
            "peak": "max_t inv_t",
            "max_drop": "max_t (inv_{t-1} - inv_t) / peak",
            "wiped_within_log_interval": "peak = 0 при actual >= 15 и types_alive >= 2 хотя бы "
                                         "в одной строке — исчез между строками лога "
                                         "(интервал логирования, НЕ «один шаг»)",
            "incomplete_placement": f"actual < {MIN_PLACEMENT} — подсадка не встала целиком",
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
    print(f"{'плечо':>9} {'сид':>3} {'подсадка':>8} {'пик':>4} {'конец':>5} "
          f"{'max_drop':>8} {'режим':>26}")
    for r in sorted(rows, key=lambda x: (x["arm"], x["seed"])):
        print(f"{r['arm']:>9} {r['seed']:>3} {r['injected_cells']:>8} {r['peak_cells']:>4} "
              f"{r['final_cells']:>5} {r['max_drop_share_of_peak']:>8} {r['mode']:>26}")
    print()
    for item in table:
        print(f"{item['arm']:>9}: n={item['runs']} пик мед.={item['peak_cells_median']} "
              f"выжило={item['survived_k']} рывок={item['abrupt_k']} "
              f"постепенно={item['gradual_k']} смешанно={item['mixed_k']} "
              f"max_drop мед.={item['max_drop_median']} | "
              f"стёрто в интервале={item['wiped_within_log_interval_k']} "
              f"неполная подсадка={item['incomplete_placement_k']} "
              f"подсадка не отразилась={item['placement_not_reflected_k']}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
