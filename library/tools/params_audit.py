#!/usr/bin/env python
"""params_audit.py — какие ручки мира реально менялись, а какие всегда стояли на одном значении.

Зачем: у нас есть параметры, которые выглядят как условия («память среды», «защита слабеющих»), но если
они ни разу не были ненулевыми, то условие **не проверялось** — а в выводах оно может выглядеть проверенным.

Запуск:
  python library/tools/params_audit.py                 # свод по всем артефактам
  python library/tools/params_audit.py --field buffer_tau
Коды: 0 — отчёт построен; 1 — артефактов не найдено.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
ROOT = REPO / "morphogenesis" / "experiments"


def scan():
    values = collections.defaultdict(collections.Counter)
    n_files = 0
    for path in ROOT.rglob("*.json"):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        params = d.get("params")
        if not isinstance(params, dict):
            continue
        n_files += 1
        for key, value in params.items():
            values[key][repr(value) if not isinstance(value, (int, float, bool, type(None))) else value] += 1
    return n_files, values


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="аудит ручек мира")
    ap.add_argument("--field", default=None, help="показать только одно поле")
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args(argv)

    n_files, values = scan()
    if not n_files:
        print("артефактов с params не найдено")
        return 1

    print(f"артефактов с params: {n_files}")
    dead, varied = [], []
    for key, counter in values.items():
        if args.field and key != args.field:
            continue
        (dead if len(counter) == 1 else varied).append((key, counter))

    print(f"\nПОСТОЯННЫЕ ручки (ни разу не менялись) — условие не проверялось: {len(dead)}")
    for key, counter in sorted(dead):
        value = next(iter(counter))
        print(f"  {key} = {value!r}  (во всех {counter[value]} артефактах)")

    print(f"\nИЗМЕНЯВШИЕСЯ ручки: {len(varied)}")
    for key, counter in sorted(varied, key=lambda kv: -len(kv[1]))[: args.limit]:
        top = ", ".join(f"{v!r}×{c}" for v, c in counter.most_common(4))
        print(f"  {key}: {len(counter)} значений | {top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
