"""

config.py — ВСЕ гиперпараметры проекта.

Агент: НИКОГДА не хардкодь параметры в других файлах.

Меняй значения ТОЛЬКО здесь.

[v5.5-EXP FINAL] Rev.7

"""

import torch

import numpy as np

import random

import math

from datetime import datetime

# === ЖЕЛЕЗО ===

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MAX_VRAM_GB = 8

# === ВОСПРОИЗВОДИМОСТЬ ===

SEED = 42

CUDNN_BENCHMARK = False

# === СЕТКА ===

GRID_SIZE = 64

N_CHANNELS = 16

BATCH_SIZE = 2

# ВАЖНО [v5.5]:

# Используем constant / zero-padding для восприятия и alive-маски,

# чтобы физика NCA и топологический мониторинг через scipy.ndimage были согласованы.

# Для диффузии стресса отдельно используется reflect-паддинг (см. nca_core.py).

BOUNDARY_MODE = "constant"

# === ВРЕМЯ ===

UNROLL_STEPS = 10

if BATCH_SIZE == 1:

    UNROLL_CURRICULUM = [10, 15, 20]

else:

    UNROLL_CURRICULUM = [10, 10, 10]

UNROLL_CURRICULUM_AT = [0, 800, 1600]

TOTAL_TRAIN_ITERS = 2000

DT = 0.1

# === ОБУЧЕНИЕ ===

LEARNING_RATE = 1e-3

WEIGHT_DECAY = 1e-5

GRAD_CLIP = 1.0

L1_REG_WEIGHT = 0.001

LR_SCHEDULER = "cosine"

# === ПУЛ СОСТОЯНИЙ ===

STATE_POOL_SIZE = 4

STATE_RESET_EVERY = 200

STATE_RESET_PROB = 0.01

# === СТОХАСТИКА И ALIVE-МАСКА ===

STOCHASTIC_UPDATE = True

UPDATE_PROB = 0.5

# ВАЖНО:

# Порог жизни равен 0.5.

# sigmoid(0) = 0.5, а условие строго больше, поэтому обнулённая клетка мертва.

ALIVE_THRESHOLD = 0.5

ALIVE_CHANNEL = 1

ALIVE_WARMUP_ITERS = 50

DEAD_ALPHA_VALUE = -10.0

# Минимальная доля живых клеток в свежем состоянии пула.

FRESH_MIN_ALIVE_FRACTION = 0.20

# === ВИДИМЫЙ КАНАЛ ===

VISIBLE_CHANNEL = 0

USE_SIGMOID_VISIBLE = True

# === ОГРАНИЧЕНИЕ СОСТОЯНИЯ ===

STATE_CLAMP_MIN = -3.0

STATE_CLAMP_MAX = 3.0

# === ТОПОЛОГИЯ (ТОЛЬКО МОНИТОРИНГ) ===

BINARY_THRESHOLD = 0.5

TARGET_COMPONENTS = 3

CONNECTIVITY = 2

MIN_CLUSTER_SIZE = 4

LYAPUNOV_MIN_DIST = 1e-8

# === ЦЕЛЕВАЯ ТОПОЛОГИЯ ===

# Для трёх кругов: β₀ = 3, β₁ = 0, χ = 3

TARGET_TOPOLOGY = {

    "b0": 3,

    "b1": 0,

    "chi": 3,

}

TOPOLOGY_TOLERANCE_B0 = 1

TOPOLOGY_TOLERANCE_B1 = 0

# === ПОРОГИ ГАЛЛЮЦИНАЦИЙ ===

# Нормировка порогов (Rev.7):

# MSE_HALLUCINATION_THRESHOLD относится к MSE, усреднённому по всем пикселям

# и супервизируемым каналам (видимый + альфа):

#   mse = F.mse_loss(pred, target, reduction='mean')

# При изменении числа супервизируемых каналов порог должен быть пересчитан.

MSE_HALLUCINATION_THRESHOLD = 0.05

# SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD относится к нормированному значению:

#   symmetric_chamfer_error = raw_chamfer / (GRID_SIZE * sqrt(2))

# То есть порог масштабно-инвариантен и не «плывёт» при смене GRID_SIZE.

SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD = 0.10

# Гистерезис: флаг галлюцинации активен только при удержании условия

# в течение HALLUCINATION_PERSISTENCE отчётов подряд.

HALLUCINATION_PERSISTENCE = 3

