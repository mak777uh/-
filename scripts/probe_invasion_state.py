#!/usr/bin/env python
"""probe_invasion_state.py — проба пути инъекции: где и когда исчезает инвайдер (§10at.1).

Зачем: в §10at.1 утверждается, что инъекция исправна (20 клеток в состоянии сразу после
`_invade`), а стирает `enforce_colony_types()` — при `invade_at`, кратном 5, в том же шаге.
Утверждение было получено интерактивной пробой; этот скрипт делает его воспроизводимым
командой (рецензенту не нужен артефакт — нужна команда).

Запуск (из корня):

    python scripts/probe_invasion_state.py            # обе механики + фазы 200/201/202
    python scripts/probe_invasion_state.py --json out.json

Требует GPU или CPU (по умолчанию CPU: проба короткая, 200 шагов × 4 запуска).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MORPHO = ROOT / "morphogenesis"


def build(merge: str, invade_at: int, seed: int, device: str):
    sys.path.insert(0, str(MORPHO))
    from world.pond import PondConfig          # noqa: E402
    from world.run_pond import PondRun         # noqa: E402

    cfg = PondConfig(
        grid=32, resource_layout="uniform", income_mode="proportional",
        init_resource_fill=0.9, baseline_income=0.2, update_cost=0.02, repair_cost=0.02,
        budding_mass=24, budding_cost=0.2, spore_cells=2, spore_bias="score", w_rich=0.1,
        freq_dep=1.0, type_mode="mixfixed", type_level="colony",
        invade_at=invade_at, invade_type=1, invade_min_cells=30, invader_cells=20,
        invade_placement="random", merge_rule=merge,
    )
    run = PondRun(world_cfg=cfg, seed=seed, device=device,
                  rule_checkpoint=str((MORPHO / "checkpoints" / "world_base_rule.pt").resolve()))
    run.seed(cells=4, energy=8.0)
    return run


def probe(merge: str, invade_at: int, seed: int, device: str) -> dict:
    run = build(merge, invade_at, seed, device)
    pond = run.pond
    while int(pond.state.step) < invade_at - 1:
        run.step()
    seen = {"after_invade": None}
    original = pond._invade

    def wrapped():
        original()
        ct, alive = pond.state.cell_type, pond.state.alive
        seen["after_invade"] = int(((ct == 1) & alive).sum()) if ct is not None else -1

    pond._invade = wrapped
    trace = []
    for _ in range(4):
        run.step()
        ct, alive = pond.state.cell_type, pond.state.alive
        trace.append(int(((ct == 1) & alive).sum()) if ct is not None else -1)
    return {
        "merge": merge, "invade_at": invade_at, "seed": seed,
        "cells_after_invade": seen["after_invade"],
        "cells_after_steps": trace,
        "invader_cells_actual": getattr(pond, "invader_cells_actual", None),
        "invasion_step": getattr(pond, "invasion_step", None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    cases = [("keep", 200), ("majority", 200), ("majority", 201), ("majority", 202)]
    out = [probe(merge, at, args.seed, args.device) for merge, at in cases]
    print(f"{'плечо':>9} {'invade_at':>9} {'сразу после':>12} {'через 1..4 шага':>22}")
    for row in out:
        print(f"{row['merge']:>9} {row['invade_at']:>9} {row['cells_after_invade']:>12} "
              f"{str(row['cells_after_steps']):>22}")
    print("\nожидание (§10at.1): сразу после _invade = 20 во всех случаях; keep сохраняет, "
          "majority стирает на ближайшем тике enforce_colony_types (каждый 5-й шаг), "
          "поэтому при invade_at=200 (кратно 5) — ноль уже в первом шаге")
    if args.json:
        Path(args.json).write_text(json.dumps({"kind": "invasion_state_probe", "rows": out},
                                              ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        print(f"записано: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
