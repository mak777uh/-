"""te_anticipation.py — упреждение через УСЛОВНУЮ передачу энтропии, а не через разности.

Зачем. Внешние разборы (31.10) показали, что наша прежняя мера `I(ΔS_t ; ΔE_{t+1})` **изготавливает** лаговую
информацию из чисто одновременного отклика: при `S_t = E_t` разности дают корреляцию −0.5 и ~0.2 бита при
нулевом предсказании. Здесь считается корректная величина:

    TE = I( X_t ; Y_{t+L} | Y_t )

то есть информация о **будущем** событии сверх той, что уже есть в текущем. Именно conditioning на `Y_t` снимает
одновременный отклик.

Суррогат — **сдвиг по времени**, а не перемешивание: перемешивание разрушает автокорреляцию ряда, и такой нуль
невалиден для стационарных данных. Сдвиг сохраняет автокорреляцию, но разрывает связь между рядами.

Данные: `x46_{lead0,lead20,lead40,shuf40}_s*.json`, поля `series[].components_log` (`cx`, `area`) — центроид
признака, `event_centre` — текущее событие (полоса распада).

Запуск:
    python scripts/te_anticipation.py --write     # посчитать и записать агрегат
    python scripts/te_anticipation.py             # только напечатать
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "L1_field" / "te_anticipation.json"
SECTORS = 12          # кольцо 96 клеток -> 12 секторов по 8
LAGS = (1, 5, 20)


def centroid(snap: dict):
    rows = snap.get("components_log") or []
    if not rows:
        return None
    w = sum(r["area"] for r in rows) or 1
    return sum(r["cx"] * r["area"] for r in rows) / w


def entropy_bits(counts: Counter, total: int) -> float:
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c)


def conditional_mi(xs: list[int], ys_future: list[int], ys_now: list[int], nbins: int) -> float:
    """I(X ; Y_future | Y_now) по трём дискретным рядам одинаковой длины."""
    n = len(xs)
    if n < 20:
        return 0.0
    joint = Counter(zip(xs, ys_future, ys_now))
    now = Counter(ys_now)
    fut_now = Counter(zip(ys_future, ys_now))
    x_now = Counter(zip(xs, ys_now))
    h_now = entropy_bits(now, n)
    h_fut_now = entropy_bits(fut_now, n)
    h_x_now = entropy_bits(x_now, n)
    h_all = entropy_bits(joint, n)
    # I(X;Yf|Yn) = H(X,Yn) + H(Yf,Yn) - H(Yn) - H(X,Yf,Yn)
    return max(0.0, h_x_now + h_fut_now - h_now - h_all)


def series_for_run(path: Path) -> tuple[list[int], list[int]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    xs, ys = [], []
    for snap in d.get("series") or []:
        cx, ev = centroid(snap), snap.get("event_centre")
        if cx is None or ev is None:
            continue
        xs.append(int(cx) // (96 // SECTORS) % SECTORS)
        ys.append(int(ev) // (96 // SECTORS) % SECTORS)
    return xs, ys


def shifted(values: list[int], by: int) -> list[int]:
    if not values:
        return values
    by = by % len(values)
    return values[by:] + values[:by]


def analyse() -> dict:
    report: dict = {"kind": "te_anticipation", "command": "python scripts/te_anticipation.py --write",
                    "metric": {"te": "I(состояние_t ; событие_{t+L} | событие_t), бит",
                               "null": "то же на сдвинутом по времени состоянии (автокорреляция сохранена)"},
                    "design": {"sectors": SECTORS, "lags": list(LAGS),
                               "surrogate": "time shift by half the series"},
                    "by_arm": {}, "not_claimed": [
                        "сектора грубые (12 на кольцо) — мера консервативна",
                        "сдвиг по времени — не единственный возможный суррогат",
                        "lead20/lead40 сравнимы только при одинаковом числе срезов",
                    ]}
    for arm in ("lead0", "lead20", "lead40", "shuf40"):
        files = sorted(glob.glob(str(ROOT / "_hourly" / f"x46_{arm}_s*.json")))
        if not files:
            files = sorted(glob.glob(str(ROOT.parent / "_hourly" / f"x46_{arm}_s*.json")))
        per_lag = {}
        for lag in LAGS:
            xs, yf, yn, xs_null = [], [], [], []
            for f in files:
                x, y = series_for_run(Path(f))
                if len(x) <= lag + 5:
                    continue
                xs.extend(x[:len(x) - lag])
                yf.extend(y[lag:])
                yn.extend(y[:len(y) - lag])
                xs_null.extend(shifted(x, len(x) // 2)[:len(x) - lag])
            if not xs:
                continue
            te = conditional_mi(xs, yf, yn, SECTORS)
            null = conditional_mi(xs_null, yf, yn, SECTORS)
            per_lag[str(lag)] = {"te": round(te, 4), "null": round(null, 4),
                                 "excess": round(te - null, 4), "n": len(xs)}
        report["by_arm"][arm] = {"files": len(files), "lags": per_lag}
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="упреждение через условную TE")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = analyse()
    if args.write:
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[te] записано: {OUT.name}")
    for arm, v in data["by_arm"].items():
        if not v["lags"]:
            print(f"  {arm}: данных нет")
            continue
        parts = ", ".join(f"L{l}: TE {m['te']} против нуля {m['null']}" for l, m in v["lags"].items())
        print(f"  {arm} ({v['files']} файлов): {parts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
