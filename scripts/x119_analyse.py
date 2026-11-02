"""x119_analyse.py — X119: does the daughter count predict survival with size held statistically?

X118's matched design could not run: near-equal-area sisters with different daughter counts barely exist. This separates the two with a linear probability
model instead — pool every uid and fit `alive ~ log(area) + daughters`, with a bootstrap over worlds for the intervals — so the whole cloud is used and each
coefficient is estimated with the other held fixed.

Plan: reports/2026-11-03-x119-model-plan.md.

    python scripts/x119_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x119_model.json"

CELLS = {"f030": 0.030, "f040": 0.040}
HEREDITY_FLOOR = 0.35
BOOTSTRAP = 500
MIN_UIDS = 300


def fit(rows: list[dict]) -> dict:
    """OLS of alive on [1, log area, daughters]; returns coefficients."""
    X = np.array([[1.0, r["log_area"], r["daughters"]] for r in rows])
    y = np.array([r["alive"] for r in rows])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {"intercept": float(beta[0]), "log_area": float(beta[1]), "daughters": float(beta[2])}


def cell_stats(flow: float) -> dict:
    heredity = []
    rows: list[dict] = []
    worlds: list[list[dict]] = []
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        last_step = max(w["per_step"]) if w["per_step"] else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        world_rows = []
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for uid, info in w["peak"].items():
            area = float(info["area"] or 0)
            if area <= 0:
                continue
            # alive if the uid itself is present at the end (its own survival, not the subtree's)
            row = {"log_area": float(np.log(area)), "daughters": float(len(children.get(uid, []))),
                   "alive": int(uid in present)}
            rows.append(row)
            world_rows.append(row)
        worlds.append(world_rows)
    base = fit(rows) if len(rows) >= 10 else None
    rng = random.Random(119)
    boots = []
    if base:
        for _ in range(BOOTSTRAP):
            sample = []
            for _ in range(len(worlds)):
                sample.extend(rng.choice(worlds))   # worlds are lists of row dicts
            if len(sample) >= 10:
                boots.append(fit(sample))
    def ci(key):
        vals = sorted(b[key] for b in boots)
        if not vals:
            return None
        return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)]
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {"uids": len(rows), "rho_heredity": round(rho, 3) if rho is not None else None,
            "coef_log_area": round(base["log_area"], 4) if base else None, "coef_log_area_ci": ci("log_area"),
            "coef_daughters": round(base["daughters"], 4) if base else None, "coef_daughters_ci": ci("daughters"),
            "alive_rate": round(st.mean([r["alive"] for r in rows]), 4) if rows else None,
            "mean_daughters": round(st.mean([r["daughters"] for r in rows]), 3) if rows else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X119 survival model")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["uids"] < MIN_UIDS:
            bad.append(f"{tag}: {c['uids']} uids")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["coef_daughters"] is None:
            bad.append(f"{tag}: the model did not fit")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        def excludes_zero(c, key):
            ci = c[f"{key}_ci"]
            return bool(ci and (ci[0] > 0 or ci[1] < 0))
        d_hat = all(excludes_zero(c, "coef_daughters") for c in (lat, maz))
        d_none = all(not excludes_zero(c, "coef_daughters") for c in (lat, maz))
        a_hat = all(excludes_zero(c, "coef_log_area") for c in (lat, maz))
        parts = [f"daughters {'does' if d_hat else ('does not' if d_none else 'may')} predict survival with size held "
                 f"({lat['coef_daughters']} with CI {lat['coef_daughters_ci']}; {maz['coef_daughters']} with CI {maz['coef_daughters_ci']})"]
        parts.append(f"area {'does' if a_hat else 'does not'} ({lat['coef_log_area']} / {maz['coef_log_area']})")
        verdict = "; ".join(parts)

    res = {
        "kind": "l1_field_x119_model",
        "experiment": "X119",
        "command": "python scripts/x119_analyse.py --write",
        "prereg": "reports/2026-11-03-x119-model-plan.md",
        "model": "alive ~ 1 + log(area) + daughters, OLS with a world-level bootstrap (500 draws)",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x119] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: uids={c['uids']} alive rate={c['alive_rate']} heredity={c['rho_heredity']} "
              f"area coef={c['coef_log_area']} (CI {c['coef_log_area_ci']}) "
              f"daughters coef={c['coef_daughters']} (CI {c['coef_daughters_ci']})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
