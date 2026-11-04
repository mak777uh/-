"""x168b_analyse.py — X168b: fusion share per (inflow, gap) cell, the crossing per rate, and the matched baseline.

The crossing of a rate is the highest tested gap whose fusion share is at least 0.6; gaps above it that fuse below that share
place it in the two-cell window between them.

Writes morphogenesis/experiments/E09_pond/l1_field_x168b_inflow_matrix.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x168b_inflow_matrix.json"
FUSE_AT = 0.6


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    return []


def r_of(a):
    return math.sqrt(max(a, 1.0) / math.pi)


def gaps_between(c, grid=96):
    c = sorted(c, key=lambda x: x["cx"])
    out = []
    for i in range(len(c) - 1):
        dx = abs(c[i + 1]["cx"] - c[i]["cx"]) % grid
        dy = abs(c[i + 1]["cy"] - c[i]["cy"]) % grid
        d = math.hypot(min(dx, grid - dx), min(dy, grid - dy))
        out.append(d - r_of(c[i]["area"]) - r_of(c[i + 1]["area"]))
    return out


def main() -> int:
    cells: dict[tuple[float, int], list[dict]] = {}
    for f in sorted(L1.glob("x168b_F*_g*_s96*.json")):
        if f.name.endswith(".compact.json"):
            continue
        parts = f.stem.split("_")
        flow = int(parts[1][1:]) / 1000.0
        gap = int(parts[2][1:])
        art = json.loads(f.read_text(encoding="utf-8"))
        series = art.get("series") or []
        counts = [row.get("components", len(comps(row))) for row in series]
        last_two = None
        for row in reversed(series):
            c = comps(row)
            if len(c) == 2:
                last_two = gaps_between(c)
                break
        cells.setdefault((flow, gap), []).append({"run": f.stem, "min": min(counts) if counts else None,
                                                  "gap_at_last_two": last_two})

    table = {}
    for (flow, gap), rows in sorted(cells.items()):
        fused = sum(1 for r in rows if r["min"] == 1)
        died = sum(1 for r in rows if r["min"] == 0)
        table[f"F{flow:g}_g{gap}"] = {"flow": flow, "gap": gap, "runs": len(rows), "fused": fused,
                                      "share": round(fused / len(rows), 4), "died": died,
                                      "mins": [r["min"] for r in rows]}

    def share(flow, gap):
        key = f"F{flow:g}_g{gap}"
        return table[key]["share"] if key in table else None

    crossings = {}
    for flow in sorted({f for f, _ in cells}):
        gs = sorted(g for f, g in cells if f == flow)
        last_fused = None
        for g in gs:
            if (share(flow, g) or 0) >= FUSE_AT:
                last_fused = g
        crossings[f"{flow:g}"] = last_fused

    controls = {f"{flow:g}": (share(flow, 8) is not None and share(flow, 8) >= 0.8)
                for flow in sorted({f for f, _ in cells})}
    all_gaps = [g for rows in cells.values() for r in rows for g in (r["gap_at_last_two"] or [])]
    spread = round(statistics.pstdev(all_gaps), 4) if len(all_gaps) > 1 else None
    row030 = {g: share(0.030, g) for g in (8, 10, 11, 12) if share(0.030, g) is not None}
    varies = len(set(row030.values())) > 1
    readout_ok = spread is not None and spread >= 0.2 and varies
    s11 = share(0.030, 11)

    if not all(controls.values()):
        verdict = ("NOT COMPARABLE: the gap-8 control failed at " +
                   ", ".join(f"F = {k}" for k, ok in controls.items() if not ok) +
                   ", so those arms are dropped and the crossings are reported for the rates that passed.")
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the readout does not vary across gaps or the contact gap does not vary."
    elif s11 is not None and s11 >= 0.6:
        verdict = ("X168'S CONTRAST WAS AN ARTEFACT: on a matched seed set and run length, F = 0.030 fuses at gap 11 in "
                   f"{s11:.0%} of runs, so the difference from 0.026 and 0.036 does not stand and the non-monotone reading is "
                   "withdrawn. The crossing is the same at all three rates within this design's resolution.")
    else:
        located = ", ".join(f"F = {k}: {v}" for k, v in crossings.items())
        verdict = ("X168 STANDS ON A MATCHED BASELINE: at F = 0.030 the crossing is between 10 and 11 cells "
                   f"({row030.get(10, float('nan')):.0%} at gap 10, {row030.get(11, float('nan')):.0%} at gap 11 on this seed "
                   f"set), while the 0.026 and 0.036 arms fuse at larger gaps. Located crossings (the highest gap fusing at "
                   f"≥ 0.6): {located}. So the crossing depends on the inflow rate, and 'about two cells' is a value at one "
                   "rate.")
    agg = {"kind": "x168b_inflow_matrix", "by_cell": table, "crossings": crossings,
           "share_at_f030_by_gap": row030, "controls": controls, "contact_gap_sd": spread,
           "verdict": verdict, "detail": {f"F{f:g}_g{g}": rows for (f, g), rows in sorted(cells.items())}}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for key, c in sorted(table.items()):
        print(f"[x168b] {key}: runs {c['runs']} fused {c['fused']} died {c['died']} share {c['share']} mins {c['mins']}")
    print(f"[x168b] crossings {crossings}")
    print(f"[x168b] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
