"""x99_analyse.py — is the memory map a property of the world or of the excursion cut?

Criteria: `reports/2026-11-02-x99-threshold-memory-plan.md`. Four cells (two inflows x two thresholds), ten worlds each, against the
committed 0.20 references of the same inflows (1.16 divisions at F = 0.030, 2.08 at 0.040).

Run:
    python scripts/x99_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x99_threshold_memory.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402
from field_metrics import half_life  # noqa: E402

LAGS = (1, 2, 3)
CELLS = {"f030_thr015": ("f030", "015", 0.030, 0.15), "f030_thr025": ("f030", "025", 0.030, 0.25),
         "f040_thr015": ("f040", "015", 0.040, 0.15), "f040_thr025": ("f040", "025", 0.040, 0.25)}
REFERENCE = {0.030: 1.16, 0.040: 2.08}
RESOLUTION = 0.40
CUT_DEPENDENT = 0.80
MIN_PAIRS, MIN_COMPONENTS, MIN_FITTABLE = 400, 10, 7


def cell_stats(flow_tag: str, thr_tag: str, flow: float, thr: float) -> dict:
    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    comps, areas = [], []
    for path in sorted(L1.glob(f"x99_{flow_tag}_thr{thr_tag}_s*.json")):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        d = json.loads(path.read_text(encoding="utf-8"))
        comps.append(st.mean([s.get("components") or 0 for s in (d.get("series") or [])]))
        for o in (d.get("uid_outcomes") or []):
            areas.append(float(o.get("peak") or 0))
        for k in LAGS:
            pairs = []
            for uid in w["peaks"]:
                anc = ancestors(uid, w["parent"], k)
                if anc is None or anc not in w["peaks"]:
                    continue
                pairs.append((w["peaks"][anc], w["peaks"][uid]))
            per_lag[k]["pairs"].extend(pairs)
            rho = spearman([a for a, _ in pairs], [b for _, b in pairs])
            per_lag[k]["worlds"][seed] = {"pairs": len(pairs), "rho": round(rho, 3) if rho is not None else None}

    out = {"flow": flow, "threshold": thr, "worlds": len(per_lag[1]["worlds"]),
           "components_mean": round(st.mean(comps), 1) if comps else None,
           "peak_area_median": round(st.median(areas), 1) if areas else None}
    for k in LAGS:
        pairs = per_lag[k]["pairs"]
        out[str(k)] = {"pairs": len(pairs),
                       "rho": round(spearman([a for a, _ in pairs], [b for _, b in pairs]) or 0.0, 3) if pairs else None}

    halves, fittable = [], 0
    for seed in per_lag[1]["worlds"]:
        rs = [per_lag[1]["worlds"][seed]["rho"], per_lag[2]["worlds"].get(seed, {}).get("rho"),
              per_lag[3]["worlds"].get(seed, {}).get("rho")]
        got = half_life(rs)
        if not got["fittable"]:
            continue
        fittable += 1
        if got["half_life"] is not None:
            halves.append(got["half_life"])
    out["worlds_fittable"] = f"{fittable}/{len(per_lag[1]['worlds'])}"
    out["half_life_median"] = round(st.median(halves), 2) if halves else None
    out["half_life_range"] = [round(min(halves), 2), round(max(halves), 2)] if halves else None
    out["reference_020"] = REFERENCE[flow]
    out["delta_vs_020"] = round(out["half_life_median"] - REFERENCE[flow], 2) if out["half_life_median"] is not None else None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X99 memory at two cuts")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x99_threshold_memory", "experiment": "X99",
           "command": "python scripts/x99_analyse.py --write",
           "prereg": "reports/2026-11-02-x99-threshold-memory-plan.md",
           "references_020": {str(k): v for k, v in REFERENCE.items()},
           "resolution": RESOLUTION, "cut_dependent": CUT_DEPENDENT, "cells": {}}
    for name, (flow_tag, thr_tag, flow, thr) in CELLS.items():
        res["cells"][name] = cell_stats(flow_tag, thr_tag, flow, thr)
    c = res["cells"]

    void = [k for k, v in c.items()
            if (v["1"]["pairs"] or 0) < MIN_PAIRS or (v["components_mean"] or 0) < MIN_COMPONENTS
            or int(v["worlds_fittable"].split("/")[0]) < MIN_FITTABLE]
    counts = {(v["flow"], v["threshold"]): v["components_mean"] for v in c.values()}
    manipulation = all(
        counts.get((f, 0.15)) != counts.get((f, 0.25)) for f in (0.030, 0.040)
    ) if len(counts) == 4 else False
    control = bool(manipulation and not void)
    res["positive_control"] = {"fires": control, "component_counts": {f"{k[0]}@{k[1]}": v for k, v in counts.items()}}

    deltas = {k: v["delta_vs_020"] for k, v in c.items()}
    res["deltas"] = deltas
    by_flow = {}
    for flow in (0.030, 0.040):
        by_flow[str(flow)] = [deltas[k] for k, v in c.items() if v["flow"] == flow]
    robust = all(all(d is not None and abs(d) <= RESOLUTION for d in ds) for ds in by_flow.values())
    dependent = any(d is not None and abs(d) >= CUT_DEPENDENT for d in deltas.values())

    if not control:
        verdict = "void: a cell is underpowered or unfittable at its cut, or the component counts did not differ between the cuts"
    elif robust:
        verdict = "robust to the cut: at both inflows both thresholds stay within 0.4 divisions of the 0.20 value"
    elif dependent:
        verdict = "cut-dependent: a threshold moves the half-life by at least 0.8 divisions in at least one inflow"
    else:
        verdict = "mixed"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x99] written: {OUT.name}")

    for k, v in c.items():
        print(f"  {k}: thr={v['threshold']} half={v['half_life_median']} (ref {v['reference_020']}, delta {v['delta_vs_020']}) "
              f"rho1={v['1']['rho']} pairs={v['1']['pairs']} comp={v['components_mean']} area_med={v['peak_area_median']} "
              f"fit={v['worlds_fittable']}")
    print("  control:", res["positive_control"])
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
