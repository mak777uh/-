"""

config.py — ВСЕ гиперпараметры проекта.

Агент: НИКОГДА не хардкодь параметры в других файлах.

Меняй значения ТОЛЬКО здесь.

[v5.6-EXP FINAL] Rev.11-IMPLEMENTATION-READY

Активная спецификация: docs/spec/MORPHOGENESIS_v5.6_Rev11.md

"""

# === ДЕТЕРМИНИЗМ CUDA (§9.2) — ДО ИМПОРТА TORCH ===

# CUBLAS_WORKSPACE_CONFIG обязан быть установлен до инициализации CUDA/torch;
# если поставить позже, детерминизм будет неполным (§9.2). Поэтому переменная
# ставится здесь, а не в utils/determinism.py (config импортируется первым).

DETERMINISTIC_MODE = True

CUBLAS_WORKSPACE_CONFIG = ":4096:8"

if DETERMINISTIC_MODE:

    import os as _os

    # Значение именно принудительно ставится, а не setdefault: §9.2 требует
    # «:4096:8», и чужая переменная окружения не должна тихо ломать детерминизм.
    CUBLAS_WORKSPACE_PREVIOUS = _os.environ.get("CUBLAS_WORKSPACE_CONFIG")

    _os.environ["CUBLAS_WORKSPACE_CONFIG"] = CUBLAS_WORKSPACE_CONFIG

    del _os

# Был ли torch уже импортирован к моменту, когда выставили переменную (§9.2).
# Если False — env выставлен слишком поздно, и CUDA-детерминизм не гарантирован;
# проверят это utils/determinism.assert_deterministic_ready().

import sys as _sys

CUBLAS_CONFIG_SET_BEFORE_TORCH_IMPORT = "torch" not in _sys.modules

del _sys

import torch

import os

import numpy as np

from datetime import datetime

# === ЖЕЛЕЗО ===

# Замеренная ловушка (torch 2.6.0+cu124, Windows): при CUDA_VISIBLE_DEVICES=""
# torch.cuda.is_available() возвращает True, а device_count() — 0, и любая
# загрузка/вычисление на "cuda" падает с "Attempting to deserialize object on
# CUDA device 0". Поэтому проверяем именно наличие устройств.
DEVICE = (
    "cuda" if (torch.cuda.is_available() and torch.cuda.device_count() > 0) else "cpu"
)

# Тот же признак в отчётах об окружении: is_available() сам по себе врёт (см.
# комментарий выше), поэтому считаем CUDA пригодной только при ненулевом
# количестве устройств.
CUDA_USABLE = bool(torch.cuda.is_available() and torch.cuda.device_count() > 0)
CUDA_DEVICE_COUNT = int(torch.cuda.device_count()) if torch.cuda.is_available() else 0

MAX_VRAM_GB = 8

# Градиентный чекпоинтинг активаций (torch.utils.checkpoint). Безопасен, потому

# что все стохастические рисования шага детерминированы внешним noise_key

# (nca_core.run_steps) и на рекомпьюте берутся из кэша, а не рисуются заново.

GRAD_CHECKPOINTING = True

# === ВОСПРОИЗВОДИМОСТЬ ===

SEED = 42

CUDNN_BENCHMARK = False

# === СЕТКА ===

GRID_SIZE = 64

N_CHANNELS = 16

# ВАЖНО [v5.6]:

# Используем constant / zero-padding для восприятия и alive-маски,

# чтобы физика NCA и топологический мониторинг через scipy.ndimage были согласованы.

# Для диффузии стресса отдельно используется reflect-паддинг (см. nca_core.py).

BOUNDARY_MODE = "constant"

# === АРХИТЕКТУРА КЛЕТКИ (§12.2.2) ===

# Восприятие — окрестность Мура 3×3 без обучаемых параметров: вход клетки
# это конкатенация 9 сдвигов состояния, т.е. 9*C каналов (144 при C=16).

MOORE_NEIGHBOR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),

                          (0, -1), (0, 0), (0, 1),

                          (1, -1), (1, 0), (1, 1)]

CELL_BRAIN_INPUT_CHANNELS = len(MOORE_NEIGHBOR_OFFSETS) * N_CHANNELS

CELL_BRAIN_HIDDEN_DIM = 128

# Скрытая «рабочая память» (§3.4): каналы 2–11.

WORKING_MEMORY_CHANNELS = list(range(2, 12))

# === ВРЕМЯ ===

DT = 0.1

# === ОБУЧЕНИЕ (§12.1.5) ===

# Имена ниже — дословно из спеки §12.6.2 «Контракт обучения». Старые имена
# (BATCH_SIZE / UNROLL_STEPS / LEARNING_RATE / TOTAL_TRAIN_ITERS / STATE_POOL_SIZE)
# удалены: две параллельные системы названий давали два разных «единственных
# источника правды», и агент мог менять параметр, который train.py не читал.

# Развертка BPTT = число шагов симуляции на одну итерацию оптимизатора.

TRAIN_BPTT_STEPS = 64

# Пул траекторий (sample pool), §12.6.2.

TRAIN_SAMPLE_POOL_SIZE = 256

TRAIN_BATCH_SIZE = 8

# Пакет для инференса и экспериментов. Batch — свойство ОБУЧЕНИЯ (§12.1.5),
# а не модели: все эксперименты (E01–E07) и когнитивный цикл работают с одной
# траекторией. Отдельное имя нужно, чтобы TRAIN_BATCH_SIZE=8 не превращал
# каждый тест и каждый кадр в 8-кратную работу.

EVAL_BATCH_SIZE = 1

TRAIN_MAX_STEPS = 20000

TRAIN_LR = 1e-3

TRAIN_WEIGHT_DECAY = 1e-4

TRAIN_WARMUP_STEPS = 500

TRAIN_GRAD_CLIP_NORM = 1.0

TRAIN_LOG_INTERVAL = 50

TRAIN_EVAL_INTERVAL = 200

