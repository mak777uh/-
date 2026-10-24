#!/usr/bin/env python
"""V8 (инвазия: размещение × правило слияния): таблица и критерии по пре-регистрации.

Пре-регистрация: reports/2026-10-24-placement-merge-plan.md.
Семантика (важно, цена путаницы — два инцидента): `--type-start a`, `--invade-type 1`
(тип 1 = B). Значит `a_share_final` — доля РЕЗИДЕНТА A, а доля инвайдера B = 1 − a_share_final.

Критерии (записаны заранее):
  * размещение: into_gap majority >= 8/10 и into_resident majority <= 2/10;
  * правило: mass_weighted выше majority на >= 6/10 при том же размещении;
  * ни то, ни другое: все плечи <= 2/10;
  * невалидно: injection_share > 0.05; alive_final < 100 (коллапс резидента);
  * ворота постановки: resident_free <= 2/10 => серия невалидна (пятно не растёт само).

Запуск: python library/tools/v8_matrix.py --src morphogenesis/experiments/E09_pond --glob "v8_*.json"
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import defaultdict
from pathlib import Path


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)


def classify(name: str, summary: dict) -> dict:
    cfg = summary.get("config") or {}
    placement = cfg.get("invade_placement", "random")
    merge = cfg.get("merge_rule", "majority")
    a_final = summary.get("a_share_final")
    invader_share = None if a_final is None else round(1.0 - float(a_final), 4)
    inject = summary.get("injection_share_actual", summary.get("invader_share_after"))
    alive = (summary.get("final") or {}).get("alive_cells") or summary.get("alive_final")
    emptied = "resident_free" in name
    invalid = None
    if inject is not None and inject > 0.05:
        invalid = f"injection_share {inject:.3f} > 0.05"
    elif alive is not None and alive < 100 and not emptied:
        invalid = f"alive_final {alive} < 100 (резидент не устоялся)"
    return {"artifact": name, "placement": placement, "merge": merge,
            "empty_field": emptied, "invader_share_final": invader_share,
            "survived": None if invader_share is None else invader_share > 0,
            "invalid": invalid, "injection_share": inject, "alive_final": alive}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="v8_*.json")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    rows = []
    for path in sorted(glob.glob(str(Path(args.src) / args.glob))):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rows.append(classify(Path(path).name, data.get("summary") or data))

    groups: dict[tuple, list] = defaultdict(list)
    for row in rows:
        key = ("empty" if row["empty_field"] else row["placement"], row["merge"])
        groups[key].append(row)

    print(f"артефактов: {len(rows)} | групп: {len(groups)}")
    print(f"{'плечо':22} {'n':>3} {'годных':>6} {'выжило':>7} {'доля':>6}  95% интервал")
    verdicts = {}
    for key, items in sorted(groups.items()):
        valid = [r for r in items if not r["invalid"] and r["survived"] is not None]
        k = sum(1 for r in valid if r["survived"])
        n = len(valid)
        ci = wilson(k, n)
        label = f"{key[0]} / {key[1]}"
        print(f"{label:22} {len(items):>3} {n:>6} {k:>7} {(k / n if n else 0):>6.2f}  {ci}")
        verdicts[label] = (k, n, ci)

    def rate(label):
        k, n, _ = verdicts.get(label, (0, 0, None))
        return (k, n)

    def le(label, x):
        k, n = rate(label); return n > 0 and k <= x

    def ge(label, x):
        k, n = rate(label); return n > 0 and k >= x

    planned = {"random / majority", "random / mass_weighted", "gap / majority",
               "gap / mass_weighted"}
    complete = {label for label, (_, n, _) in verdicts.items() if n >= 10}
    if not planned <= complete:
        missing = ", ".join(sorted(planned - complete))
        print(f"\nплечи неполные (нужно по 10 годных): {missing}")
        print("  вердикт не выносится — серия идёт или часть прогонов невалидна")
        if args.json:
            Path(args.json).write_text(json.dumps(
                {"rows": rows, "groups": {f"{k[0]}/{k[1]}": v for k, v in verdicts.items()},
                 "verdict": "incomplete", "missing": sorted(planned - complete)},
                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0

    free = [r for r in rows if r["empty_field"] and not r["invalid"]]
    gate = (sum(1 for r in free if r["survived"]), len(free))
    print()
    if gate[1]:
        print(f"ворота постановки (resident_free): {gate[0]}/{gate[1]}")
        if gate[0] <= 2:
            print("  ВЕРДИКТ: серия невалидна по постановке (пятно не растёт само на пустом поле)")
    a = "random / majority"; b = "gap / majority"
    if rate(a)[1] and rate(b)[1]:
        if ge(b, 8) and le(a, 2):
            print("  размещение работает: into_gap >= 8/10, into_resident <= 2/10")
        elif max(rate(a)[0], rate(b)[0]) <= 2:
            print("  ни размещение, ни слияние: все плечи <= 2/10")
        for placement in ("random", "gap"):
            maj = rate(f"{placement} / majority"); wei = rate(f"{placement} / mass_weighted")
            if maj[1] and wei[1] and (wei[0] - maj[0]) >= 6:
                print(f"  правило слияния работает при {placement}: +{wei[0] - maj[0]}/10")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"rows": rows, "groups": {f"{k[0]}/{k[1]}": v for k, v in verdicts.items()}},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
