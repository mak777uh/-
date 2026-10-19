"""
wp4_retention_scale.py — сколько ГРАДИЕНТА даёт retention-член относительно
видимого MSE, и при каком весе survival-штраф становится заметен оптимизатору.

Зачем. Пробный прогон R-1 (WP4b, сид 42, 400 итераций, retention K=8, вес 0.5)
повторил коллапс базлайна: alive_fraction 0.483 -> 0.148 -> 0.068 -> 0.001 к
итерации 200, а значения членов были такие:

    visible_mse   0.2663 ... 0.2498
    retention_mse 0.2651 ... 0.2499
    survival      0.00019 ... 0.00001

survival-член меньше MSE-члена в ~1000 раз, и с весом 0.5 он вносит в total
~5e-5 против 0.25. По одному наблюдению вывод делать нельзя (значение != вклад
в градиент), поэтому здесь измеряется норма градиента по параметрам от каждого
члена.

Второй вопрос, который закрывает скрипт. retention_mse в прогоне почти совпал
с visible_mse (разница <0.01 на всех точках). Если то же самое на умирающих
состояниях, roll-out не добавляет информации о форме, а дублирует уже
существующий сигнал: тогда «удержание как цель» в текущей форме не может
изменить исход коллапса независимо от веса.

Геометрия повтора train(): состояние из пула откреплено, дальше `unroll` шагов
С ГРАДИЕНТОМ (так visible_mse вообще имеет градиент — по откреплённому
состоянию градиента нет, model.visible_image — чистая функция состояния), и уже
из полученного состояния идёт retention roll-out (он сам по себе starts with
detach, см. train.retention_rollout_loss). Поэтому gn(retention) течёт через K
шагов, а gn(visible) — через unroll; сравниваем вклады ровно так, как их
видит оптимизатор на реальном шаге обучения.

Скрипт НЕ обучает: веса свежие (или из чекпоинта), состояния старятся
автономными шагами модели — это и есть §14.2 «удержать» без teacher-forcing.

Третий вопрос (wave 9). После R-8 выживание перестало быть блокером, блокером
стала форма: level-survival держит af≈1.0, а f1 стоит на 0.196 (NEG-20,
«живо всё»). Поэтому здесь же измеряется градиент парного quiet-члена —
налога на живость ВНЕ цели на той же roll-out траектории. Калибр quiet обязан
взят на срезе с ЖИВЫМ фоном (чекпоинт R-8): на мёртвом фоне quiet == 0 по
смыслу, и брать масштаб оттуда означало бы обнулить член.

Запуск:  python wp4_retention_scale.py [--steps 8] [--seeds 42] [--checkpoint PATH]
                                        [--survival-mode level] [--quiet-margin 0.0]
"""

import argparse
import math

# §9.2: config обязан идти раньше torch.
import config

import torch
import torch.nn.functional as F

from nca_core import NeuralCellularAutomaton, init_state, run_steps
from target_patterns import create_target
from train import retention_rollout_loss


def _grad_norm(model, loss):
    """||d(loss)/d(theta)|| по всем параметрам (loss обязан иметь градиент)."""
    model.zero_grad(set_to_none=True)
    loss.backward(retain_graph=True)
    total = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total += float(p.grad.detach().norm().item()) ** 2
    model.zero_grad(set_to_none=True)
    return total**0.5


def _alive_fraction(state):
    with torch.no_grad():
        alpha = torch.sigmoid(state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1])
        return float((alpha > config.ALIVE_THRESHOLD).float().mean().item())


def _snapshot(model, aged_state, target_expanded, unroll, rollout_steps):
    """Один срез: из постаревшего состояния — unroll шагов с градиентом, затем члены лосса."""
    live = run_steps(model, aged_state.detach(), steps=unroll)
    visible = F.mse_loss(model.visible_image(live), target_expanded)
    ret_mse, surv, quiet = retention_rollout_loss(
        model, live, target_expanded, steps=rollout_steps
    )
    return visible, ret_mse, surv, quiet, live


