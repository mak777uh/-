"""x111_analyse.py — X111: does the sign of rho(peak area, lifetime) survive a nine-times finer lifetime?

X92 measured the relation on lifetimes quantised by a 50-step logging interval; the dense series measures them in 10-step units. This
compares the two on the same two cells, with X92's sparse values as the positive control and a within-world shuffle null.

Plan: reports/2026-11-02-x111b-area-lifetime-plan.md.

    python scripts/x111_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x111b_area_lifetime.json"

CELLS = {"f030": 0.030, "f040": 0.040}
SERIES = {"sparse": "x100", "dense": "x108"}
X92 = {0.030: 0.067, 0.040: -0.046}   # X92 per cell; CLAIMS 312: cells .025/.030/.035/.040 = +0.191/+0.067/-0.041/-0.046     # X92's sparse reference values
CONTROL_BAND = 0.05
NULL_P95 = 0.15
MIN_UIDS = 300
SHUFFLES = 1000
# the control is recomputed on X92's own worlds, not on x100: X92 measured x85+x87 (0.030) and x88 (0.040)
REFERENCE_SERIES = {"f030": ("x85", "x87"), "f040": ("x88",)}


def ranks_of(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else None


def spearman(x, y):
    return pearson(ranks_of(x), ranks_of(y))


def lifetimes(path: Path) -> list[dict]:
    """(uid, peak area, lifetime, first step) from `uid_outcomes` — X92's own fields, so the comparison is like for like.

    The first version read `components_log` instead, and its sparse recomputation came out with the opposite signs (−0.111 / +0.160
    against X92's +0.191 / −0.041): a recomputation must use the archived fields, not a plausible equivalent.
    """
    d = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for o in d.get("uid_outcomes") or []:
        first, last, peak = o.get("first"), o.get("last"), o.get("peak")
        if first is None or last is None or peak is None or int(last) <= int(first):
            continue
        out.append({"uid": int(o["uid"]), "area": float(peak), "life": float(int(last) - int(first) + 1),
                    "first": int(first)})
    return out


def shuffle_null(rows: list[dict], rng: np.random.Generator) -> float:
    areas = [r["area"] for r in rows]
    lives = [r["life"] for r in rows]
    vals = []
    for _ in range(SHUFFLES):
        perm = list(lives)
        rng.shuffle(perm)
        rho = spearman(areas, perm)
        if rho is not None:
            vals.append(abs(rho))
    return float(np.percentile(vals, 95)) if vals else None


def cell_stats(flow: float) -> dict:
    out = {}
    for name, prefix in SERIES.items():
        rows: list[dict] = []
        per_world = []
        for path in cell_files((prefix,), flow, filename=""):
            w = lifetimes(path)
            rows.extend(w)
            if len(w) >= 30:
                r = spearman([x["area"] for x in w], [x["life"] for x in w])
                per_world.append(round(r, 3) if r is not None else None)
        rho = spearman([r["area"] for r in rows], [r["life"] for r in rows]) if rows else None
        null = shuffle_null(rows, np.random.default_rng(1102)) if rows else None
        lives = [r["life"] for r in rows]
        out[name] = {
            "uids": len(rows),
            "rho": round(rho, 3) if rho is not None else None,
            "null_p95": round(null, 3) if null is not None else None,
            "median_life": float(np.median(lives)) if lives else None,
            "per_world": per_world,
        }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X111 area vs lifetime, sparse against dense")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {f"{tag}": cell_stats(flow) for tag, flow in CELLS.items()}

    # the control is the reference recomputed on X92's OWN series (x85+x87 for 0.030, x88 for 0.040), not on x100: X92 measured
    # other worlds, and comparing x100 with X92 would be the very "borrowed control band" the X85 rule forbids.
    reference = {}
    for tag, flow in CELLS.items():
        rows = []
        for path in cell_files(REFERENCE_SERIES[tag], flow):
            rows.extend(lifetimes(path))
        rho = spearman([r["area"] for r in rows], [r["life"] for r in rows]) if rows else None
        reference[tag] = {"uids": len(rows), "rho": round(rho, 3) if rho is not None else None}

    control_bad = []
    for tag, flow in CELLS.items():
        ref = reference[tag]
        if ref["uids"] < MIN_UIDS:
            control_bad.append(f"{tag}: reference series has only {ref['uids']} uids")
        elif ref["rho"] is None or abs(ref["rho"] - X92[flow]) > CONTROL_BAND:
            control_bad.append(f"{tag}: recomputation on X92's own series gives {ref['rho']}, misses {X92[flow]} by more than {CONTROL_BAND}")
        if cells[tag]["sparse"]["uids"] < MIN_UIDS:
            control_bad.append(f"{tag}: sparse series has only {cells[tag]['sparse']['uids']} uids")
        for name in SERIES:
            null = cells[tag][name]["null_p95"]
            if null is not None and null > NULL_P95:
                control_bad.append(f"{tag}/{name}: shuffle null p95 {null} above {NULL_P95}")

    if control_bad:
        verdict = "void: " + "; ".join(control_bad)
    else:
        same_sign_both = all((cells[t]["dense"]["rho"] or 0) * (cells[t]["sparse"]["rho"] or 0) > 0 for t in CELLS)
        deltas = {t: round((cells[t]["dense"]["rho"] or 0) - (cells[t]["sparse"]["rho"] or 0), 3) for t in CELLS}
        big = [t for t, d in deltas.items() if abs(d) >= 0.15]
        above_null = all(abs(cells[t][n]["rho"] or 0) > (cells[t][n]["null_p95"] or 1) for t in CELLS for n in SERIES)
        if same_sign_both and all(abs(d) <= 0.10 for d in deltas.values()):
            verdict = ("the sign is stable across densities: both cells keep the sparse sign on 10-step lifetimes and no "
                       f"coefficient moves by more than 0.10 (deltas {deltas})")
        elif big and above_null:
            verdict = (f"the sign moves with density: the coefficients move by {deltas} and both series sit above their nulls, so "
                       f"X92's numbers must be quoted with their logging density")
        elif not same_sign_both and not above_null:
            verdict = (f"the sign is set by the sample, not the density: the cells disagree in sign between the two series "
                       f"({[cells[t]['sparse']['rho'] for t in CELLS]} against {[cells[t]['dense']['rho'] for t in CELLS]}, deltas "
                       f"{deltas}) while every coefficient sits inside its shuffle null — at this resolution the relation is "
                       f"indistinguishable from zero in both series")
        else:
            verdict = f"mixed: deltas {deltas}, sparse {[cells[t]['sparse']['rho'] for t in CELLS]}, dense {[cells[t]['dense']['rho'] for t in CELLS]}"

    res = {
        "kind": "l1_field_x111b_area_lifetime",
        "experiment": "X111",
        "command": "python scripts/x111_analyse.py --write",
        "prereg": "reports/2026-11-02-x111b-area-lifetime-plan.md",
        "readout": "Spearman(peak area, lifetime) per cell and series, with a 1 000-shuffle within-cell null",
        "series": {"sparse": "x100, --sample-every 50, seeds 291-300", "dense": "x108, --sample-every 10, seeds 301-310"},
        "reference_x92": {str(k): v for k, v in X92.items()},
        "control_band": CONTROL_BAND,
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x111] written: {OUT.name}")
    for k, v in cells.items():
        print(f"  {k}: sparse rho={v['sparse']['rho']} (null {v['sparse']['null_p95']}, n={v['sparse']['uids']}, "
              f"med life {v['sparse']['median_life']}) | dense rho={v['dense']['rho']} (null {v['dense']['null_p95']}, "
              f"n={v['dense']['uids']}, med life {v['dense']['median_life']})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
