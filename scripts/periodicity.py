"""periodicity.py — есть ли у мира СВОЙ ритм, и синхронизирован ли он с петлёй.

Гипотеза владельца (29.10): связь с железом — двусторонний процесс, «органичный как сердце». Значит
замкнутая петля (мир грузит машину → нагрузка меняет ритм мира) должна порождать **собственную
периодичность**, которой нет в разомкнутом режиме (когда тот же поток подан из записи).

Что считается по ряду активности мира (рождения за шаг из `event_series`):
* `dom_period` — период самой сильной ненулевой гармоники (в шагах);
* `dom_power` — её доля в общей дисперсии ряда (0..1): «насколько это ритм, а не шум»;
* `ac_peaks` — лаги 2..40, где автокорреляция положительна и локально максимальна;
* `damping` — насколько быстро гаснет автокорреляция (по первому пересечению нуля).

Почему это отличает петлю от записи: запись — внешний график, и мир на неё отвечает, но собственного
источника ритма у него нет; замкнутая петля может раскачаться в собственный цикл (сердцебиение).

Использование:
    python scripts/periodicity.py --src morphogenesis/experiments/E09_pond/w2bud_k2b
    python scripts/periodicity.py --src <каталог> --out <json>
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def activity(path: Path) -> list[float] | None:
    s = json.loads(path.read_text(encoding="utf-8"))
    s = s.get("summary") or s
    series = s.get("event_series") or []
    if len(series) < 16:
        return None
    steps = [r.get("step") or 0 for r in series]
    births = [r.get("births") or 0 for r in series]
    act = []
    for i in range(1, len(series)):
        ds = steps[i] - steps[i - 1]
        act.append((births[i] - births[i - 1]) / ds if ds else 0.0)
    return act or None


def dft_power(x: list[float]) -> tuple[float, float]:
    """Простейший DFT: возвращает (период, доля дисперсии) главной ненулевой гармоники."""
    n = len(x)
    if n < 8:
        return 0.0, 0.0
    mean = sum(x) / n
    xs = [v - mean for v in x]
    var = sum(v * v for v in xs)
    if var <= 0:
        return 0.0, 0.0
    best_p, best_e = 0.0, 0.0
    for k in range(1, n // 2):
        re = im = 0.0
        for t, v in enumerate(xs):
            ang = 2.0 * math.pi * k * t / n
            re += v * math.cos(ang)
            im -= v * math.sin(ang)
        e = (re * re + im * im) / n
        if e > best_e:
            best_e, best_p = e, n / k
    return best_p, best_e / var


def autocorr(x: list[float], max_lag: int = 40) -> tuple[list[int], int | None]:
    n = len(x)
    mean = sum(x) / n
    xs = [v - mean for v in x]
    var = sum(v * v for v in xs)
    if var <= 0:
        return [], None
    peaks = []
    zero = None
    for lag in range(1, min(max_lag, n - 2)):
        c = sum(xs[i] * xs[i + lag] for i in range(n - lag)) / ((n - lag) * var)
        if zero is None and c <= 0 and lag > 1:
            zero = lag
        if 2 <= lag and c > 0.15:
            prev_ = sum(xs[i] * xs[i + lag - 1] for i in range(n - lag + 1)) / ((n - lag + 1) * var)
            nxt_ = sum(xs[i] * xs[i + lag + 1] for i in range(n - lag - 1)) / ((n - lag - 1) * var)
            if c >= prev_ and c >= nxt_:
                peaks.append(lag)
    return peaks, zero


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="собственный ритм мира")
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(Path(p) for p in Path(args.src).glob("*.json"))
    rows = []
    for f in files:
        act = activity(f)
        if not act:
            continue
        period, share = dft_power(act)
        peaks, zero = autocorr(act)
        rows.append({"run": f.stem, "dom_period": round(period, 1), "dom_share": round(share, 3),
                     "ac_peaks": peaks[:5], "first_zero": zero})
    if not rows:
        print("[periodicity] нет прогонов с рядом событий достаточной длины")
        return 1

    print(f"{'прогон':38s} {'период':>7s} {'доля':>6s} {'пики AC':>18s} {'нуль AC':>8s}")
    for r in rows:
        print(f"{r['run'][:38]:38s} {r['dom_period']:7.1f} {r['dom_share']:6.3f} "
              f"{str(r['ac_peaks']):>18s} {str(r['first_zero']):>8s}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"runs": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\n[periodicity] записано: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
