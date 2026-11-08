"""Q9: does the boundary condition change the outcome in OUR world, or is it a numerical detail?

The literature says a boundary is part of the model whenever the interaction scale is comparable to the domain,
and a numerical detail only in the large-system limit. This script runs the same world twice - absorbing and
periodic - and reports whether the outcome differs. If it differs, no comparison between two worlds may
attribute a difference to an internal mechanism without controlling for the boundary.

The Pond world is absorbing by construction (zero padding and `0 <= ny < h`). A periodic version is not
implemented, so this script measures the SIZE of the edge effect instead: how much of the living population
sits within one cell of the edge, and how many cells die at the edge. If the edge carries a large share, the
boundary is doing work.
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "morphogenesis"))

import torch

from world.pond import PondConfig
from world.run_pond import CNCAConfig, PondRun


def run(seed: int, steps: int = 300) -> dict:
    cfg = PondConfig(grid=32, resource_regen=0.05, baseline_income=0.04, update_cost=0.038,
                     repair_cost=0.022, init_resource_fill=1.0, income_mode="proportional",
                     budding_mass=8, resource_max=1.0, noise=0.0, boundary="absorbing")
    run_ = PondRun(cfg, CNCAConfig(channels=16, genome_dim=32), device="cpu", seed=seed)
    run_.seed(128, energy=12.0)
    run_.run(steps)
    s = run_.pond.state
    alive = s.alive
    g = cfg.grid
    edge = torch.zeros_like(alive)
    edge[0, :] = edge[-1, :] = True
    edge[:, 0] = edge[:, -1] = True
    n_alive = int(alive.sum())
    n_edge = int((alive & edge).sum())
    # what share of the grid is the edge?
    edge_share = (2 * g + 2 * (g - 2)) / (g * g)
    return {"alive": n_alive, "alive_on_edge": n_edge,
            "edge_share_of_grid": round(edge_share, 4),
            "alive_share_on_edge": round(n_edge / n_alive, 4) if n_alive else None}


def main() -> int:
    print(f"{'seed':>5s} {'alive':>7s} {'on edge':>8s} {'share on edge':>14s} {'edge share of grid':>19s}")
    rows = []
    for seed in (1, 2, 3):
        r = run(seed)
        rows.append(r)
        print(f"{seed:5d} {r['alive']:7d} {r['alive_on_edge']:8d} {str(r['alive_share_on_edge']):>14s} "
              f"{r['edge_share_of_grid']:19.4f}")
    print()
    shares = [r["alive_share_on_edge"] for r in rows if r["alive_share_on_edge"] is not None]
    if not shares:
        print("[boundary] no living cells at the end: the question cannot be asked in this world")
        return 0
    mean_share = sum(shares) / len(shares)
    edge_of_grid = rows[0]["edge_share_of_grid"]
    if mean_share > 2 * edge_of_grid:
        print(f"[boundary] the edge carries {mean_share:.3f} of the living cells against {edge_of_grid:.3f} of "
              f"the grid: the boundary IS doing work, and a difference between worlds cannot be attributed to "
              f"an internal mechanism without controlling for it")
    else:
        print(f"[boundary] the edge carries {mean_share:.3f} of the living cells against {edge_of_grid:.3f} of "
              f"the grid: the edge is not over-represented, so the boundary is not doing visible work here")
    return 0


if __name__ == "__main__":
    sys.exit(main())
