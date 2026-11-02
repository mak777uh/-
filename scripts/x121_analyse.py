"""x121_analyse.py — X121: discrete-time hazard of disappearing, given age and daughters.

Person-period rows from every logged snapshot: `death ~ 1 + age + daughters_so_far + log_area`, with a world-level bootstrap. Age becomes a predictor instead of
an outcome, which is what the single-snapshot models could not do.
Plan: reports/2026-11-03-x121-hazard-plan.md.

    python scripts/x121_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x121_hazard.json"

CELLS = {"f030": 0.030, "f040": 0.040}
MIN_ROWS = 20000
HEREDITY_FLOOR = 0.35
DEATH_BAND = (0.01, 0.50)
BOOTSTRAP = 500
KEYS = ("age", "daughters", "log_area")


def fit(rows: list[dict]) -> dict | None:
    if len(rows) < 50:
        return None
    X = np.array([[1.0, r["age"], r["daughters"], r["log_area"]] for r in rows])
    y = np.array([r["death"] for r in rows])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {"intercept": float(beta[0]), **{k: float(b) for k, b in zip(KEYS, beta[1:])}}


def cell_stats(flow: float) -> dict:
    heredity = []
    worlds: list[list[dict]] = []
    deaths = uids_total = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        first = {uid: int(info["step"]) for uid, info in w["first"].items()}
        steps = sorted(w["per_step"])
        present_by_step = {s: {int(c["uid"]) for c in w["per_step"][s]} for s in steps}
        area_by_step = {s: {int(c["uid"]): float(c["area"] or 0) for c in w["per_step"][s]} for s in steps}
        for mother, daughters in children.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
        world_rows: list[dict] = []
        born: dict[int, list[int]] = {uid: [] for uid in first}
        for uid, kids in children.items():
            for k in kids:
                if k in first:
                    born.setdefault(uid, []).append(first[k])
        seen_uids = set()
        for i in range(len(steps) - 1):
            s, nxt = steps[i], steps[i + 1]
            for uid in present_by_step[s]:
                if uid not in first:
                    continue
                seen_uids.add(uid)
                area = area_by_step[s].get(uid, 0.0)
                if area <= 0:
                    continue
                daughters = sum(1 for b in born.get(uid, []) if b <= s)
                row = {"age": float(s - first[uid]) / 1000.0, "daughters": float(daughters),
                       "log_area": float(np.log(area)), "death": int(uid not in present_by_step[nxt])}
                world_rows.append(row)
                deaths += row["death"]
        uids_total += len(seen_uids)
        worlds.append(world_rows)
    rows = [r for block in worlds for r in block]
    base = fit(rows)
    rng = random.Random(121)
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

    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {"rows": len(rows), "uids": uids_total, "deaths": deaths,
            "death_rate": round(deaths / len(rows), 4) if rows else None,
            "rho_heredity": round(rho, 3) if rho is not None else None,
            **{f"coef_{k}": (round(base[k], 6) if base else None) for k in KEYS},
            **{f"ci_{k}": ci(k) for k in KEYS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X121 discrete-time hazard")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    bad = []
    for tag, c in cells.items():
        if c["rows"] < MIN_ROWS:
            bad.append(f"{tag}: {c['rows']} rows")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["death_rate"] is None or not (DEATH_BAND[0] <= c["death_rate"] <= DEATH_BAND[1]):
            bad.append(f"{tag}: death rate {c['death_rate']} outside {DEATH_BAND}")

    def excl(c, key):
        ci = c[f"ci_{key}"]
        return bool(ci and (ci[0] > 0 or ci[1] < 0))

    size_ok = any(excl(c, "log_area") and (c["coef_log_area"] or 0) < 0 for c in cells.values())
    if not size_ok and not bad:
        bad.append("the size direction fails: log_area is not negative with an interval excluding zero in any cell")

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lat, maz = cells["f030"], cells["f040"]
        raises = all(excl(c, "daughters") and (c["coef_daughters"] or 0) > 0 for c in (lat, maz))
        flat = all(not excl(c, "daughters") for c in (lat, maz))
        age_pos = all(excl(c, "age") and (c["coef_age"] or 0) > 0 for c in (lat, maz))
        if raises:
            verdict = (f"dividing raises the hazard: the daughters coefficient is positive in both cells "
                       f"({lat['coef_daughters']} with CI {lat['ci_daughters']}; {maz['coef_daughters']} with CI {maz['ci_daughters']}), "
                       f"given age and size")
        elif flat:
            verdict = (f"dividing does not raise the hazard once age is in the model: the daughters coefficient is "
                       f"{lat['coef_daughters']} (CI {lat['ci_daughters']}) and {maz['coef_daughters']} (CI {maz['ci_daughters']}), "
                       f"both containing zero")
        else:
            verdict = (f"mixed: lattice daughters {lat['coef_daughters']} (CI {lat['ci_daughters']}), maze "
                       f"{maz['coef_daughters']} (CI {maz['ci_daughters']})")
        if age_pos:
            verdict += ("; age itself raises the hazard in both cells, which is what the hazard reading predicted")
        verdict += (f"; size {lat['coef_log_area']} / {maz['coef_log_area']}, base death rate {lat['death_rate']} / {maz['death_rate']}")

    res = {
        "kind": "l1_field_x121_hazard",
        "experiment": "X121",
        "command": "python scripts/x121_analyse.py --write",
        "prereg": "reports/2026-11-03-x121-hazard-plan.md",
        "model": "death ~ 1 + age + daughters_so_far + log_area on person-period rows, world-level bootstrap (500 draws)",
        "cells": cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x121] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: rows={c['rows']} uids={c['uids']} deaths={c['deaths']} rate={c['death_rate']} heredity={c['rho_heredity']} | "
              f"age {c['coef_age']} {c['ci_age']} | daughters {c['coef_daughters']} {c['ci_daughters']} | "
              f"size {c['coef_log_area']} {c['ci_log_area']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
