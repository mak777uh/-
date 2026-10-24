#!/usr/bin/env python
"""idh_diversity.py — реанализ катастрофической серии на разнообразие (IDH).

Зачем: серия катастроф (§10x) проверялась по метрике «доля инвайдера» и дала
отрицательный результат — нарушения не создают сосуществования. Гипотеза IDH
(Connell 1978: промежуточное нарушение → максимум разнообразия) в ней **не
проверялась**: мерили выживание инвайдера, а не разнообразие. Здесь — только реанализ
СУЩЕСТВУЮЩИХ артефактов, без новых прогонов.

Что вычислимо, а что нет (честно):

* **Не вычислимо: разнообразие паттернов** — то, что IDH собственно утверждает.
  В артефактах пруда нет ни бинарных карт (`alive`), ни класса переписи: `log` несёт
  только скаляры (`alive_cells`, `a_share`, `damage_mean`, `born`, `died`). Для IDH
  нужен патч логгера: сохранять финальную карту `alive` (32×32 бит = 128 байт на
  прогон) и/или класс переписи; тогда разнообразие = энтропия по картам/классам.
* **Вычислимо: разнообразие поведения и исходов.** Две метрики:
  1. `behaviour_entropy` — Shannon по распределению `alive_cells` за прогон
     (10 корзин между 0 и максимумом): насколько разнообразны состояния, которые
     система проходит;
  2. `outcome_cv` — коэффициент вариации `alive_final` между сидами при одном уровне
     нарушения: насколько расходятся исходы (это дисперсия, а не разнообразие
     паттернов, и так и подписывается).

Запуск (из корня):

    python scripts/idh_diversity.py \
        --matrix morphogenesis/experiments/E09_pond/catastrophe_matrix.json \
        --out morphogenesis/experiments/E09_pond/catastrophe_diversity.json
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

BINS = 10


def behaviour_entropy(values: list[float]) -> float | None:
    """Shannon по гистограмме `alive_cells` (10 корзин)."""
    if not values:
        return None
    lo, hi = min(values), max(values)
    if hi <= lo:
        return 0.0
    width = (hi - lo) / BINS
    counts = [0] * BINS
    for value in values:
        idx = min(BINS - 1, int((value - lo) / width))
        counts[idx] += 1
    total = sum(counts)
    h = 0.0
    for c in counts:
        if c:
            p = c / total
            h -= p * math.log(p)
    return round(h, 4)


def load_series(artifact: str, root: Path) -> list[float]:
    path = root / artifact
    if not path.is_file():
        path = root.parent / artifact
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [float(row.get("alive_cells", 0)) for row in (data.get("log") or [])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--matrix", default="morphogenesis/experiments/E09_pond/catastrophe_matrix.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    matrix = json.loads((root / args.matrix).read_text(encoding="utf-8"))
    rows = matrix.get("rows") or []

    enriched = []
    for row in rows:
        series = load_series(row.get("artifact", ""), root)
        enriched.append({
            "catastrophe_rate": row.get("catastrophe_rate"),
            "catastrophe_mode": row.get("catastrophe_mode"),
            "direction": row.get("direction"),
            "seed": row.get("seed"),
            "pop_time": row.get("pop_time"),
            "alive_final": row.get("alive_final"),
            "invader_share_final": row.get("invader_share_final"),
            "behaviour_entropy": behaviour_entropy(series),
            "alive_series_points": len(series),
            "artifact": row.get("artifact"),
        })

    by_rate: list[dict] = []
    keys = sorted({(r["catastrophe_mode"], r["catastrophe_rate"]) for r in enriched
                   if r["catastrophe_rate"] is not None},
                  key=lambda k: (str(k[0]), float(k[1])))
    for mode, rate in keys:
        group = [r for r in enriched
                 if r["catastrophe_mode"] == mode and r["catastrophe_rate"] == rate]
        ent = [r["behaviour_entropy"] for r in group if r["behaviour_entropy"] is not None]
        alive = [r["alive_final"] for r in group if r["alive_final"] is not None]
        pops = [r["pop_time"] for r in group if r["pop_time"] is not None]
        cv = None
        if len(alive) >= 2 and statistics.mean(alive) > 0:
            cv = round(statistics.pstdev(alive) / statistics.mean(alive), 3)
        by_rate.append({
            "catastrophe_mode": mode,
            "catastrophe_rate": rate,
            "n": len(group),
            "behaviour_entropy_median": round(statistics.median(ent), 4) if ent else None,
            "outcome_cv": cv,
            "alive_final_median": round(statistics.median(alive), 1) if alive else None,
            "pop_time_median": round(statistics.median(pops), 1) if pops else None,
        })

    # форма зависимости: пик в середине (IDH), монотонно, или нет сигнала
    verdict = {"idh_shape": None, "detail": None}
    for mode in sorted({b["catastrophe_mode"] for b in by_rate}, key=str):
        block = [b for b in by_rate if b["catastrophe_mode"] == mode
                 and b["behaviour_entropy_median"] is not None]
        block.sort(key=lambda b: float(b["catastrophe_rate"]))
        values = [b["behaviour_entropy_median"] for b in block]
        if len(values) < 4:
            verdict["detail"] = f"{mode}: точек {len(values)} — мало для формы"
            continue
        mid = values[1:-1]
        peak_idx = values.index(max(values))
        interior = 0 < peak_idx < len(values) - 1
        if interior and max(mid) > values[0] + 1e-9 and max(mid) > values[-1] + 1e-9:
            verdict = {"idh_shape": "peak_at_intermediate",
                       "detail": f"{mode}: максимум при rate={block[peak_idx]['catastrophe_rate']}"}
            break
        if all(b >= a - 1e-9 for a, b in zip(values, values[1:])):
            verdict = {"idh_shape": "monotone_increasing", "detail": f"{mode}: энтропия растёт с нарушением"}
        elif all(b <= a + 1e-9 for a, b in zip(values, values[1:])):
            verdict = {"idh_shape": "monotone_decreasing", "detail": f"{mode}: энтропия падает с нарушением"}
        else:
            verdict = {"idh_shape": "no_clear_shape", "detail": f"{mode}: немонотонно без пика в середине"}

    # КОНФАУНД: энтропия по alive_cells растёт с самим населением, поэтому «пик» может
    # быть артефактом размера популяции, а не разнообразия. Считаем корреляцию между
    # медианами энтропии и населения по точкам сетки — если высокая, пик не заявляется.
    pairs = [(b["behaviour_entropy_median"], b["alive_final_median"]) for b in by_rate
             if b["behaviour_entropy_median"] is not None and b["alive_final_median"]]
    confound_r = None
    if len(pairs) >= 3:
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in pairs)
        den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
        confound_r = round(num / den, 3) if den else None
    if confound_r is not None and abs(confound_r) >= 0.7 and verdict["idh_shape"]:
        verdict["confound_with_population"] = confound_r
        verdict["idh_shape_after_confound"] = "not_claimable"
        verdict["detail"] = (verdict.get("detail") or "") + \
            f"; r(H, alive)={confound_r} — форма не отделена от размера популяции"

    # корреляция внутри каждого режима: смешивать shift и drop нельзя (у drop маленькое
    # население и высокая вариативность траекторий)
    per_mode_confound = {}
    for mode in sorted({b["catastrophe_mode"] for b in by_rate}, key=str):
        block = [b for b in by_rate if b["catastrophe_mode"] == mode
                 and b["behaviour_entropy_median"] is not None and b["alive_final_median"]]
        if len(block) < 3:
            continue
        xs = [b["behaviour_entropy_median"] for b in block]
        ys = [b["alive_final_median"] for b in block]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
        per_mode_confound[mode] = round(num / den, 3) if den else None
    verdict["confound_per_mode"] = per_mode_confound

    payload = {
        "kind": "idh_reanalysis",
        "experiment": "E09_pond_catastrophe_diversity",
        "metric_definition": {
            "behaviour_entropy": "Shannon по гистограмме alive_cells за прогон (10 корзин) — "
                                 "разнообразие ПОВЕДЕНИЯ, не паттернов",
            "outcome_cv": "коэффициент вариации alive_final между сидами при одном уровне нарушения",
        },
        "not_computable": [
            "разнообразие ПАТТЕРНОВ (объект IDH): в артефактах пруда нет карт alive и нет класса "
            "переписи — нужен патч логгера (сохранять финальную карту alive, 32x32 бит, и/или класс)",
        ],
        "exploratory": True,
        "note": "реанализ существующих артефактов, критерий не пре-регистрировался; числа — описательные",
        "rows": enriched,
        "by_rate": by_rate,
        "verdict": verdict,
        "confound_note": "энтропия по alive_cells монотонно связана с размером населения; "
                         "пока связь не снята, форма зависимости не заявляется",
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(enriched)}")
    print(f"{'режим':>6} {'rate':>7} {'n':>3} {'H_повед':>8} {'CV_исходов':>10} {'alive':>7} {'pop_time':>9}")
    for b in by_rate:
        print(f"{str(b['catastrophe_mode']):>6} {b['catastrophe_rate']:>7} {b['n']:>3} "
              f"{str(b['behaviour_entropy_median']):>8} {str(b['outcome_cv']):>10} "
              f"{str(b['alive_final_median']):>7} {str(b['pop_time_median']):>9}")
    print(f"форма: {verdict['idh_shape']} ({verdict['detail']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
