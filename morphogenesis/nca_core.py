"""

nca_core.py — Ядро Нейроклеточного Автомата.

[v5.6-EXP FINAL] Rev.11

Ключевые требования:

- alive-маска и life_support_mask вычисляются из pre-update state;

- delta маскируется ДО обновления;

- стресс считается из девиации относительно EMA (разрыв петли стресс→DT→стресс);

- канал 15 исключён из delta_norm;

- стресс считается после применения life_support_mask;

- reflect-паддинг для диффузии стресса;

- детерминированные генераторы для стохастики;

- свежее состояние гарантирует >= FRESH_MIN_ALIVE_FRACTION живых клеток;

- канал 15 в свежих состояниях инициализируется нулями.

"""

# §9.2: config импортируется раньше torch — он выставляет
# CUBLAS_WORKSPACE_CONFIG до загрузки CUDA. Порядок не менять (isort/intelliJ
# «optimize imports» ломают детерминизм, см. docs/spec §9.2).
import config

import torch

import torch.nn as nn

import torch.nn.functional as F

from torch.utils.checkpoint import checkpoint as grad_checkpoint

# §9.2: устройство-адаптивные рисования из ЛОКАЛЬНОГО torch.Generator.

# PyTorch привязывает Generator к устройству: из CPU-ГПСЧ нельзя наполнить

# CUDA-тензор (`Expected a 'cuda' device type for generator`). Проект держит

# один CPU-генератор на прогон — энтропийный поток тогда не зависит от наличия

# GPU и прогоны сравнимы между машинами, — а отрисованное переносится на

# устройство тензора (для масок 64×64 это десятки килобайт за шаг).

from utils.determinism import rand as _rand

from utils.determinism import randn as _randn

from utils.determinism import randperm as _randperm


class PerceptionLayer(nn.Module):

    """

    Восприятие без параметров (§12.2.2): окрестность Мура 3×3.

    [v5.6 Rev.11] Здесь больше НЕТ обучаемого свёрточного слоя: в Rev.7/8

    perception был Conv2d(C→C, 3×3), то есть клетка видела не соседей, а

    их выученную линейную смесь, и «локальность» архитектуры была мнимой.

    Теперь вход клетки — конкатенация 9 сдвигов состояния (9·C каналов),

    а вся нелинейность живёт в CellBrain (§12.2.2).

    Порядок каналов: (dy, dx) → блок из C каналов, т.е. канал k·C + c

    соответствует соседу MOORE_NEIGHBOR_OFFSETS[k] и каналу c.

    Граничные клетки видят «мёртвых» соседей как нули (constant-pad, §12.2.2).

    """

    def __init__(self, boundary_mode=config.BOUNDARY_MODE):

        super().__init__()

        self.boundary_mode = boundary_mode

    def forward(self, state):

        if self.boundary_mode == "circular":

            padded = F.pad(state, (1, 1, 1, 1), mode="circular")

        elif self.boundary_mode == "reflect":

            padded = F.pad(state, (1, 1, 1, 1), mode="reflect")

        else:

            # ПРАВИЛО 23 / §12.2.2: восприятие использует constant.

            padded = F.pad(state, (1, 1, 1, 1), mode="constant", value=0)

        b, c, h, w = state.shape

        views = []

        for dy, dx in config.MOORE_NEIGHBOR_OFFSETS:

            views.append(padded[:, :, 1 + dy:1 + dy + h, 1 + dx:1 + dx + w])

        return torch.cat(views, dim=1)

def apply_channel_dropout(perception, generator=None, draws=None):

    """

    §12.1.6 / §12.6.9: Channel Dropout только на восприятие.

    Обнуляются ВСЕ 9 копий одного канала состояния (k·C + c для всех k),

    иначе клетка продолжала бы видеть этот канал через других соседей.

    Запрещено применять к состоянию перед backward (§12.1.6).

    draws — готовый вектор равномерных чисел (нужен для репоя стохастики при

    градиентном чекпоинтинге); если None, рисуется локальным генератором.

    """

    if not config.CHANNEL_DROPOUT_ENABLED or not config.CHANNEL_DROPOUT_CHANNELS:

        return perception

    channels = config.N_CHANNELS

    b, pc, h, w = perception.shape

    n_blocks = pc // channels

    dropout_channels = [int(c) for c in config.CHANNEL_DROPOUT_CHANNELS if 0 <= int(c) < channels]

    if not dropout_channels:

        return perception

    # Один векторный рисунок на шаг — детерминированно и дёшево.

    if draws is None:

        draws = _rand(

            (len(dropout_channels),),

            generator=generator,

            device="cpu",

            dtype=torch.float32,

        )

    drop = (draws < config.CHANNEL_DROPOUT_PROB)

    keep = torch.ones(pc, device=perception.device, dtype=perception.dtype)

    for k_pos, channel in enumerate(dropout_channels):

        if bool(drop[k_pos]):

            for block in range(n_blocks):

                keep[block * channels + channel] = 0.0

    return perception * keep.view(1, pc, 1, 1)

