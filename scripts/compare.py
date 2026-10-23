#!/usr/bin/env python
"""Второй фильтр сравнения: не одно число, а распределение по сидам (B-008, I-014).

Одно `pop_time` — это первый фильтр. Политика, выигравшая по среднему, может быть
артефактом одной траектории (см. историю с random: 509 на s1 против 423 на s3).
Здесь по каталогу JSON печатаются: медиана, среднее, std, минимум/максимум, IQR и
доля сидов выше базлайна.

Запуск:
    python scripts/compare.py <каталог с json> [--baseline <значение>] [--key pop_time]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st


def collect(directory: str, key: str) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for path in glob.glob(os.path.join(directory, "*.json")):
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except (OSError, json.JSONDecodeError):
            continue
        value = data.get("summary", {}).get(key)
        if value is None:
            continue
        name = os.path.basename(path).split("_s")[0]
        out.setdefault(name, []).append(float(value))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("directory")
    ap.add_argument("--baseline", type=float, default=None)
    ap.add_argument("--key", default="pop_time")
    args = ap.parse_args(argv)

    rows = collect(args.directory, args.key)
    if not rows:
        print("нет данных: в каталоге не нашлось summary.<key>")
        return 1

    print(f"{'режим':10s} {'n':>2s} {'медиана':>9s} {'среднее':>9s} {'std':>7s} "
          f"{'min':>7s} {'max':>7s} {'IQR':>7s}  лучше базлайна")
    ordered = sorted(rows.items(), key=lambda kv: -st.median(kv[1]))
    for name, values in ordered:
        q = st.quantiles(values, n=4) if len(values) >= 3 else [min(values), st.median(values)]
        iqr = q[-1] - q[0] if len(q) >= 2 else 0.0
        above = ""
        if args.baseline is not None:
            n_above = sum(1 for v in values if v > args.baseline)
            above = f"{n_above}/{len(values)}"
        print(f"{name:10s} {len(values):2d} {st.median(values):9.0f} {st.mean(values):9.0f} "
              f"{st.pstdev(values):7.0f} {min(values):7.0f} {max(values):7.0f} {iqr:7.0f}  {above}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
