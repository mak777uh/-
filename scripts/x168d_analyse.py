"""x168d_analyse.py — X168d: ten seeds per cell at surface gaps 11 and 8, three inflow rates.

Reports the gap-11 share per rate with a Wilson interval, Fisher's exact tests, an exact permutation test for an ORDERED trend
across the three rates, the gap-8 control both as a coalescence count and as a final-state count, and the power the design
actually has.

Corrections after the independent review of 04.11 (`lab/reviews/2026-11-04-x168d-review.md`):
  * `difference` used to subtract the two FLOW values instead of the two shares, so it read 0.01 and the "trend is real"
    branch was unreachable; it now subtracts the shares it names.
  * the ordered trend test is added: Fisher on the extreme pair answers a different question and gave p = 0.21 where the
    ordered test gives p = 0.0515 one-sided.
  * the design's power is reported as computed (15 % for a 0.3 difference at n = 10), because the pre-registration claimed
    80 % and that claim was wrong.
  * `min == 1` is reported for what it is - the two bodies coalesced at least once - with the end-of-run component counts
    alongside, since the field line's late-time count is 22-56 everywhere.

Writes morphogenesis/experiments/E09_pond/l1_field_x168d_gap11.json.
"""
from __future__ import annotations

import json
import math
import statistics
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x168d_gap11.json"
CONTROL_FLOOR = 0.9
X158_G11 = 2.0 / 15.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    return []


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def fisher(a: int, n1: int, b: int, n2: int) -> float:
    def hyp(x):
        return math.comb(n1, x) * math.comb(n2, a + b - x) / math.comb(n1 + n2, a + b)
    lo = max(0, a + b - n2)
    hi = min(n1, a + b)
    obs = hyp(a)
    return round(sum(hyp(x) for x in range(lo, hi + 1) if hyp(x) <= obs + 1e-12), 5)


def ordered_trend(sizes: list[int], counts: list[int]) -> dict:
    """Exact permutation test for a monotone trend in the fusion count across three ordered groups.

    Statistic: sum over fused runs of their group index (0, 1, 2). Under the null the fused runs are exchangeable, so the
    distribution is enumerated exactly over the placements of sum(counts) successes among sum(sizes) positions.
    """
    total = sum(sizes)
    k = sum(counts)
    labels = []
    for g, n in enumerate(sizes):
        labels.extend([g] * n)
    observed = sum(g for g, n in enumerate(counts) for _ in range(n))
    at_least = 0
    all_ = 0
    for chosen in combinations(range(total), k):
        stat = sum(labels[i] for i in chosen)
        all_ += 1
        if stat >= observed:
            at_least += 1
    return {"statistic": observed, "p_one_sided": round(at_least / all_, 5),
            "placements": all_, "note": "one-sided for an increasing trend"}


def power_two_proportions(p1: float, p2: float, n: int) -> float:
    """Exact power of the two-sided Fisher test at level 0.05 for two independent groups of n."""
    def hyp_table(a, na, b, nb):
        return math.comb(na, a) * math.comb(nb, b) / math.comb(na + nb, a + b)

    observed = [[a, n - a] for a in range(n + 1)]
    pvals = {}
    for a, row in enumerate(observed):
        for b in range(n + 1):
            pvals[(a, b)] = fisher(a, n, b, n)
    hit = 0.0
    for a in range(n + 1):
        pa = math.comb(n, a) * p1 ** a * (1 - p1) ** (n - a)
        for b in range(n + 1):
            if pvals[(a, b)] < 0.05:
                hit += pa * math.comb(n, b) * p2 ** b * (1 - p2) ** (n - b)
    return round(hit, 4)


