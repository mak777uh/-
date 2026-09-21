"""

bridge.py — Мост между симулятором и когнитивным контуром.

[v5.5-EXP FINAL Rev.7]

Использует единый валидатор для всех проверок бюджета.

"""

import json

import math

import numpy as np

import torch

from scipy.ndimage import label, center_of_mass

import config

from topology import (

    compute_extended_topology_metrics,

    tensor_to_binary,

    remove_small_clusters,

    _get_structure_8,

    get_binary_mask,

)

from evaluate import compute_symmetric_chamfer_error

from cognition.protocol import (

    SYSTEM_PROMPT,

    RESPONSE_SCHEMA,

    VALID_ACTIONS,

    PARAM_RANGES,

)

from cognition.action_validator import (

    validate_action,

    compute_action_cost,

    estimate_normalized_dose,

)

def _state_4d(state_tensor):

    """

    Приводит состояние к виду [B, C, H, W], если возможно.

    """

    if not isinstance(state_tensor, torch.Tensor):

        return None

    state = state_tensor

    if state.dim() == 3:

        state = state.unsqueeze(0)

    if state.dim() != 4:

        return None

    return state

def _visible_from_state(state_tensor):

    """

    Достаёт видимый канал как 2D-тензор.

    """

    state = _state_4d(state_tensor)

    if state is None:

        return torch.as_tensor(state_tensor)

    img = state[0, config.VISIBLE_CHANNEL]

    if config.USE_SIGMOID_VISIBLE:

        img = torch.sigmoid(img)

    return img

def _stress_summary(state_tensor):

    """

    Краткая сводка по стресс-каналу.

    """

    if not config.STRESS_ENABLED:

        return {

            "enabled": False,

            "mean": 0.0,

            "max": 0.0,

            "std": 0.0,

            "saturation_fraction": 0.0,

        }

    state = _state_4d(state_tensor)

    if state is None:

        return {

            "enabled": True,

            "mean": 0.0,

            "max": 0.0,

            "std": 0.0,

            "saturation_fraction": 0.0,

        }

    if state.shape[1] <= config.STRESS_CHANNEL:

        return {

            "enabled": True,

            "mean": 0.0,

            "max": 0.0,

            "std": 0.0,

            "saturation_fraction": 0.0,

        }

    stress = state[:, config.STRESS_CHANNEL].detach().float()

    return {

        "enabled": True,

        "mean": float(stress.mean().item()),

        "max": float(stress.max().item()),

        "std": float(stress.std().item()),

        "saturation_fraction": float(

            (stress >= 0.9 * config.STRESS_MAX).float().mean().item()

        ),

    }

