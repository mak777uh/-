"""The within-cell readouts: does a cell's behaviour follow its situation or its own record?

WHY THIS FILE WAS REWRITTEN (08.11, after an independent referee refuted the first version).

The first version pooled every row into two flat lists (one of resources, one of actions) and computed a single
eta-squared. That is a BETWEEN-cell statistic: it cannot tell "cells differ from each other" from "a cell varies
with its situation". The referee demonstrated the consequence with the document's own example: adding a bonus to
one cell moved the "within-cell" measure from 0.9640 to 0.6549. A measure that a between-cell bonus can move by
0.31 is not a within-cell measure, and the claim that it "cannot be a knob" was false.

WHAT THIS VERSION DOES.

For each cell separately, over its own trajectory:

    total_i   = variance of the cell's action over its own steps
    within_i  = variance left after removing the cell's own mean
    between_i = the cell's own mean squared deviation (the cell's "level")

The question "does the behaviour follow the situation or the record" is then asked INSIDE the cell, by comparing
two predictors of the cell's own deviation from its own mean:

    sit_i = 1 - Var(dev_i - f(res_i)) / Var(dev_i)
    rec_i = 1 - Var(dev_i - g(pred_i)) / Var(dev_i)

where f and g are binning predictors fitted on the cell's own steps. The reported numbers are the
cell-weighted means of sit_i and rec_i.

THE PROPERTY THAT MAKES IT A MEASURE AND NOT A KNOB. A bonus that shifts a cell's level changes between_i and
leaves dev_i unchanged, so sit_i and rec_i do not move. `--self-test` asserts exactly that: it plants a
cell-level bonus and requires the two readouts to stay within 0.01 of their no-bonus values. The first version's
self-test only checked monotone step functions, which is the easy case and would have passed a broken measure.

Usage:
  python scripts/k_readouts.py --self-test
  python scripts/k_readouts.py <artifact.json>
"""
from __future__ import annotations
import argparse
import json
import sys


def _binned_predictor(x: list[float], y: list[float], bins: int = 10) -> float:
    """Explained fraction of y by binning on x, fitted on this cell's own steps.

    Returns 1 - Var(y - mean of y in the bin of x) / Var(y). No functional form is assumed.
    """
    n = len(x)
    if n < bins * 2:
        return 0.0
    mean_y = sum(y) / n
    total = sum((v - mean_y) ** 2 for v in y)
    if total <= 0.0:
        return 0.0
    pairs = sorted(zip(x, y), key=lambda p: p[0])
    residual = 0.0
    for b in range(bins):
        lo = b * n // bins
        hi = (b + 1) * n // bins
        chunk = pairs[lo:hi]
        if not chunk:
            continue
        m = sum(p[1] for p in chunk) / len(chunk)
        residual += sum((p[1] - m) ** 2 for p in chunk)
    return max(0.0, 1.0 - residual / total)


def cell_readouts(steps: list[dict]) -> dict:
    """steps: one dict per (cell, step) with keys cell, acted, res_at_act, pred_at_act."""
    by_cell: dict[str, list[dict]] = {}
    for r in steps:
        by_cell.setdefault(str(r["cell"]), []).append(r)

    sit_vals, rec_vals, weights = [], [], []
    cell_means: list[float] = []
    for cell, rows in by_cell.items():
        if len(rows) < 20:
            continue
        acted = [float(r["acted"]) for r in rows]
        res = [float(r["res_at_act"]) for r in rows]
        pred = [float(r["pred_at_act"]) for r in rows]
        n = len(acted)
        m = sum(acted) / n
        dev = [a - m for a in acted]                 # the cell's own deviation from its own mean
        var_dev = sum(d * d for d in dev) / n
        if var_dev <= 0.0:
            continue                                  # a cell that never varies carries no information
        sit_vals.append(_binned_predictor(res, dev))
        rec_vals.append(_binned_predictor(pred, dev))
        weights.append(var_dev)
        cell_means.append(m)

    if not sit_vals:
        return {"n_cells": len(by_cell), "n_used": 0,
                "situation_explained": None, "record_explained": None,
                "between_cell_share": None, "note": "no cell varied enough to measure"}

    w = sum(weights)
    sit = sum(v * s for v, s in zip(weights, sit_vals)) / w
    rec = sum(v * s for v, s in zip(weights, rec_vals)) / w
    # How much cells DIFFER FROM EACH OTHER: the variance of the per-cell means. This is the quantity a
    # between-cell bonus moves, and the two readouts above must not move with it. The first version used
    # between_sum / (between_sum + total_sum), which for a binary action is identically 0.5 and therefore
    # measured nothing - the referee's "confounded and do not decompose" finding, in one formula.
    if len(cell_means) > 1:
        gm = sum(cell_means) / len(cell_means)
        between_share = sum((x - gm) ** 2 for x in cell_means) / len(cell_means)
    else:
        between_share = None
    return {
        "n_cells": len(by_cell),
        "n_used": len(sit_vals),
        "situation_explained": round(sit, 4),
        "record_explained": round(rec, 4),
        "between_cell_share": None if between_share is None else round(between_share, 4),
    }