class CellBrain(nn.Module):

    """

    §12.2.2: Conv2d 9C→hidden→hidden→C со kernel_size=1 (все 1×1).

    Последний слой инициализируется НУЛЯМИ — система стартует из покоя.

    """

    def __init__(self, channels=config.N_CHANNELS, hidden_dim=config.CELL_BRAIN_HIDDEN_DIM):

        super().__init__()

        self.input_channels = config.CELL_BRAIN_INPUT_CHANNELS

        self.net = nn.Sequential(

            nn.Conv2d(self.input_channels, hidden_dim, kernel_size=1),

            nn.ReLU(),

            nn.Conv2d(hidden_dim, hidden_dim, kernel_size=1),

            nn.ReLU(),

            nn.Conv2d(hidden_dim, channels, kernel_size=1),

        )

        nn.init.zeros_(self.net[-1].weight)

        nn.init.zeros_(self.net[-1].bias)

    def forward(self, perception):

        """perception: (B, 9*C, H, W) -> delta: (B, C, H, W)."""

        return self.net(perception)

class AliveSTE(torch.autograd.Function):

    """

    §5.8: живая маска с жёстким forward и суррогатным градиентом в backward.

    forward  — смерть-инвариант соблюдается строго: мёртвая клетка обнуляется

               ЦЕЛИКОМ, включая стресс-канал (§5.7 Rev.11);

    backward — вместо нулевой производной порога используется мягкий сигмоидный

               суррогат с температурой ALIVE_SURROGATE_TAU, чтобы оптимизатор

               не попадал в мёртвую зону по alive-каналу (главный механизм

               death-spiral, из-за которого E02 складывался на ~30 итерации).

    Предикат живости — канонический для проекта: sigmoid(alpha) > ALIVE_THRESHOLD

    (совпадает с topology/evaluate/тестами; спека §5.1 пишет сравнение сырого

    канала — отклонение зарегистрировано в decisions_log). Соответствующий

    суррогат в alpha-пространстве: sigmoid(alpha / tau), т.к.

    sigmoid(alpha) > 0.5 <=> alpha > 0.

    """

    @staticmethod

    def forward(ctx, state, alive_channel, threshold):

        alive_hard = (torch.sigmoid(alive_channel) > threshold).float()

        ctx.save_for_backward(alive_channel)

        ctx.threshold = threshold

        return state * alive_hard

    @staticmethod

    def backward(ctx, grad_output):

        (alive_channel,) = ctx.saved_tensors

        tau = max(float(config.ALIVE_SURROGATE_TAU), 1e-6)

        soft = torch.sigmoid(alive_channel / tau)

        density = soft * (1.0 - soft) / tau

        # Floor: глубоко мёртвая клетка обязана оставаться обучаемой (§5.8).

        floor = max(float(getattr(config, "ALIVE_SURROGATE_GRAD_FLOOR", 0.0)), 0.0)

        density = torch.clamp(density, min=floor)

        # Градиент по состоянию проходит напрямую.

        # Градиент по alive-каналу — через производную мягкой маски (§5.8).

        grad_state = grad_output

        grad_alive = grad_output.mean(dim=1, keepdim=True) * density

        return grad_state, grad_alive, None

def alive_hard_mask(state):

    """Бинарная живость (B, 1, H, W): sigmoid(alive-канал) > порог."""

    alpha = state[:, config.ALIVE_CHANNEL:config.ALIVE_CHANNEL + 1, :, :]

    return (torch.sigmoid(alpha) > config.ALIVE_THRESHOLD).float()

def enforce_alive_policy(state):

    """§12.2.8: применить AliveSTE к состоянию."""

    alive_channel = state[:, config.ALIVE_CHANNEL:config.ALIVE_CHANNEL + 1, :, :]

    return AliveSTE.apply(state, alive_channel, config.ALIVE_THRESHOLD)

