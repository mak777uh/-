"""x167_fusion_reversibility.py — is a merged body a new object, or the old pair that can come apart?

After a fusion (component count 2 -> 1) the merged component is followed to the end of the log. The question is whether it
divides again, and whether the daughters look like the ORIGINAL two bodies (areas near the parents' areas, centres near the
parents' centres) or like two halves of a single body grown to the same area.

Readout: (a) the re-division share of merged bodies within the observation window, (b) the area ratio of the first
division after a fusion to the two parents' areas, (c) the distance of the division's products from the parents' old
centres.

Analysis only, on the X158 compact logs (two seeded bodies, six thousand steps). Writes
morphogenesis/experiments/E09_pond/l1_field_x167_reversibility.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x167_reversibility.json"
PATTERN = "x158_g*_r*_s7*.compact.json"


def r_of(area: float) -> float:
    return math.sqrt(max(area, 1.0) / math.pi)


def periodic(dx: float, dy: float, grid: int) -> float:
    dx = abs(dx) % grid
    dy = abs(dy) % grid
    return math.hypot(min(dx, grid - dx), min(dy, grid - dy))


def components(row):
    """Normalise a compact row's components to dicts: the X158 compacts store [uid, area, cx, cy]."""
    raw = row[1] if isinstance(row, list) and len(row) > 1 else []
    out = []
    for c in raw:
        if isinstance(c, dict):
            out.append(c)
        elif isinstance(c, list) and len(c) >= 4:
            out.append({"uid": c[0], "area": c[1], "cx": c[2], "cy": c[3]})
    return out


def main() -> int:
    files = sorted(L1.glob(PATTERN))
    if not files:
        raise SystemExit(f"no logs match {PATTERN}")
    events = []
    for path in files:
        art = json.loads(path.read_text(encoding="utf-8"))
        params = art.get("params") or {}
        grid = int(params.get("grid", 96))
        series = art.get("series") or []
        # find the first 2 -> 1 transition and the parents' state just before it
        prev = None
        fusion_at = None
        parents = None
        for i, row in enumerate(series):
            comps = components(row)
            if prev is not None and len(prev) == 2 and len(comps) == 1:
                fusion_at = i
                parents = prev
                merged = comps[0]
                break
            prev = comps
        if fusion_at is None or parents is None:
            events.append({"run": path.stem, "fused": False})
            continue
        # follow the merged component to the first division
        div = None
        merged_uid = merged["uid"]
        for row in series[fusion_at + 1:]:
            comps = components(row)
            uids = [c["uid"] for c in comps]
            if len(comps) == 2 and merged_uid not in uids:
                div = comps
                break
            if len(comps) == 1 and uids and uids[0] != merged_uid:
                merged_uid = uids[0]
        rec = {
            "run": path.stem, "fused": True,
            "parent_areas": [p["area"] for p in parents],
            "parent_centres": [[round(p["cx"], 2), round(p["cy"], 2)] for p in parents],
            "merged_area": merged["area"],
            "redivided": div is not None,
            "steps_after_fusion_logged": len(series) - fusion_at - 1,
        }
        if div is not None:
            rec["daughter_areas"] = [c["area"] for c in div]
            rec["daughter_centres"] = [[round(c["cx"], 2), round(c["cy"], 2)] for c in div]
            # how close are the daughters' centres to the parents' centres?
            d = []
            for dc in div:
                d.append(min(periodic(dc["cx"] - pc[0], dc["cy"] - pc[1], grid) for pc in rec["parent_centres"]))
            rec["daughter_offset_cells"] = [round(x, 2) for x in d]
            rec["area_ratio"] = round(sum(rec["daughter_areas"]) / max(1.0, sum(rec["parent_areas"])), 4)
        events.append(rec)

    fused = [e for e in events if e.get("fused")]
    red = [e for e in fused if e.get("redivided")]
    ratios = [e["area_ratio"] for e in red if e.get("area_ratio") is not None]
    offsets = [x for e in red for x in e.get("daughter_offset_cells", [])]
    agg = {
        "kind": "x167_reversibility",
        "question": "is a merged body a new object, or the old pair that can come apart?",
        "logs": len(files), "fusions": len(fused), "redivided": len(red),
        "redivision_share": round(len(red) / len(fused), 4) if fused else None,
        "area_ratio_median": round(statistics.median(ratios), 4) if ratios else None,
        "daughter_offset_median": round(statistics.median(offsets), 3) if offsets else None,
        "steps_after_fusion_median": statistics.median([e["steps_after_fusion_logged"] for e in fused]) if fused else None,
        "events": events,
        "verdict": None,
    }
    if not fused:
        agg["verdict"] = "NOT MEASURABLE: no two-to-one transition in these logs."
    elif len(red) == 0:
        agg["verdict"] = ("NOT MEASURABLE AT THIS HORIZON: no merged body divided again inside the observation window, so "
                          "the item cannot say whether the merge erased identity or the log is simply too short.")
    elif agg["area_ratio_median"] and 0.7 <= agg["area_ratio_median"] <= 1.4 and (agg["daughter_offset_median"] or 99) < 4:
        agg["verdict"] = ("THE PAIR COMES APART: a merged body that divides again does so into two bodies of the parents' "
                          "combined area, near the parents' old positions, so the merge did not create a new identity.")
    else:
        agg["verdict"] = ("THE MERGE MAKES A NEW OBJECT: the products of a re-division do not resemble the original pair in "
                          "area or position, so the merged body divides as one body.")
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[x167] logs {len(files)} fusions {len(fused)} redivided {len(red)} share {agg['redivision_share']}")
    print(f"[x167] area ratio {agg['area_ratio_median']} offset {agg['daughter_offset_median']} "
          f"steps after fusion {agg['steps_after_fusion_median']}")
    print(f"[x167] verdict: {agg['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
