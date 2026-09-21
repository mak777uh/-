"""

agent_backends.py — Бэкенды агента.

[v5.5-EXP FINAL Rev.7]

По умолчанию используется RuleBasedAgentV2, а не блокирующий input().

RuleBasedAgentV2 реализует:

- правило «Ленивый Агент» (8.14, 16.4.5);

- формулу utility-скора (8.13);

- состояния системы и таблицу политик (16.4);

- учёт stress_derivative.

"""

import json

import re

import config

class AgentBackend:

    def __call__(self, prompt: str) -> str:

        raise NotImplementedError

class RuleBasedAgent(AgentBackend):

    """

    Детерминированный автономный агент для тестов и безопасного дефолта.

    """

    def __init__(self, default_steps=10):

        self.default_steps = int(

            max(1, min(config.MAX_EXTRA_STEPS_PER_REPORT, default_steps))

        )

    def __call__(self, prompt: str) -> str:

        response = {

            "analysis": (

                "Rule-based агент наблюдает текущее состояние системы."

            ),

            "hypothesis": (

                "Для сбора дополнительных данных безопасно продолжить симуляцию."

            ),

            "action": "CONTINUE_TRAINING",

            "params": {

                "steps": self.default_steps,

            },

            "justification": (

                "CONTINUE_TRAINING не ломает расписание отчётов "

                "и даёт больше наблюдений."

            ),

            "confidence": 0.6,

            "report": {

                "stage": "Фаза 7: Нарратив",

                "status": "В процессе",

                "observations": (

                    "Система наблюдается через топологические метрики."

                ),

                "conclusions": (

                    "Требуется больше шагов симуляции для устойчивого вывода."

                ),

                "successes": "Цикл отчётности работает.",

                "failures": (

                    "Пока недостаточно данных для уверенного управляющего действия."

                ),

                "next_steps": "Продолжить наблюдение.",

            },

        }

        return json.dumps(response, ensure_ascii=False)

