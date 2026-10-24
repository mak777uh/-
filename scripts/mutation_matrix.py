#!/usr/bin/env python
"""mutation_matrix.py — агрегат серии B (мутация метки линии, условие B).

Зачем: срабатывание условия B проверяется машинно по критериям
`library/conditions-B-criteria.md`: новизна > 0 при m > 0, строго 0 при m = 0, рост
Shannon, монотонность по дозам и сохранение населения. Считать это глазами по 15
артефактам нельзя.

Метрики берутся из `scripts/trait_metrics.py` (те же определения, что у библиотеки),
поля населения и родословной — из `summary` артефакта.

Запуск (из корня):

    python scripts/mutation_matrix.py \
        --src morphogenesis/experiments/E09_pond --glob "mut_*.json" \
        --out morphogenesis/experiments/E09_pond/mutation_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trait_metrics  # noqa: E402

NAME = re.compile(r"mut_(?P<dose>m[0-9]+)_seed(?P<seed>\d+)\.json$")
DOSE = {"m0": 0.0, "m0001": 0.001, "m001": 0.01, "m005": 0.05, "m02": 0.2}
POPULATION_FLOOR = 0.7   # медиана pop_time при m=0.05 не ниже 0.7 от m=0


def dose_of(tag: str) -> float | None:
    if tag in DOSE:
        return DOSE[tag]
    digits = tag.lstrip("m")
    try:
        return float(f"0.{digits}") if digits else None
    except ValueError:
        return None


def analyse(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    metrics = trait_metrics.analyse(path)
    match = NAME.search(path.name)
    dose = dose_of(match.group("dose")) if match else None
    generation = summary.get("lineage_generation") or {}
    fitness = summary.get("lineage_fitness") or {}
    return {
        "artifact": path.name,
        "dose": dose,
        "seed": int(match.group("seed")) if match else None,
        "valid": metrics.get("valid"),
        "invalid_reason": metrics.get("invalid_reason"),
        "mutation_rate": summary.get("mutation_rate"),
        "mutation_events": summary.get("mutation_events"),
        "types_alive": summary.get("types_alive"),
        "shannon_median": metrics.get("shannon_median"),
        "shannon_first": metrics.get("shannon_first"),
        "shannon_last": metrics.get("shannon_last"),
        "shannon_second_half_median": metrics.get("shannon_second_half_median"),
        "novelty_flux": metrics.get("novelty_flux"),
        "novelty_window_steps": metrics.get("novelty_window_steps"),
        "types_total": metrics.get("types_total"),
        "spearman_trait_births": metrics.get("spearman_trait_births"),
        "spearman_note": metrics.get("spearman_reason"),
        "pop_time": summary.get("pop_time"),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
        "generation_length": summary.get("generation_length"),
        "generation_divisions": summary.get("generation_divisions"),
        "lineage_max_generation": max(generation.values()) if generation else None,
        "lineage_top_fitness": max(fitness.values()) if fitness else None,
        "series_points": len(summary.get("type_counts_series") or []),
    }


def by_dose(rows: list[dict]) -> list[dict]:
    out = []
    for dose in sorted({r["dose"] for r in rows if r["dose"] is not None}):
        group = [r for r in rows if r["dose"] == dose]
        valid = [r for r in group if r["valid"]]
        shannon = [r["shannon_median"] for r in valid if r["shannon_median"] is not None]
        novelty = [r["novelty_flux"] for r in valid if r["novelty_flux"] is not None]
        pops = [r["pop_time"] for r in valid if r["pop_time"] is not None]
        alive = [r["alive_final"] for r in valid if r["alive_final"] is not None]
        muts = [r["mutation_events"] for r in valid if r["mutation_events"] is not None]
        out.append({
            "dose": dose,
            "n": len(group),
            "valid_n": len(valid),
            "mutation_events_median": statistics.median(muts) if muts else None,
            "shannon_median": round(statistics.median(shannon), 3) if shannon else None,
            "shannon_range": [min(shannon), max(shannon)] if shannon else None,
            "shannon_second_half_median": (
                round(statistics.median([r["shannon_second_half_median"] for r in valid
                                         if r["shannon_second_half_median"] is not None]), 3)
                if any(r["shannon_second_half_median"] is not None for r in valid) else None),
            "novelty_total": sum(novelty) if novelty else 0,
            "novelty_per_run": round(statistics.mean(novelty), 2) if novelty else None,
            "pop_time_median": round(statistics.median(pops), 1) if pops else None,
            "alive_median": round(statistics.median(alive), 1) if alive else None,
            "generation_length_median": (
                round(statistics.median([r["generation_length"] for r in valid
                                         if r["generation_length"] is not None]), 1)
                if any(r["generation_length"] is not None for r in valid) else None),
        })
    return out


def verdict(table: list[dict]) -> dict:
    """Критерии условия B из пре-регистрации — считаются, но не подменяют решение."""
    by = {item["dose"]: item for item in table}
    zero = by.get(0.0) or {}
    test = [item for item in table if item["dose"] and item["dose"] > 0]
    novelty_zero_at_m0 = (zero.get("novelty_total") in (0, None))
    novelty_grows = [item["novelty_total"] for item in test]
    monotone = all(b >= a for a, b in zip(novelty_grows, novelty_grows[1:])) if novelty_grows else None
    shannon_ok = all((item["shannon_median"] or 0) > 0.1 for item in test) if test else None
    pop0 = zero.get("pop_time_median")
    pop_005 = (by.get(0.05) or {}).get("pop_time_median")
    population_preserved = (
        (pop_005 is not None and pop0 is not None and pop_005 >= POPULATION_FLOOR * pop0)
        if (pop_005 is not None and pop0) else None)
    return {
        "novelty_zero_at_m0": novelty_zero_at_m0,
        "novelty_by_dose": novelty_grows,
        "novelty_monotone": monotone,
        "shannon_above_0.1_all_positive_doses": shannon_ok,
        "population_preserved_m0.05_vs_m0": population_preserved,
        "population_floor": POPULATION_FLOOR,
        "criterion_b_satisfied": bool(
            novelty_zero_at_m0 and monotone and shannon_ok and population_preserved),
        "note": "ρ (Спирмен) в B — контроль нейтральности, не критерий (критерий E)",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="mut_*.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [analyse(Path(f)) for f in files]
    table = by_dose(rows)
    payload = {
        "kind": "mutation_runs",
        "experiment": "E09_pond_mutation",
        "metric": "Shannon по меткам линий, поток новизны (окно 50 шагов), население",
        "note": "собрано scripts/mutation_matrix.py; критерии из reports/2026-10-24-mutation-plan.md",
        "rows": rows,
        "by_dose": table,
        "verdict": verdict(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'m':>7} {'n':>3} {'вал':>4} {'мут':>6} {'H_med':>7} {'новизна':>8} "
          f"{'pop_time':>10} {'alive':>7} {'поколение':>10}")
    for item in table:
        print(f"{item['dose']:>7} {item['n']:>3} {item['valid_n']:>4} "
              f"{str(item['mutation_events_median']):>6} {str(item['shannon_median']):>7} "
              f"{str(item['novelty_per_run']):>8} {str(item['pop_time_median']):>10} "
              f"{str(item['alive_median']):>7} {str(item['generation_length_median']):>10}")
    v = payload["verdict"]
    print(f"вердикт B: нулевая новизна при m=0 — {v['novelty_zero_at_m0']}, "
          f"монотонность — {v['novelty_monotone']}, Shannon > 0.1 — "
          f"{v['shannon_above_0.1_all_positive_doses']}, население сохранено — "
          f"{v['population_preserved_m0.05_vs_m0']} -> критерий "
          f"{'ВЫПОЛНЕН' if v['criterion_b_satisfied'] else 'НЕ выполнен'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
