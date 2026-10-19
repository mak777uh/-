"""
wp4_threshold_probe.py — есть ли выученная структура ПОД порогом бинаризации (WP4).

Зачем. Штатный эндпоинт E02 бинаризует поле порогом (§5.1 ALIVE_THRESHOLD=0.5 и
BINARY_THRESHOLD), поэтому он слеп к «выучила форму, но бледно». Замеры волны 5
 это показывают: в H-N1 (маска выключена, alive_policy=0, L1=0) visible_mse упал
до 0.106-0.112, то есть НИЖЕ аналитического пола лучшего константного
предсказателя p(1-p) = 0.12914, — а coverage.f1 при этом 0.000. Либо структура
есть и не дотягивает до порога, либо MSE улучшается за счёт чего-то, что с
целью не согласовано. Скрипт отвечает на это прямо, перебирая пороги.

Что считается (по чекпоинтам указанных прогонов, sample 0):

  state_at_load   — состояние, сохранённое в чекпоинте (до последнего unroll'а);
  state_after_200 — тот же state, прогнанный 200 шагов автономно (§14.2 требует
                    устойчивости формы 200+ шагов), то есть без teacher forcing.

Для каждого — f1 при пороге 0.5, лучший f1 по скану порогов и сам скан.

Скан делается в двух вариантах: по мягкому полю как оно есть и по полю с
фиксированным условием живости (мёртвые клетки всегда «тёмные»). Второй вариант
и есть честный, потому что по §5.7-5.8 мёртвая клетка обнуляется целиком, её
видимый канал = 0 и sigmoid(0) = 0.5 — при любом пороге < 0.5 все мёртвые клетки
ложно считаются яркими. Вердикт `structure_beyond_ceiling` ставится по gated
версии (ср. со штатным эндпоинтом topology.get_binary_mask = alive AND visible>t).

H-P1 (пул стартует из цели, f1@0.5 = 1.0) добавлен как ПОЛОЖИТЕЛЬНЫЙ контроль:
если скан на заведомо выученном поле не даёт лучший f1 выше 1.0, значит сам
инструмент сломан, а не вывод про H-N1.

Запуск:  python wp4_threshold_probe.py [--experiments WP4_H-N1_s2000_seed42,...]
Результат: experiments/E02_pattern/threshold_probe.json
"""

import argparse

import glob

import json

import os

# §9.2: config раньше torch.

import config

import numpy as np

import torch

from evaluate import best_threshold_coverage, compute_coverage_endpoints
from nca_core import NeuralCellularAutomaton, run_steps
from target_patterns import create_target


def _checkpoint_files(exp_dir):
    """Все чекпоинты прогона, от старых к новому (nca_final.pt — самый свежий)."""
    iters = []
    for path in glob.glob(os.path.join(exp_dir, "nca_iter_*.pt")):
        name = os.path.basename(path)
        try:
            iters.append((int(name[len("nca_iter_") : -len(".pt")]), path))
        except ValueError:
            continue
    iters.sort()
    files = [p for _, p in iters]
    for name in ("nca_best.pt", "nca_final.pt"):
        path = os.path.join(exp_dir, name)
        if os.path.exists(path):
            files.append(path)
    return files


def _pool_init_mode_from_log(experiment_id):
    """Как пул инициализировался в этом прогоне (шум vs цель) — из run_start.

    Нужно, чтобы положительный контроль ёмкости (H-P1, пул из цели) не
    попадал в один список с прогонами «рост из шума»: у него лучший f1 обязан
    быть 1.0, и если это не так — сломан инструмент, а не вывод про H-N1.
    """
    path = os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("event") == "run_start" and entry.get("experiment_id") == experiment_id:
                return entry.get("pool_init_mode")
    return None