def _blindness_check(model, target_expanded, device):
    """Формы survival и quiet на двух предельных полях: поглощающая смерть и «живо всё».

    Состояние из нулей — это то, к чему AliveSTE приводит мёртвую клетку (§5.2:
    обнуление всего состояния), значит alpha = sigmoid(0) = 0.5 = ALIVE_THRESHOLD.
    Если transition-член на таком состоянии даёт 0 и нулевой градиент, а level —
    margin и ненулевой градиент, то слепота transition измерена, а не предположена,
    и R-4/R-5 обоснованы как исправление формы, а не как ещё один вес.

    second probe — uniformly alive field (alpha = 0.55 везде): там должен молчать
    survival (он про «не умирай»), а говорить quiet (он про «фоном прав нет»).
    Это и есть проверка, что quiet — не дубликат survival, а вторая половина той
    же полосы: без неё R-8 даёт af≈1.0 при f1 0.196 (NEG-20).
    """
    out = {}
    zero_state = torch.zeros(
        config.TRAIN_BATCH_SIZE,
        config.N_CHANNELS,
        config.GRID_SIZE,
        config.GRID_SIZE,
        device=device,
    )
    # Живое поле: alpha = 0.55 при нулевых остальных каналах (клетка живая, но
    # ничего не рисует) — модельный портрет «живо всё» из R-8.
    alive_state = zero_state.clone()
    alive_state[:, config.ALIVE_CHANNEL] = math.log(0.55 / 0.45)
    for label, probe_state in (("поглощающая смерть", zero_state), ("живо всё", alive_state)):
        for mode in config.RETENTION_SURVIVAL_MODES:
            mse, surv, quiet = retention_rollout_loss(
                model, probe_state, target_expanded, steps=1, mode=mode
            )
            key = f"{label}/{mode}"
            out[key] = {
                "state": label,
                "survival_mode": mode,
                "alive_fraction": _alive_fraction(probe_state),
                "retention_mse": float(mse.detach().item()),
                "survival": float(surv.detach().item()),
                "quiet": float(quiet.detach().item()),
                "grad_norm_survival": _grad_norm(model, surv),
                "grad_norm_quiet": _grad_norm(model, quiet),
            }
            print(
                f"[blind] {label:<18} mode={mode:<10} af={out[key]['alive_fraction']:.3f} "
                f"survival={out[key]['survival']:.6f} "
                f"gn(survival)={out[key]['grad_norm_survival']:.6f} "
                f"quiet={out[key]['quiet']:.6f} gn(quiet)={out[key]['grad_norm_quiet']:.6f}"
            )
    return out


