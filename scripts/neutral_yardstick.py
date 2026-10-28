"""neutral_yardstick.py — нейтральная линейка для наших миров.

Зачем. Мы умеем сказать «цена признака отрицательна» и «линий столько-то», но не умеем сказать,
много это или мало. В популяционной генетике для этого есть эталон: нейтральный дрейф. Здесь он
считается **из наших же артефактов**, без новых прогонов.

Три величины:

1. **Эффективный размер** `N_e`. Из дрейфа долей линий: для линии с долей `p` за интервал `dt`
   дисперсия равна `p(1-p)·dt/N_e`. Оценка `N_e = p(1-p)·dt / (Δp)²` по всем линиям и парам точек.
   Сравнение с реальным числом живых клеток `N` даёт **отношение N_e/N**: если оно мало, разнообразие
   «сжато» — часть клеток не считается, потому что принадлежит тем же линиям.
2. **Скорость потери линий.** Доля линий, исчезнувших за прогон, и **время полураспада** — сколько
   шагов нужно, чтобы исчезла половина линий, бывших в середине прогона.
3. **Зависимость выживания от начальной доли.** В нейтральной модели маленькие линии гибнут чаще;
   если у нас зависимость слабее или отсутствует — это признак, что работает не дрейф, а механизм.

Ограничения (пишутся в отчёт): серия снимается каждые ~5 шагов, а не каждый; `N_e` — грубая оценка
(медиана по линиям, без учёта мутаций и структуры); «шаг» не равен «поколению».

Использование:
    python scripts/neutral_yardstick.py --glob "morphogenesis/experiments/E09_pond/w2bud_async/*cellp05*.json"
    python scripts/neutral_yardstick.py --glob "..." --format json --out /tmp/yard.json
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from pathlib import Path


def series_of(path: Path) -> list[tuple[int, dict[str, int]]]:
    s = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
    out = []
    for row in s.get("type_counts_series") or []:
        if isinstance(row, dict) and "step" in row and "counts" in row:
            out.append((int(row["step"]), {str(k).lstrip("T"): int(v) for k, v in row["counts"].items()}))
    return out


def neutral_expectation(series: list[tuple[int, dict[str, int]]], reps: int = 400,
                        seed: int = 7) -> dict | None:
    """Что было бы при чистом дрейфе: клетки каждой точки «перетасовываются» случайно.

    Зачем именно так. Формула `N_e = p(1-p)·dt/(Δp)²` здесь **не работает**: население растёт с 4 до 560
    клеток, а новые линии рождаются мутацией. Это не дрейф фиксированной популяции, и любая оценка `N_e`
    по дисперсии долей завышает её на порядки (проверено: получалось N_e ≈ 186 тыс. при 560 клетках).
    Поэтому нейтральный эталон строится иначе: берём реальное состояние в середине прогона и наблюдаемое
    население в каждой следующей точке, но **кто именно** из линий попал в эту точку — разыгрываем
    случайно (мультиномиально, по долям середины). Механизм при этом выключен: остаётся только случай.

    Сравнение с наблюдением отвечает на вопрос «линии живут дольше или меньше, чем даёт случай».
    """
    try:
        import numpy as np
    except Exception:
        print("[yardstick] нет numpy — нейтральный эталон пропущен")
        return None
    if len(series) < 4:
        return None
    mid = len(series) // 2
    _, c_mid = series[mid]
    start_lines = [lin for lin, v in c_mid.items() if v > 0]
    if len(start_lines) < 4:
        return None
    weights = np.array([c_mid[lin] for lin in start_lines], dtype=np.float64)
    shares = weights / weights.sum()
    census = [sum(c.values()) for _, c in series[mid:]]
    rng = np.random.default_rng(seed)
    halves, survivals = [], []
    for _ in range(reps):
        cur = shares.copy()
        half = None
        alive = len(start_lines)
        for k in range(1, len(census)):
            born = rng.multinomial(int(census[k]), cur)
            # доли обновляются по реализованным числам — иначе это не дрейф,
            # а пересэмплирование из неподвижного распределения.
            cur = born / max(1, born.sum())
            alive = int((born > 0).sum())
            if half is None and alive <= len(start_lines) / 2:
                half = float(series[mid + k][0] - series[mid][0])
        halves.append(half)
        survivals.append(alive / len(start_lines))
    return {
        "neutral_half_life_steps": (st.median([h for h in halves if h is not None])
                                    if any(h is not None for h in halves) else None),
        "neutral_mid_survival": round(st.median(survivals), 3),
        "neutral_reps": reps,
    }


    if len(series) < 4:
        return None
    mid = len(series) // 2
    _, c_mid = series[mid]
    start_lines = [lin for lin, v in c_mid.items() if v > 0]
    if len(start_lines) < 4:
        return None
    weights = [c_mid[lin] for lin in start_lines]
    total = sum(weights) or 1
    shares = [w / total for w in weights]
    census = [sum(c.values()) for _, c in series[mid:]]
    rnd = random.Random(seed)
    halves, survivals = [], []
    for _ in range(reps):
        alive = set(start_lines)
        half = None
        cur = list(shares)
        for k in range(1, len(census)):
            n = census[k]
            born = [0] * len(start_lines)
            for _cell in range(n):
                x, acc, idx = rnd.random(), 0.0, len(start_lines) - 1
                for i, s in enumerate(cur):
                    acc += s
                    if x <= acc:
                        idx = i
                        break
                born[idx] += 1
            # ВАЖНО: доли обновляются по реализованным числам — иначе это не дрейф,
            # а пересэмплирование из неподвижного распределения (первая версия давала
            # выживание 0.8 и вообще не теряла линии).
            tot = sum(born) or 1
            cur = [v / tot for v in born]
            alive = {start_lines[i] for i, v in enumerate(born) if v > 0}
            if half is None and len(alive) <= len(start_lines) / 2:
                half = float(series[mid + k][0] - series[mid][0])
        halves.append(half)
        survivals.append(len(alive) / len(start_lines))
    return {
        "neutral_half_life_steps": (st.median([h for h in halves if h is not None])
                                    if any(h is not None for h in halves) else None),
        "neutral_mid_survival": round(st.median(survivals), 3),
        "neutral_reps": reps,
    }


def mid_lifetime(series: list[tuple[int, dict[str, int]]]) -> tuple[float | None, float | None]:
    """Полураспад линий, живых в середине прогона, и доля выживших к концу."""
    if len(series) < 3:
        return None, None
    s_mid, c_mid = series[len(series) // 2]
    s_end, c_end = series[-1]
    start = {lin for lin, v in c_mid.items() if v > 0}
    if not start:
        return None, None
    survived_end = {lin for lin in start if c_end.get(lin, 0) > 0}
    share = len(survived_end) / len(start)
    half = None
    for s_t, c_t in series[len(series) // 2:]:
        alive = len({lin for lin in start if c_t.get(lin, 0) > 0})
        if alive <= len(start) / 2:
            half = float(s_t - s_mid)
            break
    return half, share


def survival_by_share(series: list[tuple[int, dict[str, int]]]) -> dict[str, float] | None:
    """Выживание линий к концу, разбитое по их доле в середине: маленькие / средние / крупные."""
    if len(series) < 3:
        return None
    _, c_mid = series[len(series) // 2]
    _, c_end = series[-1]
    n_mid = sum(c_mid.values()) or 1
    rows = [(lin, v / n_mid) for lin, v in c_mid.items() if v > 0]
    if len(rows) < 4:
        return None
    rows.sort(key=lambda x: x[1])
    k = max(1, len(rows) // 3)
    groups = {"small": rows[:k], "middle": rows[k:-k] or rows[k:], "large": rows[-k:]}
    out = {}
    for name, grp in groups.items():
        if not grp:
            continue
        out[name] = round(sum(1 for lin, _ in grp if c_end.get(lin, 0) > 0) / len(grp), 3)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--glob", required=True, help="шаблон файлов прогонов")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(args.glob))[: args.limit]
    if not files:
        print("[yardstick] файлов не найдено:", args.glob)
        return 1

    rows = []
    for f in files:
        ser = series_of(Path(f))
        if len(ser) < 3:
            continue
        neutral = neutral_expectation(ser) or {}
        half, share = mid_lifetime(ser)
        sbs = survival_by_share(ser)
        _, c_end = ser[-1]
        rows.append({
            "file": Path(f).name,
            "n_end": sum(c_end.values()),
            "lineages_end": len([v for v in c_end.values() if v > 0]),
            "neutral_half_life_steps": neutral.get("neutral_half_life_steps"),
            "neutral_mid_survival": neutral.get("neutral_mid_survival"),
            "half_life_steps": half,
            "mid_survival": round(share, 3) if share is not None else None,
            "survival_by_share": sbs,
        })
    if not rows:
        print("[yardstick] не удалось разобрать ни один файл")
        return 1

    def agg(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return round(st.median(vals), 2) if vals else None

    summary = {
        "runs": len(rows),
        "median_n_end": agg("n_end"),
        "median_lineages_end": agg("lineages_end"),
        "median_neutral_half_life": agg("neutral_half_life_steps"),
        "median_neutral_survival": agg("neutral_mid_survival"),
        "median_half_life_steps": agg("half_life_steps"),
        "median_mid_survival": agg("mid_survival"),
    }
    if args.out:
        Path(args.out).write_text(json.dumps({"summary": summary, "runs": rows},
                                             ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
    if args.format == "json":
        print(json.dumps({"summary": summary, "runs": rows}, ensure_ascii=False, indent=2))
        return 0

    print(f"[yardstick] прогонов: {summary['runs']}")
    print(f"  к концу: живых клеток {summary['median_n_end']}, линий {summary['median_lineages_end']}")
    print(f"  наблюдение: полураспад {summary['median_half_life_steps']} шагов | выжило к концу "
          f"{summary['median_mid_survival']}")
    print(f"  нейтральный эталон: полураспад {summary['median_neutral_half_life']} шагов | выжило "
          f"{summary['median_neutral_survival']}")
    sbs_rows = [r["survival_by_share"] for r in rows if r.get("survival_by_share")]
    if sbs_rows:
        for grp in ("small", "middle", "large"):
            vals = [r[grp] for r in sbs_rows if grp in r]
            if vals:
                print(f"  выживание {grp:6s}: медиана {st.median(vals):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
