"""Экологическое наследование B2 (исправленная версия).

Сравниваем НЕ с абиотическим полем (организмы потребляют ресурс, и разница всегда
отрицательна), а с КОНТРОЛЕМ без строительства при том же сиде. Тогда:
  избыток = поле(строительство) − поле(контроль),
  полураспад = сколько шагов живёт этот избыток, если организмы убрать.
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


def field_after(cfg: PondConfig, steps: int, seed: int, device: str,
                checkpoint: str) -> torch.Tensor:
    run = PondRun(world_cfg=cfg, seed=seed, device=device, rule_checkpoint=checkpoint)
    run.seed(cells=4, energy=8.0)
    run.run(steps, log_every=steps)
    return run.pond.state.resource.detach().clone()


def decay_half_life(built: torch.Tensor, control: torch.Tensor, cfg: PondConfig,
                    seed: int, device: str, steps: int, start_step: int) -> tuple:
    pa = Pond(cfg, device=device, seed=seed)
    pb = Pond(cfg, device=device, seed=seed)
    pa.state.resource = built.clone()
    pb.state.resource = control.clone()
    pa.state.step = start_step
    pb.state.step = start_step
    diff0 = float((pa.state.resource - pb.state.resource).abs().mean())
    if diff0 <= 1e-9:
        return None, []
    series = []
    half = None
    for k in range(steps):
        pa.state.step += 1
        pb.state.step += 1
        pa.regenerate()
        pb.regenerate()
        cur = float((pa.state.resource - pb.state.resource).abs().mean()) / diff0
        series.append(round(cur, 4))
        if half is None and cur <= 0.5:
            half = k + 1
    return half, series


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--env", default="uniform", choices=list(ENVS))
    ap.add_argument("--invest-rate", type=float, default=0.02)
    ap.add_argument("--invest-mode", default="fixed", choices=["fixed", "surplus"])
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--decay", type=int, default=120)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--checkpoint", default="checkpoints/world_base_rule.pt")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows = []
    for seed in args.seeds:
        cfg_build = make_cfg(args.env, args.invest_rate, args.invest_mode)
        cfg_ctrl = make_cfg(args.env, 0.0, "none")
        built = field_after(cfg_build, args.steps, seed, args.device, args.checkpoint)
        control = field_after(cfg_ctrl, args.steps, seed, args.device, args.checkpoint)
        diff = float((built - control).abs().mean())
        half, series = decay_half_life(built, control, cfg_build, seed, args.device,
                                       args.decay, args.steps)
        rows.append({"env": args.env, "seed": seed, "mode": args.invest_mode,
                     "excess_mean_abs": round(diff, 6), "half_life_steps": half,
                     "decay": series[:20]})
    payload = {"env": args.env, "invest_mode": args.invest_mode,
               "invest_rate": args.invest_rate, "rows": rows}
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    if args.out:
        json.dump(payload, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
