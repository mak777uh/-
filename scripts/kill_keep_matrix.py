#!/usr/bin/env python
"""kill_keep_matrix.py — агрегат достаточности условия C (kill-and-keep против clean).

Зачем: §10ab.1 дал необходимое условие C (память среды живёт дольше поколения). Полная
минимальная демонстрация — выигрывает ли СЛЕДУЮЩАЯ когорта от наследия: убить организмы,
сохранить поле, посадить свежий пропагул; контроль — то же с очищенным полем.

Критерий (пре-регистрация `reports/2026-10-24-kill-keep-plan.md`): парная разница
`pop_time(keep) − pop_time(clean) > 0` в ≥ 4 из 5 сидов, медиана > 0, и средний ресурс
при пересеве в `keep` ниже, чем в `clean` (иначе сравниваются одинаковые поля).

Запуск (из корня):

    python scripts/kill_keep_matrix.py --src morphogenesis/experiments/E09_pond \
        --glob "killkeep_*.json" --out morphogenesis/experiments/E09_pond/kill_keep_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
from pathlib import Path

NAME = re.compile(r"killkeep[23]?_(?P<arm>keep|clean)_seed(?P<seed>\d+)\.json$")


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    invalid = []
    if (data.get("alive_phase1") or 0) < 100:
        invalid.append(f"колония фазы 1 не выросла (alive {data.get('alive_phase1')})")
    if (data.get("alive_after_reseed") or 0) != int(data.get("cells") or 0):
        invalid.append(f"пересев неполный (alive_after_reseed {data.get('alive_after_reseed')})")
    alive_final = data.get("alive_final")
    max_alive = data.get("max_alive_phase2")
    cells = int(data.get("cells") or 0)
    return {
        "artifact": f"morphogenesis/experiments/E09_pond/{path.name}",
        # ОПИСАТЕЛЬНОЕ поле (не критерий): жила ли колония в конце фазы 2 и росла ли выше
        # стартовых клеток. Нужно, потому что pop_time при заряде 1.0 может мерить время
        # смерти, а не выгоду (замечание библиотекаря, §10ah).
        "reached_growth": bool(max_alive is not None and alive_final is not None
                               and int(alive_final) > 0 and int(max_alive) > cells),
        "sensitivity_note": data.get("sensitivity_note"),
        "arm": match.group("arm"),
        "seed": int(match.group("seed")),
        "resource_mean_at_reseed": data.get("resource_mean_at_reseed"),
        "alive_phase1": data.get("alive_phase1"),
        "pop_time_phase2": data.get("pop_time_phase2"),
        "alive_final": data.get("alive_final"),
        "max_alive_phase2": data.get("max_alive_phase2"),
        "generation_length": data.get("generation_length"),
        "invalid_reason": "; ".join(invalid) if invalid else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="killkeep2_*.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    seeds = sorted({r["seed"] for r in rows})
    pairs = []
    for seed in seeds:
        keep = next((r for r in rows if r["seed"] == seed and r["arm"] == "keep"), None)
        clean = next((r for r in rows if r["seed"] == seed and r["arm"] == "clean"), None)
        if not keep or not clean:
            continue
        diff = None
        if keep["pop_time_phase2"] is not None and clean["pop_time_phase2"] is not None:
            diff = keep["pop_time_phase2"] - clean["pop_time_phase2"]
        resource_ok = (keep["resource_mean_at_reseed"] is not None
                       and clean["resource_mean_at_reseed"] is not None
                       and keep["resource_mean_at_reseed"] < clean["resource_mean_at_reseed"])
        pairs.append({
            "seed": seed,
            "pop_time_keep": keep["pop_time_phase2"],
            "pop_time_clean": clean["pop_time_phase2"],
            "pop_time_diff": diff,
            "alive_keep": keep["alive_final"],
            "alive_clean": clean["alive_final"],
            "resource_keep": keep["resource_mean_at_reseed"],
            "resource_clean": clean["resource_mean_at_reseed"],
            "resource_ok": resource_ok,
            "invalid_reason": keep["invalid_reason"] or clean["invalid_reason"],
        })
    valid = [p for p in pairs if p["invalid_reason"] is None and p["pop_time_diff"] is not None]
    positive = sum(1 for p in valid if p["pop_time_diff"] > 0)
    median_diff = statistics.median([p["pop_time_diff"] for p in valid]) if valid else None
    criteria = {
        "positive_in_4_of_5": bool(positive >= 4 and len(valid) >= 4),
        "median_diff_positive": bool(median_diff is not None and median_diff > 0),
        "resource_lower_in_keep": bool(valid and all(p["resource_ok"] for p in valid)),
        "c_sufficient": bool(positive >= 4 and len(valid) >= 4
                             and median_diff is not None and median_diff > 0
                             and all(p["resource_ok"] for p in valid)),
        "note": ("C достаточно: разница pop_time > 0 в >= 4/5 сидов, медиана > 0, "
                 "и поле keep действительно ниже по ресурсу"),
    }
    payload = {
        "kind": "kill_keep_runs",
        "experiment": "E09_pond_kill_keep",
        "metric": "pop_time фазы 2 (парно по сидам), ресурс при пересеве",
        "note": "собрано scripts/kill_keep_matrix.py; критерии из reports/2026-10-24-kill-keep-plan.md",
        "rows": rows,
        "pairs": pairs,
        "criteria": criteria,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}, пар {len(pairs)}")
    print(f"{'сид':>4} {'keep':>8} {'clean':>8} {'разница':>9} {'res_keep':>9} {'res_clean':>10}")
    for p in pairs:
        print(f"{p['seed']:>4} {str(p['pop_time_keep']):>8} {str(p['pop_time_clean']):>8} "
              f"{str(p['pop_time_diff']):>9} {str(p['resource_keep']):>9} {str(p['resource_clean']):>10}")
    print("критерии:", json.dumps(criteria, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
