"""check_seed_dispersion.py — если разброс по сидам велик, агрегат обязан это признать.

Откуда (B-077 на доске): предлагалось добавить `--min-seeds`, complete-гейт, «k из фактических сидов» и epsilon для I=0.

Проверка показала, что правило «минимум N сидов» в контракте отсутствует, зато есть наше собственное и оно строже:

    CV > 0.3  ⇒  вывод не заявлять   (lab/metrics.json → q1_slice_comparison_rule, §10bv-доп-2)

Поэтому вместо числа сидов гейт проверяет **следствие**: если по плечу разброс велик, агрегат должен содержать
пометку, что это плечо не заявляется (`not_claimed` / `cv_warning` / `weak`). Иначе читатель увидит медиану и
решит, что она надёжна.

Что делает:
  * для каждого агрегата с посидовыми строками (`seed` + числовая метрика) считает CV по плечу;
  * если CV > 0.3, а в `not_claimed` плечо не упомянуто — предупреждение; с `--ci` — падение;
  * агрегаты без посидовых строк пропускает (там CV не посчитать) и считает их отдельно.

Использование:
    python scripts/check_seed_dispersion.py [--ci]
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "morphogenesis" / "experiments"
CV_LIMIT = 0.3
METRIC_HINTS = ("value", "pop_time", "q1", "mean", "score", "survival", "rate")
# Правило про CV относится к СРЕДНИМ. Индексы разброса (I_obs и т.п.) и величины с суффиксом *_median
# не являются средними: для них заявляется знак или счёт, а не величина, и CV там — не признак
# ненадёжности (категориальная ошибка, найденная при первом прогоне гейта 30.10).
EXCLUDE_SUBSTR = ("I_obs", "I_null", "I_ratio", "median", "dispersion", "variance", "sd_", "_sd")


def excluded(name: str) -> bool:
    return any(s.lower() in name.lower() for s in EXCLUDE_SUBSTR)


def pick_metric(rows: list[dict]) -> str | None:
    """Имя числового поля, по которому есть значения у большинства строк."""
    keys: dict[str, int] = {}
    for r in rows:
        for k, v in r.items():
            if k == "seed":
                continue
            if isinstance(v, (int, float)) and not isinstance(v, bool) and not excluded(k):
                keys[k] = keys.get(k, 0) + 1
    if not keys:
        return None
    for hint in METRIC_HINTS:
        for k, n in keys.items():
            if hint.lower() in k.lower() and n >= max(2, len(rows) // 2):
                return k
    k, n = max(keys.items(), key=lambda kv: kv[1])
    return k if n >= max(2, len(rows) // 2) else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="разброс по сидам и пометка «не заявлять»")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(EXPERIMENTS / "**" / "*matrix.json"), recursive=True))
    computed, skipped, bad = 0, 0, []

    for f in files:
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
        if not rows or not any("seed" in r for r in rows):
            skipped += 1
            continue
        metric = pick_metric(rows)
        if metric is None:
            skipped += 1
            continue
        by_arm: dict[str, list[float]] = {}
        for r in rows:
            v = r.get(metric)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                by_arm.setdefault(str(r.get("arm") or "?"), []).append(float(v))
        if not by_arm:
            skipped += 1
            continue
        computed += 1
        claimed = " ".join(str(x) for x in (d.get("not_claimed") or [])).lower()
        flagged = json.dumps(d.get("criteria") or {}, ensure_ascii=False).lower()
        for arm, vals in sorted(by_arm.items()):
            if len(vals) < 3:
                continue
            m = sum(vals) / len(vals)
            sd = (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5
            cv = sd / max(1e-12, abs(m))
            if cv > CV_LIMIT:
                arm_l = arm.lower()
                mentioned = arm_l in claimed or arm_l in flagged or "cv" in claimed
                if not mentioned:
                    bad.append((Path(f).name, arm, round(cv, 2), metric, len(vals)))

    print(f"[dispersion] агрегатов: {len(files)}; CV посчитан: {computed}; без посидовых строк: {skipped}")
    if bad:
        print(f"[dispersion] плечи с CV > {CV_LIMIT} без пометки «не заявлять»: {len(bad)}")
        for name, arm, cv, metric, n in bad[:15]:
            print(f"    {name}: плечо {arm}, CV {cv}, метрика {metric}, сидов {n}")
        print("[dispersion] добавьте плечо в not_claimed агрегата или увеличьте число сидов")
        if args.ci:
            return 1
    else:
        print(f"[dispersion] все плечи с CV > {CV_LIMIT} помечены как незаявляемые")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
