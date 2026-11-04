"""x175_interior_analyse.py — X175: does the arm land where X174's curve said it would?

Contact-time corridor (X170's definition) at radius 4.5, gap 9, F = 0.030, fifteen seeds; the two registered intervals; and the
arm's position on the eight-cell relation X174 built.

Writes morphogenesis/experiments/E09_pond/l1_field_x175_interior.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x175_fields"
OUT = POND / "l1_field_x175_interior.json"
SAMPLES = 21
CORRIDOR_INTERVAL = (0.42, 0.46)
SHARE_INTERVAL = (0.45, 0.72)


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


def row_of(seed: int) -> dict:
    tag = f"s{seed}"
    art = json.loads((L1 / f"x175_{tag}.json").read_text(encoding="utf-8"))
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
    f = FIELDS / tag / f"x175_{tag}_t{step}.npy"
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
    rows = [row_of(s) for s in range(1061, 1076)]
    fused = sum(1 for r in rows if r["fused"])
    share = round(fused / len(rows), 4)
    vals = [r["normalised"] for r in rows if "normalised" in r]
    corr = round(statistics.median(vals), 4) if vals else None
    sd = round(statistics.pstdev(vals), 4) if len(vals) > 1 else None

    peak_ok = all(0.05 <= r["peak"] <= 2.0 for r in rows if "peak" in r)
    below = sum(1 for r in rows if "peak" in r and r["corridor"] < r["peak"])
    n_contact = sum(1 for r in rows if "peak" in r)
    corridor_ok = n_contact > 0 and below / n_contact >= 1.0
    readout_ok = sd is not None and sd >= 0.02

    corridor_hit = corr is not None and CORRIDOR_INTERVAL[0] <= corr <= CORRIDOR_INTERVAL[1]
    share_hit = SHARE_INTERVAL[0] <= share <= SHARE_INTERVAL[1]

    if not peak_ok or not corridor_ok:
        verdict = "NOT REPORTABLE: a control failed (peak outside [0.05, 2.0], or the corridor not below the peak everywhere)."
    elif n_contact < 3:
        verdict = (f"UNPLACED: only {n_contact} contact events, too few to describe a point on the curve; the arm is past its "
                   "crossing rather than near it.")
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the readout does not vary across runs."
    elif corridor_hit and share_hit:
        verdict = (f"THE CURVE HOLDS AT AN INTERIOR POINT: the corridor reads {corr:.2f} (predicted 0.42-0.46) and the share "
                   f"{fused}/{len(rows)} = {share:.2f} (predicted 0.45-0.72). The nine-cell relation survives an arm chosen "
                   "inside the (size, gap) plane that neither earlier family covered.")
    elif share_hit and not corridor_hit:
        verdict = (f"SHAPE MISS: the arm is where it was placed (share {fused}/{len(rows)} = {share:.2f}, inside the predicted "
                   f"0.45-0.72) but its corridor reads {corr:.2f} against a predicted 0.42-0.46, so the relation's slope is "
                   "wrong even though the share axis is right.")
    elif corridor_hit and not share_hit:
        verdict = (f"PLACEMENT MISS: the corridor lands ({corr:.2f}, predicted 0.42-0.46) but the share reads {fused}/{len(rows)} "
                   f"= {share:.2f}, outside 0.45-0.72, so the arm sits elsewhere on the curve than intended and the corridor "
                   "agreement is not evidence about the slope.")
    else:
        verdict = (f"BOTH MISS: corridor {corr:.2f} against 0.42-0.46 and share {fused}/{len(rows)} = {share:.2f} against "
                   "0.45-0.72; the arm was not placed where the interpolation said, and nothing is claimed about the curve.")

    agg = {"kind": "x175_interior", "flow": 0.030, "radius": 4.5, "gap": 9, "samples_per_profile": SAMPLES,
           "predictions": {"corridor": list(CORRIDOR_INTERVAL), "share": list(SHARE_INTERVAL)},
           "observed": {"fused": fused, "runs": len(rows), "share": share, "corridor_median": corr,
                        "corridor_sd": sd, "contact": n_contact},
           "controls": {"peak_in_band": peak_ok, "corridor_below_peak_share": round(below / n_contact, 3) if n_contact else None,
                        "readout_varies": readout_ok, "enough_contacts": n_contact >= 3},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x175] s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor']} "
                  f"normalised {r['normalised']}")
    print(f"[x175] fused {fused}/{len(rows)}, corridor {corr} (sd {sd}, n {n_contact})")
    print(f"[x175] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
