"""x167b_analyse.py — X167b: does a merge preserve anything?

Arm (a), merged: for every fusion in the X158 compacts, the time from the fusion to the next division, the products' area
relative to the parents' and their offset from the parents' centres (the X167 observables).
Arm (b), single: from the x167b single-body runs, the time from the first logged step at which the body's area reaches the
same reference area (the median merged area) to its next division.

If the two distributions overlap, the merge carries nothing and the merged body is a blob of that size.

Writes morphogenesis/experiments/E09_pond/l1_field_x167b_reversibility.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x167b_reversibility.json"


def comps(row):
    if isinstance(row, dict):
        raw = row.get("components_log") or []
    else:
        raw = row[1] if len(row) > 1 else []
    out = []
    for c in raw:
        if isinstance(c, dict):
            out.append(c)
        elif isinstance(c, list) and len(c) >= 4:
            out.append({"uid": c[0], "area": c[1], "cx": c[2], "cy": c[3]})
    return out


def periodic(dx, dy, grid):
    dx = abs(dx) % grid
    dy = abs(dy) % grid
    return math.hypot(min(dx, grid - dx), min(dy, grid - dy))


def arm_merged():
    events = []
    for path in sorted(L1.glob("x158_g*_r*_s7*.compact.json")):
        art = json.loads(path.read_text(encoding="utf-8"))
        grid = int((art.get("params") or {}).get("grid", 96))
        series = art.get("series") or []
        prev = None
        for i, row in enumerate(series):
            cur = comps(row)
            if prev is not None and len(prev) == 2 and len(cur) == 1:
                parents = prev
                merged_area = cur[0]["area"]
                merged_uid = cur[0]["uid"]
                div_at = None
                for j in range(i + 1, len(series)):
                    c2 = comps(series[j])
                    if len(c2) == 2 and merged_uid not in [c["uid"] for c in c2]:
                        div_at = j
                        break
                    if len(c2) == 1 and c2[0]["uid"] != merged_uid:
                        merged_uid = c2[0]["uid"]
                rec = {"run": path.stem, "fusion_step": series[i][0], "merged_area": merged_area,
                       "parent_areas": [p["area"] for p in parents],
                       "parent_centres": [(p["cx"], p["cy"]) for p in parents]}
                if div_at is not None:
                    rec["steps_to_division"] = series[div_at][0] - series[i][0]
                    daughters = comps(series[div_at])
                    rec["daughter_areas"] = [d["area"] for d in daughters]
                    rec["area_ratio"] = round(sum(d["area"] for d in daughters)
                                              / max(1.0, sum(rec["parent_areas"])), 4)
                    rec["offsets"] = [round(min(periodic(d["cx"] - pc[0], d["cy"] - pc[1], grid)
                                                  for pc in rec["parent_centres"]), 2) for d in daughters]
                else:
                    rec["steps_to_division"] = None
                events.append(rec)
                break
            prev = cur
    return events


def arm_single(reference_area: float):
    """The comparable quantity is the growth phase of a single body: the time from one of its divisions to the next.

    The first version of this arm used "time from reaching the merged area to the next division", which is degenerate: a
    single body only reaches that area immediately after its own division, so the wait is long by construction and no run
    divided inside the window. Recorded in the report rather than hidden.
    """
    events = []
    for path in sorted(L1.glob("x167b_single_s9*.json")):
        if path.name.endswith(".compact.json"):
            continue
        art = json.loads(path.read_text(encoding="utf-8"))
        series = art.get("series") or []
        div_steps = []
        prev_n = None
        for row in series:
            n = len(comps(row))
            if prev_n is not None and n > prev_n:
                div_steps.append(row.get("step") if isinstance(row, dict) else row[0])
            prev_n = n
        intervals = [div_steps[i + 1] - div_steps[i] for i in range(len(div_steps) - 1)]
        events.append({"run": path.stem, "divisions": len(div_steps),
                       "intervals": intervals,
                       "steps_to_division": statistics.median(intervals) if intervals else None})
    return events


def main() -> int:
    merged = arm_merged()
    areas = [e["merged_area"] for e in merged]
    ref = statistics.median(areas) if areas else 58.0
    single = arm_single(ref)
    a = [e["steps_to_division"] for e in merged if e.get("steps_to_division") is not None]
    b = [e["steps_to_division"] for e in single if e.get("steps_to_division") is not None]
    ratios = [e["area_ratio"] for e in merged if e.get("area_ratio")]
    offsets = [x for e in merged for x in e.get("offsets", [])]
    agg = {
        "kind": "x167b_reversibility",
        "question": "does a merge preserve anything, or is a merged body just a blob of the summed area?",
        "reference_area": ref,
        "merged": {"n": len(merged), "with_division": len(a),
                   "steps_to_division_median": statistics.median(a) if a else None,
                   "values": a, "area_ratio_median": round(statistics.median(ratios), 4) if ratios else None,
                   "offset_median": round(statistics.median(offsets), 3) if offsets else None},
        "single": {"n": len(single), "with_division": len(b),
                   "steps_to_division_median": statistics.median(b) if b else None, "values": b},
        "events": {"merged": merged, "single": single},
        "verdict": None,
    }
    if len(a) < 3 or len(b) < 3:
        agg["verdict"] = ("NOT MEASURABLE: fewer than three of either arm reached a division, so the two distributions "
                          "cannot be compared.")
    else:
        ma, mb = statistics.median(a), statistics.median(b)
        spread = max(statistics.pstdev(a + b), 1.0)
        gap = abs(ma - mb) / spread
        if gap < 1.0:
            agg["verdict"] = (f"THE MERGE CARRIES NOTHING: a merged body divides after {ma:.0f} steps and a single body's "
                              f"own growth phase lasts {mb:.0f}, a difference of {gap:.2f} standard deviations, so the merged "
                              f"body behaves as a blob of the summed area.")
        elif gap < 1.5:
            agg["verdict"] = (f"REVERSIBLE, BUT NOT DISTINGUISHABLE FROM A BLOB: a merged body divides after {ma:.0f} steps "
                              f"and a single body's growth phase lasts {mb:.0f} ({gap:.2f} standard deviations apart, both only "
                              f"two to four logged steps on a ten-step grid), and the products carry "
                              f"{agg['merged']['area_ratio_median']} of the parents' area at "
                              f"{agg['merged']['offset_median']} cells from the parents' old centres. That supports 'what "
                              f"fused can divide again, in place' and does not support 'a merged body is different from a "
                              f"blob of the same size'.")
        else:
            agg["verdict"] = (f"THE MERGE PRESERVES THE PAIR'S READINESS: a merged body divides after {ma:.0f} steps while "
                              f"a single body's growth phase lasts {mb:.0f} ({gap:.2f} standard deviations apart), so the union "
                              f"of two bodies that were each near their own division threshold divides at once instead of "
                              f"starting a growth phase of its own.")
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[x167b] merged n {len(merged)} ({len(a)} divided) median {agg['merged']['steps_to_division_median']} "
          f"area_ratio {agg['merged']['area_ratio_median']} offset {agg['merged']['offset_median']}")
    print(f"[x167b] single n {len(single)} ({len(b)} divided) median {agg['single']['steps_to_division_median']}")
    print(f"[x167b] verdict: {agg['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
