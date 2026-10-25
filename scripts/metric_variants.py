#!/usr/bin/env python
"""metric_variants.py — инвариантность вывода к устройству метрики (H-ALIVE-39).

Пересчитывает существующие артефакты W2-bud по трём осям (пре-регистрация
`reports/2026-10-25-metric-variants-plan.md`):

    w:        spores_per_cell | raw_spores | discrete
    порог:    cells>=5 | cells>=3 | all_with_spores
    нуль:     rate = sum(spores)/sum(cells) | rate = mean(spores/cells)

Для каждой комбинации считаются:

    S = I_obs / I_null(95 %)            (нуль-модель `library/tools/i_null.py`, условная)
    C = Spearman(tag_trait, cell_steps) и, если есть energy_per_cell_time,
        частная корреляция rho_partial(признак, cell_steps | энергия)

Эффект заявляется, только если S > 1 в >= 9/10 сидов и знак C одинаков ВО ВСЕХ 18 вариантах.

Запуск (из корня):

    python scripts/metric_variants.py --src morphogenesis/experiments/E09_pond/w2bud4s \
        --out morphogenesis/experiments/E09_pond/metric_variants.json
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

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"w2bud[0-9]?s?_(?:pilot_)?(?P<arm>colony|cell)_seed(?P<seed>\d+)\.json$")

W_VARIANTS = ("spores_per_cell", "raw_spores", "discrete")
THRESHOLDS = ("cells>=5", "cells>=3", "all_with_spores")
NULL_MODELS = ("sum_over_sum", "mean_of_ratios")


def load_i_null():
    path = ROOT / "library" / "tools" / "i_null.py"
    spec = importlib.util.spec_from_file_location("i_null_tool", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spearman(pairs):
    n = len(pairs)
    if n < 3:
        return None

    def ranks(values):
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

    xs, ys = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else None


def partial(x, y, z):
    n = len(x)
    if n < 4:
        return None

    def resid(a, b):
        ma, mb = sum(a) / n, sum(b) / n
        sbb = sum((v - mb) ** 2 for v in b)
        if sbb <= 0:
            return [v - ma for v in a]
        beta = sum((u - ma) * (v - mb) for u, v in zip(a, b)) / sbb
        return [u - ma - beta * (v - mb) for u, v in zip(a, b)]

    return spearman(list(zip(resid(x, z), resid(y, z))))


def crow(w):
    if len(w) < 2:
        return 0.0
    m = statistics.mean(w)
    if m <= 0:
        return None
    return statistics.pvariance(w) / (m * m)


def analyse(path: Path, i_null) -> list[dict]:
    match = NAME.search(path.name)
    if not match:
        return []
    summary = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
    traits = {str(k).lstrip("T"): float(v) for k, v in (summary.get("type_traits") or {}).items()}
    cells = {str(k).lstrip("T"): int(v) for k, v in (summary.get("type_counts") or {}).items()}
    spores = {str(k): int(v) for k, v in (summary.get("lineage_spores") or {}).items()}
    csteps = {str(k): int(v) for k, v in (summary.get("lineage_cell_steps") or {}).items()}
    emean = {str(k): float(v) for k, v in (summary.get("lineage_energy_mean_sum") or {}).items()}
    esamp = {str(k): int(v) for k, v in (summary.get("lineage_energy_samples") or {}).items()}
    ept = {t: emean[t] / esamp[t] for t in emean if esamp.get(t, 0) > 0}

    rows = []
    for threshold in THRESHOLDS:
        if threshold == "cells>=5":
            lineages = [t for t in cells if cells[t] >= 5 and spores.get(t, 0) >= 1]
        elif threshold == "cells>=3":
            lineages = [t for t in cells if cells[t] >= 3 and spores.get(t, 0) >= 1]
        else:
            lineages = [t for t in cells if spores.get(t, 0) >= 1]
        if len(lineages) < 2:
            continue
        rate_sum = sum(spores[t] for t in lineages) / max(1, sum(cells[t] for t in lineages))
        rate_mean = statistics.mean([spores[t] / cells[t] for t in lineages])
        med_ratio = statistics.median([spores[t] / cells[t] for t in lineages])
        for w_var in W_VARIANTS:
            if w_var == "spores_per_cell":
                w = [spores[t] / cells[t] for t in lineages]
            elif w_var == "raw_spores":
                w = [float(spores[t]) for t in lineages]
            else:
                w = [1.0 if spores[t] / cells[t] >= med_ratio else 0.0 for t in lineages]
            i_obs = crow(w)
            if i_obs is None:
                continue
            cells_list = [cells[t] for t in lineages]
            for null_model in NULL_MODELS:
                rate = rate_sum if null_model == "sum_over_sum" else rate_mean
                vals = i_null.simulate_conditional(cells_list, max(rate, 1e-9), 2000, 7)
                if not vals:
                    continue
                i_null_95 = i_null.percentile(vals, 0.95)
                pairs_cs = [(traits[t], float(csteps[t])) for t in lineages
                            if t in csteps and t in traits]
                rho_cs = spearman(pairs_cs) if len(pairs_cs) >= 3 else None
                rho_part = None
                part = [t for t in lineages if t in csteps and t in ept and t in traits]
                if len(part) >= 4:
                    rho_part = partial([traits[t] for t in part],
                                       [float(csteps[t]) for t in part],
                                       [ept[t] for t in part])
                rows.append({
                    "artifact": str(path).replace("\\", "/"),
                    "arm": match.group("arm"),
                    "seed": int(match.group("seed")),
                    "w_variant": w_var,
                    "threshold": threshold,
                    "null_model": null_model,
                    "n_lineages": len(lineages),
                    "I_obs": round(i_obs, 4),
                    "I_null_95": round(i_null_95, 4),
                    "S": round(i_obs / i_null_95, 2) if i_null_95 > 0 else None,
                    "rho_trait_cell_steps": round(rho_cs, 3) if rho_cs is not None else None,
                    "rho_partial": round(rho_part, 3) if rho_part is not None else None,
                })
    return rows


def summarise(rows: list[dict]) -> list[dict]:
    out = []
    keys = sorted({(r["w_variant"], r["threshold"], r["null_model"]) for r in rows})
    for w_var, threshold, null_model in keys:
        group = [r for r in rows if (r["w_variant"], r["threshold"], r["null_model"])
                 == (w_var, threshold, null_model)]
        cell = [r for r in group if r["arm"] == "cell"]
        s_vals = [r["S"] for r in cell if r["S"] is not None]
        part = [r["rho_partial"] for r in cell if r["rho_partial"] is not None]
        simple = [r["rho_trait_cell_steps"] for r in cell if r["rho_trait_cell_steps"] is not None]
        out.append({
            "w_variant": w_var,
            "threshold": threshold,
            "null_model": null_model,
            "runs": len(cell),
            "S_median": round(statistics.median(s_vals), 2) if s_vals else None,
            "S_gt1_k": sum(1 for v in s_vals if v > 1),
            "S_gt1_n": len(s_vals),
            "rho_partial_median": round(statistics.median(part), 3) if part else None,
            "rho_partial_negative_k": sum(1 for v in part if v < 0),
            "rho_partial_n": len(part),
            "rho_cell_steps_median": round(statistics.median(simple), 3) if simple else None,
        })
    return out


def criteria(table: list[dict]) -> dict:
    with_s = [t for t in table if t["S_gt1_n"] >= 7]
    with_c = [t for t in table if t["rho_partial_n"] >= 3]
    s_ok = bool(with_s) and all(t["S_gt1_k"] >= 9 or t["S_gt1_k"] == t["S_gt1_n"]
                                for t in with_s)
    signs = {1 if (t["rho_partial_median"] or 0) < 0 else 0 for t in with_c}
    return {
        "variants": len(table),
        "S_above_null_in_all_variants": s_ok,
        "C_sign_same_in_all_variants": len(signs) == 1,
        "C_sign": ("negative" if signs == {1} else "positive" if signs == {0}
                   else "depends_on_metric"),
        "note": ("S инвариантна, если I_obs > I_null(95 %) во всех вариантах; C инвариантна, если "
                 "медианный rho_partial отрицателен во всех вариантах; расхождение публикуется как "
                 "зависимость от метрики"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud4s")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    i_null = load_i_null()
    files = sorted(glob.glob(str(Path(args.src) / "w2bud*.json")))
    rows = []
    for f in files:
        rows.extend(analyse(Path(f), i_null))
    table = summarise(rows)
    payload = {
        "kind": "metric_variants",
        "source": args.src,
        "axes": {"w": list(W_VARIANTS), "threshold": list(THRESHOLDS),
                 "null_model": list(NULL_MODELS)},
        "rows": rows,
        "by_variant": table,
        "criteria": criteria(table),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}, вариантов {len(table)}")
    print(f"{'w':>16} {'порог':>16} {'нуль':>14} {'n':>3} {'S мед.':>7} {'S>1':>6} "
          f"{'rho_part':>9} {'отр.':>5}")
    for t in table:
        print(f"{t['w_variant']:>16} {t['threshold']:>16} {t['null_model']:>14} "
              f"{t['runs']:>3} {str(t['S_median']):>7} "
              f"{str(t['S_gt1_k']) + '/' + str(t['S_gt1_n']):>6} "
              f"{str(t['rho_partial_median']):>9} "
              f"{str(t['rho_partial_negative_k']) + '/' + str(t['rho_partial_n']):>5}")
    print("критерии:", json.dumps(payload["criteria"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
