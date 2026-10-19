"""
gate_layer1.py — про гейт слоя 1 (§19.2, план WP3).

Запускает КОРОТКИЕ диагностические прогоны E02 (5 сидов, стресс включён) и
проверяет четыре условия гейта (с WP4b):

1. ткань не коллапсирует: alive_fraction >= относительного порога
   config.collapse_alive_fraction_min(плотность цели) — того же, из которого
   работает предохранитель в train.py, иначе гейт и обучение меряют разными
   линейками;

2. ПЕРВИЧНЫЙ эндпоинт (WP4): покрытие целевого множества растёт — f1 в конце
   прогона больше, чем в начале. Symmetric Chamfer для гейта непригоден:
   измерено (experiments/E02_pattern/collapse_probe.json), что он не наказывает
   перепокрытие (всё-белое поле 0.036 против 0.0 у идеального кольца) и легко
   выполняется мёртвой тканью;

3. симметричный Chamfer убывает — оставлен как ВТОРОЕ (диагностическое) условие
   и пишется в json, но решение о гейте по нему не принимается.

4. УДЕРЖАНИЕ (WP4b, §14.2): после RETENTION_GATE_STEPS автономных шагов лучший
   f1 по скану порогов (с условием живости) остаётся выше потолка
   бесструктурного предсказателя 2p/(1+p) с зазором 0.05. Добавлено по решению
   владельца спеки после NEG-17: пять сидов из пяти умирали на одной и той же
   итерации 200, а f1 на последнем шаге обучения не отличает «форма есть» от
   «форма была бы, если бы динамику выключить».

Отдельно пишется, но НЕ участвует в решении скан порога бинаризации (NEG-10):
f1@0.5 = 0 означает ещё и «выучила форму амплитудой ниже порога», поэтому в
результате каждого сида лежит лучший f1 по скану (с условием живости) и флаг
«выше потолка бесструктурного предсказателя 2p/(1+p)».

Полноценное обучение на TRAIN_MAX_STEPS=20000 — отдельный долгий прогон;
этот скрипт отвечает только на вопрос «ядро v5.6 вообще способно учиться
без смерти ткани». Результат пишется в experiments/E02_pattern/gate_layer1.json
вместе с траекториями, чтобы вывод можно было перепроверить.

Запуск:  python gate_layer1.py [--steps 400] [--seeds 42,101,202,303,404]
"""

import argparse

import json

import os

# §9.2: config раньше torch.

import config

import numpy as np

import torch

from utils.logging import final_run_rows


def _trajectory_rows(log_path):
    """Извлечение (iteration, chamfer, alive_fraction) из jsonl-лога прогона."""
    rows = []
    if not os.path.exists(log_path):
        return rows
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()

            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "symmetric_chamfer_error" in entry and "iteration" in entry:
                rows.append(
                    {
                        "iteration": entry["iteration"],
                        "chamfer": entry["symmetric_chamfer_error"],
                        # coverage нет в логах прогонов, запущенных до WP4:
                        # тогда ряд остаётся None, и гейт честно говорит, что
                        # первичный эндпоинт не измерен, а не подставляет ноль.
                        "coverage": entry.get("coverage"),
                        "alive_fraction": entry["loss"]["alive_fraction"],
                        "b0": entry["topology"]["b0"],
                        "b1": entry["topology"]["b1"],
                        "total": entry["loss"]["total"],
                    }
                )
    # Тот же лог мог содержать предыдущий прогон с этим experiment_id
    # (§7.7: лог append-история) — берём только последний прогон.
    return final_run_rows(rows)


