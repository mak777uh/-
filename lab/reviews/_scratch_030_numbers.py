#!/usr/bin/env python
"""_scratch_030_numbers.py — reviewer's INDEPENDENT recomputation for task-3.

Written for lab/reviews/2026-11-04-030-numbers.md. It re-derives the six groups of
headline numbers from the raw artifacts and NEVER imports the lab's analysis code
(scripts/x19*_analyse.py, x194_phase_clusters.py, x197_deviance_worlds.py). Only the
raw artifacts are read: the E09_pond aggregates and the compact per-world slices in
morphogenesis/experiments/L1_field/. The bridge ratios are re-derived from the saved
field arrays in _hourly/x19*_fields/ (untracked, local only) with an independently
written midpoint/ring-peak implementation.

Run from the repository root:  python lab/reviews/_scratch_030_numbers.py [sections]
Sections: x192 x193 x195 x196 x194 x197 (default: all)
"""
from __future__ import annotations

import glob
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
HOURLY = ROOT / "_hourly"
GRID = 96
SCALE = 12.0
AMP = 0.5
RING_R = 10
PEAK_FLOOR = 0.3


# ---------------------------------------------------------------- helpers (own) --
def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def centroid(c):
    if isinstance(c, dict):
        return (float(c.get("cx", 0.0)), float(c.get("cy", 0.0)))
    return (float(c[2]), float(c[3]))


def step_of(row):
    return int(row[0])


def wrap_dx(a, b):
    return (a - b + GRID / 2) % GRID - GRID / 2


def G_at(x, y):
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def f_local_of(F, g):
    return F * (1.0 + AMP * (2.0 * g - 1.0))


def ring_peak(field, centre, r=RING_R):
    """Own reimplementation of 'peak over a radius-10 disc' (integer grid, wraparound)."""
    cx, cy = centre
    best = -1.0
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                v = float(field[int(round(cy + dy)) % GRID, int(round(cx + dx)) % GRID])
                if v > best:
                    best = v
    return best


def midpoint_val(field, c0, c1):
    """Own reimplementation of 'field at the midpoint of the two blobs'."""
    mx = (c0[0] + wrap_dx(c1[0], c0[0]) / 2.0) % GRID
    my = (c0[1] + (c1[1] - c0[1]) / 2.0) % GRID
    return float(field[int(round(my)) % GRID, int(round(mx)) % GRID])


def avg_rank(v):
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


def spearman(x, y):
    rx, ry = avg_rank(x), avg_rank(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num / den, 3) if den else None


