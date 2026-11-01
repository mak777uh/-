"""x72c_regions.py — is the mixture a property of regions? (follow-up to X72c, no new runs)

X72c showed that a daughter's band power is predicted better by a neighbouring structure than by her parent, and that the
band power varies across structures with a standard deviation of only ~0.07. That reading implies a spatial prediction which
the existing fields can test without running anything: if the mixture belongs to a region rather than to a structure, then
**structures inside one quadrant of the box should agree with each other more than quadrants agree with each other**.

Statistic: for every snapshot, a one-way ANOVA decomposition of `p_wide` across the four quadrants —
`eta2 = SS_between / SS_total`, the share of the variance that is between regions. `eta2 ≈ 0` means regions are
indistinguishable and the mixture varies structure-by-structure; `eta2` large means the mixture is regional.

Run:
    python scripts/x72c_regions.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x72c_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x72c_regions.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import window_profile, band_powers  # noqa: E402

GRID = 96
QUADRANTS = 4


def quadrant(cx: float, cy: float) -> int:
    return (0 if cx < GRID / 2 else 1) + (0 if cy < GRID / 2 else 2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X72c regional decomposition")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    res = {"kind": "l1_field_x72c_regions", "experiment": "X72c follow-up",
           "command": "python scripts/x72c_regions.py --write",
           "question": "does the band mixture belong to regions rather than to structures?",
           "statistic": "eta^2 = SS_between quadrants / SS_total, per snapshot", "worlds": {}}

    for path in sorted(L1.glob("x72c_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        etas = []
        for s in d.get("series") or []:
            step = int(s["step"])
            f = FIELDS / f"{path.stem}_t{step}.npy"
            if not f.is_file():
                continue
            v = np.load(f)
            groups: dict[int, list[float]] = {}
            for c in (s.get("components_log") or []):
                if c.get("cx") is None:
                    continue
                bp = band_powers(window_profile(v, c["cx"], c["cy"]))
                if bp:
                    groups.setdefault(quadrant(c["cx"], c["cy"]), []).append(bp[0])
            vals = [x for g in groups.values() for x in g]
            if len(vals) < 8 or len(groups) < 3:
                continue
            gm = st.mean(vals)
            ss_total = sum((x - gm) ** 2 for x in vals)
            ss_between = sum(len(g) * (st.mean(g) - gm) ** 2 for g in groups.values())
            if ss_total > 0:
                etas.append(ss_between / ss_total)
        res["worlds"][path.stem.split("_s")[-1]] = {
            "snapshots": len(etas),
            "eta2_median": round(st.median(etas), 3) if etas else None,
            "eta2_p90": round(sorted(etas)[int(0.9 * len(etas)) - 1], 3) if len(etas) >= 10 else None,
        }

    med = [w["eta2_median"] for w in res["worlds"].values() if w["eta2_median"] is not None]
    res["pooled_eta2_median"] = round(st.median(med), 3) if med else None
    res["regions_carry"] = bool(med and st.median(med) >= 0.2)
    res["verdict"] = ("regional: the mixture varies between quadrants more than within them"
                      if res["regions_carry"] else
                      "not regional at this scale: the mixture varies structure by structure")
    res["note"] = ("eta2 = 0.2 means a fifth of the variance of the band power is explained by which quadrant a structure is in; "
                   "the X72c reading predicts eta2 to be substantial, because the neighbour predicts better than the parent")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x72c-regions] written: {OUT.name}")

    for seed, w in res["worlds"].items():
        print(f"  s{seed}: snapshots={w['snapshots']} eta2_median={w['eta2_median']} p90={w['eta2_p90']}")
    print("  pooled eta2:", res["pooled_eta2_median"], "->", res["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
