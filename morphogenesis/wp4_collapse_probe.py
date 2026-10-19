"""
wp4_collapse_probe.py — дискриминатор H-A из WP4: является ли «полная смерть
ткани» оптимумом реализованной целевой функции, или только плато, в которое
оптимизатор скатывается?

Смысл проверки. Обучение E02 на всех сидах даёт один и тот же финал:
visible_mse -> 0.2499, alive_policy -> 0.2501, alive_fraction -> 0.0014.
Числа 0.25 — это не совпадение: при мёртвой клетке AliveSTE обнуляет ВСЁ
состояние, значит канал 0 = 0 и sigmoid(0) = 0.5, а MSE константы 0.5 по
бинарной цели равен ровно 0.25 независимо от плотности цели. То есть
«все клетки мертвы» — это кандидат №1, и его надо сравнить с кандидатом
«ткань живая и цель собрана» по КАЖДОМУ члену лосса, а не по одному
наблюдению за траекторией.

Скрипт ничего не обучает: он строит шесть рукотворных состояний и прогоняет
их через существующий compute_loss() (§12.6.3) — на свежих весах модели и на
чекпоинтах сколлапсировавших гейтных прогонов. Если лосс смерти ниже лосса
собранной цели, то H-A подтверждается как ДЕФЕКТ ЦЕЛИ, а не гиперпараметра,
и лечение (ALPHA_SUPERVISION_WEIGHT, LR) ничего не даст.

Запуск:  python wp4_collapse_probe.py [--seeds 42,101]
"""

import argparse

import glob

import json

import os

# §9.2: config раньше torch.

import config

import torch


def _make_state(
    batch,
    target_bin,
    *,
    alpha_value=0.0,
    alpha_from_target=False,
    visible_value=None,
    visible_from_target=None,
):
    """
    Состояние (B, C, H, W) с нулевыми скрытыми каналами.

    alpha_value / visible_value        — константы каналов;
    alpha_from_target / visible_from_target — канал = s·(2·цель − 1), т.е.
        «уверенно» рисует цель (sigmoid(±s) ≈ 1 / 0);
    Всё остальное время жизни клетки держим в нуле: именно так выглядит
    состояние после AliveSTE, а не «произвольный шум в мёртвых клетках».
    """
    device = config.DEVICE
    size = config.GRID_SIZE
    state = torch.zeros(
        batch,
        config.N_CHANNELS,
        size,
        size,
        device=device,
        dtype=torch.float32,
    )
    t = target_bin.expand(batch, -1, -1, -1)
    if visible_from_target is not None:
        state[:, config.VISIBLE_CHANNEL : config.VISIBLE_CHANNEL + 1] = visible_from_target * (2.0 * t - 1.0)
    elif visible_value is not None:
        state[:, config.VISIBLE_CHANNEL] = visible_value
    if alpha_from_target is not False:
        state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1] = alpha_from_target * (2.0 * t - 1.0)
    else:
        state[:, config.ALIVE_CHANNEL] = alpha_value
    return state


def candidates(target, batch):
    """Кандидаты для сравнения: от полной смерти до собранной цели."""
    target_bin = (target > 0).float()
    return {
        # AliveSTE обнуляет мёртвую клетку целиком, поэтому «смерть» — это
        # буквально нулевое состояние: канал 0 = 0 -> sigmoid = 0.5.
        "dead_zero_state": _make_state(batch, target_bin),
        # То же самое, но alpha заведомо глубоко отрицателен (клетка мертва
        # и по «сырому» предикату, и по sigmoid). Недостижимо после AliveSTE,
        # нужно только чтобы проверить чувствительность alive_policy.
        "dead_alpha_minus5": _make_state(batch, target_bin, alpha_value=-5.0),
        # Живая, но ещё не собравшаяся ткань: все клетки живые, видимый канал
        # нейтрален (серое поле 0.5) — это и есть состояние «после сброса пула».
        "alive_blank_grey": _make_state(batch, target_bin, alpha_value=5.0),
        # Живая ткань, которая рисует «всё чёрное»: полный фон, никакой цели.
        "alive_blank_black": _make_state(batch, target_bin, alpha_value=5.0, visible_value=-5.0),
        # Цель собрана, живёт вся ткань (фон тоже жив, но не виден).
        "ring_alive_everywhere": _make_state(
            batch, target_bin, alpha_value=5.0, visible_from_target=5.0
        ),
        # Цель собрана, жива только сама цель — «асцит» по живости.
        "ring_alive_only_in_target": _make_state(
            batch, target_bin, alpha_from_target=5.0, visible_from_target=5.0
        ),
    }


