"""pond_probe_adequacy.py — X33: несёт ли состояние организма информацию о БУДУЩЕМ среды.

Идея владельца: разум/жизнь — это адекватный отклик миру, «даёт ему истину». Измеримая замена:

    адекватность = I(S_t ; E_{t+1}) против I(S_t ; E^shuffled_{t+1})

где `S_t` — состояние обитателей (энергия, повреждение, потребление), `E_t` — состояние среды (ресурс).

Гипотеза X33: адекватность возникает там, где **ошибаться дорого**. Поэтому три плеча:

  * `cost`  — обычная цена обслуживания (update_cost 0.01, repair_cost 0.02);
  * `cheap` — цена в пять раз ниже;
  * `free`  — платить не за что (все стоимости нулевые).

Пилот показал, что дело не в еде: ресурс под живыми держится на 0.998, а энергия клетки падает — значит валюта
это пропускная способность, и менять нужно цену, а не приток.

Критерий (зафиксирован до данных): в `cost` разница `I − I_shuffled` положительна на ≥7 из 10 сидов,
а в `free` — меньше половины этой величины. Иначе «адекватность не установлена».

Зонд **не меняет мир**: он вызывает `PondRun.step()` и читает `pond.state`, ничего не подменяя.
Поэтому якорь тривиален — но проверяется (см. `--anchor`: сравнение итогов с прогоном без зонда).

Запуск:
    python scripts/pond_probe_adequacy.py --arm cost --seeds 1 --steps 60 --out ../_hourly/pa_smoke.json
    python scripts/pond_probe_adequacy.py --series 10 --steps 1200 --out ../_hourly/pa_series.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "morphogenesis"))

SAMPLE_EVERY = 1

# Поправка после пилота (§10df): еда в пруду не валюта — ресурс под живыми держится на 0.998 при падающей
# энергии, клетка гибнет от цены обслуживания. Поэтому плечи различаются ЦЕНОЙ, а не количеством еды.
ARMS = {
    "cost": {},                                                     # обычная цена
    "cheap": {"update_cost": 0.002, "repair_cost": 0.004},          # цена в 5 раз ниже
    "free": {"update_cost": 0.0, "repair_cost": 0.0, "membrane_rebuild_cost": 0.0},  # платить не за что
}


def run_once(arm: str, seed: int, steps: int) -> dict:
    import random

    import numpy as np
    import torch
    from world.pond import PondConfig
    from world.run_pond import PondRun

    # Якорь: main() сеет глобальные ГПСЧ (run_pond.py:1289-1294), и без этого мир недетерминирован —
    # два одинаковых прогона зонда дали 0 и 163 клетки. Повторяем ровно то же.
    torch.manual_seed(int(seed))
    random.seed(int(seed))
    np.random.seed(int(seed))

    cfg = PondConfig(**ARMS[arm])
    # Без обученного правила мир вымирает: CNCA по умолчанию — случайные веса, и «жизнь» в нём
    # не держится (проверено: все варианты дали 0 живых к 200 шагам). Серии пруда используют
    # замороженное правило — берём его же.
    rule = ROOT / "morphogenesis" / "checkpoints" / "world_base_rule.pt"
    run = PondRun(world_cfg=cfg, seed=seed, device="cpu",
                  rule_checkpoint=str(rule) if rule.exists() else None)
    run.seed(cells=4, energy=8.0)

    S, E, alive_n = [], [], []
    for t in range(steps):
        run.step()
        if t % SAMPLE_EVERY:
            continue
        s = run.pond.state
        alive = s.alive
        n = int(alive.sum())
        alive_n.append(n)
        if n:
            S.append({
                "energy": float(s.energy[alive].to(torch.float32).mean()),
                "damage": float(s.damage[alive].to(torch.float32).mean()),
                "consumed": float(s.consumed_total),
            })
            E.append({
                "resource_under_alive": float(s.resource[alive].mean()),
                "resource_empty": float(s.resource[~alive].mean()) if bool((~alive).any()) else None,
            })
        else:
            S.append({"energy": 0.0, "damage": 0.0, "consumed": 0.0})
            E.append({"resource_under_alive": None, "resource_empty": float(s.resource.mean())})

    return {"arm": arm, "seed": seed, "steps": steps, "sample_every": SAMPLE_EVERY,
            "alive_series": alive_n,
            "S": S, "E": E,
            "final": {"alive": alive_n[-1] if alive_n else 0,
                      "resource_mean": float(run.pond.state.resource.mean())}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X33: адекватность как информация о будущем среды")
    ap.add_argument("--arm", choices=sorted(ARMS), default=None)
    ap.add_argument("--series", type=int, default=0, help="число сидов на плечо (все три плеча)")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--seed-start", type=int, default=1)
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    if args.series:
        for arm in ("cost", "cheap", "free"):
            for k in range(args.series):
                seed = args.seed_start + k
                print(f"[x33] {arm} seed={seed}", flush=True)
                runs.append(run_once(arm, seed, args.steps))
    else:
        for k in range(args.seeds):
            runs.append(run_once(args.arm or "cost", args.seed_start + k, args.steps))

    out.write_text(json.dumps({"kind": "x33_adequacy", "runs": runs}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"[x33] записано: {out} | прогонов {len(runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
