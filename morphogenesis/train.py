"""
train.py — Основной цикл обучения (Truncated BPTT) по контракту §12.1.5.

[v5.6-EXP FINAL Rev.11]

Ключевые требования спеки, реализованные здесь:

- лосс — взвешенная сумма членов из config.LOSS_WEIGHTS (§12.6.3), а не
  ad-hoc «MSE + L1»;
- супервизия альфа-канала (alive_policy) и мониторинг топологии — compute_loss;
- пул состояний возвращает (state, index); state.detach() после каждого прогона;
- model.alive_mask_enabled = iteration >= ALIVE_WARMUP_ITERS, при переходе
  границы — pool.replace_all_fresh();
- NaN-гард, OOM-гард, предохранитель коллапса ткани (§12.1.13, COLLAPSE_*);
- атомарное сохранение чекпоинтов с метаданными и проверка совместимости;
- восстановление optimizer / scheduler / pool / best_loss при resume;
- логирование топологии, стресса, симметричного Chamfer, alive_fraction;
- pool.maybe_reset(sim_step) — привязка к накопленным шагам симуляции;
- единый детерминированный torch.Generator на прогон (§9.2);
- topo_proxy: grad_test на старте, observe() по §2.10.4, деградация → NEG.

Порядок импортов менять нельзя: config обязан идти раньше torch (§9.2).
"""

import atexit
import json
import math
import os
import tempfile
import time

# §9.2: config импортируется раньше torch — он выставляет
# CUBLAS_WORKSPACE_CONFIG до загрузки CUDA. Порядок не менять (isort /
# «optimize imports» ломают детерминизм, см. docs/spec §9.2).
import config

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.tensorboard import SummaryWriter

import evaluate
from config import create_deterministic_generator
from nca_core import (
    NeuralCellularAutomaton,
    StatePool,
    init_state,
    run_steps,
    target_conditioned_state,
)
from target_patterns import create_target
from topo_proxy import TopologicalProxy, topo_term_cap
from topology import (
    count_connected_components,
    count_holes,
    get_binary_mask_batch,
    remove_small_clusters,
)
from utils.logging import Journal, record_negative


def check_memory():
    """Сброс CUDA-кэша, если VRAM близок к потолку."""
    if config.CUDA_USABLE:
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        if allocated > config.MAX_VRAM_GB - 1.0 or reserved > config.MAX_VRAM_GB - 1.0:
            torch.cuda.empty_cache()
            return True
    return False


def get_current_unroll(iteration):
    """Curriculum длины BPTT (число шагов симуляции на одну итерацию)."""
    for i in range(len(config.TRAIN_BPTT_CURRICULUM_AT) - 1, -1, -1):
        if iteration >= config.TRAIN_BPTT_CURRICULUM_AT[i]:
            return config.TRAIN_BPTT_CURRICULUM[i]
    return config.TRAIN_BPTT_CURRICULUM[0]


def resolve_phase(iteration, ae_available=False):
    """
    §12.6.4–12.6.6: фаза обучения.

    Фаза 1 — предобучение NCA (объём слоя 1). Фазы 2 и 3 требуют аттракторный
    автоэнкодер (слой 2). Если AE нет, возвращаем 0 — вызывающий код обязан
    остановиться на границе фазы 1 с явным сообщением, а не «молча» продолжать
    по расписанию фазы 1 за её пределами.
    """
    if iteration <= config.PHASE1_STEPS:
        return 1
    if not ae_available:
        return 0
    if config.PHASE2_AE_ONLY and iteration <= config.PHASE1_STEPS + config.PHASE3_STEPS:
        return 3
    return 2


def build_lr_scheduler(optimizer, warmup_steps=None, horizon=None):
    """
    §12.1.5: линейный warmup TRAIN_WARMUP_STEPS, затем косинус до нуля.

    Горизонт — TRAIN_MAX_STEPS (контракт), а не длина диагностического прогона:
    короткий прогон обязан видеть ТОЧКУ ЖЕ кривую LR, что и полный, иначе
    сравнение сидов теряет смысл. Зарегистрировано в decisions_log.
    """
    if warmup_steps is None:
        warmup_steps = int(config.TRAIN_WARMUP_STEPS)
    if horizon is None:
        horizon = int(config.TRAIN_MAX_STEPS)

    def factor(step):
        if warmup_steps > 0 and step < warmup_steps:
            return (step + 1) / float(warmup_steps)
        if config.LR_SCHEDULER != "cosine":
            return 1.0
        denom = max(1, horizon - warmup_steps)
        progress = min(1.0, max(0.0, (step - warmup_steps) / float(denom)))
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    return LambdaLR(optimizer, lr_lambda=factor)


def _soft_local_error(state, target_expanded, model):
    """
    Дифференцируемая локальная ошибка относительно цели в [0, 1]: сглаженная
    разность мягкой маски (видимый × alive) и цели.

    Это УЧЕБНЫЙ сигнал (учитель), он не является частью биологического контура
    и detach-ится перед использованием (§6.3).
    """
    visible = model.visible_image(state)
    alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1])
    current = visible * alpha_prob
    err = (current - target_expanded).abs()
    weight = torch.ones(1, 1, 3, 3, device=state.device, dtype=state.dtype) / 9.0
    padded = F.pad(err, (1, 1, 1, 1), mode="reflect")
    return F.conv2d(padded, weight, padding=0)


def alive_fraction_of(state):
    """Доля живых клеток по каноническому предикату (§5.1)."""
    mask = state[:, config.ALIVE_CHANNEL, :, :]
    return float((torch.sigmoid(mask) > config.ALIVE_THRESHOLD).float().mean().item())


def topology_summary(state):
    """
    Топология по ВСЕМУ батчу (условие §23: метрики по одному сэмплу искажают
    картину). Возвращает средние β₀/β₁, χ и моду значимой плотности.
    """
    batch = get_binary_mask_batch(state)
    b0 = []
    b1 = []
    density = []
    for mask in batch:
        clean = remove_small_clusters(mask.astype(bool))
        b0.append(count_connected_components(clean))
        b1.append(count_holes(clean))
        density.append(float(clean.mean()))
    return {
        "b0": float(np.mean(b0)),
        "b1": float(np.mean(b1)),
        "chi": float(np.mean(b0) - np.mean(b1)),
        "density": float(np.mean(density)),
        "b0_samples": [int(v) for v in b0],
        "b1_samples": [int(v) for v in b1],
    }


