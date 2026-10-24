#!/usr/bin/env python
"""invader_dose_matrix.py — агрегат серии D (доза основателя, B-037/H73).

Зачем: вопрос «редкая линия исчезла из-за размера основателя или потому, что линия
не способна к инвазии» решается не глазами по логам, а машинно: по каждому прогону
считаются доля подсадки, доля в конце, выживание (доля > 0), максимум доли и
фиксация, а по дозе — доля выживших с интервалом Wilson (при n = 10 доверительный
интервал обязателен, H71/P64).

Критерий пре-регистрации (`reports/2026-10-24-invader-dose-plan.md`) не меняется:
рост = конец / старт; выжил = доля в конце > 0; невалидно = доля подсадки > 5%.

Запуск (из корня):

    python scripts/invader_dose_matrix.py \
        --src morphogenesis/experiments/E09_pond \
        --glob "colinv4_*.json" \
        --out morphogenesis/experiments/E09_pond/invader_dose_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"colinv4_(?P<fd>fd[\d]+)_(?P<dir>[AB]inv[AB])_(?P<mode>\w+?)_n(?P<dose>\d+)_seed(?P<seed>\d+)\.json$")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    """95 % интервал Уилсона для доли k/n (при n = 0 — None)."""
    if n <= 0:
        return None, None
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)


def invader_series(summary: dict, log: list[dict], direction: str) -> list[float]:
    """Доля инвайдера по шагам: для A-в-B это 1 - a_share (резидент A)."""
    out: list[float] = []
    for row in log:
        a_share = row.get("a_share")
        if a_share is None:
            continue
        out.append(1.0 - float(a_share) if direction == "AinvB" else float(a_share))
    return out


def analyse(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    log = data.get("log") or []
    match = NAME.search(path.name)
    dose = int(match.group("dose")) if match else None
    seed = int(match.group("seed")) if match else None
    direction = match.group("dir") if match else None
    start = summary.get("injection_share_actual", summary.get("invader_share_after"))
    end = summary.get("a_share_final")
    if end is not None and direction == "AinvB":
        end = 1.0 - float(end)
    elif end is not None:
        end = float(end)
    series = invader_series(summary, log, direction or "AinvB")
    growth = (end / start) if (start and end is not None and start > 0) else None
    invalid_reason = summary.get("invalid_reason")
    if not invalid_reason and start is not None and start > 0.05:
        invalid_reason = (f"injection_share {start:.4f} > 0.05 — подсадка не редкая "
                          f"(доза {dose} в маленькой колонии)")
    return {
        "artifact": path.name,        "git_commit": (summary.get("config") or {}).get("git_commit"),
        "git_dirty": (summary.get("config") or {}).get("git_dirty"),

        "dose": dose,
        "seed": seed,
        "direction": direction,
        "mode": match.group("mode") if match else None,
        "colony_cells_at_invasion": summary.get("colony_cells_at_invasion"),
        "invader_cells": summary.get("invader_cells"),
        "invader_cells_actual": summary.get("invader_cells_actual"),
        "invader_share_start": start,
        "invader_share_end": end,
        "max_share": round(max(series), 4) if series else None,
        "survived": bool(end is not None and end > 0.0),
        # доля исчезла уже в шаге подсадки: пятно легло вплотную к резиденту и правило
        # большинства переписало компоненту сразу (механизм §10ab)
        "vanished_within_step": bool(start and start > 0
                                     and (max(series) if series else 0.0) == 0.0),
        # пятно село ОТДЕЛЬНОЙ компонентой: его тип виден в шаге подсадки. Только такие
        # прогоны вообще могут показать дозовую зависимость — если пятно легло вплотную
        # к резиденту, правило большинства решает раньше размера
        "separate_component": bool(start and start > 0
                                   and (max(series) if series else 0.0) > 0.0),
        "fixated": bool(end is not None and end > 0.5),
        "growth": growth,
        "pop_time": summary.get("pop_time"),
        "generation_length": summary.get("generation_length"),
        "invalid_reason": invalid_reason,
    }


def by_dose(rows: list[dict]) -> list[dict]:
    out = []
    doses = sorted({r["dose"] for r in rows if r["dose"] is not None})
    for dose in doses:
        group = [r for r in rows if r["dose"] == dose]
        valid = [r for r in group if not r["invalid_reason"]]
        survived = sum(1 for r in valid if r["survived"])
        lo, hi = wilson(survived, len(valid))
        shares = [r["max_share"] for r in valid if r["max_share"] is not None]
        separate = sum(1 for r in valid if r["separate_component"])
        out.append({
            "dose": dose,
            "n": len(group),
            "valid_n": len(valid),
            "invalid_n": len(group) - len(valid),
            "survived_k": survived,
            "survival": round(survived / len(valid), 3) if valid else None,
            "survival_wilson_lo": lo,
            "survival_wilson_hi": hi,
            "median_max_share": round(statistics.median(shares), 4) if shares else None,
            "fixations": sum(1 for r in valid if r["fixated"]),
            "vanished_within_step": sum(1 for r in valid if r["vanished_within_step"]),
            "vanished_within_step_share": (
                round(sum(1 for r in valid if r["vanished_within_step"]) / len(valid), 3)
                if valid else None),
            "separate_k": separate,
            "separate_share": round(separate / len(valid), 3) if valid else None,
            # выживание СРЕДИ отделившихся: только эти прогоны проверяют дозу
            "survived_given_separate": (
                sum(1 for r in valid if r["separate_component"] and r["survived"])
                if separate else None),
            "survival_given_separate": (
                round(sum(1 for r in valid if r["separate_component"] and r["survived"]) / separate, 3)
                if separate else None),
            "dose_test_applicable": bool(separate >= 3),
            "median_pop_time": (round(statistics.median([r["pop_time"] for r in valid]), 1)
                                if valid and all(r["pop_time"] is not None for r in valid) else None),
            "actual_dose_range": (
                [min(r["invader_cells_actual"] for r in valid if r["invader_cells_actual"] is not None),
                 max(r["invader_cells_actual"] for r in valid if r["invader_cells_actual"] is not None)]
                if valid else None),
            "injection_share_range": (
                [min(r["invader_share_start"] for r in valid if r["invader_share_start"] is not None),
                 max(r["invader_share_start"] for r in valid if r["invader_share_start"] is not None)]
                if valid else None),
        })
    return out


def by_actual_dose(rows: list[dict]) -> list[dict]:
    """То же по ФАКТИЧЕСКОЙ дозе: пятно растёт по связному свободному месту и может
    не добрать до запрошенной (тогда доля меньше заявленной)."""
    out = []
    doses = sorted({r["invader_cells_actual"] for r in rows
                    if r.get("invader_cells_actual") is not None})
    for dose in doses:
        group = [r for r in rows if r.get("invader_cells_actual") == dose and not r["invalid_reason"]]
        if not group:
            continue
        survived = sum(1 for r in group if r["survived"])
        separate = sum(1 for r in group if r["separate_component"])
        out.append({
            "actual_dose": dose,
            "valid_n": len(group),
            "survived_k": survived,
            "survival": round(survived / len(group), 3),
            "separate_k": separate,
            "survival_given_separate": (
                round(sum(1 for r in group if r["separate_component"] and r["survived"]) / separate, 3)
                if separate else None),
        })
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="colinv4_*.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--design", default="4")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [analyse(Path(f)) for f in files]
    payload = {
        "kind": "invader_dose_runs",
        "experiment": "E09_pond_invader_dose",
        "design": args.design,
        "metric": "survived = invader_share_end > 0; growth = end/start; dose = число клеток инокулята",
        "note": "собрано scripts/invader_dose_matrix.py; критерии из reports/2026-10-24-invader-dose-plan.md",
        "rows": rows,
        "by_dose": by_dose(rows),
        "by_actual_dose": by_actual_dose(rows),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"{'доза':>5} {'n':>3} {'валид':>5} {'выжило':>7} {'доля':>6} {'Wilson':>14} {'max_share':>10} {'фикс':>5}")
    for item in payload["by_dose"]:
        print(f"{item['dose']:>5} {item['n']:>3} {item['valid_n']:>5} {item['survived_k']:>7} "
              f"{item['survival'] if item['survival'] is not None else '—':>6} "
              f"[{item['survival_wilson_lo']}, {item['survival_wilson_hi']}]".rjust(0)
              + f" {item['median_max_share'] if item['median_max_share'] is not None else '—':>10} "
                f"{item['fixations']:>5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
