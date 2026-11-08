"""Why does the body die by step 150? Find parameters under which the world supports life.

The boundary measurement found the population at zero by step 150 with income 0.04, update_cost 0.038,
repair_cost 0.022. That is not a boundary effect: it is the world not supporting life. Before any experiment
can measure behaviour, the world must keep something alive for the horizon.

This sweeps the income and the two costs together and reports the alive count at the end.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "morphogenesis"))

from world.pond import PondConfig
from world.run_pond import CNCAConfig, PondRun

STEPS = 300


def run(income: float, update: float, repair: float, seed: int = 1) -> int:
    cfg = PondConfig(grid=32, resource_regen=0.05, baseline_income=income, update_cost=update,
                     repair_cost=repair, init_resource_fill=1.0, income_mode="proportional",
                     budding_mass=8, resource_max=1.0, noise=0.0, damage_rate=0.02)
    r = PondRun(cfg, CNCAConfig(channels=16, genome_dim=32), device="cpu", seed=seed)
    r.seed(128, energy=12.0)
    r.run(STEPS)
    return int(r.pond.state.alive.sum())


print(f"steps={STEPS}, grid=32, seed=128, init energy=12")
print(f"{'income':>7s} {'update':>7s} {'repair':>7s} {'alive':>7s}")
best = []
for income in (0.04, 0.08, 0.12, 0.2):
    for update in (0.01, 0.02, 0.038):
        for repair in (0.005, 0.022):
            a = run(income, update, repair)
            print(f"{income:7.3f} {update:7.3f} {repair:7.3f} {a:7d}")
            if a > 0:
                best.append((a, income, update, repair))

print()
if best:
    best.sort(reverse=True)
    a, i, u, rp = best[0]
    print(f"best: alive={a} with income={i} update={u} repair={rp}")
else:
    print("NO combination keeps the body alive: the world as configured cannot support life")
