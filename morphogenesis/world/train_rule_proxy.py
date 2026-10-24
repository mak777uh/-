"""Прокси мета-обучения: рандомизация ЦЕЛИ РОСТА (не семей сред).

Честная рамка: это не обучение на семьях сред (у pond-цикла нет градиента), а
проверка «даёт ли рандомизация задачи роста перенос на 10 сред». M учится на
случайных целях (форма/размер/позиция), S — на одной (квадрат), бюджет равный.

Запуск:
    python world/train_rule_proxy.py --target-mode random --steps 800 \
        --init checkpoints/world_base_rule.pt --out checkpoints/world_rule_meta_proxy.pt
    python world/train_rule_proxy.py --target-mode square --steps 800 \
        --init checkpoints/world_base_rule.pt --out checkpoints/world_rule_single_proxy.pt
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


def square_mask(grid: int, size: int) -> torch.Tensor:
    mask = torch.zeros((1, 1, grid, grid))
    lo = (grid - size) // 2
    mask[0, 0, lo: lo + size, lo: lo + size] = 1.0
    return mask


def random_mask(grid: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    # генератор выборки целей — CPU: torch.randint с cuda-генератором падает
    """Случайная цель: форма, размер, позиция и масштаб."""
    mask = torch.zeros((1, 1, grid, grid), device=device)
    shape = int(torch.randint(0, 5, (), generator=gen))
    w = int(torch.randint(6, 20, (), generator=gen))
    h = int(torch.randint(6, 20, (), generator=gen))
    y = int(torch.randint(0, grid - h + 1, (), generator=gen))
    x = int(torch.randint(0, grid - w + 1, (), generator=gen))
    if shape == 0:      # прямоугольник
        mask[0, 0, y:y + h, x:x + w] = 1.0
    elif shape == 1:    # крест
        cy, cx = y + h // 2, x + w // 2
        mask[0, 0, cy, x:x + w] = 1.0
        mask[0, 0, y:y + h, cx] = 1.0
    elif shape == 2:    # Г-форма
        mask[0, 0, y:y + h, x:x + max(3, w // 3)] = 1.0
        mask[0, 0, y + h - max(3, h // 3):y + h, x:x + w] = 1.0
    elif shape == 3:    # ромб
        cy, cx = y + h // 2, x + w // 2
        for dy in range(-h // 2, h // 2 + 1):
            span = max(1, w // 2 - abs(dy))
            yy = cy + dy
            if 0 <= yy < grid:
                mask[0, 0, yy, max(0, cx - span):min(grid, cx + span + 1)] = 1.0
    else:               # два квадрата
        s = max(3, min(w, h) // 2)
        mask[0, 0, y:y + s, x:x + s] = 1.0
        mask[0, 0, min(grid - s, y + h - s):min(grid, y + h), min(grid - s, x + w - s):min(grid, x + w)] = 1.0
    return mask


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--rollout", type=int, default=48)
    ap.add_argument("--size", type=int, default=16)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--target-mode", default="random", choices=["random", "square"])
    ap.add_argument("--init", default="checkpoints/world_base_rule.pt")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default="checkpoints/world_rule_proxy.pt")
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    cfg = CNCAConfig(channels=16, genome_dim=32)
    rule = CNCA(cfg).to(device)
    if args.init and os.path.isfile(args.init):
        payload = torch.load(args.init, map_location=device, weights_only=False)
        rule.load_state_dict(payload.get("model_state_dict", payload))
        print(f"[proxy] старт с {args.init}", flush=True)
    opt = torch.optim.Adam(rule.parameters(), lr=args.lr)
    gen = torch.Generator(device="cpu").manual_seed(int(args.seed))
    fixed = square_mask(args.grid, args.size)

    t0 = time.perf_counter()
    for step in range(1, args.steps + 1):
        state = torch.full((args.batch, cfg.channels, args.grid, args.grid), -0.5, device=device)
        mid = args.grid // 2
        state[:, cfg.alive_channel, mid, mid] = 0.5
        genome = torch.zeros((args.batch, cfg.genome_dim, args.grid, args.grid), device=device)
        out = state
        for _ in range(args.rollout):
            out = rule(out, genome)
        alpha = out[:, cfg.alive_channel: cfg.alive_channel + 1]
        if args.target_mode == "random":
            tgt = random_mask(args.grid, gen, device).expand(args.batch, -1, -1, -1)
        else:
            tgt = fixed.to(device).expand(args.batch, -1, -1, -1)
        loss = torch.nn.functional.mse_loss(alpha, tgt * 2.0 - 1.0)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % max(1, args.steps // 5) == 0:
            print(f"шаг {step} | loss {float(loss):.4f}", flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    torch.save({"model_state_dict": rule.state_dict(), "config": cfg.__dict__}, args.out)
    print(json.dumps({"steps": args.steps, "target_mode": args.target_mode,
                      "wall_seconds": round(time.perf_counter() - t0, 1),
                      "out": args.out}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
