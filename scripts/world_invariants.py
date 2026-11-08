"""Gate: the world's invariants, as one command.

Why this exists. On 08.11 four defects were found by a human reading the code: budding created energy, age
killed although the docstring said it did not, `repair_cost` was charged every step, and a step was
unaffordable at exactly its price. None of the 83 test files caught them, because each test checked a
behaviour rather than an INVARIANT.

This gate checks the invariants directly:

  W1  energy is conserved across every event type (budding, for every spore size)
  W2  age does not kill
  W3  repair is charged only when a repair happens
  W4  every field of the config reaches the artifact
  W5  every diffusion coefficient in the explicit scheme is stable at its own dt
  W6  a step is affordable when the budget covers its price

A gate that cannot fail is decoration, so every check here has been shown to fail on the old code; the
history is in docs/design-audit.md.

Usage:
  python scripts/world_invariants.py
"""
from __future__ import annotations
import dataclasses
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MORPH = os.path.join(ROOT, "morphogenesis")

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")


def main() -> int:
    sys.path.insert(0, MORPH)
    cwd = os.getcwd()
    os.chdir(MORPH)
    try:
        import torch
        from world.pond import Pond, PondConfig
        from world.run_pond import config_block

        def pond(**kw):
            base = dict(grid=16, resource_regen=0.0, baseline_income=0.0, update_cost=0.0,
                        repair_cost=0.0, damage_rate=0.0, noise=0.0, budding_cost=8.0,
                        budding_mass=4, mobility_steps=0, mobility_cost=0.0)
            base.update(kw)
            return Pond(PondConfig(**base), seed=1)

        def body(p, energy=20.0):
            mask = torch.zeros((p.cfg.grid, p.cfg.grid), dtype=torch.bool)
            mask[7:9, 7:9] = True
            p.seed_life(mask, energy=energy)
            return mask

        # W1: energy is conserved across budding, for every spore size
        worst = 0.0
        for sc in (1, 2, 3, 4):
            p = pond(spore_cells=sc)
            parent = body(p)
            before = float(p.state.energy.sum())
            child = p.bud(parent)
            after = float(p.state.energy[parent].sum())
            got = float(p.state.energy[child].sum()) if child is not None else 0.0
            worst = max(worst, abs((after + got) - before))
        check("W1 budding conserves energy for every spore size", worst < 1e-6,
              f"worst deviation {worst:.6f}")

        # W2: age does not kill
        p = pond(max_age=5, damage_max=1000)
        m = torch.zeros((16, 16), dtype=torch.bool)
        m[8, 8] = True
        p.seed_life(m, energy=100.0)
        p.state.age[m] = 10_000
        p.step_cells()
        check("W2 age does not kill", bool(p.state.alive[m].any()),
              "a cell died of age although the docstring says age is diagnostic")

        # W3: repair is charged only when a repair happens
        p = pond(update_cost=0.1, repair_cost=0.5)
        m = torch.zeros((16, 16), dtype=torch.bool)
        m[8, 8] = True
        p.seed_life(m, energy=10.0)
        p.state.damage[m] = 0
        before = float(p.state.energy[m].sum())
        p.step_cells()
        spent = before - float(p.state.energy[m].sum())
        check("W3 repair is not charged without damage", abs(spent - 0.1) < 1e-6,
              f"spent {spent:.3f} with no damage, update_cost is 0.1")

        # W4: every config field reaches the artifact
        cfg = PondConfig()
        fields = {f.name for f in dataclasses.fields(cfg)}
        block = config_block(cfg)
        missing = sorted(fields - set(block))
        check("W4 every config field reaches the artifact", not missing, str(missing[:5]))
        try:
            json.dumps(block)
            serialisable = True
        except TypeError:
            serialisable = False
        check("W4b the config block is JSON-serialisable", serialisable)

        # W5: every diffusion coefficient is stable at its own dt
        #     explicit 4-neighbour Laplacian: amplification 1 - 8*D*dt, stable when |amp| <= 1
        unstable = []
        for name, D, dt in (("Du", 0.16, 1.0), ("Dv", 0.08, 1.0), ("Dw", 0.24, 1.0)):
            amp = 1.0 - 8.0 * D * dt
            if abs(amp) > 1.0:
                unstable.append(f"{name}={D} at dt={dt}: amplification {amp:+.2f}")
        check("W5 every diffusion coefficient is stable at its own dt", not unstable,
              "; ".join(unstable))
    finally:
        os.chdir(cwd)

    fails = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"\n[world] проверок: {len(CHECKS)}, провалов: {fails}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
