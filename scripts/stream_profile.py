"""stream_profile.py — измеряет профиль живых источников, а не угадывает «какой лучше».

Зачем. 29.10 владелец справедливо указал: я выбрал `net` вместо `mic` рассуждением, а не измерением. Этот
скрипт снимает несколько источников **одновременно** и считает то, что нужно для решения:

* `mean`, `sd`, `cv` — амплитуда;
* `duty` — доля отсчётов ниже порога (у микрофона было 0.85 — отсюда и отказ от него);
* `longest_quiet` — самый длинный провал (источник, который «молчит», не может задавать ритм);
* `ac1`, `ac10` — автокорреляция на лагах 1 и 10 (структура на масштабе шага мира);
* `beta` — наклон спектра в лог-лог (1/f^β): по литературе розовый β≈1 — «типичная среда»;
* `amp_3s`, `amp_10s` — sd сигнала после усреднения по окну 3 с и 10 с, делённое на среднее: амплитуда
  именно на масштабе шага мира, а не на частоте опроса.

Критерий выбора: `duty` низкий (источник тикает всегда), `longest_quiet` короткий, `amp_3s` большой,
`beta` ближе к 1. Оценка печатается таблицей, решение принимается по числам.

Использование:
    python scripts/stream_profile.py --seconds 120 --sources net,crypto,system,events
    python scripts/stream_profile.py --seconds 120 --out lab/streams/profile-2026-10-29.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def profile(values: list[float], rate_hz: float) -> dict:
    """Считает профиль ряда. Только стандартная библиотека: без numpy, чтобы работало и в CI."""
    n = len(values)
    if n < 8:
        return {"n": n, "error": "слишком короткий ряд"}
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    sd = math.sqrt(var)

    thr = 0.1
    below = [1 if v < thr else 0 for v in values]
    duty = sum(below) / n
    longest = cur = 0
    for b in below:
        cur = cur + 1 if b else 0
        longest = max(longest, cur)

    def ac(lag: int) -> float:
        if lag <= 0 or lag >= n or var <= 0:
            return 0.0
        s = sum((values[i] - mean) * (values[i + lag] - mean) for i in range(n - lag))
        return s / ((n - lag) * var)

    def smooth_sd(window_s: float) -> float:
        w = max(1, int(round(window_s * rate_hz)))
        if w >= n:
            return 0.0
        means = [sum(values[i:i + w]) / w for i in range(0, n - w + 1, w)]
        if len(means) < 2:
            return 0.0
        m = sum(means) / len(means)
        return math.sqrt(sum((x - m) ** 2 for x in means) / len(means)) / m if m > 0 else 0.0

    # наклон спектра: грубая оценка через дисперсию разностей на разных масштабах (без FFT)
    def loglog_slope() -> float:
        pairs = []
        for w in (2, 4, 8, 16, 32):
            if w >= n:
                continue
            agg = [sum(values[i:i + w]) / w for i in range(0, n - w + 1, w)]
            if len(agg) < 4:
                continue
            m = sum(agg) / len(agg)
            v = sum((x - m) ** 2 for x in agg) / len(agg)
            if v > 0:
                pairs.append((math.log10(w), math.log10(v)))
        if len(pairs) < 2:
            return 0.0
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        return num / den if den else 0.0

    beta = -loglog_slope() / 2.0  # Var ∝ w^-(β-1) ⇒ β ≈ 1 − slope

    return {
        "n": n, "mean": round(mean, 5), "sd": round(sd, 5),
        "cv": round(sd / mean, 4) if mean else None,
        "duty_below_0.1": round(duty, 3), "longest_quiet": int(longest),
        "ac1": round(ac(1), 3), "ac10": round(ac(10), 3),
        "amp_3s": round(smooth_sd(3.0), 4), "amp_10s": round(smooth_sd(10.0), 4),
        "beta_est": round(beta, 2),
    }


def score(p: dict) -> float:
    """Эвристика ранжирования: тикает всегда, амплитуда на масштабе шага, спектр ближе к розовому."""
    if "error" in p:
        return -1e9
    duty_pen = 2.0 * p["duty_below_0.1"]
    quiet_pen = min(1.0, p["longest_quiet"] / max(1, p["n"]))
    amp = p["amp_3s"] or 0.0
    beta_pen = abs((p["beta_est"] or 1.0) - 1.0) / 2.0
    return 3.0 * amp - duty_pen - quiet_pen - beta_pen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="профиль живых источников")
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--rate", type=float, default=4.0, help="частота опроса, Гц")
    ap.add_argument("--sources", default="net,crypto,system,events")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    from stream_sources import make  # локальный импорт: скрипт должен работать и без sources

    names = [s.strip() for s in args.sources.split(",") if s.strip()]
    live = {}
    for name in names:
        try:
            live[name] = make(name, rate=args.rate, window_s=60.0)
            live[name].start()
        except Exception as exc:  # источник может быть недоступен (нет сети/API)
            print(f"[profile] {name}: недоступен ({exc})", flush=True)
    if not live:
        print("[profile] ни один источник не поднялся")
        return 1

    samples: dict[str, list[float]] = {n: [] for n in live}
    t_end = time.time() + float(args.seconds)
    period = 1.0 / float(args.rate)
    while time.time() < t_end:
        for name, src in live.items():
            try:
                samples[name].append(float(src.value()))
            except Exception:
                pass
        time.sleep(period)
    for src in live.values():
        try:
            src.stop()
        except Exception:
            pass

    rows = {}
    for name, vals in samples.items():
        rows[name] = profile(vals, float(args.rate))
        rows[name]["score"] = round(score(rows[name]), 3)

    print(f"[profile] снято {args.seconds:.0f} с при {args.rate:.1f} Гц\n")
    print(f"{'источник':10s} {'n':>5s} {'mean':>7s} {'sd':>7s} {'cv':>6s} {'duty':>6s} {'quiet':>6s} "
          f"{'ac1':>6s} {'amp3s':>7s} {'beta':>6s} {'score':>7s}")
    for name, p in sorted(rows.items(), key=lambda kv: -kv[1].get("score", -1e9)):
        if "error" in p:
            print(f"{name:10s} {p.get('n', 0):5d}  {p['error']}")
            continue
        print(f"{name:10s} {p['n']:5d} {p['mean']:7.3f} {p['sd']:7.3f} {str(p['cv']):>6s} "
              f"{p['duty_below_0.1']:6.2f} {p['longest_quiet']:6d} {p['ac1']:6.2f} "
              f"{p['amp_3s']:7.3f} {p['beta_est']:6.2f} {p['score']:7.2f}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"rate_hz": args.rate, "seconds": args.seconds, "profiles": rows},
                                  ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\n[profile] записано: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
