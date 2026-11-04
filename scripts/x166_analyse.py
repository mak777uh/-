"""x166_analyse.py — X166: the contact threshold at one-step resolution.

For every run: find the first logged step at which the component count falls from two to one, read the two bodies'
areas and centres at the previous step, and report the surface gap between them (periodic boundaries, r = sqrt(A/pi)).
Because the log now samples every step, the residual window is the growth of the two radii over ONE step, not ten.

Writes morphogenesis/experiments/E09_pond/l1_field_x166_threshold.json.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x166_threshold.json"
GRID = 96


def r_of(area: float) -> float:
    return math.sqrt(max(area, 1.0) / math.pi)


def periodic(dx: float, dy: float, grid: int = GRID) -> float:
    dx = abs(dx) % grid
    dy = abs(dy) % grid
    dx = min(dx, grid - dx)
    dy = min(dy, grid - dy)
    return math.hypot(dx, dy)


def gap_of(comps, grid: int = GRID):
    if len(comps) < 2:
        return None
    a, b = comps[0], comps[1]
    d = periodic(b["cx"] - a["cx"], b["cy"] - a["cy"], grid) - r_of(a["area"]) - r_of(b["area"])
    return d


def analyse_run(path: Path) -> dict | None:
    art = json.loads(path.read_text(encoding="utf-8"))
    rows = art.get("series") or []
    if not rows:
        return None
    params = art.get("params") or {}
    arm = path.stem  # x166_g8_r30_s911
    parts = dict(p.split("_r") if False else ("", "") for p in [])
    gap_nom = None
    radius = None
    seed = None
    try:
        _, gpart, rpart, spart = arm.split("_")
        gap_nom = int(gpart[1:])
        radius = float(int(rpart[1:])) / 10
        seed = int(spart[1:])
    except Exception:
        pass

    two_steps = []
    fusion_step = None
    for row in rows:
        n = row.get("components")
        if n == 2:
            two_steps.append(row)
        elif n == 1 and two_steps:
            fusion_step = row.get("step")
            break
    if not two_steps:
        return {"arm": arm, "radius": radius, "gap": gap_nom, "seed": seed, "status": "never two bodies"}
    last = two_steps[-1]
    comps = last.get("components_log") or []
    g = gap_of(comps)
    # growth of the sum of the two radii over the last three one-step samples
    growth = None
    if len(two_steps) >= 3:
        def rsum(row):
            c = row.get("components_log") or []
            return sum(r_of(x["area"]) for x in c[:2]) if len(c) >= 2 else None
        a, b = rsum(two_steps[-3]), rsum(two_steps[-1])
        if a is not None and b is not None:
            growth = (b - a) / 2.0
    return {"arm": arm, "radius": radius, "gap": gap_nom, "seed": seed, "status": "fused" if fusion_step else "never one body",
            "fusion_step": fusion_step, "last_two_step": last.get("step"), "g_last": g,
            "growth_per_step": growth,
            "threshold_low": (g - growth) if (g is not None and growth is not None) else None,
            "one_step_window": growth}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    files = sorted(L1.glob("x166_g*_r*_s9*.json"))
    files = [f for f in files if not f.name.endswith(".compact.json")]
    runs = []
    for f in files:
        r = analyse_run(f)
        if r:
            runs.append(r)
    if not runs:
        raise SystemExit("no x166 runs")

    arms: dict[str, list[dict]] = {}
    for r in runs:
        arms.setdefault(f"r{r['radius']:.1f}_g{r['gap']}", []).append(r)

    summary = {}
    for name, rows in sorted(arms.items()):
        fused = [r for r in rows if r["status"] == "fused"]
        gs = [r["g_last"] for r in fused if r["g_last"] is not None]
        grows = [r["growth_per_step"] for r in fused if r["growth_per_step"] is not None]
        summary[name] = {
            "runs": len(rows), "fused": len(fused),
            "share": round(len(fused) / len(rows), 4) if rows else None,
            "g_last_median": round(statistics.median(gs), 4) if gs else None,
            "g_last_values": [round(x, 3) for x in gs],
            "g_last_sd": round(statistics.pstdev(gs), 4) if len(gs) > 1 else None,
            "growth_per_step_median": round(statistics.median(grows), 5) if grows else None,
            "fusion_step_median": statistics.median([r["fusion_step"] for r in fused if r["fusion_step"]]) if fused else None,
        }

    all_g = [r["g_last"] for r in runs if r["g_last"] is not None]
    all_growth = [r["growth_per_step"] for r in runs if r["growth_per_step"] is not None]
    one_step_window = statistics.median(all_growth) if all_growth else None
    per_arm_medians = [v["g_last_median"] for v in summary.values() if v["g_last_median"] is not None]
    spread = (max(per_arm_medians) - min(per_arm_medians)) if len(per_arm_medians) > 1 else None
    sds = [v["g_last_sd"] for v in summary.values() if v["g_last_sd"]]
    within = statistics.median(sds) if sds else None

    control_ok = (
        summary.get("r3.0_g8", {}).get("share", 0) >= 0.8 and summary.get("r6.0_g8", {}).get("share", 0) >= 0.8
    )
    readout_ok = bool(all_g) and statistics.pstdev(all_g) >= 0.1 and 0 <= statistics.median(all_g) <= 5
    if not control_ok:
        verdict = "NOT COMPARABLE: the gap-8 arms did not reproduce the block's fusion share."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the one-step readout does not vary as required."
    elif spread is not None and spread <= 0.2 and (within or 0) <= 0.5:
        verdict = (f"A THRESHOLD: the per-arm medians agree within {spread:.2f} cells and the within-arm scatter is "
                   f"{(within or 0):.2f}, so fusion happens at one gap value independent of size.")
    else:
        verdict = ("A BAND, NOT A THRESHOLD: the per-arm medians differ by "
                   f"{(spread if spread is not None else float('nan')):.2f} cells and the within-arm scatter is "
                   f"{(within if within is not None else float('nan')):.2f}, so fusion is stochastic within the window and "
                   "'about two cells' is a band by right, not by resolution.")

    agg = {
        "kind": "x166_threshold",
        "question": "at one-step resolution, is the contact gap a threshold or a band?",
        "runs": len(runs), "by_arm": summary,
        "all_g_last": {"median": round(statistics.median(all_g), 4) if all_g else None,
                       "sd": round(statistics.pstdev(all_g), 4) if len(all_g) > 1 else None,
                       "n": len(all_g)},
        "one_step_window": round(one_step_window, 5) if one_step_window else None,
        "per_arm_median_spread": round(spread, 4) if spread is not None else None,
        "median_within_arm_sd": round(within, 4) if within is not None else None,
        "controls": {"positive_control_fires": control_ok, "readout_exists": readout_ok},
        "verdict": verdict,
        "runs_detail": runs,
    }
    if args.write:
        OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for name, v in sorted(summary.items()):
        print(f"[x166] {name}: fused {v['fused']}/{v['runs']} g_last {v['g_last_median']} sd {v['g_last_sd']} "
              f"growth/step {v['growth_per_step_median']}")
    print(f"[x166] window {one_step_window} spread {spread} within {within}")
    print(f"[x166] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
