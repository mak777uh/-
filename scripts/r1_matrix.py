#!/usr/bin/env python
"""r1_matrix.py — агрегат мира `R1` (репликаторы без тела, H-ALIVE-50).

Читает `morphogenesis/experiments/R1_replicator/r1_*.json` (сырые summary) и собирает:
    by_arm:  k, n, units_final, share_units_divided, lineages_after_gate, I_obs/I_null/I_ratio
    criteria: режим чувствительности и «не оценивается» при <2 линиях после гейта.

Запуск (из корня):

    python scripts/r1_matrix.py --out morphogenesis/experiments/R1_replicator/r1_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
from pathlib import Path

NAME = re.compile(r"r1_(?:pilot_)?k(?P<k>\d+)_seed(?P<seed>\d+)\.json$")
MIN_LINEAGES = 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/R1_replicator")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows = []
    for path in sorted(glob.glob(str(Path(args.src) / "r1_*.json"))):
        match = NAME.search(Path(path).name)
        if not match or Path(path).name.endswith("_matrix.json"):
            continue
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rows.append({
            "artifact": str(path).replace("\\", "/"),
            "k": int(match.group("k")),
            "seed": int(match.group("seed")),
            "units_final": data.get("units_final"),
            "replicators_final": data.get("replicators_final"),
            "divisions_total": data.get("divisions_total"),
            "share_units_divided": data.get("share_units_divided"),
            "lineages_after_gate": data.get("lineages_after_gate"),
            "exposure_gate": data.get("exposure_gate"),
            "I_obs": data.get("I_obs"),
            "I_null_95": data.get("I_null_95"),
            "I_ratio": data.get("I_ratio"),
            "evaluable": (data.get("lineages_after_gate") or 0) >= MIN_LINEAGES,
        })

    by_arm = []
    for k in sorted({r["k"] for r in rows}):
        group = [r for r in rows if r["k"] == k]
        ok = [r for r in group if r["evaluable"]]
        ratios = [r["I_ratio"] for r in ok if r["I_ratio"] is not None]
        by_arm.append({
            "k": k,
            "runs": len(group),
            "evaluable_runs": len(ok),
            "units_final_median": statistics.median([r["units_final"] or 0 for r in group]),
            "share_units_divided_median": statistics.median(
                [r["share_units_divided"] or 0 for r in group]),
            "lineages_after_gate_median": statistics.median(
                [r["lineages_after_gate"] or 0 for r in group]),
            "I_ratio_median": round(statistics.median(ratios), 3) if ratios else None,
            "I_above_null_k": sum(1 for r in ok
                                  if (r["I_obs"] or 0) > (r["I_null_95"] or 0)),
            "status": "evaluable" if len(ok) == len(group) else "not evaluable",
        })

    payload = {
        "kind": "r1_runs",
        "world": "R1: репликаторы без тела; единица = k репликаторов; хемостат, подача не зависит от k",
        "metric": {
            "share_units_divided": "доля единиц, которые делились хотя бы раз (метрика чувствительности; "
                                   "«доля выше порога» структурно ≈0 из-за мгновенного деления)",
            "lineages_after_gate": f"линий с экспозицией >= {rows[0]['exposure_gate'] if rows else 50} "
                                   "репликатор-шагов (аналог гейта «>=5 клеток» в W2-bud)",
            "I_obs": "Var(w)/mean(w)^2 по линиям после гейта, w = делений / экспозиция",
            "I_null_95": "условный Пуассон: X_i ~ Poisson(rate * exposure_i)",
            "evaluable": f"lineages_after_gate >= {MIN_LINEAGES}; иначе плечо НЕ ОЦЕНИВАЕТСЯ",
        },
        "rows": rows,
        "by_arm": by_arm,
        "criteria": {
            "monotone_prediction": "I_ratio(k=1) > I_ratio(k=2) > I_ratio(k=8)",
            "pilot_note": "пилот: 1 сид на плечо; серия — 10 сидов после проверки режима",
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | строк {len(rows)}")
    print(f"{'k':>3} {'n':>3} {'eval':>5} {'единиц':>8} {'делилось':>9} {'линий':>6} "
          f"{'I_ratio':>8} {'I>null':>7} {'статус':>15}")
    for a in by_arm:
        print(f"{a['k']:>3} {a['runs']:>3} {a['evaluable_runs']:>5} {a['units_final_median']:>8} "
              f"{a['share_units_divided_median']:>9} {a['lineages_after_gate_median']:>6} "
              f"{str(a['I_ratio_median']):>8} {a['I_above_null_k']:>7} {a['status']:>15}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
