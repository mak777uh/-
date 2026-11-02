"""x98_analyse.py — is the angular map a property of the world or of the excursion cut?

Criteria: `reports/2026-11-02-x98-threshold-plan.md`. Recomputes `q'` and the symmetry `s` from the stored fields of X85/X87/X88 at
four excursion thresholds (0.15 / 0.20 / 0.25 / 0.30) and asks whether the ordering of the cells and the absence of q' = 11 survive.

Run:
    python scripts/x98_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x98_threshold.json"

sys.path.insert(0, str(ROOT / "scripts"))
from field_metrics import angular, cell_files  # noqa: E402

FIELDS = {L1 / "_x85_fields": "x85", L1 / "_x87_fields": "x87", L1 / "_x88_fields": "x88"}
CELLS = {"f025": (("x85", "x87"), 0.025), "f030": (("x85", "x87"), 0.030),
         "f035": (("x85", "x87"), 0.035), "f040": (("x88",), 0.040)}
THRESHOLDS = (0.15, 0.20, 0.25, 0.30)
CONTROL_CUT = 0.20
CONTROL_TOL = 0.01
COMMITTED = {"f025": 0.385, "f030": 0.679, "f035": 0.837, "f040": 0.935}   # X86/X87/X88 aggregates at 0.20
ORDER_GAP = 0.05


def field_path(run_json: Path) -> Path | None:
    stem = run_json.stem
    for base in FIELDS:
        if base.name.startswith("_" + stem.split("_")[0]):
            f = base / f"{stem}_t6000.npy"
            if f.is_file():
                return f
    return None


def mask_angular(v: np.ndarray, threshold: float) -> dict:
    """Angular readout on the excursion set: zeros outside the mask, the field inside it."""
    m = v > threshold
    if m.mean() < 0.01 or m.mean() > 0.99:
        return {"q_axis": None, "symmetry": None, "unreadable": True, "fill": round(float(m.mean()), 3)}
    masked = np.where(m, v, 0.0)
    got = angular(masked)
    got["unreadable"] = got["symmetry"] is None
    got["fill"] = round(float(m.mean()), 3)
    return got


def cell_stats(series, flow: float) -> dict:
    files = [field_path(p) for p in cell_files(series, flow)]
    files = [f for f in files if f is not None]
    out = {"flow": flow, "fields": len(files), "by_threshold": {}}
    for thr in THRESHOLDS:
        syms, qs, unread = [], [], 0
        for f in files:
            got = mask_angular(np.load(f), thr)
            if got.get("unreadable"):
                unread += 1
                continue
            syms.append(got["symmetry"])
            if got["q_axis"]:
                qs.append(got["q_axis"])
        out["by_threshold"][f"{thr:.2f}"] = {
            "symmetry_median": round(st.median(syms), 3) if syms else None,
            "symmetry_iqr": [round(st.quantiles(syms, n=4)[0], 3), round(st.quantiles(syms, n=4)[2], 3)] if len(syms) >= 4 else None,
            "q_set": sorted(set(qs)),
            "has_q11": 11 in qs,
            "unreadable": unread,
        }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X98 threshold robustness")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x98_threshold", "experiment": "X98",
           "command": "python scripts/x98_analyse.py --write",
           "prereg": "reports/2026-11-02-x98-threshold-plan.md",
           "thresholds": list(THRESHOLDS), "control": {"cut": CONTROL_CUT, "tol": CONTROL_TOL, "committed": COMMITTED},
           "cells": {}}
    for name, (series, flow) in CELLS.items():
        res["cells"][name] = cell_stats(series, flow)
    c = res["cells"]

    control_ok = True
    control_detail = {}
    for name in CELLS:
        got = c[name]["by_threshold"][f"{CONTROL_CUT:.2f}"]["symmetry_median"]
        want = COMMITTED[name]
        ok = got is not None and abs(got - want) <= CONTROL_TOL
        control_detail[name] = {"recomputed": got, "committed": want, "ok": ok}
        control_ok = control_ok and ok
    res["positive_control"] = {"fires": bool(control_ok), "detail": control_detail}

    unreadable = {name: c[name]["by_threshold"][f"{CONTROL_CUT:.2f}"]["unreadable"] for name in CELLS}
    too_many_unreadable = any(v > 0.05 * c[name]["fields"] for name, v in unreadable.items())

    checks = {}
    for thr in THRESHOLDS:
        key = f"{thr:.2f}"
        meds = [c[n]["by_threshold"][key]["symmetry_median"] for n in ("f025", "f030", "f035", "f040")]
        q11 = any(c[n]["by_threshold"][key]["has_q11"] for n in CELLS)
        ordered = all(m is not None for m in meds) and all(meds[i] < meds[i + 1] for i in range(3))
        gaps = [round(meds[i + 1] - meds[i], 3) if meds[i] is not None and meds[i + 1] is not None else None for i in range(3)]
        gaps_ok = all(g is not None and g > ORDER_GAP for g in gaps)
        checks[key] = {"medians": meds, "ordered": ordered, "gaps": gaps, "gaps_ok": gaps_ok, "q11": q11}
    res["checks"] = checks

    if not control_ok:
        verdict = "void: the 0.20 cut does not reproduce the committed medians within 0.01"
    elif too_many_unreadable:
        verdict = "void: more than 5% of fields are unreadable at the 0.20 cut"
    elif all(v["ordered"] and not v["q11"] for v in checks.values()) and all(v["gaps_ok"] for v in checks.values()):
        verdict = "robust: at every cut the medians are ordered, every gap exceeds 0.05, and q' = 11 never appears"
    elif all(v["ordered"] and not v["q11"] for v in checks.values()):
        verdict = "mixed: the ordering and the absence of q' = 11 hold at every cut, but a gap falls below 0.05 somewhere"
    else:
        bad = [k for k, v in checks.items() if not v["ordered"] or v["q11"]]
        verdict = f"cut-dependent: the map fails at cuts {bad}"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x98] written: {OUT.name}")

    for name, v in c.items():
        line = [f"{k}: s={v['by_threshold'][k]['symmetry_median']} q={v['by_threshold'][k]['q_set']}" for k in v["by_threshold"]]
        print(f"  {name} ({v['flow']}): " + " | ".join(line))
    print("  control:", res["positive_control"]["fires"], {k: x["ok"] for k, x in control_detail.items()})
    print("  checks:", {k: (v["ordered"], v["gaps_ok"], v["q11"]) for k, v in checks.items()})
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