TRAIN_SAVE_INTERVAL = 1000

# Curriculum по длине развертки — расширение поверх спеки (защита от взрыва
# градиента на длинных BPTT в начале обучения). Значения обязаны быть
# <= TRAIN_BPTT_STEPS; порог старта — номера итераций оптимизатора.

TRAIN_BPTT_CURRICULUM = [16, 32, 64]

TRAIN_BPTT_CURRICULUM_AT = [0, 200, 600]

# С чем стартует пул состояний. "noise" — контракт §14.2 («вырастить целевую
# форму из шума»), это единственное значение для серьёзных прогонов.
# "target" — диагностический режим WP4: пул каждые STATE_RESET_EVERY шагов
# перезаполняется СОСТОЯНИЕМ, в котором видимый канал уже равен цели, а живы все
# клетки. Он отделяет «архитектура не способна представить и удержать кольцо»
# от «нельзя вырасти из шума за горизонт BPTT»: в H-K1/H-K2/H-N1 visible_mse
# останавливался на аналитическом плато почти-чёрного поля (0.1393-0.1405, где
# лучшее константное предсказание — 0.12914 = p(1-p)), с grad_norm ~0.004, то
# есть обучение вставало, а не умирало.
TRAIN_POOL_INIT_MODE = "noise"

LR_SCHEDULER = "cosine"

# === ВЕСЫ ЛОССА (§12.6.3) ===

# Единственный источник весов. Действие агента MODIFY_L1_REG меняет
# LOSS_WEIGHTS["hidden_regularization"] (L1 по delta), а не отдельный параметр.

LOSS_WEIGHTS = {

    "visible_mse": 1.0,

    "alive_policy": 0.5,

    "hidden_regularization": 0.05,

    "stress_proxy": 0.1,

    "topo_proxy": 0.1,

    "attractor_divergence": 0.2,

}

# Трёхфазный протокол §12.6.4–12.6.6. Фаза 2 (AE) и фаза 3 (attractor divergence)
# реализуются в слое 2 (WP5); до прохода гейта слоя 1 обучение идёт в фазе 1.

PHASE1_STEPS = 10000

PHASE2_AE_ONLY = True

PHASE3_STEPS = 5000

# Супервизия alive-канала (§12.6.3, член alive_policy) — множитель поверх веса
# LOSS_WEIGHTS["alive_policy"]. Спецификация не задаёт формулу члена, поэтому
# она реализована как MSE(sigmoid(alpha), цель>0) и может быть ослаблена:
# именно это supervised-давление на 80% «пустых» клеток подозревается в
# death-spiral E02 (гипотеза H-A, WP4). Значение 1.0 = чистый вес спеки.

ALPHA_SUPERVISION_WEIGHT = 1.0

# Форма члена alive_policy. Спека задаёт только ИМЯ и ВЕС (§12.6.3), формулу —
# нет, поэтому выбор формулы — это решение кода, а не цитата из спеки, и он
# обязан быть переключателем, чтобы диагностика H-A была воспроизводима:
#
#   "supervised_mse"   MSE(sigmoid(alpha), цель>0). Буквальный прочтение
#                      «супервизия альфа-канала». Цена: 85% клеток цели — фон,
#                      и для них оптимум члена = sigmoid(alpha) -> 0, то есть
#                      лосс АКТИВНО убивает ткань. Замер (wp4_collapse_probe,
#                      experiments/E02_pattern/collapse_probe.json): направление
#                      спуска по alpha уменьшает alpha на 84.8% клеток — ровно
#                      на фоне; альфа-канал при этом не имеет ни одного члена,
#                      который желал бы жизни там, где цели нет.
#   "death_penalty"    односторонний штраф: relu(цель_alive - sigmoid(alpha)).
#                      Карает только недопустимую смерть (клетка мертва там,
#                      где цель требует ткани), но не требует самоубийства на
#                      фоне. Это соответствует §5.1: alive-канал — про
#                      жизнеспособность ткани, а не про форму паттерна; форму
#                      паттерна задаёт канал 0 через visible_mse (§3.3).
#   "survival"         «не убий»: штраф за ПОТЕРЮ живости живой клеткой за
#                      один шаг — mean(relu(-delta_alpha) · sigmoid(alpha)).
#                      Обязателен как отдельный режим, потому что смерть в
#                      модели абсорбирующая по построению (§5.2 запрещает
#                      воскрешение, AliveSTE обнуляет клетку целиком): измерено
#                      wp4_ablations, что траектории alive_fraction базлайна,
#                      H-A1 (вес супервизии 0) и H-A2 (death_penalty)
#                      совпадают с точностью до 3 знаков (0.483/0.199/0.195 ->
#                      0.144/0.065/0.001 на итерациях 50/100/150/200). То есть
#                      лосс НЕ наказывает убийство, а убившая динамика уже
#                      необратима — никакой последующий член этого не отыграет.
#
# Дефолт остаётся спецификационно-буквальным: сначала дискриминанты H-A..H-D
# обязаны показать, что смерть вызывает именно эта член, а не LR/ёмкость/L1.

ALIVE_POLICY_MODE = "supervised_mse"

ALIVE_POLICY_MODES = ("supervised_mse", "death_penalty", "survival")

# Предохранитель от коллапса ткани (§7.4: «смерть с низким лоссом» — не успех).
# Если доля живых клеток ниже COLLAPSE_ALIVE_FRACTION_MIN после
# COLLAPSE_GUARD_MIN_ITERATIONS шагов — обучение останавливается досрочно,
# а результат фиксируется как NEG.

COLLAPSE_GUARD = True

COLLAPSE_ALIVE_FRACTION_MIN = 0.15

COLLAPSE_GUARD_MIN_ITERATIONS = 200

