"""x91_analyse.py — is the memory at the band's shoulders lineage memory or regional resemblance?

Criteria: `reports/2026-11-02-x91-specificity-plan.md`. Uses the stored artifacts of X87 (0.025 / 0.030 / 0.035) and X88 (0.040 / 0.045):
for every lag-1 division, correlate the ancestor's peak area with the daughter's, then correlate the area of the daughter's nearest
non-ancestor at her first appearance with the same daughter. The gap between the two is the readout.

Run:
    python scripts/x91_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x91_lineage_specificity.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build, stranger_peak  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from field_metrics import cell_files, partial_spearman  # noqa: E402

CELLS = {
    # 02.11 fix: the lattice cells are twenty worlds, eight from X85 (seeds 191-198) and twelve from X87 (221-232). Globbing a
    # single prefix silently used twelve and the reports said twenty; both prefixes are pooled here.
    "f025": (("x85", "x87"), 0.025),
    "f030": (("x85", "x87"), 0.030),
    "f035": (("x85", "x87"), 0.035),
    "f040": (("x88",), 0.040),
    "f045": (("x88",), 0.045),
}
CONTROL_BAND = (0.35, 0.55)   # X73 at 0.035 with the same code
MIN_EVENTS = 100
STRANGER_COVERAGE = 0.80
GAP_RESOLUTION = 0.15
GAP_REGIONAL = 0.05


def cell_stats(series, flow: float) -> dict:
    parent_a, parent_d, stranger_a, stranger_d = [], [], [], []
    worlds, events, with_stranger = 0, 0, 0
    for path in cell_files(series, flow):
        w = build(path)
        worlds += 1
        for uid in w["peaks"]:
            anc = ancestors(uid, w["parent"], 1)
            if anc is None or anc not in w["peaks"]:
                continue
            events += 1
            parent_a.append(w["peaks"][anc])
            parent_d.append(w["peaks"][uid])
            s = stranger_peak(w, uid)
            if s is not None:
                with_stranger += 1
                stranger_a.append(s)
                stranger_d.append(w["peaks"][uid])

    rho_parent = spearman(parent_a, parent_d)
    rho_stranger = spearman(stranger_a, stranger_d)
    gap = round(rho_parent - rho_stranger, 3) if rho_parent is not None and rho_stranger is not None else None
    return {"flow": flow, "series": series, "worlds": worlds, "events": events,
            "stranger_coverage": round(with_stranger / events, 3) if events else None,
            "rho_parent": round(rho_parent, 3) if rho_parent is not None else None,
            "rho_stranger": round(rho_stranger, 3) if rho_stranger is not None else None,
            "gap": gap,
            "mean_area_parent": round(st.mean(parent_a), 1) if parent_a else None,
            "mean_area_daughter": round(st.mean(parent_d), 1) if parent_d else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X91 lineage specificity")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x91_lineage_specificity", "experiment": "X91",
           "command": "python scripts/x91_analyse.py --write",
           "prereg": "reports/2026-11-02-x91-specificity-plan.md",
           "method": "Spearman(ancestor area, daughter area) against Spearman(nearest non-ancestor area, daughter area); the gap is "
                     "the readout. Same code as X73 (x73_depth.stranger_peak).",
           "control_band": list(CONTROL_BAND), "resolution": GAP_RESOLUTION, "cells": {}}
    for name, (series, flow) in CELLS.items():
        res["cells"][name] = cell_stats(series, flow)
    c = res["cells"]

    control = (c["f035"]["rho_parent"] is not None and CONTROL_BAND[0] <= c["f035"]["rho_parent"] <= CONTROL_BAND[1]
               and c["f035"]["gap"] is not None and c["f035"]["gap"] > 0)
    res["positive_control"] = {"fires": bool(control), "f035_rho_parent": c["f035"]["rho_parent"],
                               "f035_gap": c["f035"]["gap"]}

    void = [k for k, v in c.items()
            if (v["events"] or 0) < MIN_EVENTS or (v["stranger_coverage"] or 0) < STRANGER_COVERAGE]
    lineage = [k for k, v in c.items() if v["gap"] is not None and v["gap"] >= GAP_RESOLUTION]
    shoulders = [k for k in ("f025", "f040") if c[k]["gap"] is not None and c[k]["gap"] >= GAP_RESOLUTION]
    regional = [k for k, v in c.items() if v["gap"] is not None and v["gap"] < GAP_REGIONAL]
    regional_shoulder = [k for k in ("f025", "f040") if c[k]["gap"] is not None and c[k]["gap"] < GAP_REGIONAL]

    if void:
        verdict = f"void: underpowered cells: {void}"
    elif not control:
        verdict = "void: the F = 0.035 control does not reproduce X73's band — the implementation differs"
    elif len(lineage) >= 3 and shoulders:
        verdict = "lineage memory: the parent predicts the daughter better than the nearest non-ancestor by at least 0.15 in three cells, including a shoulder"
    elif len(regional) >= 3 and regional_shoulder:
        verdict = "regional resemblance: the gap is below 0.05 in three cells including a shoulder, so the resemblance there is a property of the place"
    else:
        verdict = "mixed"
    res["lineage_cells"] = lineage
    res["regional_cells"] = regional
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x91] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k} (F={v['flow']}): events={v['events']} cover={v['stranger_coverage']} "
              f"parent={v['rho_parent']} stranger={v['rho_stranger']} gap={v['gap']} "
              f"areas parent/daughter={v['mean_area_parent']}/{v['mean_area_daughter']}")
    print("  control:", res["positive_control"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
