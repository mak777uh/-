"""x120_analyse.py — X120: cost of division or time to divide? Daughters counted in a fixed early window.

`alive ~ 1 + log(area) + daughters_1000 + start`, with daughters counted only within 1 000 steps of each uid's birth, so a long life gives no advantage in the
count. World-level bootstrap. Plan: reports/2026-11-03-x120-window-daughters-plan.md.

    python scripts/x120_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x120_window_daughters.json"

CELLS = {"f030": 0.030, "f040": 0.040}
WINDOW = 1000
MIN_UIDS = 800
HEREDITY_FLOOR = 0.35
CORR_MAX = 0.8
BOOTSTRAP = 500
KEYS = ("log_area", "daughters_1000", "start")


def fit(rows: list[dict]) -> dict | None:
    if len(rows) < 10:
        return None
    X = np.array([[1.0, r["log_area"], r["daughters_1000"], r["start"]] for r in rows])
    y = np.array([r["alive"] for r in rows])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {"intercept": float(beta[0]), **{k: float(b) for k, b in zip(KEYS, beta[1:])}}


def cell_stats(flow: float) -> dict:
    heredity = []
    rows: list[dict] = []
    worlds: list[list[dict]] = []
    life_daughters: list[float] = []
    early_daughters: list[float] = []
    excluded = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        first = {uid: int(info["step"]) for uid, info in w["first"].items()}
        last_step = max(w["per_step"]) if w["per_step"] else 0
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])}
        world_rows = []
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        for uid, info in w["peak"].items():
            start = first.get(uid)
            area = float(info["area"] or 0)
            if start is None or area <= 0:
                continue
            if start + WINDOW > last_step:
                excluded += 1
                continue
            kids = children.get(uid, [])
            early = sum(1 for k in kids if first.get(k) is not None and first[k] <= start + WINDOW)
            row = {"log_area": float(np.log(area)), "daughters_1000": float(early),
                   "start": float(start) / 1000.0, "alive": int(uid in present)}
            rows.append(row)
            world_rows.append(row)
            early_daughters.append(early)
            life_daughters.append(len(kids))
        worlds.append(world_rows)
    base = fit(rows)
    rng = random.Random(120)
    boots = []
    for _ in range(BOOTSTRAP):
        sample = []
        for _ in range(len(worlds)):
            sample.extend(rng.choice(worlds))
        f = fit(sample)
        if f:
            boots.append(f)

    def ci(key):
        vals = sorted(b[key] for b in boots)
        if not vals:
            return None
        lo = max(0, min(len(vals) - 1, int(0.025 * len(vals))))
        hi = max(0, min(len(vals) - 1, int(0.975 * len(vals)) - 1))
        return [round(vals[lo], 4), round(vals[hi], 4)]

    corr = spearman(early_daughters, life_daughters) if early_daughters else None
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {"uids": len(rows), "excluded_late_births": excluded, "rho_heredity": round(rho, 3) if rho is not None else None,
            "corr_early_vs_life": round(corr, 3) if corr is not None else None,
            "alive_rate": round(st.mean([r["alive"] for r in rows]), 4) if rows else None,
            **{f"coef_{k}": (round(base[k], 4) if base else None) for k in KEYS},
            **{f"ci_{k}": ci(k) for k in KEYS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X120 windowed daughters")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["uids"] < MIN_UIDS:
            bad.append(f"{tag}: {c['uids']} uids")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["corr_early_vs_life"] is None or c["corr_early_vs_life"] >= CORR_MAX:
            bad.append(f"{tag}: early-vs-life daughter correlation {c['corr_early_vs_life']} ≥ {CORR_MAX}")

    def excl(c, key):
        ci = c[f"ci_{key}"]
        return bool(ci and (ci[0] > 0 or ci[1] < 0))

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        survives = all(excl(c, "daughters_1000") and (c["coef_daughters_1000"] or 0) < 0 for c in (lat, maz))
        gone = all(not excl(c, "daughters_1000") for c in (lat, maz))
        start_neg = all(excl(c, "start") and (c["coef_start"] or 0) < 0 for c in (lat, maz))
        if survives:
            verdict = (f"a cost of division survives the time control: the early daughter count is negative in both cells "
                       f"({lat['coef_daughters_1000']} with CI {lat['ci_daughters_1000']}; {maz['coef_daughters_1000']} with "
                       f"CI {maz['ci_daughters_1000']})")
        elif gone:
            verdict = (f"the negative sign was time: with the count windowed the coefficient is {lat['coef_daughters_1000']} "
                       f"(CI {lat['ci_daughters_1000']}) and {maz['coef_daughters_1000']} (CI {maz['ci_daughters_1000']}), both containing zero")
        else:
            verdict = (f"mixed: lattice {lat['coef_daughters_1000']} (CI {lat['ci_daughters_1000']}), maze "
                       f"{maz['coef_daughters_1000']} (CI {maz['ci_daughters_1000']})")
        if start_neg:
            verdict += ("; note: start time itself is negative and excludes zero, so the model is finding that later-born structures are less likely to be "
                        "present at the end")
        verdict += (f"; area {lat['coef_log_area']} / {maz['coef_log_area']}, early-vs-life correlation {lat['corr_early_vs_life']} / "
                    f"{maz['corr_early_vs_life']}")

    res = {
        "kind": "l1_field_x120_window_daughters",
        "experiment": "X120",
        "command": "python scripts/x120_analyse.py --write",
        "prereg": "reports/2026-11-03-x120-window-daughters-plan.md",
        "model": "alive ~ 1 + log(area) + daughters_1000 + start, world-level bootstrap (500 draws)",
        "window": WINDOW,
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x120] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: uids={c['uids']} (excluded {c['excluded_late_births']}) alive={c['alive_rate']} heredity={c['rho_heredity']} "
              f"early~life={c['corr_early_vs_life']} | area {c['coef_log_area']} {c['ci_log_area']} | "
              f"daughters_1000 {c['coef_daughters_1000']} {c['ci_daughters_1000']} | start {c['coef_start']} {c['ci_start']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