# Измеренная причина, по которой абсолютного порога недостаточно (WP4):
# у цели ring доля живых клеток 0.1523 (experiments/E02_pattern/
# collapse_probe.json -> target_density), то есть COLLAPSE_ALIVE_FRACTION_MIN
# = 0.15 стоит ВПРИТЫК к плотности самой цели. Ткань, корректно собравшая
# кольцо, жива на 0.1523 — она формально проходит порог, но любому шуму
# бинаризации хватает упасть ниже 0.15, чтобы предохранитель сработал на
# здоровой ткани; а вымершая ткань (0.001) ловится при любом разумном пороге.
# Порог обязан быть ОТНОСИТЕЛЬНЫМ плотности цели, иначе он измеряет не смерть
# ткани, а выбранное число.
#
# Смысл: предохранитель срабатывает, если живых клеток осталось меньше, чем
# COLLAPSE_ALIVE_FRACTION_RATIO от плотности ткани в цели. FLOOR не даёт порогу
# исчезнуть на разреженных целях (тонкое кольцо, E03/E04 другой плотности).

COLLAPSE_ALIVE_FRACTION_RATIO = 0.5

COLLAPSE_ALIVE_FRACTION_FLOOR = 0.02


def collapse_alive_fraction_min(target_density=None):
    """
    Порог предохранителя коллапса для данной плотности цели.

    target_density — доля клеток цели с тканью (0..1). Если он не передан или
    не вычислен (старые вызовы, тесты без цели), возвращается абсолютный
    COLLAPSE_ALIVE_FRACTION_MIN — поведение, зафиксированное в спецификации.
    """
    if target_density is None:
        return float(COLLAPSE_ALIVE_FRACTION_MIN)
    density = float(target_density)
    if not 0.0 < density <= 1.0:
        raise ValueError(
            f"target_density={density} вне (0, 1]: плотность цели надо считать по маске, а не по сырому каналу"
        )
    return max(float(COLLAPSE_ALIVE_FRACTION_FLOOR), float(COLLAPSE_ALIVE_FRACTION_RATIO) * density)

# === ПУЛ СОСТОЯНИЙ ===

STATE_RESET_EVERY = 200

STATE_RESET_PROB = 0.01

# === СТОХАСТИКА И ALIVE-МАСКА ===

# §4: на каждом шаге обновляется доля клеток UPDATE_FRACTION.
# Rev.11: переименовано из STOCHASTIC_UPDATE / UPDATE_PROB (spec §4.2, §12.1.1).

STOCHASTIC_UPDATE_ENABLED = True

UPDATE_FRACTION = 0.9

# ВАЖНО:

# Порог жизни равен 0.5.

# sigmoid(0) = 0.5, а условие строго больше, поэтому обнулённая клетка мертва.

# (См. также §5.1: спека сравнивает сырой alive-канал; проект использует
# канонический предикат sigmoid(alpha) > порог — единый для nca_core, topology,
# evaluate и тестов. Отклонение зарегистрировано в memory/decisions_log.jsonl.)

ALIVE_THRESHOLD = 0.5

ALIVE_CHANNEL = 1

# §5.8: суррогатная производная жёсткого порога в backward AliveSTE.

ALIVE_SURROGATE_TAU = 0.1

# нижняя граница суррогатной производной (§5.8, отклонение зафиксировано в
# decisions_log). При tau=0.1 сигмоидный суррогат на глубоко мёртвой клетке
# (alpha = -5 из-за STATE_CLAMP) даёт sigmoid'(-50)/0.1 ≈ 2e-21 — формально
# ненулевой, но практически это ровно та «мёртвая зона», из-за которой ткань
# не могла восстановиться и E02 складывался. Floor сохраняет смысл суррогата
# (максимум всё ещё у порога) и гарантирует, что градиент доходит до клетки
# независимо от того, как далеко она умерла.

ALIVE_SURROGATE_GRAD_FLOOR = 1e-3

ALIVE_WARMUP_ITERS = 50

DEAD_ALPHA_VALUE = -10.0

# Минимальная доля живых клеток в свежем состоянии пула.

FRESH_MIN_ALIVE_FRACTION = 0.20

# === ВИДИМЫЙ КАНАЛ ===

VISIBLE_CHANNEL = 0

USE_SIGMOID_VISIBLE = True

# === ОГРАНИЧЕНИЕ СОСТОЯНИЯ (§3.7, §12.1.1) ===

STATE_CLAMP_MIN = -5.0

STATE_CLAMP_MAX = 5.0

# === ТОПОЛОГИЯ (ТОЛЬКО МОНИТОРИНГ) ===

BINARY_THRESHOLD = 0.5

TARGET_COMPONENTS = 3

CONNECTIVITY = 2

MIN_CLUSTER_SIZE = 4

LYAPUNOV_MIN_DIST = 1e-8

# === ЦЕЛЕВАЯ ТОПОЛОГИЯ (§12.1.2, §12.5) ===

# Rev.11: каноническая цель MVP — кольцо (β₀=1, β₁=1, χ=0). Три круга были
# дефолтом Rev.7/8 и не тестировали β₁ вообще: паттерн из трёх выпуклых
# дисков даёт β₁=0 при любой форме, поэтому «успех» E02 ничего не говорил
# о топологической корректности.

TARGET_PATTERN = "ring"

# Реестр целей: имя -> (строитель паттерна, известный топологический вектор).

TARGET_PATTERN_TOPOLOGY = {

    "ring": {"b0": 1, "b1": 1, "chi": 0},

    "disk": {"b0": 1, "b1": 0, "chi": 1},

    "two_components": {"b0": 2, "b1": 0, "chi": 2},

    "boundary_ring": {"b0": 1, "b1": 1, "chi": 0},

    "three_circles": {"b0": 3, "b1": 0, "chi": 3},

}

TARGET_TOPOLOGY = dict(TARGET_PATTERN_TOPOLOGY[TARGET_PATTERN])

TOPOLOGY_TOLERANCE = 1

TOPOLOGY_TOLERANCE_B0 = 1

