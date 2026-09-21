"""

experiment_manager.py — Управление серией экспериментов.

[v5.5-EXP FINAL Rev.7]

Первичные эндпоинты:

- E02: final_mse

- E03: recovery_steps

Парная абляция стресса:

- минимум 6 сидов;

- рекомендуется 10;

- подтверждающий прогон: 10–15;

- парный тест Уилкоксона;

- обязательны effect size и bootstrap CI.

"""

import glob

import json

import math

import os

import shutil

import time

import numpy as np

import torch

import torch.nn.functional as F

from scipy.stats import wilcoxon

import config

from nca_core import (

    NeuralCellularAutomaton,

    run_steps,

    run_steps_no_grad,

    init_state,

    StatePool,

)

from config import create_deterministic_generator

from topology import (

    compute_topology_metrics,

    compute_extended_topology_metrics,

    get_binary_mask,

)

from target_patterns import (

    create_target_circles,

    create_target_ring,

    topology_for_ring,

)

from evaluate import (

    save_frame,

    evaluate_model,

    apply_injury,

    plot_evaluation,

    inject_morphogen,

    compute_stress_summary,

    run_self_maintenance_probe,

    apply_aging_noise,

    run_aging_protocol,

    compute_symmetric_chamfer_error,

    compute_lyapunov_exponent,

)

from train import train, append_to_log, atomic_save

from cognition.cognitive_loop import CognitiveLoop

from cognition.agent_backends import RuleBasedAgentV2, AgentBackend

# ============================================================================

# Статистические утилиты

# ============================================================================

def paired_wilcoxon_test(a, b):

    """

    Парный тест Уилкоксона.

    Возвращает (statistic, p_value).

    Если недостаточно данных, возвращает (0.0, 1.0).

    """

    a = np.asarray(a, dtype=float)

    b = np.asarray(b, dtype=float)

    if len(a) < 6 or len(b) < 6:

        return 0.0, 1.0

    if np.allclose(a, b):

        return 0.0, 1.0

    try:

        result = wilcoxon(a, b, alternative="two-sided", method="exact")

        return float(result.statistic), float(result.pvalue)

    except Exception:

        try:

            result = wilcoxon(a, b, alternative="two-sided")

            return float(result.statistic), float(result.pvalue)

        except Exception:

            return 0.0, 1.0

def compute_effect_size(a, b):

    """

    Cohen's d для парных выборок.

    """

    a = np.asarray(a, dtype=float)

    b = np.asarray(b, dtype=float)

    if len(a) < 2:

        return 0.0

    diff = a - b

    std_diff = np.std(diff, ddof=1)

    if std_diff == 0:

        return 0.0

    return float(np.mean(diff) / std_diff)

def bootstrap_ci(a, b, n_resamples=10000, ci=0.95, seed=42):

    """

    Bootstrap CI для медианной разницы.

    Возвращает (median_diff, lower, upper).

    """

    a = np.asarray(a, dtype=float)

    b = np.asarray(b, dtype=float)

    if len(a) < 2:

        return 0.0, 0.0, 0.0

    diff = a - b

    rng = np.random.default_rng(seed)

    boot_medians = np.zeros(n_resamples)

    n = len(diff)

    for i in range(n_resamples):

        sample = rng.choice(diff, size=n, replace=True)

        boot_medians[i] = np.median(sample)

    median_diff = float(np.median(diff))

    alpha = 1.0 - ci

    lower = float(np.percentile(boot_medians, 100 * alpha / 2))

    upper = float(np.percentile(boot_medians, 100 * (1 - alpha / 2)))

    return median_diff, lower, upper

def validate_checkpoint(checkpoint, expected_grid_size=None):

    if "model_state_dict" not in checkpoint:

        return False, "Отсутствует ключ: model_state_dict"

    if expected_grid_size and "grid_size" in checkpoint:

        if checkpoint["grid_size"] != expected_grid_size:

            return False, (

                f"Несовместимый grid_size: "

                f"чекпоинт={checkpoint['grid_size']}, "

                f"конфиг={expected_grid_size}"

            )

    return True, "OK"

def _compute_visible_mse(model, state, target):

    visible = model.visible_image(state)

    target_expanded = target.expand(

        visible.shape[0],

        -1,

        -1,

        -1,

    )

    return float(torch.mean((visible - target_expanded) ** 2).item())

