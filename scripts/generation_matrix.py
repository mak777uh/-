#!/usr/bin/env python
"""generation_matrix.py — длина поколения на плечах, где измерен полураспад наследия.

Зачем: отношение «полураспад / поколение» (условие C) имеет смысл только **внутри
одной конфигурации**. Полураспад 20–41 шаг измерен пробой `inheritance_probe.py`
(`inherit2_*.json`), а не на плечах `b2_*_fixed`, поэтому поколение надо мерить
ровно на конфигурации пробы — иначе получается межконфигурационное отношение, за
которое формулировка «1/5 поколения» и была снята (§10ab).

Скрипт сводит `genprobe_<env>_fixed_seed<N>.json` (прогоны с `generation_length`) с
`inherit2_<env>_fixed.json` (полураспад) и считает отношение по сиду.

Запуск (из корня):

    python scripts/generation_matrix.py \
        --src morphogenesis/experiments/E09_pond \
        --out morphogenesis/experiments/E09_pond/generation_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

GEN = re.compile(r"genprobe_(?P<env>uniform|patches|gradflip)_fixed_seed(?P<seed>\d+)\.json$")

# Параметры, влияющие на деление. Сравниваем конфигурацию пробы (полураспад) с b2_*
# по тому, что задано явно: проба НЕ передаёт spore_bias/w_rich/organism-mobility,
# а b2-плечи передают — значит конфигурации разные, и ссылаться на оба плеча нельзя.
PROBE_CONFIG = {
    "grid": 32, "income_mode": "proportional", "init_resource_fill": 0.9,
    "baseline_income": 0.2, "update_cost": 0.02, "repair_cost": 0.02,
    "budding_mass": 24, "budding_cost": 0.2, "invest_rate": 0.02, "invest_mode": "fixed",
    "spore_bias": "random (default)", "w_rich": "0.5 (default)",
    "organism_mobility_cost": "0.0 (default: выключена)",
}
B2_ARM_CONFIG = {
    "grid": 32, "income_mode": "proportional", "init_resource_fill": 0.9,
    "baseline_income": 0.2, "update_cost": 0.02, "repair_cost": 0.02,
    "budding_mass": 24, "budding_cost": 0.2, "invest_rate": 0.02, "invest_mode": "fixed",
    "spore_bias": "score", "w_rich": 0.1, "organism_mobility_cost": 0.05,
}
DIFFER = ["spore_bias", "w_rich", "organism_mobility_cost"]


def half_lives(src: Path) -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = {}
    for path in sorted(glob.glob(str(src / "inherit2_*_fixed.json"))):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        env = payload.get("env")
        rows = payload.get("rows") or []
        out.setdefault(env, {})
        for row in rows:
            if row.get("half_life_steps") is not None:
                out[env][int(row["seed"])] = float(row["half_life_steps"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    halves = half_lives(Path(args.src))
    rows = []
    for path in sorted(glob.glob(str(Path(args.src) / "genprobe_*_fixed_seed*.json"))):
        match = GEN.search(Path(path).name)
        if not match:
            continue
        env, seed = match.group("env"), int(match.group("seed"))
        summary = json.loads(Path(path).read_text(encoding="utf-8")).get("summary") or {}
        gen = summary.get("generation_length")
        half = halves.get(env, {}).get(seed)
        rows.append({
            "artifact": Path(path).name,
            "env": env,
            "seed": seed,
            "generation_length": gen,
            "generation_length_oldest": summary.get("generation_length_oldest"),
            "generation_divisions": summary.get("generation_divisions"),
            "half_life_steps": half,
            "ratio_half_life_per_generation": (
                round(half / gen, 2) if half is not None and gen else None),
            "pop_time": summary.get("pop_time"),
            "alive_final": (summary.get("final") or {}).get("alive_cells"),
        })

    by_env: list[dict] = []
    for env in sorted({r["env"] for r in rows}):
        group = [r for r in rows if r["env"] == env]
        gens = [r["generation_length"] for r in group if r["generation_length"] is not None]
        halves_env = [r["half_life_steps"] for r in group if r["half_life_steps"] is not None]
        ratios = [r["ratio_half_life_per_generation"] for r in group
                  if r["ratio_half_life_per_generation"] is not None]
        by_env.append({
            "env": env,
            "n": len(group),
            "generation_range": [min(gens), max(gens)] if gens else None,
            "half_life_range": [min(halves_env), max(halves_env)] if halves_env else None,
            "ratio_range": [min(ratios), max(ratios)] if ratios else None,
        })

    payload = {
        "kind": "generation_runs",
        "experiment": "E09_pond_generation_on_inherit2",
        "metric": "длина поколения (медиана среднего возраста клеток колонии в момент почкования)",
        "note": ("конфигурация = world/inheritance_probe.py, то есть та же, где измерен "
                 "полураспад inherit2_*; НЕ совпадает с b2_*_fixed"),
        "config_probe": PROBE_CONFIG,
        "config_b2_arm": B2_ARM_CONFIG,
        "config_differs_in": DIFFER,
        "config_verdict": ("поколение и полураспад можно сравнивать только внутри конфигурации "
                           "пробы; ссылка на b2_*_fixed была бы межконфигурационной"),
        "rows": rows,
        "by_env": by_env,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"{'среда':>9} {'n':>2} {'поколение':>12} {'полураспад':>12} {'отношение':>12}")
    for item in by_env:
        print(f"{item['env']:>9} {item['n']:>2} {str(item['generation_range']):>12} "
              f"{str(item['half_life_range']):>12} {str(item['ratio_range']):>12}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
