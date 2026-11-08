"""The three readouts the reading implies, replacing the favourable share as the primary metric.

Why these three. The favourable share compares a cell with OTHER cells: it ranks. A ranking is blind to
order, because an ordered and a disordered system can have the same rank distribution. The reading's
argument (P80, P128, P255) is that what matters is the RELATION between a cell's behaviour and the
situation it is in, measured inside the cell:

  situation_explained : the fraction of the variance of "did the cell act" explained by the resource it
                        stood in at that moment. High = the behaviour follows the situation.
  record_explained    : the fraction explained by the cell's own record (pred) at that moment.
                        High = the behaviour follows the memory.
  energy_per_behaviour: energy spent per action. The reading calls the difference friction (P267).

The two explained fractions are computed by comparing the within-bin variance of the action rate under
each explanatory variable with the total variance - a simple eta-squared, no model fitting, no
assumption about the form of the relation.

Usage:
  python scripts/k_readouts.py <artifact.json>          # report for one artifact
  python scripts/k_readouts.py --self-test              # check the arithmetic on synthetic data
"""
from __future__ import annotations
import argparse
import json
import math
import sys


def eta_squared(x: list[float], y: list[float], bins: int = 10) -> float | None:
    """Fraction of the variance of y explained by binning on x (eta-squared).

    No functional form is assumed: the bins are quantiles of x, and the statistic is
    (total variance - within-bin variance) / total variance. Returns None when y has no variance.
    """
    n = len(x)
    if n < bins * 2:
        return None
    pairs = sorted(zip(x, y), key=lambda p: p[0])
    mean_y = sum(y) / n
    total = sum((v - mean_y) ** 2 for v in y)
    if total <= 0.0:
        return None
    within = 0.0
    for b in range(bins):
        lo = b * n // bins
        hi = (b + 1) * n // bins
        chunk = pairs[lo:hi]
        if not chunk:
            continue
        m = sum(p[1] for p in chunk) / len(chunk)
        within += sum((p[1] - m) ** 2 for p in chunk)
    return max(0.0, (total - within) / total)


def readouts(rows: list[dict]) -> dict:
    """rows: each has acted (0/1), res_at_act, pred_at_act, energy_spent."""
    acted = [float(r["acted"]) for r in rows]
    res = [float(r["res_at_act"]) for r in rows]
    pred = [float(r["pred_at_act"]) for r in rows]
    sit = eta_squared(res, acted)
    rec = eta_squared(pred, acted)
    n_act = sum(1 for a in acted if a > 0.5)
    spent = sum(float(r.get("energy_spent", 0.0)) for r in rows)
    return {
        "n": len(rows),
        "n_acted": n_act,
        "action_rate": round(n_act / len(rows), 4) if rows else None,
        "situation_explained": None if sit is None else round(sit, 4),
        "record_explained": None if rec is None else round(rec, 4),
        "energy_per_behaviour": round(spent / n_act, 6) if n_act else None,
    }


def self_test() -> int:
    """The arithmetic must recover a known answer before it is trusted on real data."""
    fails = 0

    # 1) behaviour determined entirely by the situation -> situation_explained ~ 1, record ~ 0
    rows = []
    for i in range(400):
        res = i / 400.0
        rows.append({"acted": 1 if res > 0.5 else 0, "res_at_act": res,
                     "pred_at_act": (i * 37 % 400) / 400.0, "energy_spent": 0.1})
    r = readouts(rows)
    ok = r["situation_explained"] > 0.9 and r["record_explained"] < 0.1
    print(f"{'OK  ' if ok else 'FAIL'} situation-driven: {r}")
    fails += 0 if ok else 1

    # 2) behaviour determined entirely by the record -> the reverse
    rows = []
    for i in range(400):
        pred = i / 400.0
        rows.append({"acted": 1 if pred > 0.5 else 0, "res_at_act": (i * 37 % 400) / 400.0,
                     "pred_at_act": pred, "energy_spent": 0.1})
    r = readouts(rows)
    ok = r["record_explained"] > 0.9 and r["situation_explained"] < 0.1
    print(f"{'OK  ' if ok else 'FAIL'} record-driven: {r}")
    fails += 0 if ok else 1

    # 3) energy per behaviour
    rows = [{"acted": 1, "res_at_act": 0.5, "pred_at_act": 0.5, "energy_spent": 0.2} for _ in range(10)]
    rows += [{"acted": 0, "res_at_act": 0.5, "pred_at_act": 0.5, "energy_spent": 0.2} for _ in range(10)]
    r = readouts(rows)
    ok = abs(r["energy_per_behaviour"] - 0.4) < 1e-9
    print(f"{'OK  ' if ok else 'FAIL'} energy per behaviour: {r['energy_per_behaviour']} (want 0.4)")
    fails += 0 if ok else 1

    print(f"\n{fails} failures out of 3 checks")
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
    rows = data.get("k_rows") or []
    if not rows:
        print(f"{args.artifact}: no k_rows (the run did not log the three fields)")
        return 1
    print(json.dumps(readouts(rows), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