TOPOLOGY_TOLERANCE_B1 = 0

# === ТОПОЛОГИЧЕСКИЙ ПРОКСИ (§2.10, §12.1.2, §12.4) ===

# Дискретная топология (scipy.ndimage.label) остаётся источником истины для
# ОТЧЁТОВ и НЕ дифференцируется (§2.4). Прокси — отдельный дифференцируемый
# функционал, который может только аппроксимировать β₀/β₁.

TOPO_PROXY_BACKEND = "soft_topological_proxy"

TOPO_PROXY_ENABLED = True

TOPO_PROXY_WEIGHT = 0.1

TOPO_PROXY_STEP_STRIDE = 5

TOPO_PROXY_GRAD_CLIP = 1.0

TOPO_PROXY_GRACE_STEPS = 500

TOPO_PROXY_REQUIRE_GRAD_TEST = True

# Персистентная гомология (torch-topological) — опциональный бэкенд;
# включается только после стабильного теста градиента (§2.10.3).

TOPO_PERSIST_ENABLED = False

TOPO_PERSIST_WEIGHT = 0.1

TOPO_PERSIST_LIBRARY = "torch-topological"

# === ПОРОГИ ГАЛЛЮЦИНАЦИЙ ===

# Нормировка порогов (Rev.11):

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

# === СТРЕСС-КАНАЛ И СТРЕСС-ШЕРИНГ [v5.6] ===

# Канал 15 — системный стресс-канал. НЕ доступен для INJECT_MORPHOGEN.

STRESS_ENABLED = True

STRESS_CHANNEL = 15

RESERVED_SYSTEM_CHANNELS = [STRESS_CHANNEL]

# ВАЖНО [v5.6]: gain снижен с 1.0 до 0.15.

# Стационарное решение s* = GAIN * x / DECAY.

# При GAIN=1.0, DECAY=0.05 коэффициент усиления = 20 → насыщение.

# При GAIN=0.15 коэффициент усиления = 3 → рабочий диапазон.

STRESS_INPUT_GAIN = 0.15

# ВАЖНО (семантика): в спеке §12.1.3 записано STRESS_DECAY = 0.9, но там это
# КОЭФФИЦИЕНТ УДЕРЖАНИЯ (stress_new = DECAY * stress_old + GAIN * error).
# В коде DECAY — доля СПАДА, поэтому 0.05 <-> удержание 0.95. Значения
# эквивалентны по смыслу; расхождение имён зарегистрировано в decisions_log.

STRESS_DECAY = 0.05

STRESS_DIFFUSION = 0.20

STRESS_MIN = 0.0

STRESS_MAX = 5.0

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

# Rev.11: опциональная логарифмическая компрессия входа стресса.

STRESS_COMPRESS_INPUT = False

# === ИНИЦИАЛИЗАЦИЯ И КОГНИТИВНЫЙ КОНТУР ===

INIT_NOISE_LEVEL = 0.95

# Rev.11: переименовано из MAX_CONTINUE_STEPS.

MAX_EXTRA_STEPS_PER_REPORT = 500

COGNITION_STEP_SIZE = 10

# Минимальный обязательный интервал отчётов: 2 * STEP_SIZE = 20\.

COGNITION_REPORT_INTERVAL = 20

# === РЕЗЕРВИРОВАНИЕ КАНАЛОВ 12–14 (§3.5) ===

# Каналы 12–14 — будущие резонансные каналы (E08). Они ДОСТУПНЫ для чтения
# сеткой, но не должны становиться основной памятью целевой формы (§12.6.8).
# Поэтому: внешние воздействия в них запрещены, а во время обучения они
# случайно зануляются/заумляются (протокол резервирования).

ENTRAINMENT_ENABLED = False

ENTRAINMENT_CHANNELS = [12, 13, 14]

ENTRAINMENT_CHANNEL_RESERVATION_ENABLED = True

ENTRAINMENT_CHANNEL_DROPOUT_PROB = 0.5

ENTRAINMENT_CHANNEL_NOISE_STD = 0.05

# Порог валидации E08: средняя значимость каналов 12–14 не выше этого значения.

ENTRAINMENT_CHANNEL_IMPORTANCE_MAX = 0.2

# Все каналы, недоступные для морфогенов и шума старения, кроме 0 и 1.

RESERVED_HIDDEN_CHANNELS = sorted(

    set(RESERVED_SYSTEM_CHANNELS) | set(ENTRAINMENT_CHANNELS)

)

# === CHANNEL DROPOUT (§12.1.6, §12.6.9) ===

# Применяется ТОЛЬКО к восприятию (входу CellBrain), никогда к состоянию перед
# backward — иначе разрушается градиент in-place (прямой запрет §12.1.6).

CHANNEL_DROPOUT_ENABLED = True

CHANNEL_DROPOUT_PROB = 0.15

CHANNEL_DROPOUT_CHANNELS = list(range(2, 12))

CHANNEL_DROPOUT_APPLY_TO = "perception"

# === МОРФОГЕНЕТИЧЕСКИЕ ВМЕШАТЕЛЬСТВА ===

# Морфогены: каналы 2–11 (рабочая память, §3.4). Каналы 12–14 зарезервированы
# под резонанс (E08), 15 — системный стресс. Запись в 12–14 была конфаундером
# будущего E08: модель могла хранить цель именно там.

MORPHOGEN_MIN_CHANNEL = 2

MORPHOGEN_MAX_CHANNEL = 11

MORPHOGEN_MIN_RADIUS = 1

MORPHOGEN_MAX_RADIUS = 16

MORPHOGEN_MIN_VALUE = -3.0

MORPHOGEN_MAX_VALUE = 3.0

# === ЭКОНОМИКА ВМЕШАТЕЛЬСТВ [v5.6] ===

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

# Rev.11: формула полезности против доминирования бесплатного CONTINUE_TRAINING.

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

# === СТАРЕНИЕ / ОМОЛОЖЕНИЕ [v5.6] ===

