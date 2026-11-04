"""x171_corridor_sizes_analyse.py — X171: is the corridor at contact the same at every body size?

Same readout as X170 (minimum of the field over the middle third of the segment joining the two bodies' centres at the last
sampled step with two bodies, over the peak field at that step), applied to radius 4.5 at gap 10 and radius 6 at gap 9 at
F = 0.030, with the radius-3 value of X170 read from its aggregate as the reference.

Writes morphogenesis/experiments/E09_pond/l1_field_x171_corridor_sizes.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x171_fields"
OUT = POND / "l1_field_x171_corridor_sizes.json"
SAMPLES = 21
PEAK_LOW, PEAK_HIGH = 0.05, 2.0


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


def run_row(radius: float, gap: int, seed: int) -> dict:
    tag = f"r{radius:g}_g{gap}_s{seed}"
    art = json.loads((L1 / f"x171_{tag}.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    first_one = None
    for i, row in enumerate(series):
        if len(comps(row)) == 1:
            first_one = i
            break
    if first_one is None:
        mins = min((len(comps(r)) for r in series), default=None)
        return {"radius": radius, "gap": gap, "seed": seed, "fused": False, "min_components": mins,
                "error": "never reached one component, so there is no contact step"}
    if first_one == 0:
        return {"radius": radius, "gap": gap, "seed": seed, "error": "one component at the first sampled step"}
    row = series[first_one - 1]
    cs = sorted(comps(row), key=lambda c: c["cx"])
    p0 = (cs[0]["cx"], cs[0]["cy"])
    p1 = (cs[-1]["cx"], cs[-1]["cy"])
    step = int(row.get("step"))
    f = FIELDS / tag / f"x171_{tag}_t{step}.npy"
    if not f.exists():
        return {"radius": radius, "gap": gap, "seed": seed, "fused": True, "error": f"no dump at step {step}"}
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    prof = profile(v, p0, p1)
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    peak = max(float(v.max()), 1e-9)
    return {"radius": radius, "gap": gap, "seed": seed, "fused": True, "step": step, "peak": round(peak, 4),
            "corridor": round(min(mid), 4), "normalised": round(min(mid) / peak, 4)}


def main() -> int:
    rows = []
    for radius, gap in ((4.5, 10), (6.0, 9)):
        for seed in range(971, 986):
            rows.append(run_row(radius, gap, seed))

    x170 = json.loads((POND / "l1_field_x170_corridor.json").read_text(encoding="utf-8"))
    ref_values = [r["normalised"] for r in x170["runs"] if r.get("normalised") and abs(r["flow"] - 0.030) < 1e-9]
    groups: dict[str, list[float]] = {"3": ref_values}
    contact: dict[str, tuple[int, int]] = {"3": (len(ref_values), sum(1 for r in x170["runs"] if abs(r["flow"] - 0.030) < 1e-9))}
    for radius in (4.5, 6.0):
        vals = [r["normalised"] for r in rows if r.get("radius") == radius and "normalised" in r]
        runs = [r for r in rows if r.get("radius") == radius]
        groups[f"{radius:g}"] = vals
        contact[f"{radius:g}"] = (len(vals), len(runs))

    medians = {k: round(statistics.median(v), 4) for k, v in groups.items() if v}
    spreads = {k: round(statistics.pstdev(v), 4) for k, v in groups.items() if len(v) > 1}
    shares = {k: round(c / n, 3) if n else None for k, (c, n) in contact.items()}
    all_vals = [x for v in groups.values() for x in v]
    sd_all = round(statistics.pstdev(all_vals), 4) if len(all_vals) > 1 else None
    peak_ok = all(PEAK_LOW <= r["peak"] <= PEAK_HIGH for r in rows if "peak" in r)
    below = sum(1 for r in rows if "peak" in r and r["corridor"] < r["peak"])
    n_contact = sum(1 for r in rows if "peak" in r)
    corridor_ok = n_contact > 0 and below / n_contact >= 0.8
    readout_ok = sd_all is not None and sd_all >= 0.02 and not all(v in (0.0, 1.0) for v in all_vals)
    crossing_ok = all(0.2 <= s <= 0.8 for s in shares.values() if s is not None)

    pooled = max(spreads.values()) if spreads else None
    diff = None
    if len(medians) >= 2:
        lo = min(medians, key=lambda k: medians[k])
        hi = max(medians, key=lambda k: medians[k])
        diff = {"low": lo, "high": hi, "difference": round(medians[hi] - medians[lo], 4), "pooled_sd": pooled,
                "within_pooled": bool(pooled and abs(medians[hi] - medians[lo]) <= pooled)}

    if not peak_ok or not corridor_ok:
        verdict = "NOT REPORTABLE: a control failed (peak left [0.05, 2.0], or the corridor did not read below the peak)."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the normalised corridor is degenerate across runs."
    elif not crossing_ok:
        verdict = ("NOT COMPARABLE AT THE CROSSING: an arm's fusion share at its own crossing gap falls outside [0.2, 0.8] — " +
                   ", ".join(f"radius {k}: {v}" for k, v in shares.items()) + " — so that arm is not sitting at the crossing.")
    elif diff and diff["within_pooled"]:
        verdict = ("THE CORRIDOR IS A SIZE-INDEPENDENT CRITERION: at F = 0.030 the field between the bodies at contact reads " +
                   ", ".join(f"{medians[k]:.2f} at radius {k}" for k in sorted(medians, key=float)) +
                   f", a difference of {diff['difference']:.2f} against a pooled within-group spread of {diff['pooled_sd']:.2f}. "
                   "Two bodies become one at a roughly constant fraction of the body peak, so the crossing in cells is wherever "
                   "that fraction is reached — X170's description is a rule.")
    else:
        verdict = ("THE CORRIDOR IS NOT A SIZE-INDEPENDENT CRITERION: at F = 0.030 it reads " +
                   ", ".join(f"{medians[k]:.2f} at radius {k}" for k in sorted(medians, key=float)) +
                   f", a difference of {diff['difference']:.2f} against a pooled within-group spread of {diff['pooled_sd']:.2f}. "
                   "The corridor describes each arm rather than predicting the crossing, and the source dependence X170 found "
                   "stays a fact without a model.")

    agg = {"kind": "x171_corridor_sizes", "flow": 0.030, "samples_per_profile": SAMPLES,
           "definition": "as X170: minimum over the middle third of the segment between the two bodies' centres, over the peak",
           "medians": medians, "spreads": spreads, "fusion_share_at_crossing_gap": shares,
           "contact_counts": {k: {"contact": c, "runs": n} for k, (c, n) in contact.items()},
           "difference": diff, "sd_all": sd_all,
           "controls": {"peak_in_band": peak_ok, "corridor_below_peak_share": round(below / n_contact, 3) if n_contact else None,
                        "readout_varies": readout_ok, "arms_at_crossing": crossing_ok},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x171] r{r['radius']:g} g{r['gap']} s{r['seed']}: step {r['step']} peak {r['peak']} "
                  f"corridor {r['corridor']} normalised {r['normalised']}")
    print(f"[x171] medians {medians} spreads {spreads} shares {shares} contacts {contact}")
    print(f"[x171] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
