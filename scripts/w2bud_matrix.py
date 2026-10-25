#!/usr/bin/env python
"""w2bud_matrix.py — агрегат W2-bud (клеточное почкование) против W1 (колониальное).

ОПРЕДЕЛЕНИЯ (формулы, а не слова) — введены 25.10 после расхождения трёх пересчётов:

| величина | формула | поле артефакта |
|---|---|---|
| живые клетки линии `t` | `cells(t) = type_counts["T<t>"]` | `summary.type_counts` |
| меток с ≥2 клетками | `#{t : cells(t) ≥ 2}` | `type_counts` |
| линия с данными | `cells(t) ≥ 5` **И** `lineage_spores[t] ≥ 1` | `type_counts` + `lineage_spores` |
| фитнес линии | `w(t) = lineage_spores[t] / cells(t)` — споры на ЖИВУЮ клетку | оба поля |
| возможность отбора | `I = Var(w) / mean(w)²` по линиям с данными | производное |
| ρ | `Spearman(tag_trait[t], w(t))` по линиям с данными (нужно ≥3) | `type_traits` |

**Почему `type_counts`, а не `lineage_fitness`.** Проверено на всех 20 артефактах:
`sum(type_counts) == final.alive_cells` (20/20), а `sum(lineage_fitness)` = 15623–18255 при
`born` 697–1959, то есть `lineage_fitness` — **накопленный счётчик рождений** (включая
повторные «зажигания» клеток, которые правило снова объявляет живыми после гибели по энергии),
а **не** число клеток. Как размер линии он не годится: у предковой линии там 13 087–18 000.

`cumulative_*`-поля считаются по `lineage_fitness` и печатаются **только для сверки**: они
воспроизводят альтернативный пересчёт и показывают, что это другая величина.

Запуск (из корня):

    python scripts/w2bud_matrix.py --src morphogenesis/experiments/E09_pond/w2bud \
        --out morphogenesis/experiments/E09_pond/w2bud_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import math
import re
import statistics
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _load_i_null():
    """Нуль-модель I Кроу (библиотекарь, Waples & Reed 2023): I > 0 ожидаемо при
    демографическом шуме, поэтому критерий — I_obs > I_null(95 %), а не I > 0."""
    path = _ROOT / "library" / "tools" / "i_null.py"
    spec = importlib.util.spec_from_file_location("i_null_tool", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

NAME = re.compile(r"w2bud2?_(?P<arm>colony|cell)_seed(?P<seed>\d+)\.json$")
MIN_CELLS = 5
MIN_LINEAGES = 5

METRIC = {
    "cells_field": "summary.type_counts[\"T<tag>\"] — ЖИВЫЕ клетки линии на конец прогона "
                   "(проверено: sum(type_counts) == final.alive_cells на 20/20 артефактах)",
    "tags_ge2": "#{t : type_counts[t] >= 2}",
    "lineage_with_data": "type_counts[t] >= 5 AND lineage_spores[t] >= 1",
    "w": "lineage_spores[t] / type_counts[t] (споры на живую клетку)",
    "crow_I": "Var(w) / mean(w)^2 по линиям с данными; при < 2 линиях I = 0 по построению",
    "rho": "Spearman(type_traits[t], w(t)) по линиям с данными (нужно >= 3)",
    "beta": "регрессия w/mean(w) на стандартизованный признак: w = 1 + b_lin*z + (b_quad/2)(z^2-1)",
    "manipulation_rho": "Spearman(type_traits[t], lineage_invested[t] / type_counts[t])",
    "cumulative_*": "то же по lineage_fitness — НЕ клетки, а накопленный счётчик рождений "
                    "(включает повторные зажигания); только для сверки, в критерии не входит",
}


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    n = len(pairs)
    if n < 3:
        return None

    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: values[i])
        out = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and values[order[j + 1]] == values[order[i]]:
                j += 1
            rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = rank
            i = j + 1
        return out

    xs = ranks([float(p[0]) for p in pairs])
    ys = ranks([float(p[1]) for p in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return (num / den) if den else None


def gradient(traits: list[float], w: list[float]) -> tuple[float | None, float | None]:
    n = len(traits)
    if n < 5:
        return None, None
    mean_t = sum(traits) / n
    sd_t = statistics.pstdev(traits)
    mean_w = sum(w) / n
    if sd_t <= 0 or mean_w <= 0:
        return None, None
    z = [(t - mean_t) / sd_t for t in traits]
    ww = [v / mean_w for v in w]
    x2 = [(v * v - 1.0) / 2.0 for v in z]
    s11 = sum(a * a for a in z)
    s22 = sum(b * b for b in x2)
    s12 = sum(a * b for a, b in zip(z, x2))
    t1 = sum(a * (wi - 1.0) for a, wi in zip(z, ww))
    t2 = sum(b * (wi - 1.0) for b, wi in zip(x2, ww))
    det = s11 * s22 - s12 * s12
    if abs(det) < 1e-12:
        return None, None
    return (round((t1 * s22 - t2 * s12) / det, 4),
            round((s11 * t2 - s12 * t1) / det, 4))


def crow(values: list[float]) -> float | None:
    if len(values) < 2:
        return 0.0            # одна линия -> разброса нет по построению
    mean = statistics.mean(values)
    if mean <= 0:
        return None
    return round(statistics.pvariance(values) / (mean * mean), 4)


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    summary = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
    traits = {str(k).lstrip("T"): float(v) for k, v in (summary.get("type_traits") or {}).items()}
    cells = {str(k).lstrip("T"): int(v) for k, v in (summary.get("type_counts") or {}).items()}
    cum = {str(k): int(v) for k, v in (summary.get("lineage_fitness") or {}).items()}
    spores = {str(k): int(v) for k, v in (summary.get("lineage_spores") or {}).items()}
    invested = {str(k): float(v) for k, v in (summary.get("lineage_invested") or {}).items()}

    def lineage_stats(size_field: dict[str, int], min_cells: int) -> dict:
        lineages = [t for t in size_field if size_field[t] >= min_cells and spores.get(t, 0) >= 1]
        w = [spores[t] / size_field[t] for t in lineages]
        pairs = [(traits[t], spores[t] / size_field[t]) for t in lineages if t in traits]
        rho = spearman(pairs) if len(pairs) >= 3 else None
        b_lin, b_quad = gradient([p[0] for p in pairs], [p[1] for p in pairs])
        return {
            "lineages": len(lineages),
            "crow_I": crow(w),
            "rho": round(rho, 3) if rho is not None else None,
            "beta_lin": b_lin,
            "beta_quad": b_quad,
        }

    final = lineage_stats(cells, MIN_CELLS)

    # --- нуль-модель для I: шум только в счёте потомков при фиксированных размерах линий ---
    lineages = [t for t in cells if cells[t] >= MIN_CELLS and spores.get(t, 0) >= 1]
    cells_list = [cells[t] for t in lineages]
    spores_sum = sum(spores[t] for t in lineages)
    rate = (spores_sum / sum(cells_list)) if cells_list and sum(cells_list) else 0.0
    i_null_95 = None
    if len(cells_list) >= 2 and rate > 0:
        null = _load_i_null().simulate_conditional(cells_list, rate, 2000, 7)
        if null:
            i_null_95 = round(_load_i_null().percentile(null, 0.95), 4)
    i_obs = final["crow_I"]
    i_ratio = (round(i_obs / i_null_95, 2)
               if i_obs is not None and i_null_95 else None)
    i_above_null = bool(i_obs is not None and i_null_95 is not None and i_obs > i_null_95)
    cumulative = lineage_stats(cum, MIN_CELLS)
    steps = int(summary.get("steps") or 600) or 600
    upd = {str(k): int(v) for k, v in (summary.get("lineage_invest_updates") or {}).items()}
    csteps = {str(k): int(v) for k, v in (summary.get("lineage_cell_steps") or {}).items()}

    def manip_rho_of(field: dict[str, float]) -> float | None:
        pairs = [(traits[t], field[t]) for t in cells
                 if t in field and cells[t] > 0 and field[t] > 0]
        return spearman(pairs) if len(pairs) >= 3 else None

    # (а) энергонезависимая: сколько РАЗ клетки линии инвестировали, на клетку
    upd_per_cell = {t: upd[t] / cells[t] for t in upd if t in cells and cells[t] > 0}
    # (б) накопленное вложение на КЛЕТКО-ШАГ линии (интеграл живых клеток по времени):
    #     это убирает смешение «накопленное за прогон / клетки в конце».
    #     Вариант «/(клетки*steps)» для Spearman эквивалентен (общий множитель) — проверено,
    #     поэтому он не годится как исправление (§10ap).
    inv_per_cell_step = {t: invested[t] / csteps[t]
                         for t in invested if t in csteps and csteps[t] > 0}
    # (в) текущая (накопленное/клетку) — для сравнения
    inv_per_cell = {t: invested[t] / cells[t] for t in invested if t in cells and cells[t] > 0}
    manip_updates = manip_rho_of(upd_per_cell)
    manip_per_step = manip_rho_of(inv_per_cell_step)
    manip_rho = manip_rho_of(inv_per_cell)
    sizes = sorted(cells.values(), reverse=True)
    return {
        "artifact": str(path).replace("\\", "/"),
        "arm": match.group("arm"),
        "seed": int(match.group("seed")),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
        "tags_total": len(cells),
        "tags_ge2": sum(1 for s in sizes if s >= 2),
        "tags_ge5": sum(1 for s in sizes if s >= 5),
        "top1_share": round(sizes[0] / sum(sizes), 4) if sizes and sum(sizes) else None,
        "lineages_with_data": final["lineages"],
        "crow_I": final["crow_I"],
        "rho": final["rho"],
        "beta_lin": final["beta_lin"],
        "beta_quad": final["beta_quad"],
        "manipulation_rho": round(manip_rho, 3) if manip_rho is not None else None,
        "manipulation_rho_updates": round(manip_updates, 3) if manip_updates is not None else None,
        "manipulation_rho_per_step": round(manip_per_step, 3) if manip_per_step is not None else None,
        "cell_steps_total": int(sum(csteps.values())) if csteps else None,
        "manipulation_n": len(inv_per_cell),
        "I_null_95": i_null_95,
        "I_obs": i_obs,
        "I_ratio": i_ratio,
        "I_above_null": i_above_null,
        "spores_total": int(sum(spores.values())) if spores else 0,
        "spores_lineages": len(spores),
        "cumulative": cumulative,
        "cumulative_fitness_sum": int(sum(cum.values())) if cum else 0,
        "born": (summary.get("final") or {}).get("born"),
        "valid": final["lineages"] >= MIN_LINEAGES,
        "invalid_reason": (None if final["lineages"] >= MIN_LINEAGES
                           else f"линий с данными {final['lineages']} < {MIN_LINEAGES}"),
        "budding_unit": (summary.get("config") or {}).get("budding_unit"),
    }


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ("colony", "cell"):
        group = [r for r in rows if r["arm"] == arm]
        if not group:
            continue
        valid = [r for r in group if r["valid"]]
        rhos = [r["rho"] for r in valid if r["rho"] is not None]
        betas = [r["beta_lin"] for r in valid if r["beta_lin"] is not None]
        agree = sum(1 for r in valid
                    if r["rho"] is not None and r["beta_lin"] is not None
                    and (r["rho"] > 0) == (r["beta_lin"] > 0))
        manip_ok = sum(1 for r in group
                       if r["manipulation_rho"] is not None
                       and abs(r["manipulation_rho"]) >= 0.2)
        out.append({
            "arm": arm,
            "runs": len(group),
            "valid_n": len(valid),
            # ВАЖНО: I > 0 считается по ВСЕМ прогонам (структурный критерий пре-регистрации),
            # а не только по валидным — иначе знаменатель подменяется.
            "crow_I_positive_k_all": sum(1 for r in group if (r["crow_I"] or 0) > 0),
            "crow_I_positive_k_valid": sum(1 for r in valid if (r["crow_I"] or 0) > 0),
            "crow_I_median_all": (round(statistics.median([r["crow_I"] for r in group
                                                           if r["crow_I"] is not None]), 4)
                                  if any(r["crow_I"] is not None for r in group) else None),
            "tags_ge2_median": round(statistics.median([r["tags_ge2"] for r in group]), 1),
            "tags_ge5_median": round(statistics.median([r["tags_ge5"] for r in group]), 1),
            "lineages_median": round(statistics.median([r["lineages_with_data"] for r in group]), 1),
            "rho_median": round(statistics.median(rhos), 3) if rhos else None,
            "rho_ge_0.3_k": sum(1 for v in rhos if v >= 0.3),
            "sign_agreement_k": agree,
            "manipulation_ok_k": manip_ok,
            "manipulation_ok_k_updates": sum(
                1 for r in group if r["manipulation_rho_updates"] is not None
                and abs(r["manipulation_rho_updates"]) >= 0.2),
            "manipulation_ok_k_per_step": sum(
                1 for r in group if r["manipulation_rho_per_step"] is not None
                and abs(r["manipulation_rho_per_step"]) >= 0.2),
            "I_obs_median": (round(statistics.median([r["I_obs"] for r in group
                                                      if r["I_obs"] is not None]), 4)
                             if any(r["I_obs"] is not None for r in group) else None),
            "I_null_95_median": (round(statistics.median([r["I_null_95"] for r in group
                                                          if r["I_null_95"] is not None]), 4)
                                 if any(r["I_null_95"] is not None for r in group) else None),
            "I_ratio_median": (round(statistics.median([r["I_ratio"] for r in group
                                                        if r["I_ratio"] is not None]), 2)
                               if any(r["I_ratio"] is not None for r in group) else None),
            "I_above_null_k_all": sum(1 for r in group if r["I_above_null"]),
        })
    return out


def criteria(table: list[dict]) -> dict:
    by = {item["arm"]: item for item in table}
    cell = by.get("cell") or {}
    colony = by.get("colony") or {}
    return {
        "I_above_null": bool((cell.get("I_obs_median") or 0) > (cell.get("I_null_95_median") or 0)),
        "I_above_null_7_of_10": bool((cell.get("I_above_null_k_all") or 0) >= 7),
        "I_positive_all_7_of_10": bool((cell.get("crow_I_positive_k_all") or 0) >= 7),
        "I_positive_valid_7_of_10": bool((cell.get("crow_I_positive_k_valid") or 0) >= 7),
        "w1_control_I_zero_all": bool((colony.get("crow_I_positive_k_all") or 0) == 0),
        "manipulation_gate_7_of_10": bool((cell.get("manipulation_ok_k") or 0) >= 7),
        "manipulation_gate_7_of_10_updates": bool(
            (cell.get("manipulation_ok_k_updates") or 0) >= 7),
        "manipulation_gate_7_of_10_per_step": bool(
            (cell.get("manipulation_ok_k_per_step") or 0) >= 7),
        "rho_median_ge_03": bool((cell.get("rho_median") or 0) >= 0.3),
        "rho_ge_03_in_7_of_10_valid": bool((cell.get("rho_ge_0.3_k") or 0) >= 7),
        "sign_agreement_7_of_10_valid": bool((cell.get("sign_agreement_k") or 0) >= 7),
        "note": ("структурный критерий пре-регистрации — I > 0 в >=7/10 ВСЕХ сидов; "
                 "критерий отклика (rho) — только по валидным сидам (>=5 линий с данными) "
                 "и только при пройденном гейте манипуляции (>=0.2 в >=7/10)"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / "w2bud*.json")))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    table = by_arm(rows)
    payload = {
        "kind": "w2bud_runs",
        "world": "W2-bud (клеточное почкование); числа НЕ сопоставимы с W1 напрямую",
        "metric": METRIC,
        "rows": rows,
        "by_arm": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'плечо':>7} {'сид':>3} {'меток':>5} {'>=2':>4} {'>=5':>4} {'линий':>5} {'I':>7} "
          f"{'rho':>6} {'манип':>6} {'cum линий':>9} {'cum I':>7}")
    for r in sorted(rows, key=lambda x: (x["arm"], x["seed"])):
        print(f"{r['arm']:>7} {r['seed']:>3} {r['tags_total']:>5} {r['tags_ge2']:>4} "
              f"{r['tags_ge5']:>4} {r['lineages_with_data']:>5} {str(r['crow_I']):>7} "
              f"{str(r['rho']):>6} {str(r['manipulation_rho']):>6} "
              f"{r['cumulative']['lineages']:>9} {str(r['cumulative']['crow_I']):>7}")
    print()
    print(f"{'плечо':>7} {'n':>3} {'вал':>4} {'I>0 всех':>9} {'I>0 вал':>8} {'медиана I':>10} "
          f"{'>=2 мед':>8} {'линий мед':>10} {'rho мед':>8} {'манип':>6}")
    for item in table:
        print(f"{item['arm']:>7} {item['runs']:>3} {item['valid_n']:>4} "
              f"{item['crow_I_positive_k_all']:>9} {item['crow_I_positive_k_valid']:>8} "
              f"{str(item['crow_I_median_all']):>10} {item['tags_ge2_median']:>8} "
              f"{item['lineages_median']:>10} {str(item['rho_median']):>8} "
              f"{item['manipulation_ok_k']:>6}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
