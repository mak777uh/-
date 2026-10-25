#!/usr/bin/env python
"""w2bud_matrix.py — агрегат W2-bud (клеточное почкование) против W1 (колониальное).

Зачем: §10ag показал, что в W1 единица изменчивости (метка) ≠ единица размножения
(почкование колонии): все споры у одной линии, `I = Var(w)/mean(w)² = 0`, отбор по
клеточному признаку неизмерим. W2-bud делает единицей размножения клетку.

Критерий (пре-регистрация `reports/2026-10-25-w2bud-plan.md`, поправка от 25.10 — ДО серии):

* первичный: `I = Var(w)/mean(w)² > 0` (структурный результат);
* `ρ` считается по каждому сиду на доступных линиях (≥ 5 линий с ≥ 1 спорой и ≥ 5 клетками);
* вердикт по 10 сидам: медиана `ρ ≥ 0.3` **и** `ρ ≥ 0.3` в ≥ 7/10 сидов **и** согласие знака с
  `β_lin` в ≥ 7/10 сидов **и** манипуляция `|ρ(trait, вложение/клетку)| ≥ 0.2` в ≥ 7/10.

Запуск (из корня):

    python scripts/w2bud_matrix.py --src morphogenesis/experiments/E09_pond/w2bud \
        --out morphogenesis/experiments/E09_pond/w2bud_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
from pathlib import Path

NAME = re.compile(r"w2bud_(?P<arm>colony|cell)_seed(?P<seed>\d+)\.json$")
MIN_CELLS = 5
MIN_LINEAGES = 5


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


def analyse(path: Path) -> dict | None:
    match = NAME.search(path.name)
    if not match:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    traits = {str(k).lstrip("T"): float(v) for k, v in (summary.get("type_traits") or {}).items()}
    counts = {str(k).lstrip("T"): int(v) for k, v in (summary.get("type_counts") or {}).items()}
    spores = {str(k): int(v) for k, v in (summary.get("lineage_spores") or {}).items()}
    invested = {str(k): float(v) for k, v in (summary.get("lineage_invested") or {}).items()}

    sizes = sorted(counts.values(), reverse=True)
    lineages = [t for t in counts if counts[t] >= MIN_CELLS and spores.get(t, 0) >= 1]
    w = [spores[t] / counts[t] for t in lineages]
    pairs = [(traits[t], spores[t] / counts[t]) for t in lineages if t in traits]
    rho = spearman(pairs) if len(pairs) >= 3 else None
    beta_lin, beta_quad = gradient([p[0] for p in pairs], [p[1] for p in pairs])
    mean_w = statistics.mean(w) if w else 0.0
    crow_i = (round(statistics.pvariance(w) / (mean_w * mean_w), 4)
              if w and mean_w > 0 else None)
    manip = [(traits[t], invested[t] / counts[t]) for t in counts
             if t in invested and counts[t] > 0 and invested[t] > 0]
    manip_rho = spearman(manip) if len(manip) >= 3 else None
    return {
        "artifact": f"morphogenesis/experiments/E09_pond/w2bud/{path.name}",
        "arm": match.group("arm"),
        "seed": int(match.group("seed")),
        "tags": len(sizes),
        "tags_ge2": sum(1 for s in sizes if s >= 2),
        "tags_ge5": sum(1 for s in sizes if s >= 5),
        "lineages_with_data": len(lineages),
        "crow_I": crow_i,
        "rho": round(rho, 3) if rho is not None else None,
        "beta_lin": beta_lin,
        "beta_quad": beta_quad,
        "manipulation_rho": round(manip_rho, 3) if manip_rho is not None else None,
        "manipulation_n": len(manip),
        "spores_total": int(sum(spores.values())) if spores else 0,
        "spores_lineages": len(spores),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
        "pop_time": summary.get("pop_time"),
        "budding_unit": (summary.get("config") or {}).get("budding_unit"),
        "valid": len(lineages) >= MIN_LINEAGES,
        "invalid_reason": (None if len(lineages) >= MIN_LINEAGES
                           else f"линий с данными {len(lineages)} < {MIN_LINEAGES}"),
    }


def by_arm(rows: list[dict]) -> list[dict]:
    out = []
    for arm in ("colony", "cell"):
        group = [r for r in rows if r["arm"] == arm]
        if not group:
            continue
        usable = [r for r in group if r["valid"]]
        rhos = [r["rho"] for r in usable if r["rho"] is not None]
        betas = [r["beta_lin"] for r in usable if r["beta_lin"] is not None]
        agree = sum(1 for r in usable
                    if r["rho"] is not None and r["beta_lin"] is not None
                    and (r["rho"] > 0) == (r["beta_lin"] > 0))
        manip = sum(1 for r in usable
                    if r["manipulation_rho"] is not None and abs(r["manipulation_rho"]) >= 0.2)
        out.append({
            "arm": arm,
            "runs": len(group),
            "valid_n": len(usable),
            "tags_ge2_median": (round(statistics.median([r["tags_ge2"] for r in group]), 1)
                                if group else None),
            "lineages_median": (round(statistics.median([r["lineages_with_data"] for r in group]), 1)
                                if group else None),
            "crow_I_median": (round(statistics.median([r["crow_I"] for r in usable
                                                       if r["crow_I"] is not None]), 4)
                              if any(r["crow_I"] is not None for r in usable) else None),
            "crow_I_positive_k": sum(1 for r in usable if (r["crow_I"] or 0) > 0),
            "rho_median": round(statistics.median(rhos), 3) if rhos else None,
            "rho_ge_0.3_k": sum(1 for v in rhos if v >= 0.3),
            "sign_agreement_k": agree,
            "manipulation_ok_k": manip,
        })
    return out


def criteria(table: list[dict]) -> dict:
    by = {item["arm"]: item for item in table}
    cell = by.get("cell") or {}
    colony = by.get("colony") or {}
    return {
        "I_positive_in_w2bud": bool((cell.get("crow_I_positive_k") or 0) >= 7),
        "rho_median_ge_03": bool((cell.get("rho_median") or 0) >= 0.3),
        "rho_ge_03_in_7_of_10": bool((cell.get("rho_ge_0.3_k") or 0) >= 7),
        "sign_agreement_7_of_10": bool((cell.get("sign_agreement_k") or 0) >= 7),
        "manipulation_ok_7_of_10": bool((cell.get("manipulation_ok_k") or 0) >= 7),
        "w1_control_I_zero": bool((colony.get("crow_I_median") or 0) == 0),
        "note": ("успех W2-bud: I>0 в >=7/10 сидов, медиана rho >= 0.3, rho >= 0.3 в >=7/10, "
                 "согласие знака с beta_lin в >=7/10, манипуляция >=0.2 в >=7/10; "
                 "контроль W1: I = 0"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / "w2bud_*.json")))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    table = by_arm(rows)
    payload = {
        "kind": "w2bud_runs",
        "world": "W2-bud (клеточное почкование); числа НЕ сопоставимы с W1 напрямую",
        "metric": "w = споры/клетки линии; I = Var(w)/mean(w)^2; rho(trait, w); beta_lin/quad",
        "note": "собрано scripts/w2bud_matrix.py; критерий из reports/2026-10-25-w2bud-plan.md",
        "rows": rows,
        "by_arm": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | прогонов {len(rows)}")
    print(f"{'плечо':>8} {'n':>3} {'вал':>4} {'>=2 клеток':>11} {'линий':>6} {'I мед.':>8} "
          f"{'I>0':>4} {'rho мед.':>9} {'rho>=.3':>8} {'знак':>5} {'манип':>6}")
    for item in table:
        print(f"{item['arm']:>8} {item['runs']:>3} {item['valid_n']:>4} {item['tags_ge2_median']:>11} "
              f"{item['lineages_median']:>6} {str(item['crow_I_median']):>8} {item['crow_I_positive_k']:>4} "
              f"{str(item['rho_median']):>9} {item['rho_ge_0.3_k']:>8} {item['sign_agreement_k']:>5} "
              f"{item['manipulation_ok_k']:>6}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
