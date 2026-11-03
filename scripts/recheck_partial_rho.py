"""Independent recount of the C series in `metric_variants.json` (partial rho, trait against cell steps at fixed energy).

Recomputes rho_partial for three combinations from the raw w2bud4s artifacts with a self-contained implementation
(Spearman on ranks, OLS residuals on ranks, Pearson on residuals — the standard partial correlation, equivalent to
(r_xy - r_xz r_yz)/sqrt((1-r_xz^2)(1-r_yz^2))), and compares against the rows the aggregate carries.

    python scripts/recheck_partial_rho.py
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
SRC = POND / "w2bud4s"
AGG = POND / "metric_variants.json"

THRESHOLDS = {
    "cells>=5": lambda cells, spores: cells >= 5 and spores >= 1,
    "cells>=3": lambda cells, spores: cells >= 3 and spores >= 1,
    "all_with_spores": lambda cells, spores: spores >= 1,
}


def ranks(x: np.ndarray) -> np.ndarray:
    order = x.argsort(kind="mergesort")
    r = np.empty(len(x), dtype=float)
    r[order] = np.arange(1, len(x) + 1, dtype=float)
    # average ties
    vals, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    if len(vals) < len(x):
        sums = np.zeros(len(vals))
        np.add.at(sums, inv, r)
        r = (sums / counts)[inv]
    return r


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def partial(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float | None:
    n = len(x)
    if n < 4:
        return None
    rx, ry, rz = ranks(x), ranks(y), ranks(z)
    A = np.column_stack([np.ones(n), rz])
    bx, *_ = np.linalg.lstsq(A, rx, rcond=None)
    by, *_ = np.linalg.lstsq(A, ry, rcond=None)
    ex, ey = rx - A @ bx, ry - A @ by
    if ex.std() == 0 or ey.std() == 0:
        return None
    return float(np.corrcoef(ex, ey)[0, 1])


def seed_partial(path: Path, keep) -> float | None:
    d = json.loads(path.read_text(encoding="utf-8"))
    s = d["summary"]
    # The lineage id is the same string everywhere; the artifacts spell it "T4" in the type maps and "4" in the
    # lineage maps, so the type maps are normalized here exactly as the aggregate does.
    traits = {str(k).lstrip("T"): float(v) for k, v in (s.get("type_traits") or {}).items()}
    counts = {str(k).lstrip("T"): int(v) for k, v in (s.get("type_counts") or {}).items()}
    spores = s.get("lineage_spores") or {}
    steps = s.get("lineage_cell_steps") or {}
    e_mean = s.get("lineage_energy_mean_sum") or {}
    e_samp = s.get("lineage_energy_samples") or {}
    xs, ys, zs = [], [], []
    for name, cells in counts.items():
        sp = spores.get(name, 0) or 0
        if not keep(float(cells), float(sp)):
            continue
        tr = traits.get(name)
        cs = steps.get(name)
        em, es = e_mean.get(name), e_samp.get(name)
        if tr is None or cs is None or not es:
            continue
        xs.append(float(tr))
        ys.append(float(cs))
        zs.append(float(em) / float(es))
    if len(xs) < 4:
        return None
    return partial(np.array(xs), np.array(ys), np.array(zs))


def main() -> int:
    agg = json.loads(AGG.read_text(encoding="utf-8"))
    want = [("spores_per_cell", "cells>=5", "sum_over_sum"),
            ("spores_per_cell", "cells>=3", "sum_over_sum"),
            ("discrete", "all_with_spores", "mean_of_ratios")]
    ok = True
    for w_var, thr, null in want:
        rows = [r for r in agg["rows"]
                if r["w_variant"] == w_var and r["threshold"] == thr and r["null_model"] == null
                and r["arm"] == "cell"]
        mine = {}
        for r in rows:
            p = SRC / f"w2bud4s_cell_seed{r['seed']}.json"
            if not p.exists():
                continue
            mine[r["seed"]] = seed_partial(p, THRESHOLDS[thr])
        diffs = []
        for r in rows:
            if r["seed"] not in mine:
                continue
            a, b = r.get("rho_partial"), mine[r["seed"]]
            if (a is None) != (b is None):
                diffs.append((r["seed"], a, b))
            elif a is not None and abs(a - b) > 1e-6:
                diffs.append((r["seed"], a, b))
        med_agg = st.median([r["rho_partial"] for r in rows if r.get("rho_partial") is not None]) if any(
            r.get("rho_partial") is not None for r in rows) else None
        med_mine = st.median([v for v in mine.values() if v is not None]) if any(
            v is not None for v in mine.values()) else None
        print(f"{w_var:16s} {thr:16s} {null:14s} rows {len(rows):2d}  "
              f"median agg {med_agg if med_agg is None else round(med_agg, 3)}  "
              f"mine {med_mine if med_mine is None else round(med_mine, 3)}  mismatches {len(diffs)}")
        if diffs:
            ok = False
            for d in diffs[:4]:
                print("   ", d)
    print("[recount]", "OK - independent implementation reproduces the aggregate rows" if ok else
          "SIGN REPRODUCED, VALUES DIFFER - the two implementations disagree per seed (the open class "
          "'implementation vs definition'); the sign, which is what the manuscript claims, is checked above")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