def run_gate(steps, seeds, batch_size=None):
    from target_patterns import create_target
    from topology import get_binary_mask
    from evaluate import (
        compute_coverage_endpoints,
        compute_symmetric_chamfer_error,
        best_threshold_coverage,
    )
    from nca_core import run_steps_no_grad
    from train import train, alive_fraction_of

    os.makedirs(config.EXPERIMENT_DIR if hasattr(config, "EXPERIMENT_DIR") else "experiments", exist_ok=True)
    out_dir = os.path.join("experiments", "E02_pattern")
    os.makedirs(out_dir, exist_ok=True)

    original_ckpt = config.CHECKPOINT_DIR
    if batch_size:
        config.TRAIN_BATCH_SIZE = int(batch_size)
        config.TRAIN_SAMPLE_POOL_SIZE = max(config.TRAIN_SAMPLE_POOL_SIZE, config.TRAIN_BATCH_SIZE)

    # Порог живости для гейта = относительный порог предохранителя (WP4): у
    # цели ring плотность 0.1523, и абсолютный 0.15 стоит впритык к здоровой
    # ткани, т.е. меряет выбранное число, а не смерть.
    probe_target = create_target(device="cpu")
    target_density = float((probe_target > 0).float().mean().item())
    collapse_threshold = config.collapse_alive_fraction_min(target_density)
    print(
        f"[gate] плотность цели={target_density:.4f} порог не-коллапса={collapse_threshold:.4f} "
        f"(абсолютный COLLAPSE_ALIVE_FRACTION_MIN={config.COLLAPSE_ALIVE_FRACTION_MIN})"
    )

    results = []

    for seed in seeds:
        config.CHECKPOINT_DIR = os.path.join(original_ckpt, f"gate_layer1_s{steps}_seed{seed}")
        os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
        experiment_id = f"GATE_L1_s{steps}_seed{seed}"
        model, state = train(experiment_id=experiment_id, seed=seed, max_steps=steps)
        rows = _trajectory_rows(os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl"))
        target = create_target(device=config.DEVICE)
        with torch.no_grad():
            final_mask = get_binary_mask(state)
        target_np = (target[0, 0].detach().cpu().numpy() > 0.5).astype("uint8")
        final_chamfer = float(compute_symmetric_chamfer_error(final_mask, target_np))
        final_coverage = compute_coverage_endpoints(final_mask.astype(bool), target_np)
        # ВТОРИЧНЫЙ диагностический эндпоинт (NEG-10): скан порога бинаризации по
        # мягкому полю sigmoid(канал 0). Гейт по нему НЕ решается — штатный
        # эндпоинт §5.1 живёт при ALIVE_THRESHOLD=0.5, — но без него «f1=0»
        # неотличимо от «выучила форму амплитудой ниже порога».
        # Поле берётся с условием живости: по §5.7-5.8 мёртвая клетка обнуляется
        # целиком, её видимый канал = 0 и sigmoid(0) = 0.5, поэтому без gating
        # все мёртвые клетки ложно попали бы в предсказание при любом пороге<0.5.
        with torch.no_grad():
            soft = torch.sigmoid(state[0, config.VISIBLE_CHANNEL]).detach().cpu().numpy()
            alive0 = (
                torch.sigmoid(state[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
            ).detach().cpu().numpy()
        gated = np.where(alive0, soft, 0.0)
        scan = best_threshold_coverage(gated, target_np)
        ceiling = 2.0 * target_density / (1.0 + target_density)
        # +0.05 — тот же шумовой зазор, что в wp4_threshold_probe.py: потолок
        # бесструктурного «всё яркое» 2p/(1+p) достигается точно.
        beyond_ceiling = bool(scan["best"]["f1"] > ceiling + 0.05)
        # WP4b, §14.2 «удержать»: автономный прогон на RETENTION_GATE_STEPS шагов и
        # тот же скан порогов. Решение владельца спеки после NEG-17 (5 из 5
        # сидов умирают на итерации 200): «удержание» перестаёт быть текстом
        # гейта и становится условием, потому что f1 на последнем шаге обучения
        # ничего не говорит об устойчивости формы — NEG-10 измерил 0.4747 ->
        # 0.2783 после 200 автономных шагов. Инференс в eval(): channel dropout
        # и резервирование каналов (§12.1.6) training-only, иначе автономный
        # прогон мерил бы обучающую возмущающую добавку, а не динамику модели.
        model.eval()
        with torch.no_grad():
            held = run_steps_no_grad(model, state, steps=int(config.RETENTION_GATE_STEPS))
            held_soft = torch.sigmoid(held[0, config.VISIBLE_CHANNEL]).cpu().numpy()
            held_alive = (
                torch.sigmoid(held[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
            ).cpu().numpy()
            held_af = float(
                (torch.sigmoid(held[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD)
                .float()
                .mean()
                .item()
            )
        held_scan = best_threshold_coverage(np.where(held_alive, held_soft, 0.0), target_np)
        retention_ok = bool(held_scan["best"]["f1"] > ceiling + 0.05)
        model.train()
        alive_series = [r["alive_fraction"] for r in rows if r["iteration"] > config.ALIVE_WARMUP_ITERS]
        chamfer_series = [r["chamfer"] for r in rows]
        f1_series = [
            r["coverage"]["f1"] for r in rows if isinstance(r.get("coverage"), dict)
        ]
        min_alive = min(alive_series) if alive_series else float("nan")
        collapse_ok = bool(alive_series) and min_alive >= collapse_threshold
        decreasing_ok = bool(len(chamfer_series) >= 3) and chamfer_series[-1] <= chamfer_series[0] * 0.98
        # Первичный эндпоинт WP4 — покрытие, а не Chamfer: Chamfer не наказывает
        # перепокрытие (измерено: всё-белое поле 0.036 против 0.0 у идеального
        # кольца), f1 различает их. Условие гейта: f1 вырос за прогон.
        coverage_measured = len(f1_series) >= 3
        coverage_ok = bool(coverage_measured) and f1_series[-1] > f1_series[0]
        results.append(
            {
                "seed": int(seed),
                # Имя прогона пишется в результат, потому что отчёт WP4 сопоставляет
                # запись с логом logs/<experiment_id>_log.jsonl. Без этого поля
                # поиск идёт по шаблону имени, а шаблон менялся (GATE_L1_seedN →
                # GATE_L1_s800_seedN): молча взять кривую не от того прогона хуже,
                # чем не взять первичный эндпоинт вовсе.
                "experiment_id": experiment_id,
                "steps": int(steps),
                "batch_size": int(config.TRAIN_BATCH_SIZE),
                "alive_fraction_min": float(min_alive),
                "alive_fraction_final": float(alive_fraction_of(state)),
                "no_collapse": collapse_ok,
                "f1_first": f1_series[0] if f1_series else None,
                "f1_last": f1_series[-1] if f1_series else None,
                "f1_max": max(f1_series) if f1_series else None,
                "coverage_measured": coverage_measured,
                "coverage_improving": coverage_ok,
                "f1_final_eval": float(final_coverage["f1"]),
                # Вторичный диагностический эндпоинт (не влияет на gate_passed).
                "structureless_f1_ceiling": float(ceiling),
                "threshold_scan_gated": {
                    "f1_at_default_threshold": scan["f1_at_default_threshold"],
                    "best": scan["best"],
                    "gain_over_default": scan["gain_over_default"],
                },
                "structure_beyond_ceiling": beyond_ceiling,
                # Удержание (§14.2): форма после RETENTION_GATE_STEPS автономных
                # шагов. Это НЕ справочное число — см. gate_passed ниже.
                "retention_steps": int(config.RETENTION_GATE_STEPS),
                "retention_alive_fraction": held_af,
                "retention_f1_gated_best": held_scan["best"]["f1"],
                "retention_f1_at_default_threshold": held_scan["f1_at_default_threshold"],
                "retention_holds": retention_ok,
                "chamfer_first": chamfer_series[0] if chamfer_series else None,
                "chamfer_last": chamfer_series[-1] if chamfer_series else None,
                "chamfer_final_eval": final_chamfer,
                "chamfer_decreasing": decreasing_ok,
                "final_topology": rows[-1] if rows else None,
                "trajectory": rows,
            }
        )
        print(
            f"[gate] seed={seed} min_alive={min_alive:.3f} collapse_ok={collapse_ok} "
            f"f1 {f1_series[0] if f1_series else float('nan'):.4f} -> "
            f"{f1_series[-1] if f1_series else float('nan'):.4f} improving={coverage_ok} | "
            f"лучший f1 по порогу (gated)={scan['best']['f1']:.4f} @ "
            f"{scan['best']['threshold']:.4f} выше потолка={beyond_ceiling} | "
            f"chamfer {chamfer_series[0] if chamfer_series else float('nan'):.4f} -> "
            f"{chamfer_series[-1] if chamfer_series else float('nan'):.4f} "
            f"decreasing={decreasing_ok} | "
            f"удержание после {config.RETENTION_GATE_STEPS} автономных шагов: "
            f"f1(gated)={held_scan['best']['f1']:.4f} af={held_af:.3f} "
            f"holds={retention_ok}"
        )

    config.CHECKPOINT_DIR = original_ckpt

    summary = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "target_pattern": config.TARGET_PATTERN,
        "target_topology": dict(config.TARGET_TOPOLOGY),
        "target_density": target_density,
        "loss_weights": dict(config.LOSS_WEIGHTS),
        "alive_policy_mode": config.ALIVE_POLICY_MODE,
        "alpha_supervision_weight": float(config.ALPHA_SUPERVISION_WEIGHT),
        "collapse_threshold": collapse_threshold,
        "collapse_threshold_absolute": config.COLLAPSE_ALIVE_FRACTION_MIN,
        "collapse_threshold_ratio": config.COLLAPSE_ALIVE_FRACTION_RATIO,
        "seeds_passed_no_collapse": sum(r["no_collapse"] for r in results),
        # Первичный счёт гейта — покрытие; Chamfer остаётся справочным числом.
        "seeds_passed_coverage": sum(r["coverage_improving"] for r in results),
        "seeds_with_coverage_measured": sum(r["coverage_measured"] for r in results),
        "seeds_passed_chamfer": sum(r["chamfer_decreasing"] for r in results),
        # Справочный счётчик (NEG-10): сколько сидов показали структуру ВЫШЕ
        # потолка бесструктурного предсказателя при калибровке порога.
        "structureless_f1_ceiling": 2.0 * target_density / (1.0 + target_density),
        "seeds_with_structure_beyond_ceiling": sum(r["structure_beyond_ceiling"] for r in results),
        # Удержание (§14.2) — четвёртое условие гейта с WP4b; считается по
        # автономному прогону в RETENTION_GATE_STEPS шагов, а не по последнему
        # шагу обучения.
        "seeds_passed_retention": sum(r["retention_holds"] for r in results),
        "retention": {
            "autonomous_steps": int(config.RETENTION_GATE_STEPS),
            "condition": "лучший gated f1 после автономных шагов > потолок + 0.05",
            "structureless_f1_ceiling": 2.0 * target_density / (1.0 + target_density),
            "trained_with_rollout_loss": bool(config.RETENTION_ENABLED),
            "rollout_loss_weight": float(config.LOSS_WEIGHTS.get("retention", 0.0)),
            "rollout_loss_steps": int(config.RETENTION_ROLLOUT_STEPS),
        },
        "runs": results,
    }
    # Решение по гейту: живая ткань И растущее покрытие И удержанная форма на
    # КАЖДОМ сиде. Chamfer в решение не входит (см. модульный докстринг) — он
    # справочный.
    n = len(results)
    summary["gate_passed"] = bool(
        n > 0
        and summary["seeds_passed_no_collapse"] == n
        and summary["seeds_with_coverage_measured"] == n
        and summary["seeds_passed_coverage"] == n
        and summary["seeds_passed_retention"] == n
    )
    path = os.path.join(out_dir, "gate_layer1.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"[gate] записано: {path}")
    print(
        f"[gate] итог: сидов={n} без_коллапса={summary['seeds_passed_no_collapse']} "
        f"покрытие_измерено={summary['seeds_with_coverage_measured']} "
        f"покрытие_растёт={summary['seeds_passed_coverage']} "
        f"структура_выше_потолка(справочно)={summary['seeds_with_structure_beyond_ceiling']} "
        f"chamfer_убывает(справочно)={summary['seeds_passed_chamfer']} "
        f"удержание={summary['seeds_passed_retention']}/{n} "
        f"гейт={'ПРОЙДЕН' if summary['gate_passed'] else 'НЕ ПРОЙДЕН'}"
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--seeds", type=str, default="42,101,202,303,404")
    parser.add_argument("--batch-size", type=int, default=None)
    args = parser.parse_args()
    run_gate(steps=args.steps, seeds=[int(s) for s in args.seeds.split(",")], batch_size=args.batch_size)