def evaluate(cands, model, target, topo_proxy):
    from train import compute_loss, alive_fraction_of

    rows = {}
    with torch.no_grad():
        for name, state in cands.items():
            _, parts = compute_loss(state, target, model, phase=1, topo_proxy=topo_proxy, iteration=0)
            parts = dict(parts)
            parts["alive_fraction_measured"] = alive_fraction_of(state)
            rows[name] = parts
    return rows


def gradient_direction(model, target, state, target_bin):
    """
    Куда лосс толкает alpha-канал ИЗ НАЧАЛА обучения.

    Это и есть настоящий дискриминатор H-A: глобальный оптимум может быть и
    живым, но если градиент на старте массово уменьшает alpha, ткань уходит в
    поглощающее множество (мёртвая клетка обнуляется AliveSTE, и выйти из него
    можно только через суррогатный градиент с пола ALIVE_SURROGATE_GRAD_FLOOR).

    Возвращает среднее −∂L/∂alpha по клеткам внутри цели, снаружи и по всем.
    Отрицательное значение = лосс толкает к смерти.
    """
    from train import compute_loss

    state = state.detach().clone().requires_grad_(True)
    with torch.enable_grad():
        loss, _ = compute_loss(state, target, model, phase=1, topo_proxy=None, iteration=0)
        (grad,) = torch.autograd.grad(loss, state)
    d_alpha = -grad[:, config.ALIVE_CHANNEL]  # направление спуска
    inside = target_bin[0, 0] > 0
    return {
        "descent_dalpha_inside_target": float(d_alpha[:, inside].mean().item()),
        "descent_dalpha_outside_target": float(d_alpha[:, ~inside].mean().item()),
        "descent_dalpha_all": float(d_alpha.mean().item()),
        "frac_cells_pushed_to_death": float((d_alpha < 0).float().mean().item()),
    }


