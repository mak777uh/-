"""x177_edge_analyse.py — X177: the band's upper edge, radius 4.5 at gap 11.

Contact-time corridor (X170's definition) at radius 4.5, gap 11, F = 0.030, twenty seeds; the two registered intervals;
and the arm's position relative to X175's two-factor reading.

Writes morphogenesis/experiments/E09_pond/l1_field_x177_edge.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIELDS = ROOT / "_hourly" / "x177_fields"
OUT = POND / "l1_field_x177_edge.json"
SAMPLES = 21
CORRIDOR_INTERVAL = (0.50, 0.56)
SHARE_INTERVAL = (0.05, 0.30)


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
    art = json.loads((L1 / f"x177_{tag}.json").read_text(encoding="utf-8"))
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
    f = FIELDS / tag / f"x177_{tag}_t{step}.npy"
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
    rows = [row_of(s) for s in range(1096, 1116)]
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

    if n_contact < 2:
        verdict = (f"UNDECIDED, AND THE EDGE IS NOT REACHABLE AT THIS CELL: only {n_contact} contact events in {len(rows)} runs "
                   f"(share {share:.2f}), so no corridor can be compared with {CORRIDOR_INTERVAL[0]}-{CORRIDOR_INTERVAL[1]}. With "
                   "X158's 0 of 15 at the same cell, radius 4.5 at gap 11 is 0 of 35: the marginal-but-alive cell the band's upper "
                   "edge needed does not exist one cell past this size's crossing. The registered share interval "
                   f"({SHARE_INTERVAL[0]}-{SHARE_INTERVAL[1]}) is missed on the low side, and the corridor half of the prediction "
                   "is untestable here.")
    elif not peak_ok or not corridor_ok:
        verdict = "NOT REPORTABLE: a control failed (peak outside [0.05, 2.0], or the corridor not below the peak everywhere)."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the readout does not vary across runs."
    elif corridor_hit and share_hit:
        verdict = (f"THE BAND'S UPPER EDGE IS REAL AND REACHABLE: the corridor reads {corr:.2f} (predicted "
                   f"{CORRIDOR_INTERVAL[0]}-{CORRIDOR_INTERVAL[1]}) and the share {fused}/{len(rows)} = {share:.2f} (predicted "
                   f"{SHARE_INTERVAL[0]}-{SHARE_INTERVAL[1]}). The most marginal arm that still fuses sits at the top of the band.")
    elif share_hit and not corridor_hit:
        verdict = (f"SHAPE MISS: the arm is where it was placed (share {fused}/{len(rows)} = {share:.2f}, inside the predicted "
                   f"{SHARE_INTERVAL[0]}-{SHARE_INTERVAL[1]}) but its corridor reads {corr:.2f} against a predicted "
                   f"{CORRIDOR_INTERVAL[0]}-{CORRIDOR_INTERVAL[1]}, so the band's upper edge is not where the two-factor picture "
                   "put it.")
    elif corridor_hit and not share_hit:
        verdict = (f"PLACEMENT MISS: the corridor lands ({corr:.2f}, predicted {CORRIDOR_INTERVAL[0]}-{CORRIDOR_INTERVAL[1]}) but "
                   f"the share reads {fused}/{len(rows)} = {share:.2f}, outside {SHARE_INTERVAL[0]}-{SHARE_INTERVAL[1]}, so the "
                   "arm sits elsewhere than intended and the corridor agreement is not evidence about the edge.")
    else:
        verdict = (f"BOTH MISS: corridor {corr:.2f} against {CORRIDOR_INTERVAL[0]}-{CORRIDOR_INTERVAL[1]} and share "
                   f"{fused}/{len(rows)} = {share:.2f} against {SHARE_INTERVAL[0]}-{SHARE_INTERVAL[1]}; the edge is not at this "
                   "cell.")

    agg = {"kind": "x177_edge", "flow": 0.030, "radius": 4.5, "gap": 11, "samples_per_profile": SAMPLES,
           "predictions": {"corridor": list(CORRIDOR_INTERVAL), "share": list(SHARE_INTERVAL)},
           "observed": {"fused": fused, "runs": len(rows), "share": share, "corridor_median": corr,
                        "corridor_sd": sd, "contact": n_contact},
           "controls": {"peak_in_band": peak_ok, "corridor_below_peak_share": round(below / n_contact, 3) if n_contact else None,
                        "readout_varies": readout_ok, "enough_contacts": n_contact >= 2},
           "runs": rows, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        if "normalised" in r:
            print(f"[x177] s{r['seed']}: step {r['step']} peak {r['peak']} corridor {r['corridor']} "
                  f"normalised {r['normalised']}")
    print(f"[x177] fused {fused}/{len(rows)}, corridor {corr} (sd {sd}, n {n_contact})")
    print(f"[x177] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
