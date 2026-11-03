"""x125_analyse.py — X125: one definition per quantity, all five readouts, both weightings.

Definitions (fixed here, stated with units):
  generation time g = uid last logged step - first + 1, in logged steps
  depth d          = longest descendant chain below the uid, in generations
  rate r           = d / g * 1000, generations per 1 000 steps of that uid's generation
  share            = g_big / g_small, a separate named readout

Plan: reports/2026-11-03-x125-definitions-plan.md.

    python scripts/x125_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x125_definitions.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
X113C_RATE_UID = {0.030: 6.056, 0.040: 18.96}
TOL = 0.10
MIN_PAIRS = 1000
BOOTSTRAP = 2000


def boot(vals, seed=125):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 3), round(means[hi], 3)]


def cell_stats(flow: float) -> dict:
    g_diff, share, d_diff, r_pair, r_uid = [], [], [], [], []
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
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    gb, gs = life_of(w, big), life_of(w, small)
                    db, ds = depth_of(children, big, memo), depth_of(children, small, memo)
                    if gb <= 0 or gs <= 0:
                        continue
                    g_diff.append(gb - gs)
                    share.append(gb / gs)
                    d_diff.append(db - ds)
                    r_pair.append(db / gb * 1000.0 - ds / gs * 1000.0)
                    r_uid.append(db / gb * 1000.0)
                    r_uid.append(-ds / gs * 1000.0)
    return {
        "pairs": len(g_diff),
        "g_diff": round(st.mean(g_diff), 3) if g_diff else None, "g_diff_ci": boot(g_diff),
        "share": round(st.mean(share), 4) if share else None, "share_ci": boot(share),
        "d_diff": round(st.mean(d_diff), 3) if d_diff else None, "d_diff_ci": boot(d_diff),
        "r_pair": round(st.mean(r_pair), 3) if r_pair else None, "r_pair_ci": boot(r_pair),
        "r_uid": round(st.mean(r_uid), 3) if r_uid else None, "r_uid_ci": boot(r_uid),
        "refs": {"depth": X113_DEPTH[flow], "rate_uid": X113C_RATE_UID[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X125 definitions")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["pairs"] < MIN_PAIRS:
            bad.append(f"{tag}: {c['pairs']} pairs")
        ref = c["refs"]
        if c["d_diff"] is None or abs(c["d_diff"] - ref["depth"]) > TOL * abs(ref["depth"]):
            bad.append(f"{tag}: depth {c['d_diff']} misses X113's {ref['depth']}")
        if c["r_uid"] is None or abs(c["r_uid"] - ref["rate_uid"]) > TOL * abs(ref["rate_uid"]):
            bad.append(f"{tag}: uid-weighted rate {c['r_uid']} misses X113c's {ref['rate_uid']}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        signs = [(c["r_pair"] or 0) * (c["r_uid"] or 0) for c in (lat, maz)]
        if any(s < 0 for s in signs):
            verdict = ("contradiction between weightings: the pair-weighted and uid-weighted rate contrasts have opposite signs, so no single sentence can be "
                       "published until the design chooses the weighting")
        else:
            verdict = (f"the vocabulary is fixed. Raw generation time: {lat['g_diff']} steps (CI {lat['g_diff_ci']}) and {maz['g_diff']} "
                       f"(CI {maz['g_diff_ci']}) — the larger sister's is SHORTER. Share: {lat['share']} / {maz['share']}. Depth: {lat['d_diff']} / "
                       f"{maz['d_diff']}. Rate, pair-weighted: {lat['r_pair']} (CI {lat['r_pair_ci']}) and {maz['r_pair']} (CI {maz['r_pair_ci']}); "
                       f"uid-weighted: {lat['r_uid']} and {maz['r_uid']}. Published: the pair-weighted one, because the claim is about pairs.")

    res = {
        "kind": "l1_field_x125_definitions",
        "experiment": "X125",
        "command": "python scripts/x125_analyse.py --write",
        "prereg": "reports/2026-11-03-x125-definitions-plan.md",
        "definitions": {
            "generation_time": "uid last logged step - first + 1, in logged steps",
            "depth": "longest descendant chain below the uid, in generations",
            "rate": "depth / generation_time * 1000, generations per 1 000 steps",
            "share": "g_big / g_small, a separate readout",
            "published_rate": "pair-weighted (mean over pairs of the two uids' rate difference)",
        },
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x125] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} g={c['g_diff']} {c['g_diff_ci']} share={c['share']} d={c['d_diff']} {c['d_diff_ci']} "
              f"r_pair={c['r_pair']} {c['r_pair_ci']} r_uid={c['r_uid']} {c['r_uid_ci']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
