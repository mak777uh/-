"""x112_analyse.py — X112: the ladder and the specificity at three excursion cuts, on the same genealogies and frames.

X108's dense series saves a field at every logged step, so a structure's area at 0.15 / 0.20 / 0.25 can be measured on the frame where its
genealogy was built. Identity comes from the 0.20 run; only the size definition changes.

Plan: reports/2026-11-02-x112-cuts-dense-plan.md.

    python scripts/x112_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x108_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x112_cuts_dense.json"

CELLS = {"f030": 0.030, "f040": 0.040}
CUTS = (0.15, 0.20, 0.25)
GRID = 96
X108_REF = {0.030: 0.548, 0.040: 0.480}
CONTROL_BAND = 0.02
MIN_PAIRS = 300


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


def torus(a, b):
    d = abs(a - b) % GRID
    return min(d, GRID - d)


def world(path: Path) -> dict:
    """Peak frame, centroid and area per uid from the component log, plus the genealogy in child -> parent order.

    `uid_outcomes` carries no peak frame and no centroid, so the frame is taken from the component log (x102's `world_data`), which
    is also the frame the logger recorded its own area on.
    """
    w = world_data(path)
    peak = {uid: {"frame": int(info["step"]), "cy": info["cy"], "cx": info["cx"], "area": float(info["area"])}
            for uid, info in w["peak"].items()}
    return {"peak": peak, "parent": w["parent"]}


def _component(field: np.ndarray, start: tuple[int, int], cut: float) -> set[tuple[int, int]]:
    """Periodic 4-connected component of `v > cut` that contains `start`, or an empty set."""
    if field[start[0], start[1]] <= cut:
        return set()
    seen = {start}
    stack = [start]
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = (y + dy) % GRID, (x + dx) % GRID
            if field[ny, nx] > cut and (ny, nx) not in seen:
                seen.add((ny, nx))
                stack.append((ny, nx))
    return seen


def area_at(field: np.ndarray, cy: float, cx: float, cut: float) -> float | None:
    """Area of the component of `v > cut` that carries this structure — 4-connectivity, **periodic**, like the logger.

    Three corrections were needed to reproduce the logger's own areas at 0.20. The centroid is area-weighted and can land in a hole of a
    ring- or crescent-shaped structure (uid 1 sits at v = 0.035 while its ring peaks at 0.38), so the anchor is the brightest pixel of
    the structure found at a **low** cut of 0.10, not the brightest pixel near the centroid; and `scipy.ndimage.label` does not wrap,
    while `field_track.label` does, so a structure crossing the boundary was being split.
    """
    yi, xi = int(round(cy)) % GRID, int(round(cx)) % GRID
    low = _component(field, (yi, xi), 0.10)
    if not low:
        return None
    anchor = max(low, key=lambda p: float(field[p[0], p[1]]))
    if float(field[anchor[0], anchor[1]]) <= cut:
        return None
    comp = _component(field, anchor, cut)
    return float(len(comp)) if comp else None


def nearest_stranger(parent: dict[int, int], peak: dict, child: int, frame: int) -> int | None:
    """X102's rule: nearest non-ancestor at the daughter's frame, by centroid."""
    if child not in peak or peak[child].get("cx") is None:
        return None
    ban = {child}
    cur = child
    for _ in range(6):
        nxt = parent.get(cur)
        if nxt is None or nxt in ban:
            break
        ban.add(nxt)
        cur = nxt
    cy, cx = float(peak[child]["cy"]), float(peak[child]["cx"])
    best, best_uid = None, None
    for uid, info in peak.items():
        if uid in ban or info.get("cx") is None or info["frame"] != frame:
            continue
        d = math.hypot(torus(float(info["cy"]), cy), torus(float(info["cx"]), cx))
        if best is None or d < best:
            best, best_uid = d, uid
    return best_uid


def cell_stats(flow: float) -> dict:
    caches: dict[tuple[str, int], np.ndarray] = {}
    out = {}
    for cut in CUTS:
        pa, ca, sa, pairs, covered = [], [], [], 0, 0
        for path in cell_files(("x108",), flow, filename=""):
            w = world(path)
            for child, par in w["parent"].items():
                pairs += 1
                if child not in w["peak"] or par not in w["peak"]:
                    continue
                cp, pp = w["peak"][child], w["peak"][par]
                if cp.get("cx") is None or pp.get("cx") is None:
                    continue
                def frame_of(step: int):
                    key = (path.name, int(step))
                    if key not in caches:
                        f = FIELDS / f"{path.stem}_t{int(step)}.npy"
                        caches[key] = np.load(f) if f.is_file() else None
                    return caches[key]

                fc, fp = frame_of(cp["frame"]), frame_of(pp["frame"])
                if fc is None or fp is None:
                    continue
                # each uid is measured at ITS OWN peak frame — the frame the logger recorded that uid on
                ac = area_at(fc, float(cp["cy"]), float(cp["cx"]), cut)
                ap = area_at(fp, float(pp["cy"]), float(pp["cx"]), cut)
                if ac is None or ap is None:
                    continue
                s = nearest_stranger(w["parent"], w["peak"], child, int(cp["frame"]))
                as_ = area_at(fc, float(w["peak"][s]["cy"]), float(w["peak"][s]["cx"]), cut) if s is not None else None
                pa.append(ap)
                ca.append(ac)
                if as_ is not None:
                    sa.append((as_, ac))
                    covered += 1
        rho = spearman(pa, ca)
        gap = None
        if sa:
            rho_s = spearman([x[0] for x in sa], [x[1] for x in sa])
            if rho is not None and rho_s is not None:
                gap = round(rho - rho_s, 3)
        out[f"{cut}"] = {"pairs": pairs, "used": len(pa), "coverage": round(len(pa) / pairs, 3) if pairs else None,
                         "rho1": round(rho, 3) if rho is not None else None,
                         "gap": gap,
                         "median_area": float(np.median(pa)) if pa else None}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X112 three cuts on the dense series")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}

    bad = []
    for tag, flow in CELLS.items():
        c = cells[tag]
        if (c["0.2"]["used"] if "0.2" in c else 0) < MIN_PAIRS:
            bad.append(f"{tag}: fewer than {MIN_PAIRS} pairs at 0.20")
        for cut in CUTS:
            key = f"{cut}"
            if c[key]["used"] < MIN_PAIRS:
                bad.append(f"{tag}@{cut}: {c[key]['used']} pairs")
        ref = c["0.2"]["rho1"]
        if ref is None or abs(ref - X108_REF[flow]) > CONTROL_BAND:
            bad.append(f"{tag}: the 0.20 recomputation gives {ref}, misses X108's {X108_REF[flow]} by more than {CONTROL_BAND}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        levels = {tag: [cells[tag][f"{c}"]["rho1"] for c in CUTS] for tag in CELLS}
        gaps = {tag: [cells[tag][f"{c}"]["gap"] for c in CUTS] for tag in CELLS}
        level_span = {t: round(max(v) - min(v), 3) for t, v in levels.items()}
        gap_span = {t: round(max(v) - min(v), 3) for t, v in gaps.items() if None not in v}
        level_bound = any(s >= 0.10 for s in level_span.values())
        level_stable = all(s <= 0.05 for s in level_span.values())
        gap_bound = any(s >= 0.15 for s in gap_span.values())
        gap_stable = bool(gap_span) and all(s <= 0.10 for s in gap_span.values())
        parts = []
        parts.append("the level is cut-bound" if level_bound else ("the level is cut-stable" if level_stable
                     else "the level moves less than 0.10"))
        parts.append(f"(spans {level_span})")
        if gap_span:
            parts.append("the gap is cut-bound" if gap_bound else ("the gap is cut-stable" if gap_stable
                         else "the gap moves less than 0.15"))
            parts.append(f"(spans {gap_span})")
        else:
            parts.append("the gap could not be measured at every cut")
        verdict = "; ".join(parts)

    res = {
        "kind": "l1_field_x112_cuts_dense",
        "experiment": "X112",
        "command": "python scripts/x112_analyse.py --write",
        "prereg": "reports/2026-11-02-x112-cuts-dense-plan.md",
        "readout": "component area at 0.15/0.20/0.25 measured on the uid's own peak frame; rho1 and the parent-versus-stranger gap",
        "cuts": list(CUTS),
        "reference_x108": {str(k): v for k, v in X108_REF.items()},
        "control_band": CONTROL_BAND,
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x112] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: " + " | ".join(f"{cut}: rho1={c[str(cut)]['rho1']} gap={c[str(cut)]['gap']} "
                                        f"used={c[str(cut)]['used']} med={c[str(cut)]['median_area']}" for cut in CUTS))
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