def measure(seed, rollout_steps, unroll=16, checkpoint=None, stages=(0, 100, 250, 600)):
    device = torch.device(config.DEVICE)
    torch.manual_seed(seed)
    config.set_seed(seed)
    generator = config.create_deterministic_generator(seed)
    model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
    model.set_generator(generator)
    if checkpoint:
        ck = torch.load(checkpoint, map_location=device, weights_only=False)
        state_dict = ck.get("model_state_dict", ck.get("model"))
        model.load_state_dict(state_dict)
        print(f"[scale] веса из чекпоинта: {checkpoint}")
    else:
        print("[scale] веса свежие (обучение не запускается) — это калибровка веса, не результат")

    target = create_target(device=device)
    target_expanded = target.expand(config.TRAIN_BATCH_SIZE, -1, -1, -1)
    cur = init_state(batch_size=config.TRAIN_BATCH_SIZE, device=device, generator=generator)

    print(
        f"[scale] seed={seed} K={rollout_steps} unroll={unroll} "
        f"веса: visible_mse={config.LOSS_WEIGHTS['visible_mse']} "
        f"retention={config.LOSS_WEIGHTS['retention']} "
        f"RETENTION_SURVIVAL_WEIGHT={config.RETENTION_SURVIVAL_WEIGHT} "
        f"RETENTION_QUIET_WEIGHT={config.RETENTION_QUIET_WEIGHT} "
        f"mode={config.RETENTION_SURVIVAL_MODE}"
    )
    print(
        f"{'возраст':>7} {'af':>7} {'vis_mse':>9} {'ret_mse':>9} {'surv':>10} {'quiet':>10} "
        f"{'gn(vis)':>9} {'gn(ret)':>9} {'gn(surv)':>10} {'gn(quiet)':>10} "
        f"{'surv/vis gn':>12} {'quiet/vis gn':>13} {'ret/vis':>8}"
    )

    rows = []
    next_stage = 0
    for age in range(max(stages) + 1):
        if next_stage < len(stages) and age == stages[next_stage]:
            next_stage += 1
            visible, ret_mse, surv, quiet, live = _snapshot(
                model, cur, target_expanded, unroll, rollout_steps
            )
            gn_vis = _grad_norm(model, visible)
            gn_ret = _grad_norm(model, ret_mse)
            gn_surv = _grad_norm(model, surv)
            gn_quiet = _grad_norm(model, quiet)
            row = {
                "state_age_steps": age,
                "alive_fraction": _alive_fraction(live),
                "visible_mse": float(visible.detach().item()),
                "retention_mse": float(ret_mse.detach().item()),
                "survival": float(surv.detach().item()),
                "quiet": float(quiet.detach().item()),
                "grad_norm_visible": gn_vis,
                "grad_norm_retention_mse": gn_ret,
                "grad_norm_survival": gn_surv,
                "grad_norm_quiet": gn_quiet,
                "grad_ratio_survival_to_visible": (gn_surv / gn_vis) if gn_vis > 0 else None,
                "grad_ratio_quiet_to_visible": (gn_quiet / gn_vis) if gn_vis > 0 else None,
                "grad_ratio_retention_to_visible": (gn_ret / gn_vis) if gn_vis > 0 else None,
                "value_ratio_survival_to_visible": (
                    float(surv.detach().item()) / float(visible.detach().item())
                    if float(visible.detach().item()) > 0
                    else None
                ),
            }
            rows.append(row)
            print(
                f"{age:7d} {row['alive_fraction']:7.3f} {row['visible_mse']:9.4f} "
                f"{row['retention_mse']:9.4f} {row['survival']:10.6f} {row['quiet']:10.6f} "
                f"{gn_vis:9.4f} {gn_ret:9.4f} {gn_surv:10.6f} {gn_quiet:10.6f} "
                f"{(row['grad_ratio_survival_to_visible'] or float('nan')):12.6f} "
                f"{(row['grad_ratio_quiet_to_visible'] or float('nan')):13.6f} "
                f"{(row['grad_ratio_retention_to_visible'] or float('nan')):8.3f}"
            )
        # Состаривание без градиента: это те самые автономные шаги, из которых
        # состоит гейт удержания; градиент мы считаем отдельно, свежим срезом.
        with torch.no_grad():
            cur = run_steps(model, cur, steps=1)

    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=int(config.RETENTION_ROLLOUT_STEPS))
    parser.add_argument("--seeds", type=str, default="42")
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument(
        "--survival-mode",
        type=str,
        default=None,
        help=f"перекрыть config.RETENTION_SURVIVAL_MODE ({'/'.join(config.RETENTION_SURVIVAL_MODES)})",
    )
    parser.add_argument(
        "--quiet-margin",
        type=float,
        default=None,
        help="перекрыть config.RETENTION_QUIET_MARGIN (потолок alpha для фона = "
        "ALIVE_THRESHOLD − margin)",
    )
    args = parser.parse_args()
    if args.survival_mode:
        if args.survival_mode not in config.RETENTION_SURVIVAL_MODES:
            parser.error(f"неизвестный survival mode {args.survival_mode!r}")
        config.RETENTION_SURVIVAL_MODE = args.survival_mode
    if args.quiet_margin is not None:
        if not (0.0 <= args.quiet_margin < float(config.ALIVE_THRESHOLD)):
            parser.error(
                f"--quiet-margin={args.quiet_margin}: вне [0, ALIVE_THRESHOLD="
                f"{config.ALIVE_THRESHOLD}), потолок alpha ушёл бы за ноль"
            )
        config.RETENTION_QUIET_MARGIN = args.quiet_margin

    # Проверка форм — на свежих весах, один раз: она не про модель, а про форму
    # члена (см. docstring _blindness_check). Печатает и survival, и quiet на двух
    # предельных полях: поглощающая смерть и «живо всё».
    print("[scale] проверка форм членов удержания на двух предельных полях:")
    _blindness_check(
        NeuralCellularAutomaton(channels=config.N_CHANNELS).to(torch.device(config.DEVICE)),
        create_target(device=torch.device(config.DEVICE)).expand(
            config.TRAIN_BATCH_SIZE, -1, -1, -1
        ),
        torch.device(config.DEVICE),
    )

    out = {}
    for seed in [int(s) for s in args.seeds.split(",")]:
        out[seed] = measure(seed, rollout_steps=args.steps, checkpoint=args.checkpoint)

    # Итог одним числом: во сколько раз градиент каждого полуобернутого члена
    # слабее градиента visible_mse на САМОМ ЖИВОМ срезе, и какой множитель
    # сравнял бы их. Масштаб берётся по первому срезу: на мёртвом состоянии
    # сигнал заведомо слабее, и брать его означало бы завысить вес.
    for seed, rows in out.items():
        live = rows[0]
        if not live["grad_norm_survival"]:
            print(f"[scale] seed={seed}: у живого состояния градиент survival = 0 — член слеп")
        else:
            need_vis = live["grad_norm_visible"] / live["grad_norm_survival"]
            need_ret = live["grad_norm_retention_mse"] / live["grad_norm_survival"]
            print(
                f"[scale] seed={seed}: градиент survival слабее visible_mse в {need_vis:.1f}x, "
                f"сравнимый вклад потребует RETENTION_SURVIVAL_WEIGHT~{need_vis:.0f}; "
                f"внутри самого retention-члена (вес {config.LOSS_WEIGHTS['retention']}) "
                f"survival должен быть в {need_ret:.1f}x сильнее roll-out MSE"
            )
        if not live["grad_norm_quiet"]:
            # Не путать со слепотой survival: на срезе, где фон мёртв, quiet
            # обязан быть нулевым — наказывать нечего. Калибр нужен по срезу,
            # где фон ЖИВОЙ (например, чекпоинт R-8, NEG-20).
            print(
                f"[scale] seed={seed}: gn(quiet)=0 на первом срезе — фон там мёртв, "
                "это не слепота, а тишина; для веса брать срез с живым фоном "
                "(--checkpoint …/WP4_R-8_s2000_seed42/nca_final.pt)"
            )
        else:
            need_quiet = live["grad_norm_visible"] / live["grad_norm_quiet"]
            print(
                f"[scale] seed={seed}: градиент quiet слабее visible_mse в {need_quiet:.1f}x "
                f"(quiet={live['quiet']:.6f}), сравнимый вклад потребует "
                f"RETENTION_QUIET_WEIGHT~{need_quiet:.0f}; парность с survival означает, "
                f"что при RETENTION_SURVIVAL_WEIGHT={config.RETENTION_SURVIVAL_WEIGHT} "
                "quiet не должен быть его меньше"
            )
    return out


if __name__ == "__main__":
    main()
