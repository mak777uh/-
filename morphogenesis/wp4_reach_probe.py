"""
wp4_reach_probe.py — разделяет «удержать» и «дособирать» (WP4b, §14.2).

Зачем. Все числа f1, которые WP4 мерил до сих пор, снимаются с состояния, в
котором модель ОКАЗЫВАЕТСЯ в процессе: траектория обучения — это пул, который
сам порождает следующие состояния (train.py: `state = run_steps(...)`, затем
`pool.update(state, ...)`), а гейтное «удержание» (gate_layer1) продолжает
последний шаг обучения. Поэтому «f1 = 0» у R-плечей означает сразу два разных
утверждения — «не дорастает до кольца» и «дорастает, но в этом состоянии не
остаётся», — а для постановки E02 это разные приговоры.

Что делает зонд. Для каждого чекпоинта WP4 прогоняет ДВЕ автономные развёртки
без обучения и без градиента:

  reach — старт из свежего шума (init_state, детерминированный генератор §9.2):
    «является ли кольцо ДОСТИЖИМЫМ состоянием этих динамик»;
  hold  — старт из target_conditioned_state (видимый канал = цель, живы все):
    «является ли кольцо УСТОЙЧИВЫМ состоянием этих динамик».

Кольцо, устойчивое, но недостижимое, — неподвижная точка, а не морфогенез:
§14.2 требует роста из шума, а H-P1 (пул стартует из цели, f1=1.000 на всех
восьми точках лога) как раз показывает, что устойчивость сама по себе тривиальна.

Критерий тот же, что у гейта слоя 1, чтобы числа были сопоставимы: лучший по
скану порогов f1 (С условием живости — NEG-10: §5.8 обнуляет мёртвую клетку
целиком, sigmoid(0)=0.5, и без условия все мёртвые клетки ложно считаются
яркими) против потолка бесструктурного поля 2p/(1+p) с зазором 0.05.

Ничего не обучает, ничего не переписывает (§7.7): результат — отдельный
артефакт experiments/E02_pattern/wp4_reach_probe.json.

Запуск:  python wp4_reach_probe.py [--steps 200] [--arms R-9,R-8,H-A0] [--all-seeds]
"""

import argparse

import glob

import json

import os

import re

# §9.2: config раньше torch.

import config

import numpy as np

import torch

from evaluate import best_threshold_coverage, compute_coverage_endpoints
from nca_core import NeuralCellularAutomaton, init_state, target_conditioned_state
from target_patterns import create_target
from topology import get_binary_mask

CHECKPOINT_GLOB = "WP4_*"
CKPT_FILE = "nca_final.pt"
_DIR_RE = re.compile(r"^WP4_(?P<arm>.+?)_s(?P<steps>\d+)_seed(?P<seed>\d+)$")
# Зазор над потолком бесструктурного предсказателя — тот же, что в gate_layer1 и
# wp4_threshold_probe: потолок 2p/(1+p) достигается точно, поэтому без зазора
# «всё яркое» засчитывалось бы как структура.
CEILING_GAP = 0.05
# Точка, по которой принимается решение, разная для двух прогонов, и это не тонкость
# оформления:
#   reach — старт это шум, поэтому кольцу «бывать» где-то на траектории достаточно,
#     и берётся МАКСИМУМ;
#   hold  — старт это ОНО И ЕСТЬ кольцо (target_conditioned_state), поэтому argmax
#     по такой траектории равен 1.0 по построению и мерит начальное состояние, а не
#     динамику. Это ровно ловушка NEG-21, пойманная на первом же запуске зонда:
#     первая версия выдавала «удерживается у всех», потому что решала по максимуму.
#     Для hold берётся ПОСЛЕДНЯЯ точка.
DECISION_POINT = {"reach": "best", "hold": "last"}


def _decision_point(probe_name, rows):
    """Точка траектории, по которой принимается решение по этому прогону."""
    if not rows:
        return None
    if DECISION_POINT.get(probe_name) == "last":
        return rows[-1]
    return max(rows, key=lambda r: r["f1_gated_best"])


