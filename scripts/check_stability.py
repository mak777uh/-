"""Gate: the integrator must be stable for the parameters the run actually uses.

Why. Q5 in docs/open-questions.md: the explicit scheme with the 5-point Laplacian requires D*dt/h^2 <= 1/4 for
EVERY diffusion coefficient. `Dw = 0.32` at `dt = 1` gives an amplification of 1 - 8*D*dt = -1.56, so the
optional third field ran an unstable diffusion at its default. Lowering `Dw` fixed that run but changed the
model: if `Dw` is a physical coefficient, the right fix is to lower `dt` and keep `Dw`.

This gate does not decide which is right. It refuses a run whose parameters violate the condition, and it
prints the two ways out, so the choice is made explicitly rather than by a default.

Usage:
  python scripts/check_stability.py --Du 0.16 --Dv 0.08 --Dw 0.24 --dt 1.0 --dx 1.0
  python scripts/check_stability.py                      # the current defaults
"""
from __future__ import annotations
import argparse
import sys


def amplification(D: float, dt: float, dx: float) -> float:
    """The high-frequency (checkerboard) multiplier of the explicit 2D 5-point scheme."""
    return 1.0 - 8.0 * D * dt / (dx * dx)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--Du", type=float, default=0.16)
    ap.add_argument("--Dv", type=float, default=0.08)
    ap.add_argument("--Dw", type=float, default=0.24)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--dx", type=float, default=1.0)
    args = ap.parse_args(argv)

    bad = []
    print(f"{'coefficient':12s} {'D':>6s} {'dt':>5s} {'dx':>5s} {'D*dt/dx^2':>10s} {'amplification':>14s}  verdict")
    for name, D in (("Du", args.Du), ("Dv", args.Dv), ("Dw", args.Dw)):
        r = D * args.dt / (args.dx ** 2)
        amp = amplification(D, args.dt, args.dx)
        ok = abs(amp) <= 1.0
        print(f"{name:12s} {D:6.3f} {args.dt:5.2f} {args.dx:5.2f} {r:10.4f} {amp:14.3f}  "
              f"{'stable' if ok else 'UNSTABLE'}")
        if not ok:
            bad.append((name, D, r))

    if bad:
        print()
        for name, D, r in bad:
            print(f"  {name} = {D} violates D*dt/dx^2 <= 0.25 (it is {r:.3f}). Two ways out:")
            print(f"    (a) keep the coefficient and lower dt to <= {0.25 * args.dx ** 2 / D:.4f}"
                  f" - the model is unchanged, the run costs more steps;")
            print(f"    (b) lower {name} to <= {0.25 * args.dx ** 2 / args.dt:.4f}"
                  f" - the run is cheap, but the MODEL changed and the artifact must say so.")
        print("\n[stability] ПРОВАЛ: параметры нарушают условие устойчивости явной схемы")
        return 1

    print("\n[stability] ok: все коэффициенты устойчивы при этих dt и dx")
    return 0


if __name__ == "__main__":
    sys.exit(main())
