"""

nca_core.py — Ядро Нейроклеточного Автомата.

[v5.5-EXP FINAL] Rev.7

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

import torch

import torch.nn as nn

import torch.nn.functional as F

from torch.utils.checkpoint import checkpoint as grad_checkpoint

import config

class PerceptionLayer(nn.Module):

    def __init__(self, channels, boundary_mode="constant"):

        super().__init__()

        self.boundary_mode = boundary_mode

        self.conv = nn.Conv2d(

            channels,

            channels,

            kernel_size=3,

            padding=0,

            bias=True,

        )

        nn.init.xavier_uniform_(self.conv.weight, gain=0.1)

        nn.init.zeros_(self.conv.bias)

    def forward(self, state):

        if self.boundary_mode == "circular":

            padded = F.pad(state, (1, 1, 1, 1), mode="circular")

        else:

            # ПРАВИЛО 23: восприятие использует constant.

            padded = F.pad(state, (1, 1, 1, 1), mode="constant", value=0)

        return self.conv(padded)

class CellBrain(nn.Module):

    """

    Последний слой инициализируется НУЛЯМИ — система стартует из покоя.

    """

    def __init__(self, channels, hidden=64):

        super().__init__()

        self.net = nn.Sequential(

            nn.Conv2d(channels, hidden, kernel_size=1),

            nn.ReLU(),

            nn.Conv2d(hidden, hidden, kernel_size=1),

            nn.ReLU(),

            nn.Conv2d(hidden, channels, kernel_size=1),

        )

        nn.init.zeros_(self.net[-1].weight)

        nn.init.zeros_(self.net[-1].bias)

    def forward(self, local_view):

        return self.net(local_view)

class NeuralCellularAutomaton(nn.Module):

    """

    [v5.5-EXP FINAL Rev.7]

    - alive_mask_enabled вместо _current_iteration;

    - life_support_mask вычисляется из pre-update state и применяется к delta;

    - мёртвая клетка без живых соседей не может самопроизвольно ожить;

    - системный стресс-канал с девиацией от EMA;

    - стресс не воскрешает мёртвые клетки;

    - поддержка режимов абляции / перемешивания / целевой ошибки / компрессии;

    - детерминированный генератор для стохастики.

    """

    def __init__(self, channels=config.N_CHANNELS):

        super().__init__()

        self.channels = channels

        self.perception = PerceptionLayer(

            channels,

            boundary_mode=config.BOUNDARY_MODE,

        )

        self.brain = CellBrain(channels)

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

    def set_generator(self, generator):

        """[Rev.7] Привязка детерминированного генератора к модели."""

        self.generator = generator

    def _rand_like(self, template):

        """Стохастическая маска с учётом генератора, если он задан."""

        if self.generator is not None:

            return torch.rand(

                template.shape,

                generator=self.generator,

                device=template.device,

                dtype=template.dtype,

            )

        return torch.rand_like(template)

    def forward(self, state, stochastic=None):

        if stochastic is None:

            stochastic = config.STOCHASTIC_UPDATE

        local_view = self.perception(state)

        raw_delta = self.brain(local_view)

        base_delta = torch.tanh(raw_delta)

        update = base_delta

        if stochastic and self.training:

            random_mask = (self._rand_like(update) < config.UPDATE_PROB).float()

            update = update * random_mask

        # === ВАЖНО [v5.5]: life_support_mask считается ДО обновления. ===

        # Это запрещает самовоскрешение из пустоты.

        # Маска вычисляется ВСЕГДА, даже при STRESS_ABLATION_MODE=True.

        life_support_mask = self._life_support_mask(state)

        if self.alive_mask_enabled:

            update = update * life_support_mask

        local_dt = self._resolve_dt(state, life_support_mask, update)

        # === Системное обновление стресс-канала. ===

        stress_new = self._update_stress(state, life_support_mask, update)

        new_state = state + local_dt * update

        new_state = torch.clamp(

            new_state,

            config.STATE_CLAMP_MIN,

            config.STATE_CLAMP_MAX,

        )

        # Канал 15 перезаписывается системным значением стресса.

        new_state = new_state.clone()

        new_state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1] = stress_new

        new_state = torch.clamp(

            new_state,

            config.STATE_CLAMP_MIN,

            config.STATE_CLAMP_MAX,

        )

        return new_state

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

        Системное обновление стресс-канала [v5.5 Rev.7].

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

        """

        # Целевая маска может быть установлена извне (например, из когнитивного цикла).

        target = getattr(self, "_target_mask", None)

        if target is None:

            # Нет цели — падаем в девиационный источник.

            delta_masked = (state * life_support_mask.float())

            delta_for_stress = delta_masked.clone()

            delta_for_stress[:, config.STRESS_CHANNEL, :, :] = 0.0

            delta_norm = delta_for_stress.abs().mean(dim=1, keepdim=True)

            return torch.clamp(delta_norm - self.stress_ema, 0.0, config.STRESS_MAX)

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

            idx = torch.randperm(H * W, generator=self.generator, device=x.device)

        else:

            idx = torch.randperm(H * W, device=x.device)

        shuffled = flat[:, :, idx]

        return shuffled.reshape(B, C, H, W)

    def _life_support_mask(self, state):

        """

        life_support_mask: клетка жива ИЛИ имеет живого соседа.

        Вычисляется из pre-update state.

        """

        alpha = state[:, config.ALIVE_CHANNEL:config.ALIVE_CHANNEL + 1, :, :]

        alpha_prob = torch.sigmoid(alpha)

        alive_binary = (alpha_prob > config.ALIVE_THRESHOLD).float()

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

        ВАЖНО [v5.5]: используется reflect-паддинг, чтобы края не были стоками.

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

    for _ in range(steps):

        if torch.is_grad_enabled():

            state = grad_checkpoint(model, state, use_reentrant=False)

        else:

            state = model(state)

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

        rand_mask = torch.rand(

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

    batch_size=config.BATCH_SIZE,

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

        state = torch.randn(

            batch_size,

            channels,

            grid_size,

            grid_size,

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

    [v5.5 Rev.7]: поддерживает детерминированный генератор.

    """

    def __init__(self, size=config.STATE_POOL_SIZE, device=config.DEVICE, generator=None):

        self.size = size

        self.device = device

        self.generator = generator

        self.states = [init_state(device=device, generator=generator) for _ in range(size)]

        self.ages = [0] * size

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

        state = init_state(device=self.device, generator=self.generator)

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

        ПРАВИЛО 29: привязка к sim_step, а не к step.

        """

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

        }

    def load_state_dict(self, state_dict):

        for i, s in enumerate(state_dict["states"]):

            self.states[i] = s.to(self.device)

        self.ages = state_dict["ages"]