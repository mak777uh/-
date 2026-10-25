#!/usr/bin/env python
"""kill_keep_probe.py — достаточность условия C: kill-and-keep против kill-and-clean.

Зачем: §10ab.1 показал, что память среды переживает поколение (необходимое условие C).
Полная минимальная демонстрация C — «убить и сохранить среду» (LIT-002): выигрывает ли
СЛЕДУЮЩАЯ когорта от того, что предыдущая оставила после себя.

Схема (одинаковая для обоих плеч):
  1) фаза 1: растить колонию из 4 клеток `--phase1` шагов (она строит нишу);
  2) убийство: все клетки гасятся, поле ресурса сохраняется;
  3) пересев: в самой далёкой от прежней колонии точке ставится пропагул `--cells` клеток;
  4) фаза 2: `--phase2` шагов бюджета и правила.
Плечо `clean` перед пересевом очищает поле: `resource = resource_max` во всех клетках.

Печатает JSON: pop_time/alive фазы 2, средний ресурс при пересеве, поколение.

Запуск (из корня):

    python scripts/kill_keep_probe.py --arm keep --seed 1 --out /tmp/keep1.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import torch

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MORPH = os.path.join(_REPO, "morphogenesis")
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.pond import PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


def make_cfg(args) -> PondConfig:
    """Конфигурация §10ab.1 + строительство ниши (иначе наследия не будет).

    `--income` управляет точкой безубыточности `own* = spent/(4·b)`: по умолчанию 0.2
    (`own*` = 0.05), для v3 нужно 0.06 (`own*` = 0.167), чтобы наследие 0.15–0.42
    пересекало порог (§10ah.2, AGENTS §3c).
    """
    return PondConfig(
        grid=32, income_mode="proportional", init_resource_fill=0.9,
        baseline_income=float(getattr(args, "income", 0.2)), update_cost=0.02, repair_cost=0.02,
        budding_mass=24, budding_cost=0.2, resource_layout="uniform",
        spore_bias="score", w_rich=0.1, freq_dep=1.0, type_mode="mixfixed",
        type_level="colony", type_start="a", invest_rate=0.02, invest_mode="fixed",
    )


def farthest_free(alive: torch.Tensor) -> tuple[int, int]:
    """Свободная клетка, максимально далёкая от живых (4-расстояние, волной)."""
    n = int(alive.shape[0])
    free = ~alive
    if not bool(alive.any()):
        ys, xs = free.nonzero(as_tuple=True)
        return int(ys[0]), int(xs[0])
    dist = torch.zeros((n, n), dtype=torch.int64)
    reached = alive.clone()
    frontier = alive.clone()
    d = 0
    while bool(frontier.any()) and d < 2 * n:
        d += 1
        grow = torch.zeros_like(frontier)
        grow[1:, :] |= frontier[:-1, :]
        grow[:-1, :] |= frontier[1:, :]
        grow[:, 1:] |= frontier[:, :-1]
        grow[:, :-1] |= frontier[:, 1:]
        frontier = grow & ~reached & free
        dist[frontier] = d
        reached |= frontier
    far = free & (dist == dist[free].max())
    ys, xs = far.nonzero(as_tuple=True)
    return int(ys[0]), int(xs[0])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=["keep", "clean"], required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--phase1", type=int, default=200)
    ap.add_argument("--phase2", type=int, default=100)
    ap.add_argument("--cells", type=int, default=5)
    ap.add_argument("--income", type=float, default=0.2,
                    help="baseline_income: точка безубыточности own* = spent/(4*b)")
    ap.add_argument("--propagule-energy", type=float, default=8.0,
                    help="стартовый заряд пересеянных клеток (v2 = 1.0: автономия ~25 шагов)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--checkpoint", default="checkpoints/world_base_rule.pt")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    cfg = make_cfg(args)
    run = PondRun(world_cfg=cfg, seed=args.seed, device=args.device,
                  rule_checkpoint=args.checkpoint)
    run.seed(cells=4, energy=8.0)
    run.run(args.phase1, log_every=args.phase1)
    pond = run.pond
    alive_phase1 = int(pond.state.alive.sum())
    resource_after_phase1 = float(pond.state.resource.mean())

    # убийство: гасим все клетки, поле ресурса не трогаем
    pond.state.alive = torch.zeros_like(pond.state.alive)
    pond.state.energy = torch.zeros_like(pond.state.energy)
    if args.arm == "clean":
        pond.state.resource = torch.full_like(pond.state.resource, cfg.resource_max)

    resource_at_reseed = float(pond.state.resource.mean())

    # пересев пропагула в самой далёкой от прежней колонии точке
    y, x = farthest_free(pond.state.alive)
    spot = torch.zeros_like(pond.state.alive)
    placed = 0
    for dy in range(0, 8):
        for dx in range(0, 8):
            if placed >= args.cells:
                break
            ny, nx = (y + dy) % 32, (x + dx) % 32
            if not bool(pond.state.alive[ny, nx]):
                spot[ny, nx] = True
                placed += 1
        if placed >= args.cells:
            break
    pond.state.alive |= spot
    pond.state.energy = torch.where(spot, torch.full_like(pond.state.energy,
                                                          float(args.propagule_energy)),
                                    pond.state.energy)
    pond.state.age = torch.where(spot, torch.zeros_like(pond.state.age), pond.state.age)
    pond.state.damage = torch.where(spot, torch.zeros_like(pond.state.damage),
                                    pond.state.damage)
    if pond.state.cell_type is not None:
        pond.state.cell_type[spot] = 1
    run._apply_alive(pond.state.alive)
    alive_after_reseed = int(pond.state.alive.sum())

    pop_before = int(getattr(run, "pop_time", 0))
    run.run(args.phase2, log_every=args.phase2)
    pop_phase2 = int(getattr(run, "pop_time", 0)) - pop_before
    phase2_log = run.log[-args.phase2:] if len(run.log) >= args.phase2 else run.log
    alive_final = int(pond.state.alive.sum())
    max_alive = max((row.get("alive_cells", 0) for row in phase2_log), default=alive_final)
    divisions = len(getattr(pond, "division_parent_ages", []))
    gen = None
    if divisions >= 20:
        import statistics
        gen = round(float(statistics.median(pond.division_parent_ages)), 1)

    payload = {
        "arm": args.arm,
        "seed": args.seed,
        "phase1_steps": args.phase1,
        "phase2_steps": args.phase2,
        "cells": args.cells,
        "propagule_energy": args.propagule_energy,
        "alive_phase1": alive_phase1,
        "resource_mean_after_phase1": round(resource_after_phase1, 4),
        "resource_mean_at_reseed": round(resource_at_reseed, 4),
        "alive_after_reseed": alive_after_reseed,
        "pop_time_phase2": pop_phase2,
        "alive_final": alive_final,
        "max_alive_phase2": max_alive,
        "generation_length": gen,
        "generation_divisions": divisions,
        "sensitivity_note": (f"фаза 2 = {args.phase2}, energy = {args.propagule_energy}, "
                             f"автономия ≈ {round(args.propagule_energy / 0.04)} шагов"),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
