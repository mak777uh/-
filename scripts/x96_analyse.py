"""x96_analyse.py — X96 pilot: does a second diffusive species move the pattern's scale?

Readouts per setting, all from the final field and the run log:
  * q' — the axis-aligned wavenumber of maximum power (field_metrics.angular, q_max = 14), the line's scale coordinate;
  * symmetry s — the same function's orientation coordinate, because a scale channel that also moves orientation is a different claim;
  * components and peak amplitude at the end — health, so a dead field cannot look like a shifted scale;
  * max|dv| against the w-off control — the manipulation check (the third field must touch the dynamics).

Plan: reports/2026-11-02-x96-second-species-plan.md. Registered criterion: q' must leave the 5-9 band by two units.

    python scripts/x96_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import angular  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x96_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x96_pilot.json"

BAND = (5, 9)          # every forced world so far: X84, X82
MOVE = 2               # one wavenumber unit is noise; two is the criterion
MIN_DV = 0.01          # the manipulation check
MIN_ALIVE = 2          # components at the end
MILD_TAGS = ("dw008_g005", "dw008_g01", "dw008_g02", "dw016_g005", "dw016_g01", "dw016_g02",
             "dw032_g005", "dw032_g01", "dw032_g02")
TAGS = ("dw008_g05", "dw008_g15", "dw016_g05", "dw016_g15", "dw032_g05", "dw032_g15")

PREFIX = "x96pilot"    # X96b switches this to x96bpilot with --mild
FIELDS_DIR = FIELDS


def load(tag: str) -> tuple[np.ndarray | None, dict | None]:
    run = L1 / f"{PREFIX}_{tag}.json"
    field = FIELDS_DIR / f"{PREFIX}_{tag}_t6000.npy"
    d = json.loads(run.read_text(encoding="utf-8")) if run.is_file() else None
    f = np.load(field) if field.is_file() else None
    return f, d


def stats(f: np.ndarray | None, d: dict | None, ref: np.ndarray | None) -> dict:
    out: dict = {}
    if f is not None:
        a = angular(f, forcing_q=8, q_max=14)
        out.update({"q": a.get("q_axis"),
                    "symmetry": round(float(a["symmetry"]), 3) if a.get("symmetry") is not None else None,
                    "field_std": round(float(a.get("field_std") or 0.0), 5)})
        if ref is not None:
            out["max_dv_vs_w_off"] = round(float(np.abs(f - ref).max()), 4)
    if d is not None:
        last = (d.get("series") or [{}])[-1]
        out["components_end"] = last.get("components")
        out["v_max_end"] = round(float(last.get("v_max") or 0.0), 4) if last.get("v_max") is not None else None
        p = d.get("params") or {}
        out["Dw"], out["gamma"] = p.get("Dw"), p.get("gamma")
    return out


def main(argv=None) -> int:
    global PREFIX, FIELDS_DIR, OUT
    ap = argparse.ArgumentParser(description="X96 pilot analysis")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--mild", action="store_true", help="X96b: the mild sweep (gamma 0.05-0.20)")
    args = ap.parse_args(argv)

    tags = TAGS
    if args.mild:
        PREFIX, FIELDS_DIR = "x96bpilot", L1 / "_x96b_fields"
        OUT = OUT.parent / "l1_field_x96b_pilot.json"
        tags = MILD_TAGS

    ref_field, ref_run = load("w_off")
    rows = {}
    for tag in ("w_off",) + tags:
        f, d = load(tag)
        if f is None and d is None:
            continue
        rows[tag] = stats(f, d, ref_field)

    control_q = (rows.get("w_off") or {}).get("q")
    control_ok = control_q is not None and BAND[0] <= control_q <= BAND[1]
    settings = {k: v for k, v in rows.items() if k != "w_off"}
    dead = [k for k, v in settings.items() if (v.get("components_end") or 0) < MIN_ALIVE]
    live = {k: v for k, v in settings.items() if k not in dead}
    moved = [k for k, v in live.items()
             if v.get("q") is not None and (v["q"] <= BAND[0] - MOVE or v["q"] >= BAND[1] + MOVE)]
    # the manipulation check does not need a live pattern: max|dv| against w_off answers "did the third field touch the field"
    touched = [k for k, v in settings.items() if (v.get("max_dv_vs_w_off") or 0) >= MIN_DV]

    if not rows:
        verdict = "void: nothing to read — the pilot has not run"
    elif not control_ok:
        verdict = f"void: the w-off control's q' = {control_q} is outside the 5-9 band, so the seed is anomalous"
    elif not touched:
        verdict = ("void: the third field does not reach the dynamics (max|dv| < 0.01 in every setting) — a dead term, "
                   "not a channel")
    elif dead:
        verdict = (f"void: the coupling is a regime change, not a perturbation — the field collapses to fewer than "
                   f"{MIN_ALIVE} components in {sorted(dead)} (max|dv| up to "
                   f"{max((settings[k].get('max_dv_vs_w_off') or 0) for k in dead):.2f}), so a weaker coupling must be swept "
                   f"before any scale statement")
    elif moved:
        verdict = (f"the scale channel exists: q' leaves the 5-9 band by at least two units in {sorted(moved)}, with a live "
                   f"field in each")
    elif all(v.get("q") is not None and BAND[0] <= v["q"] <= BAND[1] for v in live.values()):
        verdict = ("the channel does not move the scale: every live setting keeps q' inside 5-9 while the third field does reach "
                   "the dynamics — this closes the fourth and last candidate")
    else:
        verdict = "not decided: q' moves by less than two units somewhere; the pilot says what to sweep next"

    res = {
        "kind": "l1_field_x96_pilot",
        "experiment": "X96",
        "command": "python scripts/x96_analyse.py --write",
        "prereg": "reports/2026-11-02-x96-second-species-plan.md",
        "rule": "uvv = u*v*v/(1+gamma*w); dw/dt = Dw*lap(w) + beta_w*(v - w); w(0) = v(0)",
        "readout": "q' and s from field_metrics.angular on the final field, components and peak at the end, max|dv| against w_off",
        "band": list(BAND),
        "criterion_move": MOVE,
        "min_manipulation": MIN_DV,
        "cells": rows,
        "positive_control": {"fires": bool(control_ok), "control_q": control_q,
                             "note": "the w-off run's q' must sit inside the 5-9 band every forced world has shown"},
        "manipulation_check": {"reaches": touched, "threshold": MIN_DV},
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x96] written: {OUT.name}")
    for k, v in rows.items():
        print(f"  {k}: q'={v.get('q')} s={v.get('symmetry')} comps={v.get('components_end')} "
              f"max_dv={v.get('max_dv_vs_w_off')} (Dw={v.get('Dw')}, gamma={v.get('gamma')})")
    print("  control:", control_ok, "| manipulation:", sorted(touched))
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
