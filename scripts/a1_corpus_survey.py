"""A1: survey the whole artifact corpus - what do we actually have?

The repository holds over a thousand artifact JSONs and five hundred reports, and we have never looked
at them AS A WHOLE. This script builds one table of every run artifact and answers:

  - how many artifacts, how many runs, how many distinct series;
  - which parameters each series varies (so we know what the corpus can answer);
  - which artifacts FAIL the design checks we have learned to apply (R1, saturation, equal dose);
  - which (density x mobility x recovery) combinations are MISSING from the data.

Output: a JSON summary plus a printed table. Read-only: nothing is modified.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
POND = REPO / "morphogenesis" / "experiments" / "E09_pond"


def load(path):
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def is_run_artifact(data) -> bool:
    return isinstance(data, dict) and ("rows" in data or "summary" in data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(POND / "a1_corpus_survey.json"))
    ap.add_argument("--limit", type=int, default=25)
    args = ap.parse_args(argv)

    artifacts = []
    for path in sorted(POND.glob("*.json")):
        data = load(path)
        if not is_run_artifact(data):
            continue
        rows = data.get("rows") or []
        artifacts.append({
            "file": path.name,
            "kind": data.get("kind"),
            "n_rows": len(rows),
            "keys": sorted(set(k for r in rows[:3] for k in r.keys())) if rows else [],
            "data": data,
        })

    # ---- basic counts
    total_rows = sum(a["n_rows"] for a in artifacts)
    kinds = Counter(a["kind"] for a in artifacts)
    print(f"[a1] artifacts: {len(artifacts)} | run rows: {total_rows} | distinct kinds: {len(kinds)}")

    # ---- design checks over every row
    r1_fail = 0
    r1_total = 0
    sat_fail = 0
    dose_mismatch = 0
    dose_total = 0
    for a in artifacts:
        for r in a["data"].get("rows") or []:
            if "R1" in r:
                r1_total += 1
                if not r["R1"]:
                    r1_fail += 1
            peak = r.get("peak_fav")
            if peak is not None and peak > 0.85:
                sat_fail += 1
            if "dose_actual" in r and "dose_nominal" in r:
                dose_total += 1
                nom = r["dose_nominal"]
                if nom and r["dose_actual"] < 0.85 * nom:
                    dose_mismatch += 1
    print(f"[a1] R1 failures: {r1_fail}/{r1_total}")
    print(f"[a1] saturated rows (peak_fav > 0.85): {sat_fail}")
    print(f"[a1] clipped-dose rows: {dose_mismatch}/{dose_total}")

    # ---- coverage of the (density x mobility x recovery) grid
    dens_vals, mob_vals, reg_vals = set(), set(), set()
    cells = set()
    for a in artifacts:
        for r in a["data"].get("rows") or []:
            d = r.get("density_cells")
            m = r.get("moves_per_step")
            g = r.get("resource_regen")
            if d is not None:
                dens_vals.add(d)
            if m is not None:
                mob_vals.add(m)
            if g is not None:
                reg_vals.add(g)
            if d is not None and m is not None and g is not None:
                cells.add((d, m, g))
    print(f"[a1] densities seen: {sorted(dens_vals)}")
    print(f"[a1] mobilities seen: {sorted(mob_vals)}")
    print(f"[a1] recoveries seen: {sorted(reg_vals)}")
    print(f"[a1] grid cells covered: {len(cells)}")

    # ---- which artifacts carry which parameters (what the corpus can answer)
    param_use = defaultdict(set)
    for a in artifacts:
        for r in (a["data"].get("rows") or [])[:3]:
            for k in r.keys():
                param_use[k].add(a["file"])
    top_params = sorted(param_use.items(), key=lambda kv: -len(kv[1]))[: args.limit]
    print("\n[a1] most common row fields (field -> how many artifacts use it):")
    for k, files in top_params:
        print(f"   {k:24s} {len(files)}")

    out = {
        "kind": "a1_corpus_survey",
        "artifacts": len(artifacts),
        "run_rows": total_rows,
        "kinds": dict(kinds),
        "design_checks": {
            "r1_fail": r1_fail, "r1_total": r1_total,
            "saturated_rows": sat_fail,
            "clipped_dose_rows": dose_mismatch, "dose_rows": dose_total,
        },
        "coverage": {
            "densities": sorted(dens_vals), "mobilities": sorted(mob_vals),
            "recoveries": sorted(reg_vals), "grid_cells": len(cells),
        },
        "param_use": {k: len(v) for k, v in param_use.items()},
        "files": [{"file": a["file"], "kind": a["kind"], "n_rows": a["n_rows"]} for a in artifacts],
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\n[a1] written {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