def probe_mode(mode, seeds, target, cands, batch):
    """
    Полный прогон педали для ОДНОЙ формулы alive_policy.

    Режим переключается прямо в config, потому что compute_loss читает его на
    каждом вызове: так один и тот же набор кандидатов и весов сравнивает
    формулы без расхождения в чём-либо ещё.
    """
    from nca_core import NeuralCellularAutomaton, init_state, run_steps
    from train import make_topo_proxy

    config.ALIVE_POLICY_MODE = mode
    reports = {}

    def proxy_for():
        # make_topo_proxy возвращает (proxy, grad_test_report): отчёт нужен,
        # чтобы засвидетельствовать, что прокси в пробе живой.
        proxy, report = make_topo_proxy(target, "WP4_PROBE")
        reports["grad_test"] = report
        return proxy

    arms = {}
    fresh = NeuralCellularAutomaton().to(config.DEVICE)
    fresh.eval()
    arms["fresh_model"] = evaluate(cands, fresh, target, proxy_for())
    last_trained = fresh
    # Какие веса реально использованы для атрибуции — это надо писать, а не
    # подразумевать: у свежей модели delta тождественно 0 (§12.2.2), и
    # атрибутировалась бы как «градиента нет», чего на самом деле нет.
    last_trained_source = "fresh_model(delta=0)"

    # Имена чекпоинтов менялись вместе с гейтом (gate_layer1_seed{S} ->
    # gate_layer1_s{STEPS}_seed{S}) и с аблациями (WP4_{ARM}_s{STEPS}_seed{S}),
    # поэтому ищем глобально, а не по одному шаблону.
    ckpt_candidates = []
    for pattern in ("gate_layer1*seed*", "WP4_*_seed*"):
        ckpt_candidates += sorted(glob.glob(os.path.join(config.CHECKPOINT_DIR, pattern)))
    # --seeds выбирает, какие именно прогоны брать как «натренированные веса»:
    # имя каталога обязано содержать seed{S}.
    ckpt_candidates = [d for d in ckpt_candidates if any(f"seed{s}" in os.path.basename(d) for s in seeds)]
    for run_dir in ckpt_candidates:
        path = os.path.join(run_dir, "nca_final.pt")
        if not os.path.exists(path):
            continue
        payload = torch.load(path, map_location=config.DEVICE, weights_only=False)
        model = NeuralCellularAutomaton().to(config.DEVICE)
        model.load_state_dict(payload["model_state_dict"])
        model.eval()
        name = os.path.basename(run_dir)
        arms[f"trained_{name}"] = evaluate(cands, model, target, proxy_for())
        last_trained = model
        last_trained_source = path

    # --- градиентное направление: отдельный прогон без topo-члена, чтобы
    #     вывод не зависел от stride прокси (iteration=0 его включает, поэтому
    #     topo_proxy=None — чисто MSE+alive+L1+stress).
    gen = config.create_deterministic_generator(42)
    pool_state = init_state(batch_size=batch, device=config.DEVICE, generator=gen)
    t_bin = (target > 0).float()
    probe_model = NeuralCellularAutomaton().to(config.DEVICE)
    probe_model.eval()
    with torch.no_grad():
        rolled = run_steps(probe_model, pool_state, 16)
    dirs = {}
    for label, st in {
        "pool_init": pool_state,
        "after_rollout16": rolled,
        "alive_blank_grey": cands["alive_blank_grey"],
        "dead_zero_state": cands["dead_zero_state"],
    }.items():
        m = NeuralCellularAutomaton().to(config.DEVICE)
        m.eval()
        dirs[label] = gradient_direction(m, target, st, t_bin)
        dirs[label]["alive_fraction_start"] = float(
            (torch.sigmoid(st[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean().item()
        )

    # Атрибуция по членам: на живом сером поле (все клетки живы, паттерна нет)
    # и на мёртвом нулевом (куда прогон уже свалился). Взять именно
    # натренированные в коллапсе веса, а не свежие: у свежей модели последний
    # слой занулён (§12.2.2), delta тождественно 0 и градиента в alpha нет
    # вовсе — атрибутировать было бы нечего.
    attribution = {
        "weights": last_trained_source,
        "alive_blank_grey": term_attribution(last_trained, target, cands["alive_blank_grey"]),
        "dead_zero_state": term_attribution(last_trained, target, cands["dead_zero_state"]),
    }

    verdicts = {}
    for arm, rows in arms.items():
        dead = rows["dead_zero_state"]["total"]
        built = rows["ring_alive_only_in_target"]["total"]
        alive_everywhere = rows["ring_alive_everywhere"]["total"]
        verdicts[arm] = {
            "loss_dead": dead,
            "loss_ring_built": built,
            "loss_ring_alive_everywhere": alive_everywhere,
            # ЛУЧШИЙ из «живых» состояний, до которых можно договориться за
            # один однородный шаг (серо-чёрное поле или собранная цель при
            # всеобщей живости). Если даже оно дороже смерти, спуск из
            # случайного состояния обязан идти через смерть — это и есть ловушка.
            "best_alive_total": min(alive_everywhere, rows["alive_blank_black"]["total"]),
            "death_is_optimum_of_implemented_loss": bool(dead <= built),
            "death_beats_best_alive_state": bool(dead <= min(alive_everywhere, rows["alive_blank_black"]["total"])),
        }
    return {"arms": arms, "gradient_direction": dirs, "verdict": verdicts, "topo_grad_test": reports.get("grad_test"), "term_attribution": attribution}


def term_attribution(model, target, state):
    """
    Кто именно толкает ткань в смерть: −∂(взвешенный член)/∂alpha по каждой
    клетке, усреднённая по фону и по области цели.

    Нужно, потому что ALPHA_SUPERVISION_WEIGHT=0 (дискриминант H-A1) коллапс
    НЕ снял: значит смерть вызывает не только supervised-давление, и полагаться
    на «уберём alive_policy» было бы гаданием. Атрибуция считается через
    return_terms у того же compute_loss, что и обучение, — иначе прогон
    сравнивал бы пересобранную вручную сумму с настоящей.
    """
    from train import compute_loss

    inside = (target > 0)[0, 0]
    out = {}
    for name in ("visible_mse", "alive_policy", "hidden_regularization", "stress_proxy", "topo_proxy"):
        state_grad = state.detach().clone().requires_grad_(True)
        with torch.enable_grad():
            _, _, weighted = compute_loss(
                state_grad,
                target,
                model,
                phase=1,
                topo_proxy=None,
                iteration=0,
                return_terms=True,
            )
            term = weighted.get(name)
            if term is None:
                out[name] = {"note": "член не участвует в этой фазе"}
                continue
            if float(term.detach().item()) == 0.0:
                out[name] = {"descent_dalpha_outside_target": 0.0, "descent_dalpha_inside_target": 0.0,
                             "killed": False, "note": "обнулён весом"}
                continue
            (grad,) = torch.autograd.grad(term, state_grad, retain_graph=True, allow_unused=True)
        if grad is None:
            out[name] = {"descent_dalpha_outside_target": 0.0, "descent_dalpha_inside_target": 0.0,
                         "killed": False, "note": "градиента в alpha нет"}
            continue
        d_alpha = -grad[:, config.ALIVE_CHANNEL]
        row = {
            "term_value": float(term.detach().item()),
            "descent_dalpha_outside_target": float(d_alpha[:, ~inside].mean().item()),
            "descent_dalpha_inside_target": float(d_alpha[:, inside].mean().item()),
            # Клетка «убита» этим членом, если направление спуска по alpha
            # отрицательнее шага LR: тогда за один шаг оптимизатор опускает
            # alpha ниже порога живости.
            "killed": bool(float(d_alpha.mean().item()) < 0.0),
        }
        out[name] = row
    return out


def main(seeds, modes):
    from target_patterns import create_target

    target = create_target(device=config.DEVICE)
    batch = 4
    cands = candidates(target, batch)

    key_order = [
        "total",
        "visible_mse",
        "alive_policy",
        "hidden_reg",
        "stress_proxy",
        "topo_proxy",
        "alive_fraction",
    ]

    results = {}
    original_mode = config.ALIVE_POLICY_MODE
    for mode in modes:
        results[mode] = probe_mode(mode, seeds, target, cands, batch)
        print(f"\n===== ALIVE_POLICY_MODE = {mode} =====")
        print(f"{'кандидат':28s} " + " ".join(f"{k:>15s}" for k in key_order))
        for arm, rows in results[mode]["arms"].items():
            print(f"— {arm}")
            for name, parts in rows.items():
                print(f"  {name:26s} " + " ".join(f"{parts[k]:15.4f}" for k in key_order))
        print(json.dumps(results[mode]["gradient_direction"], ensure_ascii=False, indent=2))
        print(json.dumps(results[mode]["term_attribution"], ensure_ascii=False, indent=2))
        print(json.dumps(results[mode]["verdict"], ensure_ascii=False, indent=2))
    config.ALIVE_POLICY_MODE = original_mode

    out = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "target_pattern": config.TARGET_PATTERN,
        "target_density": float((target > 0).float().mean().item()),
        "loss_weights": dict(config.LOSS_WEIGHTS),
        "alpha_supervision_weight": float(config.ALPHA_SUPERVISION_WEIGHT),
        "collapse_alive_fraction_min": float(config.COLLAPSE_ALIVE_FRACTION_MIN),
        # Сравнение формул — суть WP4: одна и та же цель, те же веса, разные
        # alive_policy. Разница в вердиктах и есть измерение гипотезы H-A.
        "modes": results,
    }

    out_dir = os.path.join("experiments", "E02_pattern")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "collapse_probe.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"[probe] записано: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=str, default="42,101,202,303")
    parser.add_argument("--modes", type=str, default=",".join(config.ALIVE_POLICY_MODES))
    args = parser.parse_args()
    main(
        seeds=[int(s) for s in args.seeds.split(",")],
        modes=[m.strip() for m in args.modes.split(",") if m.strip()],
    )
