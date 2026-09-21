"""

cognitive_loop.py — Главный цикл когнитивного контура.

[v5.5-EXP FINAL Rev.7]

Запуск:

python -m cognition.cognitive_loop "Фаза 7: Нарратив" 500 50

"""

import json

import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch

import config

from nca_core import (

    NeuralCellularAutomaton,

    run_steps_no_grad,

    init_state,

)

from config import create_deterministic_generator

from topology import compute_extended_topology_metrics, get_binary_mask

from target_patterns import create_target_circles

from evaluate import (

    apply_injury,

    save_frame,

    inject_morphogen,

    compute_symmetric_chamfer_error,

    compute_stress_summary,

)

from cognition.bridge import (

    encode_observation,

    build_agent_prompt,

    parse_agent_response,

    apply_action,

)

from cognition.action_validator import validate_action

from cognition.memory_manager import MemoryManager

from cognition.reporter import Reporter

from cognition.agent_backends import RuleBasedAgentV2

class CognitiveLoop:

    def __init__(

        self,

        phase="Фаза 7: Нарратив",

        report_interval=None,

        agent_backend=None,

        model=None,

        optimizer=None,

        generator=None,

    ):

        self.phase = phase

        self.step_size = int(getattr(config, "COGNITION_STEP_SIZE", 10))

        # Отчётный интервал по умолчанию из конфига.

        if report_interval is None:

            report_interval = int(getattr(config, "COGNITION_REPORT_INTERVAL", 20))

        self.report_interval = int(report_interval)

        # ПРАВИЛО 37: минимальный интервал = 2 * STEP_SIZE.

        min_interval = 2 * self.step_size

        if self.report_interval < min_interval:

            print(

                f"⚠️ report_interval {self.report_interval} < {min_interval}. "

                f"Автоматически повышен до {min_interval}."

            )

            self.report_interval = min_interval

        # Интервал должен быть кратен шагу.

        if self.report_interval % self.step_size != 0:

            self.report_interval = max(

                min_interval,

                round(self.report_interval / self.step_size) * self.step_size,

            )

        if agent_backend is None:

            agent_backend = RuleBasedAgentV2(default_steps=self.step_size)

        self.agent_backend = agent_backend

        self.model = model

        self.optimizer = optimizer

        self.generator = generator

        self.history = []

        self.decisions = []

        self.target = None

        self.memory = MemoryManager(memory_dir=config.MEMORY_DIR)

        self.reporter = Reporter(reports_dir=config.REPORTS_DIR)

        self.goal_state = self.memory.load_goal_state()

        # АТР-бюджет на отчёт.

        self.budget_remaining = float(config.INTERVENTION_BUDGET_PER_REPORT)

        # Кулдауны.

        # Разрешаем первую инъекцию морфогена сразу.

        self.last_morphogen_report = -int(config.MORPHOGEN_COOLDOWN_REPORTS + 1)

        self.last_injury_report = -int(config.INJURY_COOLDOWN_REPORTS + 1)

        self.morphogen_injections_this_report = 0

        # Гистерезис галлюцинаций.

        self.topological_hallucination_streak = 0

        self.geometric_hallucination_streak = 0

        # Предыдущий стресс для производной.

        self.prev_stress_mean = 0.0

        # Откат MODIFY_DT.

        self.rollback_state = None

        self.rollback_steps_remaining = 0

        os.makedirs(config.COGNITION_FRAMES_DIR, exist_ok=True)

    def _get_model_params(self):

        lr = config.LEARNING_RATE

        if self.optimizer is not None:

            lr = self.optimizer.param_groups[0]["lr"]

        target_b0 = config.TARGET_COMPONENTS

        if self.goal_state:

            target_topology = self.goal_state.get("target_topology", {})

            target_b0 = int(target_topology.get("b0", config.TARGET_COMPONENTS))

        return {

            "grid_size": config.GRID_SIZE,

            "n_channels": config.N_CHANNELS,

            "dt": self.model.dt if self.model else config.DT,

            "lr": lr,

            "l1_reg": config.L1_REG_WEIGHT,

            "target_b0": target_b0,

            "stress_enabled": config.STRESS_ENABLED,

            "stress_channel": config.STRESS_CHANNEL,

        }

    def _current_report_number(self):

        return self.reporter.report_count

    def _compute_symmetric_chamfer(self, state):

        """Симметричный Chamfer между состоянием и целью."""

        if self.target is None:

            return 0.0

        pred_mask = get_binary_mask(state)

        target_mask = (self.target[0, 0].detach().cpu().numpy() > 0.5).astype(np.uint8)

        return compute_symmetric_chamfer_error(pred_mask, target_mask)

    def observe(self, state, model_params, step=0, sim_step=0):

        symmetric_chamfer_error = self._compute_symmetric_chamfer(state)

        stress_summary = compute_stress_summary(state)

        stress_derivative = stress_summary["mean"] - self.prev_stress_mean

        self.prev_stress_mean = stress_summary["mean"]

        return encode_observation(

            state_tensor=state,

            model_params=model_params,

            history=self.history,

            step=step,

            sim_step=sim_step,

            model=self.model,

            budget=self.budget_remaining,

            goal_state=self.goal_state,

            symmetric_chamfer_error=symmetric_chamfer_error,

            stress_derivative=stress_derivative,

        )

    def _get_agent_response(self, prompt):

        response = self.agent_backend(prompt)

        if isinstance(response, dict):

            return json.dumps(response, ensure_ascii=False)

        return str(response)

    def _compute_extended_topology(self, state):

        """

        Расширенные топологические метрики с гистерезисом.

        """

        visible = self.model.visible_image(state)

        mse = None

        if self.target is not None:

            target_exp = self.target.expand(

                visible.shape[0],

                -1,

                -1,

                -1,

            )

            mse = float(torch.mean((visible - target_exp) ** 2).item())

        target_topology = config.TARGET_TOPOLOGY

        if self.goal_state:

            target_topology = self.goal_state.get(

                "target_topology",

                config.TARGET_TOPOLOGY,

            )

        symmetric_chamfer_error = self._compute_symmetric_chamfer(state)

        topo_raw = compute_extended_topology_metrics(

            state,

            target_topology=target_topology,

            mse=mse,

            symmetric_chamfer_error=symmetric_chamfer_error,

        )

        # Гистерезис топологической галлюцинации.

        if topo_raw["topological_hallucination_raw"]:

            self.topological_hallucination_streak += 1

        else:

            self.topological_hallucination_streak = 0

        topological_hallucination = (

            self.topological_hallucination_streak >= config.HALLUCINATION_PERSISTENCE

        )

        # Гистерезис геометрической галлюцинации.

        if topo_raw["geometric_hallucination_raw"]:

            self.geometric_hallucination_streak += 1

        else:

            self.geometric_hallucination_streak = 0

        geometric_hallucination = (

            self.geometric_hallucination_streak >= config.HALLUCINATION_PERSISTENCE

        )

        topo = dict(topo_raw)

        topo["topological_hallucination"] = topological_hallucination

        topo["geometric_hallucination"] = geometric_hallucination

        topo["symmetric_chamfer_error"] = symmetric_chamfer_error

        return topo, mse

    def _compute_topology(self, state):

        topo, _ = self._compute_extended_topology(state)

        return topo

    def _check_metrics_after_action(self, state, n_steps=None):

        if n_steps is None:

            n_steps = min(

                config.GRACE_WINDOW,

                max(0, self.report_interval - 1),

            )

        current = state.clone()

        if n_steps > 0:

            current = run_steps_no_grad(

                self.model,

                current,

                steps=n_steps,

            )

        topo, mse = self._compute_extended_topology(current)

        if mse is None:

            mse = 0.0

        return topo.get("b0", 0), mse, topo

    def _fallback_continue(self, reason):

        parsed = {

            "valid": True,

            "analysis": reason,

            "hypothesis": reason,

            "action": "CONTINUE_TRAINING",

            "params": {

                "steps": self.step_size,

            },

            "justification": reason,

            "confidence": 0.5,

            "report": {

                "stage": self.phase,

                "status": "В процессе",

                "observations": reason,

                "conclusions": "Действие заменено на CONTINUE_TRAINING.",

                "successes": "Бюджет и безопасность соблюдены.",

                "failures": "Исходное действие не прошло проверку.",

                "next_steps": "Продолжить наблюдение.",

            },

        }

        return parsed, 0.0

    def _enforce_budget_and_cooldown(self, parsed_action):

        """

        Единая точка валидации через action_validator.

        """

        if not parsed_action.get("valid", False):

            return parsed_action, 0.0

        validation = validate_action(

            parsed_action,

            budget_remaining=self.budget_remaining,

            current_report_number=self._current_report_number(),

            last_morphogen_report=self.last_morphogen_report,

            last_injury_report=self.last_injury_report,

            morphogen_injections_this_report=self.morphogen_injections_this_report,

        )

        if not validation["allowed"]:

            return self._fallback_continue(validation["reason"])

        return parsed_action, validation["cost"]

    def _apply_rollback_if_needed(self, state, b0_before, mse_before):

        """

        Проверка отката MODIFY_DT после GRACE_WINDOW.

        """

        if self.rollback_state is None or self.rollback_steps_remaining <= 0:

            return state

        b0_now = self._compute_topology(state)["b0"]

        mse_now = self._compute_symmetric_chamfer(state)

        b0_target = int(

            self.goal_state.get("target_topology", {}).get(

                "b0",

                config.TARGET_COMPONENTS,

            )

        )

        b0_before_err = abs(int(b0_before) - b0_target)

        b0_now_err = abs(int(b0_now) - b0_target)

        should_rollback = (

            (mse_now > mse_before + 0.05)

            or (b0_now_err > b0_before_err + 2)

        )

        if should_rollback:

            print(

                f"⚠️ Откат: MSE {mse_before:.4f}→{mse_now:.4f}, "

                f"|β₀-t| {b0_before_err}→{b0_now_err}"

            )

            config.DT = self.rollback_state["config_dt"]

            if self.model is not None:

                self.model.dt = self.rollback_state["model_dt"]

            self.rollback_state = None

            self.rollback_steps_remaining = 0

        return state

    def think_and_act(

        self,

        observation,

        current_state,

        step,

        sim_step,

        total_steps,

    ):

        recent = self.memory.load_recent_decisions(n=5)

        model_params = self._get_model_params()

        prompt = build_agent_prompt(

            observation=observation,

            target_b0=model_params["target_b0"],

            iteration=step,

            total_iterations=total_steps,

            recent_decisions=recent,

            sim_step=sim_step,

            budget=self.budget_remaining,

            goal_state=self.goal_state,

        )

        response_text = self._get_agent_response(prompt)

        parsed_action = parse_agent_response(response_text)

        if not parsed_action.get("valid"):

            report_text = self.reporter.generate_failure_report(

                step=step,

                sim_step=sim_step,

                phase=self.phase,

                error_description=(

                    f"Невалидный ответ: {parsed_action.get('error')}"

                ),

                context=f"Промпт:\n{prompt[:500]}...",

            )

            return (

                parsed_action,

                {

                    "applied": False,

                    "effective": False,

                    "rolled_back": False,

                    "changes": {},

                    "note": parsed_action.get("error"),

                    "cost": 0.0,

                },

                report_text,

                0.0,

            )

        parsed_action, expected_cost = self._enforce_budget_and_cooldown(

            parsed_action

        )

        b0_before, mse_before, topo_before = self._check_metrics_after_action(

            current_state

        )

        action_result = apply_action(

            parsed_action,

            model=self.model,

            optimizer=self.optimizer,

            target_generator=lambda: create_target_circles(

                device=config.DEVICE

            ),

            state=current_state,

            budget_remaining=self.budget_remaining,

            current_report_number=self._current_report_number(),

            last_morphogen_report=self.last_morphogen_report,

            last_injury_report=self.last_injury_report,

            morphogen_injections_this_report=self.morphogen_injections_this_report,

        )

        if (

            parsed_action["action"] == "MODIFY_TARGET_B0"

            and action_result.get("changes", {}).get("target_regenerated")

        ):

            self.target = create_target_circles(device=config.DEVICE)

        # Сохраняем состояние отката для MODIFY_DT.

        if (

            parsed_action["action"] == "MODIFY_DT"

            and action_result.get("effective", False)

        ):

            self.rollback_state = {

                "config_dt": action_result.get("rollback_state", {}).get(

                    "config_dt", config.DT

                ),

                "model_dt": action_result.get("rollback_state", {}).get(

                    "model_dt", self.model.dt if self.model else config.DT

                ),

                "mse_before": mse_before,

                "b0_before": b0_before,

                "step_applied": step,

                "sim_step_applied": sim_step,

            }

            self.rollback_steps_remaining = config.GRACE_WINDOW

        # Обновляем бюджет и кулдауны.

        cost = float(action_result.get("cost", expected_cost))

        if (

            parsed_action.get("valid", False)

            and action_result.get("applied", False)

            and action_result.get("effective", False)

            and not action_result.get("rolled_back", False)

            and cost > 0.0

        ):

            self.budget_remaining = max(0.0, self.budget_remaining - cost)

            if parsed_action["action"] == "INJECT_MORPHOGEN":

                self.last_morphogen_report = self._current_report_number()

                self.morphogen_injections_this_report += 1

            if parsed_action["action"] == "APPLY_INJURY":

                self.last_injury_report = self._current_report_number()

        else:

            cost = 0.0

        topo, _ = self._compute_extended_topology(current_state)

        stress_summary = compute_stress_summary(current_state)

        report_text = self.reporter.generate_report(

            step=step,

            sim_step=sim_step,

            phase=self.phase,

            parsed_action=parsed_action,

            action_result=action_result,

            topology_metrics=topo,

            history=self.history,

            stress_summary=stress_summary,

            cost=cost,

            budget_remaining=self.budget_remaining,

            goal_state=self.goal_state,

            symmetric_chamfer_error=topo.get("symmetric_chamfer_error"),

        )

        return parsed_action, action_result, report_text, cost

    def remember(

        self,

        step,

        sim_step,

        observation,

        parsed_action,

        action_result,

        topology_metrics=None,

        cost=0.0,

        stress_summary=None,

        symmetric_chamfer_error=None,

    ):

        model_params = self._get_model_params()

        self.memory.save_state(

            step=step,

            sim_step=sim_step,

            observation=observation,

            parsed_action=parsed_action,

            action_result=action_result,

            topology_metrics=topology_metrics,

            model_params=model_params,

            stress_summary=stress_summary,

            cost=cost,

            budget_remaining=self.budget_remaining,

            goal_state=self.goal_state,

            symmetric_chamfer_error=symmetric_chamfer_error,

        )

        b0 = topology_metrics.get("b0", "?") if topology_metrics else "?"

        b1 = topology_metrics.get("b1", "?") if topology_metrics else "?"

        self.history.append(

            {

                "step": step,

                "sim_step": sim_step,

                "action": parsed_action.get("action"),

                "b0": b0,

                "b1": b1,

            }

        )

        if len(self.history) > 100:

            self.history = self.history[-100:]

        self.decisions.append(

            {

                "action": parsed_action.get("action"),

                "justification": parsed_action.get("justification"),

                "cost": cost,

            }

        )

    def run(self, nca_model, state, target, total_steps=500):

        print(f"КОГНИТИВНЫЙ ЦИКЛ: {self.phase}")

        self.model = nca_model

        self.target = target

        self.model.eval()

        self.model.alive_mask_enabled = True

        current_state = state.clone()

        step = 0

        sim_step = 0

        self.goal_state["phase"] = self.phase

        self.memory.save_goal_state(self.goal_state)

        while step < total_steps:

            # Основной шаг.

            current_state = run_steps_no_grad(

                self.model,

                current_state,

                steps=self.step_size,

            )

            step += self.step_size

            sim_step += self.step_size

            # Проверяем откат.

            if self.rollback_steps_remaining > 0:

                self.rollback_steps_remaining -= self.step_size

                if self.rollback_steps_remaining <= 0:

                    current_state = self._apply_rollback_if_needed(

                        current_state,

                        self.rollback_state.get("b0_before", 0),

                        self.rollback_state.get("mse_before", 0.0),

                    )

            # Периодический сброс пула.

            # ПРАВИЛО 29: привязка к sim_step.

            # Примечание: здесь нет пула, но если он есть в будущем,

            # использовать pool.maybe_reset(sim_step).

            if step % self.report_interval == 0:

                # Новый отчётный интервал — новый бюджет.

                self.budget_remaining = float(config.INTERVENTION_BUDGET_PER_REPORT)

                self.morphogen_injections_this_report = 0

                model_params = self._get_model_params()

                observation = self.observe(

                    current_state,

                    model_params,

                    step=step,

                    sim_step=sim_step,

                )

                parsed, result, report, cost = self.think_and_act(

                    observation,

                    current_state,

                    step,

                    sim_step,

                    total_steps,

                )

                if parsed.get("valid"):

                    action = parsed["action"]

                    if action == "MODIFY_TARGET_B0":

                        new_b0 = int(config.TARGET_COMPONENTS)

                        self.target = create_target_circles(

                            n_circles=new_b0,

                            device=config.DEVICE,

                        )

                        self.goal_state["target_topology"] = {

                            "b0": new_b0,

                            "b1": 0,

                            "chi": new_b0,

                        }

                        self.goal_state["notes"] = (

                            "Цель изменена агентом через MODIFY_TARGET_B0."

                        )

                        self.memory.save_goal_state(self.goal_state)

                    elif action == "APPLY_INJURY":

                        b0_before = self._compute_topology(current_state)["b0"]

                        injury_size = int(

                            parsed.get("params", {}).get("size", 16)

                        )

                        current_state = apply_injury(

                            current_state,

                            injury_size,

                            target_pattern=self.target,

                        )

                        b0_after = self._compute_topology(current_state)["b0"]

                        if b0_after == b0_before and injury_size < 32:

                            injury_size = min(32, injury_size + 8)

                            current_state = apply_injury(

                                current_state,

                                injury_size,

                                target_pattern=self.target,

                            )

                            b0_after = self._compute_topology(current_state)["b0"]

                        if b0_after == b0_before:

                            print("⚠️ Травма не изменила β₀")

                            self.memory.save_theory(

                                name=f"injury_ineffective_step_{step}",

                                content=(

                                    f"Травма размера {injury_size} "

                                    f"не изменила β₀.\n"

                                    f"β₀ до: {b0_before}, после: {b0_after}.\n"

                                    f"Возможно, размер травмы недостаточен "

                                    f"или система уже устойчива."

                                ),

                            )

                    elif action == "INJECT_MORPHOGEN":

                        inj = result.get("changes", {}).get("morphogen", {})

                        if not inj:

                            inj = parsed.get("params", {})

                        topo_before = self._compute_topology(current_state)

                        current_state = inject_morphogen(

                            current_state,

                            channel=inj.get("channel"),

                            value=inj.get("value"),

                            x=inj.get("x"),

                            y=inj.get("y"),

                            radius=inj.get("radius"),

                        )

                        topo_after = self._compute_topology(current_state)

                        self.memory.save_morphogen_effects(

                            {

                                "step": step,

                                "sim_step": sim_step,

                                "channel": inj.get("channel"),

                                "value": inj.get("value"),

                                "radius": inj.get("radius"),

                                "x": inj.get("x"),

                                "y": inj.get("y"),

                                "b0_before": topo_before.get("b0"),

                                "b1_before": topo_before.get("b1"),

                                "b0_after": topo_after.get("b0"),

                                "b1_after": topo_after.get("b1"),

                                "density_before": topo_before.get("density"),

                                "density_after": topo_after.get("density"),

                                "cost": cost,

                            }

                        )

                    elif action == "STOP":

                        save_frame(

                            self.model,

                            current_state,

                            step,

                            save_dir=config.COGNITION_FRAMES_DIR,

                        )

                        break

                    elif action == "CONTINUE_TRAINING":

                        extra = int(

                            result.get("changes", {}).get("train_steps", 0)

                        )

                        extra = max(

                            0,

                            min(

                                extra,

                                config.MAX_EXTRA_STEPS_PER_REPORT,

                                self.report_interval - 1,

                            ),

                        )

                        if extra > 0:

                            current_state = run_steps_no_grad(

                                self.model,

                                current_state,

                                steps=extra,

                            )

                            sim_step += extra

                            # ПРАВИЛО 19: step НЕ сдвигаем.

                topo = self._compute_topology(current_state)

                stress_summary = compute_stress_summary(current_state)

                self.remember(

                    step=step,

                    sim_step=sim_step,

                    observation=observation,

                    parsed_action=parsed,

                    action_result=result,

                    topology_metrics=topo,

                    cost=cost,

                    stress_summary=stress_summary,

                    symmetric_chamfer_error=topo.get("symmetric_chamfer_error"),

                )

                save_frame(

                    self.model,

                    current_state,

                    step,

                    save_dir=config.COGNITION_FRAMES_DIR,

                )

        final_report = self.reporter.generate_phase_summary(

            phase_name=self.phase,

            results={

                "total_steps": step,

                "total_sim_steps": sim_step,

                "total_decisions": len(self.decisions),

                "budget_remaining": self.budget_remaining,

                "success": len(self.decisions) > 0,

                "conclusions": "Когнитивный цикл завершён.",

                "next_phase": "Фаза 8: Управление",

            },

        )

        return final_report

