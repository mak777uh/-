"""Analyse E19: does turning the record on kill the body?

Reads morphogenesis/experiments/E19/*.json and reports, per arm, the fraction of runs alive at the end, the
median alive count, and the manipulation check the pre-registration requires.

The refusal rule from the pre-registration is applied FIRST: a series that fails it gets no verdict.
"""
from __future__ import annotations
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E19 = os.path.join(ROOT, "morphogenesis", "experiments", "E19")
ARMS = ("no_record", "record_random", "record_pred")


def load(arm: str) -> dict[int, dict]:
    out = {}
    for p in sorted(glob.glob(os.path.join(E19, f"e19_{arm}_s*.json"))):
        seed = int(os.path.basename(p).rsplit("_s", 1)[1].split(".")[0])
        with open(p, encoding="utf-8") as fh:
            out[seed] = json.load(fh)
    return out


def read(arm: str) -> dict:
    runs = load(arm)
    alive, moves, pop_time = [], [], []
    for seed, d in runs.items():
        s = d.get("summary") or {}
        alive.append(int((s.get("final") or {}).get("alive_cells", 0)))
        moves.append(int(s.get("plastic_moves", 0)))
        pop_time.append(int(s.get("pop_time", 0) or 0))
    n = len(alive)
    return {
        "n": n,
        "alive": alive,
        "moves": moves,
        "pop_time": pop_time,
        "alive_frac": (sum(1 for a in alive if a > 0) / n) if n else None,
        "alive_median": statistics.median(alive) if alive else None,
        "moves_median": statistics.median(moves) if moves else None,
    }


def main() -> int:
    stats = {arm: read(arm) for arm in ARMS}
    print(f"{'arm':16s} {'runs':>5s} {'alive>0':>9s} {'median alive':>13s} {'median moves':>13s}")
    for arm in ARMS:
        s = stats[arm]
        print(f"{arm:16s} {s['n']:5d} {str(s['alive_frac']):>9s} {str(s['alive_median']):>13s} "
              f"{str(s['moves_median']):>13s}")

    print()
    # ---- the refusal rule, applied before any verdict -------------------------------------------
    invalid = []
    for arm in ARMS:
        s = stats[arm]
        if s["n"] < 15:
            invalid.append(f"{arm}: only {s['n']} runs (need 15)")
        if arm != "no_record" and s["moves_median"] == 0:
            invalid.append(f"{arm}: no moves, but this arm should act")
    acting = [arm for arm in ARMS if arm != "no_record"]
    if all(stats[a]["moves_median"] is not None for a in acting):
        if stats["record_random"]["moves_median"] == stats["record_pred"]["moves_median"]:
            invalid.append("record_random and record_pred made the same number of moves: the gate did not reach "
                           "the dynamics")
    if all(stats[a]["alive_frac"] == 0 for a in ARMS if stats[a]["n"]):
        invalid.append("every arm died: the world does not support life and the question cannot be asked")

    if invalid:
        print("INVALID SERIES - no verdict:")
        for m in invalid:
            print(f"  - {m}")
        return 1

    print("manipulation check: passed (the acting arms differ)")
    print()
    # ---- the verdict ----------------------------------------------------------------------------
    pred = stats["record_pred"]["alive_frac"]
    rand = stats["record_random"]["alive_frac"]
    diff = rand - pred
    print(f"alive fraction: record_random {rand:.2f}, record_pred {pred:.2f}, difference {diff:+.2f}")
    print()
    if diff >= 0.15:
        print("VERDICT: the record HURTS. Using the prediction reduces survival by at least 0.15, as predicted.")
    elif diff >= 0.10:
        print("VERDICT: the record hurts, but by less than the predicted 0.15 - the direction holds, the size "
              "is smaller.")
    elif diff > -0.10:
        print("VERDICT: NOT DISTINGUISHABLE at 20 seeds. The difference is below what this number of seeds can "
              "see; it is not evidence of no effect.")
    else:
        print("VERDICT: the record HELPS. The prediction is refuted in the opposite direction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
