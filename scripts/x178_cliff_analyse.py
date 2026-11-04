"""x178_cliff_analyse.py — X178: is the crossing a plateau or a cliff? Radius 6, gap 9, thirty seeds.

Primary readout: the fusion share with its Wilson interval, compared against X158's 3/10 at the same cell and X176's 0/25 one
cell out. Secondary: X170's contact-time corridor, reported whenever there are contact events.

Writes morphogenesis/experiments/E09_pond/l1_field_x178_cliff.json.
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
FIELDS = ROOT / "_hourly" / "x178_fields"
OUT = POND / "l1_field_x178_cliff.json"
SAMPLES = 21
SHARE_INTERVAL = (0.05, 0.55)
X158_AT_GAP9 = (3, 10)


def comps(row):
    return row.get("components_log") or [] if isinstance(row, dict) else []


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
    art = json.loads((L1 / f"x178_{tag}.json").read_text(encoding="utf-8"))
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
    cs = sorted(comps(row), key=lambda c: c.get("area", 0), reverse=True)[:2]
    if len(cs) < 2:
        out["error"] = "no second component at the contact step"
        return out
    step = int(row.get("step"))
    f = FIELDS / tag / f"x178_{tag}_t{step}.npy"
    if not f.exists():
        out["error"] = f"no dump at step {step}"
        return out
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    prof = profile(v, (cs[0]["cx"], cs[0]["cy"]), (cs[1]["cx"], cs[1]["cy"]))
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    peak = max(float(v.max()), 1e-9)
    out.update({"step": step, "peak": round(peak, 4), "corridor": round(min(mid), 4),
                "normalised": round(min(mid) / peak, 4)})
    return out


def main() -> int:
    rows = [row_of(s) for s in range(1121, 1151)]
    fused = sum(1 for r in rows if r["fused"])
    share = round(fused / len(rows), 4)
    ci = wilson(fused, len(rows))
    vals = [r["normalised"] for r in rows if "normalised" in r]
    corr = round(statistics.median(vals), 4) if vals else None
    sd = round(statistics.pstdev(vals), 4) if len(vals) > 1 else None

    x176 = json.loads((POND / "l1_field_x176_past_crossing.json").read_text(encoding="utf-8"))
    gap10 = x176["observed"]
    pooled = (fused + X158_AT_GAP9[0], len(rows) + X158_AT_GAP9[1])

    peak_ok = all(0.05 <= r["peak"] <= 2.0 for r in rows if "peak" in r)
    below = sum(1 for r in rows if "peak" in r and r["corridor"] < r["peak"])
    n_contact = sum(1 for r in rows if "peak" in r)
    readout_ok = sd is not None and sd >= 0.02
    share_hit = SHARE_INTERVAL[0] <= share <= SHARE_INTERVAL[1]

    if not peak_ok:
        verdict = "NOT REPORTABLE: the peak left [0.05, 2.0] at some read."
    elif not share_hit:
        verdict = (f"THE CROSSING IS A CLIFF AT THIS SIZE: the gap-9 share is {fused}/{len(rows)} = {share:.2f} "
                   f"(Wilson {ci}), below the registered floor of {SHARE_INTERVAL[0]}, against {X158_AT_GAP9[0]}/"
                   f"{X158_AT_GAP9[1]} in X158. Pooling the two gives {pooled[0]}/{pooled[1]} = {pooled[0] / pooled[1]:.2f}: the "
                   "three fusions X158 saw were the top of the noise, and radius 6 stops fusing between gap 9 and gap 10.")
    elif share > 0.45:
        verdict = (f"THE SHARE IS HIGHER THAN THE CROSSING'S OWN REPORT: {fused}/{len(rows)} = {share:.2f} (Wilson {ci}) "
                   f"against {X158_AT_GAP9[0]}/{X158_AT_GAP9[1]} in X158 — this cell fuses more readily than X158's arm said, so "
                   f"the crossing's own report understated it, while 0 of {gap10['runs']} at gap 10 keeps the threshold between "
                   "the two cells.")
    else:
        verdict = (f"THE SHARE IS NEAR THE FLOOR BUT NOT AT IT: {fused}/{len(rows)} = {share:.2f} (Wilson {ci}), against "
                   f"{X158_AT_GAP9[0]}/{X158_AT_GAP9[1]} in X158 and 0 of {gap10['runs']} at gap 10. Radius 6 fuses occasionally "
                   "at gap 9 and never at gap 10 — a threshold over one cell with a small share just above it.")

    agg = {"kind": "x178_cliff", "flow": 0.030, "radius": 6.0, "gap": 9, "samples_per_profile": SAMPLES,
           "registered_share_interval": list(SHARE_INTERVAL),
           "observed": {"fused": fused, "runs": len(rows), "share": share, "wilson": ci,
                        "corridor_median": corr, "corridor_sd": sd, "contact": n_contact},
           "references": {"x158_same_cell": {"fused": X158_AT_GAP9[0], "runs": X158_AT_GAP9[1]},
                          "x176_gap10": {"fused": gap10["fused"], "runs": gap10["runs"]},
                          "pooled_gap9": {"fused": pooled[0], "runs": pooled[1], "share": round(pooled[0] / pooled[1], 4)}},
           "controls": {"peak_in_band": peak_ok, "corridor_below_peak_share": round(below / n_contact, 3) if n_contact else None,
                        "readout_varies": readout_ok, "share_in_registered_band": share_hit},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x178] s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor']} "
                  f"normalised {r['normalised']}")
    print(f"[x178] fused {fused}/{len(rows)} = {share} (Wilson {ci}), corridor {corr} (sd {sd}, n {n_contact})")
    print(f"[x178] pooled gap 9: {pooled[0]}/{pooled[1]}")
    print(f"[x178] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
