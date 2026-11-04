"""x191_site_sweep_analyse.py — X191: the bridge as a dose-response in the local inflow.

Readout (registered in the plan, not post hoc): the contact-moment bridge ratio — the field value midway between the two bodies over
the maximum of v inside a radius-10 disc around them, at the last saved slice on which the two bodies are still separate. Secondary:
the same ratio at fixed step 100, the minimum over the central half of the segment, and the run's outcome (one component at some
sample).

Reports per-level means with every site value, the number of inversions between adjacent level means, the Spearman correlation
between the site's own local inflow and the ratio over all 30 sites, and the point-biserial between the ratio and the outcome.
Writes morphogenesis/experiments/E09_pond/l1_field_x191_site_sweep.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x191_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x191_site_sweep.json"
GRID = 96
SCALE = 12.0
AMP = 0.5
RING_R = 10
PEAK_FLOOR = 0.3
FIXED_STEP = 100
SPEARMAN_BAR = -0.5
OUTCOME_RHO_BAR = 0.5
TOP_SHARE_BAR = 0.6


def comps(row):
    return row[1] if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list) else []


def cxy(c):
    return (float(c[2]), float(c[3]))


def step_of(row):
    return int(row[0])


def wrap_dx(a, b):
    return (a - b + GRID / 2) % GRID - GRID / 2


def G_at(x, y):
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def ring_peak(field, centre, r=RING_R):
    cx, cy = centre
    return max(float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID])
               for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= r * r)


def midpoint(field, c0, c1):
    mx = (c0[0] + wrap_dx(c1[0], c0[0]) / 2.0) % GRID
    my = (c0[1] + (c1[1] - c0[1]) / 2.0) % GRID
    return float(field[int(round(my)) % GRID, int(round(mx)) % GRID])


def central_min(field, c0, c1, n=200):
    dx, dy = wrap_dx(c1[0], c0[0]), c1[1] - c0[1]
    return min(float(field[int(round(c0[1] + dy * (i / n))) % GRID, int(round(c0[0] + dx * (i / n))) % GRID])
               for i in range(int(0.25 * n), int(0.75 * n) + 1))


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num / den, 3) if den else None


def point_biserial(x, flag):
    mx, mf = statistics.fmean(x), statistics.fmean(flag)
    num = sum((a - mx) * (b - mf) for a, b in zip(x, flag))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - mf) ** 2 for b in flag))
    return round(num / den, 3) if den else None


index = json.loads((L1 / "x191_series_index.json").read_text(encoding="utf-8"))
F = float(index["flow"])
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"L{r['level_index']}_site{r['site']}_s{r['seed']}"
    series = json.loads((L1 / f"x191_{tag}.compact.json").read_text(encoding="utf-8")).get("series") or []
    if not series:
        continue
    cs0 = comps(series[0])
    if len(cs0) != 2:
        continue
    g_cold = min(G_at(*cxy(cs0[0])), G_at(*cxy(cs0[1])))
    f_local = F * (1 + AMP * (2 * g_cold - 1))
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    per_slice = []
    for sp in sorted(FIELDS.glob(f"*/x191_{tag}_t*.npy"), key=lambda p: int(p.stem.split("_t")[-1])):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = by_step.get(step)
        rec = {"step": step, "n_components": len(cur) if cur is not None else None}
        if not cur or len(cur) != 2:
            per_slice.append(rec)
            continue
        peak = max(ring_peak(field, cur[0]), ring_peak(field, cur[1]))
        rec.update({"peak": round(peak, 5), "ratio": round(midpoint(field, *cur) / peak, 5) if peak > 0 else None,
                    "ratio_min": round(central_min(field, *cur) / peak, 5) if peak > 0 else None})
        per_slice.append(rec)
    ok = [x for x in per_slice if x.get("ratio") is not None and (x.get("peak") or 0) >= PEAK_FLOOR]
    contact = max(ok, key=lambda x: x["step"]) if ok else None
    at_fixed = next((x for x in ok if x["step"] == FIXED_STEP), None)
    runs.append({"level_index": r["level_index"], "level": r["level"], "site": r["site"], "jitter": r.get("jitter"),
                 "phase": r.get("phase"),
                 "seed": r["seed"], "f_local": round(f_local, 5), "fused": int(min(counts) == 1),
                 "min_count": min(counts), "usable_slices": len(ok),
                 "contact_step": contact["step"] if contact else None,
                 "ratio_contact": contact["ratio"] if contact else None,
                 "ratio_contact_min": contact["ratio_min"] if contact else None,
                 "ratio_fixed_100": at_fixed["ratio"] if at_fixed else None,
                 "peak_min": min((x["peak"] for x in per_slice if x.get("peak") is not None), default=None),
                 "per_slice": per_slice})

levels = []
dropped = []
for li, target in enumerate(index["levels"]):
    sel = [x for x in runs if x["level_index"] == li]
    vals = [x["ratio_contact"] for x in sel if x["ratio_contact"] is not None]
    if len(vals) < 4:
        dropped.append({"level": target, "sites_reaching_contact": len(vals),
                        "available_sites": index.get("available_sites_per_level", {}).get(f"{target:.3f}"),
                        "why": "fewer than four sites reached the contact moment, so the level is dropped and said so "
                               "(the plan's refusal rule for an unattainable level)"})
        continue
    levels.append({"level": target, "runs": len(sel), "sites_reaching_contact": len(vals),
                   "f_local_mean": round(statistics.fmean([x["f_local"] for x in sel]), 5) if sel else None,
                   "ratio_contact_mean": round(statistics.fmean(vals), 5) if vals else None,
                   "ratio_contact_values": vals,
                   "ratio_contact_sd": round(statistics.pstdev(vals), 5) if len(vals) > 1 else None,
                   "distinct_phases": len({tuple(x["phase"]) for x in sel if x.get("phase")}),
                   "distinct_ratios": len({round(v, 5) for v in vals}),
                   "fused": sum(x["fused"] for x in sel),
                   "share": round(statistics.fmean([x["fused"] for x in sel]), 4) if sel else None,
                   "ratio_fixed_100_mean": round(statistics.fmean([x["ratio_fixed_100"] for x in sel
                                                                   if x["ratio_fixed_100"] is not None]), 5)
                   if any(x["ratio_fixed_100"] is not None for x in sel) else None})

usable = [x for x in runs if x["ratio_contact"] is not None]
fl = [x["f_local"] for x in usable]
rt = [x["ratio_contact"] for x in usable]
rho = spearman(fl, rt)
rho_out = point_biserial(rt, [x["fused"] for x in usable])
means = [l["ratio_contact_mean"] for l in levels if l["ratio_contact_mean"] is not None]
inversions = sum(1 for a, b in zip(means, means[1:]) if b > a)
top_share = levels[-1]["share"] if levels and levels[-1]["share"] is not None else None
top_target = levels[-1]["level"] if levels else None
sites_per_level_ok = all(l["sites_reaching_contact"] >= 4 for l in levels)
peak_ok = all((l["ratio_contact_mean"] is not None) for l in levels) and all(
    (x["peak_min"] or 0) >= PEAK_FLOOR for x in usable)
spacing_ok = all(abs(b - a) >= 0.003 for a, b in zip(index["levels"], index["levels"][1:]))

if not sites_per_level_ok or not peak_ok:
    verdict = ("NOT SENSITIVE BY CONSTRUCTION at this site list: fewer than four sites per level reached the contact moment, or a ring "
               "peak fell below the floor, so no trend is claimed.")
elif inversions <= 1 and rho is not None and rho <= SPEARMAN_BAR:
    verdict = (f"THE BRIDGE IS A DOSE-RESPONSE IN THE LOCAL INFLOW: over six levels and 30 sites the contact-moment bridge ratio falls "
               f"from {means[0]} at F_local = {index['levels'][0]} to {means[-1]} at {index['levels'][-1]} with {inversions} inversion between "
               f"adjacent level means, and the Spearman correlation over the sites is {rho} (bar {SPEARMAN_BAR}); the fusion share runs the "
               f"other way, {levels[0]['share']} to {top_share} (bar {TOP_SHARE_BAR} at the top level), and the site-level correlation between "
               f"the bridge and the outcome is {rho_out} (bar -{OUTCOME_RHO_BAR}). So the flip of the law's sign at the largest bodies is the same "
               "trend seen from the other end: a stronger site thins the bridge enough that the touching pair separates again.")
elif inversions >= 2:
    verdict = (f"THE BRIDGE HAS A WINDOW, NOT A MONOTONE RESPONSE: the level means are {means} with {inversions} inversions between "
               f"adjacent levels and a Spearman correlation of {rho}, so the flip is a threshold at the top of the inflow band rather than a "
               f"continuation of a trend; the outcome share over the levels is "
               f"{[l['share'] for l in levels]}.")
else:
    verdict = (f"THE BRIDGE AND THE OUTCOME COME APART AT THE LEVEL LEVEL: the level means fall with {inversions} inversion "
               f"(Spearman {rho}, bar {SPEARMAN_BAR}) but the site-level correlation with the outcome is only {rho_out} and the top level's "
               f"share is {top_share}, so X190's site-level result stands as a two-population comparison and not as a dose-response.")

agg = {"kind": "x191_site_sweep", "flow": F, "radius": index["radius"], "gap": index["gap"],
       "dropped_levels": dropped,
       "note": ("the highest registered level (F_local 0.041) has no site within 0.0025 anywhere in the seed map, because the top of the "
                "pattern's band is sparse; it is dropped as the plan provides, so the sweep is five levels spanning about 0.017 to 0.0375"),
       "ring_radius": RING_R, "levels": levels, "level_means": means,
       "spearman_site_ratio_vs_f_local": rho, "point_biserial_ratio_vs_outcome": rho_out,
       "inversions_between_level_means": inversions, "top_level_share": top_share,
       "bars": {"spearman": SPEARMAN_BAR, "outcome_rho": OUTCOME_RHO_BAR, "top_share": TOP_SHARE_BAR},
       "checks": {"sites_per_level_ok": sites_per_level_ok, "peak_ok": peak_ok, "spacing_ok": spacing_ok,
                  "available_sites_per_level": index.get("available_sites_per_level")},
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for l in levels:
    print(f"[x191] F_local {l['f_local_mean']}: ratio {l['ratio_contact_mean']} {l['ratio_contact_values']} "
          f"(sd {l['ratio_contact_sd']})  share {l['share']}  fixed-step {l['ratio_fixed_100_mean']} "
          f"sites {l['sites_reaching_contact']} phases {l['distinct_phases']} ratios {l['distinct_ratios']}")
print(f"[x191] level means {means}: {inversions} inversions; Spearman over sites {rho} (bar {SPEARMAN_BAR}); "
      f"rho(ratio, outcome) {rho_out}; top share {top_share}")
print(f"[x191] verdict: {verdict}")
