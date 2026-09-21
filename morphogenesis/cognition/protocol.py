"""

protocol.py — Протокол рассуждений и схема действий.

[v5.5-EXP FINAL Rev.7]

Включает:

- правило «Ленивый Агент»;

- формулу utility-скора;

- диапазоны параметров;

- правила бюджета.

"""

import config

SYSTEM_PROMPT = """Ты — автономный исследователь морфогенеза.

Твоя задача: анализировать топологическое состояние клеточного автомата и принимать решения для достижения целевой морфологии.

ПРИНЦИПЫ СИСТЕМЫ:

- Клетки видят только соседей (локальность)

- Глобальная структура возникает из локальных правил (эмерджентность)

- Цель: целевой топологический вектор, стабильность, регенерация

- Морфогенетические вмешательства должны быть мягкими, локальными и бюджетными

- Агент не рисует форму напрямую

- Агент создаёт условия для самоорганизации

ПРАВИЛО «ЛЕНИВЫЙ АГЕНТ» [Rev.7]:

Если symmetric_chamfer_error высок (выше порога), а stress_mean низок (< 0.2 * STRESS_MAX), это означает статическую геометрическую ошибку, которую стресс не видит.

В этом случае ты ОБЯЗАН:

1\. Не ждать стресс-сигнала.

2\. Использовать INJECT_MORPHOGEN в зоны максимального локального расхождения (если бюджет позволяет).

3\. Зафиксировать в отчёте: «Статическая геометрическая ошибка не обнаружена стрессом».

ФОРМУЛА UTILITY-СКОРА [Rev.7]:

utility = expected_metric_improvement - INTERVENTION_COST_WEIGHT * action_cost

Если max(utility) < MIN_UTILITY_THRESHOLD, выбери CONTINUE_TRAINING.

Если CONTINUE_TRAINING выбирается более MAX_CONSECUTIVE_CONTINUE раз подряд при ненулевой ошибке, обязан рассмотреть активное вмешательство.

ПРАВИЛА ВЫВОДА:

- Отвечай ТОЛЬКО валидным JSON

- Никакого текста до или после JSON

- Если не уверен — выбери CONTINUE_TRAINING

- Если действие дорогое или ожидаемая польза мала — выбери CONTINUE_TRAINING

"""

RESPONSE_SCHEMA = """

{

  "analysis": "Краткое описание (2-3 предложения)",

  "hypothesis": "Почему система в таком состоянии",

  "action": "ОДНО из допустимых действий",

  "params": {

    "new_value": 0.15

  },

  "justification": "Почему это действие улучшит систему",

  "confidence": 0.8,

  "report": {

    "stage": "Текущая фаза",

    "status": "Успех / Частичный успех / Неудача / В процессе",

    "observations": "Что наблюдает агент",

    "conclusions": "Какие выводы сделаны",

    "successes": "Что работает хорошо",

    "failures": "Что не работает и почему",

    "next_steps": "Что будет сделано дальше"

  }

}

ДОПУСТИМЫЕ ДЕЙСТВИЯ:

- MODIFY_DT: (params: {"new_value": float 0.01-0.5})

- MODIFY_LR: (params: {"new_value": float 1e-5-1e-2})

- MODIFY_L1_REG: (params: {"new_value": float 0.0-0.1})

- MODIFY_TARGET_B0: (params: {"new_value": int 1-10})

- CONTINUE_TRAINING: (params: {"steps": int 1-500})

- APPLY_INJURY: (params: {"size": int 4-32})

- INJECT_MORPHOGEN: (params: {"channel": int 2-14, "value": float -3.0-3.0, опционально "x", "y", "radius"})

- STOP: (params: {})

ПРИМЕЧАНИЯ:

- Канал 15 зарезервирован под стресс-канал и недоступен для инъекций.

- Каналы 0 и 1 не изменяются через INJECT_MORPHOGEN.

- MODIFY_LR действует только при наличии оптимизатора.

- MODIFY_TARGET_B0 — заявка на смену цели, немедленное дообучение не обязательно.

- INJECT_MORPHOGEN — мягкое локальное вмешательство в скрытые каналы 2-14.

- Каждое действие имеет стоимость. АТР-бюджет ограничен.

- APPLY_INJURY вне АТР-бюджета, но имеет глобальный кулдаун.

"""

VALID_ACTIONS = list(config.KNOWN_ACTIONS)

PARAM_RANGES = {

    "MODIFY_DT": {

        "new_value": (0.01, 0.5),

    },

    "MODIFY_LR": {

        "new_value": (1e-5, 1e-2),

    },

    "MODIFY_L1_REG": {

        "new_value": (0.0, 0.1),

    },

    "MODIFY_TARGET_B0": {

        "new_value": (1, 10),

    },

    "CONTINUE_TRAINING": {

        "steps": (1, config.MAX_EXTRA_STEPS_PER_REPORT),

    },

    "APPLY_INJURY": {

        "size": (4, 32),

    },

    "INJECT_MORPHOGEN": {

        "x": (0, config.GRID_SIZE - 1),

        "y": (0, config.GRID_SIZE - 1),

        "radius": (

            config.MORPHOGEN_MIN_RADIUS,

            config.MORPHOGEN_MAX_RADIUS,

        ),

        "channel": (

            config.MORPHOGEN_MIN_CHANNEL,

            config.MORPHOGEN_MAX_CHANNEL,

        ),

        "value": (

            config.MORPHOGEN_MIN_VALUE,

            config.MORPHOGEN_MAX_VALUE,

        ),

    },

    "STOP": {},

}

BUDGET_RULES = {

    "intervention_budget_per_report": config.INTERVENTION_BUDGET_PER_REPORT,

    "morphogen_cooldown_reports": config.MORPHOGEN_COOLDOWN_REPORTS,

    "morphogen_max_injections_per_report": config.MORPHOGEN_MAX_INJECTIONS_PER_REPORT,

    "morphogen_max_dose_per_report": config.MORPHOGEN_MAX_DOSE_PER_REPORT,

    "min_effect_threshold": config.MORPHOGEN_MIN_EFFECT_THRESHOLD,

    "injury_cooldown_reports": config.INJURY_COOLDOWN_REPORTS,

    "intervention_cost_weight": config.INTERVENTION_COST_WEIGHT,

    "min_utility_threshold": config.MIN_UTILITY_THRESHOLD,

    "max_consecutive_continue": config.MAX_CONSECUTIVE_CONTINUE,

    "action_costs": config.ACTION_COSTS,

}