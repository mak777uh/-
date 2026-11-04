"""x174_gap_corridor_analyse.py — X174: corridor at contact across three gaps, one size, one rate.

Radius 3, F = 0.030, surface gaps 8 and 9 measured here; gap 10 read from X170's aggregate (same seeds family, same readout).
Readout: X170's contact-time corridor.
Writes morphogenesis/experiments/E09_pond/l1_field_x174_gap_corridor.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x174_fields"
OUT = POND / "l1_field_x174_gap_corridor.json"
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


def row_of(gap: int, seed: int) -> dict:
    tag = f"g{gap}_s{seed}"
    art = json.loads((L1 / f"x174_{tag}.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    counts = [len(comps(r)) for r in series]
    fused = bool(counts) and min(counts) == 1
    out = {"gap": gap, "seed": seed, "fused": fused, "min": min(counts) if counts else None,
           "final": counts[-1] if counts else None}
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
    p0 = (cs[0]["cx"], cs[0]["cy"])
    p1 = (cs[1]["cx"], cs[1]["cy"])
    step = int(row.get("step"))
    f = FIELDS / tag / f"x174_{tag}_t{step}.npy"
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


def main() -> int:
    rows = [row_of(8, s) for s in range(1031, 1041)] + [row_of(9, s) for s in range(1031, 1046)]
    x170 = json.loads((POND / "l1_field_x170_corridor.json").read_text(encoding="utf-8"))
    # every radius-3 gap-10 run at F = 0.030, fused or not, so the arm's share is a real share
    ref10 = [{"gap": 10, "seed": r["seed"], "fused": bool(r.get("fused")),
              **({"normalised": r["normalised"]} if r.get("normalised") else {})}
             for r in x170["runs"] if abs(r["flow"] - 0.030) < 1e-9]
    pool = rows + ref10

    by_gap = {}
    for gap in (8, 9, 10):
        sub = [r for r in pool if r["gap"] == gap]
        vals = [r["normalised"] for r in sub if "normalised" in r]
        by_gap[str(gap)] = {"contact": len(vals), "runs": len(sub),
                            "median": round(statistics.median(vals), 4) if vals else None,
                            "spread": round(statistics.pstdev(vals), 4) if len(vals) > 1 else None,
                            "share": round(len(vals) / len(sub), 3) if sub else None,
                            "values": vals}
    medians = {k: v["median"] for k, v in by_gap.items() if v["median"] is not None}
    pooled = max((v["spread"] for v in by_gap.values() if v["spread"]), default=None)
    diff = None
    if len(medians) >= 2:
        lo = min(medians, key=lambda k: medians[k])
        hi = max(medians, key=lambda k: medians[k])
        diff = {"low_gap": lo, "high_gap": hi, "difference": round(medians[hi] - medians[lo], 4),
                "pooled_sd": pooled, "within_pooled": bool(pooled and abs(medians[hi] - medians[lo]) <= pooled)}

    g8 = by_gap["8"]
    g10 = by_gap["10"]
    control_ok = (g8["share"] or 0) >= 0.8 and (g10["share"] or 0) <= 0.8
    all_vals = [r["normalised"] for r in pool if "normalised" in r]
    sd_all = round(statistics.pstdev(all_vals), 4) if len(all_vals) > 1 else None
    peak_ok = all(0.05 <= r["peak"] <= 2.0 for r in rows if "peak" in r)
    below = sum(1 for r in rows if "peak" in r and r["corridor"] < r["peak"])
    n_contact = sum(1 for r in rows if "peak" in r)
    corridor_ok = n_contact > 0 and below / n_contact >= 0.8
    readout_ok = sd_all is not None and sd_all >= 0.02

    if not control_ok:
        verdict = (f"STOP: the control did not fire — the gap-8 share is {g8['share']} and the gap-10 share is {g10['share']}, "
                   "outside the registered (gap 8 at or above 0.8, gap 10 at or below 0.8).")
    elif not (peak_ok and corridor_ok and readout_ok):
        verdict = "NOT REPORTABLE: a control failed (peak outside band, corridor not below peak, or no variance)."
    elif diff and diff["within_pooled"]:
        verdict = ("THE CRITERION IS PER-CONTACT: at F = 0.030 and radius 3 the corridor at contact reads " +
                   ", ".join(f"{medians[k]:.2f} at gap {k}" for k in sorted(medians, key=int)) +
                   f", a difference of {diff['difference']:.2f} against a pooled within-gap spread of {diff['pooled_sd']:.3f}. "
                   "Neither the body's size (X171) nor the initial distance moves the fraction at which a merge happens, so "
                   "X171's confound is resolved in the direction that keeps the rule.")
    else:
        verdict = ("THE CRITERION DEPENDS ON THE INITIAL GAP: at F = 0.030 and radius 3 the corridor at contact reads " +
                   ", ".join(f"{medians[k]:.2f} at gap {k}" for k in sorted(medians, key=int)) +
                   f", a difference of {diff['difference']:.2f} against a pooled within-gap spread of {diff['pooled_sd']:.3f}. "
                   "X171's confound is real: the fraction is not a property of the moment alone but also of how far the bridge "
                   "had to travel, and the rule takes the gap as a second input.")

    agg = {"kind": "x174_gap_corridor", "flow": 0.030, "radius": 3.0, "samples_per_profile": SAMPLES,
           "definition": "as X170/X171: contact-time corridor over the peak",
           "by_gap": {k: {kk: vv for kk, vv in v.items() if kk != "values"} for k, v in by_gap.items()},
           "medians": medians, "difference": diff, "sd_all": sd_all,
           "controls": {"gap8_share": g8["share"], "gap10_share": g10["share"], "peak_in_band": peak_ok,
                        "corridor_below_peak_share": round(below / n_contact, 3) if n_contact else None,
                        "readout_varies": readout_ok},
           "runs": rows, "gap10_from_x170": ref10, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x174] g{r['gap']} s{r['seed']}: step {r['step']} peak {r['peak']} "
                  f"corridor {r['corridor']} normalised {r['normalised']}")
    print(f"[x174] by gap {({k: (v['contact'], v['runs'], v['median'], v['spread']) for k, v in by_gap.items()})}")
    print(f"[x174] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
