"""Analyse E20: does moving cost survival?

Reads morphogenesis/experiments/E20/*.json and reports, per arm, the fraction alive at the end, the median
moves, and the median total energy. The refusal rule from the pre-registration is applied FIRST.
"""
from __future__ import annotations
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E20 = os.path.join(ROOT, "morphogenesis", "experiments", "E20")
ARMS = ("still", "moves_cheap", "moves_base", "moves_dear")


def read(arm: str) -> dict:
    alive, moves, energy = [], [], []
    for p in sorted(glob.glob(os.path.join(E20, f"e20_{arm}_s*.json"))):
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        s = d.get("summary") or {}
        alive.append(int((s.get("final") or {}).get("alive_cells", 0)))
        moves.append(int(s.get("plastic_moves", 0)))
        fin = s.get("final") or {}
        energy.append(float(fin.get("energy_total", s.get("energy_total", 0.0)) or 0.0))
    n = len(alive)
    return {
        "n": n,
        "alive_frac": (sum(1 for a in alive if a > 0) / n) if n else None,
        "alive_median": statistics.median(alive) if alive else None,
        "moves_median": statistics.median(moves) if moves else None,
        "energy_median": statistics.median(energy) if energy else None,
        "alive_values": alive,
    }


def main() -> int:
    st = {arm: read(arm) for arm in ARMS}
    print(f"{'arm':14s} {'runs':>5s} {'alive>0':>8s} {'median alive':>13s} {'median moves':>13s} "
          f"{'median energy':>14s}")
    for arm in ARMS:
        s = st[arm]
        print(f"{arm:14s} {s['n']:5d} {str(s['alive_frac']):>8s} {str(s['alive_median']):>13s} "
              f"{str(s['moves_median']):>13s} {str(round(s['energy_median'], 1) if s['energy_median'] is not None else None):>14s}")

    print()
    invalid = []
    for arm in ARMS:
        s = st[arm]
        if s["n"] < 15:
            invalid.append(f"{arm}: only {s['n']} runs (need 15)")
        if arm != "still" and s["moves_median"] is not None and s["moves_median"] < 100:
            invalid.append(f"{arm}: median moves {s['moves_median']} < 100, not a behaviour")
    if st["moves_cheap"]["moves_median"] is not None and \
            st["moves_cheap"]["moves_median"] == st["moves_dear"]["moves_median"]:
        invalid.append("moves_cheap and moves_dear made the same number of moves: the price did not reach "
                       "the dynamics")
    if st["moves_cheap"]["energy_median"] is not None and \
            st["moves_cheap"]["energy_median"] == st["moves_dear"]["energy_median"]:
        invalid.append("moves_cheap and moves_dear have the same total energy: the price reached nothing")
    if all(st[a]["alive_frac"] == 0 for a in ARMS if st[a]["n"]):
        invalid.append("every arm died: the world does not support life")

    if invalid:
        print("INVALID SERIES - no verdict:")
        for m in invalid:
            print(f"  - {m}")
        return 1

    print("manipulation check: passed")
    print()
    cheap = st["moves_cheap"]["alive_frac"]
    base = st["moves_base"]["alive_frac"]
    diff = cheap - base
    print(f"alive fraction: moves_cheap {cheap:.2f}, moves_base {base:.2f}, difference {diff:+.2f}")
    print()
    if diff >= 0.15:
        print("VERDICT: the PRICE of moving is what hurts. Paying for a move reduces survival by at least 0.15.")
    elif diff >= 0.10:
        print("VERDICT: the price hurts, but by less than 0.15 - direction holds, size smaller.")
    elif diff > -0.10:
        print("VERDICT: NOT DISTINGUISHABLE at 20 seeds between paying and not paying for a move.")
    else:
        print("VERDICT: paying for a move HELPS. The prediction is refuted in the opposite direction.")

    # the monotone check the pre-registration asked for
    print()
    order = sorted([a for a in ARMS if st[a]["moves_median"] is not None],
                   key=lambda a: st[a]["moves_median"])
    fracs = [st[a]["alive_frac"] for a in order]
    mono = all(fracs[i] >= fracs[i + 1] for i in range(len(fracs) - 1))
    print(f"arms ordered by moves: {order}")
    print(f"alive fractions in that order: {fracs}")
    print(f"monotone falling with moves: {'yes' if mono else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