class NeuralCellularAutomaton(nn.Module):

    """

    [v5.6-EXP FINAL Rev.11]

    - alive_mask_enabled вместо _current_iteration;

    - life_support_mask вычисляется из pre-update state и применяется к delta;

    - мёртвая клетка без живых соседей не может самопроизвольно ожить;

    - после каждого шага применяется AliveSTE (§5.7–5.8): мёртвая клетка

      обнуляется целиком, включая стресс-канал;

    - системный стресс-канал с девиацией от EMA;

    - стресс не воскрешает мёртвые клетки;

    - поддержка режимов абляции / перемешивания / целевой ошибки / компрессии;

    - детерминированный генератор для стохастики;

    - резервирование каналов 12–14 (§3.5) и Channel Dropout (§12.1.6).

    """

    def __init__(self, channels=config.N_CHANNELS):

        super().__init__()

        self.channels = channels

        self.perception = PerceptionLayer(boundary_mode=config.BOUNDARY_MODE)

        self.brain = CellBrain(channels=channels)

        self.dt = config.DT

        # Безопасный дефолт: маска включена.

        self.alive_mask_enabled = True

        # EMA девиации — буфер модели, не параметр.

        # При загрузке старых чекпоинтов без него: инициализируется нулём.

        self.register_buffer(

            "stress_ema",

            torch.zeros(1, dtype=torch.float32),

            persistent=True,

        )

        # Детерминированный генератор может быть установлен извне.

        self.generator = None

        # [Rev.11] Целевая маска для диагностического «Оракула» (STRESS_TARGET_ERROR_MODE).

        # По умолчанию отсутствует: биологический контур не имеет доступа к цели.

        self._target_mask = None

        # [WP3] Реплей стохастики для градиентного чекпоинтинга.
        #
        # torch.utils.checkpoint при обратном проходе ПОВТОРНО выполняет forward.
        # Если стохастические маски (channel dropout, update mask, шум
        # резервирования) рисуются заново, то (а) градиент считается по ДРУГОЙ
        # реализации шума, чем прямой проход, и (б) воспроизводимость прогона
        # по §9.2 нарушается. Поэтому forward принимает noise_key: все рисования
        # одного шага кэшируются по этому ключу и на рекомпьюте берутся из
        # кэша. Ключ присваивает run_steps монотонно, т.е. он сам детерминирован.
        self._noise_cache = {}
        self._noise_key = None
        self._noise_seq = 0

    def set_generator(self, generator):

        """[Rev.11] Привязка детерминированного генератора к модели."""

        self.generator = generator

    def set_target_mask(self, target_mask):

        """

        [Rev.11] Явная передача цели для диагностического режима «Оракул».

        Вызывается ТОЛЬКО из обучающего/диагностического кода и никогда

        из экспериментального инференса (см. §6.3, STRESS_INFERENCE_LOCK).

        """

        if target_mask is not None and not isinstance(target_mask, torch.Tensor):

            raise TypeError("target_mask должен быть torch.Tensor или None.")

        self._target_mask = target_mask

    def _rand_like(self, template):

        """Стохастическая маска с учётом генератора, если он задан."""

        if self.generator is not None:

            return _rand(

                tuple(template.shape),

                generator=self.generator,

                device=template.device,

                dtype=template.dtype,

            )

        return torch.rand_like(template)

    def _draw(self, kind, shape, *, device, dtype, normal=False):

        """

        Единственная точка рисования случайных величин внутри forward (§9.2).

        Локальный генератор + реплей по noise_key (см. __init__). kind обязан

        быть уникальным в пределах одного шага.

        """
        op = _randn if normal else _rand
        key = (self._noise_key, kind)
        if self._noise_key is not None and key in self._noise_cache:
            cached = self._noise_cache[key]
            return cached.to(device=device, dtype=dtype)
        value = op(tuple(shape), generator=self.generator, device=device, dtype=dtype)
        if self._noise_key is not None:
            self._noise_cache[key] = value.detach()
        return value

    def begin_segment(self):
        """Новая серия шагов: кэш ремпья очищается, счётчик ключей сохраняется."""
        self._noise_cache = {}

    def allocate_keys(self, steps):
        base = self._noise_seq
        self._noise_seq += int(steps)
        return base

    def forward(self, state, stochastic=None, noise_key=None):

        """

        Один шаг NCA по псевдокоду §12.2.3 (без резонанса и gap junctions —

        они относятся к слоям 4–5 и запрещены §1.8 до прохода гейтов).

        Порядок: восприятие → dropout восприятия → delta → life-support → dt →

        стресс → обновление → стохастический выбор клеток → кламп →

        резервирование каналов → запись стресса → кламп → alive-политика.

        """

        if noise_key is None:
            noise_key = self.allocate_keys(1)
        self._noise_key = noise_key

        if stochastic is None:

            stochastic = config.STOCHASTIC_UPDATE_ENABLED

        # 1\. Восприятие: окрестность Мура 3×3, без обучаемых параметров.

        perception = self.perception(state)

        # 2\. Channel Dropout ТОЛЬКО на восприятие (§12.1.6). В eval-режиме

        #    выключен: оценка должна быть детерминированной, а стохастика

        #    обучения не имеет права проникать в метрики экспериментов.

        if self.training and config.CHANNEL_DROPOUT_ENABLED:
            n_drop = len([c for c in config.CHANNEL_DROPOUT_CHANNELS if 0 <= int(c) < self.channels])
            draws = self._draw("channel_dropout", (n_drop,), device="cpu", dtype=torch.float32)
            perception = apply_channel_dropout(perception, self.generator, draws=draws)

        # 3\. Модель клетки.

        raw_delta = self.brain(perception)

        update = torch.tanh(raw_delta)

        # === ВАЖНО [v5.6]: life_support_mask считается ДО обновления. ===

        # Это запрещает самовоскрешение из пустоты.

        # Маска вычисляется ВСЕГДА, даже при STRESS_ABLATION_MODE=True.

        life_support_mask = self._life_support_mask(state)

        if self.alive_mask_enabled:

            update = update * life_support_mask

        local_dt = self._resolve_dt(state, life_support_mask, update)

        # === Системное обновление стресс-канала (шаг 6 §12.2.3). ===

        stress_new = self._update_stress(state, life_support_mask, update)

        # 4\. Обновление состояния.

        new_state = state + local_dt * update

        # 5\. Стохастическое обновление (§4.5 Rev.11): mask выбирает КЛЕТКИ,

        #    которые вообще обновляются на этом шаге:

        #      new_state = torch.where(update_mask, new_state, state).

        #    Раньше вместо этого обнулялась дельта с вероятностью UPDATE_PROB,

        #    что семантически отличалось от «клетка не обновилась» и путало

        #    frac_delta_nonzero с плотностью обновлений.

        # [Rev.11] §4.5: не зависит от self.training — иначе поведение на

        # обучении и в экспериментах расходится при одном и том же сиде.

        if stochastic and config.STOCHASTIC_UPDATE_ENABLED:

            update_mask = self._generate_update_mask(state, new_state)

            new_state = torch.where(update_mask, new_state, state)

        # 10\. Кламп (§3.7).

        new_state = torch.clamp(

            new_state,

            config.STATE_CLAMP_MIN,

            config.STATE_CLAMP_MAX,

        )

        # Резервирование каналов 12–14 (§3.5) — только на обучении.

        new_state = self._apply_channel_reservation(new_state)

        # Канал 15 перезаписывается системным значением стресса.

        new_state = new_state.clone()

        new_state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1] = stress_new

        new_state = torch.clamp(

            new_state,

            config.STATE_CLAMP_MIN,

            config.STATE_CLAMP_MAX,

        )

        # 11\. Alive-политика и смерть-инвариант (§5.7–5.8, §12.2.8):

        # мёртвая клетка обнуляется ЦЕЛИКОМ, включая стресс-канал.

        if self.alive_mask_enabled:

            new_state = enforce_alive_policy(new_state)

        return new_state

    def _generate_update_mask(self, state, template):

        """

        §4.5: булева маска клеток, обновляемых на этом шаге (доля UPDATE_FRACTION).

        Форма (B, 1, H, W) — решение принимается на клетку, а не на канал.

        """

        b, _c, h, w = state.shape

        draws = self._draw(
            "update_mask",
            (b, 1, h, w),
            device=template.device,
            dtype=template.dtype,
        )

        return draws < config.UPDATE_FRACTION

    def _apply_channel_reservation(self, state):

        """

        §3.5: резервирование каналов 12–14 во время обучения базовой модели.

        Каналы остаются доступными для ЧТЕНИЯ (это требование §12.6.8), но

        случайно зануляются с вероятностью ENTRAINMENT_CHANNEL_DROPOUT_PROB

        и получают ограниченный шум — так модель не может сделать из них

        основную память целевой формы, и E08 останется измеримым.

        Только self.training: на инференсе состояние обязано быть детерминированным.

        """

        if not config.ENTRAINMENT_CHANNEL_RESERVATION_ENABLED or not self.training:

            return state

        reserved = [int(c) for c in config.ENTRAINMENT_CHANNELS if 0 <= int(c) < self.channels]

        if not reserved:

            return state

        draws = self._draw(
            "reservation_keep",
            (len(reserved),),
            device="cpu",
            dtype=torch.float32,
        )

        dropped = (draws < config.ENTRAINMENT_CHANNEL_DROPOUT_PROB)

        keep = torch.ones(self.channels, device=state.device, dtype=state.dtype)

        for pos, channel in enumerate(reserved):

            if bool(dropped[pos]):

                keep[channel] = 0.0

        state = state * keep.view(1, -1, 1, 1)

        std = float(config.ENTRAINMENT_CHANNEL_NOISE_STD)

        if std > 0.0:

            noise = torch.zeros_like(state)

            for pos, channel in enumerate(reserved):

                if bool(dropped[pos]):

                    continue  # занулённый канал не нужно ещё и зашумлять

                noise[:, channel:channel + 1] = self._draw(
                    f"reservation_noise:{channel}",
                    tuple(state[:, channel:channel + 1].shape),
                    device=state.device,
                    dtype=state.dtype,
                    normal=True,
                ) * std

            state = state + noise

        return state

    def _resolve_dt(self, state, life_support_mask, update):

        """

        Вычисляет локальный эффективный шаг времени.

        При стрессе: локальный рост не более +STRESS_TEMP_SCALE.

        Реальный масштаб эффекта — информационный, не темпоральный.

        """

        stress_active = (

            config.STRESS_ENABLED

            and config.STRESS_AFFECTS_DT

            and not config.STRESS_ABLATION_MODE

        )

        if not stress_active:

            return float(self.dt)

        stress_old = state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1]

        stress_norm = stress_old / config.STRESS_MAX

        local_dt_tensor = float(self.dt) * (

            1.0 + config.STRESS_TEMP_SCALE * stress_norm

        )

        min_dt = min(float(self.dt), float(config.DT_MAX_EFFECTIVE))

        local_dt = torch.clamp(

            local_dt_tensor,

            min_dt,

            config.DT_MAX_EFFECTIVE,

        )

        return local_dt

    def _update_stress(self, state, life_support_mask, update):

        """

        Системное обновление стресс-канала [v5.6 Rev.11].

        Всегда возвращает тензор стресса формы (B, 1, H, W).

        При абляции или отключении — нули.

        """

        stress_shape = state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1].shape

        stress_active = config.STRESS_ENABLED and not config.STRESS_ABLATION_MODE

        if not stress_active:

            return torch.zeros(stress_shape, device=state.device, dtype=state.dtype)

        with torch.no_grad():

            # 1\. Дельта для стресса:

            #    - уже маскирована по life_support_mask (мёртвые не считаются);

            #    - канал 15 исключён, чтобы стресс не разгонял сам себя.

            delta_masked = update * life_support_mask.float()

            delta_for_stress = delta_masked.clone()

            delta_for_stress[:, config.STRESS_CHANNEL, :, :] = 0.0

            delta_norm = delta_for_stress.abs().mean(dim=1, keepdim=True)

            # 2\. EMA девиации (обновляется каждый шаг по умолчанию).

            self.stress_ema = (

                config.STRESS_EMA_ALPHA * self.stress_ema

                + (1.0 - config.STRESS_EMA_ALPHA) * delta_norm.mean()

            ).detach()

            # 3\. Источник стресса.

            if config.STRESS_TARGET_ERROR_MODE:

                stress_source = self._local_target_error(state, life_support_mask)

            else:

                stress_source = torch.clamp(

                    delta_norm - self.stress_ema,

                    0.0,

                    config.STRESS_MAX,

                )

            # 3b. Опциональная компрессия входа.

            if config.STRESS_COMPRESS_INPUT:

                stress_source = torch.log1p(stress_source)

                stress_source = torch.clamp(stress_source, 0.0, config.STRESS_MAX)

            # 4\. Опциональное разрушение пространственной информации.

            if config.STRESS_SHUFFLE_MODE:

                stress_source = self._spatial_shuffle(stress_source)

            # 5\. Затухание + вход.

            stress = state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1]

            stress = stress * (1.0 - config.STRESS_DECAY)

            stress = stress + config.STRESS_INPUT_GAIN * stress_source

            # 6\. Диффузия с reflect-паддингом (биологическая ткань не обрывается).

            stress = stress + config.STRESS_DIFFUSION * (self._blur_reflect(stress) - stress)

            # 7\. Ограничения и мёртвые клетки.

            stress = torch.clamp(stress, 0.0, config.STRESS_MAX)

            stress = stress * life_support_mask.float()

        return stress

    def _local_target_error(self, state, life_support_mask):

        """

        Диагностический режим: стресс из локальной ошибки относительно цели.

        Использует знание цели, поэтому НЕ считается биологически достоверным.

        Возвращает тензор той же формы, что и стресс.

        [Rev.11] «Оракул» требует ЯВНО переданной целевой маски. Молчаливый

        откат на девиационный источник запрещён: режим и так помечен как

        небиологический, а подмена источника стресса внутри него делала

        абляцию нечитаемой (в базлайне `_target_mask` не выставлялся нигде).

        """

        # Целевая маска может быть установлена извне (например, из когнитивного цикла).

        target = getattr(self, "_target_mask", None)

        if target is None:

            raise RuntimeError(

                "STRESS_TARGET_ERROR_MODE=True, но целевая маска не передана "

                "в model.set_target_mask(...). Диагностический «Оракул» требует "

                "явного знания цели; включите STRESS_TARGET_ERROR_MODE=False, "

                "если нужен биологический девиационный источник стресса."

            )

        # Бинарная текущая маска (единое правило).

        alpha = torch.sigmoid(state[:, config.ALIVE_CHANNEL:config.ALIVE_CHANNEL + 1])

        visible = state[:, config.VISIBLE_CHANNEL:config.VISIBLE_CHANNEL + 1]

        if config.USE_SIGMOID_VISIBLE:

            visible = torch.sigmoid(visible)

        current_mask = ((alpha > config.ALIVE_THRESHOLD) & (visible > config.BINARY_THRESHOLD)).float()

        target_mask = target.to(state.device).float()

        if target_mask.dim() == 3:

            target_mask = target_mask.unsqueeze(0)

        if target_mask.shape[1] != 1:

            target_mask = target_mask[:, :1]

        target_mask = target_mask.expand(current_mask.shape[0], -1, -1, -1)

        mismatch = (current_mask - target_mask).abs()

        # Сглаженный локальный сигнал ошибки.

        error_field = self._blur_reflect(mismatch)

        error_field = torch.clamp(error_field * config.STRESS_MAX, 0.0, config.STRESS_MAX)

        return error_field

    def _spatial_shuffle(self, x):

        """

        Пространственное перемешивание для диагностического режима.

        Глобальная статистика сохраняется, локальная структура разрушается.

        """

        B, C, H, W = x.shape

        flat = x.reshape(B, C, H * W)

        if self.generator is not None:

            idx = _randperm(H * W, generator=self.generator, device=x.device)

        else:

            idx = torch.randperm(H * W, device=x.device)

        shuffled = flat[:, :, idx]

        return shuffled.reshape(B, C, H, W)

    def _life_support_mask(self, state):

        """

        life_support_mask: клетка жива ИЛИ имеет живого соседа.

        Вычисляется из pre-update state.

        """

        alive_binary = alive_hard_mask(state)

        has_alive_neighbor = F.max_pool2d(

            alive_binary,

            kernel_size=3,

            stride=1,

            padding=1,

        )

        alive = torch.clamp(alive_binary + has_alive_neighbor, 0, 1)

        return alive

    def _alive_mask(self, state):

        """Совместимый алиас для внешних вызовов."""

        return self._life_support_mask(state)

    def _blur_reflect(self, x):

        """

        Сглаживание 3×3 для диффузии стресса.

        ВАЖНО [v5.6]: используется reflect-паддинг, чтобы края не были стоками.

        """

        weight = torch.ones(1, 1, 3, 3, device=x.device, dtype=x.dtype) / 9.0

        padded = F.pad(x, (1, 1, 1, 1), mode="reflect")

        return F.conv2d(padded, weight, padding=0)

    def visible_image(self, state):

        image = state[:, config.VISIBLE_CHANNEL:config.VISIBLE_CHANNEL + 1, :, :]

        if config.USE_SIGMOID_VISIBLE:

            image = torch.sigmoid(image)

        return image

    def get_delta(self, state):

        """

        Используется для L1-регуляризации.

        Возвращает базовый масштабированный градиент динамики без стресс-модуляции.

        """

        local_view = self.perception(state)

        delta = self.brain(local_view)

        return self.dt * torch.tanh(delta)

