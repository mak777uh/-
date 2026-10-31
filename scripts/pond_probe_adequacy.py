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
import random
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


def cost_schedule(steps: int, period: int, cheap_share: float, low: float, high: float,
                  shuffle: bool, seed: int) -> list[float]:
    """X42: расписание цены обслуживания. Дешёвая фаза — окно роста, дорогая — окно нужды.

    При `shuffle` тот же набор значений (и та же доля дешёвых) идёт в случайном порядке: ритм есть, а
    предсказуемости нет. Это контроль на то, что мера ловит именно ритм, а не уровень цены.
    """
    n_cheap = max(1, int(round(period * cheap_share)))
    block = [low] * n_cheap + [high] * (period - n_cheap)
    sched: list[float] = []
    rng = random.Random(seed * 7919 + 17)
    while len(sched) < steps:
        chunk = list(block)
        if shuffle:
            rng.shuffle(chunk)
        sched.extend(chunk)
    return sched[:steps]


def run_once(arm: str, seed: int, steps: int, stream: str | None = None,
             stream_coupling: float = 1.0, plastic: bool = False, plastic_eta: float = 0.3,
             cost_period: int = 0, cost_cheap_share: float = 0.4, cost_low: float = 0.002,
             cost_high: float = 0.02, cost_shuffle: bool = False,
             floor: float = 0.0, income: float | None = None, ghost: bool = False) -> dict:
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

    over = dict(ARMS[arm])
    stream_values = None
    if stream:
        raw = json.loads(Path(stream).read_text(encoding="utf-8"))
        stream_values = [float(v) for v in (raw.get("values") or [])]
        over["inflow_coupling"] = float(stream_coupling)
        over["inflow_stream_mode"] = "global"
        over["inflow_target"] = "income"
    if plastic:
        over["plastic_eta"] = float(plastic_eta)
    if floor > 0.0:
        over["alive_floor"] = float(floor)
    if income is not None:
        over["baseline_income"] = float(income)
    if ghost:
        over["ghost_no_consumption"] = True
    cfg = PondConfig(**over)
    if stream_values:
        # как в run_pond.py: `inflow_values` и `inflow_scale` — атрибуты, а не поля dataclass
        cfg.inflow_values = list(stream_values)
        cfg.inflow_scale = torch.ones((cfg.grid, cfg.grid), device="cpu")
    # Без обученного правила мир вымирает: CNCA по умолчанию — случайные веса, и «жизнь» в нём
    # не держится (проверено: все варианты дали 0 живых к 200 шагам). Серии пруда используют
    # замороженное правило — берём его же.
    rule = ROOT / "morphogenesis" / "checkpoints" / "world_base_rule.pt"
    run = PondRun(world_cfg=cfg, seed=seed, device="cpu",
                  rule_checkpoint=str(rule) if rule.exists() else None)
    if stream_values:
        # как в run_pond.py:1321 — множитель притока выделяет сам прогон, а не конфиг
        run.pond.state.income_scale = torch.ones((cfg.grid, cfg.grid), device="cpu")
    run.seed(cells=4, energy=8.0)

    sched = (cost_schedule(steps, cost_period, cost_cheap_share, cost_low, cost_high, cost_shuffle, seed)
             if cost_period > 0 else None)
    if sched is not None:
        run.pond.cfg.update_cost = float(sched[0])

    S, E, alive_n, costs = [], [], [], []
    for t in range(steps):
        if sched is not None:
            # цена читается в pond.py:813 на каждом шаге, поэтому менять её из зонда безопасно
            run.pond.cfg.update_cost = float(sched[t])
        run.step()
        if t % SAMPLE_EVERY:
            continue
        s = run.pond.state
        alive = s.alive
        n = int(alive.sum())
        alive_n.append(n)
        if sched is not None:
            costs.append(round(float(sched[t]), 5))
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
            "stream": Path(stream).name if stream else None,
            "stream_value_at_sample": [stream_values[i] for i in range(0, min(len(stream_values or []), steps), SAMPLE_EVERY)]
            if stream_values else None,
            "plastic": bool(plastic),
            "cost_schedule": costs or None,
            "cost_period": cost_period, "cost_cheap_share": cost_cheap_share if cost_period else None,
            "cost_low": cost_low if cost_period else None, "cost_high": cost_high if cost_period else None,
            "cost_shuffle": bool(cost_shuffle),
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
    ap.add_argument("--stream", default=None,
                    help="X41: JSON-ряд притока (периодический или его перемешанная копия)")
    ap.add_argument("--stream-coupling", type=float, default=1.0)
    ap.add_argument("--plastic", action="store_true", help="X41: включить пластичность (plastic_eta)")
    ap.add_argument("--plastic-eta", type=float, default=0.3)
    ap.add_argument("--label", default=None, help="метка плеча для артефакта")
    ap.add_argument("--cost-period", type=int, default=0,
                    help="X42: период колебания цены обслуживания (0 = цена постоянна)")
    ap.add_argument("--cost-cheap-share", type=float, default=0.4,
                    help="X42: доля периода, когда цена низкая (окно роста)")
    ap.add_argument("--cost-low", type=float, default=0.002, help="X42: низкая цена (update_cost)")
    ap.add_argument("--cost-high", type=float, default=0.02, help="X42: высокая цена (update_cost)")
    ap.add_argument("--income", type=float, default=None,
                    help="X43: baseline_income (доход). Максимум дохода за шаг = 4*income*own")
    ap.add_argument("--ghost", action="store_true",
                    help="X50: контроль «призрак» — доход есть, но ресурс не выедается, действие на среду заблокировано")
    ap.add_argument("--floor", type=float, default=0.0,
                    help="X43: порог ресурса (хемостат); 0 = выключено")
    ap.add_argument("--cost-shuffle", action="store_true",
                    help="X42: перемешать фазы (тот же набор цен, случайный порядок) — контроль на ритм")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    if args.series:
        for arm in ("cost", "cheap", "free"):
            for k in range(args.series):
                seed = args.seed_start + k
                print(f"[x33] {arm} seed={seed}", flush=True)
                runs.append(run_once(arm, seed, args.steps, args.stream, args.stream_coupling,
                                     args.plastic, args.plastic_eta, args.cost_period,
                                     args.cost_cheap_share, args.cost_low, args.cost_high, args.cost_shuffle,
                                     args.floor, args.income, args.ghost))
    else:
        for k in range(args.seeds):
            runs.append(run_once(args.arm or "cost", args.seed_start + k, args.steps, args.stream,
                                 args.stream_coupling, args.plastic, args.plastic_eta, args.cost_period,
                                 args.cost_cheap_share, args.cost_low, args.cost_high, args.cost_shuffle,
                                 args.floor, args.income, args.ghost))

    out.write_text(json.dumps({"kind": "x33_adequacy", "runs": runs}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"[x33] записано: {out} | прогонов {len(runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
