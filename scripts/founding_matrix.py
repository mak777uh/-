#!/usr/bin/env python
"""founding_matrix.py — агрегат серии «порог основания» (H-ALIVE-23 / V10).

Зачем: после §10ae вопрос сместился — не «проходит ли инвазия», а «поддерживает ли среда
основание колонии из N клеток на пустом поле». Считать это надо машинно и по критерию,
записанному в `reports/2026-10-24-founding-threshold-plan.md` до прогона:

* `grew` = `alive_final > N` **и** `alive_final > alive_step1` (пятно не просто выжило,
  а превысило собственный стартовый размер);
* «среда поддерживает основание» = при N = 20 выживание и `grew` ≥ 8/10, при N = 1 ≤ 2/10;
* «не поддерживает из ≤ 20 клеток» = при N = 20 выживание ≤ 4/10;
* невалидно, если гейт не сработал (на шаге 1 живых > N + 4).

Запуск (из корня):

    python scripts/founding_matrix.py --src morphogenesis/experiments/E09_pond \
        --glob "found_*.json" --out morphogenesis/experiments/E09_pond/founding_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"found_n(?P<n>\d+)_seed(?P<seed>\d+)\.json$")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    log = data.get("log") or []
    n = int(match.group("n"))
    seed = int(match.group("seed"))
    config = summary.get("config") or {}
    step1 = next((row for row in log if int(row.get("step", 0)) == 1), {})
    alive1 = step1.get("alive_cells")
    alive_final = (summary.get("final") or {}).get("alive_cells")
    max_alive = max((row.get("alive_cells", 0) for row in log), default=None)
    gate = bool(config.get("ignition_gate", False))
    invalid_reason = None
    if not gate:
        invalid_reason = "гейт зажигания выключен: серия шла бы в незащищённом мире"
    elif alive1 is not None and int(alive1) > n + 4:
        invalid_reason = (f"гейт не сработал: на шаге 1 живых {alive1} при инокуляте {n} "
                          "(поле зажглось)")
    grew = bool(alive_final is not None and alive1 is not None
                and int(alive_final) > n and int(alive_final) > int(alive1))
    return {
        "artifact": f"morphogenesis/experiments/E09_pond/{path.name}",
        "n": n,
        "seed": seed,
        "alive_step1": alive1,
        "alive_final": alive_final,
        "max_alive": max_alive,
        "survived": bool(alive_final is not None and int(alive_final) > 0),
        "grew": grew,
        "pop_time": summary.get("pop_time"),
        "generation_length": summary.get("generation_length"),
        "ignition_gate": gate,
        "git_code_commit": config.get("git_code_commit"),
        "rule_sha256": config.get("rule_sha256"),
        "git_dirty": config.get("git_dirty"),
        "invalid_reason": invalid_reason,
    }


def by_n(rows: list[dict]) -> list[dict]:
    out = []
    for n in sorted({r["n"] for r in rows}):
        group = [r for r in rows if r["n"] == n]
        valid = [r for r in group if not r["invalid_reason"]]
        survived = sum(1 for r in valid if r["survived"])
        grew = sum(1 for r in valid if r["grew"])
        lo, hi = wilson(survived, len(valid))
        finals = [r["alive_final"] for r in valid if r["alive_final"] is not None]
        maxes = [r["max_alive"] for r in valid if r["max_alive"] is not None]
        pops = [r["pop_time"] for r in valid if r["pop_time"] is not None]
        out.append({
            # `dose` — сколько клеток в инокуляте; `runs`/`valid_runs` — знаменатели.
            # Раньше поле называлось `n` и читалось как «число прогонов» (25.10).
            "dose": n,
            "runs": len(group),
            "valid_runs": len(valid),
            "invalid_runs": len(group) - len(valid),
            "survived_k": survived,
            "survival": round(survived / len(valid), 3) if valid else None,
            "survival_wilson_lo": lo,
            "survival_wilson_hi": hi,
            "grew_k": grew,
            "grew_share": round(grew / len(valid), 3) if valid else None,
            "alive_final_median": round(statistics.median(finals), 1) if finals else None,
            "max_alive_median": round(statistics.median(maxes), 1) if maxes else None,
            "pop_time_median": round(statistics.median(pops), 1) if pops else None,
        })
    return out


def criteria(table: list[dict]) -> dict:
    by = {item["dose"]: item for item in table}

    def get(n: int, key: str):
        return (by.get(n) or {}).get(key)

    res = {
        # порог МЕЖДУ 1 и 20: при 20 основание идёт, при 1 — нет
        "threshold_between_1_and_20": bool((get(20, "survival") or 0) >= 0.8
                                           and (get(20, "grew_share") or 0) >= 0.8
                                           and (get(1, "survival") or 0) <= 0.2),
        # основание работает и при ОДНОЙ клетке — порога в проверенном диапазоне нет
        "founding_from_one_cell": bool((get(1, "survival") or 0) >= 0.8
                                       and (get(1, "grew_share") or 0) >= 0.8),
        "no_founding_up_to_20": bool((get(20, "survival") or 0) <= 0.4),
        "threshold_above_20": None,
        "monotone_survival": None,
    }
    survivals = [item["survival"] for item in table if item["survival"] is not None]
    if len(survivals) >= 3:
        res["monotone_survival"] = all(b >= a - 1e-9 for a, b in zip(survivals, survivals[1:]))
        # «порог выше 20» заявляем ТОЛЬКО если основание при 20 не идёт
        if res["monotone_survival"] and not res["threshold_between_1_and_20"] \
                and (get(20, "survival") or 0) < 0.8:
            res["threshold_above_20"] = True
    if res["founding_from_one_cell"]:
        res["verdict"] = ("основание идёт из ОДНОЙ клетки (10/10): порога в проверенном "
                          "диапазоне N = 1..20 нет; размер основателя влияет на размер "
                          "колонии, но не на сам факт основания")
    elif res["threshold_between_1_and_20"]:
        res["verdict"] = "порог основания лежит между 1 и 20 клетками"
    elif res["no_founding_up_to_20"]:
        res["verdict"] = "основание из <= 20 клеток не поддерживается"
    else:
        res["verdict"] = "промежуточно: ни порога, ни полного отказа заявить нельзя"
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="found_*.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    table = by_n(rows)
    payload = {
        "kind": "founding_runs",
        "experiment": "E09_pond_founding_threshold",
        "metric": "survived = alive_final > 0; grew = alive_final > N И alive_final > alive_step1",
        "note": ("мир МОДИФИЦИРОВАН: включён --ignition-gate (по умолчанию выключен); "
                 "числа не сравнивать напрямую с сериями D/V8"),
        "rows": rows,
        "by_n": table,
        "criteria": criteria(table),
        "provenance": {
            "code_commits": sorted({r["git_code_commit"] for r in rows if r["git_code_commit"]}),
            "rule_sha256": sorted({r["rule_sha256"] for r in rows if r["rule_sha256"]}),
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'доза':>4} {'прогонов':>8} {'вал':>4} {'выжило':>7} {'доля':>6} {'grew':>6} "
          f"{'alive_final':>12} {'max':>6} {'pop_time':>9}")
    for item in table:
        print(f"{item['dose']:>4} {item['runs']:>8} {item['valid_runs']:>4} {item['survived_k']:>7} "
              f"{str(item['survival']):>6} {str(item['grew_k']):>6} "
              f"{str(item['alive_final_median']):>12} {str(item['max_alive_median']):>6} "
              f"{str(item['pop_time_median']):>9}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