def chamfer_summary(state, target):
    """Симметричный Chamfer по батчу (мониторинг, не лосс)."""
    target_mask = (target[0, 0].detach().cpu().numpy() > 0.5).astype(np.uint8)
    values = []
    for mask in get_binary_mask_batch(state):
        values.append(float(evaluate.compute_symmetric_chamfer_error(mask, target_mask)))
    return float(np.mean(values)) if values else float("nan")


def coverage_summary(state, target):
    """
    Покрытийный эндпоинт по батчу: recall/precision/f1 (среднее по образцам).

    Введён в WP4 как первичная точка отсчёта E02 вместо Chamfer: нормированный
    симметричный Chamfer не видит перепокрытия (измерено: всё-белое поле 0.036,
    случайное p=0.5 0.038 при 0.0 у идеального кольца), а f1 различает их
    качественно — 0.264 / 0.236 / 1.000. Chamfer остаётся в логе вторичной
    метрикой, он по-прежнему нужен для сличения с историей v5.5.
    """
    target_mask = (target[0, 0].detach().cpu().numpy() > 0.5)
    rows = [
        evaluate.compute_coverage_endpoints(mask.astype(bool), target_mask)
        for mask in get_binary_mask_batch(state)
    ]
    if not rows:
        return {k: float("nan") for k in ("recall", "precision", "f1", "over_coverage", "missed")}
    return {k: float(np.mean([r[k] for r in rows])) for k in ("recall", "precision", "f1", "over_coverage", "missed")}


def retention_rollout_loss(model, state, target_expanded, steps=None, mode=None):
    """§14.2 «удержать»: K автономных шагов из state с градиентом через них.

    Возвращает (mse, survival, quiet): среднюю за K шагов ошибку формы к цели,
    среднюю потерю живости по клеткам ЦЕЛИ и средний штраф за живость по клеткам
    ВНЕ цели.

    Почему это отдельный член, а не «длиннее unroll»: обычный BPTT считает лосс
    на ОДНОМ целевом кадре и на состоянии, полученном из пула (то есть из
    распределения, которое сама модель и породила). Оптимум такого лосса достижим
    мёртвым полем — замерено в wp4_collapse_probe (NEG-07: мёртвое поле не есть
    глобальный оптимум, но NEG-17: на постановке без удержания ткань умирает у
    5 из 5 сидов на итерации 200). Roll-out требует, чтобы поле оставалось
    целевым и живым ПОСЛЕ того, как teacher-forcing выключен, — то есть переносит
    второй критерий §14.2 из текста гейта в целевую функцию.

    Старт detach(): градиент через весь накопленный unroll удвоил бы память, а
    вопрос «удерживает ли модель форму» не про то, как она пришла в это состояние.
    Шаг берётся через run_steps, поэтому стохастические ключи (шум, dropout,
    выбор 10% обновлений) выделяются тем же ГПСЧ прогона — детерминизм §9.2
    сохраняется и внутри roll-out.

    Два режима survival-члена (config.RETENTION_SURVIVAL_MODE, см. комментарий
    там же — выбор основан на измерении, NEG-18):
      transition: relu(alpha_prev − alpha) · alpha_prev — потеря живости клеткой,
        которая была жива (идея fitness из Growing NCA).
      level: relu(ALIVE_THRESHOLD + margin − alpha) по клеткам ЦЕЛИ — требование
        «то, что должно быть живым, остаётся живым с запасом».

    Почему нужен level, а не только transition. Мёртвая клетка по AliveSTE имеет
    обнулённое состояние, а sigmoid(0) = 0.5 = ALIVE_THRESHOLD (§5.7–5.8). Для
    transition-штрафа «умереть» — это alpha_prev = alpha = 0.5, то есть ровно 0:
    член тождественно слеп к поглощающей смерти и в прогоне R-1 дал 1.9e-4…8.5e-4
    против visible_mse 0.25 (вклад в total ~5e-5, траектория не изменилась).
    level при alpha = 0.5 даёт ровно margin, а в полосе alpha ∈ (0.5; 0.5+margin),
    где клетка ещё живая, но уже на грани, — ненулевой и по значению, и по
    градиенту (замер: gn 0.043…0.136 против gn(visible_mse) 0.66).

    Граница метода, чтобы её не приписывали члену задним числом: на ПОЛНОСТЬЮ
    мёртвом поле градиент ОБОИХ форм равен 0 — обнулённое состояние нельзя
    обратить ничем (§5.2, поглощающая смерть). Значит retention может только
    предотвращать смерть в момент, когда ткань ещё живая; прогон, где ткань уже
    мертва, он не спасёт, и это проверяется тестом
    tests/test_retention_loss.py::TestLevelSurvivalSeesAbsorbingDeath.

    Третий член, quiet: relu(alpha − (ALIVE_THRESHOLD − RETENTION_QUIET_MARGIN))
    по клеткам ВНЕ цели на той же траектории. Он нужен потому, что односторонний
    survival даёт только выживание: прогон R-8 (level ×10, flat curriculum,
    alive_policy вес 2.0) на итерациях 50…600 дал af 0.988…0.999 при
    f1 ≤ 0.196 — «живо всё», NEG-20. Штраф за фон из ОДНОГО целевого кадра
    (alive_policy) эту динамику не лечит: вырождение живёт после выключения
    teacher-forcing, поэтому наказание обязано считаться на том же roll-out.
    Вес члена по умолчанию 0.0 — при нулевом весе суммарный лосс побитово
    совпадает с R-1…R-8.
    """
    k = int(config.RETENTION_ROLLOUT_STEPS if steps is None else steps)
    survival_mode = str(config.RETENTION_SURVIVAL_MODE if mode is None else mode)
    if survival_mode not in config.RETENTION_SURVIVAL_MODES:
        raise ValueError(
            f"retention survival mode={survival_mode!r} вне списка "
            f"{config.RETENTION_SURVIVAL_MODES}"
        )
    device, dtype = state.device, state.dtype
    if k <= 0:
        zero = torch.zeros((), device=device, dtype=dtype)
        return zero, zero, zero
    cur = state.detach()
    with torch.no_grad():
        alpha_prev = torch.sigmoid(cur[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1])
        # Клетки, которые по цели обязаны быть живыми. Порог 0.5 — бинаризация
        # soft-цели, а не ALIVE_THRESHOLD: это про «где должен быть рисунок».
        live_required = (target_expanded > 0.5).to(dtype=dtype)
        n_required = float(live_required.sum().item())
        alpha_floor = float(config.ALIVE_THRESHOLD) + float(config.RETENTION_ALIVE_MARGIN)
        # Зеркальная половина: клетки, которым право быть живыми цель НЕ даёт.
        quiet_mask = 1.0 - live_required
        n_quiet = float(quiet_mask.sum().item())
        alpha_ceiling = float(config.ALIVE_THRESHOLD) - float(config.RETENTION_QUIET_MARGIN)
    mse_acc = torch.zeros((), device=device, dtype=dtype)
    surv_acc = torch.zeros((), device=device, dtype=dtype)
    quiet_acc = torch.zeros((), device=device, dtype=dtype)
    for _ in range(k):
        cur = run_steps(model, cur, steps=1)
        mse_acc = mse_acc + F.mse_loss(model.visible_image(cur), target_expanded)
        alpha = torch.sigmoid(cur[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1])
        if survival_mode == "level":
            if n_required <= 0:
                raise ValueError(
                    "retention survival mode=level, а в цели нет обязательных для "
                    "жизни клеток: член был бы делением на ноль и молча нулевым"
                )
            surv = (F.relu(alpha_floor - alpha) * live_required).sum() / n_required
        else:
            surv = (F.relu(alpha_prev - alpha) * alpha_prev).mean()
        # quiet считается всегда (вклад в сумму решает вес): нулевой вес должен
        # давать побитово тот же лосс, что и до появления члена (R-1…R-8).
        if n_quiet > 0:
            quiet_acc = quiet_acc + (
                F.relu(alpha - alpha_ceiling) * quiet_mask
            ).sum() / n_quiet
        surv_acc = surv_acc + surv
        alpha_prev = alpha.detach()
    return mse_acc / k, surv_acc / k, quiet_acc / k


