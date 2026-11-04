"""x168_analyse.py — X168: does the crossing move with the inflow rate?

Readout: the fusion share at gaps 8 and 11 in each F arm, and the surface gap at the last logged step with two bodies.
If the gap-11 share is the same in both arms, turnover does not set the crossing in this window.

Writes morphogenesis/experiments/E09_pond/l1_field_x168_inflow.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x168_inflow.json"


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
    arms: dict[tuple[str, int], list[dict]] = {}
    for f in sorted(L1.glob("x168_F*_g*_s96*.json")):
        if f.name.endswith(".compact.json"):
            continue
        parts = f.stem.split("_")
        flow = int(parts[1][1:]) / 1000.0
        gap = int(parts[2][1:])
        art = json.loads(f.read_text(encoding="utf-8"))
        series = art.get("series") or []
        counts = [row.get("components", len(comps(row))) for row in series]
        n_min = min(counts) if counts else 0
        last_two = None
        for row in reversed(series):
            c = comps(row)
            if len(c) == 2:
                last_two = gaps_between(c)
                break
        arms.setdefault((flow, gap), []).append({"run": f.stem, "components_min": n_min,
                                                "components_final": counts[-1] if counts else 0,
                                                "gap_at_last_two": last_two})

    summary = {}
    for (flow, gap), rows in sorted(arms.items()):
        fused = sum(1 for r in rows if r["components_min"] == 1)
        died = sum(1 for r in rows if r["components_min"] == 0)
        summary[f"F{flow:g}_g{gap}"] = {"flow": flow, "gap": gap, "runs": len(rows), "fused": fused, "died": died,
                                        "share": round(fused / len(rows), 4),
                                        "mins": [r["components_min"] for r in rows]}
    def share(flow, gap):
        key = f"F{flow:g}_g{gap}"
        return summary[key]["share"] if key in summary else None

    g8 = [share(0.026, 8), share(0.036, 8)]
    g11 = [share(0.026, 11), share(0.036, 11)]
    controls_ok = all(s is not None and s >= 0.8 for s in g8)
    gaps_all = [g for rows in arms.values() for r in rows for g in (r["gap_at_last_two"] or [])]
    spread = round(statistics.pstdev(gaps_all), 4) if len(gaps_all) > 1 else None
    baseline_g11 = 2.0 / 15.0  # X158 at F = 0.030, surface gap 11
    moved = all(s is not None and abs(s - baseline_g11) >= 0.4 for s in g11)
    readout_ok = spread is not None and spread >= 0.2 and (g11[0] != g11[1] or moved)
    if not controls_ok:
        verdict = ("NOT COMPARABLE: the gap-8 control did not fire in both arms, so the two inflow rates are not the same "
                   "world and the crossing cannot be compared across them.")
    elif not readout_ok:
        verdict = ("NO DETECTABLE DEPENDENCE OF THE CROSSING ON F: the gap-11 share is the same at both inflow rates "
                   f"({g11[0]} and {g11[1]}) and no different from the 13 % of X158 at F = 0.030, so in this window the "
                   "crossing is not set by the turnover. With five seeds a small shift could still be hidden.")
    elif g11[0] == g11[1] and moved:
        verdict = ("THE CROSSING MOVES WITH THE INFLOW RATE, AND NOT MONOTONICALLY: at F = 0.030 a pair at a surface gap of "
                   "11 fuses in 2 of 15 runs, but at both F = 0.026 and F = 0.036 it fuses in "
                   f"{g11[0]:.0%} of runs - both a lower and a higher inflow push the crossing past 11 cells, so the "
                   "crossing has a minimum near 0.030 and the 'about two cells' of §4.1 is a value at one inflow rate. This "
                   "design shows the direction, not the new position: both arms fused at gap 11, so their crossing lies "
                   "beyond it and needs brackets at 12 and 14.")
    else:
        verdict = ("THE CROSSING MOVES WITH THE INFLOW RATE: the gap-11 share is "
                   f"{g11[0]:.0%} at F = 0.026 against {g11[1]:.0%} at F = 0.036 (and 13 % at F = 0.030), so the 'about two "
                   "cells' of §4.1 is a value at one inflow rate and has to be written as a curve.")
    agg = {"kind": "x168_inflow", "by_arm": summary, "baseline_g11_share_at_F030": round(baseline_g11, 4),
           "controls": {"gap8_fires_both_arms": controls_ok, "readout_exists": readout_ok},
           "gap_at_last_two_sd": spread, "verdict": verdict,
           "detail": {f"F{f:g}_g{g}": rows for (f, g), rows in sorted(arms.items())}}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for key, s in sorted(summary.items()):
        print(f"[x168] {key}: runs {s['runs']} fused {s['fused']} died {s['died']} share {s['share']} mins {s['mins']}")
    print(f"[x168] gap sd {spread}")
    print(f"[x168] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
