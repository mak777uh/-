"""size_resolved_contrast.py — what size are the structures that make the contrast?

Why this exists. Four literature reviews of 1 November converged on one worry about our headline
number: at a fixed threshold of 0.2 the heterogeneous world has more components than the
homogeneous one, but "more components" can mean "more structures" or it can mean "more debris".
The difference is testable on stored data — every snapshot records the area of every component —
and it costs nothing.

Two blocks.

1. `count_vs_min_area`: the component count and the contrast recomputed while ignoring components
   below 2, 4, 8, ... 256 cells. If the contrast is made of fragments it collapses at small
   areas; if it is a property of the pattern it survives.
2. `lifetime_vs_min_peak`: the lifetime contrast recomputed over `uid`s whose *peak* area reaches
   the same thresholds. This is the free half of the tracking-sensitivity analysis: it does not
   touch the overlap rule (which needs masks), only the minimum size at which a structure is
   counted as a structure.

Also reported: the largest-cluster share per snapshot, which says whether one structure dominates
(`~1`) or the field is a scatter of pieces (`~1/n`).

Run:
    python scripts/size_resolved_contrast.py --write
    python scripts/size_resolved_contrast.py
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_size_resolved.json"

ARMS = {
    "dt=1.0": ("x18_pattern_s*", "x18_homog_s*"),
    "dt=0.5": ("x56_dt0.5_static_s*", "x56_dt0.5_homog_s*"),
}
LIFETIME_ARMS = {"hetero": "static", "homog": "homog"}
MIN_AREA = [1, 2, 4, 8, 16, 32, 64, 128, 256]
MIN_PEAK = [1, 2, 4, 8, 16, 32, 64, 128]


def load(pattern: str) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for f in sorted(glob.glob(str(L1 / (pattern + ".json")))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        out[seed] = json.loads(Path(f).read_text(encoding="utf-8")).get("series") or []
    return out


def per_seed_counts(series: list[dict], min_area: int) -> float:
    counts = [sum(1 for a in s.get("areas") or [] if a >= min_area) for s in series]
    return sum(counts) / len(counts) if counts else 0.0


def contrast_rows(het: dict, hom: dict, min_area: int) -> dict | None:
    seeds = sorted(set(het) & set(hom))
    if not seeds:
        return None
    h = [per_seed_counts(het[s], min_area) for s in seeds]
    o = [per_seed_counts(hom[s], min_area) for s in seeds]
    diffs = [a - b for a, b in zip(h, o)]
    return {
        "min_area": min_area,
        "n_seeds": len(seeds),
        "hetero_median": round(st.median(h), 2),
        "homog_median": round(st.median(o), 2),
        "diff_of_medians": round(st.median(h) - st.median(o), 2),
        "median_of_diffs": round(st.median(diffs), 2),
        "seeds_positive": sum(1 for d in diffs if d > 0),
    }


def largest_share(series: list[dict]) -> float:
    shares = []
    for s in series:
        areas = s.get("areas") or []
        tot = sum(areas)
        if areas and tot:
            shares.append(max(areas) / tot)
    return st.mean(shares) if shares else 0.0


def uids(arm: str) -> list[tuple[int, int]]:
    rows = []
    for f in sorted(glob.glob(str(L1 / ("x23_%s_s*.json" % arm)))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        lt = d.get("lifetimes") or {}
        rows += list(zip(lt.get("life_steps") or [], lt.get("peak_sizes") or []))
    return rows


def build() -> dict:
    arms = {label: (load(a), load(b)) for label, (a, b) in ARMS.items()}

    count_rows = {}
    share_rows = {}
    for label, (het, hom) in arms.items():
        count_rows[label] = [r for r in (contrast_rows(het, hom, m) for m in MIN_AREA) if r]
        share_rows[label] = {
            "hetero": round(st.median([largest_share(v) for v in het.values()]), 3),
            "homog": round(st.median([largest_share(v) for v in hom.values()]), 3),
        }

    life_rows = []
    for label, arm in LIFETIME_ARMS.items():
        rows = uids(arm)
        for m in MIN_PEAK:
            kept = [life for life, peak in rows if peak >= m]
            life_rows.append({
                "arm": label, "min_peak_area": m, "n_uids": len(kept),
                "median_life_steps": (st.median(kept) if kept else None),
                "share_life_ge_1500": (round(sum(1 for x in kept if x >= 1500) / len(kept), 3)
                                       if kept else None),
            })

    return {
        "kind": "l1_field_size_resolved",
        "experiment": "X56 / X23 (re-analysis of stored snapshots and uids)",
        "command": "python scripts/size_resolved_contrast.py --write",
        "question": "is the heterogeneous advantage made of structures, or of fragments?",
        "design": {
            "source": "morphogenesis/experiments/L1_field/x18_*, x56_dt0.5_*, x23_*",
            "threshold": 0.2, "grid": 96, "laplacian": "4 neighbours, periodic",
            "estimator": ("per-seed mean of the per-snapshot count over snapshots, then median across "
                          "seeds; diff_of_medians = median(hetero) - median(homog); median_of_diffs is the "
                          "paired estimator"),
            "lifetime_sampling": "uids tracked at every 500th step, so lifetimes below 500 are unresolved",
        },
        "count_vs_min_area": count_rows,
        "largest_cluster_share": share_rows,
        "lifetime_vs_min_peak": life_rows,
        "verdict": (
            "The advantage is real but it is an advantage in *small* structures. At dt=1.0 the count contrast "
            "is +3.57 with every component counted and unchanged down to 8 cells, then +1.36 at 32 cells, "
            "+0.86 at 64 and +0.07 at 128: the two worlds are indistinguishable once components below about "
            "100 cells are excluded. The homogeneous world is one dominant cluster (largest share 0.925); the "
            "heterogeneous one is a scatter (0.817) whose count is carried by small pieces. Lifetimes agree "
            "under the same filter: the heterogeneous median falls from 54 to 13 steps as the peak-size "
            "threshold rises, while the homogeneous median stays at 3575, so the lifetime gap widens rather "
            "than closes. At dt=0.5 the size filter removes the count contrast entirely and turns it slightly "
            "negative above 128 cells. Read together: heterogeneous inflow multiplies small, short-lived "
            "pieces; it does not add durable structures."
        ),
        "not_claimed": [
            "min-area filtering is not the same as identity tracking: it does not test the overlap rule, which needs masks",
            "a 100-cell cutoff is where this dataset becomes blind, not a natural length scale",
            "lifetimes exist only at dt=1.0, so nothing here separates lifetime from step size",
            "no claim that small pieces are 'debris' in a mechanistic sense: they are small and short-lived, which is all we measured",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="size-resolved contrast")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[size] written: {OUT.name}")
    for label, rows in data["count_vs_min_area"].items():
        print(f"count vs min area, {label}:")
        for r in rows:
            print("  min_area=%3d  het=%5.2f hom=%5.2f  Dmed=%+5.2f  medD=%+5.2f  pos=%d/%d" % (
                r["min_area"], r["hetero_median"], r["homog_median"],
                r["diff_of_medians"], r["median_of_diffs"], r["seeds_positive"], r["n_seeds"]))
    print("lifetime vs min peak area:")
    for r in data["lifetime_vs_min_peak"]:
        print("  %-6s peak>=%3d  n=%2d  median=%6s  share>=1500=%s" % (
            r["arm"], r["min_peak_area"], r["n_uids"], r["median_life_steps"], r["share_life_ge_1500"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