def compute_loss(
    state,
    target,
    model,
    phase=1,
    topo_proxy=None,
    iteration=0,
    attractor_loss=None,
    return_terms=False,
):
    """
    §12.6.3: лосс — ВЗВЕШЕННАЯ СУММА членов из config.LOSS_WEIGHTS:
      visible_mse, alive_policy, hidden_regularization, stress_proxy, topo_proxy;
      attractor_divergence добавляется только в фазе 3.
    Плюс retention (вне списка §12.6.3, расширение по §14.2): считается только
    при RETENTION_ENABLED и весе > 0 — в состоянии «как в спеке» его нет.

    Формулы alive_policy / stress_proxy спецификацией не заданы (заданы только
    имена и веса) — реализация зафиксирована в decisions_log (§0.3):
    - alive_policy = MSE(sigmoid(alpha), цель>0) · ALPHA_SUPERVISION_WEIGHT при
      ALIVE_POLICY_MODE="supervised_mse" и relu(цель−sigmoid(alpha)).mean() при
      mode="death_penalty" (односторонний штраф за смерть в области цели);
    - stress_proxy = MSE(нормированной активности |delta|, сглаженной ошибки
      относительно цели): обучает внутренний сенсор ошибки следовать внешней
      ошибке, что и есть гипотеза §6.1 (стресс-канал как системный сенсор
      пишется без градиента, поэтому «учить» сам канал напрямую нельзя —
      учится динамика, которая его порождает).
    """
    weights = config.LOSS_WEIGHTS

    # 1. visible_mse — форма в видимом канале.
    image = model.visible_image(state)
    target_expanded = target.expand(image.shape[0], -1, -1, -1)
    visible_mse = F.mse_loss(image, target_expanded)

    # 2. alive_policy — кто имеет право быть живым.
    alpha = torch.sigmoid(state[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1])
    target_alpha = (target_expanded > 0).float()
    if config.ALIVE_POLICY_MODE == "death_penalty":
        # Штрафуется только смерть там, где цель требует ткани. Жизненные
        # клетки вне цели не наказываются: их форма — задача канала 0 (§3.3).
        alive_policy = F.relu(target_alpha - alpha).mean()
    elif config.ALIVE_POLICY_MODE == "survival":
        # «Не убий»: штраф за потерю живости живой клеткой за один шаг.
        # Смерть в этой модели абсорбирующая (§5.2 запрещает воскрешение,
        # AliveSTE обнуляет клетку целиком), поэтому единственный способ
        # удержать ткань живой — наказать сам переход живой->мёртвая.
        # delta уже посчитан ниже для L1; берём его заранее, чтобы порядок
        # членов в сумме не зависел от режима.
        delta_for_alive = model.get_delta(state)
        d_alpha = delta_for_alive[:, config.ALIVE_CHANNEL : config.ALIVE_CHANNEL + 1]
        alive_policy = (F.relu(-d_alpha) * alpha).mean()
    else:
        alive_policy = F.mse_loss(alpha, target_alpha)
    alive_policy = alive_policy * float(config.ALPHA_SUPERVISION_WEIGHT)

    # 3. hidden_regularization — L1 по дельте (инерция, «ленивая» ткань).
    delta = model.get_delta(state)
    hidden_reg = torch.mean(torch.abs(delta))

    # 4. stress_proxy — активность должна следовать локальной ошибке.
    err_ref = _soft_local_error(state, target_expanded, model).detach()
    act = delta.abs().mean(dim=1, keepdim=True)
    act_norm = (act / max(1e-6, float(model.dt))).clamp(0.0, 1.0)
    stress_proxy = F.mse_loss(act_norm, err_ref)

    # 5. topo_proxy — дифференцируемый прокси β₀/β₁ (§2.10), считается не
    #    каждый шаг (TOPO_PROXY_STEP_STRIDE).
    if topo_proxy is None or not topo_proxy.next_step_ok(iteration):
        topo_proxy_loss = torch.zeros((), device=state.device, dtype=state.dtype)
    else:
        raw = topo_proxy.compute_loss(image)
        if torch.is_tensor(raw):
            # §12.6.8: гладкий потолок вклада, чтобы прокси не перекрывал MSE.
            topo_proxy_loss = topo_term_cap(raw, config.TOPO_PROXY_GRAD_CLIP)
        else:
            topo_proxy_loss = torch.zeros((), device=state.device, dtype=state.dtype)

    weighted = {
        "visible_mse": float(weights["visible_mse"]) * visible_mse,
        "alive_policy": float(weights["alive_policy"]) * alive_policy,
        "hidden_regularization": float(weights["hidden_regularization"]) * hidden_reg,
        "stress_proxy": float(weights["stress_proxy"]) * stress_proxy,
        "topo_proxy": float(weights["topo_proxy"]) * topo_proxy_loss,
    }
    total_loss = sum(weighted.values())

    # 6. retention — автономный roll-out (§14.2 «удержать»), см.
    #    retention_rollout_loss. Выключен по умолчанию (вес 0.0 и
    #    RETENTION_ENABLED=False), чтобы лосс §12.6.3 в базовом состоянии совпадал
    #    со спекой побитово.
    retention_term = torch.zeros((), device=state.device, dtype=state.dtype)
    retention_mse = torch.zeros((), device=state.device, dtype=state.dtype)
    retention_survival = torch.zeros((), device=state.device, dtype=state.dtype)
    retention_quiet = torch.zeros((), device=state.device, dtype=state.dtype)
    retention_on = (
        bool(config.RETENTION_ENABLED)
        and float(weights.get("retention", 0.0)) > 0.0
        and int(getattr(config, "RETENTION_EVERY", 1)) >= 1
        and iteration >= int(getattr(config, "RETENTION_START_ITER", 0))
        and (iteration % int(config.RETENTION_EVERY) == 0)
    )
    if retention_on:
        retention_mse, retention_survival, retention_quiet = retention_rollout_loss(
            model, state, target_expanded
        )
        retention_term = float(weights["retention"]) * (
            retention_mse
            + float(config.RETENTION_SURVIVAL_WEIGHT) * retention_survival
            # Парная половина удержания: «живое должно жить» без «фоном прав нет»
            # даёт вырождение «живо всё» (замерено в R-8, NEG-20). При весе 0.0
            # слагаемое тождественно ноль, поэтому R-1…R-8 не меняются.
            + float(config.RETENTION_QUIET_WEIGHT) * retention_quiet
        )
        weighted["retention"] = retention_term
        total_loss = total_loss + retention_term

    attractor_term = torch.zeros((), device=state.device, dtype=state.dtype)
    if phase == 3:
        if attractor_loss is None:
            raise RuntimeError(
                "Фаза 3 требует attractor_divergence (§12.6.6), а значения нет: "
                "аттракторный автоэнкодер относится к слою 2."
            )
        attractor_term = float(weights["attractor_divergence"]) * attractor_loss
        weighted["attractor_divergence"] = attractor_term
        total_loss = total_loss + attractor_term

    with torch.no_grad():
        frac_delta_nonzero = float((delta.abs() > 1e-6).float().mean().item())

    loss_dict = {
        "total": float(total_loss.item()),
        "visible_mse": float(visible_mse.item()),
        "alive_policy": float(alive_policy.item()),
        "hidden_reg": float(hidden_reg.item()),
        "stress_proxy": float(stress_proxy.item()),
        "topo_proxy": float(topo_proxy_loss.item()),
        "attractor_divergence": float(attractor_term.item()),
        "retention_mse": float(retention_mse.item()),
        "retention_survival": float(retention_survival.item()),
        "retention_quiet": float(retention_quiet.item()),
        "alive_fraction": alive_fraction_of(state),
        "frac_delta_nonzero": frac_delta_nonzero,
    }
    if return_terms:
        # Взвешенные вклады каждого члена — единственный источник истины для
        # атрибуции градиента (wp4_collapse_probe спрашивает «кто толкает в
        # смерть», и спрашивает по ОТДЕЛЬНЫМ членам, а не по пересобранной
        # вручную сумме: пересобранная вручную сумма — это расхождение с
        # обучением, и тест тогда проверял бы сам себя).
        return total_loss, loss_dict, weighted
    return total_loss, loss_dict


