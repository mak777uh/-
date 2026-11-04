"""x173_bridge_analyse.py — X173: does the bridge's maximum separate the runs that fuse from those that do not?

For each run, and for each sampled step at which there are at least two components, the corridor is read between the two
largest components' centres (X170's definition: minimum of the field over the middle third of the segment, over the peak at that
step). The per-run readout is the maximum of that series, `c_max`, with a censoring flag when it occurs at the last sampled step.

Writes morphogenesis/experiments/E09_pond/l1_field_x173_bridge.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x173_fields"
OUT = POND / "l1_field_x173_bridge.json"
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


def run_row(gap: int, seed: int) -> dict:
    tag = f"g{gap}_s{seed}"
    art = json.loads((L1 / f"x173_{tag}.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    counts = [len(comps(r)) for r in series]
    fused = bool(counts) and min(counts) == 1
    best = None
    best_step = None
    last_usable = None
    for i, row in enumerate(series):
        cs = comps(row)
        # Identity guard: once the world holds many bodies, "the two largest" need not be the seeded pair, and a corridor read
        # between two arbitrary bodies is not the bridge this item is about. The corridor is therefore read only while the
        # pair is essentially alone (at most two extra bodies); later steps are outside the readout.
        if len(cs) < 2 or len(cs) > 4:
            continue
        biggest = sorted(cs, key=lambda c: c.get("area", 0), reverse=True)[:2]
        p0 = (biggest[0]["cx"], biggest[0]["cy"])
        p1 = (biggest[-1]["cx"], biggest[-1]["cy"])
        step = int(row.get("step"))
        f = FIELDS / tag / f"x173_{tag}_t{step}.npy"
        if not f.exists():
            continue
        v = np.load(f)
        if v.ndim == 3:
            v = v[0]
        prof = profile(v, p0, p1)
        n = len(prof)
        mid = prof[n // 3: n - n // 3]
        peak = max(float(v.max()), 1e-9)
        val = min(mid) / peak
        last_usable = step
        if best is None or val > best:
            best, best_step = round(val, 4), step
    return {"gap": gap, "seed": seed, "fused": fused, "min": min(counts) if counts else None,
            "final": counts[-1] if counts else None, "c_max": best, "c_max_step": best_step,
            "last_usable_step": last_usable,
            "censored": bool(best_step is not None and last_usable is not None and best_step >= last_usable)}


def best_threshold(rows: list[dict]) -> dict:
    vals = sorted({r["c_max"] for r in rows if r["c_max"] is not None})
    if not vals:
        return {"threshold": None, "misclassified": None}
    candidates = [vals[0] - 1e-6] + [(a + b) / 2 for a, b in zip(vals, vals[1:])] + [vals[-1] + 1e-6]
    best = None
    for t in candidates:
        miss = sum(1 for r in rows if r["c_max"] is not None and ((r["c_max"] >= t) != r["fused"]))
        if best is None or miss < best["misclassified"]:
            best = {"threshold": round(t, 4), "misclassified": miss, "of": len([r for r in rows if r["c_max"] is not None])}
    return best


def main() -> int:
    rows = [run_row(gap, s) for gap in (8, 10, 11) for s in range(1011, 1021)]
    by_gap = {}
    for gap in (8, 10, 11):
        sub = [r for r in rows if r["gap"] == gap]
        vals = [r["c_max"] for r in sub if r["c_max"] is not None]
        by_gap[str(gap)] = {"fused": sum(1 for r in sub if r["fused"]), "runs": len(sub),
                            "c_max_median": round(statistics.median(vals), 4) if vals else None,
                            "c_max_min": round(min(vals), 4) if vals else None,
                            "c_max_max": round(max(vals), 4) if vals else None,
                            "censored": sum(1 for r in sub if r["censored"])}
    split = best_threshold(rows)
    all_vals = [r["c_max"] for r in rows if r["c_max"] is not None]
    sd_all = round(statistics.pstdev(all_vals), 4) if len(all_vals) > 1 else None
    g8 = by_gap["8"]
    g11 = by_gap["11"]
    control_ok = g8["fused"] >= 9 and g11["fused"] <= 2
    readout_ok = sd_all is not None and sd_all >= 0.02 and all(v < 1.0 for v in all_vals)

    if not control_ok:
        verdict = (f"STOP: the control did not fire — gap 8 fused {g8['fused']}/{g8['runs']} and gap 11 fused "
                   f"{g11['fused']}/{g11['runs']}, outside the registered thresholds (gap 8 at 1.0, gap 11 at or below 0.2).")
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the readout is degenerate (no variance, or a value at or above 1 somewhere)."
    elif split["misclassified"] <= 2:
        verdict = (f"THE CROSSING IS PREDICTABLE FROM THE BRIDGE ALONE: the maximum normalised corridor separates the runs that "
                   f"fuse from those that do not with {split['misclassified']} misclassified of {split['of']} at a threshold of "
                   f"{split['threshold']:.2f}. Gap 8 reads {g8['c_max_median']:.2f} (median), gap 10 {by_gap['10']['c_max_median']:.2f} "
                   f"and gap 11 {g11['c_max_median']:.2f}, so the crossing is the gap at which the bridge stops reaching the "
                   f"threshold, not a separately measured length.")
    else:
        verdict = (f"THE CORRIDOR IS A READOUT OF CONTACT, NOT A PREDICTOR OF IT: the best single threshold on the bridge's "
                   f"maximum misclassifies {split['misclassified']} of {split['of']} runs (gap 8 median "
                   f"{g8['c_max_median']:.2f}, gap 10 {by_gap['10']['c_max_median']:.2f}, gap 11 {g11['c_max_median']:.2f}), so "
                   f"the maximum the bridge reaches does not by itself decide which pairs merge.")

    agg = {"kind": "x173_bridge", "flow": 0.030, "radius": 3.0, "samples_per_profile": SAMPLES,
           "definition": "per-step corridor between the two largest components, normalised by the peak; per-run readout is the maximum",
           "by_gap": by_gap, "split": split, "sd_all": sd_all,
           "controls": {"gap8_fused": g8["fused"], "gap11_fused": g11["fused"], "control_fired": control_ok,
                        "readout_varies": readout_ok},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        print(f"[x173] g{r['gap']} s{r['seed']}: fused {r['fused']} c_max {r['c_max']} at {r['c_max_step']} "
              f"(last usable {r['last_usable_step']}, censored {r['censored']})")
    print(f"[x173] by gap {by_gap}")
    print(f"[x173] split {split}, sd_all {sd_all}")
    print(f"[x173] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
