"""x179_crossing_table.py — X179: every two-body cell this line has run, with intervals, from the committed projections.

The unit is a **cell**: a body radius, a surface gap and an inflow rate. Each cell's share is the fraction of its runs that
reach one component at some logged step, with a Wilson interval. Cells are identified from the data itself — the radius from the
seeded area (`sqrt(area/pi)`) and the gap from the centre separation minus twice that radius — so the table can be rebuilt from
`*.compact.json` alone, without the lab machine's raw logs.

Cells with other than two seeded components (single-body controls, rows of three) are counted separately and listed, not mixed
into the two-body table.

Writes morphogenesis/experiments/E09_pond/l1_field_x179_crossing_table.json.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x179_crossing_table.json"
GRID = 96


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def wrap_delta(a: float, b: float) -> float:
    d = abs(a - b) % GRID
    return min(d, GRID - d)


def comp_tuple(c):
    """Components appear as [uid, area, cx, cy] in most projections and as dicts in the shape runs (x156)."""
    if isinstance(c, dict):
        return int(c.get("uid", 0)), float(c.get("area", 0)), float(c.get("cx", 0)), float(c.get("cy", 0))
    return int(c[0]), float(c[1]), float(c[2]), float(c[3])


def n_comps(entry) -> int:
    return len(entry[1]) if isinstance(entry, list) and len(entry) > 1 and isinstance(entry[1], list) else 0


def main() -> int:
    cells: dict[tuple, dict] = defaultdict(lambda: {"runs": 0, "fused": 0, "sources": [], "per_source": {}})
    other: dict[tuple, dict] = defaultdict(lambda: {"runs": 0, "fused": 0, "sources": [], "per_source": {}})

    files = sorted(L1.glob("*.compact.json"))
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        params = d.get("params") or {}
        if not series:
            continue
        first = series[0]
        if not isinstance(first, list) or len(first) != 2 or not isinstance(first[1], list) or not first[1]:
            continue
        comps = [comp_tuple(c) for c in first[1]]
        r0 = math.sqrt(max(comps[0][1], 1) / math.pi)
        if len(comps) == 2:
            sep = wrap_delta(comps[0][2], comps[1][2]) if abs(comps[0][3] - comps[1][3]) < 1e-6 \
                else math.dist((comps[0][2], comps[0][3]), (comps[1][2], comps[1][3]))
            gap = round(sep - 2 * r0)
            key = (round(r0, 1), gap, round(float(params.get("F", 0.0)), 3))
        else:
            key = (round(r0, 1), len(comps), round(float(params.get("F", 0.0)), 3))
        fused = any(n_comps(row) == 1 for row in series)
        bucket = cells if len(comps) == 2 else other
        bucket[key]["runs"] += 1
        bucket[key]["fused"] += int(fused)
        src = f.stem.replace(".compact", "")
        # a "source family" is the run prefix before the seed suffix (_s123 or a bare seed number): the arms that could be
        # pooled should be pooled, and the families that disagree should be visible.
        family = src.split("_s")[0] if "_s" in src else src
        bucket[key]["sources"].append(src)
        bucket[key]["per_source"].setdefault(family, [0, 0])
        bucket[key]["per_source"][family][0] += int(fused)
        bucket[key]["per_source"][family][1] += 1

    def table(d: dict) -> list[dict]:
        rows = []
        for key in sorted(d, key=lambda k: (k[0], k[1], k[2])):
            v = d[key]
            share = round(v["fused"] / v["runs"], 4) if v["runs"] else None
            shares = [c / n for c, n in v["per_source"].values() if n >= 3]
            spread = round(max(shares) - min(shares), 3) if len(shares) > 1 else None
            rows.append({"radius": key[0], "gap": key[1], "F": key[2], "runs": v["runs"], "fused": v["fused"],
                         "share": share, "wilson": wilson(v["fused"], v["runs"]),
                         "per_source": {k: {"fused": c, "runs": n, "share": round(c / n, 3)}
                                        for k, (c, n) in sorted(v["per_source"].items())},
                         "source_spread": spread,
                         "heterogeneous": bool(spread is not None and spread > 0.4)})
        return rows

    two = table(cells)
    three_plus = table(other)
    total_runs = sum(r["runs"] for r in two)
    total_files = len(files)
    verdict = (f"A TABLE OF {len(two)} TWO-BODY CELLS AND {total_runs} RUNS, ALL OF IT FROM COMMITTED PROJECTIONS: the crossing "
               "(the first gap whose share falls below one half) is read off with its interval rather than as a single number.")
    agg = {"kind": "x179_crossing_table", "grid": GRID, "files_scanned": total_files,
           "two_body_cells": two, "other_cells": three_plus, "two_body_runs": total_runs, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"[x179] scanned {total_files} compact projections; {len(two)} two-body cells, {total_runs} runs")
    print(f"{'radius':>6} {'gap':>4} {'F':>6} {'fused':>7} {'runs':>5} {'share':>6}  wilson                spread het")
    for r in two:
        print(f"{r['radius']:>6} {r['gap']:>4} {r['F']:>6} {r['fused']:>7} {r['runs']:>5} {r['share']:>6}  "
              f"{str(r['wilson']):<21} {str(r['source_spread']):>6} {r['heterogeneous']}")
    het = [r for r in two if r["heterogeneous"]]
    if het:
        print("[x179] cells where the pooling hides disagreement between seed families:")
        for r in het:
            parts = "; ".join(f"{k}: {v['fused']}/{v['runs']}" for k, v in r["per_source"].items() if v["runs"] >= 3)
            print(f"   radius {r['radius']} gap {r['gap']} F {r['F']}: {parts}")
    if three_plus:
        print("[x179] other seeded-component cells (controls and rows):")
        for r in three_plus:
            print(f"   radius {r['radius']} components {r['gap']} F {r['F']}: {r['fused']}/{r['runs']} = {r['share']}")
    print(f"[x179] {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
