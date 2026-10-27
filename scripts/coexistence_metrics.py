#!/usr/bin/env python
"""coexistence_metrics.py — метрики сосуществования линий из СУЩЕСТВУЮЩИХ артефактов (0 GPU).

Зачем: «число линий с данными» — величина с произвольным порогом (≥5 клеток) и она обманывает:
в серии с одним бутоном медиана меток 40.5, а эффективное число линий 1/Σp² = 1.53. Нужны метрики,
которые не зависят от порога и от размера мира.

**Формулы и знаменатели (каждая метрика подписана, §3c):**

1. `effective_lineages = 1 / Σ p_i²` — обратный индекс Симпсона по долям клеток линий;
   `p_i = cells_i / Σ_j cells_j`; знаменатель — **все живые клетки прогона** (не только крупные линии).
2. `pielou_evenness = H / ln S`, где `H = −Σ p_i ln p_i`, `S` — число линий с ≥1 клеткой;
   знаменатель — `ln S`, то есть метрика нормирована на число линий.
3. `rarefied_richness(n)` — ожидаемое число линий при выборке `n` клеток **без возвращения**
   (гипергеометрическое разрежение): `E[S_n] = Σ_i [1 − C(N−N_i, n)/C(N, n)]`, `N` — все клетки;
   знаменатель — фиксированный бюджет `n` (одинаковый для всех прогонов, чтобы размер мира не влиял).
4. `dominant_share = max_i p_i` — доля крупнейшей линии; знаменатель — все клетки.
5. `coexistence_steps` — число шагов лога, где в мире **больше одной** метки (`types_alive > 1`);
   знаменатель — `steps` прогона. Это прокси «сколько времени в мире сосуществовали разные линии»;
   он не требует порога и считается по `log`.
6. `lines_ge_5` — число линий с ≥5 клетками (старая величина, для сравнения).

Запуск (из корня repo):

    python scripts/coexistence_metrics.py --out morphogenesis/experiments/E09_pond/coexistence_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from pathlib import Path

SERIES = {
    "cell_onebud": "w2bud_onebud/w2bud_onebud_cell_seed*.json",
    "cell_uniform": "w2bud_rep_uniform/w2bud5_cell_seed*.json",
    "colony": "w2bud_rep_uniform/w2bud5_colony_seed*.json",
    "pair_same_tag": "w2bud_pair/w2bud_pair_pair_seed*.json",
    "pair_any_tag": "w2bud_pairany/w2bud_pairany_pair_seed*.json",
    "n3_dev": "w2budd2/w2budd2_cell_seed*.json",
}
RAREFACTION_BUDGETS = (100, 300)


def lineage_counts(summary: dict) -> dict[str, int]:
    return {str(k).lstrip("T"): int(v) for k, v in (summary.get("type_counts") or {}).items() if int(v) > 0}


def rarefied(counts: list[int], n: int) -> float:
    """E[S_n] при выборке n клеток без возвращения (гипергеометрическое разрежение)."""
    total = sum(counts)
    if total <= 0 or n <= 0:
        return 0.0
    if n >= total:
        return float(len(counts))

    def log_comb(a: int, b: int) -> float:
        if b < 0 or b > a:
            return float("-inf")
        return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)

    expected = 0.0
    for c in counts:
        # P(линия не попала в выборку) = C(total-c, n) / C(total, n)
        if total - c < n:
            expected += 1.0
        else:
            expected += 1.0 - math.exp(log_comb(total - c, n) - log_comb(total, n))
    return expected


def metrics(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    counts = lineage_counts(summary)
    values = list(counts.values())
    total = sum(values)
    ps = [v / total for v in values]
    eff = 1.0 / sum(p * p for p in ps) if ps else None
    h = -sum(p * math.log(p) for p in ps) if ps else 0.0
    even = (h / math.log(len(ps))) if len(ps) > 1 else None
    log = data.get("log") or []
    steps = summary.get("steps") or (log[-1]["step"] if log else None)
    coex = sum(1 for r in log if (r.get("types_alive") or 0) > 1)
    return {
        "artifact": str(path).replace("\\", "/"),
        "lines_total": len(values),
        "cells_total": total,
        "effective_lineages": round(eff, 3) if eff else None,
        "pielou_evenness": round(even, 3) if even is not None else None,
        **{f"rarefied_richness_{n}": round(rarefied(values, n), 3) for n in RAREFACTION_BUDGETS},
        "dominant_share": round(max(ps), 4) if ps else None,
        "lines_ge_5": sum(1 for v in values if v >= 5),
        # ВНИМАНИЕ: в логе нет по-линейных размеров по шагам, только число меток.
        # Поэтому «время сосуществования» из существующих артефактов НЕ считается;
        # ниже — доля шагов, где меток больше одной (насыщается почти сразу, малоинформативно).
        "multi_tag_steps": coex,
        "steps": steps,
        "multi_tag_share": round(coex / steps, 4) if steps else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    by_series = []
    for name, pattern in SERIES.items():
        paths = sorted(glob.glob(str(Path(args.src) / pattern)))
        rows = [metrics(Path(p)) for p in paths]
        if not rows:
            by_series.append({"series": name, "runs": 0})
            continue
        by_series.append({
            "series": name,
            "runs": len(rows),
            "lines_total_median": statistics.median([r["lines_total"] for r in rows]),
            "effective_lineages_median": round(statistics.median(
                [r["effective_lineages"] for r in rows if r["effective_lineages"]]), 3),
            "pielou_median": round(statistics.median(
                [r["pielou_evenness"] for r in rows if r["pielou_evenness"] is not None]), 3),
            **{f"rarefied_{n}_median": round(statistics.median(
                [r[f"rarefied_richness_{n}"] for r in rows]), 3) for n in RAREFACTION_BUDGETS},
            "dominant_share_median": round(statistics.median(
                [r["dominant_share"] for r in rows if r["dominant_share"] is not None]), 4),
            "lines_ge_5_median": statistics.median([r["lines_ge_5"] for r in rows]),
            "multi_tag_share_median": round(statistics.median(
                [r["multi_tag_share"] for r in rows if r["multi_tag_share"] is not None]), 3),
            "rows": rows,
        })

    payload = {
        "kind": "coexistence_metrics",
        "world": "W2-bud (и W1-подобные плечи) — метрики сосуществования линий по существующим артефактам",
        "metric": {
            "effective_lineages": "1 / Σ p_i², p_i = клетки линии / все живые клетки прогона",
            "pielou_evenness": "H / ln S, H = −Σ p_i ln p_i, S = число линий с ≥1 клеткой",
            "rarefied_richness_n": "E[S_n] = Σ_i [1 − C(N−N_i, n)/C(N, n)] при выборке n клеток без "
                                   f"возвращения; бюджеты n = {RAREFACTION_BUDGETS} (гипергеометрическое разрежение)",
            "dominant_share": "max_i p_i, знаменатель — все живые клетки",
            "multi_tag_share": "доля шагов лога с types_alive > 1; знаменатель — steps прогона; "
                               "НАСЫЩАЕТСЯ почти сразу, для времени сосуществования не годится",
            "persistence_time": "НЕ вычисляется из существующих артефактов: в логе нет по-линейных "
                                "размеров по шагам, только число меток",
            "lines_ge_5": "число линий с ≥5 клетками (старая величина, для сравнения)",
        },
        "series_masks": SERIES,
        "series_masks_note": (
            "маска — часть определения агрегата (§3c). Колония взята из w2bud_rep_uniform/"
            "w2bud5_colony_seed* (сиды 101-110) НАМЕРЕННО: это те же сиды, что у pair и pair_any_tag "
            "(парный дизайн). Другие серии колонии дают близкие числа: w2bud/w2bud_colony_seed* "
            "37.0 меток / 1.127 / 0.119, w2bud2 и w2bud3 - 36.0 / 1.124 / 0.117; вывод не меняется."
        ),
        "by_series": by_series,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out}")
    print(f"{'серия':>16} {'runs':>5} {'меток':>7} {'1/Σp²':>7} {'Pielou':>7} {'raref100':>9} "
          f"{'raref300':>9} {'топ-1':>7} {'≥5':>5}")
    for s in by_series:
        if not s.get("runs"):
            print(f"{s['series']:>16} {'0':>5}  —")
            continue
        print(f"{s['series']:>16} {s['runs']:>5} {s['lines_total_median']:>7} "
              f"{s['effective_lineages_median']:>7} {s['pielou_median']:>7} "
              f"{s['rarefied_100_median']:>9} {s['rarefied_300_median']:>9} "
              f"{s['dominant_share_median']:>7} {s['lines_ge_5_median']:>5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