def encode_observation(

    state_tensor,

    model_params,

    history,

    step=0,

    sim_step=0,

    model=None,

    budget=None,

    goal_state=None,

    symmetric_chamfer_error=None,

    stress_derivative=None,

):

    """

    Формирует текстовое наблюдение для агента.

    """

    img = _visible_from_state(state_tensor)

    topo = compute_extended_topology_metrics(

        img,

        target_topology=config.TARGET_TOPOLOGY,

        mse=None,

    )

    stress = _stress_summary(state_tensor)

    binary = tensor_to_binary(img)

    binary = remove_small_clusters(binary)

    structure = _get_structure_8()

    labeled_array, n_components = label(

        binary.astype(np.int32),

        structure=structure,

    )

    cluster_info = []

    if n_components > 0:

        max_clusters = min(n_components, 5)

        indices = list(range(1, max_clusters + 1))

        centers = center_of_mass(

            binary,

            labeled_array,

            indices,

        )

        if max_clusters == 1:

            centers = [centers]

        sizes = [

            int((labeled_array == i).sum())

            for i in indices

        ]

        for idx, (size, center) in enumerate(zip(sizes, centers)):

            cluster_info.append(

                f"  Кластер {idx + 1}: размер={size}, "

                f"центр=({center[0]:.0f}, {center[1]:.0f})"

            )

    lines = [

        f"=== ОТЧЁТ О СОСТОЯНИИ СИСТЕМЫ (шаг {step}, sim_step {sim_step}) ===",

        "",

        "ТОПОЛОГИЯ:",

        f"  Изолированных кластеров (β₀): {topo['b0']}",

        f"  Полостей/циклов (β₁): {topo['b1']}",

        f"  Эйлерова характеристика (χ): {topo['chi']}",

        f"  Плотность заполнения: {topo['density']:.3f}",

        f"  Средняя интенсивность: {topo['mean_intensity']:.3f}",

        f"  Пространственная энтропия: {topo['spatial_entropy']:.3f}",

        f"  Доменные стенки: {topo['domain_wall_energy']:.3f}",

        f"  Топологическая галлюцинация: {topo['topological_hallucination']}",

        f"  Геометрическая галлюцинация: {topo['geometric_hallucination']}",

        "",

        "СТРЕСС:",

        f"  Стресс включён: {stress['enabled']}",

        f"  Средний стресс: {stress['mean']:.3f}",

        f"  Максимальный стресс: {stress['max']:.3f}",

        f"  Насыщение: {stress['saturation_fraction']:.3f}",

        "",

    ]

    if symmetric_chamfer_error is not None:

        lines.append(

            f"  Симметричный Chamfer error: {symmetric_chamfer_error:.4f}"

        )

        lines.append("")

    if stress_derivative is not None:

        lines.append(f"  Производная стресса: {stress_derivative:.4f}")

        lines.append("")

    if cluster_info:

        lines.append("ДЕТАЛИ КЛАСТЕРОВ:")

        lines.extend(cluster_info)

        lines.append("")

    # Правило «Ленивый Агент».

    if symmetric_chamfer_error is not None and stress["mean"] < 0.2 * config.STRESS_MAX:

        if symmetric_chamfer_error > config.SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD:

            lines.append(

                "⚠️ ПРАВИЛО «ЛЕНИВЫЙ АГЕНТ»: высокий симметричный Chamfer error "

                "при низком стрессе. Статическая геометрическая ошибка. "

                "Стресс не видит её. Требуется вмешательство через морфоген."

            )

            lines.append("")

    if topo["density"] < 0.01:

        lines.append("КАЧЕСТВО: Система практически мертва.")

    elif topo["density"] > 0.9:

        lines.append("КАЧЕСТВО: Система перенасыщена.")

    elif topo["b0"] == 0:

        lines.append("КАЧЕСТВО: Нет устойчивых структур. Хаос.")

    elif topo["b0"] == 1 and topo["b1"] == 0:

        lines.append("КАЧЕСТВО: Единый монолитный кластер.")

    elif topo["b0"] > 1 and topo["b1"] == 0:

        lines.append(f"КАЧЕСТВО: {topo['b0']} изолированных структур.")

    elif topo["b1"] > 0:

        lines.append(f"КАЧЕСТВО: Обнаружены полости ({topo['b1']}).")

    lines.extend(

        [

            "",

            "ПАРАМЕТРЫ СИСТЕМЫ:",

            f"  Размер сетки: {model_params.get('grid_size', 'N/A')}",

            f"  Шаг времени (dt): {model_params.get('dt', 'N/A')}",

            f"  Скорость обучения: {model_params.get('lr', 'N/A')}",

            f"  L1 регуляризация: {model_params.get('l1_reg', 'N/A')}",

            f"  Целевых кластеров: {model_params.get('target_b0', 'N/A')}",

            f"  Стресс-канал: {config.STRESS_CHANNEL}",

            f"  Зарезервированные каналы: {config.RESERVED_SYSTEM_CHANNELS}",

        ]

    )

    if budget is not None:

        lines.extend(

            [

                "",

                "БЮДЖЕТ ВМЕШАТЕЛЬСТВ:",

                f"  Остаток бюджета: {budget:.3f}",

                f"  Бюджет на отчёт: {config.INTERVENTION_BUDGET_PER_REPORT:.3f}",

                f"  Кулдаун морфогена: {config.MORPHOGEN_COOLDOWN_REPORTS}",

                f"  Кулдаун травмы: {config.INJURY_COOLDOWN_REPORTS}",

            ]

        )

    if goal_state:

        target_topology = goal_state.get("target_topology", {})

        lines.extend(

            [

                "",

                "СТИГМЕРГИЧЕСКАЯ ЦЕЛЬ:",

                f"  Фаза: {goal_state.get('phase', 'N/A')}",

                f"  Приоритет: {goal_state.get('priority', 'N/A')}",

                f"  Целевой β₀: {target_topology.get('b0', 'N/A')}",

                f"  Целевой β₁: {target_topology.get('b1', 'N/A')}",

                f"  Целевой χ: {target_topology.get('chi', 'N/A')}",

                f"  Заметки: {goal_state.get('notes', 'N/A')}",

            ]

        )

    if history:

        lines.extend(["", "ИСТОРИЯ (последние 5 шагов):"])

        for entry in history[-5:]:

            step_h = entry.get("step", "?")

            sim_step_h = entry.get("sim_step", "?")

            b0_h = entry.get("b0", "?")

            b1_h = entry.get("b1", "?")

            lines.append(

                f"  Шаг {step_h} (sim {sim_step_h}): β₀={b0_h}, β₁={b1_h}"

            )

    return "\n".join(lines)

