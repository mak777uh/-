#!/usr/bin/env python
"""Кривая «класс от длины роллаута» для одного или нескольких чекпоинтов.

Зачем: класс может зависеть от того, сколько шагов CA выполняется при переписи
(в смежных работах метрика зависит от числа шагов инференса). Протокол v1.1
(§3) требует такой кривой для каждого заявленного класса.

Скрипт запускает `e02c_census.py` последовательно с разной длиной роллаута и
печатает таблицу «семейство × длина → класс». Каждая перепись пишет свою пару
start/finish в журнал, поэтому след остаётся полным.

Запуск (из корня репозитория):

    python scripts/census_curve.py \
        --families E02c_R-9_s2000_seed42_tf32 \
        --lengths 500,1000,2000,3000 --tag seed42tf32

Результаты: `morphogenesis/experiments/E02c_replication/census_curve_<tag>_<len>.json`
и `...summary_curve_<tag>_<len>.json`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MORPH = REPO / "morphogenesis"
EXP = MORPH / "experiments" / "E02c_replication"


def run_census(families: list[str], length: int, tag: str, seeds: str) -> dict | None:
    out = EXP / f"census_curve_{tag}_{length}.json"
    summary = EXP / f"summary_curve_{tag}_{length}.json"
    cmd = [
        sys.executable,
        "-u",
        "e02c_census.py",
        "--seeds", seeds,
        "--steps", str(length),
        "--families", ",".join(families),
        "--allow-missing-control",
        "--out", str(out.relative_to(MORPH)),
        "--summary-out", str(summary.relative_to(MORPH)),
    ]
    print(f"=== длина роллаута {length} ===", flush=True)
    proc = subprocess.run(cmd, cwd=MORPH)
    if proc.returncode != 0:
        print(f"[curve] перепись на {length} шагах упала (код {proc.returncode})")
        return None
    if not summary.exists():
        print(f"[curve] нет сводки {summary}")
        return None
    return json.loads(summary.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--families", required=True, help="через запятую")
    ap.add_argument("--lengths", default="500,1000,2000,3000")
    ap.add_argument("--tag", default="curve")
    ap.add_argument("--seeds", default="0-63")
    args = ap.parse_args(argv)

    families = [f.strip() for f in args.families.split(",") if f.strip()]
    lengths = [int(x) for x in args.lengths.split(",") if x.strip()]
    table: dict[str, dict[int, dict]] = {fam: {} for fam in families}

    for length in lengths:
        summary = run_census(families, length, args.tag, args.seeds)
        if summary is None:
            continue
        stats = summary.get("stats", {})
        for fam in families:
            entry = stats.get(fam) or {}
            table[fam][length] = {
                "class": entry.get("frozen_class_counts"),
                "struct_2": entry.get("struct_2"),
                "stable_frozen": entry.get("struct_2_stable_frozen"),
            }

    print("\n== кривая класс-длина роллаута ==")
    header = f"{'семейство':32s}" + "".join(f"{ln:>26d}" for ln in lengths)
    print(header)
    for fam, by_len in table.items():
        line = f"{fam:32s}"
        for length in lengths:
            cell = by_len.get(length)
            if not cell:
                line += f"{'—':>26s}"
            else:
                cls = cell["class"] or {}
                desc = ",".join(f"{k}:{v}" for k, v in sorted(cls.items()))
                line += f"{desc[:25]:>26s}"
        print(line)

    payload = {
        "kind": "census_curve",
        "protocol": "docs/protocol.md",
        "families": families,
        "lengths": lengths,
        "table": {fam: {str(k): v for k, v in d.items()} for fam, d in table.items()},
    }
    path = EXP / f"curve_{args.tag}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n[curve] таблица записана: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
