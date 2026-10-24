#!/usr/bin/env python
"""Собрать colony_type_matrix.json из артефактов дизайна 3 (инвазия новой колонии).

Зачем: критерий «растёт ли редкий тип» должен считаться машинно и одинаково, а не глазами по
логу. Скрипт:
  * читает `_hourly/polish/colinv3_*.json` (или указанный каталог);
  * берёт фактическую долю инвайдера сразу после подсадки и в конце;
  * считает рост `end / start` (инвазионный критерий: >1 — редкий растёт);
  * помечает прогон невалидным, если фактическая доля подсадки не близка к ожидаемой
    (переворот компонента — та самая ошибка дизайна 2);
  * пишет агрегат с `kind: invasion_runs`, чтобы его проверял `aggregate_check`
    (проверки `check_invasion`: рост = end/start, невалидные помечены).

Запуск:
    python scripts/colony_matrix.py --src ../_hourly/polish --out morphogenesis/experiments/E09_pond/colony_type_matrix.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

NAME = re.compile(r"colinv3_(fd\d+)_(\w+?)_(inherit|random)_seed(\d+)\.json$")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default=str(Path(__file__).resolve().parents[2] / "_hourly" / "polish"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--design", default="3")
    ap.add_argument("--provenance-note", default=None,
                    help="оговорка о происхождении артефактов серии (пишется в агрегат верхним полем)")
    ap.add_argument("--invalid-extra", default=None,
                    help="вторая причина для строк с долей подсадки > 0.05 (дописывается к первой)")
    args = ap.parse_args(argv)

    src = Path(args.src)
    rows = []
    for path in sorted(src.glob("colinv3_*.json")):
        match = NAME.search(path.name)
        if not match:
            continue
        fd, direction, mode, seed = match.groups()
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary") or data
        start = summary.get("injection_share_actual", summary.get("invader_share_after"))
        end = summary.get("a_share_final")
        if end is None:
            end = (summary.get("final") or {}).get("a_share")
        # направление BinvA: резидент B, инвайдер A -> доля инвайдера = a_share
        # направление AinvB: резидент A, инвайдер B -> доля инвайдера = 1 - a_share
        if end is not None and direction == "AinvB":
            end = 1.0 - end
        growth = (end / start) if (start and end is not None and start > 0) else None
        invalid_reason = summary.get("invalid_reason")
        if not invalid_reason and start is not None and start > 0.05:
            invalid_reason = f"injection_share {start:.3f} > 0.05 — не редкая подсадка (переворот или крупная инъекция)"
        if args.invalid_extra and invalid_reason and start is not None and start > 0.05:
            invalid_reason = f"{invalid_reason}; {args.invalid_extra}"
        rows.append({
            "design": summary.get("design", args.design),
            "fd": fd,
            "direction": direction,
            "mode": mode,
            "seed": int(seed),
            "pop_time": summary.get("pop_time"),
            "colony_cells_at_invasion": summary.get("colony_cells_at_invasion"),
            "invader_share_start": start,
            "invader_share_end": end,
            "growth": growth,
            "fixated": bool(end is not None and end > 0.5),
            "invalid_reason": invalid_reason,
            "artifact": str(path.name),
        })

    payload = {
        "kind": "invasion_runs",
        "experiment": "E09_pond_colony_type",
        "design": args.design,
        "metric": "invader growth = end/start",
        "note": "собрано scripts/colony_matrix.py из артефактов дизайна 3",
        "rows": rows,
    }
    if args.provenance_note:
        payload["provenance_note"] = args.provenance_note
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    valid = [r for r in rows if not r["invalid_reason"]]
    by = defaultdict(list)
    for row in valid:
        by[(row["fd"], row["mode"])].append(row["growth"])
    for key, values in sorted(by.items()):
        print(f"  {key[0]} {key[1]:8s} n={len(values)} рост: "
              + ", ".join("—" if v is None else f"{v:.2f}" for v in values))
    if len(valid) != len(rows):
        print(f"  невалидных: {len(rows) - len(valid)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
