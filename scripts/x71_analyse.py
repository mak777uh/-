"""x71_analyse.py — is the selected wavelength single-valued across worlds, or do two branches coexist?

Reads `morphogenesis/experiments/L1_field/x71_f<F>_<arm>_s<seed>.json` and the saved fields in `_x71_fields/`, and answers
the question preregistered in `reports/2026-11-01-x71-multistability-plan.md`:

1. does the peak position move monotonically with the inflow (positive control)?
2. inside one inflow cell, do the worlds share one peak position, or split into two clusters wider than the instrument?
3. does any single run keep two modes with shares both >= 0.2?

The spectrum comes from `x60_analyse.structure_factor`, the same implementation the rest of the line uses — a second
implementation would be a second definition.

Run:
    python scripts/x71_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x71_multistability.json"
FIELDS = L1 / "_x71_fields"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile, drop_small, beta0, euler  # noqa: E402

THRESHOLD = 0.2
MIN_CELLS = 5
GRID = 96
# q из `radial_profile` считается в циклах на ящик (целый радиальный индекс), то есть ровно в «бинах» Фурье:
# один бин = 1 цикл/ящик = 1/96 цикл/клетка. Длина волны в клетках = GRID/q.
BIN = 1.0
SPLIT_BINS = 3.0          # a split must be wider than the instrument (preregistered)
SECOND_MODE_SHARE = 0.2   # "two modes" means both carry at least a fifth of the power
FLOWS = {"f025": 0.025, "f030": 0.030, "f035": 0.035, "f040": 0.040, "f045": 0.045,
         "f050": 0.050, "f055": 0.055}
ARMS = ("pattern", "homog")


def spectrum_stats(v: np.ndarray) -> dict:
    prof = radial_profile(v)
    if not prof:
        return {"q_peak": None, "share_peak": None, "share_second": None, "bins": 0}
    q = np.array([float(k) for k in sorted(prof)], dtype=float)
    s = np.array([prof[int(k)] for k in sorted(prof)], dtype=float)
    total = float(s.sum())
    if total <= 0:
        return {"q_peak": None, "share_peak": None, "share_second": None, "bins": int(len(s))}
    i_peak = int(np.argmax(s))
    share_peak = float(s[i_peak] / total)
    far = np.abs(np.arange(len(s)) - i_peak) >= SPLIT_BINS
    candidates = np.where(far)[0]
    second = float(s[candidates].max() / total) if len(candidates) else 0.0
    return {"q_peak": float(q[i_peak]), "share_peak": round(share_peak, 3),
            "share_second": round(second, 3), "bins": int(len(s))}


def world_row(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    tag = path.stem
    f = FIELDS / f"{tag}_t6000.npy"
    row = {"file": path.name, "field": f.name, "ok": f.is_file()}
    if not f.is_file():
        return row
    v = np.load(f)
    row.update(spectrum_stats(v))
    mask = drop_small(v >= THRESHOLD, MIN_CELLS)
    row["b0"] = beta0(mask)
    row["b1"] = beta0(mask) - euler(mask)
    return row


def clusters(values: list[float]) -> list[dict]:
    """Split sorted peak positions at gaps wider than SPLIT_BINS bins; clusters with >= 2 worlds count."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return []
    out = [[vals[0]]]
    for v in vals[1:]:
        if v - out[-1][-1] >= SPLIT_BINS * BIN:
            out.append([v])
        else:
            out[-1].append(v)
    return [{"n": len(c), "centre": round(st.mean(c), 4), "values": [round(x, 4) for x in c]} for c in out]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X71 multistability scan")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x71_multistability", "experiment": "X71",
           "command": "python scripts/x71_analyse.py --write",
           "prereg": "reports/2026-11-01-x71-multistability-plan.md",
           "split_bins": SPLIT_BINS, "second_mode_share": SECOND_MODE_SHARE,
           "bin_width": BIN, "cells": {}}

    for arm in ARMS:
        for flow, F in FLOWS.items():
            rows = [world_row(p) for p in sorted(L1.glob(f"x71_{flow}_{arm}_s*.json"))]
            rows = [r for r in rows if r.get("ok")]
            qs = [r["q_peak"] for r in rows if r.get("q_peak") is not None]
            cl = clusters(qs)
            two_mode = [r["file"] for r in rows
                        if (r.get("share_second") or 0) >= SECOND_MODE_SHARE and (r.get("share_peak") or 0) >= SECOND_MODE_SHARE]
            res["cells"][f"{flow}_{arm}"] = {
                "flow": F, "arm": arm, "worlds": len(rows),
                "q_peak": [round(x, 2) for x in qs],
                "wavelength_cells": [round(GRID / x, 2) for x in qs],
                "spread_bins": round((max(qs) - min(qs)) / BIN, 1) if len(qs) > 1 else 0.0,
                "clusters": cl,
                "split": len([c for c in cl if c["n"] >= 2]) >= 2,
                "two_mode_runs": two_mode,
                "b0_median": st.median([r["b0"] for r in rows]) if rows else None,
                "b1_median": st.median([r["b1"] for r in rows]) if rows else None,
            }

    # positive control: the peak position must move monotonically with the inflow, per arm
    control = {}
    for arm in ARMS:
        pts = [(res["cells"][f"{flow}_{arm}"]["flow"],
                st.median([r for r in res["cells"][f"{flow}_{arm}"]["q_peak"]] or [0]))
               for flow in FLOWS]
        pts = [(f, q) for f, q in pts if q]
        mono_down = all(pts[i][1] >= pts[i + 1][1] for i in range(len(pts) - 1))
        span_bins = round((max(q for _, q in pts) - min(q for _, q in pts)) / BIN, 1) if len(pts) > 1 else 0.0
        # План (поправка 17:55) требует от контроля ОТКЛИК, а не монотонность: монотонность печатается как факт.
        control[arm] = {"points": [[round(f, 3), round(q, 4)] for f, q in pts],
                        "monotone_non_increasing": mono_down, "span_bins": span_bins,
                        "fires": span_bins >= SPLIT_BINS}
    res["positive_control"] = control

    splits = [k for k, c in res["cells"].items() if c["split"]]
    two_modes = [k for k, c in res["cells"].items() if c["two_mode_runs"]]
    fires = any(c["fires"] for c in control.values())
    if not fires:
        verdict = "insensitive: the peak position does not move with the inflow"
    elif splits or two_modes:
        verdict = "multistable: two branches visible at some inflow"
    else:
        verdict = "one branch everywhere at this resolution"
    res["verdict"] = verdict
    res["split_cells"] = splits
    res["two_mode_cells"] = two_modes

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x71] written: {OUT.name}")

    for arm, c in control.items():
        print("  control %-8s monotone=%s span_bins=%.1f fires=%s points=%s" % (
            arm, c["monotone_non_increasing"], c["span_bins"], c["fires"], c["points"]))
    for key, cell in res["cells"].items():
        print("  %-14s worlds=%d q=%s spread=%.1f bins split=%s two_mode=%d  b0=%s b1=%s" % (
            key, cell["worlds"], cell["q_peak"], cell["spread_bins"], cell["split"],
            len(cell["two_mode_runs"]), cell["b0_median"], cell["b1_median"]))
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
