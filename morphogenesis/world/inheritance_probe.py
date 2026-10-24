"""Экологическое наследование: сколько живёт поднятый ресурс после удаления организмов.

Зачем (B2): ниша — это изменение среды, которое переживает своего строителя.
Меряем: (1) избыток ресурса против абиотического контроля в конце прогона;
(2) время полураспада этого избытка, если организмы убрать и оставить только
динамику среды.

Запуск:
    python world/inheritance_probe.py --env uniform --invest-mode learn \
        --invest-rate 0.02 --seeds 1 2 3 --steps 300 --decay 120
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

from world.pond import Pond, PondConfig  # noqa: E402
from world.run_pond import PondRun  # noqa: E402


ENVS = {
    "uniform": dict(resource_layout="uniform"),
    "patches": dict(resource_layout="patches"),
    "gradflip": dict(resource_layout="gradient", flip_at=150),
}


def make_cfg(env: str, invest_rate: float, invest_mode: str) -> PondConfig:
    base = dict(grid=32, income_mode="proportional", init_resource_fill=0.9,
                baseline_income=0.2, update_cost=0.02, repair_cost=0.02,
                budding_mass=24, budding_cost=0.2, invest_rate=invest_rate,
                invest_mode=invest_mode)
    base.update(ENVS[env])
    return PondConfig(**base)


def resource_field_after_organisms(cfg: PondConfig, steps: int, seed: int, device: str,
                                   checkpoint: str) -> torch.Tensor:
    run = PondRun(world_cfg=cfg, seed=seed, device=device, rule_checkpoint=checkpoint)
    run.seed(cells=4, energy=8.0)
    run.run(steps, log_every=steps)
    return run.pond.state.resource.detach().clone()


def abiotic_field(cfg: PondConfig, steps: int, seed: int, device: str) -> torch.Tensor:
    pond = Pond(cfg, device=device, seed=seed)
    for _ in range(steps):
        pond.state.step += 1
        pond.regenerate()
    return pond.state.resource.detach().clone()


def decay_half_life(field: torch.Tensor, abiotic_end: torch.Tensor, cfg: PondConfig,
                    seed: int, device: str, steps: int) -> tuple[int | None, list[float]]:
    """Полураспад избытка ресурса при выключенных организмах."""
    pond = Pond(cfg, device=device, seed=seed)
    pond.state.resource = field.clone()
    pond.state.step = steps
    excess0 = float((field - abiotic_end).clamp_min(0.0).sum())
    if excess0 <= 1e-6:
        return None, []
    series = []
    half = None
    for k in range(steps):
        pond.state.step += 1
        pond.regenerate()
        # абиотический контроль той же длины: регенерация без организмов
        cur = float((pond.state.resource - abiotic_end).clamp_min(0.0).sum())
        series.append(round(cur / excess0, 4))
        if half is None and cur <= excess0 / 2:
            half = k + 1
    return half, series


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--env", default="uniform", choices=list(ENVS))
    ap.add_argument("--invest-rate", type=float, default=0.02)
    ap.add_argument("--invest-mode", default="learn", choices=["fixed", "learn", "none"])
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--decay", type=int, default=120)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--checkpoint", default="checkpoints/world_base_rule.pt")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows = []
    for seed in args.seeds:
        cfg = make_cfg(args.env, args.invest_rate, args.invest_mode)
        with_org = resource_field_after_organisms(cfg, args.steps, seed, args.device, args.checkpoint)
        abiotic = abiotic_field(cfg, args.steps, seed, args.device)
        excess = float((with_org - abiotic).clamp_min(0.0).sum())
        half, series = decay_half_life(with_org, abiotic, cfg, seed, args.device, args.decay)
        rows.append({"env": args.env, "seed": seed, "invest_mode": args.invest_mode,
                     "excess_end": round(excess, 3), "half_life_steps": half,
                     "decay": series[:20]})
    payload = {"env": args.env, "invest_mode": args.invest_mode,
               "invest_rate": args.invest_rate, "rows": rows}
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    if args.out:
        json.dump(payload, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
