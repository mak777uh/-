"""Случайная инициализация весов в масштабе обученной модели (базлайн v1.1).

Зачем: `untrained_current_arch` отвечает на вопрос «что даёт архитектура без
обучения», но не отделяет «масштаб весов» от «выученной структуры». Если обучить
модель и заменить её веса случайными с тем же распределением, то любое различие в
классе/способностях нельзя списать на масштаб.

Два режима:

- `shuffle` (по умолчанию) — перемешать значения внутри каждого тензора. Точно
  сохраняет распределение (включая выбросы), ломает только структуру.
- `rms` — заменить значения нормальным шумом с тем же средним и СКО на тензор.

Запуск (cwd = morphogenesis или из корня с путями):

    python make_random_init.py --source checkpoints/E02c_R-9_s2000_seed42/nca_final.pt \
        --out checkpoints/E02c_randinit_seed42/nca_final.pt --seed 7 --mode shuffle

Скрипт не обучает и не меняет исходный файл; результат — обычный чекпоинт той же
структуры, который подхватывает `e02c_census.py`.
"""
from __future__ import annotations

import argparse
import os
import sys

import torch


def randomize_state_dict(state_dict: dict, mode: str, generator: torch.Generator) -> dict:
    """Вернуть новый state_dict с разрушенной структурой весов."""
    if mode not in {"shuffle", "rms"}:
        raise SystemExit(f"режим должен быть shuffle или rms, получено {mode!r}")

    out: dict = {}
    for name, value in state_dict.items():
        if not torch.is_tensor(value):
            out[name] = value
            continue
        if not value.is_floating_point() or value.numel() < 2:
            # счётчики, маски, скаляры — оставляем как есть
            out[name] = value
            continue
        flat = value.clone().reshape(-1)
        if mode == "shuffle":
            perm = torch.randperm(flat.numel(), generator=generator, device=flat.device)
            new_flat = flat[perm]
        else:
            mean = flat.mean()
            std = flat.std(unbiased=False)
            noise = torch.randn(flat.numel(), generator=generator, device=flat.device)
            new_flat = mean + noise * std
        out[name] = new_flat.reshape(value.shape).to(value.dtype)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", required=True, help="обученный чекпоинт (nca_final.pt)")
    ap.add_argument("--out", required=True, help="куда сохранить (путь к nca_final.pt)")
    ap.add_argument("--seed", type=int, default=0, help="сид генератора перемешивания")
    ap.add_argument("--mode", choices=["shuffle", "rms"], default="shuffle")
    args = ap.parse_args(argv)

    checkpoint = torch.load(args.source, map_location="cpu", weights_only=False)
    if "model_state_dict" not in checkpoint:
        raise SystemExit(f"в {args.source} нет model_state_dict")

    generator = torch.Generator().manual_seed(int(args.seed))
    checkpoint["model_state_dict"] = randomize_state_dict(
        checkpoint["model_state_dict"], args.mode, generator
    )
    checkpoint["random_init"] = {
        "mode": args.mode,
        "seed": int(args.seed),
        "source": os.path.basename(os.path.dirname(os.path.abspath(args.source))),
    }

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    torch.save(checkpoint, out)
    print(f"[randinit] {args.mode}, seed={args.seed} -> {out}")
    print(f"[randinit] размер: {os.path.getsize(out) / 1e6:.1f} МБ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
