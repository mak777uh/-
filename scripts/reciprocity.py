"""reciprocity.py — двусторонняя связь потока и мира: считается ОБА направления передачи.

Откуда (29.10, гипотеза владельца). Запись имеет **нулевую взаимность по построению**: мир на неё
реагирует, но она на мир — нет. Поэтому вопрос не «запись или живое», а:

    у потока есть информация о состоянии мира (мир → поток), или только у мира о потоке?

Что считается для каждого прогона:
* `r_forward` — корреляция входа `s_t` с активностью мира на лагах ≥ 0 (поток → мир);
* `r_backward` — корреляция активности мира с ПОСЛЕДУЮЩИМИ значениями входа (мир → поток);
* `reciprocity` — min(|r_forward|, |r_backward|): ноль, если связь односторонняя (любая запись);
* `asymmetry` — |r_forward| − |r_backward|.

Оговорка, которую надо помнить: корреляция — не трансферная энтропия. Это дешёвый индикатор направления;
если он покажет различие, следующий шаг — настоящая transfer entropy.

Использование:
    python scripts/reciprocity.py --src morphogenesis/experiments/E09_pond/w2bud_k3
    python scripts/reciprocity.py --src <каталог> --stream-dir lab/streams --out <json>
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STREAM_HINTS = {
    "real": "mic-2026-10-28.json",
    "iaaft": "mic_iaaft-2026-10-29.json",
    "shuffle": "mic_shuffle-2026-10-29.json",
}


def pearson(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n < 4:
        return 0.0
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def lagged_best(fed: list[float], act: list[float], lags: range) -> tuple[float, int]:
    best, best_lag = 0.0, 0
    for lag in lags:
        if lag >= 0:
            a, b = fed[: len(fed) - lag], act[lag:]
        else:
            a, b = fed[-lag:], act[: len(act) + lag]
        if len(a) < 5:
            continue
        r = pearson(a, b)
        if abs(r) > abs(best):
            best, best_lag = r, lag
    return best, best_lag


def stream_values(run_stem: str, summary: dict, stream_dir: Path | None) -> list[float]:
    live = (summary.get("live_stream") or {}).get("values_seen") or []
    if live:
        return list(live)
    if stream_dir is None:
        return []
    for key, fname in STREAM_HINTS.items():
        if f"_{key}_" in f"_{run_stem}_":
            f = stream_dir / fname
            if f.exists():
                return list(json.loads(f.read_text(encoding="utf-8")).get("values") or [])
    return []


def analyse(path: Path, stream_dir: Path | None) -> dict | None:
    s = json.loads(path.read_text(encoding="utf-8"))
    s = s.get("summary") or s
    series = s.get("event_series") or []
    if len(series) < 8:
        return None
    steps = [r.get("step") or 0 for r in series]
    births = [r.get("births") or 0 for r in series]
    act = []
    for i in range(1, len(series)):
        ds = steps[i] - steps[i - 1]
        act.append((births[i] - births[i - 1]) / ds if ds else 0.0)
    vals = stream_values(path.stem, s, stream_dir)
    if not vals:
        return None
    n, m = len(act), len(vals)
    fed = [vals[int(round(i * (m - 1) / max(1, n - 1)))] for i in range(n)]

    fwd, fwd_lag = lagged_best(fed, act, range(0, 15))       # вход раньше активности
    bwd, bwd_lag = lagged_best(act, fed, range(1, 15))       # активность раньше входа

    # НУЛЬ НА СДВИГАХ. Поток автокоррелирован, поэтому «обратная» корреляция возникает и у записи,
    # которая по определению на мир не реагирует (поймано 29.10: у записи |r| = 0.25-0.28). Чтобы
    # отделить связь от памяти сигнала, считаем обратную корреляцию для многих циклических сдвигов
    # того же потока и берём 95-й перцентиль как нуль.
    import random
    rnd = random.Random(12345)
    null_vals = []
    for _ in range(60):
        shift = rnd.randrange(1, max(2, len(fed)))
        rolled = fed[shift:] + fed[:shift]
        r_null, _lag = lagged_best(act, rolled, range(1, 15))
        null_vals.append(abs(r_null))
    null_vals.sort()
    null95 = null_vals[int(0.95 * (len(null_vals) - 1))] if null_vals else 0.0
    excess = abs(bwd) - null95

    return {
        "run": path.stem,
        "r_forward": round(fwd, 3), "lag_forward": fwd_lag,
        "r_backward": round(bwd, 3), "lag_backward": bwd_lag,
        "reciprocity": round(max(0.0, excess), 3),
        "null95_backward": round(null95, 3),
        "asymmetry": round(abs(fwd) - abs(bwd), 3),
        "pop_time": s.get("pop_time"),
        "types_alive": s.get("types_alive"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="двусторонняя связь потока и мира")
    ap.add_argument("--src", required=True)
    ap.add_argument("--stream-dir", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(Path(p) for p in Path(args.src).glob("*.json"))
    stream_dir = Path(args.stream_dir) if args.stream_dir else None
    rows = [r for r in (analyse(f, stream_dir) for f in files) if r]
    if not rows:
        print("[reciprocity] нет прогонов с рядом событий и известным входом")
        return 1

    print(f"{'прогон':38s} {'r→мир':>7s} {'лаг':>4s} {'r→вход':>7s} {'лаг':>4s} {'взаимн.':>8s}")
    for r in rows:
        print(f"{r['run'][:38]:38s} {r['r_forward']:7.3f} {r['lag_forward']:4d} "
              f"{r['r_backward']:7.3f} {r['lag_backward']:4d} {r['reciprocity']:8.3f}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"runs": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\n[reciprocity] записано: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