def run_steps(model, state, steps):
    """
    Серия шагов с градиентами.

    Ключи стохастики выделяются СЮДА, а не рисуются внутри forward: при
    torch.utils.checkpoint forward выполняется дважды (прямой проход и рекомпьют
    на backward), и без внешнего ключа маски обновлений/dropout/шума
    перерисовывались бы заново — градиент считался бы по другой реализации шума,
    а воспроизводимость прогона (§9.2) терялась бы.
    """
    use_checkpoint = bool(getattr(config, "GRAD_CHECKPOINTING", True))
    if hasattr(model, "begin_segment"):
        model.begin_segment()
    base = model.allocate_keys(steps) if hasattr(model, "allocate_keys") else None
    for i in range(steps):
        key = None if base is None else base + i
        if torch.is_grad_enabled() and use_checkpoint:
            state = grad_checkpoint(model, state, None, key, use_reentrant=False)
        elif key is None:
            state = model(state)
        else:
            state = model(state, noise_key=key)
    return state

def run_steps_no_grad(model, state, steps):

    with torch.no_grad():

        for _ in range(steps):

            state = model(state)

    return state

def _guarantee_alive(state, generator=None):

    """

    Гарантирует, что свежее состояние содержит >= FRESH_MIN_ALIVE_FRACTION

    живых клеток. sigmoid(0) = 0.5, а порог строгий >, поэтому нулевой

    альфа-канал означает смерть. Мы явно смещаем альфа-канал.

    """

    B, C, H, W = state.shape

    alpha = state[:, config.ALIVE_CHANNEL, :, :]

    alive_prob = torch.sigmoid(alpha)

    alive_fraction = float((alive_prob > config.ALIVE_THRESHOLD).float().mean().item())

    if alive_fraction >= config.FRESH_MIN_ALIVE_FRACTION:

        return state

    # Принудительно делаем часть клеток живыми.

    # Случайная маска с долей, заведомо выше порога.

    target_fraction = max(config.FRESH_MIN_ALIVE_FRACTION + 0.20, 0.40)

    if generator is not None:

        rand_mask = _rand(

            (B, H, W),

            generator=generator,

            device=state.device,

            dtype=state.dtype,

        )

    else:

        rand_mask = torch.rand(B, H, W, device=state.device, dtype=state.dtype)

    live = (rand_mask < target_fraction).float()

    # Живые клетки: положительное значение альфа. Мёртвые: отрицательное.

    new_alpha = torch.where(

        live > 0.5,

        torch.full_like(alpha, 2.0),

        torch.full_like(alpha, -2.0),

    )

    state = state.clone()

    state[:, config.ALIVE_CHANNEL, :, :] = new_alpha

    return state