def run_cognitive_experiment(

    phase="Фаза 7: Нарратив",

    total_steps=500,

    report_interval=None,

    agent_backend=None,

    seed=None,

):

    checkpoint_path = os.path.join(

        config.CHECKPOINT_DIR,

        "nca_final.pt",

    )

    if not os.path.exists(checkpoint_path):

        print("ОШИБКА: Нет обученной модели.")

        return

    config.validate()

    if seed is None:

        seed = config.SEED

    config.set_seed(seed)

    generator = create_deterministic_generator(seed)

    step_size = int(getattr(config, "COGNITION_STEP_SIZE", 10))

    if total_steps % step_size != 0:

        total_steps = max(

            step_size,

            (total_steps // step_size) * step_size,

        )

    if report_interval is None:

        report_interval = int(getattr(config, "COGNITION_REPORT_INTERVAL", 20))

    if report_interval % step_size != 0:

        report_interval = max(

            step_size,

            round(report_interval / step_size) * step_size,

        )

    model = NeuralCellularAutomaton().to(config.DEVICE)

    model.set_generator(generator)

    checkpoint = torch.load(

        checkpoint_path,

        map_location=config.DEVICE,

        weights_only=False,

    )

    # Проверка метаданных чекпоинта.

    metadata = checkpoint.get("metadata", {})

    if metadata.get("spec_version") != config.SPEC_VERSION:

        print(

            f"⚠️ Предупреждение: чекпоинт имеет версию "

            f"{metadata.get('spec_version')}, "

            f"ожидалась {config.SPEC_VERSION}"

        )

    if metadata.get("grid_size") != config.GRID_SIZE:

        raise ValueError(

            f"Несовместимый чекпоинт: grid_size={metadata.get('grid_size')}, "

            f"конфиг={config.GRID_SIZE}"

        )

    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()

    model.alive_mask_enabled = True

    state = checkpoint.get("state", None)

    if state is None:

        state = init_state(device=config.DEVICE, generator=generator)

        state = run_steps_no_grad(model, state, steps=100)

    else:

        state = state.to(config.DEVICE)

    target = create_target_circles(device=config.DEVICE)

    loop = CognitiveLoop(

        phase=phase,

        report_interval=report_interval,

        agent_backend=agent_backend,

        model=model,

        optimizer=None,

        generator=generator,

    )

    final_report = loop.run(

        nca_model=model,

        state=state,

        target=target,

        total_steps=total_steps,

    )

    print("\n" + final_report)

if __name__ == "__main__":

    phase = "Фаза 7: Нарратив"

    total_steps = 500

    report_interval = 50

    if len(sys.argv) > 1:

        phase = sys.argv[1]

    if len(sys.argv) > 2:

        total_steps = int(sys.argv[2])

    if len(sys.argv) > 3:

        report_interval = int(sys.argv[3])

    run_cognitive_experiment(

        phase=phase,

        total_steps=total_steps,

        report_interval=report_interval,

    )
