"""make_periodic_stream.py — ряд притока с предсказуемым периодом (X41: мир, который предъявляет требования).

Зачем. `X33` показал: в мирах без предсказуемых требований «адекватный отклик» измерить не на чем. Здесь
строится ряд, который организм **может** предвосхитить: чередование «голодно» и «прилив», с известным периодом.
Контроль — тот же ряд, перемешанный по времени (тот же спектр значений, но без ритма).

Формат файла — как у остальных потоков в `lab/streams/`: JSON со списком values в [0, 1]. Приток считается как
`base + (max - base) * value`.

Использование:
    python scripts/make_periodic_stream.py --period 120 --flood 24 --out lab/streams/periodic_120_24.json
    python scripts/make_periodic_stream.py --period 120 --flood 24 --shuffle --seed 7 \
        --out lab/streams/periodic_120_24_shuffled.json
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(period: int, flood: int, total: int, low: float, high: float, seed: int, shuffle: bool) -> dict:
    if flood >= period:
        raise SystemExit("длина прилива должна быть меньше периода")
    values: list[float] = []
    while len(values) < total:
        values.append(low)
        if (len(values) % period) >= (period - flood):
            values[-1] = high
    values = values[:total]
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(values)
    flood_share = sum(1 for v in values if v >= high) / len(values)
    return {
        "kind": "periodic_stream",
        "period": period,
        "flood": flood,
        "total": len(values),
        "low": low,
        "high": high,
        "shuffled": bool(shuffle),
        "seed": seed,
        "mean": round(sum(values) / len(values), 4),
        "flood_share": round(flood_share, 4),
        "note": ("предсказуемый ритм (или его перемешанная копия с тем же спектром). Цикл: голодно, затем прилив "
                 "в последние `flood` шагов каждого периода; индекс периода считается по абсолютному шагу, "
                 "поэтому ряд можно сцепить на любой горизонт"),
        "values": [round(v, 4) for v in values],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="периодический ряд притока")
    ap.add_argument("--period", type=int, default=120)
    ap.add_argument("--flood", type=int, default=24)
    ap.add_argument("--total", type=int, default=6000)
    ap.add_argument("--low", type=float, default=0.2)
    ap.add_argument("--high", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    data = build(args.period, args.flood, args.total, args.low, args.high, args.seed, args.shuffle)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tag = "перемешанный" if data["shuffled"] else "периодический"
    print(f"[stream] {tag}: период {data['period']}, прилив {data['flood']}, "
          f"доля прилива {data['flood_share']:.2f}, среднее {data['mean']} → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