def fisher_greater(a, b, c, d):
    """One-sided exact p that a/(a+b) > c/(c+d); returns the unrounded p."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    if not n or not r1 or not r2 or not c1:
        return 1.0
    p_obs = comb(r1, a) * comb(r2, c1 - a) / comb(n, c1)
    p = 0.0
    for x in range(a, min(r1, c1) + 1):
        if 0 <= c1 - x <= r2:
            pr = comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
            if pr <= p_obs + 1e-12:
                p += pr
    return p


def logistic(x, y):
    """Own two-parameter logistic fused ~ a + b*ratio, Newton/IRLS, returns b, se, z."""
    X = np.column_stack([np.ones(len(x)), np.array(x, dtype=float)])
    yv = np.array(y, dtype=float)
    beta = np.zeros(2)
    for _ in range(100):
        eta = X @ beta
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-9, None)
        z = eta + (yv - p) / w
        beta_new = np.linalg.solve(X.T @ (w[:, None] * X), X.T @ (w * z))
        if np.max(np.abs(beta_new - beta)) < 1e-12:
            beta = beta_new
            break
        beta = beta_new
    p = 1.0 / (1.0 + np.exp(-(X @ beta)))
    w = np.clip(p * (1 - p), 1e-9, None)
    cov = np.linalg.inv(X.T @ (w[:, None] * X))
    se = float(math.sqrt(cov[1, 1]))
    return round(float(beta[1]), 3), round(se, 3), round(float(beta[1] / se), 2) if se else None


def auc(values, flags):
    pos = [v for v, f in zip(values, flags) if f]
    neg = [v for v, f in zip(values, flags) if not f]
    if not pos or not neg:
        return None
    r = avg_rank(list(values))
    r1 = sum(r[i] for i in range(len(values)) if flags[i])
    u = r1 - len(pos) * (len(pos) + 1) / 2.0
    return round(u / (len(pos) * len(neg)), 5)


def pr(label, value):
    print(f"  {label:<52} {value}")


def hdr(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


# --------------------------------------------- field-backed census recomputation --
def load_runs(family: str):
    """Recompute f_local / fused for every compact slice of one x19* family, plus the
    contact ratio re-derived from the saved fields (when present)."""
    files = sorted(L1.glob(f"{family}_*.compact.json"))
    # index the saved fields once: <family>_<tag>_t<step>.npy
    field_files = defaultdict(list)
    for p in (HOURLY / f"{family}_fields").rglob(f"{family}_*_t*.npy"):
        stem = p.stem
        t = stem.rsplit("_t", 1)[0]
        field_files[t.replace(family + "_", "", 1)].append(p)
    out = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        series = d.get("series") or []
        params = d.get("params") or {}
        if len(series) < 1:
            continue
        first = comps(series[0])
        if len(first) != 2:
            continue
        F = float(params.get("F", 0.0))
        c0, c1 = centroid(first[0]), centroid(first[1])
        g_cold = min(G_at(*c0), G_at(*c1))
        counts = [len(comps(x)) for x in series]
        by_step = {step_of(row): [centroid(c) for c in comps(row)] for row in series}
        tag = f.stem.replace(".compact", "").replace(family + "_", "")
        per_slice = []
        for sp in sorted(field_files.get(tag, []), key=lambda p: int(p.stem.split("_t")[-1])):
            step = int(sp.stem.split("_t")[-1])
            field = np.load(sp)
            cur = by_step.get(step)
            if not cur or len(cur) != 2:
                continue
            peak = max(ring_peak(field, cur[0]), ring_peak(field, cur[1]))
            ratio = round(midpoint_val(field, *cur) / peak, 5) if peak > 0 else None
            if ratio is not None and peak >= PEAK_FLOOR:
                per_slice.append({"step": step, "ratio": ratio, "peak": peak})
        contact = max(per_slice, key=lambda x: x["step"]) if per_slice else None
        out.append({"tag": tag, "f_local": f_local_of(F, g_cold),
                    "fused": int(min(counts) == 1), "min_count": min(counts),
                    "ratio_contact": contact["ratio"] if contact else None,
                    "contact_step": contact["step"] if contact else None,
                    "usable_slices": len(per_slice)})
    return out


def value_table(runs, key="f_local"):
    by_value = defaultdict(list)
    for r in runs:
        by_value[round(r[key], 5)].append(r)
    values = []
    for v in sorted(by_value):
        sel = by_value[v]
        ratios = sorted(x["ratio_contact"] for x in sel if x["ratio_contact"] is not None)
        values.append({"f_local": v, "classes": len(sel), "classes_with_contact": len(ratios),
                       "fused": sum(x["fused"] for x in sel),
                       "share": round(statistics.fmean([x["fused"] for x in sel]), 4),
                       "ratio_values": ratios,
                       "ratio_min": ratios[0] if ratios else None,
                       "ratio_max": ratios[-1] if ratios else None,
                       "ratio_spread": round(ratios[-1] - ratios[0], 5) if len(ratios) > 1 else None,
                       "ratio_mean": round(statistics.fmean(ratios), 5) if ratios else None})
    return values


def census_report(family, agg_name, sections):
    hdr(f"[RECOMP] {agg_name}  (family {family})")
    agg = json.loads((POND / f"l1_field_{agg_name}.json").read_text(encoding="utf-8"))
    runs = load_runs(family)
    values = value_table(runs)
    usable = [x for x in runs if x["ratio_contact"] is not None]
    crowd = max(values, key=lambda v: v["classes_with_contact"])
    cr = [x for x in runs if round(x["f_local"], 5) == crowd["f_local"] and x["ratio_contact"] is not None]
    med = statistics.median([x["ratio_contact"] for x in cr])
    above = [x for x in cr if x["ratio_contact"] > med]
    below = [x for x in cr if x["ratio_contact"] <= med]
    a_f, b_f = sum(x["fused"] for x in above), sum(x["fused"] for x in below)
    p = fisher_greater(a_f, len(above) - a_f, b_f, len(below) - b_f)
    rho_c = spearman([round(x["f_local"], 5) for x in usable], [x["ratio_contact"] for x in usable])
    means = [v for v in values if v["ratio_mean"] is not None]
    rho_v = spearman([v["f_local"] for v in means], [v["ratio_mean"] for v in means])
    slope, se, z = logistic([x["ratio_contact"] for x in usable], [x["fused"] for x in usable])
    print("  AGG stored: classes=%s values=%d crowded=%s spread=%s contrast=%s fish=%s "
          "rho_c=%s rho_v=%s slope=%s/%s/%s" % (
              agg["classes"], len(agg["values"]), agg["crowded_value_contrast"]["f_local"],
              agg["registered_criteria"]["phase_spread_at_crowded_value"]["spread"],
              agg["crowded_value_contrast"]["difference"], agg["crowded_value_contrast"]["fisher_p"],
              agg["spearman_ratio_vs_inflow_classes"], agg["spearman_ratio_vs_inflow_value_means"],
              agg["logistic_slope_fusion_on_ratio"]["slope"], agg["logistic_slope_fusion_on_ratio"]["se"],
              agg["logistic_slope_fusion_on_ratio"]["z"]))
    pr("classes (runs)", len(runs))
    pr("distinct f_local values", len(values))
    pr("max classes at one value", max(v["classes"] for v in values))
    pr("crowded value / classes with contact", (crowd["f_local"], crowd["classes_with_contact"]))
    pr("ratio min-max / spread at crowded value", (crowd["ratio_min"], crowd["ratio_max"], crowd["ratio_spread"]))
    pr("median ratio at crowded value", round(med, 5))
    pr("above: n / fused / share", (len(above), a_f, round(a_f / len(above), 4) if above else None))
    pr("below: n / fused / share", (len(below), b_f, round(b_f / len(below), 4) if below else None))
    pr("difference", round((a_f / len(above) - b_f / len(below)), 4) if above and below else None)
    pr("one-sided Fisher exact p (unrounded)", f"{p:.3e}")
    pr("fused worlds (min count == 1)", sum(x["fused"] for x in runs))
    pr("Spearman ratio vs inflow, classes", rho_c)
    pr("Spearman ratio vs inflow, value means", rho_v)
    pr("logistic slope / se / z on ratio", (slope, se, z))
    pr("bottom share / top share (first-last value)", (values[0]["share"], values[-1]["share"]))
    if sections.get("details"):
        for v in values:
            pr(f"  value {v['f_local']}: classes={v['classes']} contact={v['classes_with_contact']} "
               f"fused={v['fused']} share={v['share']} spread={v['ratio_spread']}", "")
    return {"runs": runs, "values": values}


def arms_of(family, agg_name):
    idx = json.loads((L1 / f"{family}_series_index.json").read_text(encoding="utf-8"))
    arms = idx["arms"]
    all_runs = load_runs(family)
    # tag -> pure row
    by_tag = {r["tag"]: r for r in all_runs}
    for a in arms:
        sel = [by_tag[r["tag"]] for r in idx["runs"] if r.get("arm") == a["name"] and r["tag"] in by_tag]
        a["_runs"] = sel
    return idx, arms


# ------------------------------------------------------------------ X194 / X197 --
def pool_compacts():
    """The observational pool used by X194/X197: every top-level compact slice except the
    phase/inflow-selected x18*/x19* families. Returns (rows, excluded_count)."""
    rows, excluded = [], 0
    for f in sorted(L1.glob("*.compact.json")):
        if f.stem.startswith(("x18", "x19")):
            excluded += 1
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        params = d.get("params") or {}
        if not series:
            continue
        first = comps(series[0])
        if len(first) < 2:
            continue
        counts = [len(comps(r)) for r in series]
        c0, c1 = centroid(first[0]), centroid(first[1])
        dx = abs(c0[0] - c1[0]) % GRID
        dx = min(dx, GRID - dx)
        dy = abs(c0[1] - c1[1]) % GRID
        dy = min(dy, GRID - dy)
        area0 = float(first[0]["area"]) if isinstance(first[0], dict) else float(first[0][1])
        r0 = math.sqrt(max(area0, 1) / math.pi)
        F = float(params.get("F", 0.0))
        g_cold = min(G_at(*centroid(c)) for c in first)
        phase = tuple(sorted((int(round(c[0])) % 12, int(round(c[1])) % 12) for c in (centroid(c) for c in first)))
        phase2 = tuple(sorted((int(round(c[0])) % 12, int(round(c[1])) % 12)
                              for c in (centroid(c) for c in first[:2])))
        rows.append({"file": f.stem.replace(".compact", ""), "r0": round(r0, 3),
                     "radius1": round(r0, 1),
                     "gap": round(math.hypot(dx, dy) - 2 * r0),
                     "F": F, "steps": int(params.get("steps", 0)), "n_bodies": len(first),
                     "fused": int(min(counts) == 1), "phase": phase,
                     "f_local5": round(f_local_of(F, g_cold), 5),
                     "f_local6": round(f_local_of(F, g_cold), 6),
                     "phase2": phase2})
    return rows, excluded


def do_x194(sections):
    hdr("[RECOMP] X194  l1_field_x194_phase_clusters.json")
    agg = json.loads((POND / "l1_field_x194_phase_clusters.json").read_text(encoding="utf-8"))
    rows, excluded = pool_compacts()
    def wkey(r):
        return (round(r["r0"] / 0.2) * 0.2, r["gap"], r["F"], r["steps"], r["phase"])
    by_world = defaultdict(list)
    for r in rows:
        by_world[wkey(r)].append(r)
    by_pos = defaultdict(list)
    for r in rows:
        by_pos[r["phase"]].append(r)
    sizes = sorted((len(v) for v in by_world.values()), reverse=True)
    homog = [v for v in by_world.values() if len({x["fused"] for x in v}) == 1]
    mixed = [v for v in by_world.values() if len({x["fused"] for x in v}) > 1]
    obs_auc = auc([r["f_local5"] for r in rows], [r["fused"] for r in rows])
    auc_h = auc([v[0]["f_local5"] for v in homog], [v[0]["fused"] for v in homog])
    print("  AGG stored: runs=%s worlds=%s excluded=%s largest=%s singletons=%s mixed=%s "
          "auc_runs=%s auc_worlds=%s sd_runs=%s sd_worlds=%s ratio=%s" % (
              agg["composition"]["runs"], agg["composition"]["distinct_worlds"],
              agg["composition"]["excluded_phase_selected_runs"], agg["composition"]["largest_phase"],
              agg["composition"]["phases_with_one_run"], agg["composition"]["phases_with_mixed_outcome"],
              agg["auc_by_runs"], agg["auc_by_phases_homogeneous"],
              agg["bootstrap"]["by_runs"]["ci95"][2], agg["bootstrap"]["by_phases"]["ci95"][2],
              agg["bootstrap"]["sd_ratio_phases_over_runs"]))
    pr("pool runs", len(rows))
    pr("distinct worlds (phase x arm)", len(by_world))
    pr("distinct positions (phase only)", len(by_pos))
    pr("excluded x18*/x19* compact files (current disk)", excluded)
    pr("largest world (runs)", sizes[0] if sizes else 0)
    pr("singleton worlds", sum(1 for s in sizes if s == 1))
    pr("worlds with mixed outcome", len(mixed))
    pr("AUC by runs", obs_auc)
    pr("AUC by homogeneous worlds", auc_h)
    # bootstrap, re-implemented
    rng = random.Random(194)
    br, bw = [], []
    items = [(round(statistics.fmean([x["f_local5"] for x in v]), 5),
              round(statistics.fmean([x["fused"] for x in v]), 5)) for v in by_world.values()]
    for _ in range(1000):
        s = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        a = auc([r["f_local5"] for r in s], [r["fused"] for r in s])
        if a is not None:
            br.append(a)
        cl = [items[rng.randrange(len(items))] for _ in range(len(items))]
        a2 = auc([c[0] for c in cl], [1 if c[1] >= 0.5 else 0 for c in cl])
        if a2 is not None:
            bw.append(a2)
    def sd(v):
        return round(statistics.pstdev(v), 4)
    pr("bootstrap sd by runs (mine)", sd(br))
    pr("bootstrap sd by worlds (mine)", sd(bw))
    pr("sd ratio worlds/runs (mine)", round(sd(bw) / sd(br), 2))
    pr("bootstrap CI by runs (2.5/97.5)", (sorted(br)[int(0.025 * len(br))], sorted(br)[int(0.975 * len(br))]))
    pr("bootstrap CI by worlds (2.5/97.5)", (sorted(bw)[int(0.025 * len(bw))], sorted(bw)[int(0.975 * len(bw))]))


def deviance_x186(rows, key):
    """Own reimplementation of X186's grid-searched binomial deviance (slope x shift)."""
    if len({r["fused"] for r in rows}) < 2:
        return None
    vals = [key(r) for r in rows]
    if min(vals) <= 0 or len(set(vals)) < 2:
        return None
    base = statistics.fmean(r["fused"] for r in rows)
    base = min(max(base, 1e-6), 1 - 1e-6)
    lv = [math.log(v) for v in vals]
    mlv = statistics.fmean(lv)
    best = None
    for m in range(-30, 31):
        w = m / 10.0
        for shift in range(-30, 31, 5):
            b = math.log(base / (1 - base)) + shift / 20.0
            dev = 0.0
            for fv, x in zip((r["fused"] for r in rows), lv):
                z = max(min(b + w * (x - mlv), 30), -30)
                p = 1 / (1 + math.exp(-z))
                p = min(max(p, 1e-9), 1 - 1e-9)
                dev += -2 * (fv * math.log(p) + (1 - fv) * math.log(1 - p))
            if best is None or dev < best:
                best = dev
    return round(best, 1)