def build_agent_prompt(

    observation,

    target_b0,

    iteration,

    total_iterations,

    recent_decisions=None,

    sim_step=None,

    budget=None,

    goal_state=None,

):

    decisions_str = "\n".join(

        f"  - {d.get('action', '?')}: {d.get('justification', 'без обоснования')}"

        for d in (recent_decisions or [])

    ) or "  Нет предыдущих решений."

    sim_line = ""

    if sim_step is not None:

        sim_line = f"Фактический шаг симуляции: {sim_step}\n"

    budget_line = ""

    if budget is not None:

        budget_line = f"Остаток бюджета вмешательств: {budget:.3f}\n"

    goal_line = ""

    if goal_state:

        target_topology = goal_state.get("target_topology", {})

        goal_line = (

            "Цель из стигмергической памяти: "

            f"β₀={target_topology.get('b0', '?')}, "

            f"β₁={target_topology.get('b1', '?')}, "

            f"χ={target_topology.get('chi', '?')}\n"

        )

    prompt = f"""{SYSTEM_PROMPT}

=== ТЕКУЩЕЕ НАБЛЮДЕНИЕ ===

{observation}

=== КОНТЕКСТ ===

Целевая топология: {target_b0} изолированных кластеров (β₀ = {target_b0})

{goal_line}Итерация: {iteration}/{total_iterations}

{sim_line}{budget_line}

Последние решения:

{decisions_str}

=== ЗАДАНИЕ ===

Проанализируй состояние, сформулируй гипотезу и выбери действие.

Помни о стоимости действий, принципе минимального вмешательства

и правиле «Ленивый Агент».

Ответь СТРОГО в формате JSON без дополнительного текста.

{RESPONSE_SCHEMA}"""

    return prompt

