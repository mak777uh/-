"""

reporter.py — Система отчётности.

[v5.5-EXP FINAL Rev.7]

ВАЖНО:

regex должен быть только с одинарными экранированными последовательностями:

r"report_(\d{4})\.md"

"""

import json

import os

import re

from datetime import datetime

import config

class Reporter:

    def __init__(self, reports_dir=config.REPORTS_DIR):

        self.reports_dir = reports_dir

        os.makedirs(reports_dir, exist_ok=True)

        self.report_count = self._find_max_report_number()

    def _find_max_report_number(self):

        """

        Находим максимальный номер, а не количество.

        """

        if not os.path.exists(self.reports_dir):

            return 0

        max_num = 0

        for f in os.listdir(self.reports_dir):

            match = re.match(r"report_(\d{4})\.md", f)

            if match:

                num = int(match.group(1))

                if num > max_num:

                    max_num = num

        return max_num

    def _safe_float(self, value, default=0.0):

        try:

            return float(value)

        except (TypeError, ValueError):

            return default

    def generate_report(

        self,

        step,

        sim_step,

        phase,

        parsed_action,

        action_result,

        topology_metrics,

        history,

        stress_summary=None,

        cost=0.0,

        budget_remaining=None,

        goal_state=None,

        symmetric_chamfer_error=None,

        stress_derivative=None,

    ):

        self.report_count += 1

        report_data = parsed_action.get("report", {})

        stage = report_data.get("stage", phase)

        status = report_data.get("status", "В процессе")

        observations = report_data.get("observations", "Нет данных")

        conclusions = report_data.get("conclusions", "Нет данных")

        successes = report_data.get("successes", "Нет данных")

        failures = report_data.get("failures", "Нет данных")

        next_steps = report_data.get("next_steps", "Нет данных")

        b0 = topology_metrics.get("b0", "N/A")

        b1 = topology_metrics.get("b1", "N/A")

        chi = topology_metrics.get("chi", "N/A")

        density = self._safe_float(topology_metrics.get("density", 0))

        spatial_entropy = self._safe_float(

            topology_metrics.get("spatial_entropy", 0)

        )

        domain_wall_energy = self._safe_float(

            topology_metrics.get("domain_wall_energy", 0)

        )

        topological_hallucination = topology_metrics.get(

            "topological_hallucination_raw",

            topology_metrics.get("topological_hallucination", False),

        )

        geometric_hallucination = topology_metrics.get(

            "geometric_hallucination_raw",

            topology_metrics.get("geometric_hallucination", False),

        )

        lines = [

            f"# ОТЧЁТ #{self.report_count:04d}",

            "",

            f"**Дата:** {datetime.now().isoformat()}",

            f"**Шаг:** {step}",

            f"**Фактический шаг симуляции:** {sim_step}",

            f"**Фаза:** {stage}",

            f"**Статус:** {status}",

            f"**Версия спецификации:** {config.SPEC_VERSION}",

            f"**Ревизия:** {config.SPEC_REVISION}",

            "",

            "## ТЕКУЩЕЕ СОСТОЯНИЕ",

            "| Метрика | Значение |",

            "|---------|----------|",

            f"| β₀ (кластеры) | {b0} |",

            f"| β₁ (полости) | {b1} |",

            f"| χ (Эйлер) | {chi} |",

            f"| Плотность | {density:.3f} |",

            f"| Пространственная энтропия | {spatial_entropy:.3f} |",

            f"| Доменные стенки | {domain_wall_energy:.3f} |",

            f"| Топологическая галлюцинация | {topological_hallucination} |",

            f"| Геометрическая галлюцинация | {geometric_hallucination} |",

            "",

        ]

        if symmetric_chamfer_error is not None:

            lines.append(

                f"| Симметричный Chamfer error | "

                f"{self._safe_float(symmetric_chamfer_error):.4f} |"

            )

            lines.append("")

        if stress_summary:

            stress_mode = "ablation" if config.STRESS_ABLATION_MODE else "normal"

            if config.STRESS_SHUFFLE_MODE:

                stress_mode = "shuffle"

            if config.STRESS_TARGET_ERROR_MODE:

                stress_mode = "target_error"

            lines.extend(

                [

                    "## СТРЕСС",

                    "| Метрика | Значение |",

                    "|---------|----------|",

                    f"| Включён | {stress_summary.get('enabled', False)} |",

                    f"| Режим | {stress_mode} |",

                    f"| Средний | {self._safe_float(stress_summary.get('mean', 0)):.3f} |",

                    f"| Максимальный | {self._safe_float(stress_summary.get('max', 0)):.3f} |",

                    f"| Насыщение | {self._safe_float(stress_summary.get('saturated_fraction', 0)):.3f} |",

                ]

            )

            if stress_derivative is not None:

                lines.append(

                    f"| Производная стресса | {self._safe_float(stress_derivative):.4f} |"

                )

            lines.append("")

        if budget_remaining is not None or cost is not None:

            lines.extend(

                [

                    "## ЭКОНОМИКА ВМЕШАТЕЛЬСТВ",

                    "| Метрика | Значение |",

                    "|---------|----------|",

                    f"| Стоимость действия | {self._safe_float(cost):.3f} |",

                    f"| Остаток бюджета | {self._safe_float(budget_remaining):.3f} |",

                    "",

                ]

            )

        if goal_state:

            target_topology = goal_state.get("target_topology", {})

            lines.extend(

                [

                    "## ЦЕЛЬ ИЗ СТИГМЕРГИЧЕСКОЙ ПАМЯТИ",

                    "| Поле | Значение |",

                    "|------|----------|",

                    f"| Фаза | {goal_state.get('phase', 'N/A')} |",

                    f"| Приоритет | {goal_state.get('priority', 'N/A')} |",

                    f"| Целевой β₀ | {target_topology.get('b0', 'N/A')} |",

                    f"| Целевой β₁ | {target_topology.get('b1', 'N/A')} |",

                    f"| Целевой χ | {target_topology.get('chi', 'N/A')} |",

                    "",

                ]

            )

        lines.extend(

            [

                "## НАБЛЮДЕНИЯ АГЕНТА",

                observations,

                "",

                "## ВЫВОДЫ",

                conclusions,

                "",

                "## УСПЕХИ",

                successes,

                "",

                "## НЕУДАЧИ",

                failures,

                "",

                "## СЛЕДУЮЩИЕ ШАГИ",

                next_steps,

                "",

                "## ДЕЙСТВИЕ",

                f"**Выбрано:** {parsed_action.get('action', 'N/A')}",

                f"**Параметры:** {json.dumps(parsed_action.get('params', {}), ensure_ascii=False)}",

                f"**Обоснование:** {parsed_action.get('justification', 'N/A')}",

                f"**Уверенность:** {self._safe_float(parsed_action.get('confidence', 0.5))}",

                "",

                "## РЕЗУЛЬТАТ ПРИМЕНЕНИЯ",

                json.dumps(action_result, indent=2, ensure_ascii=False),

                "",

                "## ИСТОРИЯ (последние 5 шагов)",

            ]

        )

        for entry in history[-5:]:

            step_h = entry.get("step", "?")

            sim_step_h = entry.get("sim_step", "?")

            b0_h = entry.get("b0", "?")

            b1_h = entry.get("b1", "?")

            action_h = entry.get("action", "?")

            lines.append(

                f"- Шаг {step_h} (sim {sim_step_h}): "

                f"β₀={b0_h}, β₁={b1_h}, действие={action_h}"

            )

        report_text = "\n".join(lines)

        self._save_report(report_text)

        self._update_summary(report_text)

        return report_text

    def _save_report(self, report_text):

        path = os.path.join(

            self.reports_dir,

            f"report_{self.report_count:04d}.md",

        )

        with open(path, "w", encoding="utf-8") as f:

            f.write(report_text)

        print(f"Отчёт сохранён: {path}")

    def _update_summary(self, report_text):

        path = os.path.join(self.reports_dir, "summary_latest.md")

        with open(path, "w", encoding="utf-8") as f:

            f.write(report_text)

    def generate_failure_report(

        self,

        step,

        sim_step,

        phase,

        error_description,

        context,

        traceback_str=None,

    ):

        self.report_count += 1

        lines = [

            f"# ОТЧЁТ ОБ ОШИБКЕ #{self.report_count:04d}",

            "",

            f"**Дата:** {datetime.now().isoformat()}",

            f"**Шаг:** {step}",

            f"**Фактический шаг симуляции:** {sim_step}",

            f"**Фаза:** {phase}",

            f"**Тип:** КРИТИЧЕСКАЯ ОШИБКА",

            f"**Версия спецификации:** {config.SPEC_VERSION}",

            "",

            "## ОПИСАНИЕ ОШИБКИ",

            error_description,

            "",

        ]

        if traceback_str:

            lines.extend(

                [

                    "## TRACEBACK",

                    "```",

                    traceback_str,

                    "```",

                    "",

                ]

            )

        lines.extend(

            [

                "## КОНТЕКСТ",

                context,

                "",

                "## РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ",

                "1. Проверить параметры конфигурации",

                "2. Уменьшить размер сетки до 32×32",

                "3. Уменьшить UNROLL_STEPS до 5",

                "4. Проверить память GPU: `nvidia-smi`",

                "5. Если ошибка повторяется — откатиться к последнему чекпоинту",

            ]

        )

        report_text = "\n".join(lines)

        failures_path = os.path.join(self.reports_dir, "failures_log.md")

        with open(failures_path, "a", encoding="utf-8") as f:

            f.write(report_text + "\n\n---\n\n")

        self._save_report(report_text)

        return report_text

    def generate_phase_summary(self, phase_name, results):

        self.report_count += 1

        success = results.get("success", False)

        status = "✅ УСПЕХ" if success else "❌ ПРОВАЛ"

        lines = [

            f"# ИТОГ ФАЗЫ: {phase_name}",

            "",

            f"**Дата:** {datetime.now().isoformat()}",

            f"**Статус:** {status}",

            f"**Версия спецификации:** {config.SPEC_VERSION}",

            f"**Ревизия:** {config.SPEC_REVISION}",

            "",

            "## РЕЗУЛЬТАТЫ",

        ]

        for key, value in results.items():

            lines.append(f"- **{key}:** {value}")

        lines.extend(

            [

                "",

                "## ВЫВОДЫ",

                results.get("conclusions", "Нет данных"),

                "",

                "## СЛЕДУЮЩАЯ ФАЗА",

                results.get("next_phase", "Не определена"),

            ]

        )

        report_text = "\n".join(lines)

        self._save_report(report_text)

        return report_text