# === СТРЕСС-КАНАЛ И СТРЕСС-ШЕРИНГ [v5.5] ===

# Канал 15 — системный стресс-канал. НЕ доступен для INJECT_MORPHOGEN.

STRESS_ENABLED = True

STRESS_CHANNEL = 15

RESERVED_SYSTEM_CHANNELS = [STRESS_CHANNEL]

# ВАЖНО [v5.5]: gain снижен с 1.0 до 0.15.

# Стационарное решение s* = GAIN * x / DECAY.

# При GAIN=1.0, DECAY=0.05 коэффициент усиления = 20 → насыщение.

# При GAIN=0.15 коэффициент усиления = 3 → рабочий диапазон.

STRESS_INPUT_GAIN = 0.15

STRESS_DECAY = 0.05

STRESS_DIFFUSION = 0.20

STRESS_MAX = 3.0

# Если True, высокий стресс слегка повышает локальный эффективный dt.

# Реальный масштаб: при DT=0.1 и STRESS_TEMP_SCALE=0.10 рост ≤ +10%.

# Это преимущественно информационный (входной), а не темпоральный эффект.

STRESS_AFFECTS_DT = True

STRESS_TEMP_SCALE = 0.10

DT_MAX_EFFECTIVE = 0.5

# EMA для разрыва петли стресс→DT→стресс.

# При обновлении каждый шаг и α=0.95 эффективное окно ≈ 20 шагов.

STRESS_EMA_ALPHA = 0.95

# Режимы абляции / диагностики.

STRESS_ABLATION_MODE = False

STRESS_SHUFFLE_MODE = False

STRESS_TARGET_ERROR_MODE = False

# Rev.7: опциональная логарифмическая компрессия входа стресса.

STRESS_COMPRESS_INPUT = False

# === ИНИЦИАЛИЗАЦИЯ И КОГНИТИВНЫЙ КОНТУР ===

INIT_NOISE_LEVEL = 0.95

# Rev.7: переименовано из MAX_CONTINUE_STEPS.

MAX_EXTRA_STEPS_PER_REPORT = 500

COGNITION_STEP_SIZE = 10

# Минимальный обязательный интервал отчётов: 2 * STEP_SIZE = 20\.

COGNITION_REPORT_INTERVAL = 20

# === МОРФОГЕНЕТИЧЕСКИЕ ВМЕШАТЕЛЬСТВА ===

# Канал 15 зарезервирован под стресс. Морфогены доступны только в каналах 2–14.

MORPHOGEN_MIN_CHANNEL = 2

MORPHOGEN_MAX_CHANNEL = 14

MORPHOGEN_MIN_RADIUS = 1

MORPHOGEN_MAX_RADIUS = 16

MORPHOGEN_MIN_VALUE = -3.0

MORPHOGEN_MAX_VALUE = 3.0

# === ЭКОНОМИКА ВМЕШАТЕЛЬСТВ [v5.5] ===

# АТР-бюджет: сколько стоимости действий доступно за один отчёт.

INTERVENTION_BUDGET_PER_REPORT = 2.0

# Кулдаун морфогена.

# Условие разрешения: (current_report - last_morphogen_report) > COOLDOWN.

MORPHOGEN_COOLDOWN_REPORTS = 1

MORPHOGEN_MAX_INJECTIONS_PER_REPORT = 1

MORPHOGEN_MAX_DOSE_PER_REPORT = 1.0

MORPHOGEN_MIN_EFFECT_THRESHOLD = 0.005

# Utility-штраф в скоре агента, а не жёсткий бюджет.

INTERVENTION_COST_WEIGHT = 0.1

# Травма вне АТР-бюджета, но с глобальным кулдауном.

INJURY_COOLDOWN_REPORTS = 5

# Rev.7: формула полезности против доминирования бесплатного CONTINUE_TRAINING.

MIN_UTILITY_THRESHOLD = 0.005

MAX_CONSECUTIVE_CONTINUE = 5

KNOWN_ACTIONS = (

    "MODIFY_DT",

    "MODIFY_LR",

    "MODIFY_L1_REG",

    "MODIFY_TARGET_B0",

    "CONTINUE_TRAINING",

    "APPLY_INJURY",

    "INJECT_MORPHOGEN",

    "STOP",

)

