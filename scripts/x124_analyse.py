"""x124_analyse.py — X124: do the generation-time and generation-rate results agree?

X93 says the larger sister's generation time is longer; X113 says her lineage reaches more generations per unit time. A longer denominator should lower the rate
unless the depth grows faster. This checks the three numbers against each other on the same pairs.
Plan: reports/2026-11-03-x124-coherence-plan.md.

    python scripts/x124_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x113_analyse import depth_of, life_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x124_coherence.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
X113C_RATE = {0.030: 6.056, 0.040: 18.96}
TOL = 0.10
MIN_PAIRS = 1000
BOOTSTRAP = 2000


def bootstrap_ci(vals, seed=124):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def cell_stats(flow: float) -> dict:
    d_life, d_depth, d_rate = [], [], []
    ratio_depth, ratio_life = [], []
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        memo: dict[int, int] = {}
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    if w["peak"][a]["area"] >= w["peak"][b]["area"]:
                        big, small = a, b
                    else:
                        big, small = b, a
                    la, ls = life_of(w, big), life_of(w, small)
                    da, ds = depth_of(children, big, memo), depth_of(children, small, memo)
                    if la <= 0 or ls <= 0:
                        continue
                    ra, rs = da / la * 1000.0, ds / ls * 1000.0
                    d_life.append(la - ls)
                    d_depth.append(da - ds)
                    d_rate.append(ra - rs)
                    if ls > 0 and ds > 0:
                        ratio_life.append(la / ls)
                        ratio_depth.append((da + 1) / (ds + 1))
    return {
        "pairs": len(d_life),
        "gen_time_diff": round(st.mean(d_life), 3) if d_life else None,
        "gen_time_ci": bootstrap_ci(d_life),
        "depth_diff": round(st.mean(d_depth), 3) if d_depth else None,
        "depth_ci": bootstrap_ci(d_depth),
        "rate_diff": round(st.mean(d_rate), 3) if d_rate else None,
        "rate_ci": bootstrap_ci(d_rate),
        "mean_ratio_life": round(st.mean(ratio_life), 4) if ratio_life else None,
        "mean_ratio_depth": round(st.mean(ratio_depth), 4) if ratio_depth else None,
        "implied_rate_ratio": (round(st.mean(ratio_depth) / st.mean(ratio_life), 4)
                               if ratio_life and ratio_depth else None),
        "refs": {"depth": X113_DEPTH[flow], "rate": X113C_RATE[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X124 coherence audit")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} pairs")
        ref = c["refs"]
        if c["depth_diff"] is None or abs(c["depth_diff"] - ref["depth"]) > TOL * abs(ref["depth"]):
            bad.append(f"{tag}: depth {c['depth_diff']} misses X113's {ref['depth']}")
        if c["rate_diff"] is None or abs(c["rate_diff"] - ref["rate"]) > TOL * abs(ref["rate"]):
            bad.append(f"{tag}: rate {c['rate_diff']} misses X113c's {ref['rate']}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        parts = []
        for tag, c in cells.items():
            coh = "coherent"
            if c["rate_diff"] is not None and c["depth_diff"] is not None and c["gen_time_diff"] is not None:
                # the rate must grow if depth grows faster than generation time
                implied = (c["depth_diff"] > 0 and c["gen_time_diff"] is not None)
                if (c["rate_diff"] > 0) != (implied):
                    coh = "contradictory"
            parts.append(f"{tag}: gen time {c['gen_time_diff']} (CI {c['gen_time_ci']}), depth {c['depth_diff']} "
                         f"(CI {c['depth_ci']}), rate {c['rate_diff']} (CI {c['rate_ci']}), implied rate ratio "
                         f"{c['implied_rate_ratio']} — {coh}")
        verdict = "; ".join(parts)

    res = {
        "kind": "l1_field_x124_coherence",
        "experiment": "X124",
        "command": "python scripts/x124_analyse.py --write",
        "prereg": "reports/2026-11-03-x124-coherence-plan.md",
        "readout": "paired generation time, subtree depth and rate per sister pair, plus the ratio decomposition",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x124] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} gen_time={c['gen_time_diff']} {c['gen_time_ci']} depth={c['depth_diff']} "
              f"{c['depth_ci']} rate={c['rate_diff']} {c['rate_ci']} ratios life={c['mean_ratio_life']} "
              f"depth={c['mean_ratio_depth']} implied={c['implied_rate_ratio']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