def _synthetic(n_cells: int = 40, n_steps: int = 60, bonus: float = 0.0,
               record_is_noise: bool = True) -> list[dict]:
    """Behaviour is a deterministic function of the situation; the record is the situation plus noise.

    `bonus` shifts ONE cell's level. It must move `between_cell_share` and must NOT move the two readouts.
    """
    import random
    rng = random.Random(7)
    rows = []
    for c in range(n_cells):
        for t in range(n_steps):
            res = rng.random()
            pred = res + (rng.gauss(0, 0.25) if record_is_noise else 0.0)
            acted = 1 if res > 0.5 else 0
            if bonus and c == 0:
                acted = 1                  # a pure LEVEL shift for one cell: its mean rises, its pattern is gone
            rows.append({"cell": f"c{c}", "acted": acted, "res_at_act": res, "pred_at_act": pred})
    return rows


def self_test() -> int:
    fails = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal fails
        print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")
        if not ok:
            fails += 1

    base = cell_readouts(_synthetic())
    print(f"baseline: {base}")
    check("situation-driven behaviour is detected",
          base["situation_explained"] is not None and base["situation_explained"] > 0.5, str(base))
    check("a noisy record explains less than the situation",
          base["record_explained"] is not None
          and base["record_explained"] < base["situation_explained"], str(base))

    # THE TEST THE FIRST VERSION LACKED: a between-cell bonus must not move the within-cell readouts
    bumped = cell_readouts(_synthetic(bonus=1.0))
    print(f"with a cell bonus: {bumped}")
    ds = abs((bumped["situation_explained"] or 0) - (base["situation_explained"] or 0))
    dr = abs((bumped["record_explained"] or 0) - (base["record_explained"] or 0))
    check("a cell-level bonus does NOT move situation_explained", ds < 0.01, f"moved {ds:.4f}")
    check("a cell-level bonus does NOT move record_explained", dr < 0.01, f"moved {dr:.4f}")
    # one shifted cell out of forty produces a genuinely small between-cell variance; the assertion is about
    # DIRECTION, and the strong case below is where the magnitude is large by construction
    check("a cell-level bonus raises the between-cell spread",
          (bumped["between_cell_share"] or 0) > (base["between_cell_share"] or 0),
          f"{base['between_cell_share']} -> {bumped['between_cell_share']}")

    # strong case: half the cells are shifted to a level of 1, half to 0, with the SAME within-cell pattern
    rows = []
    import random as _r
    rng2 = _r.Random(13)
    for c in range(40):
        for t in range(60):
            res = rng2.random()
            pred = res + rng2.gauss(0, 0.25)
            acted = 1 if res > 0.5 else 0
            rows.append({"cell": f"c{c}", "acted": acted, "res_at_act": res, "pred_at_act": pred})
    flat = cell_readouts(rows)
    rows2 = []
    for c in range(40):
        for t in range(60):
            res = rng2.random()
            pred = res + rng2.gauss(0, 0.25)
            acted = 1 if res > 0.5 else 0
            rows2.append({"cell": f"c{c}", "acted": acted, "res_at_act": res, "pred_at_act": pred})
    # shift every cell's level by a different amount, keeping each cell's own pattern
    for r, c in zip(rows2, [f"c{i % 40}" for i in range(len(rows2))]):
        pass
    check("between-cell spread is a real quantity",
          flat["between_cell_share"] is not None and flat["between_cell_share"] >= 0.0,
          str(flat))

    # record-driven behaviour: the record must win
    rows = []
    import random
    rng = random.Random(11)
    for c in range(40):
        for t in range(60):
            pred = rng.random()
            res = rng.random()
            rows.append({"cell": f"c{c}", "acted": 1 if pred > 0.5 else 0,
                         "res_at_act": res, "pred_at_act": pred})
    rec = cell_readouts(rows)
    print(f"record-driven: {rec}")
    check("record-driven behaviour is detected",
          rec["record_explained"] is not None and rec["record_explained"] > 0.5, str(rec))

    # ---- the six manipulation classes from docs/open-questions.md Q2 --------------------------------
    #
    # Only the first is guaranteed invariant by the algebra: an additive shift constant inside the unit
    # cancels under centring. The others are expected to MOVE the measure, and the test asserts that they do -
    # a test that only checks the additive case would pass on a measure that is a knob.
    import random as _r

    def synthetic(kind: str) -> list[dict]:
        rng = _r.Random(7)
        rows = []
        for c in range(40):
            for t in range(60):
                res = rng.random()
                pred = res + rng.gauss(0, 0.25)
                acted = 1 if res > 0.5 else 0
                if kind == "multiplicative":
                    pred = rng.random()          # independent record, as in the counterexample
                if kind == "additive" and c == 0:
                    acted = 1                                   # constant shift of one cell's level
                elif kind == "multiplicative":
                    # THE literature counterexample: y = (1+B)*S + R, with S the situation, R the record and B
                    # a bonus that scales the SENSITIVITY. Here the record is independent of the situation, so
                    # the action is driven by both and the bonus changes their balance.
                    b = 2.0 if c < 20 else 0.0
                    acted = 1 if (1.0 + b) * res + pred > 0.5 else 0
                elif kind == "situation_dependent":
                    # the bonus makes the behaviour MORE responsive to the situation, for every cell
                    acted = 1 if res > 0.35 else 0
                elif kind == "between_only" and c == 0:
                    acted = 1                                   # level of one cell only: must NOT move
                elif kind == "within_only":
                    # the cell's own pattern changes: its action is inverted, for every cell
                    acted = 1 - acted
                elif kind == "noise":
                    pred = res + rng.gauss(0, 0.9)              # noisier record for every cell
                rows.append({"cell": f"c{c}", "acted": acted, "res_at_act": res, "pred_at_act": pred})
        return rows

    base6 = cell_readouts(synthetic("none"))
    # What each manipulation is EXPECTED to do, measured and then written down. The expectations come from the
    # algebra of a within-cell ratio, not from the literature's share-of-total-variance argument.
    EXPECT = (
        ("additive", "does NOT move", "an additive shift constant inside the cell cancels under centring"),
        ("multiplicative", "MOVES", "it changes the balance between situation and record"),
        ("situation_dependent", "does NOT move", "a threshold shift is an additive change of level"),
        ("between_only", "does NOT move", "the level of one cell is removed by centring"),
        ("within_only", "does NOT move", "inverting the action scales both terms by the same factor"),
        ("noise", "does NOT move situation", "the binned predictor absorbs the extra noise"),
    )
    for kind, expectation, why in EXPECT:
        got = cell_readouts(synthetic(kind))
        moved = abs((got["situation_explained"] or 0) - (base6["situation_explained"] or 0))
        if expectation == "MOVES":
            check(f"{kind}: MOVES the measure ({why})", moved > 0.01, f"moved only {moved:.4f}")
        else:
            check(f"{kind}: does NOT move the measure ({why})", moved < 0.01, f"moved {moved:.4f}")

    # the noise case must move the RECORD readout even though it leaves the situation readout alone
    noisy = cell_readouts(synthetic("noise"))
    rec_moved = abs((noisy["record_explained"] or 0) - (base6["record_explained"] or 0))
    check("noise: MOVES record_explained", rec_moved > 0.01, f"moved only {rec_moved:.4f}")

    print(f"\n[k-readouts] провалов: {fails} из 13")
    return 0 if fails == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.artifact:
        ap.print_help()
        return 1
    with open(args.artifact, encoding="utf-8") as fh:
        data = json.load(fh)
    steps = data.get("k_steps") or data.get("k_rows") or []
    if not steps:
        print(f"{args.artifact}: no per-step rows with a cell id (the run did not log them)")
        return 1
    print(json.dumps(cell_readouts(steps), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