ACTION_COSTS = {

    "CONTINUE_TRAINING": 0.0,

    "MODIFY_DT": 0.10,

    "MODIFY_LR": 0.10,

    "MODIFY_L1_REG": 0.10,

    "MODIFY_TARGET_B0": 0.20,

    "INJECT_MORPHOGEN": 0.5,

    "APPLY_INJURY": 0.0,

    "STOP": 0.0,

}

# === GRACE WINDOW / MAINTENANCE ===

GRACE_WINDOW = 30

MINI_MAINTENANCE_STEPS = 30

MAINTENANCE_WINDOW = 200

# === СТАРЕНИЕ / ОМОЛОЖЕНИЕ [v5.5] ===

AGING_STEPS = 1000

AGING_NOISE_STD = 0.01

# Обязательный sweep по шуму в E05.

AGING_NOISE_SWEEP = [0.01, 0.05, 0.1]

AGING_NOISE_CHANNELS = list(range(2, 15))  # скрытые каналы 2–14, без 15

# Пре-регистрированные пороги деградации и восстановления.

AGING_DEGRADATION_THRESHOLD_B0 = 2

AGING_DEGRADATION_THRESHOLD_ENTROPY = 0.15

AGING_RECOVERY_THRESHOLD = 0.8

REJUVENATION_ENTROPY_INCREASE = 0.15

REJUVENATION_B0_ERROR = 2

# === КРИТИЧНОСТЬ [v5.5] ===

CRITICALITY_SCAN_ENABLED = True

CRITICALITY_MAX_CONFIGS = 12

CRITICALITY_STEPS = 100

# Показатель Ляпунова: целевой критический коридор.

CRITICALITY_LYAPUNOV_MIN = -0.01

CRITICALITY_LYAPUNOV_MAX = 0.01

SENSITIVITY_MIN = 0.001

SENSITIVITY_MAX = 50.0

DENSITY_VAR_MIN = 0.01

DENSITY_VAR_MAX = 10.0

# === АБЛЯЦИЯ [v5.5] ===

# Минимум 6 сидов, потому что при n=5 двусторонний точный тест Уилкоксона

# не может дать p < 0.05 (минимальный p = 2/2^5 = 0.0625).

ABLATION_MIN_SEEDS = 6

ABLATION_RECOMMENDED_SEEDS = 10

# Rev.7: для подтверждающего (не пилотного) прогона.

ABLATION_CONFIRMATION_SEEDS = 15

# === СТИГМЕРГИЯ ===

STIGMERGY_ENABLED = True

GOAL_STATE_PATH = "memory/goal_state.json"

# === ТЯЖЁЛЫЕ МЕТРИКИ И АРХИТЕКТУРНЫЕ РЕЖИМЫ ===

HEAVY_INFO_METRICS_ONLINE = False

CONNECTIVITY_MODE = "local"

# === СОХРАНЕНИЕ ===

SAVE_EVERY = 100

VISUALIZE_EVERY = 50

LOG_EVERY = 10

# === ВЕРСИЯ ===

SPEC_VERSION = "v5.5-EXP FINAL"

SPEC_REVISION = "Rev.7"

# === ПУТИ ===

# ВАЖНО: без завершающих пробелов.

CHECKPOINT_DIR = "checkpoints"

LOG_DIR = "logs"

OUTPUT_DIR = "outputs"

FRAMES_DIR = "outputs/frames"

COGNITION_FRAMES_DIR = "outputs/cognition_frames"

EVAL_DIR = "outputs/eval"

REPORTS_DIR = "reports"

MEMORY_DIR = "memory"

def set_seed(seed=None):

    """

    Полный контроль энтропии [Rev.7].

    Фиксируем все глобальные ГПСЧ. Для детерминированных операций

    в экспериментальном коде должны использоваться отдельные

    torch.Generator(), созданные через create_deterministic_generator.

    """

    if seed is None:

        seed = SEED

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(seed)

        if CUDNN_BENCHMARK:

            torch.backends.cudnn.benchmark = True

            torch.backends.cudnn.deterministic = False

        else:

            torch.backends.cudnn.benchmark = False

            torch.backends.cudnn.deterministic = True

def create_deterministic_generator(seed=None):

    """

    [Rev.7] Инвариант полного контроля энтропии.

    Возвращает отдельный torch.Generator для данного сида.

    Все стохастические операции в экспериментальном коде должны

    использовать этот генератор, а не глобальные ГСЧ.

    """

    if seed is None:

        seed = SEED

    gen = torch.Generator()

    gen.manual_seed(int(seed))

    return gen

