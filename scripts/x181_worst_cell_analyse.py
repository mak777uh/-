"""x181_worst_cell_analyse.py — X181: X179's worst-heterogeneity cell (radius 3, gap 10, F = 0.030) on thirty fresh seeds.

Primary readout: the fusion share with its Wilson interval, compared against X158's 3/10 at the same cell and X176's 0/25 one
cell out. Secondary: X170's contact-time corridor, reported whenever there are contact events.

Writes morphogenesis/experiments/E09_pond/l1_field_x181_worst_cell.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x181_fields"
OUT = POND / "l1_field_x181_worst_cell.json"
SAMPLES = 21
SHARE_INTERVAL = (0.23, 0.59)
POOLED_BEFORE = (20, 49)  # X179's table for this cell


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def profile(v, p0, p1, n=SAMPLES):
    g = v.shape[0]
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = p0[0] + t * (p1[0] - p0[0])
        y = p0[1] + t * (p1[1] - p0[1])
        out.append(float(v[int(round(y)) % g, int(round(x)) % g]))
    return out


def wilson(k: int, n: int, z: float = 1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def row_of(seed: int) -> dict:
    tag = f"s{seed}"
    art = json.loads((L1 / f"x181_{tag}.compact.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    counts = [len(comps(r)) for r in series]
    fused = bool(counts) and min(counts) == 1
    out = {"seed": seed, "fused": fused, "min": min(counts) if counts else None, "final": counts[-1] if counts else None}
    if not fused:
        return out
    first_one = counts.index(1)
    if first_one == 0:
        out["error"] = "one component at the first sampled step"
        return out
    row = series[first_one - 1]
    cs = sorted(comps(row), key=lambda c: float(c["area"]) if isinstance(c, dict) else float(c[1]), reverse=True)[:2]
    if len(cs) < 2:
        out["error"] = "no second component at the contact step"
        return out
    step = int(row[0]) if isinstance(row, list) else int(row.get("step"))
    f = FIELDS / tag / f"x181_{tag}_t{step}.npy"
    if not f.exists():
        out["error"] = f"no dump at step {step}"
        return out
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    p0 = (float(cs[0]["cx"]), float(cs[0]["cy"])) if isinstance(cs[0], dict) else (float(cs[0][2]), float(cs[0][3]))
    p1 = (float(cs[1]["cx"]), float(cs[1]["cy"])) if isinstance(cs[1], dict) else (float(cs[1][2]), float(cs[1][3]))
    prof = profile(v, p0, p1)
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    peak = max(float(v.max()), 1e-9)
    out.update({"step": step, "peak": round(peak, 4), "corridor": round(min(mid), 4),
                "normalised": round(min(mid) / peak, 4)})
    return out


def main() -> int:
    rows = [row_of(s) for s in range(1211, 1241)]
    fused = sum(1 for r in rows if r["fused"])
    share = round(fused / len(rows), 4)
    ci = wilson(fused, len(rows))
    vals = [r["normalised"] for r in rows if "normalised" in r]
    corr = round(statistics.median(vals), 4) if vals else None
    sd = round(statistics.pstdev(vals), 4) if len(vals) > 1 else None

    # the six families X179 pooled into this cell, read from its own aggregate
    x179 = json.loads((POND / "l1_field_x179_crossing_table.json").read_text(encoding="utf-8"))
    cell = next((c for c in x179["two_body_cells"]
                 if c["gap"] == 10 and c["F"] == 0.03 and 2.7 <= c["radius"] <= 3.1), None)
    before = {"fused": cell["fused"], "runs": cell["runs"], "share": cell["share"]} if cell else None
    families = {k: v for k, v in (cell or {}).get("per_source", {}).items() if v["runs"] >= 3}
    pooled = ((fused + before["fused"]) / (len(rows) + before["runs"])) if before else None
    within = (before and before["runs"]) and min(f["share"] for f in families.values()) <= share <= max(
        f["share"] for f in families.values())

    peak_ok = all(0.05 <= r["peak"] <= 2.0 for r in rows if "peak" in r)
    n_contact = sum(1 for r in rows if "peak" in r)
    readout_ok = sd is not None and sd >= 0.02
    share_hit = SHARE_INTERVAL[0] <= share <= SHARE_INTERVAL[1]

    if not peak_ok:
        verdict = "NOT REPORTABLE: the peak left [0.05, 2.0] at some read."
    elif share_hit and within:
        verdict = (f"THE POOLED SHARE IS REPRODUCIBLE BY A FRESH FAMILY: {fused}/{len(rows)} = {share:.2f} "
                   f"(Wilson {ci}) lands inside the registered 0.23-0.59 and inside the range the six existing families "
                   f"already spanned ({min(f['share'] for f in families.values()):.2f}-"
                   f"{max(f['share'] for f in families.values()):.2f}), so this cell's dispersion is between-family noise and "
                   f"the pooled 0.41 (now {pooled:.2f} over {len(rows) + before['runs']} runs) stands as the cell's share.")
    elif share_hit and not within:
        verdict = (f"A FRESH FAMILY LANDS INSIDE THE POOLED INTERVAL BUT OUTSIDE THE FAMILY RANGE: {fused}/{len(rows)} = "
                   f"{share:.2f} (Wilson {ci}) against the six existing families "
                   f"({min(f['share'] for f in families.values()):.2f}-"
                   f"{max(f['share'] for f in families.values()):.2f}). The cell's share is not a property of (radius, gap, "
                   "rate) alone, and every pooled share in the table must be quoted with its family spread.")
    elif share > SHARE_INTERVAL[1]:
        verdict = (f"THE NEW FAMILY SITS ABOVE EVERY EXISTING ONE: {fused}/{len(rows)} = {share:.2f} (Wilson {ci}), above the "
                   f"registered {SHARE_INTERVAL[1]} and above the six families' maximum "
                   f"({max(f['share'] for f in families.values()):.2f}). Families are not exchangeable at this cell.")
    else:
        verdict = (f"THE NEW FAMILY SITS BELOW EVERY EXISTING ONE: {fused}/{len(rows)} = {share:.2f} (Wilson {ci}), below the "
                   f"registered {SHARE_INTERVAL[0]} and below the six families' minimum "
                   f"({min(f['share'] for f in families.values()):.2f}) — the cell is still crossable at gap 10, but by fewer "
                   "draws than the pooling suggested. Families are not exchangeable at this cell.")

    agg = {"kind": "x181_worst_cell", "flow": 0.030, "radius": 3.0, "gap": 10, "samples_per_profile": SAMPLES,
           "registered_share_interval": list(SHARE_INTERVAL),
           "observed": {"fused": fused, "runs": len(rows), "share": share, "wilson": ci,
                        "corridor_median": corr, "corridor_sd": sd, "contact": n_contact},
           "references": {"families_before": families,
                          "pooled_before": before,
                          "pooled_after": {"fused": fused + (before["fused"] if before else 0),
                                           "runs": len(rows) + (before["runs"] if before else 0),
                                           "share": round(pooled, 4) if pooled else None}},
           "controls": {"peak_in_band": peak_ok, "readout_varies": readout_ok,
                        "share_in_registered_band": share_hit, "within_family_range": within},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x181] s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor']} "
                  f"normalised {r['normalised']}")
    print(f"[x181] fused {fused}/{len(rows)} = {share} (Wilson {ci}), corridor {corr} (sd {sd}, n {n_contact})")
    print(f"[x181] pooled before {before}, after {pooled}")
    print(f"[x181] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