def do_x197(sections):
    hdr("[RECOMP] X197  l1_field_x197_deviance_worlds.json")
    agg = json.loads((POND / "l1_field_x197_deviance_worlds.json").read_text(encoding="utf-8"))
    rows, excluded = pool_compacts()
    rows = [r for r in rows if r["n_bodies"] == 2]  # X197's own guard: exactly two bodies
    cells = defaultdict(list)
    for r in rows:
        r["cell"] = (r["radius1"], r["gap"], round(r["F"], 3))
        cells[r["cell"]].append(r)
    mixed = [r for r in rows if 0 < statistics.fmean(x["fused"] for x in cells[r["cell"]]) < 1]
    worlds = defaultdict(list)
    for r in mixed:
        worlds[(r["cell"], r["phase2"])].append(r)
    world_rows = [{"fused": statistics.fmean(x["fused"] for x in v),
                   "f_local": statistics.fmean(x["f_local6"] for x in v),
                   "F": v[0]["F"], "cell": v[0]["cell"]} for v in worlds.values()]
    dnr = deviance_x186(mixed, lambda r: r["F"])
    dlr = deviance_x186(mixed, lambda r: r["f_local6"])
    dnw = deviance_x186(world_rows, lambda r: r["F"])
    dlw = deviance_x186(world_rows, lambda r: r["f_local"])
    print("  AGG stored: runs=%s mixed=%s worlds=%s rpw=%s drop_runs=%s (%s->%s) "
          "drop_worlds=%s (%s->%s) boot_runs=%s boot_worlds=%s" % (
              agg["pool"]["runs"], agg["pool"]["mixed_cell_runs"], agg["worlds"]["count"],
              agg["worlds"]["runs_per_world"], agg["deviance"]["drop_runs"],
              agg["deviance"]["nominal_runs"], agg["deviance"]["local_runs"],
              agg["deviance"]["drop_worlds"], agg["deviance"]["nominal_worlds"], agg["deviance"]["local_worlds"],
              agg["bootstrap"]["share_above_bar_runs"], agg["bootstrap"]["share_above_bar_worlds"]))
    pr("pool runs", len(rows))
    pr("excluded x18*/x19* compact files (current disk)", excluded)
    pr("cells / mixed cells", (len(cells), sum(1 for v in cells.values() if 0 < statistics.fmean(x["fused"] for x in v) < 1)))
    pr("mixed-cell runs", len(mixed))
    pr("worlds (cell x phase)", len(world_rows))
    pr("runs per world", round(len(mixed) / len(world_rows), 3) if world_rows else None)
    pr("deviance nominal runs", dnr); pr("deviance local runs", dlr)
    pr("drop runs", None if None in (dnr, dlr) else round(dnr - dlr, 1))
    pr("deviance nominal worlds", dnw); pr("deviance local worlds", dlw)
    pr("drop worlds", None if None in (dnw, dlw) else round(dnw - dlw, 1))
    # bootstrap
    rng = random.Random(197)
    b_r, b_w = [], []
    for _ in range(120):
        s = [mixed[rng.randrange(len(mixed))] for _ in range(len(mixed))]
        n, l = deviance_x186(s, lambda r: r["F"]), deviance_x186(s, lambda r: r["f_local6"])
        if None not in (n, l):
            b_r.append(round(n - l, 1))
        ws = [world_rows[rng.randrange(len(world_rows))] for _ in range(len(world_rows))]
        n2, l2 = deviance_x186(ws, lambda r: r["F"]), deviance_x186(ws, lambda r: r["f_local"])
        if None not in (n2, l2):
            b_w.append(round(n2 - l2, 1))
    sh = lambda v: round(sum(1 for x in v if x > 20.0) / len(v), 3) if v else None
    pr("bootstrap share above 20, runs (mine)", sh(b_r))
    pr("bootstrap share above 20, worlds (mine)", sh(b_w))
    pr("bootstrap median drop runs/worlds (mine)", (statistics.median(b_r), statistics.median(b_w)))