AGING_STEPS = 1000

AGING_NOISE_STD = 0.01

# Обязательный sweep по шуму в E05.

AGING_NOISE_SWEEP = [0.01, 0.05, 0.1]

# Шум старения — только по рабочей памяти (2–11). Каналы 12–14 защищены от
# записи (§3.5), 15 — системный стресс.

AGING_NOISE_CHANNELS = list(range(2, 12))  # скрытые каналы 2–11

# Пре-регистрированные пороги деградации и восстановления.

AGING_DEGRADATION_THRESHOLD_B0 = 2

AGING_DEGRADATION_THRESHOLD_ENTROPY = 0.15

AGING_RECOVERY_THRESHOLD = 0.8

REJUVENATION_ENTROPY_INCREASE = 0.15

REJUVENATION_B0_ERROR = 2

# === КРИТИЧНОСТЬ [v5.6] ===

CRITICALITY_SCAN_ENABLED = True

CRITICALITY_MAX_CONFIGS = 12

CRITICALITY_STEPS = 100

# Амплитуда симметризующего возмущения последнего слоя CellBrain в E01.
# §12.2.2 инициализирует последний слой НУЛЯМИ («система из покоя»), поэтому
# без возмущения E01 измерял бы λ покоящейся системы (тривиальное λ≈0).
# Величина 0.0025 выбрана не «на глаз»: это точка скана λ от амплитуды
# (0 → −0.007, 0.0025 → +0.0006, 0.005 → +0.009, 0.01 → +0.044, 0.05 → +0.56),
# ближайшая к СЕРЕДИНЕ коридора §7.3 (а не к его краю), в которой паттерн
# остаётся живым (alive_fraction 0.81, β₀=41, β₁=82). Скан сохраняется в experiments/E01_criticality/lyapunov_scan.json
# вместе с результатом — решение фальсифицируемо и видно целиком.
# Отклонение (хардкод 0.05 в experiment_manager → именованный параметр)
# зарегистрировано в memory/decisions_log.jsonl.

CRITICALITY_INIT_PERTURBATION = 0.0025

CRITICALITY_SCAN_SCALES = (0.0, 0.0025, 0.005, 0.01, 0.02, 0.05)

# Показатель Ляпунова: целевой критический коридор.

CRITICALITY_LYAPUNOV_MIN = -0.01

CRITICALITY_LYAPUNOV_MAX = 0.01

SENSITIVITY_MIN = 0.001

SENSITIVITY_MAX = 50.0

DENSITY_VAR_MIN = 0.01

DENSITY_VAR_MAX = 10.0

# === АБЛЯЦИЯ [v5.6] ===

# Минимум 6 сидов, потому что при n=5 двусторонний точный тест Уилкоксона

# не может дать p < 0.05 (минимальный p = 2/2^5 = 0.0625).

ABLATION_MIN_SEEDS = 6

ABLATION_RECOMMENDED_SEEDS = 10

# Rev.11: для подтверждающего (не пилотного) прогона.

ABLATION_CONFIRMATION_SEEDS = 15

# === СТИГМЕРГИЯ ===

STIGMERGY_ENABLED = True

GOAL_STATE_PATH = "memory/goal_state.json"

# === ТЯЖЁЛЫЕ МЕТРИКИ И АРХИТЕКТУРНЫЕ РЕЖИМЫ ===

HEAVY_INFO_METRICS_ONLINE = False

CONNECTIVITY_MODE = "local"

# === ЩЕЛЕВЫЕ КОНТАКТЫ (физика — слой 5, §1.8 запрещает её до гейтов) ===

# Здесь только геометрические константы цели boundary_ring для отложенного E09:

# паттерн обязан пересекать границу щелевых контактов (§12.5.4), поэтому её

# положение нужно знать уже сейчас. GAP_JUNCTION_ENABLED=False — ничего не

# диффузирует через границу.

GAP_JUNCTION_ENABLED = False

GAP_JUNCTION_AXIS = "x"

GAP_JUNCTION_POSITION = 32

GAP_JUNCTION_TARGET_RADIUS = 20

GAP_JUNCTION_TARGET_THICKNESS = 5

# === СОХРАНЕНИЕ ===

# Интервалы чекпоинтов и логов обучения живут в TRAIN_* (§12.1.5).
# Здесь — только визуализация (кадры), которая спекой не нормируется.

TRAIN_VISUALIZE_INTERVAL = 50

# === ВЕРСИЯ ===

SPEC_VERSION = "v5.6-EXP FINAL"

SPEC_REVISION = "Rev.11-IMPLEMENTATION-READY"

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

# Файлы памяти агента (§15.1–15.6). Пути относительные — как и все пути в config.

MEMORY_MD_PATH = "memory/MEMORY.md"

HYPOTHESES_PATH = "memory/hypotheses.md"

DISCOVERIES_PATH = "memory/discoveries.md"

NEGATIVE_RESULTS_PATH = "memory/negative_results.md"

DECISIONS_LOG_PATH = "memory/decisions_log.jsonl"

CURRENT_STATE_PATH = "memory/current_state.json"

POWER_ANALYSIS_PATH = "memory/power_analysis.json"

# === СТАТИСТИКА (§12.1.11) ===

STATS_MIN_SEEDS = 12

STATS_PILOT_SEEDS = 5

STATS_MAX_SEEDS = 30

STATS_FDR_METHOD = "benjamini-hochberg"

STATS_ALPHA = 0.05

STATS_POWER_TARGET = 0.8

STATS_POWER_ANALYSIS_REQUIRED = True

STATS_EFFECT_SIZE_MIN_INTEREST = 0.10

# Число bootstrap-ресэмплов для доверительных интервалов (utils/stats.py).

STATS_BOOTSTRAP_RESAMPLES = 10000

