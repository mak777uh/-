"""x116_analyse.py — X116: is the survival advantage mechanical?

Match sister pairs on the number of daughters and compare survival among the matched ones. If the advantage survives, it is not the branch count.
Plan: reports/2026-11-03-x116-matched-plan.md.

    python scripts/x116_analyse.py --write
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x116_matched.json"

CELLS = {"f030": 0.030, "f040": 0.040}
X115_SURVIVAL = {0.030: 0.2496, 0.040: 0.1372}
SURVIVAL_TOL = 0.05
MIN_MATCHED = 200
HEREDITY_FLOOR = 0.35
RESOLUTION = 0.10
BOOTSTRAP = 2000


def descendants(children, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(children.get(node, []))
    return out


def bootstrap_ci(vals, seed=116):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    return [round(means[int(0.025 * BOOTSTRAP)], 4), round(means[int(0.975 * BOOTSTRAP)], 4)]


def cell_stats(flow: float) -> dict:
    heredity = []
    full, matched = [], []
    n_diff_full, n_diff_matched = [], []
    only_big = only_small = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        last_step = max(w["per_step"]) if w["per_step"] else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for mother, daughters in children.items():
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    na, ns = len(children.get(big, [])), len(children.get(small, []))
                    alive_big = any(u in present for u in descendants(children, big))
                    alive_small = any(u in present for u in descendants(children, small))
                    diff = int(alive_big) - int(alive_small)
                    full.append(diff)
                    n_diff_full.append(na - ns)
                    if na == ns:
                        matched.append(diff)
                        n_diff_matched.append(0)
                        if alive_big and not alive_small:
                            only_big += 1
                        elif alive_small and not alive_big:
                            only_small += 1
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "pairs_full": len(full), "pairs_matched": len(matched),
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "full_diff_mean": round(st.mean(full), 4) if full else None,
        "matched_diff_mean": round(st.mean(matched), 4) if matched else None,
        "matched_diff_ci": bootstrap_ci(matched),
        "n_diff_full": round(st.mean(n_diff_full), 3) if n_diff_full else None,
        "n_diff_matched": round(st.mean(n_diff_matched), 3) if n_diff_matched else None,
        "only_bigger": only_big, "only_smaller": only_small,
        "x115_reference": X115_SURVIVAL[flow],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X116 matched-branch test")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        ref = c["x115_reference"]
        if c["pairs_matched"] < MIN_MATCHED:
            bad.append(f"{tag}: only {c['pairs_matched']} matched pairs")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["full_diff_mean"] is None or abs(c["full_diff_mean"] - ref) > SURVIVAL_TOL * abs(ref):
            bad.append(f"{tag}: full-sample {c['full_diff_mean']} misses X115's {ref}")
        if c["n_diff_matched"] != 0:
            bad.append(f"{tag}: matching failed, mean n difference {c['n_diff_matched']}")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        holds = all(c["matched_diff_ci"] and c["matched_diff_ci"][0] > 0 for c in (lat, maz))
        gone = all(c["matched_diff_ci"] and c["matched_diff_ci"][0] <= 0 <= c["matched_diff_ci"][1] for c in (lat, maz))
        if holds:
            verdict = (f"the advantage is not branch count: among pairs matched on the number of daughters the larger sister still survives "
                       f"{lat['matched_diff_mean']:.3f} more often (CI {lat['matched_diff_ci']}) in the lattice and {maz['matched_diff_mean']:.3f} "
                       f"in the maze (CI {maz['matched_diff_ci']})")
        elif gone:
            verdict = (f"the advantage was branch count: matched on the number of daughters the difference is {lat['matched_diff_mean']:.3f} "
                       f"(CI {lat['matched_diff_ci']}) and {maz['matched_diff_mean']:.3f} (CI {maz['matched_diff_ci']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['matched_diff_mean']:.3f} (CI {lat['matched_diff_ci']}), maze {maz['matched_diff_mean']:.3f} "
                       f"(CI {maz['matched_diff_ci']})")
        verdict += (f"; matched pairs {lat['pairs_matched']} / {maz['pairs_matched']}, mean n difference "
                    f"{lat['n_diff_full']} before matching against 0.0 after")

    res = {
        "kind": "l1_field_x116_matched",
        "experiment": "X116",
        "command": "python scripts/x116_analyse.py --write",
        "prereg": "reports/2026-11-03-x116-matched-plan.md",
        "readout": "survival difference among sister pairs matched on the number of daughters",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x116] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: full={c['pairs_full']} matched={c['pairs_matched']} heredity={c['rho_heredity']} "
              f"full diff={c['full_diff_mean']} matched diff={c['matched_diff_mean']} (CI {c['matched_diff_ci']}) "
              f"n diff {c['n_diff_full']} -> {c['n_diff_matched']}, onlyBig/onlySmall={c['only_bigger']}/{c['only_smaller']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
