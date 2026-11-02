"""x117_analyse.py — X117: match on area as well as on daughters. Does any survival advantage remain?

Plan: reports/2026-11-03-x117-area-matched-plan.md.

    python scripts/x117_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x117_area_matched.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X116_MATCHED = {0.030: 0.1248, 0.040: 0.0444}
TOL = 0.05
MIN_MATCHED = 150
BANDS = (0.10, 0.20)        # area tolerance: 10 % first, widen to 20 % if a cell is short
HEREDITY_FLOOR = 0.35
BOOTSTRAP = 2000


def descendants(children, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
    return out


def bootstrap_ci(vals, seed=117):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 4), round(means[int(0.975 * BOOTSTRAP)], 4)]


def cell_stats(flow: float) -> dict:
    heredity = []
    daughters_only = []          # equal n
    area_ratio_full = []
    pairs_by_band: dict[float, list[int]] = {b: [] for b in BANDS}
    counts_by_band: dict[float, list[int]] = {b: [0, 0] for b in BANDS}
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        last_step = max(w["per_step"]) if w["per_step"] else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    if len(children.get(big, [])) != len(children.get(small, [])):
                        continue
                    area_big = w["peak"][big]["area"]
                    area_small = w["peak"][small]["area"]
                    ratio = area_big / area_small if area_small else 1.0
                    area_ratio_full.append(ratio)
                    diff = int(any(u in present for u in descendants(children, big))) - \
                        int(any(u in present for u in descendants(children, small)))
                    daughters_only.append(diff)
                    for band in BANDS:
                        if abs(area_big - area_small) / max(area_big, 1e-9) <= band:
                            pairs_by_band[band].append(diff)
                            if diff > 0:
                                counts_by_band[band][0] += 1
                            elif diff < 0:
                                counts_by_band[band][1] += 1
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    chosen = next((b for b in BANDS if len(pairs_by_band[b]) >= MIN_MATCHED), BANDS[-1])
    vals = pairs_by_band[chosen]
    return {
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "pairs_daughters_only": len(daughters_only),
        "diff_daughters_only": round(st.mean(daughters_only), 4) if daughters_only else None,
        "mean_area_ratio_full": round(st.mean([r for r in area_ratio_full if r > 1.0]), 3) if area_ratio_full else None,
        "band_used": chosen,
        "pairs_matched": len(vals),
        "diff_matched": round(st.mean(vals), 4) if vals else None,
        "diff_matched_ci": bootstrap_ci(vals),
        "only_bigger": counts_by_band[chosen][0], "only_smaller": counts_by_band[chosen][1],
        "pairs_by_band": {str(b): len(v) for b, v in pairs_by_band.items()},
        "x116_reference": X116_MATCHED[flow],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X117 area-matched survival")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["pairs_matched"] < MIN_MATCHED:
            bad.append(f"{tag}: only {c['pairs_matched']} matched pairs even at ±20 %")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        ref = c["x116_reference"]
        if c["diff_daughters_only"] is None or abs(c["diff_daughters_only"] - ref) > TOL * abs(ref):
            bad.append(f"{tag}: equal-daughters contrast {c['diff_daughters_only']} misses X116's {ref}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        holds = all(c["diff_matched_ci"] and c["diff_matched_ci"][0] > 0 for c in (lat, maz))
        gone = all(c["diff_matched_ci"] and c["diff_matched_ci"][0] <= 0 <= c["diff_matched_ci"][1] for c in (lat, maz))
        if holds:
            verdict = (f"a lineage effect remains: with branches matched on daughters and area the larger sister still survives "
                       f"{lat['diff_matched']:.3f} more often (CI {lat['diff_matched_ci']}) in the lattice and {maz['diff_matched']:.3f} "
                       f"in the maze (CI {maz['diff_matched_ci']})")
        elif gone:
            verdict = (f"the survival advantage is fully arithmetic: matched on daughters and area the difference is {lat['diff_matched']:.3f} "
                       f"(CI {lat['diff_matched_ci']}) and {maz['diff_matched']:.3f} (CI {maz['diff_matched_ci']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['diff_matched']:.3f} (CI {lat['diff_matched_ci']}), maze {maz['diff_matched']:.3f} "
                       f"(CI {maz['diff_matched_ci']})")
        verdict += (f"; matched pairs {lat['pairs_matched']} / {maz['pairs_matched']} at ±{int(lat['band_used'] * 100)} %, "
                    f"mean area ratio {lat['mean_area_ratio_full']} before matching")

    res = {
        "kind": "l1_field_x117_area_matched",
        "experiment": "X117",
        "command": "python scripts/x117_analyse.py --write",
        "prereg": "reports/2026-11-03-x117-area-matched-plan.md",
        "readout": "survival difference among sister pairs matched on the number of daughters and on area",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x117] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: daughters-only={c['pairs_daughters_only']} ({c['diff_daughters_only']}) matched={c['pairs_matched']} "
              f"diff={c['diff_matched']} (CI {c['diff_matched_ci']}) band=±{int(c['band_used'] * 100)} % "
              f"area ratio {c['mean_area_ratio_full']} onlyBig/onlySmall={c['only_bigger']}/{c['only_smaller']} "
              f"bands={c['pairs_by_band']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