def init_state(

    batch_size=config.EVAL_BATCH_SIZE,

    channels=config.N_CHANNELS,

    grid_size=config.GRID_SIZE,

    noise_level=None,

    device=config.DEVICE,

    generator=None,

):

    """

    Инициализация состояния.

    - Шум по всем каналам с уровнем INIT_NOISE_LEVEL.

    - Альфа-канал гарантирует >= FRESH_MIN_ALIVE_FRACTION живых клеток.

    - Канал 15 инициализируется нулями.

    """

    if noise_level is None:

        noise_level = config.INIT_NOISE_LEVEL

    if generator is not None:

        state = _randn(

            (batch_size, channels, grid_size, grid_size),

            generator=generator,

            device=device,

        ) * noise_level

    else:

        state = torch.randn(

            batch_size,

            channels,

            grid_size,

            grid_size,

            device=device,

        ) * noise_level

    state = _guarantee_alive(state, generator=generator)

    # Системный стресс-канал всегда стартует с нуля.

    state[:, config.STRESS_CHANNEL, :, :] = 0.0

    return state

def target_conditioned_state(
    target,
    batch_size=config.EVAL_BATCH_SIZE,
    channels=config.N_CHANNELS,
    grid_size=config.GRID_SIZE,
    device=config.DEVICE,
    logit_scale=4.0,
):
    """

    Диагностическое состояние для TRAIN_POOL_INIT_MODE="target" (WP4).

    Видимый канал равен ЦЕЛИ (насыщенный логит: sigmoid(+-4) = 0.982/0.018),
    альфа-канал положителен ВЕЗДЕ (живы все клетки — иначе нарушение ПРАВИЛА 31,
    у цели ring плотность 0.1523 < FRESH_MIN_ALIVE_FRACTION=0.20), скрытые
    каналы и канал стресса обнулены.

    Зачем: аблации H-K1/H-K2/H-N1 показали, что visible_mse встаёт на аналитическом
    плато почти-чёрного поля с grad_norm ~0.004. Этим состоянием отделяется вопрос
    «способна ли архитектура представить и УДЕРЖАТЬ кольцо» от вопроса «способна ли
    она вырастить кольцо из шума за горизонт BPTT». Шум здесь отсутствует намеренно:
    детерминированность (§9.2) требует, чтобы прогон был воспроизводим без генератора.

    """

    state = torch.zeros(batch_size, channels, grid_size, grid_size, device=device)

    mask = (target > 0).to(state.dtype)

    if mask.ndim == 3:

        # (B, H, W) -> (B, 1, H, W) для broadcast по каналам.

        mask = mask.unsqueeze(1)

    state[:, config.VISIBLE_CHANNEL, :, :] = logit_scale * (2.0 * mask[:, 0] - 1.0)

    state[:, config.ALIVE_CHANNEL, :, :] = logit_scale

    state[:, config.STRESS_CHANNEL, :, :] = 0.0

    return state