# ---------------------------------------------------------------- X195 / X196 ----
def do_x195(sections):
    hdr("[RECOMP] X195  l1_field_x195_sign_sweep.json")
    agg = json.loads((POND / "l1_field_x195_sign_sweep.json").read_text(encoding="utf-8"))
    idx, plan = arms_of("x195", "x195_sign_sweep")
    live_by_name = {a["name"]: a for a in agg["arms"]}
    for a in plan:
        sel = a["_runs"]
        live = live_by_name[a["name"]]
        values = value_table(sel)
        usable = [x for x in sel if x["ratio_contact"] is not None]
        crowd = max(values, key=lambda v: v["classes_with_contact"])
        rho_c = spearman([round(x["f_local"], 5) for x in usable], [x["ratio_contact"] for x in usable])
        means = [v for v in values if v["ratio_mean"] is not None]
        rho_v = spearman([v["f_local"] for v in means], [v["ratio_mean"] for v in means])
        print(f"  ARM {a['name']} radius={live['radius']} gap={live['gap']} sep={live['sep']}")
        pr("AGG: worlds / contact / fused / rho_c / rho_v / crowded spread / classes",
           (live["worlds"], live["worlds_with_contact"], live["fused_worlds"],
            live["spearman_ratio_vs_inflow_classes"], live["spearman_ratio_vs_inflow_value_means"],
            live["crowded_value"]["ratio_spread"], live["crowded_value"]["classes"]))
        pr("MINE: worlds / contact / fused", (len(sel), len(usable), sum(x["fused"] for x in usable)))
        pr("MINE: rho_c / rho_v", (rho_c, rho_v))
        pr("MINE: crowded value / classes / spread / min / max",
           (crowd["f_local"], crowd["classes_with_contact"], crowd["ratio_spread"],
            crowd["ratio_min"], crowd["ratio_max"]))
        pr("MINE: bottom share / top share", (values[0]["share"], values[-1]["share"]))