def set_seed(seed=None, assert_ready=True):

    """

    Полный контроль энтропии [Rev.11] (§9.2).

    Делегирует utils.determinism.init_determinism: фиксирует глобальные ГПСЧ,

    включает torch.use_deterministic_algorithms и cudnn.deterministic,

    возвращает отчёт о деградациях. Для стохастических операций в

    экспериментальном коде по-прежнему нужны отдельные torch.Generator()

    (create_deterministic_generator) — глобальное состояние не используется.

    assert_ready=True выполняет предзапусковый гейт §23: прогон не стартует, если

    окружение не удовлетворяет §9.2 (поздняя установка CUBLAS_WORKSPACE_CONFIG,

    cudnn.benchmark, warn_only-деградация).

    """

    from utils.determinism import assert_deterministic_ready, init_determinism

    report = init_determinism(seed=seed)

    if assert_ready:
        assert_deterministic_ready(report)

    return report

def create_deterministic_generator(seed=None):

    """

    [Rev.11] Инвариант полного контроля энтропии.

    Возвращает отдельный torch.Generator для данного сида.

    Все стохастические операции в экспериментальном коде должны

    использовать этот генератор, а не глобальные ГСЧ.

    """

    if seed is None:

        seed = SEED

    gen = torch.Generator()

    gen.manual_seed(int(seed))

    return gen

def set_target_pattern(name):

    """

    Единообразная смена активной цели (§12.5).

    Меняет Имя паттерна и его топологический вектор ОДНИМ вызовом, чтобы

    TARGET_PATTERN и TARGET_TOPOLOGY физически не могли разойтись — расхождение

    делало бы прогон несопоставимым с его же собственным описанием в чекпоинте.

    """

    if name not in TARGET_PATTERN_TOPOLOGY:

        raise KeyError(

            f"Неизвестная цель '{name}'. Доступны: "

            f"{sorted(TARGET_PATTERN_TOPOLOGY)}"

        )

    global TARGET_PATTERN

    global TARGET_TOPOLOGY

    TARGET_PATTERN = name

    TARGET_TOPOLOGY = dict(TARGET_PATTERN_TOPOLOGY[name])

    return dict(TARGET_TOPOLOGY)

