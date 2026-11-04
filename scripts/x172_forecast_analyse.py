"""x172_forecast_analyse.py — X172: did the two registered predictions at F = 0.033 land?

Readouts as in X170: fusion share over the twenty gap-10 runs (min component count == 1 at least once) and the corridor at
contact (minimum over the middle third of the segment between the two bodies' centres at the last two-body step, over the peak).
Both are compared with the intervals registered in the plan, and with the two neighbouring rates read from X170's aggregate.

Writes morphogenesis/experiments/E09_pond/l1_field_x172_forecast.json.
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
FIELDS = ROOT / "_hourly" / "x172_fields"
OUT = POND / "l1_field_x172_forecast.json"
SAMPLES = 21


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


def row_of(arm: str, seed: int) -> dict:
    tag = f"{arm}_s{seed}"
    art = json.loads((L1 / f"x172_{tag}.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    counts = [len(comps(r)) for r in series]
    fused = bool(counts) and min(counts) == 1
    out = {"arm": arm, "seed": seed, "fused": fused, "min": min(counts) if counts else None,
           "final": counts[-1] if counts else None}
    if not fused:
        return out
    first_one = counts.index(1)
    if first_one == 0:
        out["error"] = "one component at the first sampled step"
        return out
    row = series[first_one - 1]
    cs = sorted(comps(row), key=lambda c: c["cx"])
    p0, p1 = (cs[0]["cx"], cs[0]["cy"]), (cs[-1]["cx"], cs[-1]["cy"])
    step = int(row.get("step"))
    f = FIELDS / tag / f"x172_{tag}_t{step}.npy"
    if not f.exists():
        out["error"] = f"no dump at step {step}"
        return out
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    prof = profile(v, p0, p1)
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    peak = max(float(v.max()), 1e-9)
    out.update({"step": step, "peak": round(peak, 4), "corridor": round(min(mid), 4),
                "normalised": round(min(mid) / peak, 4)})
    return out


def wilson(k: int, n: int, z: float = 1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def main() -> int:
    rows = [row_of("gap10", s) for s in range(986, 1006)] + [row_of("gap8", s) for s in range(986, 991)]
    g10 = [r for r in rows if r["arm"] == "gap10"]
    g8 = [r for r in rows if r["arm"] == "gap8"]
    fused = sum(1 for r in g10 if r["fused"])
    share = round(fused / len(g10), 4)
    vals = [r["normalised"] for r in g10 if "normalised" in r]
    corr = round(statistics.median(vals), 4) if vals else None
    sd = round(statistics.pstdev(vals), 4) if len(vals) > 1 else None
    control = sum(1 for r in g8 if r["fused"]) / len(g8) if g8 else None

    x170 = json.loads((POND / "l1_field_x170_corridor.json").read_text(encoding="utf-8"))
    neighbour = {}
    for flow in (0.026, 0.030, 0.036):
        sub = [r for r in x170["runs"] if abs(r["flow"] - flow) < 1e-9 and r.get("fused")]
        neighbour[f"{flow:g}"] = {"share": round(len(sub) / 15, 4),
                                  "corridor": round(statistics.median([r["normalised"] for r in sub]), 4) if sub else None}

    share_ok = 9 <= fused <= 15
    corr_ok = corr is not None and 0.356 <= corr <= 0.516
    peak_ok = all(0.05 <= r["peak"] <= 2.0 for r in g10 if "peak" in r)
    below = sum(1 for r in g10 if "peak" in r and r["corridor"] < r["peak"])
    n_contact = sum(1 for r in g10 if "peak" in r)
    corridor_ok = n_contact > 0 and below / n_contact >= 0.8
    readout_ok = sd is not None and sd >= 0.02

    if control is None or control < 1.0:
        verdict = f"STOP: the gap-8 control fused {control:.0%} of its runs at this rate, so the regime is not the same."
    elif not (peak_ok and corridor_ok and readout_ok):
        verdict = "NOT REPORTABLE: a control or the readout failed (peak outside band, corridor not below peak, or no variance)."
    elif share_ok and corr_ok:
        verdict = (f"BOTH PREDICTIONS LAND: {fused} of 20 runs fused (predicted 9-15) and the corridor at contact reads "
                   f"{corr:.2f} (predicted 0.436 ± 0.08). The dependence of the crossing on the source is smooth enough to "
                   "interpolate across the range it was measured in, which turns X170's ladder into a calibrated relation.")
    elif share_ok and not corr_ok:
        verdict = (f"PARTIAL: the share lands ({fused} of 20, predicted 9-15) but the corridor reads {corr:.2f}, outside the "
                   "predicted 0.436 ± 0.08 — the share interpolates and the corridor does not, so the second relation is not "
                   "linear in this range even though the first is.")
    elif corr_ok and not share_ok:
        verdict = (f"PARTIAL: the corridor lands ({corr:.2f}, predicted 0.436 ± 0.08) but only {fused} of 20 runs fused "
                   "(predicted 9-15), so the corridor interpolates and the share does not — the two readouts are less tightly "
                   "coupled than the ladder assumed.")
    else:
        verdict = (f"BOTH MISS: {fused} of 20 runs fused (predicted 9-15) and the corridor reads {corr:.2f} (predicted "
                   "0.436 ± 0.08). The dependence on the source is real in direction — X170 measured it at both neighbours — but "
                   "not monotone-to-linear across this range, and the interpolation is not a law.")

    agg = {"kind": "x172_forecast", "flow": 0.033, "radius": 3.0, "gap": 10,
           "predictions": {"share": "between 9 and 15 of 20", "share_point": 0.567,
                           "corridor": "0.436 ± 0.08", "corridor_interval": [0.356, 0.516]},
           "observed": {"fused": fused, "runs": len(g10), "share": share, "wilson": wilson(fused, len(g10)),
                        "corridor_median": corr, "corridor_sd": sd, "contact_runs": len(vals)},
           "controls": {"gap8_share": control, "peak_in_band": peak_ok, "corridor_below_peak_share":
                        round(below / n_contact, 3) if n_contact else None, "readout_varies": readout_ok},
           "neighbours_from_x170": neighbour, "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in g10:
        if "normalised" in r:
            print(f"[x172] s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor']} "
                  f"normalised {r['normalised']}")
    print(f"[x172] fused {fused}/20, corridor median {corr} (sd {sd}, n {len(vals)}), control {control}")
    print(f"[x172] neighbours {neighbour}")
    print(f"[x172] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