def _validate_fresh_state(state):

    """

    ПРАВИЛО 31: свежие состояния обязаны содержать живые клетки.

    Иначе в момент включения маски вся сетка мертва навсегда.

    """

    alive_fraction = float(

        (torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :]) > config.ALIVE_THRESHOLD)

        .float()

        .mean()

        .item()

    )

    assert alive_fraction >= config.FRESH_MIN_ALIVE_FRACTION, (

        f"Fresh state has {alive_fraction:.2%} alive cells, "

        f"need >= {config.FRESH_MIN_ALIVE_FRACTION:.2%}"

    )

    return True

class StatePool:

    """

    Пул состояний.

    [v5.6 Rev.11]: поддерживает детерминированный генератор.

    """

    def __init__(

        self,

        size=config.TRAIN_SAMPLE_POOL_SIZE,

        device=config.DEVICE,

        generator=None,

        batch_size=config.TRAIN_BATCH_SIZE,

        fresh_fn=None,

    ):

        self.size = size

        self.device = device

        self.generator = generator

        self.batch_size = int(batch_size)

        # [WP4] fresh_fn задаёт, чем наполняется пул при сбросе. По умолчанию —
        # шум init_state (§14.2 «расти из шума»). train.py подставляет
        # target_conditioned_state, когда TRAIN_POOL_INIT_MODE="target": иначе
        # периодический сброс (ПРАВИЛО 29) молча вернул бы шум и диагноз
        # «архитектура не может» перепутался бы с «не успела вырасти».
        self.fresh_fn = fresh_fn

        self.states = [

            self._fresh_state()

            for _ in range(size)

        ]

        self.ages = [0] * size

        # [Rev.11] Счётчик шагов симуляции для ПРАВИЛА 29 (привязка сброса к sim_step).

        self.last_reset_sim_step = 0

    def set_generator(self, generator):

        self.generator = generator

    def sample(self):

        """Возвращает (state, index)."""

        if self.generator is not None:

            index = int(torch.randint(0, self.size, (1,), generator=self.generator).item())

        else:

            index = int(torch.randint(0, self.size, (1,)).item())

        self.ages[index] += 1

        return self.states[index], index

    def update(self, state, index):

        """Обновляет состояние по индексу."""

        self.states[index] = state.detach()

    def _fresh_state(self):

        if self.fresh_fn is not None:

            state = self.fresh_fn()

        else:

            state = init_state(

                batch_size=self.batch_size,

                device=self.device,

                generator=self.generator,

            )

        _validate_fresh_state(state)

        return state

    def replace_with_fresh(self, index):

        """Заменяет состояние свежим шумом (например, при NaN/OOM)."""

        self.states[index] = self._fresh_state()

        self.ages[index] = 0

    def replace_all_fresh(self):

        """Полный сброс пула свежим шумом."""

        for i in range(self.size):

            self.states[i] = self._fresh_state()

            self.ages[i] = 0

    def maybe_reset(self, sim_step):

        """

        Периодический сброс.

        ПРАВИЛО 29 [Rev.11]: привязка к sim_step, а не к step.

        sim_step — накопленное число шагов симуляции (unroll-ы), а не номер

        итерации оптимизатора. Сброс happens не чаще STATE_RESET_EVERY

        шагов симуляции.

        """

        sim_step = int(sim_step)

        due = sim_step - self.last_reset_sim_step >= config.STATE_RESET_EVERY

        if due:

            self.replace_all_fresh()

            self.last_reset_sim_step = sim_step

        # Страхующий сброс пересидевших слотов (защита от застоя пула).

        for i in range(self.size):

            if self.ages[i] >= config.STATE_RESET_EVERY:

                self.states[i] = self._fresh_state()

                self.ages[i] = 0

        if self.generator is not None:

            r = torch.rand(1, generator=self.generator).item()

        else:

            r = torch.rand(1).item()

        if r < config.STATE_RESET_PROB:

            if self.generator is not None:

                i = int(torch.randint(0, self.size, (1,), generator=self.generator).item())

            else:

                i = int(torch.randint(0, self.size, (1,)).item())

            self.states[i] = self._fresh_state()

            self.ages[i] = 0

    def state_dict(self):

        return {

            "states": [s.cpu() for s in self.states],

            "ages": self.ages,

            "last_reset_sim_step": int(self.last_reset_sim_step),

        }

    def load_state_dict(self, state_dict):

        for i, s in enumerate(state_dict["states"]):

            self.states[i] = s.to(self.device)

        self.ages = state_dict["ages"]

        # [Rev.11] Старые чекпоинты могут не содержать счётчик — это совместимо.

        self.last_reset_sim_step = int(state_dict.get("last_reset_sim_step", 0))