def _scan_field(soft, alive0, target_np, model, state, device, rollout_steps):
    """Скан порогов на сохранённом состоянии и на автономном продолжении.

    Два варианта каждой точки. Без условия живости (`saved_state`) — как умело
    скантер WP4 до проверки этого артефакта. И с фиксированным Alive-условием
    (`*_alive_gated`) — честный вариант: по §5.2/§5.8 мёртвая клетка обнуляется
    ЦЕЛИКОМ, значит её видимый канал = 0 и sigmoid(0) = 0.5, то есть при любом
    пороге < 0.5 все мёртвые клетки ложно попадают в предсказание и топят
    precision. Именно так устроен штатный эндпоинт (topology.get_binary_mask =
    alive AND visible > t), поэтому вывод о наличии структуры делаем по gated
    версии, а ungated оставляем в артифакте для сопоставления.
    """
    gated = np.where(alive0, soft, 0.0)
    out = {
        "saved_state": best_threshold_coverage(soft, target_np),
        "saved_state_alive_gated": best_threshold_coverage(gated, target_np),
        "saved_state_coverage_at_default": compute_coverage_endpoints(soft > 0.5, target_np),
        "saved_state_coverage_at_default_gated": compute_coverage_endpoints(gated > 0.5, target_np),
    }
    if rollout_steps <= 0:
        return out, None
    with torch.no_grad():
        grown = run_steps(model, state, steps=rollout_steps)
    grown_soft = torch.sigmoid(grown[0, config.VISIBLE_CHANNEL]).detach().cpu().numpy()
    grown_alive = (
        torch.sigmoid(grown[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
    ).detach().cpu().numpy()
    grown_gated = np.where(grown_alive, grown_soft, 0.0)
    out["after_autonomous_steps"] = {
        "steps": int(rollout_steps),
        "scan": best_threshold_coverage(grown_soft, target_np),
        "coverage_at_default": compute_coverage_endpoints(grown_soft > 0.5, target_np),
        "alive_fraction": float(
            (torch.sigmoid(grown[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean()
        ),
    }
    out["after_autonomous_steps_alive_gated"] = {
        "steps": int(rollout_steps),
        "scan": best_threshold_coverage(grown_gated, target_np),
        "coverage_at_default": compute_coverage_endpoints(grown_gated > 0.5, target_np),
        "alive_fraction": float(
            (torch.sigmoid(grown[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean()
        ),
    }
    return out, grown


def probe_experiment(experiment_id, target_np, rollout_steps=200, device="cpu"):
    exp_dir = os.path.join(config.CHECKPOINT_DIR, experiment_id)
    files = _checkpoint_files(exp_dir)
    if not files:
        print(f"[probe] {experiment_id}: чекпоинтов нет в {exp_dir} — пропуск")
        return None
    path = files[-1]
    ckpt = torch.load(path, map_location=device, weights_only=False)
    config.assert_checkpoint_compatible(ckpt, context=f"wp4_threshold_probe:{experiment_id}")
    state = ckpt["state"].to(device)
    model = NeuralCellularAutomaton(channels=state.shape[1]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    soft = torch.sigmoid(state[0, config.VISIBLE_CHANNEL]).detach().cpu().numpy()
    alive0 = (
        torch.sigmoid(state[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
    ).detach().cpu().numpy()
    alive = float(
        (torch.sigmoid(state[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean()
    )
    scan, _ = _scan_field(soft, alive0, target_np, model, state, device, rollout_steps)
    record = {
        "experiment_id": experiment_id,
        "checkpoint": os.path.relpath(path, config.CHECKPOINT_DIR),
        "checkpoint_iteration": ckpt.get("iteration"),
        "checkpoint_loss": ckpt.get("loss"),
        "pool_init_mode_in_log": _pool_init_mode_from_log(experiment_id),
        "alive_fraction_at_checkpoint": alive,
        "visible_mse_at_checkpoint": float(
            np.mean((soft - target_np) ** 2)
        ),
        "threshold_scan": scan,
    }
    best_saved = scan["saved_state"]["best"]
    best_gated = scan["saved_state_alive_gated"]["best"]
    print(
        f"[probe] {experiment_id}: f1@0.5={scan['saved_state']['f1_at_default_threshold']:.4f} "
        f"лучший f1={best_saved['f1']:.4f} при пороге {best_saved['threshold']:.4f} "
        f"(доля клеток {best_saved['pred_fraction']:.4f}) | "
        f"с условием живости: лучший={best_gated['f1']:.4f} @ {best_gated['threshold']:.4f} "
        f"(R={best_gated['recall']:.3f} P={best_gated['precision']:.3f} "
        f"доля={best_gated['pred_fraction']:.4f})"
    )
    best_grown = (scan.get("after_autonomous_steps") or {}).get("scan", {}).get("best")
    best_grown_gated = (
        (scan.get("after_autonomous_steps_alive_gated") or {}).get("scan", {}).get("best")
    )
    if best_grown is not None:
        print(
            f"[probe]   после {rollout_steps} автономных шагов: "
            f"f1@0.5={scan['after_autonomous_steps']['scan']['f1_at_default_threshold']:.4f} "
            f"лучший={best_grown['f1']:.4f} @ {best_grown['threshold']:.4f} | "
            f"с живостью={best_grown_gated['f1']:.4f} @ {best_grown_gated['threshold']:.4f}"
        )
    return record


def _best_f1_points(rec, gated_only=False):
    """Лучшие точки скана: сохранённое поле и автономное продолжение.

    gated_only=True — только варианты с фиксированным Alive-условием; именно по
    ним выносится вердикт о наличии структуры (см. докстринг _scan_field).
    """
    ts = rec["threshold_scan"]
    keys = (
        ("saved_state_alive_gated", "after_autonomous_steps_alive_gated")
        if gated_only
        else ("saved_state", "after_autonomous_steps")
    )
    points = []
    for key in keys:
        block = ts.get(key) or {}
        best = (block.get("scan") or {}).get("best") or block.get("best")
        if best:
            points.append((key, best))
    return points


def main(experiments, rollout_steps, device=None):
    device = device or "cpu"
    os.makedirs("experiments/E02_pattern", exist_ok=True)
    target = create_target(device="cpu")
    target_np = (target[0, 0] > 0.5).numpy().astype("uint8")
    density = float(target_np.mean())

    records = []
    for exp in experiments:
        rec = probe_experiment(exp, target_np, rollout_steps=rollout_steps, device=device)
        if rec is not None:
            records.append(rec)

    ceiling = 2 * density / (1 + density)
    for rec in records:
        # Вердикт — по gated-скану: без условия живости мёртвые клетки
        # (sigmoid(0)=0.5 по §5.8) ложно попадают в предсказание.
        best = max((b["f1"] for _, b in _best_f1_points(rec, gated_only=True)), default=0.0)
        best_ungated = max((b["f1"] for _, b in _best_f1_points(rec)), default=0.0)
        # +0.05 — шумовой зазор: потолок бесструктурного «всё яркое» достигается
        # точно (измерено 0.2643-0.2649 при 2p/(1+p)=0.2644), поэтому превышение
        # меньше зазора означает «тот же трюк», а не выученную форму.
        rec["best_f1_any_threshold_gated"] = float(best)
        rec["best_f1_any_threshold"] = float(best_ungated)
        rec["structure_beyond_ceiling"] = bool(best > ceiling + 0.05)
        rec["structure_beyond_ceiling_ungated"] = bool(best_ungated > ceiling + 0.05)

    payload = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "target_pattern": config.TARGET_PATTERN,
        "target_density": density,
        "default_threshold": float(config.ALIVE_THRESHOLD),
        "constant_field_floor": float(density * (1 - density)),
        # Потолок БЕССТРУКТУРНОГО предсказателя: «всё яркое» даёт recall=1 и
        # precision=p, то есть f1 = 2p/(1+p). Скан порогов всегда может вернуть
        # это число, ничего не выучив, поэтому вывод делается так: структура есть
        # только если best.f1 ПРЕВЫШАЕТ этот потолок.
        "structureless_f1_ceiling": float(2 * density / (1 + density)),
        "note": (
            "f1@0.5 = штатный эндпоинт; best = максимум f1 по скану порогов. "
            "Если best заметно больше f1@0.5, структура в поле ЕСТЬ, но её амплитуда "
            "ниже порога бинаризации — это другой диагноз, чем «ничему не научилась». "
            "Вердикт structure_beyond_ceiling считается по gated-скану (мёртвые клетки "
            "не могут считаться яркими, §5.2/§5.8); ungated оставлен для сопоставления."
        ),
        "runs": records,
    }
    path = os.path.join("experiments", "E02_pattern", "threshold_probe.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"[probe] записано: {path}")
    return payload


DEFAULT_EXPERIMENTS = [
    # Положительный контроль: пул из цели, f1@0.5 = 1.0 — скан обязан вернуть 1.0.
    "WP4_H-P1_s400_seed42",
    "WP4_H-N1_s2000_seed42",
    "WP4_H-K1_s400_seed42",
    "WP4_H-K2_s400_seed42",
    "WP4_H-M2_s4000_seed42",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", type=str, default=",".join(DEFAULT_EXPERIMENTS))
    parser.add_argument("--rollout-steps", type=int, default=200)
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="cpu по умолчанию: зонд читает чекпоинты и делает короткий rollout, "
        "GPU оставляем обучению; вывод от устройства не зависит (eval, без стохастики).",
    )
    args = parser.parse_args()
    main(
        experiments=[e for e in args.experiments.split(",") if e],
        rollout_steps=args.rollout_steps,
        device=args.device,
    )
