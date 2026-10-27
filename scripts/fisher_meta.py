#!/usr/bin/env python
"""fisher_meta.py — критерий на среднем по Фишеру для серии one-bud (H-ALIVE-53).

Читает артефакты `w2bud_onebud/*.json`, считает ρ_partial по каждому прогону **тем же кодом, что
основной агрегатор** (`w2bud_matrix.analyse`), и применяет пре-регистрацию
`reports/2026-10-27-fisher-plan.md`:

    центр      = tanh(mean z),  z = artanh(ρ)
    верхняя    = tanh(mean z + 1.96·SD(z)/√n)
    вердикт    = «цена ≥ 0.3», если центр ≤ −0.3 И верхняя < −0.3
    опровержение = верхняя ≥ −0.3 при N = 15 ⇒ величина не определяется статистикой

Публикуется и медиана (старая оценка), чтобы читатель видел, чем именно получен вердикт.

Запуск (из корня repo):

    python scripts/fisher_meta.py --out morphogenesis/experiments/E09_pond/w2bud_onebud_fisher_matrix.json
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD = -0.3
PREREG_N = 15


def load_analyser():
    spec = importlib.util.spec_from_file_location("wm", ROOT / "scripts" / "w2bud_matrix.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fisher_block(values: list[float], label: str) -> dict:
    n = len(values)
    if n < 2:
        return {"label": label, "n": n, "center": None, "upper": None, "lower": None}
    zs = [math.atanh(max(min(v, 0.999999), -0.999999)) for v in values]
    mz = statistics.mean(zs)
    sd = statistics.stdev(zs)
    se = sd / math.sqrt(n)
    return {
        "label": label,
        "n": n,
        "mean_rho_arithmetic": round(statistics.mean(values), 4),
        "median_rho": round(statistics.median(values), 4),
        "mean_z": round(mz, 4),
        "sd_z": round(sd, 4),
        "se_z": round(se, 4),
        "center": round(math.tanh(mz), 4),
        "lower": round(math.tanh(mz - 1.96 * se), 4),
        "upper": round(math.tanh(mz + 1.96 * se), 4),
        "q1": round(statistics.quantiles(values, n=4)[0], 4),
        "q3": round(statistics.quantiles(values, n=4)[2], 4),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud_onebud")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    wm = load_analyser()
    rows = []
    for path in sorted(glob.glob(str(Path(args.src) / "w2bud_onebud_cell_seed*.json"))):
        result = wm.analyse(Path(path))
        if result is None:
            continue
        rows.append({
            "seed": result["seed"],
            "rho": result["rho_partial_energy"],
            "rho_hybrid": result.get("rho_partial_energy_hybrid"),
            "lines": result["lineages_with_data"],
            "artifact": str(path).replace("\\", "/"),
        })

    old = [r["rho"] for r in rows if r["seed"] <= 110 and r["rho"] is not None]
    new = [r["rho"] for r in rows if r["seed"] >= 201 and r["rho"] is not None]
    allv = [r["rho"] for r in rows if r["rho"] is not None]

    blocks = [
        fisher_block(old, "существующие сиды 101-110"),
        fisher_block(new, "новые сиды 201-215"),
        fisher_block(allv, "объединённые"),
    ]
    combined = blocks[2]
    verdict = None
    if combined["center"] is not None:
        if combined["center"] <= THRESHOLD and combined["upper"] < THRESHOLD:
            verdict = "цена >= 0.3 (центр и верхняя граница ниже порога)"
        elif combined["upper"] >= THRESHOLD and len([r for r in rows if r["seed"] >= 201]) >= PREREG_N:
            launched_new = len([r for r in rows if r["seed"] >= 201])
            verdict = ("величина не определяется статистикой: верхняя граница "
                       f"{combined['upper']:+.3f} >= -0.3 при N = {launched_new} новых сидов "
                       "(пре-регистрация: вопрос закрывается)")
        else:
            verdict = "недостаточно прогонов для критерия"

    payload = {
        "kind": "onebud_fisher",
        "world": "W2-bud, --one-bud-per-lineage; расширение сидов 201-215 (H-ALIVE-53)",
        "prereg": "reports/2026-10-27-fisher-plan.md",
        "metric": {
            "rho": "стандартный частный Спирмен (ранги → остатки по энергии → Пирсон), тот же код, что w2bud_matrix.analyse",
            "center": "tanh(mean artanh(rho)) — среднее по Фишеру",
            "interval": "tanh(mean z ± 1.96·SD(z)/√n), n = прогоны с вычислимой rho",
            "threshold": THRESHOLD,
            "criterion": "центр <= -0.3 И верхняя граница < -0.3",
            "refutation": "верхняя граница >= -0.3 при N = 15 новых сидов ⇒ величина не определяется статистикой",
        },
        "series_mask": "w2bud_onebud/w2bud_onebud_cell_seed*.json",
        "series_mask_note": (
            "маска — часть определения агрегата (§3c): одна серия one-bud, старые сиды 101-110 и новые "
            "201-215; блоки считаются отдельно, чтобы видеть, что дало расширение"
        ),
        "rho_undefined_note": (
            "rho не вычислима, когда частная корреляция вырождена: если cell_steps и энергия "
            "идеально совпадают по рангам (Spearman = 1.0), остаток после контроля энергии имеет "
            "нулевую дисперсию и частная корреляция не определена (0/0), а не равна нулю"
        ),
        "rows": rows,
        "blocks": blocks,
        "valid_n": len(allv),
        "seeds_without_rho": [r["seed"] for r in rows if r["rho"] is None],
        "verdict": verdict,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out}")
    for b in blocks:
        if b["center"] is None:
            print(f"{b['label']:>24}: n={b['n']} — недостаточно")
            continue
        print(f"{b['label']:>24}: n={b['n']:>2} | медиана {b['median_rho']:+.3f} | "
              f"центр(Фишер) {b['center']:+.3f} | ДИ [{b['lower']:+.3f}, {b['upper']:+.3f}]")
    print(f"\nвердикт: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
