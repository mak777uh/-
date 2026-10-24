"""Мягкий (дифференцируемый) суррогат пруда для A-gate.

Зачем: у hard-пруда нет градиента (рождения/смерти — пороги), поэтому правило
нельзя обучать на цель пруда (`pop_time`). Здесь те же уравнения бюджета и то же
обученное правило, но решения мягкие (sigmoid с температурой T), и `pop_time`
дифференцируем по параметрам правила.

Гейт A: при T → 0 мягкая модель обязана воспроизводить hard в пределах порога
(4.7%) по `pop_time` и числу живых на тех же сидах. Проверяем на окне ДО первого
почкования (у hard первое деление ~125–206 шагов), потому что мягкое почкование
в этой версии не реализовано — это ограничение фиксируется.

Запуск:
    python world/soft_pond.py --steps 100 --temps 1.0 0.5 0.1 0.01 --seeds 1 2 3
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.cnca import CNCA, CNCAConfig  # noqa: E402
from world.pond import Pond, PondConfig  # noqa: E402


def soft_rollout(rule: CNCA, cfg: PondConfig, steps: int, temp: float, seed: int,
                 device: torch.device) -> dict:
    """Мягкий прогон: доход/энергия/смерть — sigmoid, ресурс и правило — как в hard."""
    n = cfg.grid
    gen = torch.Generator(device=device).manual_seed(seed)
    state = torch.full((1, 16, n, n), -0.5, device=device)
    mid = n // 2
    state[0, 0, mid - 1:mid + 1, mid - 1:mid + 1] = 0.5
    genome = torch.zeros((1, cfg.genome_dim, n, n), device=device)

    rows = torch.arange(n, device=device, dtype=torch.float32)
    position = 1.0 - rows / max(n - 1, 1)
    ceiling = cfg.resource_max * (0.2 + 0.8 * position)[:, None].expand(n, n)
    inflow = cfg.resource_regen * (0.1 + 0.9 * position)[:, None].expand(n, n)
    resource = cfg.resource_max * cfg.init_resource_fill * (0.2 + 0.8 * position)[:, None].expand(n, n)
    energy = torch.zeros((n, n), device=device)
    alive = torch.zeros((n, n), device=device)
    alive[mid - 1:mid + 1, mid - 1:mid + 1] = 1.0
    energy[mid - 1:mid + 1, mid - 1:mid + 1] = 8.0

    pop_time = 0.0
    for _ in range(steps):
        state = rule(state, genome)
        gate = torch.sigmoid(state[0, 0] / temp)
        alive = torch.clamp(gate, 0.0, 1.0)
        resource = torch.minimum(resource + inflow, ceiling)
        income = torch.minimum(resource, cfg.baseline_income * resource * 4.0) * alive
        resource = resource - income
        energy = energy + income - (cfg.update_cost + cfg.repair_cost) * alive
        survival = torch.sigmoid(energy / max(temp, 1e-4))
        energy = energy * survival
        # мягкое «живое» без отдельной вспышки: клетка с нулевой энергией гаснет
        alive_eff = alive * survival
        state[0, 0] = torch.logit(alive_eff.clamp(1e-4, 1 - 1e-4))
        pop_time = pop_time + alive_eff.sum()
    return {"pop_time": float(pop_time), "alive_final": float(alive_eff.sum())}


def hard_rollout(cfg: PondConfig, steps: int, seed: int, device: torch.device,
                 checkpoint: str) -> dict:
    """Окно hard-прогона без почкования: считаем только рост (рождения отключены массой)."""
    cfg2 = PondConfig(**{**cfg.__dict__, "budding_mass": 10**9})
    pond = Pond(cfg2, device=device, seed=seed)
    from world.run_pond import PondRun
    run = PondRun(world_cfg=cfg2, seed=seed, device=str(device), rule_checkpoint=checkpoint)
    run.seed(cells=4, energy=8.0)
    run.run(steps, log_every=steps)
    return {"pop_time": float(run.pop_time), "alive_final": float(run.pond.state.alive.sum())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--temps", type=float, nargs="+", default=[1.0, 0.5, 0.1, 0.01])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--checkpoint", default="checkpoints/world_base_rule.pt")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    cfg = PondConfig(grid=args.grid, resource_layout="gradient", income_mode="proportional",
                     init_resource_fill=0.9, baseline_income=0.2, update_cost=0.02,
                     repair_cost=0.02, budding_mass=24, budding_cost=0.2)
    rule_cfg = CNCAConfig(channels=16, genome_dim=32)
    payload = torch.load(args.checkpoint, map_location=device, weights_only=False)
    rule = CNCA(rule_cfg).to(device)
    rule.load_state_dict(payload.get("model_state_dict", payload))
    rule.eval()

    rows = []
    for seed in args.seeds:
        hard = hard_rollout(cfg, args.steps, seed, device, args.checkpoint)
        for temp in args.temps:
            with torch.no_grad():
                soft = soft_rollout(rule, cfg, args.steps, temp, seed, device)
            rows.append({"seed": seed, "temp": temp, "hard": hard, "soft": soft,
                         "pop_ratio": soft["pop_time"] / max(hard["pop_time"], 1e-9),
                         "alive_ratio": soft["alive_final"] / max(hard["alive_final"], 1e-9)})
    out = {"steps": args.steps, "rows": rows}
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    if args.out:
        json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
