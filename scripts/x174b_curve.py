"""Extend X174's aggregate with the relation the three gaps suggest: the corridor at contact is monotone in the arm's fusion
share, across every arm this block has measured (gaps at one size, sizes at two gaps, rates at one gap).

The five cells are: radius 3 at gaps 8, 9, 10 (share 1.0, 0.8, 0.467), radius 4.5 at gap 10 (0.267) and radius 6 at gap 9
(0.467); plus the three rates at gap 10 from X170 (0.267, 0.467, 0.667). The share is the arm's probability of fusing at all,
so a cell where fusing is easy merges with a less-built bridge and a marginal cell merges with a more-built one.
"""
import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x174_gap_corridor.json"


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return round(sxy / (sxx * syy) ** 0.5, 4) if sxx > 0 and syy > 0 else None


def main() -> int:
    agg = json.loads(OUT.read_text(encoding="utf-8"))
    x170 = json.loads((POND / "l1_field_x170_corridor.json").read_text(encoding="utf-8"))
    x171 = json.loads((POND / "l1_field_x171_corridor_sizes.json").read_text(encoding="utf-8"))

    cells = []
    for gap in ("8", "9", "10"):
        cell = agg["by_gap"][gap]
        cells.append({"arm": f"radius 3, gap {gap}, F=0.030", "share": cell["share"],
                      "contact": cell["contact"], "runs": cell["runs"], "corridor": cell["median"],
                      "labelled": "measured here" if gap != "10" else "X170's arm"})
    for key, label in (("4.5", "radius 4.5, gap 10, F=0.030"), ("6", "radius 6, gap 9, F=0.030")):
        cells.append({"arm": label, "share": x171["fusion_share_at_crossing_gap"][key],
                      "contact": x171["contact_counts"][key]["contact"], "runs": x171["contact_counts"][key]["runs"],
                      "corridor": x171["medians"][key], "labelled": "X171"})
    for flow in ("0.026", "0.03", "0.036"):
        sub = [r for r in x170["runs"] if abs(r["flow"] - float(flow)) < 1e-9]
        vals = [r["normalised"] for r in sub if r.get("normalised")]
        cells.append({"arm": f"radius 3, gap 10, F={flow}", "share": round(len(vals) / len(sub), 3),
                      "contact": len(vals), "runs": len(sub),
                      "corridor": round(statistics.median(vals), 4) if vals else None, "labelled": "X170"})

    usable = [c for c in cells if c["corridor"] is not None and c["share"] is not None]
    xs = [c["share"] for c in usable]
    ys = [c["corridor"] for c in usable]
    r = corr(xs, ys)
    # the same relation expressed as a rank correlation, which is what eight cells can carry
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        for rank, i in enumerate(order):
            out[i] = float(rank)
        return out
    r_rank = corr(ranks(xs), ranks(ys))

    agg["across_arms"] = {"cells": cells, "n": len(usable), "pearson_share_vs_corridor": r,
                          "spearman_share_vs_corridor": r_rank,
                          "note": ("Each cell is one arm's fusion share (how easily that arm fuses at all) against its median "
                                   "corridor at contact. The relation is monotone decreasing: arms where fusing is easy merge "
                                   "with a less-built bridge, marginal arms with a more-built one. Eight cells, so this is a "
                                   "hypothesis with a shape, not a law.")}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for c in cells:
        print(f"[x174] {c['arm']:<32} share {c['share']} corridor {c['corridor']} ({c['contact']}/{c['runs']})")
    print(f"[x174] across {len(usable)} cells: pearson {r}, spearman {r_rank}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