def get_checkpoint_metadata(seed=None, experiment_id="", iteration=0, best_loss=float("inf")):

    """

    [Rev.7] Обязательные метаданные чекпоинта.

    Каждый чекпоинт обязан содержать этот словарь.

    """

    return {

        "spec_version": SPEC_VERSION,

        "revision": SPEC_REVISION,

        "grid_size": GRID_SIZE,

        "n_channels": N_CHANNELS,

        "target_topology": dict(TARGET_TOPOLOGY),

        "stress_mode": {

            "enabled": STRESS_ENABLED,

            "ablation": STRESS_ABLATION_MODE,

            "shuffle": STRESS_SHUFFLE_MODE,

            "target_error": STRESS_TARGET_ERROR_MODE,

            "compress_input": STRESS_COMPRESS_INPUT,

        },

        "alive_threshold": ALIVE_THRESHOLD,

        "seed": seed if seed is not None else SEED,

        "created_at": datetime.now().isoformat(),

        "experiment": experiment_id,

        "iteration": iteration,

        "best_loss": float(best_loss),

    }

def validate():

    """

    Проверяет все абсолютные правила.

    [v5.5-EXP FINAL Rev.7]: полная валидация.

    """

    # Железо и сетка

    assert GRID_SIZE <= 64, f"ПРАВИЛО 1: GRID_SIZE={GRID_SIZE} > 64"

    assert 1 <= BATCH_SIZE <= 2, f"ПРАВИЛО 2: BATCH_SIZE={BATCH_SIZE} вне [1, 2]"

    max_unroll = 20 if BATCH_SIZE == 1 else 10

    assert UNROLL_STEPS <= max_unroll, (

        f"ПРАВИЛО 3: UNROLL_STEPS={UNROLL_STEPS} > {max_unroll} "

        f"при BATCH_SIZE={BATCH_SIZE}"

    )

    for u in UNROLL_CURRICULUM:

        assert u <= max_unroll, (

            f"ПРАВИЛО 3: curriculum unroll {u} > {max_unroll} "

            f"при BATCH_SIZE={BATCH_SIZE}"

        )

    assert len(UNROLL_CURRICULUM) == len(UNROLL_CURRICULUM_AT), (

        "UNROLL_CURRICULUM и UNROLL_CURRICULUM_AT должны быть одной длины"

    )

    for i in range(1, len(UNROLL_CURRICULUM_AT)):

        assert UNROLL_CURRICULUM_AT[i] > UNROLL_CURRICULUM_AT[i - 1], (

            "UNROLL_CURRICULUM_AT должна быть строго возрастающей"

        )

    # Время и обучение

    assert 0 < DT <= 0.5, f"DT={DT} вне (0, 0.5]"

    assert 0 < DT_MAX_EFFECTIVE <= 0.5

    assert DT_MAX_EFFECTIVE >= DT, "DT_MAX_EFFECTIVE должен быть >= DT"

    # Каналы

    assert 0 < ALIVE_CHANNEL < N_CHANNELS

    assert 0 <= VISIBLE_CHANNEL < N_CHANNELS

    assert VISIBLE_CHANNEL != ALIVE_CHANNEL

    # Топология

    assert CONNECTIVITY in (1, 2)

    assert MIN_CLUSTER_SIZE >= 1

    assert 0 < BINARY_THRESHOLD < 1.0

    assert TARGET_COMPONENTS >= 1

    assert LYAPUNOV_MIN_DIST > 0

    # Целевая топология

    assert isinstance(TARGET_TOPOLOGY, dict)

    for key in ("b0", "b1", "chi"):

        assert key in TARGET_TOPOLOGY, f"TARGET_TOPOLOGY не содержит ключ {key}"

    assert int(TARGET_TOPOLOGY["b0"]) >= 0

    assert int(TARGET_TOPOLOGY["b1"]) >= 0

    assert int(TARGET_TOPOLOGY["chi"]) == int(TARGET_TOPOLOGY["b0"]) - int(TARGET_TOPOLOGY["b1"]), (

        "TARGET_TOPOLOGY: chi должен быть равен b0 - b1"

    )

    assert TOPOLOGY_TOLERANCE_B0 >= 0

    assert TOPOLOGY_TOLERANCE_B1 >= 0

    assert 0 < MSE_HALLUCINATION_THRESHOLD < 1.0

    assert SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD > 0

    assert HALLUCINATION_PERSISTENCE >= 2

    # Alive-маска

    assert STATE_POOL_SIZE >= 1

    assert 0 < UPDATE_PROB <= 1.0

    assert 0.0 < ALIVE_THRESHOLD < 1.0

    assert abs(ALIVE_THRESHOLD - 0.5) < 1e-12, (

        "ALIVE_THRESHOLD должен быть равен 0.5. "

        "Иначе мёртвые клетки могут самопроизвольно воскресать."

    )

    assert DEAD_ALPHA_VALUE <= STATE_CLAMP_MIN, (

        "DEAD_ALPHA_VALUE должен быть <= STATE_CLAMP_MIN, "

        "чтобы травма гарантированно убивала клетки."

    )

    assert FRESH_MIN_ALIVE_FRACTION > 0

    assert ALIVE_WARMUP_ITERS >= 0

    assert ALIVE_WARMUP_ITERS < TOTAL_TRAIN_ITERS, (

        f"ALIVE_WARMUP_ITERS={ALIVE_WARMUP_ITERS} >= TOTAL={TOTAL_TRAIN_ITERS}"

    )

    assert STATE_CLAMP_MIN < STATE_CLAMP_MAX

    assert INIT_NOISE_LEVEL > 0

    assert MAX_EXTRA_STEPS_PER_REPORT >= 10

    assert COGNITION_STEP_SIZE >= 1

    assert COGNITION_REPORT_INTERVAL >= 2 * COGNITION_STEP_SIZE, (

        "report_interval должен быть не меньше 2 * STEP_SIZE"

    )

    assert COGNITION_REPORT_INTERVAL % COGNITION_STEP_SIZE == 0, (

        "report_interval должен быть кратен STEP_SIZE"

    )

    # Граничный режим

    assert BOUNDARY_MODE == "constant", (

        "В v5.5-EXP FINAL BOUNDARY_MODE должен быть 'constant', "

        "иначе NCA-физика и scipy-топология могут расходиться."

    )

    # Стресс-канал

    assert 0 <= STRESS_CHANNEL < N_CHANNELS

    assert STRESS_CHANNEL != VISIBLE_CHANNEL

    assert STRESS_CHANNEL != ALIVE_CHANNEL

    if STRESS_ENABLED:

        assert STRESS_CHANNEL in RESERVED_SYSTEM_CHANNELS, (

            "Если STRESS_ENABLED=True, STRESS_CHANNEL должен быть зарезервирован."

        )

    assert 0.0 < STRESS_INPUT_GAIN <= 0.5, (

        "STRESS_INPUT_GAIN должен быть в (0, 0.5] во избежание насыщения."

    )

    assert 0.0 <= STRESS_DECAY <= 1.0

    assert 0.0 <= STRESS_DIFFUSION <= 1.0

    assert 0.0 < STRESS_MAX <= STATE_CLAMP_MAX

    assert STRESS_TEMP_SCALE >= 0.0

    assert 0.0 < STRESS_EMA_ALPHA < 1.0

    # Диагностические режимы не должны конфликтовать.

    if STRESS_SHUFFLE_MODE or STRESS_TARGET_ERROR_MODE:

        assert STRESS_ENABLED and not STRESS_ABLATION_MODE, (

            "Диагностические режимы стресса требуют STRESS_ENABLED=True "

            "и STRESS_ABLATION_MODE=False."

        )

    assert not (STRESS_SHUFFLE_MODE and STRESS_TARGET_ERROR_MODE), (

        "STRESS_SHUFFLE_MODE и STRESS_TARGET_ERROR_MODE не должны быть "

        "включены одновременно в базовых режимах."

    )

    # Морфогены

    assert MORPHOGEN_MIN_CHANNEL >= 2, "Морфогены не должны трогать каналы 0 и 1"

    assert MORPHOGEN_MAX_CHANNEL < N_CHANNELS

    assert MORPHOGEN_MIN_CHANNEL <= MORPHOGEN_MAX_CHANNEL

    for channel in range(MORPHOGEN_MIN_CHANNEL, MORPHOGEN_MAX_CHANNEL + 1):

        assert channel not in RESERVED_SYSTEM_CHANNELS, (

            f"Канал {channel} зарезервирован и не доступен для INJECT_MORPHOGEN"

        )

    assert MORPHOGEN_MIN_RADIUS >= 1

    assert MORPHOGEN_MAX_RADIUS <= max(1, GRID_SIZE // 4), (

        "MORPHOGEN_MAX_RADIUS слишком велик для текущей сетки"

    )

    assert MORPHOGEN_MIN_VALUE >= STATE_CLAMP_MIN

    assert MORPHOGEN_MAX_VALUE <= STATE_CLAMP_MAX

    assert MORPHOGEN_MIN_VALUE <= MORPHOGEN_MAX_VALUE

    # Экономика вмешательств

    assert INTERVENTION_BUDGET_PER_REPORT > 1.0, (

        "Бюджет должен быть > 1.0, чтобы покрывать полную стоимость морфогена."

    )

    assert MORPHOGEN_COOLDOWN_REPORTS >= 0

    assert MORPHOGEN_MAX_INJECTIONS_PER_REPORT >= 1

    if MORPHOGEN_COOLDOWN_REPORTS > 0:

        assert MORPHOGEN_MAX_INJECTIONS_PER_REPORT == 1, (

            "При кулдауне > 0 допустима только одна инъекция за отчёт."

        )

    assert MORPHOGEN_MAX_DOSE_PER_REPORT >= 0.0

    assert MORPHOGEN_MIN_EFFECT_THRESHOLD >= 0.0

    assert INTERVENTION_COST_WEIGHT >= 0.0

    assert INJURY_COOLDOWN_REPORTS >= 0

    assert MIN_UTILITY_THRESHOLD >= 0

    assert MAX_CONSECUTIVE_CONTINUE >= 1

    assert isinstance(ACTION_COSTS, dict)

    for action, cost in ACTION_COSTS.items():

        assert action in KNOWN_ACTIONS, f"Неизвестное действие в ACTION_COSTS: {action}"

        assert float(cost) >= 0.0, f"Стоимость действия {action} отрицательна"

    # Окна и пробы

    assert GRACE_WINDOW >= 0

    assert MINI_MAINTENANCE_STEPS >= 0

    assert MAINTENANCE_WINDOW >= 0

    # Старение

    assert AGING_STEPS >= 0

    assert AGING_NOISE_STD >= 0.0

    assert len(AGING_NOISE_SWEEP) >= 3

    assert isinstance(AGING_NOISE_CHANNELS, (list, tuple))

    for channel in AGING_NOISE_CHANNELS:

        assert int(channel) >= 2

        assert int(channel) < N_CHANNELS

        assert int(channel) != VISIBLE_CHANNEL

        assert int(channel) != ALIVE_CHANNEL

        assert int(channel) not in RESERVED_SYSTEM_CHANNELS

    assert REJUVENATION_ENTROPY_INCREASE >= 0.0

    assert REJUVENATION_B0_ERROR >= 0

    # Критичность

    assert CRITICALITY_MAX_CONFIGS >= 1

    assert CRITICALITY_STEPS >= 1

    assert CRITICALITY_LYAPUNOV_MIN < CRITICALITY_LYAPUNOV_MAX

    assert 0 < SENSITIVITY_MIN < SENSITIVITY_MAX

    assert 0 < DENSITY_VAR_MIN < DENSITY_VAR_MAX

    # Абляция

    assert ABLATION_MIN_SEEDS >= 6, (

        "Минимум 6 сидов: при 5 сидах точный двусторонний тест Уилкоксона "

        "не может достичь p < 0.05."

    )

    assert ABLATION_RECOMMENDED_SEEDS >= ABLATION_MIN_SEEDS

    assert ABLATION_CONFIRMATION_SEEDS >= ABLATION_RECOMMENDED_SEEDS

    # Стигмергия

    assert isinstance(GOAL_STATE_PATH, str)

    assert GOAL_STATE_PATH == GOAL_STATE_PATH.strip()

    # Тяжёлые метрики и режимы связности

    assert isinstance(HEAVY_INFO_METRICS_ONLINE, bool)

    assert CONNECTIVITY_MODE == "local", (

        "В текущей реализации поддерживается только CONNECTIVITY_MODE='local'."

    )

    # Пути

    for path in (

        CHECKPOINT_DIR,

        LOG_DIR,

        OUTPUT_DIR,

        FRAMES_DIR,

        COGNITION_FRAMES_DIR,

        EVAL_DIR,

        REPORTS_DIR,

        MEMORY_DIR,

        GOAL_STATE_PATH,

    ):

        assert isinstance(path, str), f"Путь должен быть строкой: {path}"

        assert path == path.strip(), f"Путь содержит лишние пробелы: '{path}'"

    return True