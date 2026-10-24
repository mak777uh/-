#!/usr/bin/env python
"""v8_matrix.py — агрегат серии V8 (размещение инокулята × правило слияния).

Зачем: пре-регистрация (`reports/2026-10-24-placement-merge-plan.md`) задаёт критерии
в долях на плечо (n = 10), а не «на глаз»: размещение работает при ≥ 8/10 выживания в
`into_gap` против ≤ 2/10 в `into_resident`; слияние — при разнице ≥ 6/10 при одном
размещении; `resident_free` — контроль постановки. Здесь это считается машинно, с
интервалами Wilson и проверкой однородности провенанса кода.

Запуск (из корня):

    python scripts/v8_matrix.py --src morphogenesis/experiments/E09_pond --glob "v8_*.json" \
        --out morphogenesis/experiments/E09_pond/v8_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"v8_(?P<arm>[a-z0-9_]+?)_seed(?P<seed>\d+)\.json$")
ARMS = ("into_resident_majority", "into_resident_weighted", "into_gap_majority",
        "into_gap_weighted", "resident_free", "propagule20_gap_weighted")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)


def invader_series(log: list[dict]) -> list[float]:
    """Доля инвайдера B по шагам (резидент A): 1 - a_share."""
    out = []
    for row in log:
        a_share = row.get("a_share")
        if a_share is not None:
            out.append(1.0 - float(a_share))
    return out


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None                      # агрегат и прочие v8_*.json — не прогоны
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    log = data.get("log") or []
    arm = match.group("arm")
    config = summary.get("config") or {}
    end = summary.get("a_share_final")
    end = 1.0 - float(end) if end is not None else None
    series = invader_series(log)
    start = summary.get("injection_share_actual", summary.get("invader_share_after"))
    resident_free = arm == "resident_free"
    invalid_reason = summary.get("invalid_reason")
    if resident_free:
        # это не инвазия в колонию, а основание своей: критерий «доля подсадки <= 5%» неприменим
        invalid_reason = None
    elif not invalid_reason and start is not None and start > 0.05:
        invalid_reason = f"injection_share {start:.4f} > 0.05"
    return {
        "artifact": f"morphogenesis/experiments/E09_pond/{path.name}",
        "arm": arm,
        "seed": int(match.group("seed")) if match else None,
        "placement": config.get("invade_placement"),
        "merge_rule": config.get("merge_rule"),
        "invader_cells": summary.get("invader_cells"),
        "invader_cells_actual": summary.get("invader_cells_actual"),
        "colony_cells_at_invasion": summary.get("colony_cells_at_invasion"),
        "invader_share_start": start,
        "invader_share_end": end,
        "max_share": round(max(series), 4) if series else None,
        "separate_component": bool(series and max(series) > 0.0),
        "survived": bool(end is not None and end > 0.0),
        "fixated": bool(end is not None and end > 0.5),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
        "pop_time": summary.get("pop_time"),
        "git_commit": config.get("git_commit"),
        "git_dirty": config.get("git_dirty"),
        "git_code_commit": config.get("git_code_commit"),
        "rule_sha256": config.get("rule_sha256"),
        "start_cells": config.get("start_cells"),
        "invalid_reason": invalid_reason,
    }


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ARMS:
        group = [r for r in rows if r["arm"] == arm]
        if not group:
            continue
        valid = [r for r in group if not r["invalid_reason"]]
        survived = sum(1 for r in valid if r["survived"])
        separate = sum(1 for r in valid if r["separate_component"])
        lo, hi = wilson(survived, len(valid))
        shares = [r["max_share"] for r in valid if r["max_share"] is not None]
        alive = [r["alive_final"] for r in valid if r["alive_final"] is not None]
        out.append({
            "arm": arm,
            "placement": group[0]["placement"],
            "merge_rule": group[0]["merge_rule"],
            "n": len(group),
            "valid_n": len(valid),
            "survived_k": survived,
            "survival": round(survived / len(valid), 3) if valid else None,
            "survival_wilson_lo": lo,
            "survival_wilson_hi": hi,
            "separate_k": separate,
            "median_max_share": round(statistics.median(shares), 4) if shares else None,
            "alive_median": round(statistics.median(alive), 1) if alive else None,
            "fixations": sum(1 for r in valid if r["fixated"]),
        })
    return out


def criteria(table: list[dict]) -> dict:
    """Критерии пре-регистрации: размещение, слияние, контроль resident_free."""
    by = {item["arm"]: item for item in table}
    res: dict = {}

    def surv(arm: str) -> float | None:
        item = by.get(arm)
        return item["survival"] if item else None

    res["placement_works"] = bool(
        (surv("into_gap_majority") or 0) >= 0.8 and (surv("into_resident_majority") or 0) <= 0.2)
    res["merge_works_resident"] = bool(
        surv("into_resident_weighted") is not None and surv("into_resident_majority") is not None
        and surv("into_resident_weighted") - surv("into_resident_majority") >= 0.6)
    res["merge_works_gap"] = bool(
        surv("into_gap_weighted") is not None and surv("into_gap_majority") is not None
        and surv("into_gap_weighted") - surv("into_gap_majority") >= 0.6)
    res["merge_works"] = res["merge_works_resident"] or res["merge_works_gap"]
    res["resident_free_control_ok"] = bool((surv("resident_free") or 0) >= 0.3)
    res["propagule_survival"] = surv("propagule20_gap_weighted")
    res["all_arms_low"] = all((item["survival"] or 0) <= 0.2 for item in table)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="v8_*.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--code-changes", default=None,
                    help="JSON-список объявленных изменений кода между плечами")
    ap.add_argument("--anchor-check", default=None,
                    help="JSON проверки-якоря: {run, artifact, fields, matched}")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    table = by_arm(rows)
    code_commits = {r["git_code_commit"] for r in rows if r["git_code_commit"]}
    head_commits = {r["git_commit"] for r in rows if r["git_commit"]}
    payload = {
        "kind": "v8_placement_merge",
        "experiment": "E09_pond_placement_merge",
        "metric": "survived = invader_share_end > 0; separate_component = max_share > 0",
        "note": "собрано scripts/v8_matrix.py; критерии из reports/2026-10-24-placement-merge-plan.md",
        "rows": rows,
        "by_arm": table,
        "criteria": criteria(table),
        "provenance": {
            "code_commits": sorted(code_commits),
            "head_commits": sorted(head_commits),
            "rule_sha256": sorted({r["rule_sha256"] for r in rows if r["rule_sha256"]}),
            "code_changes": json.loads(args.code_changes) if args.code_changes else [],
            "anchor_check": json.loads(args.anchor_check) if args.anchor_check else None,
            "note": ("git_commit — HEAD на старте прогона (мог сдвинуться коммитами документов "
                     "во время серии); идентичность кода проверяется по git_code_commit, "
                     "идентичность мира — по rule_sha256"),
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'плечо':>26} {'n':>3} {'вал':>4} {'выжило':>7} {'доля':>6} {'Wilson':>14} {'отдел':>6} {'alive':>6}")
    for item in table:
        print(f"{item['arm']:>26} {item['n']:>3} {item['valid_n']:>4} {item['survived_k']:>7} "
              f"{str(item['survival']):>6} [{item['survival_wilson_lo']},{item['survival_wilson_hi']}]"
              f" {item['separate_k']:>6} {str(item['alive_median']):>6}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
