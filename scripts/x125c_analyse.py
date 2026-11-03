"""x125c_analyse.py — X125c: is X93's tie-excluded fraction bare once ties are counted?

X93 skips sister pairs with equal lifetimes; X125b counted them. Same pairs, one rule changed and named. The identity p_all = p_nt * (1 - t) is checked, not assumed.

Plan: reports/2026-11-03-x125c-ties-plan.md.

    python scripts/x125c_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x125c_ties.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X113_DEPTH = {0.030: 1.479, 0.040: 2.213}
X93_FRACTION = {0.030: 0.530, 0.040: 0.401}
TIE_TOL = 1e-9
MIN_NON_TIED = 300
HEREDITY_FLOOR = 0.35
TOL = 0.10
BOOTSTRAP = 2000


def boot(vals, seed=1253):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def cell_stats(flow: float) -> dict:
    diffs, heredity, d_diff = [], [], []
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        memo: dict[int, int] = {}
        lives: dict[int, float] = {}

        def life(u: int) -> float:
            if u not in lives:
                lives[u] = life_of(w, u)
            return lives[u]

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
                    if w["peak"][a]["area"] >= w["peak"][b]["area"]:
                        big, small = a, b
                    else:
                        big, small = b, a
                    gb, gs = life(big), life(small)
                    if gb <= 0 or gs <= 0:
                        continue
                    diffs.append(gb - gs)
                    d_diff.append(depth_of(children, big, memo) - depth_of(children, small, memo))

    ties = [d for d in diffs if d == 0]
    non_tied = [d for d in diffs if d != 0]
    pos_nt = [d for d in non_tied if d > 0]
    n, n_nt = len(diffs), len(non_tied)
    t = len(ties) / n if n else None
    p_nt = len(pos_nt) / n_nt if n_nt else None
    p_all = len([d for d in diffs if d > 0]) / n if n else None
    identity = round(p_nt * (1 - t), 12) if (p_nt is not None and t is not None) else None
    return {
        "pairs": n, "ties": len(ties), "tie_share": round(t, 4) if t is not None else None,
        "non_tied": n_nt,
        "p_nt": round(p_nt, 4) if p_nt is not None else None,
        "p_nt_ci": boot([1.0 if d > 0 else 0.0 for d in non_tied]),
        "p_all": round(p_all, 4) if p_all is not None else None,
        "identity_p_nt_x_1_minus_t": identity,
        "identity_gap": abs(identity - p_all) if identity is not None else None,
        "mean_diff_non_tied": round(st.mean(non_tied), 3) if non_tied else None,
        "mean_diff_non_tied_ci": boot(non_tied, seed=1254),
        "d_mean": round(st.mean(d_diff), 3) if d_diff else None,
        "d_mean_ci": boot(d_diff, seed=1255),
        "rho_heredity": round(spearman([p[0] for p in heredity], [p[1] for p in heredity]), 3) if heredity else None,
        "x93_fraction": X93_FRACTION[flow],
        "refs": {"depth": X113_DEPTH[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X125c tie rule")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad, disagrees = [], []
    for tag, c in cells.items():
        if c["non_tied"] < MIN_NON_TIED:
            bad.append(f"{tag}: {c['non_tied']} non-tied pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["identity_gap"] is None or c["identity_gap"] > TIE_TOL:
            bad.append(f"{tag}: identity gap {c['identity_gap']}")
        ref_depth = c["refs"]["depth"]
        if c["d_mean"] is None or abs(c["d_mean"] - ref_depth) > TOL * abs(ref_depth):
            bad.append(f"{tag}: depth {c['d_mean']} misses X113's {ref_depth}")
        if c["p_nt_ci"] and not (c["p_nt_ci"][0] <= c["x93_fraction"] <= c["p_nt_ci"][1]):
            disagrees.append(f"{tag}: p_nt {c['p_nt']} (CI {c['p_nt_ci']}) excludes X93's {c['x93_fraction']}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    elif disagrees:
        verdict = ("the contradiction stands: " + "; ".join(disagrees) + " — the two series disagree about the direction of the "
                   "generation-time contrast, so the disagreement is a property of the worlds, not of the vocabulary")
    else:
        lat, maz = cells["f030"], cells["f040"]
        verdict = (
            f"the tie rule was the whole gap: ties are {lat['tie_share']:.1%} / {maz['tie_share']:.1%} of pairs, and with ties removed the "
            f"larger sister's generation time is longer in {lat['p_nt']:.1%} (CI {lat['p_nt_ci']}) / {maz['p_nt']:.1%} (CI {maz['p_nt_ci']}) "
            f"of pairs, which brackets X93's {lat['x93_fraction']} / {maz['x93_fraction']}. Counting ties as 'not larger' gives "
            f"{lat['p_all']:.1%} / {maz['p_all']:.1%} — the same pairs, two statistics, and the earlier comparison set the tie-excluded "
            f"proportion against the tie-counted one. "
            f"Tie-excluded mean difference: {lat['mean_diff_non_tied']} (CI {lat['mean_diff_non_tied_ci']}) / "
            f"{maz['mean_diff_non_tied']} (CI {maz['mean_diff_non_tied_ci']})."
        )

    res = {
        "kind": "l1_field_x125c_ties",
        "experiment": "X125c",
        "command": "python scripts/x125c_analyse.py --write",
        "prereg": "reports/2026-11-03-x125c-ties-plan.md",
        "definitions": {
            "tie_share": "fraction of sister pairs with identical generation times, in logged steps",
            "p_nt": "fraction of non-tied pairs in which the larger sister's generation time is longer (X93's rule)",
            "p_all": "the same fraction with ties in the denominator counted as 'not larger' (X125b's rule)",
            "identity": "p_all = p_nt * (1 - tie_share), checked to 1e-9",
        },
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x125c] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: pairs={c['pairs']} ties={c['ties']} ({c['tie_share']}) non_tied={c['non_tied']} "
              f"p_nt={c['p_nt']} {c['p_nt_ci']} (X93 {c['x93_fraction']}) p_all={c['p_all']} "
              f"identity_gap={c['identity_gap']:.2e} mean_nt={c['mean_diff_non_tied']} {c['mean_diff_non_tied_ci']} "
              f"depth={c['d_mean']} (X113 {c['refs']['depth']}) heredity={c['rho_heredity']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
