"""Облегчить чекпоинт для инференса: только веса правила + метаданные.

Зачем: наши `nca_final.pt` весят ~514 МБ, хотя само правило — единицы мегабайт.
Внутри лежат ещё оптимизатор (Adam: два момента), состояние пула и снимок состояния —
всё это нужно для продолжения тренировки, но не для анализа и не для депозита.

Использование:
    python scripts/slim_checkpoint.py <вход.pt> [--out <выход.pt>]
Печатает размеры до и после. Канонические файлы не перезаписываются без --out.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch


def slim(payload: dict) -> dict:
    """Оставить только то, что нужно для инференса и трассировки."""
    keep = {}
    for key in ("model_state_dict", "iteration", "metadata", "config", "seed", "loss"):
        if key in payload:
            keep[key] = payload[key]
    if "model_state_dict" not in keep:
        raise SystemExit("в файле нет model_state_dict — это не чекпоинт правила")
    return keep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    src = Path(args.source)
    payload = torch.load(src, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise SystemExit("неожиданный формат чекпоинта")
    out = Path(args.out) if args.out else src.with_name(src.stem + ".lite.pt")
    torch.save(slim(payload), out)

    before = src.stat().st_size / 1e6
    after = out.stat().st_size / 1e6
    print(f"{src.name}: {before:.1f} МБ -> {out.name}: {after:.1f} МБ "
          f"({before / after:.1f}x меньше)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