def do_x196(sections):
    hdr("[RECOMP] X196  l1_field_x196_gap_or_size.json")
    agg = json.loads((POND / "l1_field_x196_gap_or_size.json").read_text(encoding="utf-8"))
    idx, plan = arms_of("x196", "x196_gap_or_size")
    live_by_name = {a["name"]: a for a in agg["arms"]}
    x192 = load_runs("x192")
    x195 = load_runs("x195")
    print("  AGG mean_shares:", agg["mean_shares"])
    print("  AGG references:", {k: v.get("share_over_values") for k, v in agg["references"].items()})
    table = {}
    for a in plan:
        values = value_table(a["_runs"])
        mean_share = round(statistics.fmean([v["share"] for v in values]), 4)
        table[a["name"]] = {"radius": live_by_name[a["name"]]["radius"],
                            "gap": live_by_name[a["name"]]["gap"], "sep": live_by_name[a["name"]]["sep"],
                            "share_over_values": mean_share,
                            "fused_worlds": sum(x["fused"] for x in a["_runs"]),
                            "spread": max(v["ratio_spread"] or 0 for v in values)}
        print(f"  ARM {a['name']}: radius={table[a['name']]['radius']} gap={table[a['name']]['gap']} "
              f"sep={table[a['name']]['sep']} -> share(mean over values)={mean_share} "
              f"fused={table[a['name']]['fused_worlds']}/144 crowded spread={table[a['name']]['spread']}  "
              f"[AGG mean_shares {agg['mean_shares'].get(a['name'])}]")
    # references recomputed from their own raw runs, not from the aggregates
    for label, runs, radius, gap, sep in (("r4_g12", x195, 4.0, 12.0, 20.0),
                                          ("r6_g9", x192, 6.0, 9.0, 21.0)):
        values = value_table(runs)
        mean_share = round(statistics.fmean([v["share"] for v in values]), 4)
        table[label] = {"radius": radius, "gap": gap, "sep": sep, "share_over_values": mean_share,
                        "fused_worlds": sum(x["fused"] for x in runs),
                        "spread": max(v["ratio_spread"] or 0 for v in values)}
        print(f"  REF {label}: radius={radius} gap={gap} sep={sep} -> share(mean over values)={mean_share} "
              f"fused={sum(x['fused'] for x in runs)}/144  "
              f"[AGG {agg['references'].get(label, {}).get('share_over_values')}]")
    print("  ORDERED FIVE-ARM GAP TABLE (mine):")
    for k, v in sorted(table.items(), key=lambda kv: (kv[1]["gap"], -kv[1]["radius"])):
        print(f"    gap {v['gap']:>4} radius {v['radius']} -> share {v['share_over_values']} "
              f"(fused {v['fused_worlds']}/144, crowded spread {v['spread']})")
    pr("MINE criteria: r4 share does not fall gap10->gap8",
       bool(table["r4_g8"]["share_over_values"] >= table["r4_g10"]["share_over_values"]
            and table["r4_g8"]["share_over_values"] > 0.1))
    pr("MINE criteria: r6 gap8 still fuses >= gap9 reference",
       bool(table["r6_g8"]["share_over_values"] > 0 and
            table["r6_g8"]["share_over_values"] >= table["r6_g9"]["share_over_values"]))
    pr("MINE criteria: phase spread >= 0.05 in each of the three new arms",
       all(table[k]["spread"] >= 0.05 for k in ("r4_g10", "r4_g8", "r6_g8")))


