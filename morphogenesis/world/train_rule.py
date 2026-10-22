"""Быстрое обучение базового правила: cNCA растёт из одной клетки к маске.

Зачем: эволюции нужно правило, которое УМЕЕТ расти (иначе нет потомков и отбору
нечего выбирать — проверено дымовым прогоном 23.10). Здесь правило учится на
простой цели (квадрат) за считанные минуты: цель не важна, важна способность
к росту. Дальше геном модулирует это правило, и отбор работает поверх.

Запуск (10–20 минут на GPU):

    python world/train_rule.py --steps 1500 --size 16 --out checkpoints/world_base_rule.pt

Критерий готовности (v0.1a): за 200 шагов роллаута из одной клетки появляется
компонент ≥ 64 клеток.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import torch

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.cnca import CNCA, CNCAConfig  # noqa: E402


def target_mask(size: int, grid: int) -> torch.Tensor:
    """Целевая маска: квадрат size×size в центре."""
    mask = torch.zeros((1, 1, grid, grid))
    lo = (grid - size) // 2
    mask[0, 0, lo : lo + size, lo : lo + size] = 1.0
    return mask


def rollout(rule: CNCA, state: torch.Tensor, genome: torch.Tensor, steps: int) -> torch.Tensor:
    for _ in range(steps):
        state = rule(state, genome)
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--steps", type=int, default=1500, help="шагов обучения")
    ap.add_argument("--rollout", type=int, default=48, help="шагов CA в одном примере")
    ap.add_argument("--size", type=int, default=16, help="сторона целевого квадрата")
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default="checkpoints/world_base_rule.pt")
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    cfg = CNCAConfig(channels=16, genome_dim=32)
    rule = CNCA(cfg).to(device)
    opt = torch.optim.Adam(rule.parameters(), lr=args.lr)
    gen = torch.Generator(device=device).manual_seed(0)

    target = target_mask(args.size, args.grid).to(device)
    # канал живости цели: внутри маски живая, снаружи мёртвая
    target_alive = target.clone()

    t0 = time.perf_counter()
    for step in range(1, args.steps + 1):
        state = torch.full((args.batch, cfg.channels, args.grid, args.grid), -20.0, device=device)
        # одна живая клетка в центре
        mid = args.grid // 2
        state[:, cfg.alive_channel, mid, mid] = 10.0
        genome = torch.zeros((args.batch, cfg.genome_dim, args.grid, args.grid), device=device)

        out = rollout(rule, state, genome, args.rollout)
        alive = torch.sigmoid(out[:, cfg.alive_channel : cfg.alive_channel + 1])
        loss = torch.nn.functional.mse_loss(alive, target_alive)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % max(1, args.steps // 10) == 0:
            with torch.no_grad():
                frac = float(((alive > 0.5) & (target_alive > 0.5)).sum()) / max(
                    float(alive.numel()), 1.0
                )
            print(f"шаг {step:5d} | loss {float(loss):.4f} | совпало с целью {frac:.3f}", flush=True)

    # проверка критерия v0.1a: растёт ли из одной клетки
    with torch.no_grad():
        state = torch.full((1, cfg.channels, args.grid, args.grid), -20.0, device=device)
        state[0, cfg.alive_channel, args.grid // 2, args.grid // 2] = 10.0
        genome = torch.zeros((1, cfg.genome_dim, args.grid, args.grid), device=device)
        out = rollout(rule, state, genome, 200)
        alive = (torch.sigmoid(out[0, cfg.alive_channel]) > 0.5).sum().item()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    torch.save({"model_state_dict": rule.state_dict(), "config": cfg.__dict__}, args.out)
    summary = {
        "steps": args.steps,
        "alive_after_200": int(alive),
        "criterion_alive_ge_64": bool(alive >= 64),
        "wall_seconds": round(time.perf_counter() - t0, 1),
        "out": args.out,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
