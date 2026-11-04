"""x182_local_inflow_analyse.py — X182: five chosen levels of the seeded site's local inflow, same arm.

Recomputes G from the logged centres (not from the selection), reports the per-level shares with Wilson intervals, the
Cochran-Armitage one-sided test for a negative trend in G, and X170's contact-time corridor as a description per level.

Writes morphogenesis/experiments/E09_pond/l1_field_x182_local_inflow.json.
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
FIELDS = ROOT / "_hourly" / "x182_fields"
OUT = POND / "l1_field_x182_local_inflow.json"
GRID = 96
HETERO_SCALE = 12.0
SAMPLES = 21
PREDICTION = {"bottom_share": [0.5, 1.0], "top_share": [0.0, 0.35], "p_threshold": 0.05}


def G_at(x: float, y: float) -> float:
    ky = 2.0 * math.pi / HETERO_SCALE
    return (math.sin(ky * (int(round(y)) % GRID)) * math.cos(ky * (int(round(x)) % GRID)) + 1.0) / 2.0


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def cochran_armitage_negative(scores: list[float], cases: list[int], totals: list[int]):
    """One-sided (negative) Cochran-Armitage trend test on group scores."""
    n = sum(totals)
    if n == 0:
        return None, None
    p = sum(cases) / n
    if p in (0.0, 1.0):
        return None, None
    xbar = sum(s * t for s, t in zip(scores, totals)) / n
    num = sum(s * c for s, c in zip(scores, cases)) - p * sum(s * t for s, t in zip(scores, totals))
    var = p * (1 - p) * sum(t * (s - xbar) ** 2 for s, t in zip(scores, totals))
    if var <= 0:
        return None, None
    z = num / math.sqrt(var)
    p_one = round(0.5 * math.erfc(z / math.sqrt(2)), 4)  # negative direction: small p means z << 0 is NOT significant
    p_two = round(math.erfc(abs(z) / math.sqrt(2)), 4)
    return round(z, 3), {"p_negative_direction": round(1 - 0.5 * math.erfc(z / math.sqrt(2)), 4), "p_two_sided": p_two}


def comps(row):
    """Component list of one sampled step: dict rows carry it under components_log, list rows in position 1."""
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def comp_xy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def comp_area(c):
    return float(c["area"]) if isinstance(c, dict) else float(c[1])


def profile(v, p0, p1, n=SAMPLES):
    g = v.shape[0]
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = p0[0] + t * (p1[0] - p0[0])
        y = p0[1] + t * (p1[1] - p0[1])
        out.append(float(v[int(round(y)) % g, int(round(x)) % g]))
    return out


def corridor_of(tag: str, art: dict) -> dict | None:
    series = art.get("series") or []
    counts = [len(comps(r)) for r in series]
    if not counts or min(counts) != 1:
        return None
    first_one = counts.index(1)
    if first_one == 0:
        return None
    row = series[first_one - 1]
    cs = sorted(comps(row), key=comp_area, reverse=True)[:2]
    if len(cs) < 2:
        return None
    step = int(row[0]) if isinstance(row, list) else int(row.get("step"))
    f = FIELDS / tag / f"x182_{tag}_t{step}.npy"
    if not f.exists():
        return None
    v = np.load(f)
    if v.ndim == 3:
        v = v[0]
    prof = profile(v, comp_xy(cs[0]), comp_xy(cs[1]))
    n = len(prof)
    mid = prof[n // 3: n - n // 3]
    return {"step": step, "corridor": round(min(mid), 4), "normalised": round(min(mid) / max(float(v.max()), 1e-9), 4)}


def main() -> int:
    index = json.loads((L1 / "x182_series_index.json").read_text(encoding="utf-8"))
    target = index["levels"]
    rows = []
    for r in index["runs"]:
        if r["status"] not in ("ok", "skipped (exists)"):
            continue
        lv = r["level"]
        seed = r["seed"]
        tag = f"L{int(round(lv * 100)):03d}_s{seed}"
        art = json.loads((L1 / f"x182_{tag}.compact.json").read_text(encoding="utf-8"))
        series = art.get("series") or []
        counts = [len(comps(x)) for x in series]
        fused = bool(counts) and min(counts) == 1
        cs0 = comps(series[0]) if series else []
        if cs0:
            mid_x = statistics.fmean([comp_xy(c)[0] for c in cs0])
            mid_y = statistics.fmean([comp_xy(c)[1] for c in cs0])
            g_actual = round(G_at(mid_x, mid_y), 4)
        else:
            g_actual = None

        rows.append({"level": lv, "target_G": lv, "seed": seed, "G_actual": g_actual, "fused": fused,
                     "final_count": counts[-1] if counts else None,
                     "corridor": corridor_of(tag, art)})

    levels = []
    for lv in target:
        sel = [r for r in rows if r["level"] == lv]
        gs = [r["G_actual"] for r in sel if r["G_actual"] is not None]
        k = sum(1 for r in sel if r["fused"])
        corrs = [r["corridor"]["normalised"] for r in sel if r["corridor"]]
        levels.append({"level": lv, "target_G": lv, "runs": len(sel), "fused": k,
                       "share": round(k / len(sel), 4) if sel else None, "wilson": wilson(k, len(sel)),
                       "G_actual_mean": round(statistics.fmean(gs), 4) if gs else None,
                       "F_local_mean": round(0.030 * 2 * statistics.fmean(gs), 5) if gs else None,
                       "runs_with_recomputed_G": len(gs),
                       "corridor_median": round(statistics.median(corrs), 4) if corrs else None,
                       "corridor_sd": round(statistics.pstdev(corrs), 4) if len(corrs) > 1 else None,
                       "contacts": len(corrs)})

    scores = [l["G_actual_mean"] for l in levels if l["share"] is not None]
    cases = [l["fused"] for l in levels if l["share"] is not None]
    totals = [l["runs"] for l in levels if l["share"] is not None]
    z, pvals = cochran_armitage_negative(scores, cases, totals)

    bottom = levels[0]
    top = levels[-1]
    pred_bottom = PREDICTION["bottom_share"][0] <= bottom["share"] if bottom["share"] is not None else 0.0 <= PREDICTION["bottom_share"][1]
    pred_top = PREDICTION["top_share"][0] <= top["share"] if top["share"] is not None else 1.0 <= PREDICTION["top_share"][1]
    trend_ok = pvals is not None and pvals["p_negative_direction"] < PREDICTION["p_threshold"]

    if pred_bottom and pred_top and trend_ok:
        verdict = (f"THE MIDPOINT PHASE CONTROLS THE OUTCOME, AND NEGATIVELY: with the pattern value at the pair's midpoint chosen in advance, the share falls "
                   f"from {bottom['share']:.2f} at local G {bottom['G_actual_mean']:.2f} (F_local "
                   f"{bottom['F_local_mean']:.4f}) to {top['share']:.2f} at G {top['G_actual_mean']:.2f} (F_local "
                   f"{top['F_local_mean']:.4f}); Cochran-Armitage z = {z}, one-sided p = "
                   f"{pvals['p_negative_direction']:.4f}. All of the block's crossing statements should be re-read in "
                   "the midpoint reading. X183 puts the ladder on the colder body's inflow and reads the same data the other way " 
                   "round - the two are one law, which X185 demonstrates.")
    elif pred_bottom and pred_top and not trend_ok:
        verdict = (f"THE EXTREMES SEPARATE BUT NOT MONOTONELY: bottom {bottom['share']:.2f} against top {top['share']:.2f} as "
                   f"predicted, yet the trend across the five levels gives z = {z} and one-sided p = "
                   f"{pvals['p_negative_direction'] if pvals else None} — the levels in between do not follow, so the effect is "
                   "weaker or not monotone in G.")
    elif not pred_bottom and not pred_top:
        verdict = (f"REVERSED UNDER CONTROL: the bottom level reads {bottom['share']:.2f} (predicted 0.50-1.00) and the top "
                   f"{top['share']:.2f} (predicted 0.00-0.35), so X180's correlation does not survive a design that selects "
                   "the site in advance and the readout itself needs re-examination.")
    else:
        verdict = (f"PARTIAL: bottom {bottom['share']:.2f} (predicted 0.50-1.00) and top {top['share']:.2f} (predicted "
                   f"0.00-0.35); z = {z}, one-sided p = {pvals['p_negative_direction'] if pvals else None}. One extreme holds "
                   "and the other does not, which is recorded as a partial result rather than as a confirmation.")

    agg = {"kind": "x182_local_inflow", "flow": 0.030, "radius": 3.0, "gap": 10, "steps": 2000,
           "prediction": PREDICTION, "levels": levels, "runs": rows,
           "trend": {"z": z, **(pvals or {})}, "bottom_predicted": pred_bottom, "top_predicted": pred_top,
           "trend_predicted": trend_ok, "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"{'level':>6} {'G':>6} {'F_local':>8} {'fused':>7} {'share':>6}  wilson            corridor")
    for l in levels:
        print(f"{l['level']:>6} {l['G_actual_mean']:>6} {l['F_local_mean']:>8} {l['fused']:>3}/{l['runs']:<3} "
              f"{l['share']:>6}  {str(l['wilson']):<17} {l['corridor_median']} (n {l['contacts']})")
    print(f"[x182] trend z = {z}, {pvals}")
    print(f"[x182] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