class RuleBasedAgentV2(RuleBasedAgent):

    """

    Более осмысленный, но всё ещё безопасный детерминированный агент.

    Он не обучается и не использует внешние API.

    Его цель — минимальные вмешательства, если состояние явно отклоняется от цели.

    [v5.5-EXP FINAL Rev.7]:

    - правило «Ленивый Агент»;

    - формула utility-скора;

    - учёт стресс-производной;

    - состояния системы.

    """

    # Состояния системы.

    STATE_UNKNOWN = "UNKNOWN"

    STATE_STABLE_HEALTHY = "STABLE_HEALTHY"

    STATE_STABLE_OFF_TARGET = "STABLE_OFF_TARGET"

    STATE_REGRESSING = "REGRESSING"

    STATE_INJURED = "INJURED"

    STATE_COLLAPSING = "COLLAPSING"

    STATE_EXPLODING = "EXPLODING"

    STATE_CRITICAL_UNSTABLE = "CRITICAL_UNSTABLE"

    def __init__(self, default_steps=10):

        super().__init__(default_steps=default_steps)

        self.consecutive_continue = 0

    def _extract_int(self, pattern, prompt, default=None):

        try:

            match = re.search(pattern, prompt)

            if match:

                return int(match.group(1))

        except Exception:

            pass

        return default

    def _extract_float(self, pattern, prompt, default=None):

        try:

            match = re.search(pattern, prompt)

            if match:

                return float(match.group(1))

        except Exception:

            pass

        return default

    def _classify_state(self, metrics):

        """

        Классификация состояния системы по метрикам.

        """

        b0 = metrics.get("b0")

        target_b0 = metrics.get("target_b0")

        density = metrics.get("density", 0.0)

        stress_mean = metrics.get("stress_mean", 0.0)

        stress_max = metrics.get("stress_max", 0.0)

        symmetric_chamfer_error = metrics.get("symmetric_chamfer_error", 0.0)

        if b0 is None or target_b0 is None:

            return self.STATE_UNKNOWN

        b0_error = abs(b0 - target_b0)

        # Система практически мертва.

        if density < 0.01:

            return self.STATE_COLLAPSING

        # Система перенасыщена.

        if density > 0.9:

            return self.STATE_EXPLODING

        # Стресс-канал насыщен.

        if stress_max > 0.9 * config.STRESS_MAX:

            return self.STATE_CRITICAL_UNSTABLE

        # Цель достигнута.

        if b0_error <= config.TOPOLOGY_TOLERANCE_B0:

            if symmetric_chamfer_error <= config.SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD:

                return self.STATE_STABLE_HEALTHY

            else:

                return self.STATE_STABLE_OFF_TARGET

        # Цель не достигнута.

        return self.STATE_STABLE_OFF_TARGET

    def _compute_utility(self, action, expected_improvement, action_cost):

        """

        Формула utility-скора (8.13):

        utility = expected_metric_improvement - INTERVENTION_COST_WEIGHT * action_cost

        """

        return expected_improvement - config.INTERVENTION_COST_WEIGHT * action_cost

    def __call__(self, prompt: str) -> str:

        # Извлечение метрик из промпта.

        b0 = self._extract_int(r"β₀\D+(\d+)", prompt, default=None)

        target_b0 = self._extract_int(r"β₀ = (\d+)", prompt, default=None)

        density = self._extract_float(

            r"Плотность заполнения: ([0-9.]+)",

            prompt,

            default=None,

        )

        dt = self._extract_float(

            r"Шаг времени \(dt\): ([0-9.eE+-]+)",

            prompt,

            default=None,

        )

        stress_mean = self._extract_float(

            r"Средний стресс: ([0-9.]+)",

            prompt,

            default=None,

        )

        stress_max = self._extract_float(

            r"Максимальный стресс: ([0-9.]+)",

            prompt,

            default=None,

        )

        symmetric_chamfer_error = self._extract_float(

            r"Симметричный Chamfer error: ([0-9.]+)",

            prompt,

            default=None,

        )

        stress_derivative = self._extract_float(

            r"Производная стресса: ([0-9.\-]+)",

            prompt,

            default=None,

        )

        if b0 is None or target_b0 is None:

            return super().__call__(prompt)

        metrics = {

            "b0": b0,

            "target_b0": target_b0,

            "density": density or 0.0,

            "stress_mean": stress_mean or 0.0,

            "stress_max": stress_max or 0.0,

            "symmetric_chamfer_error": symmetric_chamfer_error or 0.0,

        }

        system_state = self._classify_state(metrics)

        b0_error = abs(b0 - target_b0)

        # === ПРАВИЛО «ЛЕНИВЫЙ АГЕНТ» (8.14, 16.4.5) ===

        # Если symmetric_chamfer_error высок, а стресс низок —

        # статическая геометрическая ошибка, стресс слеп.

        # Агент ОБЯЗАН вмешаться через морфоген или диагностику.

        if (

            symmetric_chamfer_error is not None

            and symmetric_chamfer_error > config.SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD

            and stress_mean is not None

            and stress_mean < 0.2 * config.STRESS_MAX

        ):

            # Правило «Ленивый Агент» не может быть переопределено,

            # если бюджет и кулдауны позволяют.

            action = "INJECT_MORPHOGEN"

            params = {

                "channel": 5,

                "value": 0.2,

                "radius": 4,

            }

            hypothesis = (

                "ПРАВИЛО «ЛЕНИВЫЙ АГЕНТ»: высокий симметричный Chamfer error "

                "при низком стрессе. Статическая геометрическая ошибка не видна "

                "стресс-каналом. Требуется морфогенетическое вмешательство."

            )

            justification = (

                "Стресс слеп к статическим ошибкам. Вмешательство основано "

                "на симметричном Chamfer error."

            )

            response = self._build_response(

                action,

                params,

                hypothesis,

                justification,

                system_state,

                metrics,

            )

            return json.dumps(response, ensure_ascii=False)

        # === Учёт производной стресса ===

        # Если стресс высок, но падает — система успокаивается, не вмешиваться.

        if (

            stress_mean is not None

            and stress_mean > 0.5 * config.STRESS_MAX

            and stress_derivative is not None

            and stress_derivative < 0

        ):

            action = "CONTINUE_TRAINING"

            params = {"steps": self.default_steps}

            hypothesis = (

                "Стресс высок, но падает. Система успокаивается. "

                "Вмешательство не требуется."

            )

            justification = (

                "stress_derivative < 0 при высоком стрессе означает, "

                "что система выходит из стрессового состояния."

            )

            self.consecutive_continue += 1

            response = self._build_response(

                action,

                params,

                hypothesis,

                justification,

                system_state,

                metrics,

            )

            return json.dumps(response, ensure_ascii=False)

        # === Таблица политик (16.4.2) ===

        # Система практически мертва.

        if system_state == self.STATE_COLLAPSING:

            action = "CONTINUE_TRAINING"

            params = {"steps": self.default_steps}

            hypothesis = "Система почти мертва. Нужно наблюдение, не вмешательство."

            justification = "Продолжение симуляции безопасно и даёт данные."

            self.consecutive_continue += 1

        # Цель достигнута.

        elif system_state == self.STATE_STABLE_HEALTHY:

            action = "CONTINUE_TRAINING"

            params = {"steps": self.default_steps}

            hypothesis = "Текущее число компонент близко к цели."

            justification = "Минимальное вмешательство: продолжить наблюдение."

            self.consecutive_continue += 1

        # Компонент меньше цели: пробуем мягкий морфоген.

        elif b0 < target_b0:

            action = "INJECT_MORPHOGEN"

            params = {

                "channel": 5,

                "value": 0.2,

                "radius": 4,

            }

            hypothesis = (

                "Недостаточное число устойчивых компонент. "

                "Мягкий морфоген может помочь росту."

            )

            justification = (

                "INJECT_MORPHOGEN является локальным мягким вмешательством "

                "и предпочтительнее глобальных изменений."

            )

            self.consecutive_continue = 0

        # Компонент больше цели: очень осторожно снижаем динамику.

        elif b0 > target_b0 and dt is not None and dt > 0.1:

            action = "MODIFY_DT"

            params = {

                "new_value": max(0.05, dt * 0.8),

            }

            hypothesis = (

                "Слишком много компонент или чрезмерная фрагментация. "

                "Снижение шага времени может стабилизировать динамику."

            )

            justification = (

                "Уменьшение шага времени снижает риск чрезмерной фрагментации."

            )

            self.consecutive_continue = 0

        # Во всех сомнительных случаях — наблюдение.

        else:

            action = "CONTINUE_TRAINING"

            params = {"steps": self.default_steps}

            hypothesis = "Состояние не даёт уверенности для вмешательства."

            justification = "Безопаснее продолжить наблюдение."

            self.consecutive_continue += 1

        # === Формула utility-скора (8.13) ===

        # Если CONTINUE_TRAINING выбирается более MAX_CONSECUTIVE_CONTINUE раз

        # подряд при ненулевой ошибке, обязан рассмотреть активное вмешательство.

        if (

            action == "CONTINUE_TRAINING"

            and self.consecutive_continue >= config.MAX_CONSECUTIVE_CONTINUE

            and b0_error > 0

        ):

            # Принудительно рассматриваем активное вмешательство.

            if b0 < target_b0:

                action = "INJECT_MORPHOGEN"

                params = {

                    "channel": 5,

                    "value": 0.2,

                    "radius": 4,

                }

                hypothesis = (

                    "CONTINUE_TRAINING доминировал слишком долго. "

                    "Принудительное вмешательство через морфоген."

                )

                justification = (

                    "MAX_CONSECUTIVE_CONTINUE достигнут. "

                    "Требуется активное вмешательство."

                )

                self.consecutive_continue = 0

            elif dt is not None and dt > 0.1:

                action = "MODIFY_DT"

                params = {

                    "new_value": max(0.05, dt * 0.8),

                }

                hypothesis = (

                    "CONTINUE_TRAINING доминировал слишком долго. "

                    "Принудительное снижение шага времени."

                )

                justification = (

                    "MAX_CONSECUTIVE_CONTINUE достигнут. "

                    "Требуется активное вмешательство."

                )

                self.consecutive_continue = 0

        response = self._build_response(

            action,

            params,

            hypothesis,

            justification,

            system_state,

            metrics,

        )

        return json.dumps(response, ensure_ascii=False)

    def _build_response(

        self,

        action,

        params,

        hypothesis,

        justification,

        system_state,

        metrics,

    ):

        b0 = metrics.get("b0", "?")

        target_b0 = metrics.get("target_b0", "?")

        density = metrics.get("density", "?")

        symmetric_chamfer_error = metrics.get("symmetric_chamfer_error", "?")

        return {

            "analysis": (

                f"RuleBasedAgentV2 видит β₀={b0} при цели β₀={target_b0}. "

                f"Состояние: {system_state}."

            ),

            "hypothesis": hypothesis,

            "action": action,

            "params": params,

            "justification": justification,

            "confidence": 0.55,

            "report": {

                "stage": "Фаза 7: Нарратив",

                "status": "В процессе",

                "observations": (

                    f"β₀={b0}, цель β₀={target_b0}, density={density}, "

                    f"chamfer={symmetric_chamfer_error}, state={system_state}"

                ),

                "conclusions": "Выбрано минимально безопасное действие.",

                "successes": "Метрики читаются, бюджет учитывается внешним контуром.",

                "failures": "Эвристика может быть неточной.",

                "next_steps": "Проверить эффект действия на следующем отчёте.",

            },

        }

