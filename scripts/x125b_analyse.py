"""x125b_analyse.py — X125b: the filter printed with the number, four statistics of one paired difference.

Definitions and filters, all fixed in the plan before the run:
  g  = uid last logged step - first + 1, in logged steps            (no filter)
  d  = longest descendant chain below the uid, in generations        (no filter)
  r  = d / g * 1000, generations per 1 000 steps                     (both sisters' g >= 50 steps)
Published statistics: generation time -> median + fraction of pairs; depth -> mean; rate -> pair-weighted mean.

Plan: reports/2026-11-03-x125b-definitions-plan.md.

    python scripts/x125b_analyse.py --write
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
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402
from x113_analyse import depth_of, life_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x125b_statistics.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
X113C_RATE = {0.030: 6.056, 0.040: 18.96}
X93_FRACTION = {0.030: 0.530, 0.040: 0.401}   # comparison across series, NOT a control
MIN_LIFE = 50.0
MIN_PAIRS = 1000
HEREDITY_FLOOR = 0.35
TOL = 0.10
TAIL = 1000.0
BOOTSTRAP = 2000


def boot(vals, seed=1252):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 3), round(means[hi], 3)]


def cell_stats(flow: float) -> dict:
    g_diff, d_diff, r_filt, r_raw = [], [], [], []
    g_big, g_small = [], []
    heredity = []
    dropped = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        memo: dict[int, int] = {}
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    gb, gs = life_of(w, big), life_of(w, small)
                    db, ds = depth_of(children, big, memo), depth_of(children, small, memo)
                    if gb <= 0 or gs <= 0:
                        continue
                    g_diff.append(gb - gs)
                    g_big.append(gb)
                    g_small.append(gs)
                    d_diff.append(db - ds)
                    r_raw.append(db / gb * 1000.0 - ds / gs * 1000.0)
                    if gb >= MIN_LIFE and gs >= MIN_LIFE:
                        r_filt.append(db / gb * 1000.0 - ds / gs * 1000.0)
                    else:
                        dropped += 1
    pos = [x for x in g_diff if x > 0]
    neg = [x for x in g_diff if x < 0]
    return {
        "pairs": len(g_diff),
        "pairs_after_filter": len(r_filt),
        "pairs_dropped_by_filter": dropped,
        # generation time: four statistics, all named
        "g_mean": round(st.mean(g_diff), 3) if g_diff else None,
        "g_mean_ci": boot(g_diff),
        "g_median": round(st.median(g_diff), 1) if g_diff else None,
        "g_fraction_larger": round(len(pos) / len(g_diff), 4) if g_diff else None,
        "g_ratio_of_means": round(st.mean(g_big) / st.mean(g_small), 4) if g_small else None,
        "g_mean_big": round(st.mean(g_big), 1) if g_big else None,
        "g_mean_small": round(st.mean(g_small), 1) if g_small else None,
        "g_tail_beyond_1000": round(sum(1 for x in g_diff if abs(x) > TAIL) / len(g_diff), 4) if g_diff else None,
        "g_mean_positive_part": round(st.mean(pos), 1) if pos else None,
        "g_mean_negative_part": round(st.mean(neg), 1) if neg else None,
        # depth
        "d_mean": round(st.mean(d_diff), 3) if d_diff else None,
        "d_mean_ci": boot(d_diff),
        # rate
        "r_filtered": round(st.mean(r_filt), 3) if r_filt else None,
        "r_filtered_ci": boot(r_filt, seed=1253),
        "r_unfiltered": round(st.mean(r_raw), 3) if r_raw else None,
        "rho_heredity": round(spearman([p[0] for p in heredity], [p[1] for p in heredity]), 3) if heredity else None,
        "x93_fraction": X93_FRACTION[flow],
        "refs": {"depth": X113_DEPTH[flow], "rate": X113C_RATE[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X125b statistics of one paired difference")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        ref = c["refs"]
        if c["pairs_after_filter"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs_after_filter']} pairs survive the filter")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["d_mean"] is None or abs(c["d_mean"] - ref["depth"]) > TOL * abs(ref["depth"]):
            bad.append(f"{tag}: depth {c['d_mean']} misses X113's {ref['depth']}")
        if c["r_filtered"] is None or abs(c["r_filtered"] - ref["rate"]) > TOL * abs(ref["rate"]):
            bad.append(f"{tag}: filtered rate {c['r_filtered']} misses X113c's {ref['rate']}")

    disagree = [tag for tag, c in cells.items()
                if c["g_mean"] is not None and c["g_median"] is not None
                and (c["g_mean"] > 0) != (c["g_median"] > 0)]

    if bad:
        verdict = "void: " + "; ".join(bad)
    elif disagree:
        verdict = ("contradiction: in " + ", ".join(disagree) + " the mean and the median of the generation-time difference have opposite signs, "
                   "so the magnitude statistic and the pair statistic disagree about the direction")
    else:
        lat, maz = cells["f030"], cells["f040"]
        verdict = (
            f"the filter is the whole difference: with both generation times >= {MIN_LIFE:.0f} steps the pair-weighted rate contrast is "
            f"{lat['r_filtered']} (CI {lat['r_filtered_ci']}) and {maz['r_filtered']} (CI {maz['r_filtered_ci']}), reproducing X113c's "
            f"{lat['refs']['rate']} / {maz['refs']['rate']}, and {lat['pairs_dropped_by_filter']} / {maz['pairs_dropped_by_filter']} pairs are dropped "
            f"by the filter. Generation time: median {lat['g_median']} / {maz['g_median']} steps, mean {lat['g_mean']} / {maz['g_mean']}, larger sister "
            f"longer in {lat['g_fraction_larger']:.1%} / {maz['g_fraction_larger']:.1%} of pairs, ratio of means {lat['g_ratio_of_means']} / "
            f"{maz['g_ratio_of_means']}. Depth: +{lat['d_mean']} / +{maz['d_mean']} generations. Published: generation time as median plus fraction, "
            f"depth as mean, rate as the filtered pair-weighted mean."
        )

    res = {
        "kind": "l1_field_x125b_statistics",
        "experiment": "X125b",
        "command": "python scripts/x125b_analyse.py --write",
        "prereg": "reports/2026-11-03-x125b-definitions-plan.md",
        "definitions": {
            "generation_time": f"uid last logged step - first + 1, in logged steps; no filter; statistic: median and fraction of pairs",
            "depth": "longest descendant chain below the uid, in generations; no filter; statistic: mean",
            "rate": f"depth / generation_time * 1000, generations per 1 000 steps; filter: both sisters >= {MIN_LIFE:.0f} steps; statistic: pair-weighted mean",
            "withdrawn": "mean of the ratio g_big/g_small (denominator near zero for short-lived uids)",
        },
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x125b] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} kept={c['pairs_after_filter']} dropped={c['pairs_dropped_by_filter']} "
              f"g median={c['g_median']} mean={c['g_mean']} {c['g_mean_ci']} frac={c['g_fraction_larger']} "
              f"ratio={c['g_ratio_of_means']} d={c['d_mean']} {c['d_mean_ci']} "
              f"r_filt={c['r_filtered']} {c['r_filtered_ci']} r_raw={c['r_unfiltered']} heredity={c['rho_heredity']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