def get_checkpoint_metadata(seed=None, experiment_id="", iteration=0, best_loss=float("inf")):

    """

    [Rev.11] Обязательные метаданные чекпоинта.

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

        "target_pattern": TARGET_PATTERN,

        "topo_proxy_backend": TOPO_PROXY_BACKEND,

        "seed": seed if seed is not None else SEED,

        "created_at": datetime.now().isoformat(),

        "experiment": experiment_id,

        "iteration": iteration,

        "best_loss": float(best_loss),

        # §23: артефакт обязан нести окружение прогона, иначе «воспроизводимый»

        # чекпоинт нельзя отличить от чекпоинта с молча выключенным детерминизмом.

        "environment": {

            "torch": torch.__version__,

            "device": DEVICE,

            "cuda": torch.version.cuda,

            "numpy": np.__version__,

            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),

        },

    }

def assert_checkpoint_compatible(checkpoint, allow_missing_metadata=False, context=""):

    """

    [Rev.11] §13.5: чекпоинты разных версий спецификации НЕ смешиваются.

    Базлайн молча предупреждал и продолжал загружать чужие веса — это

    делало результаты невоспроизводимыми. Теперь — отказ загрузки.

    """

    if not isinstance(checkpoint, dict):

        raise TypeError("checkpoint должен быть dict с метаданными.")

    metadata = checkpoint.get("metadata") or {}

    version = metadata.get("spec_version")

    if version is None:

        if allow_missing_metadata:

            return

        raise RuntimeError(

            f"Чекпоинт без метаданных spec_version ({context or 'контекст не указан'}); "

            f"загрузка запрещена §13.5."

        )

    if version != SPEC_VERSION:

        raise RuntimeError(

            f"Несовместимая версия чекпоинта: {version} (ревизия "

            f"{metadata.get('revision', '?')}), активная спецификация — "

            f"{SPEC_VERSION} ({SPEC_REVISION}). Откатитесь на matching-баслайну "

            f"вес или переобучите (§13)."

        )

def validate():

    """

    Проверяет все абсолютные правила.

    [v5.6-EXP FINAL Rev.11]: полная валидация.

    """

    # Железо и сетка

    assert GRID_SIZE <= 64, f"ПРАВИЛО 1: GRID_SIZE={GRID_SIZE} > 64"

    assert N_CHANNELS == 16, "§12.1.1: архитектура определена на 16 каналов"

    # ПРАВИЛА 2/3 в редакции Rev.7/8 ограничивали BATCH_SIZE<=2 и unroll<=10 —
    # это была страховка VRAM, противоречащая §12.1.5 (TRAIN_BATCH_SIZE=8,
    # TRAIN_BPTT_STEPS=64). Оставляем бюджет по памяти явным проверкам ниже.

    assert TRAIN_BATCH_SIZE >= 1, "TRAIN_BATCH_SIZE должен быть >= 1"

    assert TRAIN_BPTT_STEPS > 0, "§12.1.13: TRAIN_BPTT_STEPS > 0"

    assert TRAIN_SAMPLE_POOL_SIZE >= TRAIN_BATCH_SIZE, (

        "§12.1.13: пул траекторий не может быть меньше пакета"

    )

    assert TRAIN_GRAD_CLIP_NORM > 0, "§12.1.13: TRAIN_GRAD_CLIP_NORM > 0"

    assert TRAIN_LR > 0 and TRAIN_WARMUP_STEPS >= 0

    assert TRAIN_MAX_STEPS >= 1

    assert len(TRAIN_BPTT_CURRICULUM) == len(TRAIN_BPTT_CURRICULUM_AT), (

        "TRAIN_BPTT_CURRICULUM и TRAIN_BPTT_CURRICULUM_AT должны быть одной длины"

    )

    for u in TRAIN_BPTT_CURRICULUM:

        assert 0 < u <= TRAIN_BPTT_STEPS, (

            f"Curriculum BPTT {u} вне (0, TRAIN_BPTT_STEPS={TRAIN_BPTT_STEPS}]"

        )

    for i in range(1, len(TRAIN_BPTT_CURRICULUM_AT)):

        assert TRAIN_BPTT_CURRICULUM_AT[i] > TRAIN_BPTT_CURRICULUM_AT[i - 1], (

            "TRAIN_BPTT_CURRICULUM_AT должна быть строго возрастающей"

        )

    assert TRAIN_POOL_INIT_MODE in ("noise", "target"), (
        f'TRAIN_POOL_INIT_MODE={TRAIN_POOL_INIT_MODE!r}: допустимы "noise" (§14.2) '
        'и "target" (диагностика WP4)'
    )

    # Бюджет VRAM: траектория длиной BPTT хранит активации всех шагов.
    # Оценка консервативна (без gradient checkpointing) — она не запрещает
    # запуск, а запрещает молча выйти за пределы железа (§14 «в пределах 8 ГБ»).

    est_activation_gb = (

        TRAIN_BATCH_SIZE

        * TRAIN_BPTT_STEPS

        * (9 * N_CHANNELS + 2 * 128)

        * GRID_SIZE

        * GRID_SIZE

        * 4

        / 1e9

    )

    assert est_activation_gb <= MAX_VRAM_GB, (

        f"Предположительный пик активностей {est_activation_gb:.1f} ГБ > "

        f"бюджета {MAX_VRAM_GB} ГБ: снизь TRAIN_BATCH_SIZE/TRAIN_BPTT_STEPS "

        f"(через decisions_log) или включи градиентный чекпоинтинг"

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

    assert TRAIN_SAMPLE_POOL_SIZE >= 1

    assert 0 < UPDATE_FRACTION <= 1.0, "§4.2: доля обновляемых клеток в (0, 1]"

    assert 0.0 < ALIVE_THRESHOLD < 1.0

    assert ALIVE_SURROGATE_TAU > 0, "§5.8: температура суррогата должна быть > 0"

    assert 0 <= ALIVE_SURROGATE_GRAD_FLOOR < 1.0 / (4 * ALIVE_SURROGATE_TAU), (
        "§5.8: floor суррогатного градиента обязан быть меньше пика у порога, "
        "иначе живые/мёртвые клетки становятся равноправными в backward"
    )

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

    assert ALIVE_WARMUP_ITERS < TRAIN_MAX_STEPS, (

        f"ALIVE_WARMUP_ITERS={ALIVE_WARMUP_ITERS} >= {TRAIN_MAX_STEPS}"

    )

    assert ALIVE_WARMUP_ITERS < PHASE1_STEPS, (

        "Alive-warmup обязан завершиться внутри фазы 1 (§12.6.4)"

    )

    assert STATE_CLAMP_MIN < 0 < STATE_CLAMP_MAX

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

        "В v5.6-EXP FINAL BOUNDARY_MODE должен быть 'constant', "

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

    assert 0.0 <= STRESS_MIN < STRESS_MAX

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

    # §3.5: каналы 12–14 зарезервированы под резонанс (E08) и недоступны для
    # записи морфогеном — иначе базовая модель хранит цель именно там, и E08
    # перестаёт быть измеримым.

    if ENTRAINMENT_CHANNEL_RESERVATION_ENABLED:

        assert MORPHOGEN_MAX_CHANNEL < min(ENTRAINMENT_CHANNELS), (

            f"MORPHOGEN_MAX_CHANNEL={MORPHOGEN_MAX_CHANNEL} пересекается с "

            f"зарезервированными каналами {ENTRAINMENT_CHANNELS}"

        )

    for channel in range(MORPHOGEN_MIN_CHANNEL, MORPHOGEN_MAX_CHANNEL + 1):

        assert channel not in RESERVED_HIDDEN_CHANNELS, (

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

        assert int(channel) not in RESERVED_HIDDEN_CHANNELS, (

            f"Канал {channel} зарезервирован (§3.5) — шум старения не имеет "

            f"права в него писать"

        )

    assert REJUVENATION_ENTROPY_INCREASE >= 0.0

    assert REJUVENATION_B0_ERROR >= 0

    # Критичность

    assert CRITICALITY_MAX_CONFIGS >= 1

    assert CRITICALITY_STEPS >= 1

    assert 0.0 < CRITICALITY_INIT_PERTURBATION <= SENSITIVITY_MAX, (
        "E01: амплитуда возмущения обязана быть положительной и конечной"
    )

    assert list(CRITICALITY_SCAN_SCALES) == sorted(CRITICALITY_SCAN_SCALES), (
        "CRITICALITY_SCAN_SCALES должна быть отсортирована — скан логируется как кривая"
    )

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

    # Статистика (§12.1.11): без согласованных порогов power analysis даёт
    # бессмысленный required_seeds, а основной прогон — ложную «воспроизводимость».

    assert 0 < STATS_ALPHA < 1

    assert 0 < STATS_POWER_TARGET < 1

    assert 1 <= STATS_PILOT_SEEDS <= STATS_MIN_SEEDS <= STATS_MAX_SEEDS, (

        f"STATS_* неупорядочены: pilot={STATS_PILOT_SEEDS}, "

        f"min={STATS_MIN_SEEDS}, max={STATS_MAX_SEEDS}"

    )

    assert STATS_FDR_METHOD == "benjamini-hochberg", (

        "Другая поправка не реализована в utils/stats.py"

    )

    assert STATS_EFFECT_SIZE_MIN_INTEREST > 0

    assert STATS_BOOTSTRAP_RESAMPLES >= 1000

    # Цель и её топология (§12.5.2): у каждой цели обязан быть известный вектор.

    assert TARGET_PATTERN in TARGET_PATTERN_TOPOLOGY, (

        f"Неизвестная цель TARGET_PATTERN={TARGET_PATTERN!r}; "

        f"реестр: {sorted(TARGET_PATTERN_TOPOLOGY)}"

    )

    assert dict(TARGET_TOPOLOGY) == dict(TARGET_PATTERN_TOPOLOGY[TARGET_PATTERN]), (

        f"TARGET_TOPOLOGY={TARGET_TOPOLOGY} разошлась с вектором цели "

        f"{TARGET_PATTERN!r}. Меняй цель только через config.set_target_pattern()."

    )

    for name, vec in TARGET_PATTERN_TOPOLOGY.items():

        assert int(vec["chi"]) == int(vec["b0"]) - int(vec["b1"]), (

            f"Цель {name!r}: χ != β₀ − β₁ (χ={vec['chi']}, "

            f"b0={vec['b0']}, b1={vec['b1']})"

        )

    # LOSS_WEIGHTS (§12.6.3): лосс обязан быть полной суммой взвешенных членов.

    for key in (

        "visible_mse",

        "alive_policy",

        "hidden_regularization",

        "stress_proxy",

        "topo_proxy",

        "attractor_divergence",

    ):

        assert key in LOSS_WEIGHTS, f"LOSS_WEIGHTS не содержит член {key!r}"

        assert float(LOSS_WEIGHTS[key]) >= 0.0, f"Вес {key} отрицателен"

    assert float(LOSS_WEIGHTS["visible_mse"]) > 0.0, (

        "Без видимого MSE обучение не имеет целевой функции формы"

    )

    assert PHASE1_STEPS >= 1 and PHASE3_STEPS >= 0, (

        f"Некорректные фазы: PHASE1_STEPS={PHASE1_STEPS}, PHASE3_STEPS={PHASE3_STEPS}"

    )

    assert ALPHA_SUPERVISION_WEIGHT >= 0.0

    assert ALIVE_POLICY_MODE in ALIVE_POLICY_MODES, (
        f"ALIVE_POLICY_MODE={ALIVE_POLICY_MODE!r} вне списка {ALIVE_POLICY_MODES}"
    )

    assert 0.0 < COLLAPSE_ALIVE_FRACTION_MIN < 1.0

    assert 0.0 < COLLAPSE_ALIVE_FRACTION_RATIO <= 1.0

    assert 0.0 < COLLAPSE_ALIVE_FRACTION_FLOOR < 1.0

    assert COLLAPSE_GUARD_MIN_ITERATIONS >= 1

    # Топологический прокси (§2.10.1, §12.1.13).

    assert TOPO_PROXY_BACKEND in {

        "torch-topological",

        "soft_topological_proxy",

        "disabled",

    }, f"§2.10.1: недопустимый бэкенд {TOPO_PROXY_BACKEND!r}"

    assert TOPO_PROXY_STEP_STRIDE >= 1

    assert TOPO_PROXY_GRAD_CLIP > 0

    assert TOPO_PROXY_GRACE_STEPS >= 1

    # Дифференцируемость β₀/β₁ через scipy.ndimage.label запрещена (§2.4):
    # если включён torch-topological, тест градиента обязан требоваться.

    if TOPO_PROXY_BACKEND == "torch-topological":

        assert TOPO_PROXY_REQUIRE_GRAD_TEST, (

            "§2.10.3: персистентный бэкенд допускается только после теста градиента"

        )

    # Channel Dropout (§12.1.6): только на восприятие, только скрытые каналы.

    assert CHANNEL_DROPOUT_APPLY_TO == "perception", (

        "§12.1.6: dropout к состоянию до backward применять запрещено"

    )

    assert 0.0 <= CHANNEL_DROPOUT_PROB < 1.0

    for channel in CHANNEL_DROPOUT_CHANNELS:

        assert int(channel) not in (VISIBLE_CHANNEL, ALIVE_CHANNEL, STRESS_CHANNEL), (

            f"Channel Dropout трогает служебный канал {channel}"

        )

    # Резервирование каналов 12–14 (§3.5, §12.1.13).

    assert len(ENTRAINMENT_CHANNELS) == 3

    assert all(2 <= int(ch) <= 14 for ch in ENTRAINMENT_CHANNELS)

    assert STRESS_CHANNEL not in ENTRAINMENT_CHANNELS

    assert VISIBLE_CHANNEL not in ENTRAINMENT_CHANNELS

    assert ALIVE_CHANNEL not in ENTRAINMENT_CHANNELS

    if ENTRAINMENT_ENABLED:

        assert ENTRAINMENT_CHANNEL_RESERVATION_ENABLED, (

            "§12.1.13: при включённом резонансе резервирование каналов обязательно"

        )

    if ENTRAINMENT_CHANNEL_RESERVATION_ENABLED:

        assert 0.0 < ENTRAINMENT_CHANNEL_DROPOUT_PROB <= 1.0

        assert ENTRAINMENT_CHANNEL_NOISE_STD >= 0.0

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

        MEMORY_MD_PATH,

        HYPOTHESES_PATH,

        DISCOVERIES_PATH,

        NEGATIVE_RESULTS_PATH,

        DECISIONS_LOG_PATH,

        CURRENT_STATE_PATH,

        POWER_ANALYSIS_PATH,

    ):

        assert isinstance(path, str), f"Путь должен быть строкой: {path}"

        assert path == path.strip(), f"Путь содержит лишние пробелы: '{path}'"

    # Файлы памяти (§15) обязаны лежать в MEMORY_DIR — иначе агент пишет знание в корень.

    for path in (

        GOAL_STATE_PATH,

        MEMORY_MD_PATH,

        HYPOTHESES_PATH,

        DISCOVERIES_PATH,

        NEGATIVE_RESULTS_PATH,

        DECISIONS_LOG_PATH,

        CURRENT_STATE_PATH,

        POWER_ANALYSIS_PATH,

    ):

        assert path.startswith(MEMORY_DIR + "/"), f"{path} вне {MEMORY_DIR}/ — нарушает §15.1"

    return True