def parse_agent_response(response_text):

    if response_text is None:

        return {

            "valid": False,

            "error": "Empty agent response",

            "raw_response": "",

        }

    text = str(response_text).strip()

    if text.startswith("```json"):

        text = text[7:]

    elif text.startswith("```"):

        text = text[3:]

    if text.endswith("```"):

        text = text[:-3]

    text = text.strip()

    try:

        parsed = json.loads(text)

    except json.JSONDecodeError as e:

        return {

            "valid": False,

            "error": f"JSON parse error: {str(e)}",

            "raw_response": response_text,

        }

    required = ["analysis", "hypothesis", "action", "justification"]

    for field in required:

        if field not in parsed:

            return {

                "valid": False,

                "error": f"Missing field: {field}",

                "raw_response": response_text,

            }

    if "params" not in parsed or parsed["params"] is None:

        parsed["params"] = {}

    if not isinstance(parsed["params"], dict):

        return {

            "valid": False,

            "error": "Field 'params' must be an object",

            "raw_response": response_text,

        }

    action = str(parsed.get("action", "")).upper()

    if action not in VALID_ACTIONS:

        return {

            "valid": False,

            "error": f"Unknown action: {action}",

            "raw_response": response_text,

        }

    required_params = {

        "MODIFY_DT": "new_value",

        "MODIFY_LR": "new_value",

        "MODIFY_L1_REG": "new_value",

        "MODIFY_TARGET_B0": "new_value",

        "CONTINUE_TRAINING": "steps",

        "APPLY_INJURY": "size",

        "INJECT_MORPHOGEN": ["channel", "value"],

    }

    params = parsed["params"]

    if action in required_params:

        required = required_params[action]

        if isinstance(required, str):

            required = [required]

        for required_key in required:

            if required_key not in params:

                return {

                    "valid": False,

                    "error": f"Missing required parameter: {required_key}",

                    "raw_response": response_text,

                }

    # Проверка зарезервированных каналов.

    if action == "INJECT_MORPHOGEN":

        try:

            channel = int(params.get("channel", -1))

        except Exception:

            return {

                "valid": False,

                "error": "INJECT_MORPHOGEN channel must be integer",

                "raw_response": response_text,

            }

        if channel in config.RESERVED_SYSTEM_CHANNELS:

            return {

                "valid": False,

                "error": (

                    f"Channel {channel} is reserved for system fields "

                    f"and cannot be used for INJECT_MORPHOGEN."

                ),

                "raw_response": response_text,

            }

        if channel == config.VISIBLE_CHANNEL or channel == config.ALIVE_CHANNEL:

            return {

                "valid": False,

                "error": (

                    f"Channel {channel} cannot be used for INJECT_MORPHOGEN."

                ),

                "raw_response": response_text,

            }

    # Проверка диапазонов.

    if action in PARAM_RANGES:

        for param_name, param_value in params.items():

            if param_name in PARAM_RANGES[action]:

                min_val, max_val = PARAM_RANGES[action][param_name]

                if isinstance(param_value, bool) or not isinstance(

                    param_value,

                    (int, float),

                ):

                    return {

                        "valid": False,

                        "error": f"Parameter {param_name} must be numeric",

                        "raw_response": response_text,

                    }

                if not (min_val <= param_value <= max_val):

                    return {

                        "valid": False,

                        "error": f"Parameter {param_name} out of range",

                        "raw_response": response_text,

                    }

    parsed["action"] = action

    parsed["valid"] = True

    return parsed

