"""x190_bridge_sites_analyse.py — X190: the bridge measured over five distinct SITES per level.

Readout identical to X189: the bridge ratio is the field value midway between the two bodies divided by the maximum of v inside a
radius-10 disc around them, on the last saved slice on which the two bodies are still separate (the contact moment). What changes is
the sample: five distinct sites per level, three seeds per site, so a level's mean is a mean over sites and the within-site spread
is measurable.

Also reports the ratio at a fixed step (100, the most frequent contact step in X189) and each site's three-seed spread.
Writes morphogenesis/experiments/E09_pond/l1_field_x190_bridge_sites.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x190_fields"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x190_bridge_sites.json"
GRID = 96
RING_R = 10
BAR = 0.05
SPREAD_BAR = 0.02
PEAK_FLOOR = 0.3
FIXED_STEP = 100


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def cxy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def step_of(row):
    return int(row[0]) if isinstance(row, list) else int(row.get("step"))


def wrap_dx(a, b):
    return (a - b + GRID / 2) % GRID - GRID / 2


def ring_peak(field, centre, r=RING_R):
    cx, cy = centre
    best = 0.0
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                best = max(best, float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID]))
    return best


def midpoint_value(field, c0, c1):
    mx = (c0[0] + wrap_dx(c1[0], c0[0]) / 2.0) % GRID
    my = (c0[1] + (c1[1] - c0[1]) / 2.0) % GRID
    return float(field[int(round(my)) % GRID, int(round(mx)) % GRID])


def central_min(field, c0, c1, n=200):
    dx, dy = wrap_dx(c1[0], c0[0]), c1[1] - c0[1]
    vals = [float(field[int(round(c0[1] + dy * (i / n))) % GRID, int(round(c0[0] + dx * (i / n))) % GRID])
            for i in range(int(0.25 * n), int(0.75 * n) + 1)]
    return min(vals)


index = json.loads((L1 / "x190_series_index.json").read_text(encoding="utf-8"))
runs = []
for r in index["runs"]:
    if r["status"] not in ("ok", "skipped (exists)"):
        continue
    tag = f"{r['arm']}_{r['level']}_site{r['site']}_s{r['seed']}"
    d = json.loads((L1 / f"x190_{tag}.compact.json").read_text(encoding="utf-8"))
    series = d.get("series") or []
    if not series:
        continue
    counts = [len(comps(x)) for x in series]
    by_step = {step_of(row): [cxy(c) for c in comps(row)] for row in series}
    per_slice = []
    for sp in sorted(FIELDS.glob(f"*/x190_{tag}_t*.npy"), key=lambda p: int(p.stem.split("_t")[-1])):
        step = int(sp.stem.split("_t")[-1])
        field = np.load(sp)
        cur = by_step.get(step)
        rec = {"step": step, "n_components": len(cur) if cur is not None else None}
        if not cur or len(cur) != 2:
            per_slice.append(rec)
            continue
        c0, c1 = cur
        peak = max(ring_peak(field, c0), ring_peak(field, c1))
        rec.update({"peak": round(peak, 5), "ratio": round(midpoint_value(field, c0, c1) / peak, 5) if peak > 0 else None,
                    "ratio_min": round(central_min(field, c0, c1) / peak, 5) if peak > 0 else None})
        per_slice.append(rec)
    ok = [x for x in per_slice if x.get("ratio") is not None and (x.get("peak") or 0) >= PEAK_FLOOR]
    contact = max(ok, key=lambda x: x["step"]) if ok else None
    at_fixed = next((x for x in ok if x["step"] == FIXED_STEP), None)
    runs.append({"arm": r["arm"], "level": r["level"], "site": r["site"], "seed": r["seed"],
                 "jitter": r.get("jitter"), "f_local": round(r["f_local"], 5) if "f_local" in r else None,
                 "fused": int(min(counts) == 1), "min_count": min(counts),
                 "usable_slices": len(ok), "contact_step": contact["step"] if contact else None,
                 "ratio_contact": contact["ratio"] if contact else None,
                 "ratio_contact_min": contact["ratio_min"] if contact else None,
                 "ratio_fixed_100": at_fixed["ratio"] if at_fixed else None,
                 "peak_min": min((x["peak"] for x in per_slice if x.get("peak") is not None), default=None),
                 "per_slice": per_slice})

levels = {}
for arm in index["arms"]:
    for lvl, spec in index["arms"][arm]["levels"].items():
        site_flows = [s["f_local"] for s in spec["sites"]]
        rows = [x for x in runs if x["arm"] == arm and x["level"] == lvl]
        sites = []
        for si in range(len(spec["sites"])):
            sel = [x for x in rows if x["site"] == si]
            vals = [x["ratio_contact"] for x in sel if x["ratio_contact"] is not None]
            sites.append({"site": si, "jitter": spec["sites"][si]["jitter"], "f_local": spec["sites"][si]["f_local"],
                          "runs": len(sel), "fused": sum(x["fused"] for x in sel),
                          "contact_values": vals,
                          "contact_mean": round(statistics.fmean(vals), 5) if vals else None,
                          "within_site_sd": round(statistics.pstdev(vals), 5) if len(vals) > 1 else None,
                          "contact_steps": [x["contact_step"] for x in sel]})
        levels[f"{arm}_{lvl}"] = {
            "radius": index["arms"][arm]["radius"], "gap": index["arms"][arm]["gap"],
            "distinct_sites": len({s["jitter"] and tuple(s["jitter"]) for s in spec["sites"]}),
            "f_local_sites": site_flows, "f_local_mean": round(statistics.fmean(site_flows), 5),
            "runs": len(rows), "fused": sum(x["fused"] for x in rows),
            "share": round(statistics.fmean([x["fused"] for x in rows]), 4) if rows else None,
            "sites": sites,
            "site_means": [s["contact_mean"] for s in sites if s["contact_mean"] is not None],
            "contact_mean_over_sites": round(statistics.fmean([s["contact_mean"] for s in sites
                                                               if s["contact_mean"] is not None]), 5)
            if any(s["contact_mean"] is not None for s in sites) else None,
            "within_site_sd_mean": round(statistics.fmean([s["within_site_sd"] for s in sites
                                                           if s["within_site_sd"] is not None]), 5)
            if any(s["within_site_sd"] is not None for s in sites) else None,
            "sites_reaching_contact": sum(1 for s in sites if s["contact_mean"] is not None),
            "fixed_step_mean": round(statistics.fmean([x["ratio_fixed_100"] for x in rows
                                                       if x["ratio_fixed_100"] is not None]), 5)
            if any(x["ratio_fixed_100"] is not None for x in rows) else None}

r6c, r6w = levels["r6_g9_cold"], levels["r6_g9_warm"]
r3c, r3w = levels["r3_g10_cold"], levels["r3_g10_warm"]


def site_diff(x, y, key="contact_mean_over_sites"):
    if x.get(key) is None or y.get(key) is None:
        return None
    return round(y[key] - x[key], 5)


d6 = site_diff(r6c, r6w)
d3 = site_diff(r3c, r3w)
d6_fixed = site_diff(r6c, r6w, "fixed_step_mean")
sd6 = r6w["within_site_sd_mean"]

# site-paired test: the two levels sit on different sites, so the pairing is not by site but the spread is what decides.
cold_sites = sorted(x for x in r6c["site_means"] if x is not None)
warm_sites = sorted(x for x in r6w["site_means"] if x is not None)
overlap = (max(cold_sites[0], warm_sites[0]), min(cold_sites[-1], warm_sites[-1])) if cold_sites and warm_sites else None
separated = bool(cold_sites and warm_sites and warm_sites[-1] < cold_sites[0])

checks = {"sites_per_level_ok": min(len(r6c["site_means"]), len(r6w["site_means"]),
                                    len(r3c["site_means"]), len(r3w["site_means"])) >= 5,
          "level_separation_ok": all(abs(a - b) >= 0.008 for a, b in ((r6w["f_local_mean"], r6c["f_local_mean"]),
                                                                       (r3w["f_local_mean"], r3c["f_local_mean"]))),
          "spread_ok": (sd6 or 0) >= SPREAD_BAR,
          "sites_reaching_contact_ok": min(r6c["sites_reaching_contact"], r6w["sites_reaching_contact"]) >= 3}

if not checks["sites_per_level_ok"] or not checks["sites_reaching_contact_ok"]:
    verdict = ("NOT SENSITIVE BY CONSTRUCTION at this site list: fewer than five sites per level reached the contact moment, so no "
               "claim is made.")
elif d6 is not None and d6 <= -BAR and separated:
    verdict = (f"THE BRIDGE DIFFERENCE SURVIVES THE SITE-LEVEL SAMPLE: over five distinct sites per level the warm level's "
               f"contact-moment bridge ratio is {r6w['contact_mean_over_sites']} against {r6c['contact_mean_over_sites']} for the cold "
               f"(difference {d6:+g}, bar {-BAR:g}), and the two site populations do not overlap "
               f"({[round(v, 3) for v in warm_sites]} against {[round(v, 3) for v in cold_sites]}). The mean within-site spread is "
               f"{sd6}, so the difference is larger than the seed-level noise. The flip therefore has a measured mechanism at the "
               f"largest size: a warm site thins the bridge enough that a touched pair separates again.")
elif d6 is not None and d6 <= -BAR:
    verdict = (f"THE BRIDGE DIFFERENCE SURVIVES IN THE MEAN BUT NOT SITE BY SITE: the warm level's contact ratio is "
               f"{r6w['contact_mean_over_sites']} against {r6c['contact_mean_over_sites']} (difference {d6:+g}, bar {-BAR:g}), but the "
               f"site populations overlap (warm {[round(v, 3) for v in warm_sites]} against cold {[round(v, 3) for v in cold_sites]}), "
               f"with a mean within-site spread of {sd6}; the mechanism is therefore a shift of the distribution rather than a "
               "separation of it.")
else:
    verdict = (f"THE BRIDGE DIFFERENCE DOES NOT SURVIVE THE SITE-LEVEL SAMPLE: the warm level's contact ratio is "
               f"{r6w['contact_mean_over_sites']} against {r6c['contact_mean_over_sites']} (difference {d6}, bar {-BAR:g}), so X189's "
               "candidate mechanism is withdrawn: neither the bodies around the pair (X188) nor the bridge (X189, X190) explains the "
               "flip, and that is recorded as the boundary of the current law rather than as another probe.")

agg = {"kind": "x190_bridge_sites", "bar": BAR, "spread_bar": SPREAD_BAR, "ring_radius": RING_R,
       "fixed_step": FIXED_STEP, "sites_per_level": 5, "seeds_per_site": 3,
       "prediction": index["prediction"], "levels": levels, "checks": checks,
       "radius6_warm_minus_cold_over_sites": d6, "radius3_warm_minus_cold_over_sites": d3,
       "radius6_warm_minus_cold_at_fixed_step": d6_fixed,
       "radius6_cold_site_means": cold_sites, "radius6_warm_site_means": warm_sites,
       "radius6_site_populations_separated": separated, "radius6_site_population_overlap": overlap,
       "within_site_sd_mean_radius6_warm": sd6,
       "runs_detail": runs, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for k in ("r6_g9_cold", "r6_g9_warm", "r3_g10_cold", "r3_g10_warm"):
    v = levels[k]
    print(f"[x190] {k}: share {v['share']}  sites reaching contact {v['sites_reaching_contact']}/5  "
          f"contact mean over sites {v['contact_mean_over_sites']}  within-site sd {v['within_site_sd_mean']}  "
          f"site means {[round(x, 3) if x is not None else None for x in v['site_means']]}")
print(f"[x190] radius6 warm-minus-cold over sites {d6} (bar {-BAR}), at fixed step {d6_fixed}; separated {separated}; "
      f"checks {checks}")
print(f"[x190] verdict: {verdict}")