def compare_runs_detail(family, agg_name):
    """Row-by-row: are my field-derived f_local / fused / ratio_contact identical to the
    committed aggregate's runs_detail?"""
    agg = json.loads((POND / f"l1_field_{agg_name}.json").read_text(encoding="utf-8"))
    mine = {r["tag"]: r for r in load_runs(family)}
    bad = {"n_agg": 0, "missing": 0, "fused": 0, "f_local": 0, "ratio": 0}
    worst = 0.0
    for row in agg["runs_detail"]:
        bad["n_agg"] += 1
        tag = row["tag"]
        r = mine.get(tag)
        if r is None:
            bad["missing"] += 1
            continue
        if int(row["fused"]) != r["fused"]:
            bad["fused"] += 1
        fo = row.get("f_local", row.get("f_local_index"))
        if abs(round(float(fo), 5) - round(r["f_local"], 5)) > 1e-9:
            bad["f_local"] += 1
        ar = row.get("ratio_contact")
        if (ar is None) != (r["ratio_contact"] is None):
            bad["ratio"] += 1
        elif ar is not None:
            d = abs(float(ar) - r["ratio_contact"])
            worst = max(worst, d)
            if d > 1e-9:
                bad["ratio"] += 1
    return bad, worst


def do_compare(sections):
    hdr("[RECOMP] aggregate runs_detail vs my field-derived rows")
    for family, agg_name in (("x192", "x192_phase_census"), ("x193", "x193_phase_census_r3"),
                             ("x195", "x195_sign_sweep"), ("x196", "x196_gap_or_size")):
        bad, worst = compare_runs_detail(family, agg_name)
        pr(f"{agg_name}: rows compared / missing / fused-mismatch / f_local-mismatch / ratio-mismatch",
           (bad["n_agg"], bad["missing"], bad["fused"], bad["f_local"], bad["ratio"]))
        pr(f"{agg_name}: max |ratio_contact diff|", f"{worst:.2e}")


# ------------------------------------------------------------------------ main --
def main():
    which = sys.argv[1:] or ["x192", "x193", "x195", "x196", "x194", "x197"]
    print("ROOT =", ROOT)
    if "compare" in which:
        do_compare({})
    if "x192" in which:
        census_report("x192", "x192_phase_census", {})
    if "x193" in which:
        census_report("x193", "x193_phase_census_r3", {})
    if "x195" in which:
        do_x195({})
    if "x196" in which:
        do_x196({})
    if "x194" in which:
        do_x194({})
    if "x197" in which:
        do_x197({})


if __name__ == "__main__":
    main()