def apply_action(

    parsed_action,

    model=None,

    optimizer=None,

    target_generator=None,

    state=None,

    budget_remaining=0.0,

    current_report_number=0,

    last_morphogen_report=-1,

    last_injury_report=-1,

    morphogen_injections_this_report=0,

):

    """

    Применяет действие к живым объектам.

    Использует единый валидатор перед любым действием.

    """

    result = {

        "applied": False,

        "effective": False,

        "rolled_back": False,

        "changes": {},

        "note": "",

        "cost": 0.0,

        "budget_remaining": float(budget_remaining),

        "rollback_state": None,

    }

    if not parsed_action.get("valid"):

        result["reason"] = parsed_action.get("error")

        return result

    # Единая валидация.

    validation = validate_action(

        parsed_action,

        budget_remaining=budget_remaining,

        current_report_number=current_report_number,

        last_morphogen_report=last_morphogen_report,

        last_injury_report=last_injury_report,

        morphogen_injections_this_report=morphogen_injections_this_report,

    )

    if not validation["allowed"]:

        result["reason"] = validation["reason"]

        result["note"] = validation["reason"]

        return result

    action = parsed_action["action"]

    params = parsed_action.get("params", {}) or {}

    changes = {}

    result["cost"] = validation["cost"]

    result["budget_remaining"] = validation["budget_remaining"]

    if action == "MODIFY_DT":

        old = config.DT

        new_val = max(

            0.01,

            min(0.5, float(params.get("new_value", config.DT))),

        )

        config.DT = new_val

        if model is not None:

            model.dt = new_val

        changes["DT"] = {"old": old, "new": new_val}

        # Явные поля отката (Rev.7).

        result["rollback_state"] = {

            "config_dt": old,

            "model_dt": old,

        }

        result["effective"] = True

    elif action == "MODIFY_LR":

        old = config.LEARNING_RATE

        new_val = max(

            1e-5,

            min(1e-2, float(params.get("new_value", config.LEARNING_RATE))),

        )

        config.LEARNING_RATE = new_val

        changes["LEARNING_RATE"] = {"old": old, "new": new_val}

        if optimizer is not None:

            for group in optimizer.param_groups:

                group["lr"] = new_val

            result["effective"] = True

        else:

            result["effective"] = False

            result["note"] = (

                "Оптимизатор отсутствует. "

                "Значение сохранено для будущего обучения."

            )

    elif action == "MODIFY_L1_REG":

        old = config.L1_REG_WEIGHT

        new_val = max(

            0.0,

            min(0.1, float(params.get("new_value", config.L1_REG_WEIGHT))),

        )

        config.L1_REG_WEIGHT = new_val

        changes["L1_REG_WEIGHT"] = {"old": old, "new": new_val}

        if optimizer is not None:

            result["effective"] = True

        else:

            result["effective"] = False

            result["note"] = (

                "Оптимизатор отсутствует. "

                "Значение сохранено для будущего обучения."

            )

    elif action == "MODIFY_TARGET_B0":

        old = config.TARGET_COMPONENTS

        new_val = max(

            1,

            min(10, int(params.get("new_value", config.TARGET_COMPONENTS))),

        )

        config.TARGET_COMPONENTS = new_val

        changes["TARGET_COMPONENTS"] = {"old": old, "new": new_val}

        changes["pending_retraining"] = True

        if target_generator is not None and callable(target_generator):

            changes["target_regenerated"] = True

        result["effective"] = True

        result["note"] = (

            "Цель изменена. "

            "Немедленное дообучение не запускается автоматически."

        )

    elif action == "CONTINUE_TRAINING":

        steps = int(params.get("steps", 50))

        steps = max(1, min(config.MAX_EXTRA_STEPS_PER_REPORT, steps))

        changes["train_steps"] = steps

        result["effective"] = True

    elif action == "APPLY_INJURY":

        size = int(params.get("size", 16))

        size = max(4, min(32, size))

        changes["injury_size"] = size

        result["effective"] = True

    elif action == "INJECT_MORPHOGEN":

        channel = int(params.get("channel", config.MORPHOGEN_MIN_CHANNEL))

        value = float(params.get("value", 0.0))

        channel = max(

            config.MORPHOGEN_MIN_CHANNEL,

            min(config.MORPHOGEN_MAX_CHANNEL, channel),

        )

        value = max(

            config.MORPHOGEN_MIN_VALUE,

            min(config.MORPHOGEN_MAX_VALUE, value),

        )

        injection = {

            "channel": channel,

            "value": value,

        }

        if "x" in params:

            injection["x"] = int(params["x"])

        if "y" in params:

            injection["y"] = int(params["y"])

        if "radius" in params:

            injection["radius"] = int(params["radius"])

        changes["morphogen"] = injection

        changes["requires_state_injection"] = True

        result["effective"] = True

        result["note"] = (

            "INJECT_MORPHOGEN должен быть применён "

            "к current_state в cognitive_loop."

        )

    elif action == "STOP":

        changes["stop"] = True

        result["effective"] = True

    result["applied"] = True

    result["changes"] = changes

    return result