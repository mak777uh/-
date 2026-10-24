#!/usr/bin/env python
"""selection_matrix.py — условие E: отбор по наследуемому признаку.

Зачем: §10ad закрыл условие B как **нейтральную** изменчивость (`tag_trait` нигде не
читался, ρ ≈ 0 — контроль). Для E признак должен читаться миром, и вопрос ставится так:
растёт ли фитнес линии с признаком.

Метрики (по пре-регистрации `reports/2026-10-24-selection-plan.md`):

* **фитнес линии = число спор** (`lineage_spores`), не клеток: клетки, выросшие по
  правилу, родителя не имеют, а единица размножения у нас — почкование;
* **ρ = Spearman(tag_trait, lineage_spores)** по линиям с ≥ 3 спорами; нужно ≥ 10 таких
  линий, иначе `null` и прогон невалиден по метрике (не «отбора нет»);
* **градиент отбора (Lande & Arnold 1983)**: регрессия относительного фитнеса
  `w = spores / mean(spores)` на стандартизованный признак `z`:
  `w = 1 + β_lin·z + (β_quad/2)·(z²−1)`; β_quad < 0 — стабилизирующий отбор,
  β_quad > 0 — дизруптивный;
* **манипуляционная проверка**: мир должен РЕАЛЬНО читать признак — иначе серия
  невалидна. Здесь: корреляция признака с вложенной энергией линии
  (`lineage_invested`), |ρ| ≥ 0.2 или разница между верхним и нижним квантилем признака
  ≥ 10 %.

Запуск (из корня):

    python scripts/selection_matrix.py --src morphogenesis/experiments/E09_pond \
        --glob "sel_*.json" --out morphogenesis/experiments/E09_pond/selection_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"sel_eps(?P<eps>\d+)_seed(?P<seed>\d+)\.json$")
MIN_SPORES = 1        # >= 1 спора на линию
MIN_CELLS = 5         # >= 5 живых клеток у линии (иначе шум размера)
MIN_LINEAGES = 10
MANIP_RHO = 0.2
MANIP_SHARE = 0.10


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


def selection_gradient(traits: list[float], spores: list[float]) -> tuple[float | None, float | None]:
    """β_lin и β_quad из регрессии относительного фитнеса на стандартизованный признак."""
    n = len(traits)
    if n < 5:
        return None, None
    mean_t = sum(traits) / n
    sd_t = statistics.pstdev(traits)
    if sd_t <= 0:
        return None, None
    mean_w = sum(spores) / n
    if mean_w <= 0:
        return None, None
    z = [(t - mean_t) / sd_t for t in traits]
    w = [s / mean_w for s in spores]
    # две регрессора: z и (z^2 - 1)/2 (центрированный квадрат)
    x1 = z
    x2 = [(v * v - 1.0) / 2.0 for v in z]
    # OLS через нормальные уравнения 2x2 (свободный член не нужен: w центрирован ~1)
    s11 = sum(a * a for a in x1)
    s22 = sum(b * b for b in x2)
    s12 = sum(a * b for a, b in zip(x1, x2))
    t1 = sum(a * (wi - 1.0) for a, wi in zip(x1, w))
    t2 = sum(b * (wi - 1.0) for b, wi in zip(x2, w))
    det = s11 * s22 - s12 * s12
    if abs(det) < 1e-12:
        return None, None
    beta_lin = (t1 * s22 - t2 * s12) / det
    beta_quad = (s11 * t2 - s12 * t1) / det
    return round(beta_lin, 4), round(beta_quad, 4)


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    eps_code = int(match.group("eps"))
    eps = eps_code / 100.0
    traits = summary.get("type_traits") or {}
    spores_map = summary.get("lineage_spores")
    cells_map = summary.get("lineage_fitness") or {}
    counts_map = {str(k).lstrip("T"): v for k, v in (summary.get("type_counts") or {}).items()}
    invested_map = summary.get("lineage_invested") or {}
    fitness_source = "lineage_spores"
    if not isinstance(spores_map, dict):
        spores_map = cells_map
        fitness_source = "lineage_fitness (клетки; поле lineage_spores отсутствует)"
    pairs: list[tuple[float, float]] = []
    traits_used: list[float] = []
    spores_used: list[float] = []
    for tag, trait in traits.items():
        key = str(tag).lstrip("T")
        spores = spores_map.get(key, spores_map.get(tag))
        cells = counts_map.get(key)
        if spores is None or cells is None:
            continue
        # фитнес линии = споры НА ЖИВУЮ КЛЕТКУ (нормировка на размер: иначе отбирается
        # размер линии, а не признак); порог данных — >= 1 спора и >= 5 клеток
        if float(spores) < MIN_SPORES or float(cells) < MIN_CELLS:
            continue
        w = float(spores) / float(cells)
        pairs.append((float(trait), w))
        traits_used.append(float(trait))
        spores_used.append(w)
    row: dict = {
        "artifact": f"morphogenesis/experiments/E09_pond/{path.name}",
        "eps": eps,
        "seed": int(match.group("seed")),
        "fitness_source": fitness_source,
        "lineages_with_min_spores": len(pairs),
        "valid_metric": True,
        "invalid_reason": None,
        "rho": None,
        "beta_lin": None,
        "beta_quad": None,
        "manipulation_rho": None,
        "manipulation_ok": None,
        "crow_I": None,
        "pop_time": summary.get("pop_time"),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
    }
    # СЫРЫЕ (ungated) значения: считаются всегда, даже если прогон невалиден по метрике.
    # §2/§6b: число, названное в §-разделе, обязано быть в артефакте, а не в памяти.
    raw_manip = [(float(traits[t]), float(invested_map[str(t).lstrip("T")])
                  / max(1, int(counts_map.get(str(t).lstrip("T"), 0))))
                 for t in traits
                 if str(t).lstrip("T") in invested_map
                 and int(counts_map.get(str(t).lstrip("T"), 0)) > 0
                 and float(invested_map[str(t).lstrip("T")]) > 0]
    raw_rho = spearman(raw_manip)
    raw_ws = [float(spores_map.get(str(t).lstrip("T"), 0))
              / max(1, int(counts_map.get(str(t).lstrip("T"), 0)))
              for t in traits if int(counts_map.get(str(t).lstrip("T"), 0)) >= MIN_CELLS]
    raw_I = None
    if raw_ws:
        mean_w = sum(raw_ws) / len(raw_ws)
        if mean_w > 0:
            raw_I = round(statistics.pvariance(raw_ws) / (mean_w * mean_w), 4)
    row["raw"] = {
        "manipulation_rho": round(raw_rho, 3) if raw_rho is not None else None,
        "manipulation_n": len(raw_manip),
        "crow_I": raw_I,
        "lineages_with_cells": sum(1 for t in traits
                                   if int(counts_map.get(str(t).lstrip("T"), 0)) >= MIN_CELLS),
        "lineages_with_cells_and_spores": len(pairs),
        "spores_total": int(sum(float(v) for v in spores_map.values())) if spores_map else 0,
        "spores_lineages": len(spores_map) if spores_map else 0,
        "tags_total": len(traits),
        "note": "сырые значения считаются без гейта валидности: они описывают, ЧТО есть, а не то, можно ли считать rho",
    }
    if len(pairs) < MIN_LINEAGES:
        row["valid_metric"] = False
        row["invalid_reason"] = (f"линий с >= {MIN_SPORES} спорами {len(pairs)} < {MIN_LINEAGES} "
                                 "(мало точек: rho и градиент не считаются)")
        return row
    row["rho"] = round(spearman(pairs), 3) if spearman(pairs) is not None else None
    mean_w = sum(spores_used) / len(spores_used)
    var_w = statistics.pvariance(spores_used)
    # opportunity for selection (Crow): отбор не может работать при нулевом разбросе
    row["crow_I"] = round(var_w / (mean_w * mean_w), 4) if mean_w > 0 else None
    beta_lin, beta_quad = selection_gradient(traits_used, spores_used)
    row["beta_lin"] = beta_lin
    row["beta_quad"] = beta_quad
    # манипуляционная проверка: признак должен быть связан с вложенной энергией линии
    manip_pairs = [(float(traits[t]), float(invested_map[t])) for t in traits
                   if t in invested_map and float(invested_map[t]) > 0]
    if len(manip_pairs) >= MIN_LINEAGES:
        row["manipulation_rho"] = round(spearman(manip_pairs), 3) if spearman(manip_pairs) else None
        row["manipulation_ok"] = bool(row["manipulation_rho"] is not None
                                      and abs(row["manipulation_rho"]) >= MANIP_RHO)
    return row


def by_eps(rows: list[dict]) -> list[dict]:
    out = []
    for eps in sorted({r["eps"] for r in rows}):
        group = [r for r in rows if r["eps"] == eps]
        usable = [r for r in group if r["valid_metric"]]
        rhos = [r["rho"] for r in usable if r["rho"] is not None]
        betas = [r["beta_lin"] for r in usable if r["beta_lin"] is not None]
        quads = [r["beta_quad"] for r in usable if r["beta_quad"] is not None]
        agree = sum(1 for r in usable
                    if r["rho"] is not None and r["beta_lin"] is not None
                    and (r["rho"] > 0) == (r["beta_lin"] > 0))
        out.append({
            "eps": eps,
            "runs": len(group),
            "valid_n": len(usable),
            "invalid_n": len(group) - len(usable),
            "rho_median": round(statistics.median(rhos), 3) if rhos else None,
            "rho_range": [min(rhos), max(rhos)] if rhos else None,
            "rho_ge_0.3_k": sum(1 for v in rhos if v >= 0.3),
            "beta_lin_median": round(statistics.median(betas), 4) if betas else None,
            "beta_quad_median": round(statistics.median(quads), 4) if quads else None,
            "sign_agreement_k": agree,
            "manipulation_ok_k": sum(1 for r in usable if r["manipulation_ok"]),
            "crow_I_median": (round(statistics.median([r["crow_I"] for r in usable
                                                       if r["crow_I"] is not None]), 4)
                              if any(r["crow_I"] is not None for r in usable) else None),
        })
    return out


def criteria(table: list[dict]) -> dict:
    by = {item["eps"]: item for item in table}
    test = by.get(0.1) or {}
    control = by.get(0.0) or {}
    res = {
        "manipulation_ok": bool((test.get("manipulation_ok_k") or 0) >= 7),
        "opportunity_for_selection": bool((test.get("crow_I_median") or 0) > 0),
        "e_confirmed": bool((test.get("rho_median") or 0) >= 0.3
                            and (test.get("rho_ge_0.3_k") or 0) >= 7
                            and (test.get("sign_agreement_k") or 0) >= 7
                            and (test.get("manipulation_ok_k") or 0) >= 7),
        "control_neutral": bool(abs(control.get("rho_median") or 0) < 0.3),
        "note": ("три уровня: (1) мир прочитал признак — |rho(trait, invested)| >= 0.2 в >= 7/10; "
                 "(2) есть из чего выбирать — медиана индекса Кроу I > 0; "
                 "(3) есть отклик — медиана rho(trait, споры/клетку) >= 0.3, rho >= 0.3 в >= 7/10 "
                 "и знак beta_lin совпадает с rho в >= 7/10"),
    }
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="sel_*.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    table = by_eps(rows)
    payload = {
        "kind": "selection_runs",
        "experiment": "E09_pond_selection",
        "metric": ("фитнес линии = число спор; rho = Spearman(trait, spores); "
                   "beta_lin/beta_quad — градиент отбора Lande & Arnold"),
        "note": "собрано scripts/selection_matrix.py; критерии из reports/2026-10-24-selection-plan.md",
        "rows": rows,
        "by_eps": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'eps':>5} {'n':>3} {'вал':>4} {'rho_med':>8} {'rho>=.3':>8} {'b_lin':>8} {'b_quad':>8} {'манип':>6}")
    for item in table:
        print(f"{item['eps']:>5} {item['runs']:>3} {item['valid_n']:>4} "
              f"{str(item['rho_median']):>8} {item['rho_ge_0.3_k']:>8} "
              f"{str(item['beta_lin_median']):>8} {str(item['beta_quad_median']):>8} "
              f"{item['manipulation_ok_k']:>6}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