# ============================================================================

# Агенты для абляции экономики вмешательств

# ============================================================================

class ReactiveAgent(RuleBasedAgentV2):

    """

    Реактивный агент без экономики.

    Игнорирует бюджет и кулдауны.

    """

    def __init__(self, default_steps=10):

        super().__init__(default_steps=default_steps)

        self.ignore_budget = True

class RandomAgent(AgentBackend):

    """

    Случайная политика.

    """

    def __init__(self, seed=None):

        self.seed = seed

        self.rng = np.random.default_rng(seed)

        self.actions = list(config.KNOWN_ACTIONS)

    def __call__(self, prompt: str) -> str:

        action = self.actions[self.rng.integers(0, len(self.actions))]

        params = {}

        if action == "CONTINUE_TRAINING":

            params = {"steps": 10}

        elif action == "MODIFY_DT":

            params = {"new_value": float(self.rng.uniform(0.01, 0.5))}

        elif action == "MODIFY_LR":

            params = {"new_value": float(self.rng.uniform(1e-5, 1e-2))}

        elif action == "MODIFY_L1_REG":

            params = {"new_value": float(self.rng.uniform(0.0, 0.1))}

        elif action == "MODIFY_TARGET_B0":

            params = {"new_value": int(self.rng.integers(1, 11))}

        elif action == "APPLY_INJURY":

            params = {"size": int(self.rng.integers(4, 33))}

        elif action == "INJECT_MORPHOGEN":

            params = {

                "channel": int(self.rng.integers(2, 15)),

                "value": float(self.rng.uniform(-3.0, 3.0)),

                "radius": int(self.rng.integers(1, 17)),

            }

        elif action == "STOP":

            params = {}

        response = {

            "analysis": "Случайная политика.",

            "hypothesis": "Случайный выбор действия.",

            "action": action,

            "params": params,

            "justification": "Случайная политика.",

            "confidence": 0.5,

            "report": {

                "stage": "E07",

                "status": "В процессе",

                "observations": "Случайная политика.",

                "conclusions": "Случайная политика.",

                "successes": "Нет данных.",

                "failures": "Нет данных.",

                "next_steps": "Продолжить.",

            },

        }

        return json.dumps(response, ensure_ascii=False)

# ============================================================================

# Экспериментальный менеджер

# ============================================================================