# На Windows os.replace падает с PermissionError, если целевой файл в этот
# момент открыт другим процессом. Для 539-МБ чекпоинтов это регулярно делает
# Defender: он сканирует только что созданный nca_best.pt и держит его, пока
# следующий best пытается заменить предыдущий. Без retry длинный прогон
# умирает не из-за модели, а из-за антивируса (наблюдалось на H-P1 s2000).
_REPLACE_RETRIES = 20
_REPLACE_DELAY_S = 0.5


def atomic_save(obj, path):
    dir_name = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            torch.save(obj, f)
        for attempt in range(_REPLACE_RETRIES):
            try:
                os.replace(tmp_path, path)
                break
            except PermissionError:
                if attempt == _REPLACE_RETRIES - 1:
                    raise
                time.sleep(_REPLACE_DELAY_S)
    except BaseException:
        # Уборка tmp не должна маскировать исходную ошибку сохранения.
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        raise


def append_to_log(log_path, entry):
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def checkpoint_payload(model, optimizer, scheduler, pool, state, *, iteration, loss, seed,
                       experiment_id, best_loss, topo_proxy=None):
    """Единая форма чекпоинта (§13.5): метаданные обязательны."""
    metadata = config.get_checkpoint_metadata(
        seed=seed,
        experiment_id=experiment_id,
        iteration=iteration,
        best_loss=best_loss,
    )
    if topo_proxy is not None:
        metadata["topo_proxy_backend"] = topo_proxy.backend
    return {
        "iteration": iteration,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict() if scheduler else None,
        "pool_state_dict": pool.state_dict(),
        "state": state,
        "loss": loss,
        "seed": seed,
        "grid_size": config.GRID_SIZE,
        "n_channels": config.N_CHANNELS,
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "stress_enabled": config.STRESS_ENABLED,
        "stress_channel": config.STRESS_CHANNEL,
        "metadata": metadata,
    }


def make_topo_proxy(target, experiment_id="E02", device=None):
    """
    §2.10: прокси обязан пройти градиентный чекпоинт ДО начала обучения.
    Непрошедший прокси честно деградирует в disabled и пишется в NEG.
    """
    proxy = TopologicalProxy(target, backend=None)
    report = {"backend": proxy.backend, "passed": None, "note": "grad_test не требуется"}
    if proxy.backend != "disabled":
        report = proxy.grad_test(device=device)
        if not report["passed"]:
            event = proxy._degrade(f"grad_test не пройден: {report}")
            neg = record_negative(
                title="topo_proxy: градиентный чекпоинт не пройден",
                experiment=experiment_id,
                hypothesis="§2.10: дифференцируемый топологический член даёт ненулевой градиент",
                expected="‖∂L_topo/∂state‖ > 0 и конечен",
                observed=str(report),
                interpretation="Прокси отключён (backend=disabled), обучение идёт без topo-члена.",
                next_step=(
                    "Реализовать torch-topological persistent homology или "
                    "мягкий прокси с другой параметризацией."
                ),
            )
            append_to_log(
                os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl"),
                {"event": "topo_proxy_degraded", "neg": neg, "report": report, "detail": event},
            )
    return proxy, report


def topo_proxy_health(proxy):
    """Снимок состояния прокси для eval-записи (§2.10.4)."""
    return {
        "backend": proxy.backend,
        "stride": proxy.stride,
        "weight": proxy.weight,
        "target_chi": proxy.target_chi,
        "steps_without_gradient": proxy.steps_without_gradient,
        "nan_count": proxy.nan_count,
        "degraded": proxy.degraded,
        "degradation_reason": proxy.degradation_reason,
    }