def _overrides_by_key():
    """overrides плечей из артифакта аблаций: по ним восстанавливается, была ли
    alive-маска включена на момент последнего шага обучения. Брать их из
    чекпоинта нельзя — метаданные §13.5 состояния модели этот флаг не хранят."""
    path = os.path.join("experiments", "E02_pattern", "wp4_ablations.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for run in data.get("runs", []):
        out[(str(run.get("arm")), int(run.get("steps", 0)), int(run.get("seed", 0)))] = (
            run.get("overrides") or {}
        )
    return out


def _alive_mask_enabled(overrides, steps, fallback):
    """Маска включается с ALIVE_WARMUP_ITERS (train.py), поэтому на финальном
    шаге прогона она выключена ровно тогда, когда warmup больше горизонта.
    Без этого зонд прогонял бы mask-off плечи (H-K1/H-K2/H-N1/H-M2) по правилам
    mask-on динамики и мерил бы не ту модель."""
    if not overrides:
        return bool(fallback)
    warmup = int(overrides.get("ALIVE_WARMUP_ITERS", config.ALIVE_WARMUP_ITERS))
    return bool(warmup <= int(steps))


def _load_model(path, device, seed):
    generator = config.create_deterministic_generator(seed)
    model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
    model.set_generator(generator)
    ck = torch.load(path, map_location=device, weights_only=False)
    config.assert_checkpoint_compatible(ck, allow_missing_metadata=True, context=f"reach_probe({path})")
    model.load_state_dict(ck["model_state_dict"])
    model.eval()
    return model, ck


def _measure(state, target_np):
    """Одна точка развёртки: f1 по единому правилу бинаризации (§2.3:
    sigmoid(alpha)>ALIVE_THRESHOLD И sigmoid(visible)>BINARY_THRESHOLD, уже
    внутри get_binary_mask) и лучший f1 по скану порогов с условием живости.

    Precision/recall/pred_fraction лучшей точки пишутся рядом с f1 намеренно:
    gated_best — это максимум по 60 квантильным порогам И по точкам траектории,
    поэтому число само по себе оптимистично смещено. Отличить структуру от
    «поле чуть ярче» по одному f1 нельзя: у бесструктурного поля pred_fraction
    совпадает с плотностью цели, а у частичной структуры — нет."""
    with torch.no_grad():
        mask = get_binary_mask(state)
        soft = torch.sigmoid(state[0, config.VISIBLE_CHANNEL]).detach().cpu().numpy()
        alive0 = (
            torch.sigmoid(state[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
        ).detach().cpu().numpy()
        alive_fraction = float(
            (torch.sigmoid(state[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD)
            .float()
            .mean()
            .item()
        )
    f1_default = float(compute_coverage_endpoints(mask, target_np)["f1"])
    scan = best_threshold_coverage(np.where(alive0, soft, 0.0), target_np)
    best = scan["best"]
    return {
        "f1_default": f1_default,
        "f1_gated_best": float(best["f1"]),
        "f1_gated_threshold": float(best["threshold"]),
        "gated_recall": float(best["recall"]),
        "gated_precision": float(best["precision"]),
        "gated_pred_fraction": float(best["pred_fraction"]),
        "n_gated_thresholds": int(len(scan["curve"])),
        "alive_fraction": alive_fraction,
    }


def _rollout(model, state, steps, target_np, every):
    """Пошаговая развёртка без градиента. Шаги пишутся каждые `every`, но
    максимум берётся по всем записанным точкам — NEG-21 требует видеть, ГДЕ
    достигнут оптимум, а не только сколько."""
    rows = []
    for i in range(1, steps + 1):
        with torch.no_grad():
            state = model(state)
        if i % every == 0 or i == steps:
            point = _measure(state, target_np)
            point["step"] = i
            rows.append(point)
    return rows, state


def probe(checkpoints, rollout_steps, every, device):
    overrides = _overrides_by_key()
    target = create_target(device=device)
    target_np = (target[0, 0].detach().cpu().numpy() > 0.5).astype("uint8")
    target_density = float(target_np.mean())
    ceiling = 2.0 * target_density / (1.0 + target_density)
    out = []
    for path, arm, steps_trained, seed in checkpoints:
        model, _ck = _load_model(path, device, seed)
        ov = overrides.get((arm, steps_trained, seed), {})
        mask_on = _alive_mask_enabled(ov, steps_trained, config.ALIVE_WARMUP_ITERS <= steps_trained)
        model.alive_mask_enabled = mask_on
        for probe_name in ("reach", "hold"):
            gen = config.create_deterministic_generator(seed)
            if probe_name == "reach":
                start = init_state(
                    batch_size=1,
                    channels=config.N_CHANNELS,
                    grid_size=config.GRID_SIZE,
                    device=device,
                    generator=gen,
                )
            else:
                start = target_conditioned_state(target, batch_size=1, device=device)
            first = _measure(start, target_np)
            rows, _final = _rollout(model, start, rollout_steps, target_np, every)
            decision = _decision_point(probe_name, rows)
            best = max(rows, key=lambda r: r["f1_gated_best"]) if rows else None
            last = rows[-1] if rows else None
            out.append(
                {
                    "arm": arm,
                    "steps_trained": steps_trained,
                    "seed": seed,
                    "probe": probe_name,
                    "checkpoint": path.replace(os.sep, "/"),
                    "alive_mask_enabled": bool(mask_on),
                    "overrides_source": "wp4_ablations.json" if ov else "нет записи (взят конфиг)",
                    "rollout_steps": int(rollout_steps),
                    "decision_point": DECISION_POINT[probe_name],
                    "first": first,
                    "best": best,
                    "last": last,
                    "decision": decision,
                    "alive_fraction_min": min((r["alive_fraction"] for r in rows), default=None),
                    "structureless_f1_ceiling": ceiling,
                    "beyond_ceiling": bool(
                        decision and decision["f1_gated_best"] > ceiling + CEILING_GAP
                    ),
                    "trajectory": rows,
                }
            )
            print(
                f"[reach] {arm:5s} s{steps_trained:<5d} seed={seed} {probe_name:5s} "
                f"mask={int(mask_on)} | старт f1@0.5={first['f1_default']:.4f} "
                f"| лучший gated={best['f1_gated_best']:.4f}@{best['step']} "
                f"| конец gated={last['f1_gated_best']:.4f} f1@0.5={last['f1_default']:.4f} "
                f"| af_min={out[-1]['alive_fraction_min']:.3f} "
                f"| решение по {DECISION_POINT[probe_name]}="
                f"{decision['f1_gated_best']:.4f} "
                f"(P={decision['gated_precision']:.2f} pred={decision['gated_pred_fraction']:.3f}) "
                f"выше потолка={out[-1]['beyond_ceiling']}"
            )
        model.train()
    return out, ceiling


def _find_checkpoints(arms_filter, require_current_seed, ckpt_file):
    out = []
    for directory in sorted(glob.glob(os.path.join(config.CHECKPOINT_DIR, CHECKPOINT_GLOB))):
        m = _DIR_RE.match(os.path.basename(directory))
        if not m:
            continue
        arm, steps, seed = m.group("arm"), int(m.group("steps")), int(m.group("seed"))
        if arms_filter and arm not in arms_filter:
            continue
        if require_current_seed and seed != require_current_seed:
            continue
        path = os.path.join(directory, ckpt_file)
        if os.path.exists(path):
            out.append((path, arm, steps, seed))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--steps", type=int, default=int(config.RETENTION_GATE_STEPS),
                    help="длина автономной развёртки (по умолчанию RETENTION_GATE_STEPS)")
    ap.add_argument("--every", type=int, default=10, help="как часто писать точку траектории")
    ap.add_argument("--arms", default="", help="фильтр плечей через запятую (по умолчанию все WP4_*)")
    ap.add_argument(
        "--seed",
        type=int,
        default=42,
        help="сид чекпоинта (по умолчанию 42: единственный сид, пройденный всеми "
        "плечями; --all-seeds снимает фильтр)",
    )
    ap.add_argument("--all-seeds", action="store_true", help="не фильтровать по сидам")
    ap.add_argument("--ckpt", default=CKPT_FILE, help="имя файла весов внутри папки прогона")
    ap.add_argument("--out", default=os.path.join("experiments", "E02_pattern", "wp4_reach_probe.json"))
    args = ap.parse_args()

    device = torch.device(config.DEVICE)
    config.set_seed(42)
    arms_filter = [a.strip() for a in args.arms.split(",") if a.strip()]
    # По умолчанию зонд идёт по сидам уже записанных прогонов (42), потому что
    # sweep'ы добавляют сиды, а с ними и чекпоинты — без фильтра один запуск
    # начал бы мерить все, что есть, и смешал бы горизонты.
    require_seed = None if args.all_seeds else args.seed
    checkpoints = _find_checkpoints(arms_filter, require_seed, args.ckpt)
    if not checkpoints:
        raise SystemExit("[reach] нет чекпоинтов под фильтр — нечего мерить")
    print(
        f"[reach] чекпоинтов={len(checkpoints)} развёртка={args.steps} каждые={args.every} "
        f"устройство={device} маска по умолчанию warmup={config.ALIVE_WARMUP_ITERS}"
    )
    rows, ceiling = probe(checkpoints, int(args.steps), int(args.every), device)

    verdict = {
        "ceiling": ceiling,
        "gap": CEILING_GAP,
        "threshold": ceiling + CEILING_GAP,
        "reachable_arms": sorted({r["arm"] for r in rows if r["probe"] == "reach" and r["beyond_ceiling"]}),
        "holdable_arms": sorted({r["arm"] for r in rows if r["probe"] == "hold" and r["beyond_ceiling"]}),
        "note": (
            "reach = кольцо достигается из шума (решение по МАКСИМУМУ траектории); "
            "hold = кольцо ещё есть через N шагов, если его туда поставить (решение "
            "по ПОСЛЕДНЕЙ точке: argmax у hold равен 1.0 по построению, потому что "
            "старт и есть цель, и решать по нему — то же, что измерять начальное "
            "состояние модели, см. NEG-21). Пустой reach при непустом hold — "
            "неподвижная точка, а не морфогенез (§14.2)."
        ),
    }
    payload = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "experiment": "E02_pattern (WP4b: достижимость формы против удержания)",
        "rollout_steps": int(args.steps),
        # Зонд — чистый инференс, но числа траекторий зависят от устройства
        # (плавающая точка), поэтому оно записывается, а не подразумевается.
        "device": str(device),
        "verdict": verdict,
        "runs": rows,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"[reach] записано: {args.out}")
    print(
        f"[reach] порог {verdict['threshold']:.4f} (потолок {ceiling:.4f} + {CEILING_GAP}) | "
        f"достижимо у: {verdict['reachable_arms'] or 'ни у кого'} | "
        f"удерживается у: {verdict['holdable_arms'] or 'ни у кого'}"
    )
    return payload


if __name__ == "__main__":
    main()