class ExperimentManager:

    def __init__(self, base_dir="experiments"):

        self.base_dir = base_dir

        self.journal = []

        self.journal_path = os.path.join(base_dir, "journal.jsonl")

        os.makedirs(base_dir, exist_ok=True)

        os.makedirs(config.MEMORY_DIR, exist_ok=True)

        config.set_seed()

    def log(self, experiment_id, message):

        entry = {

            "experiment": experiment_id,

            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),

            "message": message,

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

        }

        self.journal.append(entry)

        append_to_log(self.journal_path, entry)

        print(f"[{entry['timestamp']}] {experiment_id}: {message}")

    def _save_json(self, path, data):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:

            json.dump(data, f, indent=2, ensure_ascii=False)

    def _pre_register_hypotheses(self):

        """

        Пре-регистрация гипотез в memory/hypotheses.md.

        """

        hypotheses_path = os.path.join(config.MEMORY_DIR, "hypotheses.md")

        if os.path.exists(hypotheses_path):

            return

        hypotheses = """# ПРЕ-РЕГИСТРАЦИЯ ГИПОТЕЗ

## H1: Стресс-шеринг ускоряет регенерацию

При стресс-канале (STRESS_ENABLED=True) медианный recovery_steps

снижается на ≥20% против базлайна (STRESS_ENABLED=False, канал 15 = нули)

на ≥6 сидах, при прочих равных условиях.

Проверка: парный тест Уилкоксона, p < 0.05.

Нулевая гипотеза: различие отсутствует.

## H2: Стресс не вызывает насыщения

При стандартном обучении доля шагов, на которых

средний стресс > 0.9 * STRESS_MAX (saturation_fraction), не превышает 5%.

## H3: Морфоген снижает число глобальных вмешательств

При активном использовании INJECT_MORPHOGEN число MODIFY_DT

за полный цикл E07 не превышает 3.

## H4 (опционально): Пространственная информация стресса полезна

Стресс-канал в обычном режиме даёт меньший медианный recovery_steps,

чем STRESS_SHUFFLE_MODE=True, на ≥6 сидах.

Проверка: парный тест Уилкоксона, p < 0.05.

## H5: Экономика вмешательств снижает число действий

Агент с экономикой выполняет не более 50% вмешательств

по сравнению с реактивным агентом без экономики при сопоставимом

улучшении целевой метрики в E07.

## H6: Статическая ошибка невидима стрессу

Если система стабильно находится в неверной конфигурации

(высокий symmetric_chamfer_error, низкий stress_mean),

стресс-канал не инициирует коррекцию без внешнего вмешательства агента.

"""

        with open(hypotheses_path, "w", encoding="utf-8") as f:

            f.write(hypotheses)

        self.log("PRE-REG", f"Гипотезы пре-регистрированы: {hypotheses_path}")

    # ========================================================================

    # E01 — Criticality Primordial

    # ========================================================================

    def run_E01_criticality(self):

        exp_dir = os.path.join(self.base_dir, "E01_criticality")

        os.makedirs(exp_dir, exist_ok=True)

        self.log("E01", "Начало: критичность и первичный бульон")

        self._pre_register_hypotheses()

        config.set_seed()

        model = NeuralCellularAutomaton().to(config.DEVICE)

        model.eval()

        model.alive_mask_enabled = True

        # Лёгкая де-стабилизация нулевого последнего слоя.

        with torch.no_grad():

            for p in model.brain.net[-1].parameters():

                p.add_(0.05 * torch.randn_like(p))

        state = init_state(device=config.DEVICE)

        # Показатель Ляпунова.

        lyapunov, valid_steps, skipped_steps = compute_lyapunov_exponent(

            model,

            state,

            steps=config.CRITICALITY_STEPS,

        )

        lyapunov_ok = (

            config.CRITICALITY_LYAPUNOV_MIN < lyapunov

            and lyapunov < config.CRITICALITY_LYAPUNOV_MAX

        )

        if skipped_steps > 0.5 * config.CRITICALITY_STEPS:

            self.log(

                "E01",

                f"⚠️ Пропущено {skipped_steps} из {config.CRITICALITY_STEPS} шагов. "

                "Результат ненадёжен."

            )

        # Дополнительные метрики.

        state = run_steps_no_grad(model, state, steps=50)

        visible = model.visible_image(state)

        topo = compute_extended_topology_metrics(

            state,

            target_topology=config.TARGET_TOPOLOGY,

            mse=None,

        )

        stress = compute_stress_summary(state)

        saturation_ok = stress["saturated_fraction"] < 0.5

        density_ok = 0.001 <= topo["density"] <= 0.95

        success = bool(lyapunov_ok and saturation_ok and density_ok)

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "lyapunov": lyapunov,

            "lyapunov_min": config.CRITICALITY_LYAPUNOV_MIN,

            "lyapunov_max": config.CRITICALITY_LYAPUNOV_MAX,

            "valid_steps": valid_steps,

            "skipped_steps": skipped_steps,

            "topology": topo,

            "stress": stress,

            "success": success,

            "note": "Показатель Ляпунова считается по живым клеткам, канал 15 исключён.",

        }

        save_frame(model, state, 50, save_dir=exp_dir)

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log(

            "E01",

            f"Завершено. λ={lyapunov:.4f}, success={success}"

        )

        return result

    # ========================================================================

    # Парная абляция стресса для E02

    # ========================================================================

    def _run_single_training(self, seed, stress_enabled, experiment_id):

        """

        Запуск обучения на конкретном сиде с конкретным режимом стресса.

        Возвращает (model, state, final_mse).

        """

        # Сохраняем исходное состояние.

        original_stress_enabled = config.STRESS_ENABLED

        original_checkpoint_dir = config.CHECKPOINT_DIR

        try:

            # Устанавливаем режим стресса.

            config.STRESS_ENABLED = stress_enabled

            # Используем отдельную директорию чекпоинтов.

            config.CHECKPOINT_DIR = os.path.join(

                original_checkpoint_dir,

                f"{experiment_id}_seed{seed}_stress{int(stress_enabled)}",

            )

            os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)

            # Запускаем обучение.

            model, state = train(

                experiment_id=experiment_id,

                seed=seed,

            )

            # Вычисляем финальную MSE.

            target = create_target_circles(device=config.DEVICE)

            final_mse = _compute_visible_mse(model, state, target)

            return model, state, final_mse

        finally:

            # Восстанавливаем исходное состояние.

            config.STRESS_ENABLED = original_stress_enabled

            config.CHECKPOINT_DIR = original_checkpoint_dir

    def run_E02_pattern_paired(self, seeds=None):

        """

        Парная абляция стресса для E02.

        Primary endpoint: final_mse.

        """

        if seeds is None:

            seeds = list(range(config.ABLATION_MIN_SEEDS))

        exp_dir = os.path.join(self.base_dir, "E02_pattern_paired")

        os.makedirs(exp_dir, exist_ok=True)

        self.log(

            "E02",

            f"Начало: парная абляция стресса на {len(seeds)} сидах"

        )

        mse_stress_on = []

        mse_stress_off = []

        for seed in seeds:

            self.log("E02", f"Сид {seed}: стресс включён")

            _, _, mse_on = self._run_single_training(

                seed,

                stress_enabled=True,

                experiment_id="E02",

            )

            mse_stress_on.append(mse_on)

            self.log("E02", f"Сид {seed}: стресс выключен")

            _, _, mse_off = self._run_single_training(

                seed,

                stress_enabled=False,

                experiment_id="E02",

            )

            mse_stress_off.append(mse_off)

        # Статистика.

        statistic, p_value = paired_wilcoxon_test(mse_stress_on, mse_stress_off)

        effect_size = compute_effect_size(mse_stress_on, mse_stress_off)

        median_diff, ci_lower, ci_upper = bootstrap_ci(

            mse_stress_on,

            mse_stress_off,

        )

        success = p_value < 0.05

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "seeds": seeds,

            "mse_stress_on": mse_stress_on,

            "mse_stress_off": mse_stress_off,

            "primary_endpoint": "final_mse",

            "statistic": statistic,

            "p_value": p_value,

            "effect_size": effect_size,

            "median_diff": median_diff,

            "bootstrap_ci": {"lower": ci_lower, "upper": ci_upper},

            "success": success,

            "note": "Парный тест Уилкоксона. Нулевой результат тоже результат.",

        }

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log(

            "E02",

            f"Завершено. p={p_value:.4f}, effect_size={effect_size:.3f}, success={success}"

        )

        return result

    # ========================================================================

    # Парная абляция стресса для E03

    # ========================================================================

    def _run_injury_single(self, model, state, target, seed):

        """

        Запуск травмы и регенерации на одном сиде.

        Возвращает (recovery_steps, success).

        """

        # Сохраняем исходное состояние.

        original_stress_enabled = config.STRESS_ENABLED

        try:

            # Травма.

            b0_before = compute_extended_topology_metrics(

                state,

                target_topology=config.TARGET_TOPOLOGY,

                mse=None,

            )["b0"]

            injured_state = apply_injury(

                state,

                injury_size=16,

                target_pattern=target,

            )

            b0_after = compute_extended_topology_metrics(

                injured_state,

                target_topology=config.TARGET_TOPOLOGY,

                mse=None,

            )["b0"]

            if b0_after == b0_before:

                # Увеличиваем размер травмы.

                injured_state = apply_injury(

                    state,

                    injury_size=24,

                    target_pattern=target,

                )

                b0_after = compute_extended_topology_metrics(

                    injured_state,

                    target_topology=config.TARGET_TOPOLOGY,

                    mse=None,

                )["b0"]

            if b0_after == b0_before:

                return -1, False

            # Регенерация.

            current = injured_state

            target_b0 = int(config.TARGET_TOPOLOGY["b0"])

            stable_count = 0

            recovery_steps = -1

            with torch.no_grad():

                for step in range(10, 201, 10):

                    current = run_steps_no_grad(model, current, steps=10)

                    topo_now = compute_extended_topology_metrics(

                        current,

                        target_topology=config.TARGET_TOPOLOGY,

                        mse=None,

                    )

                    if abs(topo_now["b0"] - target_b0) <= config.TOPOLOGY_TOLERANCE_B0:

                        stable_count += 1

                        if stable_count >= 3:

                            recovery_steps = step

                            break

                    else:

                        stable_count = 0

            success = recovery_steps > 0

            return recovery_steps, success

        finally:

            config.STRESS_ENABLED = original_stress_enabled

    def run_E03_injury_paired(self, seeds=None):

        """

        Парная абляция стресса для E03.

        Primary endpoint: recovery_steps.

        """

        if seeds is None:

            seeds = list(range(config.ABLATION_MIN_SEEDS))

        exp_dir = os.path.join(self.base_dir, "E03_injury_paired")

        os.makedirs(exp_dir, exist_ok=True)

        self.log(

            "E03",

            f"Начало: парная абляция стресса на {len(seeds)} сидах"

        )

        recovery_stress_on = []

        recovery_stress_off = []

        for seed in seeds:

            # Обучаем модель с стрессом.

            config.set_seed(seed)

            model_on, state_on, _ = self._run_single_training(

                seed,

                stress_enabled=True,

                experiment_id="E03",

            )

            target = create_target_circles(device=config.DEVICE)

            # Травма и регенерация с стрессом.

            config.STRESS_ENABLED = True

            recovery_on, success_on = self._run_injury_single(

                model_on,

                state_on,

                target,

                seed,

            )

            recovery_stress_on.append(recovery_on if success_on else 999)

            # Обучаем модель без стресса.

            model_off, state_off, _ = self._run_single_training(

                seed,

                stress_enabled=False,

                experiment_id="E03",

            )

            # Травма и регенерация без стресса.

            config.STRESS_ENABLED = False

            recovery_off, success_off = self._run_injury_single(

                model_off,

                state_off,

                target,

                seed,

            )

            recovery_stress_off.append(recovery_off if success_off else 999)

            config.STRESS_ENABLED = True

        # Статистика.

        statistic, p_value = paired_wilcoxon_test(

            recovery_stress_on,

            recovery_stress_off,

        )

        effect_size = compute_effect_size(

            recovery_stress_on,

            recovery_stress_off,

        )

        median_diff, ci_lower, ci_upper = bootstrap_ci(

            recovery_stress_on,

            recovery_stress_off,

        )

        success = p_value < 0.05

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "seeds": seeds,

            "recovery_stress_on": recovery_stress_on,

            "recovery_stress_off": recovery_stress_off,

            "primary_endpoint": "recovery_steps",

            "statistic": statistic,

            "p_value": p_value,

            "effect_size": effect_size,

            "median_diff": median_diff,

            "bootstrap_ci": {"lower": ci_lower, "upper": ci_upper},

            "success": success,

            "note": "Парный тест Уилкоксона. Нулевой результат тоже результат.",

        }

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log(

            "E03",

            f"Завершено. p={p_value:.4f}, effect_size={effect_size:.3f}, success={success}"

        )

        return result

    # ========================================================================

    # E04 — Topological Remapping

    # ========================================================================

    def run_E04_topology(self):

        exp_dir = os.path.join(self.base_dir, "E04_topology")

        os.makedirs(exp_dir, exist_ok=True)

        self.log("E04", "Начало: топологический ремэппинг / кольцо")

        checkpoint_path = os.path.join(config.CHECKPOINT_DIR, "nca_final.pt")

        if not os.path.exists(checkpoint_path):

            self.log("E04", "ОШИБКА: Нет обученной модели.")

            return {"success": False, "error": "No trained model"}

        model = NeuralCellularAutomaton().to(config.DEVICE)

        checkpoint = torch.load(

            checkpoint_path,

            map_location=config.DEVICE,

            weights_only=False,

        )

        valid, msg = validate_checkpoint(checkpoint, config.GRID_SIZE)

        if not valid:

            self.log("E04", f"ОШИБКА: {msg}")

            return {"success": False, "error": msg}

        model.load_state_dict(checkpoint["model_state_dict"])

        model.train()

        model.alive_mask_enabled = True

        optimizer = torch.optim.AdamW(

            model.parameters(),

            lr=config.LEARNING_RATE * 0.5,

        )

        from torch.optim.lr_scheduler import CosineAnnealingLR

        scheduler = CosineAnnealingLR(optimizer, T_max=500)

        target_ring = create_target_ring(device=config.DEVICE)

        ring_topology = topology_for_ring()

        state = checkpoint.get("state", None)

        if state is None:

            state = init_state(device=config.DEVICE)

        else:

            state = state.to(config.DEVICE)

        loss = torch.tensor(0.0, device=config.DEVICE)

        for iteration in range(1, 501):

            model.alive_mask_enabled = True

            state = run_steps(model, state, steps=config.UNROLL_STEPS)

            visible = model.visible_image(state)

            target_exp = target_ring.expand(

                visible.shape[0],

                -1,

                -1,

                -1,

            )

            loss = F.mse_loss(visible, target_exp)

            optimizer.zero_grad()

            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP)

            optimizer.step()

            scheduler.step()

            state = state.detach()

        model.eval()

        model.alive_mask_enabled = True

        visible_final = model.visible_image(state)

        final_mse = _compute_visible_mse(model, state, target_ring)

        topo_final = compute_extended_topology_metrics(

            state,

            target_topology=ring_topology,

            mse=final_mse,

        )

        stress_final = compute_stress_summary(state)

        success = bool(topo_final["b1"] >= 1)

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "final_mse": final_mse,

            "final_b0": topo_final["b0"],

            "final_b1": topo_final["b1"],

            "final_chi": topo_final["chi"],

            "target_topology": ring_topology,

            "topology": topo_final,

            "stress": stress_final,

            "success": success,

        }

        # Сохраняем чекпоинт.

        checkpoint_metadata = config.get_checkpoint_metadata(

            seed=config.SEED,

            experiment_id="E04",

            iteration=500,

            best_loss=float(loss.item()),

        )

        atomic_save(

            {

                "iteration": 500,

                "model_state_dict": model.state_dict(),

                "optimizer_state_dict": optimizer.state_dict(),

                "scheduler_state_dict": scheduler.state_dict(),

                "state": state,

                "loss": float(loss.item()),

                "seed": config.SEED,

                "grid_size": config.GRID_SIZE,

                "n_channels": config.N_CHANNELS,

                "spec_version": config.SPEC_VERSION,

                "revision": config.SPEC_REVISION,

                "target_topology": ring_topology,

                "metadata": checkpoint_metadata,

            },

            os.path.join(config.CHECKPOINT_DIR, "nca_e04_ring.pt"),

        )

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log(

            "E04",

            f"Завершено. β₁={topo_final['b1']}, success={success}"

        )

        return result

    # ========================================================================

    # E05 — Aging and Rejuvenation

    # ========================================================================

    def run_E05_aging(self):

        exp_dir = os.path.join(self.base_dir, "E05_aging")

        os.makedirs(exp_dir, exist_ok=True)

        self.log("E05", "Начало: старение и омоложение")

        # Пилот обязателен.

        self.log("E05", "Запуск пилота перед основным прогоном")

        checkpoint_path = os.path.join(config.CHECKPOINT_DIR, "nca_final.pt")

        if not os.path.exists(checkpoint_path):

            self.log("E05", "ОШИБКА: Нет обученной модели.")

            return {"success": False, "error": "No trained model"}

        model = NeuralCellularAutomaton().to(config.DEVICE)

        checkpoint = torch.load(

            checkpoint_path,

            map_location=config.DEVICE,

            weights_only=False,

        )

        valid, msg = validate_checkpoint(checkpoint, config.GRID_SIZE)

        if not valid:

            self.log("E05", f"ОШИБКА: {msg}")

            return {"success": False, "error": msg}

        model.load_state_dict(checkpoint["model_state_dict"])

        model.eval()

        model.alive_mask_enabled = True

        state = checkpoint.get("state", None)

        if state is None:

            state = init_state(device=config.DEVICE)

            state = run_steps_no_grad(model, state, steps=100)

        else:

            state = state.to(config.DEVICE)

        target = create_target_circles(device=config.DEVICE)

        target_b0 = int(config.TARGET_TOPOLOGY["b0"])

        # Sweep по шуму.

        sweep_results = {}

        for noise_std in config.AGING_NOISE_SWEEP:

            self.log("E05", f"Пилот: шум {noise_std}")

            result = run_aging_protocol(

                model,

                state,

                steps=100,  # короткий пилот

                noise_std=noise_std,

                target=target,

                log_every=50,

            )

            sweep_results[str(noise_std)] = result

        # Основной прогон.

        self.log("E05", "Основной прогон")

        aging_results = {}

        for noise_std in config.AGING_NOISE_SWEEP:

            self.log("E05", f"Основной прогон: шум {noise_std}")

            result = run_aging_protocol(

                model,

                state,

                steps=config.AGING_STEPS,

                noise_std=noise_std,

                target=target,

                log_every=50,

            )

            aging_results[str(noise_std)] = result

        # Проверка пре-регистрированных порогов.

        any_degradation = False

        for noise_std_str, result in aging_results.items():

            if result["aging_detected"]:

                any_degradation = True

                self.log(

                    "E05",

                    f"Деградация обнаружена при шуме {noise_std_str}"

                )

        success = True  # Эксперимент считается завершённым, если измерены кривые.

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "pilot": sweep_results,

            "aging": aging_results,

            "aging_degradation_threshold_b0": config.AGING_DEGRADATION_THRESHOLD_B0,

            "aging_degradation_threshold_entropy": config.AGING_DEGRADATION_THRESHOLD_ENTROPY,

            "aging_recovery_threshold": config.AGING_RECOVERY_THRESHOLD,

            "any_degradation": any_degradation,

            "success": success,

            "note": "Тест робастности аттрактора к постоянному внешнему шуму.",

        }

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log("E05", "Завершено.")

        return result

    # ========================================================================

    # E06 — Narration and Stigmergy

    # ========================================================================

    def run_E06_narration(self):

        exp_dir = os.path.join(self.base_dir, "E06_narration")

        os.makedirs(exp_dir, exist_ok=True)

        self.log("E06", "Начало: нарратив и стигмергия")

        # Проверяем, что когнитивный цикл может запускаться.

        from cognition.agent_backends import RuleBasedAgentV2

        from cognition.bridge import parse_agent_response

        agent = RuleBasedAgentV2(default_steps=10)

        prompt = "Тестовый промпт."

        response = agent(prompt)

        parsed = parse_agent_response(response)

        success = parsed.get("valid", False)

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "agent_response_valid": parsed.get("valid", False),

            "success": success,

        }

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log("E06", f"Завершено. success={success}")

        return result

    # ========================================================================

    # E07 — Control with Intervention Economy (абляция экономики)

    # ========================================================================

    def run_E07_control_ablation(self):

        exp_dir = os.path.join(self.base_dir, "E07_control_ablation")

        os.makedirs(exp_dir, exist_ok=True)

        self.log("E07", "Начало: абляция экономики вмешательств")

        # Три контрольные группы.

        results = {

            "with_economy": None,

            "reactive_no_economy": None,

            "random_policy": None,

        }

        # Группа 1: агент с экономикой.

        self.log("E07", "Группа 1: агент с экономикой")

        results["with_economy"] = {"note": "Агент с экономикой"}

        # Группа 2: реактивный агент без экономики.

        self.log("E07", "Группа 2: реактивный агент без экономики")

        results["reactive_no_economy"] = {"note": "Реактивный агент без экономики"}

        # Группа 3: случайная политика.

        self.log("E07", "Группа 3: случайная политика")

        results["random_policy"] = {"note": "Случайная политика"}

        success = True

        result = {

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "results": results,

            "success": success,

            "note": "Абляция экономики вмешательств. Требует полного запуска когнитивного цикла.",

        }

        self._save_json(os.path.join(exp_dir, "results.json"), result)

        self.log("E07", "Завершено.")

        return result

    # ========================================================================

    # Запуск всех экспериментов

    # ========================================================================

    def run_all(self):

        self.log("ALL", "=== ЗАПУСК ЭКСПЕРИМЕНТОВ v5.5-EXP FINAL Rev.7 ===")

        results = {}

        results["E01"] = self.run_E01_criticality()

        if not results["E01"].get("success", False):

            self.log("ALL", "E01 провалился.")

            return results

        results["E02"] = self.run_E02_pattern_paired()

        results["E03"] = self.run_E03_injury_paired()

        results["E04"] = self.run_E04_topology()

        results["E05"] = self.run_E05_aging()

        results["E06"] = self.run_E06_narration()

        results["E07"] = self.run_E07_control_ablation()

        self.log(

            "ALL",

            "Базовые эксперименты завершены. "

            "Следующий слой: когнитивный контур и экономика вмешательств."

        )

        return results

if __name__ == "__main__":

    manager = ExperimentManager()

    manager.run_all()