def train(
    resume_from=None,
    experiment_id="E02",
    seed=None,
    max_steps=None,
    target_pattern=None,
    ae_available=False,
    stop_on_collapse=True,
    init_seed=None,
    data_seed=None,
):
    print("=" * 60)
    print("PROJECT MORPHOGENESIS: Запуск обучения")
    print("=" * 60)

    config.validate()

    if seed is None:
        seed = config.SEED
    # Декомпозиция сида (H-E02C-5): по умолчанию оба фактора равны `seed`,
    # поэтому поведение побитово прежнее. `init_seed` задаёт только глобальный
    # RNG (инициализацию весов), `data_seed` — только генератор шума, пула и
    # порядка сэмплов. Разделение нужно, чтобы понять, какой фактор выбирает
    # класс `struct_2`.
    init_seed = int(seed) if init_seed is None else int(init_seed)
    data_seed = int(seed) if data_seed is None else int(data_seed)
    config.set_seed(init_seed)
    if target_pattern is not None:
        config.set_target_pattern(target_pattern)

    # Детерминированный генератор для всех стохастических операций (§9.2).
    generator = create_deterministic_generator(data_seed)

    for d in [
        config.CHECKPOINT_DIR,
        config.LOG_DIR,
        config.OUTPUT_DIR,
        config.FRAMES_DIR,
        config.EVAL_DIR,
    ]:
        os.makedirs(d, exist_ok=True)

    log_dir = os.path.join(config.LOG_DIR, experiment_id)
    os.makedirs(log_dir, exist_ok=True)
    event_log_path = os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl")

    device = torch.device(config.DEVICE)
    print(f"Устройство: {device}")

    model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)
    model.set_generator(generator)

    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.TRAIN_LR,
        weight_decay=config.TRAIN_WEIGHT_DECAY,
    )

    target = create_target(device=device)

    # Плотность цели нужна предохранителю коллапса: абсолютный порог 0.15
    # стоит впритык к плотности цели ring (измерено 0.1523), поэтому порог
    # считается ОТНОСИТЕЛЬНО цели — см. config.collapse_alive_fraction_min и
    # запись в memory/decisions_log.jsonl (WP4).
    with torch.no_grad():
        target_density = float((target > 0).float().mean().item())
    collapse_threshold = config.collapse_alive_fraction_min(target_density)

    # [WP4] Диагностический режим пула: TRAIN_POOL_INIT_MODE="target" наполняет
    # (и перезаполняет на сбросе ПРАВИЛА 29) пул состоянием, где видимый канал
    # УЖЕ равен цели. Это проверяет ёмкость и удержание формы отдельно от роста
    # из шума; по умолчанию "noise" — контракт §14.2 не меняется.
    pool_fresh_fn = None
    if config.TRAIN_POOL_INIT_MODE == "target":

        def pool_fresh_fn():
            return target_conditioned_state(
                target,
                batch_size=config.TRAIN_BATCH_SIZE,
                device=device,
            )

    pool = StatePool(
        size=config.TRAIN_SAMPLE_POOL_SIZE,
        device=device,
        generator=generator,
        batch_size=config.TRAIN_BATCH_SIZE,
        fresh_fn=pool_fresh_fn,
    )

    total_steps = int(config.TRAIN_MAX_STEPS)
    if max_steps is not None:
        total_steps = min(int(max_steps), total_steps)

    start_iteration = 1
    best_loss = float("inf")
    scheduler = None
    checkpoint = None

    if resume_from and os.path.exists(resume_from):
        checkpoint = torch.load(resume_from, map_location=device, weights_only=False)
        if checkpoint.get("grid_size", config.GRID_SIZE) != config.GRID_SIZE:
            raise ValueError(
                f"Несовместимый чекпоинт: grid_size={checkpoint['grid_size']}, "
                f"конфиг={config.GRID_SIZE}"
            )
        if checkpoint.get("n_channels", config.N_CHANNELS) != config.N_CHANNELS:
            raise ValueError(
                f"Несовместимый чекпоинт: n_channels={checkpoint['n_channels']}, "
                f"конфиг={config.N_CHANNELS}"
            )
        # §13.5: чужая версия/ревизия — отказ загрузки.
        config.assert_checkpoint_compatible(
            checkpoint,
            allow_missing_metadata=True,
            context=f"train.resume({resume_from})",
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if "pool_state_dict" in checkpoint:
            pool.load_state_dict(checkpoint["pool_state_dict"])
        start_iteration = checkpoint.get("iteration", 0) + 1
        best_loss = checkpoint.get("loss", float("inf"))
        print(f"Возобновление из {resume_from}, итерация {start_iteration}")

    if start_iteration > total_steps:
        print(
            f"Обучение уже завершено (итерация {start_iteration} > {total_steps})"
        )
        if checkpoint is not None:
            return model, checkpoint.get("state", init_state(device=device, generator=generator))
        return model, init_state(batch_size=config.TRAIN_BATCH_SIZE, device=device, generator=generator)

    scheduler = build_lr_scheduler(optimizer)
    if checkpoint is not None and checkpoint.get("scheduler_state_dict") is not None:
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    topo_proxy, grad_report = make_topo_proxy(target, experiment_id=experiment_id, device=device)

    writer = SummaryWriter(log_dir=log_dir)

    print("\nПараметры:")
    print(f"  Версия: {config.SPEC_VERSION} / {config.SPEC_REVISION}")
    print(f"  Цель: {config.TARGET_PATTERN} {config.TARGET_TOPOLOGY}")
    print(f"  Сетка: {config.GRID_SIZE}x{config.GRID_SIZE}, каналов: {config.N_CHANNELS}")
    print(f"  Батч: {config.TRAIN_BATCH_SIZE}, пул: {config.TRAIN_SAMPLE_POOL_SIZE}")
    print(f"  Шагов: {total_steps}, curriculum BPTT: {config.TRAIN_BPTT_CURRICULUM}")
    print(f"  LR: {config.TRAIN_LR} (warmup {config.TRAIN_WARMUP_STEPS}), wd {config.TRAIN_WEIGHT_DECAY}")
    print(f"  Stress enabled: {config.STRESS_ENABLED}, канал: {config.STRESS_CHANNEL}")
    print(f"  topo_proxy: {topo_proxy.backend}, grad_test: {grad_report}")
    print(f"  Seed: {seed}")
    print(
        f"  Плотность цели: {target_density:.4f} | порог коллапса: {collapse_threshold:.4f} "
        f"(ratio {config.COLLAPSE_ALIVE_FRACTION_RATIO} от цели, floor {config.COLLAPSE_ALIVE_FRACTION_FLOOR})"
    )
    print(
        f"  Retention (§14.2): enabled={config.RETENTION_ENABLED} "
        f"вес={config.LOSS_WEIGHTS.get('retention')} K={config.RETENTION_ROLLOUT_STEPS} "
        f"survival={config.RETENTION_SURVIVAL_WEIGHT} mode={config.RETENTION_SURVIVAL_MODE}"
        f" margin={config.RETENTION_ALIVE_MARGIN}"
        f" quiet={config.RETENTION_QUIET_WEIGHT}"
        f"(margin={config.RETENTION_QUIET_MARGIN}) every={config.RETENTION_EVERY}"
    )
    print()

    append_to_log(
        event_log_path,
        {
            "event": "run_start",
            "experiment_id": experiment_id,
            "spec_version": config.SPEC_VERSION,
            "revision": config.SPEC_REVISION,
            "seed": seed,
            "target_pattern": config.TARGET_PATTERN,
            "target_topology": dict(config.TARGET_TOPOLOGY),
            "target_density": target_density,
            "alive_policy_mode": config.ALIVE_POLICY_MODE,
            "alpha_supervision_weight": float(config.ALPHA_SUPERVISION_WEIGHT),
            "collapse_alive_fraction_min": collapse_threshold,
            "total_steps": total_steps,
            "batch_size": config.TRAIN_BATCH_SIZE,
            "pool_init_mode": config.TRAIN_POOL_INIT_MODE,
            "loss_weights": dict(config.LOSS_WEIGHTS),
            # Retention (§14.2): вес сам по себе в loss_weights есть, но K,
            # survival-множитель и интервал — отдельные числа, и без них запись
            # run_start не различает «retention при K=8 каждый шаг» и «K=32 раз в
            # 4 шага» при одинаковом весе.
            "retention": {
                "enabled": bool(config.RETENTION_ENABLED),
                "rollout_steps": int(config.RETENTION_ROLLOUT_STEPS),
                "survival_weight": float(config.RETENTION_SURVIVAL_WEIGHT),
                # Форма штрафа (transition/level) решает, видит ли член
                # поглощающую смерть вообще, поэтому два прогона с одинаковым
                # весом, но разным mode — разные эксперименты (§13.5).
                "survival_mode": str(config.RETENTION_SURVIVAL_MODE),
                "alive_margin": float(config.RETENTION_ALIVE_MARGIN),
                # Парная половина без этих двух чисел неразличима: прогон
                # «survival + quiet» и прогон «только survival» при одном и том
                # же survival-весе — разные эксперименты (§13.5).
                "quiet_weight": float(config.RETENTION_QUIET_WEIGHT),
                "quiet_margin": float(config.RETENTION_QUIET_MARGIN),
                "every": int(config.RETENTION_EVERY),
                "start_iter": int(config.RETENTION_START_ITER),
            },
            "topo_proxy_backend": topo_proxy.backend,
            "topo_proxy_grad_test": grad_report,
            "device": config.DEVICE,
            # §13.3 / NEG-11: отметка, что этот билд умеет закрывать пару. Старые
            # логи (волны WP4, прошлые гейты) писались кодом без finish, и
            # требовать от них пары нельзя — инструмент отличает «прогон без
            # финиша» от «прогон до появления финиша» по этому полю, а не по
            # догадке. Задним числом прошлые прогоны не дописываются (§7.7).
            "emits_run_finish": True,
        },
    )

    nan_count = 0
    collapse_fuse_fired = False
    phase_boundary_reached = False
    last_grad_norm = float("nan")

    # §13.3: эксперимент без finish-записи = оборванный эксперимент. Пишем
    # гарантированную пару start/finish в общий logs/journal.jsonl (per-run лог
    # отвечает за траекторию, журнал — за то, что прогон вообще дошёл до конца).
    journal = Journal(experiment=experiment_id)
    run_finished = {"done": False}

    def _finish_marker():
        """Вызывается и из штатного конца, и из atexit: оборванный процесс обязан
        оставить в журнале след, иначе §13.3 молча нарушается при падении."""
        if run_finished["done"]:
            return
        run_finished["done"] = True
        journal.finish(
            level="warning",
            stop_reason="aborted",
            note="процесс завершился без штатной finish-записи (atexit)",
        )

    atexit.register(_finish_marker)
    journal.start(
        spec_version=config.SPEC_VERSION,
        revision=config.SPEC_REVISION,
        seed=int(seed),
        init_seed=int(init_seed),
        data_seed=int(data_seed),
        total_steps=total_steps,
        batch_size=config.TRAIN_BATCH_SIZE,
        pool_init_mode=config.TRAIN_POOL_INIT_MODE,
        device=config.DEVICE,
        emits_run_finish=True,
    )
    t_run = time.time()

    # ПРАВИЛО 29: сброс пула привязан к накопленным шагам СИМУЛЯЦИИ,
    # а не к номеру итерации оптимизатора.
    sim_steps_accumulated = (start_iteration - 1) * get_current_unroll(start_iteration)

    model.train()
    state = None

    for iteration in range(start_iteration, total_steps + 1):
        t_start = time.time()

        phase = resolve_phase(iteration, ae_available=ae_available)
        if phase == 0:
            print(
                f"\n[{iteration}] Граница фазы 1 (PHASE1_STEPS={config.PHASE1_STEPS}) "
                f"достигнута, аттракторного автоэнкодера (слой 2) нет — остановка. "
                f"Продолжать фазу 2/3 расписанием нельзя (§12.6.5)."
            )
            phase_boundary_reached = True
            break

        unroll = get_current_unroll(iteration)
        sim_steps_accumulated += unroll

        if config.ALIVE_WARMUP_ITERS > 0 and iteration == config.ALIVE_WARMUP_ITERS:
            pool.replace_all_fresh()
            print(
                f"[{iteration:5d}] ♻️ Сброс пула: включение alive-маски после warmup"
            )
        model.alive_mask_enabled = iteration >= config.ALIVE_WARMUP_ITERS

        state, pool_idx = pool.sample()

        try:
            state = run_steps(model, state, steps=unroll)
            total_loss, loss_dict = compute_loss(
                state, target, model, phase=phase, topo_proxy=topo_proxy, iteration=iteration
            )
        except RuntimeError as exc:
            if "out of memory" in str(exc):
                print(f"⚠️ OOM на итерации {iteration}. Заменяю состояние.")
                if config.CUDA_USABLE:
                    torch.cuda.empty_cache()
                pool.replace_with_fresh(pool_idx)
                continue
            raise

        if not torch.isfinite(total_loss):
            nan_count += 1
            print(f"⚠️ NaN/Inf (подряд: {nan_count})")
            if nan_count >= 3:
                ckpt_path = os.path.join(config.CHECKPOINT_DIR, "nca_best.pt")
                if os.path.exists(ckpt_path):
                    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
                    config.assert_checkpoint_compatible(ckpt, context="train.nan_rollback")
                    model.load_state_dict(ckpt["model_state_dict"])
                    optimizer.load_state_dict(ckpt["optimizer_state_dict"])
                    if ckpt.get("scheduler_state_dict") is not None:
                        scheduler.load_state_dict(ckpt["scheduler_state_dict"])
                    print(f"Откат к {ckpt_path}")
                nan_count = 0
            pool.replace_with_fresh(pool_idx)
            continue
        nan_count = 0

        optimizer.zero_grad()
        total_loss.backward()
        last_grad_norm = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.TRAIN_GRAD_CLIP_NORM)
        )
        optimizer.step()
        scheduler.step()

        state = state.detach()
        pool.update(state, pool_idx)
        pool.maybe_reset(sim_steps_accumulated)
        check_memory()

        # §2.10.4: наблюдение за состоянием прокси после шага.
        event = topo_proxy.observe(
            loss_value=loss_dict["topo_proxy"],
            grad_norm=last_grad_norm,
            step=iteration,
        )
        if event is not None:
            neg = record_negative(
                title="topo_proxy: деградация в disabled по §2.10.4",
                experiment=experiment_id,
                hypothesis="§2.10.4: нулевой/NaN вклад топологического члена обнаруживается и чинится",
                expected="ненулевой конечный вклад прокси в пределах GRACE_STEPS",
                observed=str(event),
                interpretation="Прокси переведён в backend=disabled, обучение продолжается без topo-члена.",
                next_step="Разобраться с причиной (пороговая бинаризация / площадь цели / шаг).",
            )
            append_to_log(
                event_log_path,
                {"event": "topo_proxy_degraded", "neg": neg, "iteration": iteration, "detail": event},
            )
            print(f"[{iteration:5d}] ⚠️ topo_proxy → disabled ({event.get('reason')}) NEG={neg}")

        # Предохранитель коллапса ткани (§12.1.13). Порог относительный —
        # collapse_threshold считан из плотности цели до начала цикла.
        if (
            config.COLLAPSE_GUARD
            and stop_on_collapse
            and iteration >= config.COLLAPSE_GUARD_MIN_ITERATIONS
            and loss_dict["alive_fraction"] < collapse_threshold
        ):
            collapse_fuse_fired = True
            neg = record_negative(
                title="Коллапс ткани: alive_fraction ниже порога",
                experiment=experiment_id,
                hypothesis="Обучаемая динамика сохраняет живые клетки (живой паттерн, §5)",
                expected=(
                    f"alive_fraction >= {collapse_threshold:.4f} "
                    f"(= {config.COLLAPSE_ALIVE_FRACTION_RATIO} · плотность цели {target_density:.4f})"
                ),
                observed=(
                    f"iteration={iteration}, alive_fraction={loss_dict['alive_fraction']:.4f}, "
                    f"loss={loss_dict['total']:.4f}, grad_norm={last_grad_norm:.4f}"
                ),
                interpretation=(
                    "Целевая функция достижима ценой полной смерти ткани: MSE(мёртвое поле, "
                    "фон) минимален. См. диагностику WP4 (H-A..H-D)."
                ),
                next_step="ALIVE_POLICY_MODE, ALPHA_SUPERVISION_WEIGHT / warmup, hidden_regularization, ёмкость CellBrain, LR-sweep.",
            )
            append_to_log(
                event_log_path,
                {
                    "event": "collapse_fuse",
                    "neg": neg,
                    "iteration": iteration,
                    "alive_fraction": loss_dict["alive_fraction"],
                    "collapse_alive_fraction_min": collapse_threshold,
                    "target_density": target_density,
                    "loss": loss_dict,
                    "grad_norm": last_grad_norm,
                },
            )
            print(
                f"\n[{iteration:5d}] ☠️ COLLAPSE FUSE: alive_fraction="
                f"{loss_dict['alive_fraction']:.4f} < {collapse_threshold:.4f} "
                f"— остановка, NEG={neg}"
            )
            break

        if iteration % config.TRAIN_LOG_INTERVAL == 0:
            topo_metrics = topology_summary(state)
            current_lr = optimizer.param_groups[0]["lr"]
            if config.STRESS_ENABLED:
                stress_mean = float(state[:, config.STRESS_CHANNEL].mean().item())
                stress_max = float(state[:, config.STRESS_CHANNEL].max().item())
            else:
                stress_mean = 0.0
                stress_max = 0.0
            sym_chamfer = chamfer_summary(state, target)
            coverage = coverage_summary(state, target)

            ret_note = (
                f", ret={loss_dict['retention_mse']:.4f} "
                f"surv={loss_dict['retention_survival']:.4f}"
                if config.RETENTION_ENABLED
                else ""
            )
            # quiet печатается только когда член реально входит в сумму: строка
            # лога, обещающая «удержание с парой» при выключенном члене, — это
            # ровно тот класс самообмана, из-за которого §13.3 требует пару
            # старт/финиш.
            if config.RETENTION_ENABLED and float(config.RETENTION_QUIET_WEIGHT) > 0.0:
                ret_note += f" quiet={loss_dict['retention_quiet']:.4f}"
            print(
                f"[{iteration:5d}/{total_steps}] loss={loss_dict['total']:.4f} "
                f"(vis={loss_dict['visible_mse']:.4f}, alive={loss_dict['alive_policy']:.4f}, "
                f"l1={loss_dict['hidden_reg']:.5f}, str={loss_dict['stress_proxy']:.4f}, "
                f"topo={loss_dict['topo_proxy']:.4f}{ret_note}) "
                f"| β₀={topo_metrics['b0']:.1f} β₁={topo_metrics['b1']:.1f} "
                f"| af={loss_dict['alive_fraction']:.3f} "
                f"| stress={stress_mean:.3f} | chamfer={sym_chamfer:.3f} "
                f"| f1={coverage['f1']:.3f} R={coverage['recall']:.3f} P={coverage['precision']:.3f} "
                f"| lr={current_lr:.2e} gn={last_grad_norm:.2f} "
                f"| unroll={unroll} ph{phase} | {time.time() - t_start:.2f}s"
            )

            for key in (
                "total",
                "visible_mse",
                "alive_policy",
                "hidden_reg",
                "stress_proxy",
                "topo_proxy",
                "attractor_divergence",
            ):
                writer.add_scalar(f"Loss/{key}", loss_dict[key], iteration)
            writer.add_scalar("Alive/fraction", loss_dict["alive_fraction"], iteration)
            writer.add_scalar("Alive/frac_delta_nonzero", loss_dict["frac_delta_nonzero"], iteration)
            writer.add_scalar("Topology/beta_0", topo_metrics["b0"], iteration)
            writer.add_scalar("Topology/beta_1", topo_metrics["b1"], iteration)
            writer.add_scalar("Topology/chi", topo_metrics["chi"], iteration)
            writer.add_scalar("Topology/density", topo_metrics["density"], iteration)
            writer.add_scalar("Stress/mean", stress_mean, iteration)
            writer.add_scalar("Stress/max", stress_max, iteration)
            writer.add_scalar("Chamfer/symmetric", sym_chamfer, iteration)
            for key in ("f1", "recall", "precision", "over_coverage"):
                writer.add_scalar(f"Coverage/{key}", coverage[key], iteration)
            writer.add_scalar("LR/current", current_lr, iteration)
            writer.add_scalar("Grad/norm", last_grad_norm, iteration)
            writer.add_scalar("TopoProxy/loss", loss_dict["topo_proxy"], iteration)

            append_to_log(
                event_log_path,
                {
                    "iteration": iteration,
                    "spec_version": config.SPEC_VERSION,
                    "revision": config.SPEC_REVISION,
                    "phase": phase,
                    "loss": loss_dict,
                    "topology": topo_metrics,
                    "stress_mean": stress_mean,
                    "stress_max": stress_max,
                    "symmetric_chamfer_error": sym_chamfer,
                    "coverage": coverage,
                    "lr": current_lr,
                    "grad_norm": last_grad_norm,
                    "unroll": unroll,
                    "alive_mask_enabled": bool(model.alive_mask_enabled),
                    "topo_proxy_backend": topo_proxy.backend,
                },
            )

        if iteration % config.TRAIN_EVAL_INTERVAL == 0:
            append_to_log(
                event_log_path,
                {
                    "event": "eval",
                    "iteration": iteration,
                    "target_topology": dict(config.TARGET_TOPOLOGY),
                    "topology": topology_summary(state),
                    "alive_fraction": loss_dict["alive_fraction"],
                    "symmetric_chamfer_error": chamfer_summary(state, target),
                    "coverage": coverage_summary(state, target),
                    "topo_proxy": topo_proxy_health(topo_proxy),
                },
            )

        if iteration % config.TRAIN_VISUALIZE_INTERVAL == 0:
            evaluate.save_frame(model, state, iteration, save_dir=config.FRAMES_DIR)

        if iteration % config.TRAIN_SAVE_INTERVAL == 0:
            atomic_save(
                checkpoint_payload(
                    model,
                    optimizer,
                    scheduler,
                    pool,
                    state,
                    iteration=iteration,
                    loss=loss_dict["total"],
                    seed=seed,
                    experiment_id=experiment_id,
                    best_loss=best_loss,
                    topo_proxy=topo_proxy,
                ),
                os.path.join(config.CHECKPOINT_DIR, f"nca_iter_{iteration}.pt"),
            )

        if loss_dict["total"] < best_loss:
            best_loss = loss_dict["total"]
            atomic_save(
                checkpoint_payload(
                    model,
                    optimizer,
                    scheduler,
                    pool,
                    state,
                    iteration=iteration,
                    loss=best_loss,
                    seed=seed,
                    experiment_id=experiment_id,
                    best_loss=best_loss,
                    topo_proxy=topo_proxy,
                ),
                os.path.join(config.CHECKPOINT_DIR, "nca_best.pt"),
            )

    if state is not None:
        final_iteration = iteration
        final_metadata_loss = best_loss if math.isfinite(best_loss) else loss_dict["total"]
        atomic_save(
            checkpoint_payload(
                model,
                optimizer,
                scheduler,
                pool,
                state,
                iteration=final_iteration,
                loss=final_metadata_loss,
                seed=seed,
                experiment_id=experiment_id,
                best_loss=best_loss,
                topo_proxy=topo_proxy,
            ),
            os.path.join(config.CHECKPOINT_DIR, "nca_final.pt"),
        )

    stop_reason = (
        "collapse_fuse"
        if collapse_fuse_fired
        else "phase_boundary"
        if phase_boundary_reached
        else "max_steps"
    )
    finish_fields = {
        "stop_reason": stop_reason,
        "iterations_done": int(iteration - start_iteration + 1) if state is not None else 0,
        "best_loss": float(best_loss) if math.isfinite(best_loss) else None,
        "nan_count": int(nan_count),
        "wall_time_sec": round(time.time() - t_run, 2),
        "pool_init_mode": config.TRAIN_POOL_INIT_MODE,
    }
    if state is not None:
        finish_fields["alive_fraction_final"] = float(alive_fraction_of(state))
        finish_fields["sim_steps_accumulated"] = int(sim_steps_accumulated)
    append_to_log(
        event_log_path,
        {"event": "run_finish", "experiment_id": experiment_id, **finish_fields},
    )
    journal.finish(**finish_fields)
    run_finished["done"] = True

    writer.flush()
    writer.close()

    print(f"\nОбучение завершено. Лучший лосс: {best_loss:.4f}")
    if collapse_fuse_fired:
        print("⚠️ Остановка по коллапсу ткани — результат NEG, см. memory/negative_results.md")
    if phase_boundary_reached:
        print("ℹ️ Остановка на границе фазы 1 (слой 2 не реализован).")
    return model, state


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--experiment", type=str, default="E02")
    parser.add_argument("--seed", type=int, default=config.SEED)
    parser.add_argument("--max-steps", type=int, default=None,
                        help="Диагностический прогон короче TRAIN_MAX_STEPS")
    parser.add_argument("--target", type=str, default=None,
                        help=f"Цель из каталога §12.5: {sorted(config.TARGET_PATTERN_TOPOLOGY)}")
    parser.add_argument("--no-collapse-stop", action="store_true",
                        help="Не останавливаться по предохранителю коллапса (для диагностики)")
    args = parser.parse_args()

    train(
        resume_from=args.resume,
        experiment_id=args.experiment,
        seed=args.seed,
        max_steps=args.max_steps,
        target_pattern=args.target,
        stop_on_collapse=not args.no_collapse_stop,
    )
