"""x164_analyse.py — X164: does the fusion crossing depend on the size RATIO?

Same reconstruction as X157/X166: the last logged step with exactly two components, the surface gap between them
(periodic boundaries, r = sqrt(area/pi)), and the fusion share per arm with a Wilson interval.

Writes morphogenesis/experiments/E09_pond/l1_field_x164_asymmetric.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x164_asymmetric.json"
GRID = 96
ARMS = ("asym_g4", "asym_g6", "asym_g8", "asym_g10", "sym_r3_g8", "sym_r6_g8")


def r_of(area: float) -> float:
    return math.sqrt(max(area, 1.0) / math.pi)


def periodic(dx: float, dy: float, grid: int = GRID) -> float:
    dx = abs(dx) % grid
    dy = abs(dy) % grid
    return math.hypot(min(dx, grid - dx), min(dy, grid - dy))


def wilson(k: int, n: int) -> list[float] | None:
    if n == 0:
        return None
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - s) / d, 4), round((c + s) / d, 4)]


def analyse_run(path: Path) -> dict:
    art = json.loads(path.read_text(encoding="utf-8"))
    rows = art.get("series") or []
    last_two = None
    fused = False
    for row in rows:
        comps = row.get("components_log") or []
        n = row.get("components", len(comps))
        if n == 2 and len(comps) == 2:
            last_two = row
        elif n == 1 and last_two is not None:
            fused = True
            break
    gap = None
    areas = None
    if last_two:
        c = last_two["components_log"]
        a, b = c[0], c[1]
        d = periodic(b["cx"] - a["cx"], b["cy"] - a["cy"])
        gap = d - r_of(a["area"]) - r_of(b["area"])
        areas = [a["area"], b["area"]]
    return {"run": path.stem, "fused": fused, "gap": gap, "areas": areas}


def main() -> int:
    by_arm: dict[str, list[dict]] = {a: [] for a in ARMS}
    for f in sorted(L1.glob("x164_*_s93*.json")):
        if f.name.endswith(".compact.json"):
            continue
        arm = next((a for a in ARMS if f.name.startswith(f"x164_{a}_")), None)
        if arm is None:
            continue
        r = analyse_run(f)
        r["seed"] = int(f.stem.rsplit("_s", 1)[-1])
        by_arm[arm].append(r)

    summary = {}
    for arm, runs in by_arm.items():
        if not runs:
            continue
        fused = [r for r in runs if r["fused"]]
        gaps = [r["gap"] for r in fused if r["gap"] is not None]
        summary[arm] = {
            "runs": len(runs), "fused": len(fused), "share": round(len(fused) / len(runs), 4),
            "wilson": wilson(len(fused), len(runs)),
            "g_median": round(statistics.median(gaps), 4) if gaps else None,
            "g_values": [round(g, 3) for g in gaps],
        }

    all_gaps = [r["gap"] for runs in by_arm.values() for r in runs if r["gap"] is not None]
    spread = round(statistics.pstdev(all_gaps), 4) if len(all_gaps) > 1 else None
    control_ok = (summary.get("sym_r3_g8", {}).get("share", 0) >= 0.8
                  and summary.get("sym_r6_g8", {}).get("share", 0) >= 0.8)
    readout_ok = bool(all_gaps) and (spread or 0) >= 0.1 and 0 <= statistics.median(all_gaps) <= 6

    asym = [summary.get(f"asym_g{g}", {}).get("share") for g in (4, 6, 8, 10)]
    crossing = None
    for g, share in zip((4, 6, 8, 10), asym):
        if share is not None and share < 0.5:
            crossing = g
            break
    if not control_ok:
        verdict = "NOT COMPARABLE: the symmetric controls did not reproduce the block's fusion shares."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the gap readout does not vary as required."
    elif crossing is None:
        verdict = ("THE ASYMMETRIC PAIR FUSES AT EVERY GAP TESTED (4-10 cells): the crossing for the pair (3, 6) lies "
                   "beyond 10 cells, so this series gives a lower bound only.")
    elif crossing <= 4:
        verdict = ("THE ASYMMETRIC PAIR FUSES AT NO GAP TESTED: the crossing for (3, 6) lies below 4 cells, an upper "
                   "bound only.")
    else:
        verdict = (f"THE CROSSING MOVES WITH THE RATIO: the pair (3, 6) stops fusing between {crossing - 2} and {crossing} "
                   f"cells, against 10 ± 1 for equal bodies, so the crossing is a property of the pair and not only of the "
                   f"medium.")

    agg = {"kind": "x164_asymmetric", "question": "does the fusion crossing depend on the size ratio?",
           "by_arm": summary, "gap_sd_overall": spread,
           "controls": {"positive_control_fires": control_ok, "readout_exists": readout_ok},
           "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for arm, s in summary.items():
        print(f"[x164] {arm:10s} fused {s['fused']}/{s['runs']} share {s['share']} wilson {s['wilson']} "
              f"g_median {s['g_median']} values {s['g_values']}")
    print(f"[x164] gap sd {spread}")
    print(f"[x164] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
