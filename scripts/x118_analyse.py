"""x118_analyse.py — X118: at fixed size, does the number of daughters matter?

Exposure (area) held fixed within ±10 %, mediator (number of daughters) varied: compare survival of the many-daughter branch against the few-daughter one.
Plan: reports/2026-11-03-x118-mediator-plan.md.

    python scripts/x118_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x118_mediator.json"

CELLS = {"f030": 0.030, "f040": 0.040}
BANDS = (0.10, 0.15)
MIN_PAIRS = 120
HEREDITY_FLOOR = 0.35
AREA_RATIO_BAND = (0.95, 1.05)
MIN_DAUGHTER_DIFF = 1.0
BOOTSTRAP = 2000


def descendants(children, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
    return out


def bootstrap_ci(vals, seed=118):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(BOOTSTRAP)) for _ in range(len(vals)))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP)))
    return [round(means[lo], 4), round(means[hi], 4)]


def cell_stats(flow: float) -> dict:
    heredity = []
    per_band: dict[float, dict] = {b: {"diffs": [], "ratios": [], "ddiff": [], "only_many": 0, "only_few": 0} for b in BANDS}
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
                    area_a, area_b = w["peak"][a]["area"], w["peak"][b]["area"]
                    if not area_a or not area_b:
                        continue
                    ratio = min(area_a, area_b) / max(area_a, area_b)
                    na, nb = len(children.get(a, [])), len(children.get(b, []))
                    if na == nb:
                        continue
                    many, few = (a, b) if na > nb else (b, a)
                    alive_many = int(any(u in present for u in descendants(children, many)))
                    alive_few = int(any(u in present for u in descendants(children, few)))
                    diff = alive_many - alive_few
                    for band in BANDS:
                        if ratio >= 1.0 - band:
                            per_band[band]["diffs"].append(diff)
                            per_band[band]["ratios"].append(ratio)
                            per_band[band]["ddiff"].append(abs(na - nb))
                            if diff > 0:
                                per_band[band]["only_many"] += 1
                            elif diff < 0:
                                per_band[band]["only_few"] += 1
    used = next((b for b in BANDS if len(per_band[b]["diffs"]) >= MIN_PAIRS), BANDS[-1])
    d = per_band[used]
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "band_used": used,
        "pairs": len(d["diffs"]),
        "area_ratio_mean": round(st.mean(d["ratios"]), 4) if d["ratios"] else None,
        "daughter_diff_mean": round(st.mean(d["ddiff"]), 3) if d["ddiff"] else None,
        "survival_diff_mean": round(st.mean(d["diffs"]), 4) if d["diffs"] else None,
        "survival_diff_ci": bootstrap_ci(d["diffs"]),
        "only_many": d["only_many"], "only_few": d["only_few"],
        "pairs_by_band": {str(b): len(per_band[b]["diffs"]) for b in BANDS},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X118 mediator at fixed size")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: only {c['pairs']} pairs even at ±15 %")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["area_ratio_mean"] is None or not (AREA_RATIO_BAND[0] <= c["area_ratio_mean"] <= AREA_RATIO_BAND[1]):
            bad.append(f"{tag}: area ratio {c['area_ratio_mean']} outside {AREA_RATIO_BAND}")
        if c["daughter_diff_mean"] is None or c["daughter_diff_mean"] < MIN_DAUGHTER_DIFF:
            bad.append(f"{tag}: daughter difference {c['daughter_diff_mean']} below {MIN_DAUGHTER_DIFF}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        matters = all(c["survival_diff_ci"] and c["survival_diff_ci"][0] > 0 for c in (lat, maz))
        nothing = all(c["survival_diff_ci"] and c["survival_diff_ci"][0] <= 0 <= c["survival_diff_ci"][1] for c in (lat, maz))
        if matters:
            verdict = (f"the number of daughters matters independently of size: at a fixed area ratio the many-daughter branch survives "
                       f"{lat['survival_diff_mean']:.3f} more often (CI {lat['survival_diff_ci']}) in the lattice and {maz['survival_diff_mean']:.3f} "
                       f"in the maze (CI {maz['survival_diff_ci']})")
        elif nothing:
            verdict = (f"the number of daughters adds nothing beyond size: at a fixed area ratio the difference is {lat['survival_diff_mean']:.3f} "
                       f"(CI {lat['survival_diff_ci']}) and {maz['survival_diff_mean']:.3f} (CI {maz['survival_diff_ci']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['survival_diff_mean']:.3f} (CI {lat['survival_diff_ci']}), maze {maz['survival_diff_mean']:.3f} "
                       f"(CI {maz['survival_diff_ci']})")
        verdict += (f"; area ratio {lat['area_ratio_mean']} / {maz['area_ratio_mean']}, daughter difference "
                    f"{lat['daughter_diff_mean']} / {maz['daughter_diff_mean']}, pairs {lat['pairs']} / {maz['pairs']}")

    res = {
        "kind": "l1_field_x118_mediator",
        "experiment": "X118",
        "command": "python scripts/x118_analyse.py --write",
        "prereg": "reports/2026-11-03-x118-mediator-plan.md",
        "roles": "area = exposure (held fixed within the band), number of daughters = mediator (varied)",
        "readout": "paired survival difference between the many-daughter and few-daughter branch at a fixed area ratio",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x118] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} (bands {c['pairs_by_band']}) heredity={c['rho_heredity']} "
              f"area ratio={c['area_ratio_mean']} daughter diff={c['daughter_diff_mean']} "
              f"survival diff={c['survival_diff_mean']} (CI {c['survival_diff_ci']}) onlyMany/onlyFew={c['only_many']}/{c['only_few']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
