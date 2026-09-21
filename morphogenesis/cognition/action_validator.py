"""

action_validator.py — Единый валидатор действий.

[v5.5-EXP FINAL Rev.7] ПРАВИЛО 34

Все проверки:

- АТР-бюджета;

- стоимости действия;

- нормированной дозы морфогена;

- кулдауна морфогена;

- кулдауна травмы;

- зарезервированных каналов;

- каналов 0 и 1;

- диапазонов параметров;

- максимально допустимого числа инъекций за отчёт

выполняются ЗДЕСЬ и только здесь.

Запрещено размазывать проверки бюджета между

bridge.py, cognitive_loop.py и agent_backends.py.

"""

import config

from cognition.protocol import PARAM_RANGES

def estimate_normalized_dose(params):

    """

    Приблизительная нормированная доза INJECT_MORPHOGEN.

    Не является точным интегралом поля, но достаточно для бюджетной политики.

    """

    if not isinstance(params, dict):

        return 0.0

    try:

        value = abs(float(params.get("value", 0.0)))

    except Exception:

        value = 0.0

    try:

        radius = int(params.get("radius", 4))

    except Exception:

        radius = 4

    max_value = float(config.MORPHOGEN_MAX_VALUE)

    max_radius = float(config.MORPHOGEN_MAX_RADIUS)

    if max_value <= 0 or max_radius <= 0:

        return 0.0

    value_fraction = min(1.0, value / max_value)

    radius_fraction = min(1.0, radius / max_radius)

    dose = value_fraction * (0.25 + 0.75 * radius_fraction)

    return float(min(1.0, max(0.0, dose)))

def compute_action_cost(parsed_action):

    """

    Стоимость действия.

    Для INJECT_MORPHOGEN стоимость масштабируется нормированной дозой.

    Полная стоимость морфогена: 0.5 + 0.5 * normalized_dose (макс 1.0).

    """

    if not isinstance(parsed_action, dict):

        return 0.0

    if not parsed_action.get("valid", False):

        return 0.0

    action = parsed_action.get("action")

    base_cost = float(config.ACTION_COSTS.get(action, 0.0))

    if action == "INJECT_MORPHOGEN":

        dose = estimate_normalized_dose(parsed_action.get("params", {}))

        cost = 0.5 + 0.5 * dose

        return float(min(1.0, max(0.0, cost)))

    return float(base_cost)

def validate_action(

    parsed_action,

    budget_remaining,

    current_report_number,

    last_morphogen_report,

    last_injury_report,

    morphogen_injections_this_report=0,

):

    """

    Единая точка валидации.

    Возвращает:

    {

        "allowed": bool,

        "cost": float,

        "budget_remaining": float,

        "reason": str

    }

    """

    result = {

        "allowed": False,

        "cost": 0.0,

        "budget_remaining": float(budget_remaining),

        "reason": "",

    }

    if not isinstance(parsed_action, dict):

        result["reason"] = "Invalid action structure"

        return result

    if not parsed_action.get("valid", False):

        result["reason"] = parsed_action.get("error", "Invalid action")

        return result

    action = parsed_action.get("action")

    params = parsed_action.get("params", {}) or {}

    # STOP и CONTINUE_TRAINING бесплатны.

    if action in ("STOP", "CONTINUE_TRAINING"):

        result["allowed"] = True

        result["cost"] = 0.0

        result["reason"] = "free action"

        return result

    # APPLY_INJURY вне АТР-бюджета, но с кулдауном.

    if action == "APPLY_INJURY":

        if config.INJURY_COOLDOWN_REPORTS > 0:

            reports_since = current_report_number - last_injury_report

            if reports_since <= config.INJURY_COOLDOWN_REPORTS:

                result["reason"] = (

                    f"APPLY_INJURY заблокирован кулдауном: "

                    f"{reports_since} <= {config.INJURY_COOLDOWN_REPORTS}"

                )

                return result

        result["allowed"] = True

        result["cost"] = 0.0

        result["reason"] = "injury outside ATP budget"

        return result

    # Проверка диапазонов параметров.

    if action in PARAM_RANGES:

        for param_name, param_value in params.items():

            if param_name in PARAM_RANGES[action]:

                min_val, max_val = PARAM_RANGES[action][param_name]

                if isinstance(param_value, bool) or not isinstance(

                    param_value,

                    (int, float),

                ):

                    result["reason"] = f"Parameter {param_name} must be numeric"

                    return result

                if not (min_val <= param_value <= max_val):

                    result["reason"] = (

                        f"Parameter {param_name} out of range "

                        f"[{min_val}, {max_val}]"

                    )

                    return result

    # Специальные проверки для INJECT_MORPHOGEN.

    if action == "INJECT_MORPHOGEN":

        channel = params.get("channel")

        if channel is None:

            result["reason"] = "Missing channel parameter"

            return result

        try:

            channel = int(channel)

        except Exception:

            result["reason"] = "Channel must be integer"

            return result

        # Сначала проверяем диапазон морфогенов [2, 14].

        if not (

            config.MORPHOGEN_MIN_CHANNEL

            <= channel

            <= config.MORPHOGEN_MAX_CHANNEL

        ):

            result["reason"] = (

                f"Parameter channel out of range "

                f"[{config.MORPHOGEN_MIN_CHANNEL}, {config.MORPHOGEN_MAX_CHANNEL}]"

            )

            return result

        # Затем проверяем зарезервированные каналы.

        if channel in config.RESERVED_SYSTEM_CHANNELS:

            result["reason"] = (

                f"Channel {channel} is reserved for system fields"

            )

            return result

        if channel == config.VISIBLE_CHANNEL or channel == config.ALIVE_CHANNEL:

            result["reason"] = (

                f"Channel {channel} cannot be used for INJECT_MORPHOGEN"

            )

            return result

        # Кулдаун морфогена: явное условие из спеки.

        # allowed = (current_report - last_morphogen_report) > COOLDOWN

        if config.MORPHOGEN_COOLDOWN_REPORTS > 0:

            reports_since = current_report_number - last_morphogen_report

            if reports_since <= config.MORPHOGEN_COOLDOWN_REPORTS:

                result["reason"] = (

                    f"INJECT_MORPHOGEN заблокирован кулдауном: "

                    f"{reports_since} <= {config.MORPHOGEN_COOLDOWN_REPORTS}"

                )

                return result

        # Максимум инъекций за отчёт.

        if morphogen_injections_this_report >= config.MORPHOGEN_MAX_INJECTIONS_PER_REPORT:

            result["reason"] = (

                f"Превышен лимит инъекций за отчёт: "

                f"{morphogen_injections_this_report} >= "

                f"{config.MORPHOGEN_MAX_INJECTIONS_PER_REPORT}"

            )

            return result

    # Стоимость и бюджет.

    cost = compute_action_cost(parsed_action)

    result["cost"] = cost

    if cost > budget_remaining:

        result["reason"] = (

            f"Недостаточно бюджета: стоимость {cost:.3f} > "

            f"остаток {budget_remaining:.3f}"

        )

        return result

    result["allowed"] = True

    result["budget_remaining"] = float(budget_remaining) - float(cost)

    result["reason"] = "ok"

    return result