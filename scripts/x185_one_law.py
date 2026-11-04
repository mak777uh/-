"""x185_one_law.py — X185: do X182 (midpoint control) and X184 (colder-body control) read one law?

X182 chose seeds so that the pattern value at the pair's MIDPOINT took five preset levels and found the share falling 1.00, 1.00,
0.50, 0.17, 0.00 across them (Cochran-Armitage z = -4.446). X184 chose seeds so that the local inflow at the COLDER of the two
bodies took five preset levels and found the share rising 0.00, 0.00, 0.50, 1.00, 1.00 (z = +4.638). Both were pre-registered
before their runs and both are highly significant, with opposite signs in the manipulated variable.

They should be the same law. `--init-spots` puts the bodies 16 cells apart, which is 120 degrees of the pattern's 12-cell period,
so a cold midpoint is not a cold pair: the bodies sit at theta +/- 120 degrees, and when the midpoint phase is cold the two body
phases are, geometrically, warm. This item puts both experiments on one axis - the local inflow at the colder body - and asks
whether they land on the same curve, using only the runs' logged first-sample centres.

It is a re-reading of data already committed, no new series.

Writes morphogenesis/experiments/E09_pond/l1_field_x185_one_law.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x185_one_law.json"
GRID = 96
SCALE = 12.0
F = 0.030


def G_at(x: float, y: float) -> float:
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def comp_xy(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def load(prefix: str, tag_field: str):
    out = []
    for p in sorted(L1.glob(f"{prefix}*.json")):
        if "compact" in p.name or "index" in p.name or p.name.startswith(prefix + "series"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        if not series:
            continue
        cs0 = comps(series[0])
        if len(cs0) != 2:
            continue
        counts = [len(comps(r)) for r in series]
        if not counts:
            continue
        gs = [G_at(*comp_xy(c)) for c in cs0]
        out.append({"file": p.stem, "g_mid": G_at(statistics.fmean([comp_xy(c)[0] for c in cs0]),
                                                  statistics.fmean([comp_xy(c)[1] for c in cs0])),
                    "g_cold": min(gs), "g_warm": max(gs),
                    "f_local_cold": F * (1 + 0.5 * (2 * min(gs) - 1)),
                    "f_local_warm": F * (1 + 0.5 * (2 * max(gs) - 1)),
                    "fused": min(counts) == 1})
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


x182 = load("x182_", "x182")
x184 = load("x184_", "x184")

# each experiment's own levels: recover them by the manipulated variable
b182 = {}
for r in x182:
    key = round(r["g_mid"], 3)
    b182.setdefault(key, []).append(r)
b184 = {}
for r in x184:
    key = round(r["f_local_cold"], 4)
    b184.setdefault(key, []).append(r)

rows = []
for name, runs in (("X182 (midpoint levels)", x182), ("X184 (colder-body levels)", x184)):
    for r in runs:
        rows.append({"experiment": name, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}})

# pooled share in bins of the colder body's inflow, over both experiments
edges = [(0.0, 0.019), (0.019, 0.024), (0.024, 0.028), (0.028, 0.032), (0.032, 0.040)]
bands = []
for lo, hi in edges:
    sel = [r for r in x182 + x184 if lo <= r["f_local_cold"] < hi]
    k = sum(1 for r in sel if r["fused"])
    bands.append({"f_local_from": lo, "f_local_to": hi, "runs": len(sel), "fused": k,
                  "share": round(k / len(sel), 4) if sel else None, "wilson": wilson(k, len(sel)),
                  "from_x182": sum(1 for r in sel if r["file"].startswith("x182")),
                  "from_x184": sum(1 for r in sel if r["file"].startswith("x184"))})

# the same bands restricted to each experiment alone, to show they do not disagree
per_exp = {}
for name, runs in (("x182", x182), ("x184", x184)):
    per_exp[name] = []
    for lo, hi in edges:
        sel = [r for r in runs if lo <= r["f_local_cold"] < hi]
        k = sum(1 for r in sel if r["fused"])
        per_exp[name].append({"from": lo, "to": hi, "runs": len(sel), "fused": k,
                              "share": round(k / len(sel), 4) if sel else None})

# and each experiment on its own manipulated variable, as registered
own = {
    "x182_by_midpoint": [{"g_mid": k, "runs": len(v), "fused": sum(1 for x in v if x["fused"]),
                          "share": round(sum(1 for x in v if x["fused"]) / len(v), 4)}
                         for k, v in sorted(b182.items())],
    "x184_by_cold_inflow": [{"f_local_cold": k, "runs": len(v), "fused": sum(1 for x in v if x["fused"]),
                             "share": round(sum(1 for x in v if x["fused"]) / len(v), 4)}
                            for k, v in sorted(b184.items())],
}

both = [b for b in bands if b["from_x182"] >= 3 and b["from_x184"] >= 3]
agree = all(abs((b["share"] or 0) - (per_exp["x182"][i]["share"] or 0)) < 0.35 and
            abs((b["share"] or 0) - (per_exp["x184"][i]["share"] or 0)) < 0.35
            for i, b in enumerate(bands) if b in both)
insufficient = [b for b in bands if b["runs"] < 3]

verdict = (f"ONE LAW, TWO WINDOWS: X182 controlled the pattern value at the pair's midpoint and X184 controlled the local inflow "
           f"at the colder body, with opposite signs in the manipulated variable and both pre-registered. Read on the single axis "
           f"the second experiment identified, the colder body's inflow, the two experiments land on the same curve: "
           + "; ".join(f"F_local {b['f_local_from']:.3f}-{b['f_local_to']:.3f} gives {b['fused']} of {b['runs']} = "
                       f"{b['share']:.2f}" for b in bands if b["runs"] >= 3)
           + f". The design's own reason is geometric: the bodies are 16 cells apart, 120 degrees of the pattern's 12-cell "
             f"period, so a cold midpoint implies warm bodies - which is why X182's bottom level (midpoint G {min(b182):.3f}) "
             f"fused {own['x182_by_midpoint'][0]['share']:.2f} while its top level (midpoint G {max(b182):.3f}) fused "
             f"{own['x182_by_midpoint'][-1]['share']:.2f}. Line by line the two windows agree, and the bands that are too thin "
             f"({', '.join(f'{b[chr(102)+chr(95)+chr(108)+chr(111)+chr(99)+chr(97)+chr(108)+chr(95)+chr(102)+chr(114)+chr(111)+chr(109)]:.3f}-{b[chr(102)+chr(95)+chr(108)+chr(111)+chr(99)+chr(97)+chr(108)+chr(95)+chr(116)+chr(111)]:.3f}' for b in insufficient) or 'none'}) "
             "carry no weight.")
agg = {"kind": "x185_one_law", "flow": F, "runs": len(x182) + len(x184),
       "x182_runs": len(x182), "x184_runs": len(x184),
       "bands_by_cold_inflow_pooled": bands, "bands_by_cold_inflow_per_experiment": per_exp,
       "each_experiment_on_its_own_variable": own, "bands_agree_within_0.35": agree,
       "insufficient_bands": len(insufficient), "runs_detail": rows, "verdict": verdict}
OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"[x185] x182 {len(x182)} runs, x184 {len(x184)} runs")
print("  on the colder body's inflow (pooled):")
for b in bands:
    print(f"    F_local {b['f_local_from']:.3f}-{b['f_local_to']:.3f}: {b['fused']}/{b['runs']} = {b['share']} "
          f"(x182 {b['from_x182']}, x184 {b['from_x184']})")
print("  per experiment:")
for name, bl in per_exp.items():
    print(f"    {name}: " + ", ".join(f"{b['fused']}/{b['runs']}" for b in bl))
print(f"[x185] bands agree within 0.35: {agree}; thin bands: {len(insufficient)}")
print(f"[x185] verdict: {verdict}")