class HumanConsoleAgent(AgentBackend):

    """

    Ручной режим. Использовать только явно.

    """

    def __call__(self, prompt: str) -> str:

        print("\nОЖИДАНИЕ ОТВЕТА АГЕНТА (строго JSON)...")

        return input("\nВведите JSON-ответ агента:\n")

class LocalLLMAgent(AgentBackend):

    """

    Опциональная локальная LLM через llama-cpp-python.

    Внешние облачные API запрещены.

    [v5.5-EXP FINAL Rev.7] ПРАВИЛО 35:

    Локальная LLM не используется для расчёта бюджета, доз и параметров

    вмешательства. Она может использоваться только для нарратива, гипотез

    и интерпретации логов.

    """

    def __init__(

        self,

        model_path=None,

        n_ctx=4096,

        n_gpu_layers=-1,

        **kwargs,

    ):

        try:

            from llama_cpp import Llama

        except ImportError as e:

            raise ImportError(

                "Для LocalLLMAgent нужно установить llama-cpp-python. "

                "Это опциональный компонент."

            ) from e

        if model_path is None:

            raise ValueError("model_path обязателен для LocalLLMAgent")

        self.llm = Llama(

            model_path=model_path,

            n_ctx=n_ctx,

            n_gpu_layers=n_gpu_layers,

            **kwargs,

        )

    def __call__(self, prompt: str) -> str:

        output = self.llm(

            prompt,

            max_tokens=1024,

            temperature=0.7,

        )

        return output["choices"][0]["text"]