def main() -> int:
    cells: dict[tuple[float, int], list[dict]] = {}
    for f in sorted(L1.glob("x168d_F*_g*_s9*.json")):
        if f.name.endswith(".compact.json"):
            continue
        parts = f.stem.split("_")
        flow = int(parts[1][1:]) / 1000.0
        gap = int(parts[2][1:])
        art = json.loads(f.read_text(encoding="utf-8"))
        series = art.get("series") or []
        counts = [row.get("components", len(comps(row))) for row in series]
        cells.setdefault((flow, gap), []).append({
            "run": f.stem, "min": min(counts) if counts else None,
            "final": counts[-1] if counts else None,
            "fused_at_least_once": bool(counts) and min(counts) == 1,
            "one_at_last_step": bool(counts) and counts[-1] == 1,
        })

    table = {}
    for (flow, gap), rows in sorted(cells.items()):
        fused = sum(1 for r in rows if r["fused_at_least_once"])
        died = sum(1 for r in rows if r["min"] == 0)
        one_last = sum(1 for r in rows if r["one_at_last_step"])
        table[f"F{flow:g}_g{gap}"] = {"flow": flow, "gap": gap, "runs": len(rows), "fused": fused, "died": died,
                                      "share": round(fused / len(rows), 4), "wilson": wilson(fused, len(rows)),
                                      "one_at_last_step": one_last,
                                      "final_counts": [r["final"] for r in rows],
                                      "mins": [r["min"] for r in rows]}

    def get(f, g):
        return table.get(f"F{f:g}_g{g}")

    rates = sorted({f for f, _ in cells})
    controls = {}
    for f in rates:
        c = get(f, 8)
        controls[f"{f:g}"] = (c is not None and c["share"] >= CONTROL_FLOOR)
    g11 = {f: get(f, 11) for f in rates}
    shares = {k: v["share"] for k, v in g11.items() if v}
    tests = {}
    for a, b in combinations(sorted(shares), 2):
        tests[f"{a}_vs_{b}"] = fisher(g11[a]["fused"], g11[a]["runs"], g11[b]["fused"], g11[b]["runs"])

    trend = None
    if len(g11) >= 2:
        keys = sorted(g11)
        trend = ordered_trend([g11[k]["runs"] for k in keys], [g11[k]["fused"] for k in keys])

    extreme = None
    if len(shares) >= 2:
        lo = min(shares, key=lambda k: shares[k])
        hi = max(shares, key=lambda k: shares[k])
        extreme = {"contrast": f"{lo} (0/{g11[lo]['runs']} would be 0 %) vs {hi}", "low_rate": lo, "high_rate": hi,
                   "difference": round(shares[hi] - shares[lo], 4),
                   "fisher_p": fisher(g11[lo]["fused"], g11[lo]["runs"], g11[hi]["fused"], g11[hi]["runs"])}

    n = g11[sorted(g11)[0]]["runs"] if g11 else 10
    power = {"n_per_rate": n, "level": 0.05,
             "for_0.0_vs_0.3": power_two_proportions(0.0, 0.3, n),
             "for_0.0_vs_0.4": power_two_proportions(0.0, 0.4, n),
             "for_0.2_vs_0.5": power_two_proportions(0.2, 0.5, n)}
    saturated = all(v["share"] in (0.0, 1.0) for v in g11.values() if v)
    readout_ok = not saturated and len(shares) >= 2
    end_counts = [c for v in g11.values() for c in v["final_counts"]]

    if not all(controls.values()):
        verdict = ("NOT COMPARABLE: the gap-8 control failed at " +
                   ", ".join(f"F = {k}" for k, ok in controls.items() if not ok) + ", so those arms are dropped.")
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the gap-11 readout is saturated at 0 or 1 in every rate."
    elif trend and trend["p_one_sided"] < 0.05 and extreme and extreme["difference"] >= 0.3:
        verdict = ("AN INCREASING TREND: the gap-11 share runs " +
                   ", ".join(f"{v:.0%} at F = {k}" for k, v in shares.items()) +
                   f", a difference of {extreme['difference']:.0%} between the extreme rates, ordered-trend p = "
                   f"{trend['p_one_sided']} one-sided; the crossing depends on the inflow rate and §4.1 needs the curve.")
    else:
        verdict = ("NO TREND DETECTED, AND THE DESIGN COULD NOT HAVE FOUND A SMALL ONE: with ten seeds per rate the gap-11 "
                   "share runs " + ", ".join(f"{v:.0%} at F = {k}" for k, v in shares.items()) +
                   f" (X158 at F = 0.030: {X158_G11:.0%}), a difference of {extreme['difference']:.0%} between the extreme "
                   f"rates with Fisher p = {extreme['fisher_p']} and an exact ordered-trend p = {trend['p_one_sided']} "
                   f"one-sided. A 0.3 difference at this sample size would have been detected only {power['for_0.0_vs_0.3']:.0%} "
                   f"of the time and a 0.4 difference {power['for_0.0_vs_0.4']:.0%}, so the flat result rules out nothing "
                   "larger than about 0.4 and the insensitivity of the crossing stands as 'no dependence detected in a narrow "
                   "range', not as a measured absence.")

    agg = {"kind": "x168d_gap11", "conversion": "surface gap g -> SEP = 2R + g",
           "readout_note": ("'fused' is min(component count) == 1 over the run, i.e. the two bodies coalesced at least once; "
                            "one_at_last_step is reported separately because the field line's late-time component count is "
                            "22-56 in every run, so 'one body at the end' is not what this measure reads"),
           "by_cell": table, "shares_gap11": shares, "fisher_tests": tests, "ordered_trend": trend,
           "extreme_contrast": extreme, "power": power, "x158_gap11_baseline": round(X158_G11, 4),
           "end_component_counts": {"min": min(end_counts) if end_counts else None,
                                    "max": max(end_counts) if end_counts else None},
           "controls": {"gap8_fires_everywhere": all(controls.values()), "per_rate": controls},
           "corrections": ("difference now subtracts shares rather than flow values; the ordered-trend test and the computed "
                           "power are added; the pre-registration's 80 % power claim was wrong and is reported as such above"),
           "verdict": verdict}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for key, c in sorted(table.items()):
        print(f"[x168d] {key}: runs {c['runs']} fused {c['fused']} died {c['died']} one_at_end {c['one_at_last_step']} "
              f"share {c['share']} wilson {c['wilson']}")
    print(f"[x168d] fisher {tests}")
    print(f"[x168d] ordered trend {trend}")
    print(f"[x168d] extreme {extreme}")
    print(f"[x168d] power {power}")
    print(f"[x168d] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
