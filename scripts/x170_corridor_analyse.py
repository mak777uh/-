"""x170_corridor_analyse.py — X170: the corridor concentration at contact, at three inflow rates.

At the last logged step with two bodies, the field is sampled along the segment joining the two component centres, the minimum
is taken over the middle third (the space between the bodies, not their rims), and divided by the larger of the two bodies'
peak values at that step. Group medians and spreads per rate, plus the control checks the plan registered.

Writes morphogenesis/experiments/E09_pond/l1_field_x170_corridor.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x170_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x170_corridor.json"
PEAK_LOW, PEAK_HIGH = 0.05, 2.0
SAMPLES = 21


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
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


def run_row(flow: float, seed: int) -> dict | None:
    tag = f"F{int(flow * 1000)}_s{seed}"
    art = json.loads((L1 / f"x170_{tag}.json").read_text(encoding="utf-8"))
    series = art.get("series") or []
    first_one = None
    for i, row in enumerate(series):
        if len(comps(row)) == 1:
            first_one = i
            break
    if first_one is None:
        # never fused: no contact event, so this run carries no contact state
        last = series[-1] if series else None
        if last is None:
            return {"flow": flow, "seed": seed, "error": "empty series"}
        return {"flow": flow, "seed": seed, "fused": False, "min_components": min(len(comps(r)) for r in series),
                "error": "never reached one component, so there is no contact step"}
    last_two = series[first_one - 1] if first_one > 0 else None
    if last_two is None:
        return {"flow": flow, "seed": seed, "error": "one component at the first sampled step"}
    cs = sorted(comps(last_two), key=lambda c: c["cx"])
    p0 = (cs[0]["cx"], cs[0]["cy"])
    p1 = (cs[-1]["cx"], cs[-1]["cy"])
    step = int(last_two.get("step"))
    f = FIELDS / tag / f"x170_{tag}_t{step}.npy"
    if not f.exists():
        return {"flow": flow, "seed": seed, "error": f"no dump at step {step}"}
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    prof = profile(v, p0, p1)
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    peak = max(float(v.max()), 1e-9)
    return {"flow": flow, "seed": seed, "fused": True, "step": step, "peak": round(peak, 4),
            "corridor": round(min(prof), 4), "corridor_middle": round(min(mid), 4),
            "normalised": round(min(mid) / peak, 4),
            "normalised_full": round(min(prof) / peak, 4),
            "profile": [round(x, 4) for x in prof]}


def main() -> int:
    rows = []
    for flow in (0.026, 0.030, 0.036):
        for seed in range(971, 986):
            r = run_row(flow, seed)
            if r:
                rows.append(r)
    good = [r for r in rows if "normalised" in r]
    contact = sum(1 for r in rows if r.get("fused"))
    print(f"[x170] runs with a contact step: {contact} of {len(rows)}")
    by_flow = {}
    for r in good:
        by_flow.setdefault(f"{r['flow']:g}", []).append(r["normalised"])
    medians = {k: round(statistics.median(v), 4) for k, v in by_flow.items()}
    spreads = {k: round(statistics.pstdev(v), 4) if len(v) > 1 else None for k, v in by_flow.items()}
    values = [r["normalised"] for r in good]
    sd_all = round(statistics.pstdev(values), 4) if len(values) > 1 else None

    peak_ok = all(PEAK_LOW <= r["peak"] <= PEAK_HIGH for r in good)
    below = sum(1 for r in good if r["corridor_middle"] < r["peak"])
    corridor_ok = bool(good) and below / len(good) >= 0.8
    readout_ok = sd_all is not None and sd_all >= 0.02 and not all(v in (0.0, 1.0) for v in values)
    extreme = None
    if len(medians) >= 2:
        lo = min(medians, key=lambda k: medians[k])
        hi = max(medians, key=lambda k: medians[k])
        spread = max((s for s in spreads.values() if s is not None), default=0.0)
        diff = round(medians[hi] - medians[lo], 4)
        extreme = {"contrast": f"{lo} (lowest) vs {hi} (highest)", "difference": diff,
                   "pooled_sd": spread, "within_one_sd": bool(spread and abs(diff) <= spread),
                   "direction": "falls with the source" if medians[hi] < medians[lo] else "rises with the source"}

    if not peak_ok:
        verdict = "NOT REPORTABLE: the body peak left the registered band at some dump, so the runs are not in the regime."
    elif not corridor_ok:
        verdict = "NOT REPORTABLE: the corridor does not read below the body peak, so the segment is measuring rims."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the normalised corridor is degenerate (constant, or at 0 or 1 in every run)."
    elif extreme and extreme["within_one_sd"]:
        verdict = (
            "THE CORRIDOR IS THE SAME AT EVERY RATE: the normalised concentration between the bodies at contact is "
            + ", ".join(f"{medians[k]:.2f} at F = {k}" for k in sorted(medians))
            + f", a spread of {extreme['difference']:.2f} against a within-group sd of {extreme['pooled_sd']:.2f}. The source "
            "changes the amount of chemical and not the state of the gap, which is why the crossing does not move with it.")
    else:
        verdict = (
            "THE CORRIDOR DOES DEPEND ON THE SOURCE: the normalised concentration at contact runs "
            + ", ".join(f"{medians[k]:.2f} at F = {k}" for k in sorted(medians))
            + f", a difference of {extreme['difference']:.2f} against a within-group sd of {extreme['pooled_sd']:.2f}, so the "
            "insensitivity of the crossing needs a different explanation.")

    agg = {"kind": "x170_corridor", "gap": 10, "sep": 16, "samples_per_profile": SAMPLES,
           "definition": ("minimum of the field over the middle third of the segment joining the two component centres at the "
                          "last two-body step, divided by the peak field at that step"),
           "medians": medians, "spreads": spreads, "sd_all": sd_all, "extreme": extreme,
           "contact_runs": contact, "runs_total": len(rows),
           "controls": {"peak_in_band": peak_ok, "corridor_below_peak_share": round(below / len(good), 3) if good else None,
                        "corridor_below_peak": corridor_ok, "readout_varies": readout_ok},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x170] F{r['flow']:g} s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor_middle']} "
                  f"normalised {r['normalised']}")
    print(f"[x170] medians {medians} spreads {spreads}")
    print(f"[x170] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
