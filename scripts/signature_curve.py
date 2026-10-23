#!/usr/bin/env python
"""Кривая подписи: (компоненты, полости, плотность) как функция горизонта обучения.

Зачем: после находки «проектор на модельные инварианты» главный объект статьи —
подпись модели. Нужна её зависимость от горизонта обучения: одна точка на
чекпоинт, короткий прогон проекции (случайная маска → 2000 шагов → (b0, b1, ρ)).

Запуск (cwd = morphogenesis):

    python ../scripts/signature_curve.py --groups seed42,seed202,seed101,fp32 \
        --density 0.5 --starts 8 --out experiments/E02c_replication/signature_curve.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
MORPH = os.path.join(os.path.dirname(HERE), "morphogenesis")
if MORPH not in sys.path:
    sys.path.insert(0, MORPH)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import config  # noqa: E402
import morphometry as mm  # noqa: E402
import e02b_morphospace as e02b  # noqa: E402
import topology  # noqa: E402


GROUPS = {
    "seed42": [1000, 2000, 3000, 4000],
    "seed202": [1000, 2000, 3000, 4000],
    "seed101": [1000, 1250, 1500, 1750, 2000],
    "fp32": [1000, 2000, 3000, 4000],
}


def family_for(group: str, steps: int) -> str:
    if group == "seed42":
        return f"E02c_R-9_s{steps}_seed42_tf32"
    if group == "seed202":
        return f"E02c_R-9_s{steps}_seed202_tf32"
    if group == "seed101":
        return f"E02c_R-9_s{steps}_seed101_tf32"
    if group == "fp32":
        return f"E02c_R-9_s{steps}_seed42_fp32"
    raise SystemExit(f"неизвестная группа {group}")


def signature(checkpoint_dir: str, density: float, starts: int, rollout: int,
              device: torch.device) -> dict:
    """Спроецировать случайные маски и вернуть подпись (средние по стартам)."""
    model, spec = mm._build_model(checkpoint_dir, device)
    rng = np.random.default_rng(1234)
    b0s, b1s, dens = [], [], []
    for _ in range(starts):
        mask = rng.random((config.GRID_SIZE, config.GRID_SIZE)) < density
        state = torch.zeros((1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE), device=device)
        vis = torch.full((config.GRID_SIZE, config.GRID_SIZE), -20.0, device=device)
        vis[torch.from_numpy(mask).to(device)] = 20.0
        state[0, config.VISIBLE_CHANNEL] = vis
        state[0, config.ALIVE_CHANNEL] = vis
        final_state, _p, _t, _e = e02b.rollout(model, state, rollout, 100)
        final_mask = topology.get_binary_mask(final_state)
        topo = mm.components_and_holes(final_mask)
        b0s.append(topo["b0"])
        b1s.append(topo["b1"])
        dens.append(float(final_mask.mean()))
    return {
        "family": spec.family,
        "b0": float(np.mean(b0s)),
        "b1": float(np.mean(b1s)),
        "density": float(np.mean(dens)),
        "b0_std": float(np.std(b0s)),
        "density_std": float(np.std(dens)),
        "starts": starts,
        "input_density": density,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--groups", default="seed42,seed202,seed101,fp32")
    ap.add_argument("--density", type=float, default=0.5)
    ap.add_argument("--starts", type=int, default=8)
    ap.add_argument("--rollout", type=int, default=2000)
    ap.add_argument("--out", default="experiments/E02c_replication/signature_curve.json")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    rows: list[dict] = []
    for group in [g.strip() for g in args.groups.split(",") if g.strip()]:
        for steps in GROUPS[group]:
            family = family_for(group, steps)
            path = os.path.join("checkpoints", family)
            if not os.path.exists(os.path.join(path, "nca_final.pt")):
                print(f"[signature] нет чекпоинта {family} — пропуск", flush=True)
                continue
            sig = signature(path, args.density, args.starts, args.rollout, device)
            sig["group"] = group
            sig["steps"] = steps
            rows.append(sig)
            print(f"[signature] {group:8s} {steps:5d} -> b0={sig['b0']:7.1f} "
                  f"b1={sig['b1']:7.1f} rho={sig['density']:.3f}", flush=True)

    payload = {"input_density": args.density, "rollout": args.rollout, "rows": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"[signature] записано: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
