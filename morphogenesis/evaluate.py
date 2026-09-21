"""

evaluate.py — Визуализация, оценка и морфогенетические вмешательства.

[v5.5-EXP FINAL Rev.7]

Ключевые требования:

- симметричный Chamfer как основная метрика геометрической галлюцинации;

- стресс-сводка с saturation_fraction;

- показатель Ляпунова с защитой от клампинга;

- гистерезис топологической галлюцинации;

- супервизия альфа-канала;

- защита стресс-канала от инъекций.

"""

import math

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import numpy as np

import torch

import torch.nn.functional as F

from scipy.ndimage import label, center_of_mass, distance_transform_edt

import config

from topology import (

    compute_topology_metrics,

    compute_extended_topology_metrics,

    _get_structure_8,

    _get_structure_4,

    remove_small_clusters,

    get_binary_mask,

    count_connected_components,

    count_holes,

)

from nca_core import run_steps_no_grad

def save_frame(model, state, step, save_dir=config.FRAMES_DIR):

    os.makedirs(save_dir, exist_ok=True)

    img = model.visible_image(state)[0, 0].detach().cpu().numpy()

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))

    ax.imshow(img, cmap="viridis", vmin=0, vmax=1)

    ax.set_title(f"Step {step}")

    ax.axis("off")

    plt.savefig(

        os.path.join(save_dir, f"frame_{step:06d}.png"),

        dpi=100,

        bbox_inches="tight",

    )

    plt.close(fig)

def compute_stress_summary(state):

    """

    Сводка по стресс-каналу.

    [Rev.7]: добавлен saturation_fraction.

    """

    if not config.STRESS_ENABLED:

        return {

            "enabled": False,

            "mean": 0.0,

            "max": 0.0,

            "std": 0.0,

            "saturated_fraction": 0.0,

        }

    stress = state[:, config.STRESS_CHANNEL:config.STRESS_CHANNEL + 1]

    stress = stress.detach().float()

    mean = float(stress.mean().item())

    max_value = float(stress.max().item())

    std = float(stress.std().item())

    saturated_fraction = float(

        (stress >= 0.9 * config.STRESS_MAX).float().mean().item()

    )

    return {

        "enabled": True,

        "mean": mean,

        "max": max_value,

        "std": std,

        "saturated_fraction": saturated_fraction,

    }

def compute_symmetric_chamfer_error(pred_mask, target_mask, grid_size=None):

    """

    Симметричная метрика расстояния между предсказанной и целевой бинарной маской.

    Штрафует и пропущенную массу, и лишнюю массу.

    Нормируется на диагональ сетки: GRID_SIZE * sqrt(2).

    pred_mask, target_mask: 2D numpy bool/uint8.

    """

    if grid_size is None:

        grid_size = config.GRID_SIZE

    diag = float(grid_size) * math.sqrt(2.0)

    pred_mask = np.asarray(pred_mask, dtype=bool)

    target_mask = np.asarray(target_mask, dtype=bool)

    dt_target = distance_transform_edt(~target_mask)

    dt_pred = distance_transform_edt(~pred_mask)

    large = diag

    if pred_mask.any():

        pred_to_target = float(dt_target[pred_mask].mean())

    else:

        pred_to_target = large

    if target_mask.any():

        target_to_pred = float(dt_pred[target_mask].mean())

    else:

        target_to_pred = large

    err = 0.5 * (pred_to_target + target_to_pred)

    return float(err / diag)

def compute_distance_transform_error(pred_mask, target_mask):

    """

    Диагностическая односторонняя метрика расстояния.

    Не является основной метрикой геометрической галлюцинации.

    """

    pred_mask = np.asarray(pred_mask, dtype=bool)

    target_mask = np.asarray(target_mask, dtype=bool)

    dt_target = distance_transform_edt(~target_mask)

    if pred_mask.any():

        return float(dt_target[pred_mask].mean())

    return float(config.GRID_SIZE)

def compute_lyapunov_exponent(model, state, steps=100, eps=1e-3):

    """

    Нормированный показатель Ляпунова.

    - Считается только по живым клеткам.

    - Канал 15 исключён из расхождения.

    - Канал 15 исключён из clamp_fraction.

    - Шаги с насыщением клампинга пропускаются.

    - При слишком малом расхождении шаг пропускается, возмущение переинициализируется.

    - Логируется число пропущенных шагов.

    [Rev.7]: если пропущено более 50% шагов, результат считается ненадёжным.

    """

    model.eval()

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.alive_mask_enabled = True

    perturbation = torch.randn_like(state) * eps

    state_b = state + perturbation

    lyap_sum = 0.0

    valid_steps = 0

    skipped_steps = 0

    with torch.no_grad():

        for t in range(steps):

            state = model(state)

            state_b = model(state_b)

            alive = (

                torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

                > config.ALIVE_THRESHOLD

            ).float().unsqueeze(1)

            clamp_mask = (state.abs() > config.STATE_CLAMP_MAX - 0.01)

            clamp_mask[:, config.STRESS_CHANNEL, :, :] = False

            clamp_fraction = clamp_mask.float().mean().item()

            if clamp_fraction > 0.05:

                skipped_steps += 1

                continue

            diff = (state - state_b).abs()

            diff[:, config.STRESS_CHANNEL, :, :] = 0.0

            diff = diff * alive

            d = diff.mean().item()

            if d < config.LYAPUNOV_MIN_DIST:

                skipped_steps += 1

                state_b = state + torch.randn_like(state) * eps

                continue

            lyap_sum += np.log(d / eps)

            valid_steps += 1

            state_b = state + (state_b - state) / d * eps

    model.alive_mask_enabled = was_alive

    if valid_steps == 0:

        return 0.0, valid_steps, skipped_steps

    lyapunov = lyap_sum / valid_steps

    return lyapunov, valid_steps, skipped_steps

def evaluate_model(model, state, target, n_steps=100):

    """

    Оценка модели.

    [v5.5-EXP FINAL Rev.7]:

    - model.eval();

    - alive_mask_enabled=True;

    - расширенные топологические метрики;

    - симметричный Chamfer;

    - мониторинг стресса;

    - гистерезис топологической галлюцинации;

    - восстановление исходного режима после оценки.

    """

    was_training = model.training

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.eval()

    model.alive_mask_enabled = True

    results = {

        "steps": [],

        "b0": [],

        "b1": [],

        "chi": [],

        "density": [],

        "pattern_error": [],

        "stress_mean": [],

        "spatial_entropy": [],

        "domain_wall_energy": [],

        "topological_hallucination": [],

        "geometric_hallucination": [],

        "symmetric_chamfer_error": [],

    }

    current_state = state.clone()

    hallucination_streak = 0

    geometric_hallucination_streak = 0

    for step in range(0, n_steps + 1, 10):

        if step > 0:

            current_state = run_steps_no_grad(model, current_state, steps=10)

        visible = model.visible_image(current_state)

        target_exp = target.expand(visible.shape[0], -1, -1, -1)

        pattern_err = float(torch.mean((visible - target_exp) ** 2).item())

        # Симметричный Chamfer.

        pred_mask = get_binary_mask(current_state)

        target_mask = (target[0, 0].detach().cpu().numpy() > 0.5).astype(np.uint8)

        sym_chamfer = compute_symmetric_chamfer_error(pred_mask, target_mask)

        topo = compute_extended_topology_metrics(

            current_state,

            target_topology=config.TARGET_TOPOLOGY,

            mse=pattern_err,

            symmetric_chamfer_error=sym_chamfer,

        )

        # Гистерезис топологической галлюцинации.

        if topo["topological_hallucination_raw"]:

            hallucination_streak += 1

        else:

            hallucination_streak = 0

        topological_hallucination = hallucination_streak >= config.HALLUCINATION_PERSISTENCE

        # Гистерезис геометрической галлюцинации.

        if topo["geometric_hallucination_raw"]:

            geometric_hallucination_streak += 1

        else:

            geometric_hallucination_streak = 0

        geometric_hallucination = geometric_hallucination_streak >= config.HALLUCINATION_PERSISTENCE

        stress_summary = compute_stress_summary(current_state)

        results["steps"].append(step)

        results["b0"].append(topo["b0"])

        results["b1"].append(topo["b1"])

        results["chi"].append(topo["chi"])

        results["density"].append(topo["density"])

        results["pattern_error"].append(pattern_err)

        results["stress_mean"].append(stress_summary["mean"])

        results["spatial_entropy"].append(topo["spatial_entropy"])

        results["domain_wall_energy"].append(topo["domain_wall_energy"])

        results["topological_hallucination"].append(topological_hallucination)

        results["geometric_hallucination"].append(geometric_hallucination)

        results["symmetric_chamfer_error"].append(sym_chamfer)

    if was_training:

        model.train()

    model.alive_mask_enabled = was_alive

    return results

def plot_evaluation(results, save_path=None):

    if not results["steps"]:

        return

    has_stress = len(results.get("stress_mean", [])) > 0

    if has_stress:

        fig, axes = plt.subplots(3, 2, figsize=(12, 14))

    else:

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    axes[0, 0].plot(results["steps"], results["b0"], "b-", label="β₀")

    axes[0, 0].plot(results["steps"], results["b1"], "r-", label="β₁")

    axes[0, 0].legend()

    axes[0, 0].set_title("Топология")

    axes[0, 1].plot(results["steps"], results["chi"], "g-")

    axes[0, 1].set_title("χ")

    axes[1, 0].plot(results["steps"], results["density"], "m-")

    axes[1, 0].set_title("Плотность")

    axes[1, 1].plot(results["steps"], results["pattern_error"], "r-")

    axes[1, 1].set_title("MSE")

    if has_stress:

        axes[2, 0].plot(results["steps"], results["stress_mean"], "orange")

        axes[2, 0].set_title("Stress mean")

        axes[2, 1].plot(

            results["steps"],

            results["spatial_entropy"],

            "purple",

        )

        axes[2, 1].set_title("Spatial entropy")

    plt.tight_layout()

    if save_path:

        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    plt.close(fig)

def apply_injury(state, injury_size=16, target_pattern=None):

    """

    Травма в центр конкретного кластера.

    Альфа-канал = DEAD_ALPHA_VALUE, чтобы рана была устойчиво мёртвой.

    """

    injured = state.clone()

    h, w = state.shape[2], state.shape[3]

    if target_pattern is not None:

        target_np = target_pattern[0, 0].detach().cpu().numpy()

        binary = target_np > 0.5

        structure = _get_structure_8()

        labeled, n_clusters = label(

            binary.astype(np.int32),

            structure=structure,

        )

        if n_clusters > 0:

            cluster_id = np.random.randint(1, n_clusters + 1)

            cy, cx = center_of_mass(binary, labeled, cluster_id)

            cx, cy = int(cx), int(cy)

        else:

            cx, cy = h // 2, w // 2

    else:

        cx, cy = h // 2, w // 2

    h0 = max(0, cy - injury_size // 2)

    h1 = min(h, h0 + injury_size)

    w0 = max(0, cx - injury_size // 2)

    w1 = min(w, w0 + injury_size)

    injured[:, :, h0:h1, w0:w1] = 0.0

    injured[:, config.ALIVE_CHANNEL, h0:h1, w0:w1] = config.DEAD_ALPHA_VALUE

    return injured

def _largest_alive_center(state):

    """

    Возвращает центр наибольшего живого кластера.

    Если живых кластеров нет — центр сетки.

    """

    alpha = torch.sigmoid(state[0, config.ALIVE_CHANNEL]).detach().cpu().numpy()

    binary = alpha > config.ALIVE_THRESHOLD

    binary = remove_small_clusters(binary)

    structure = _get_structure_8()

    labeled, n_clusters = label(

        binary.astype(np.int32),

        structure=structure,

    )

    if n_clusters == 0:

        return state.shape[2] // 2, state.shape[3] // 2

    sizes = np.bincount(labeled.ravel())[1:]

    largest_id = int(np.argmax(sizes)) + 1

    cy, cx = center_of_mass(binary, labeled, largest_id)

    return int(cy), int(cx)

def inject_morphogen(

    state,

    channel,

    value,

    x=None,

    y=None,

    radius=None,

):

    """

    Локальная инъекция морфогена в скрытый канал.

    [v5.5-EXP FINAL Rev.7]

    Правила:

    - каналы 0 и 1 не изменяются напрямую;

    - системный стресс-канал недоступен;

    - радиус ограничен;

    - если координаты не заданы, выбирается центр наибольшего живого кластера;

    - воздействие мягкое, с радиальным затуханием.

    """

    if state is None:

        raise ValueError("state обязателен для inject_morphogen")

    if channel is None:

        raise ValueError("channel обязателен для inject_morphogen")

    new_state = state.clone()

    _, C, H, W = new_state.shape

    channel = int(channel)

    if channel in config.RESERVED_SYSTEM_CHANNELS:

        raise ValueError(

            f"Канал {channel} зарезервирован под системные поля "

            f"и недоступен для INJECT_MORPHOGEN."

        )

    if not (

        config.MORPHOGEN_MIN_CHANNEL <= channel <= config.MORPHOGEN_MAX_CHANNEL

    ):

        raise ValueError(

            f"Морфогенный канал должен быть в "

            f"[{config.MORPHOGEN_MIN_CHANNEL}, {config.MORPHOGEN_MAX_CHANNEL}], "

            f"получено: {channel}"

        )

    if channel >= C:

        raise ValueError(f"Канал {channel} выходит за пределы N_CHANNELS={C}")

    value = float(value)

    value = max(config.MORPHOGEN_MIN_VALUE, min(config.MORPHOGEN_MAX_VALUE, value))

    if radius is None:

        radius = 4

    radius = int(radius)

    radius = max(config.MORPHOGEN_MIN_RADIUS, min(config.MORPHOGEN_MAX_RADIUS, radius))

    if x is None or y is None:

        y, x = _largest_alive_center(new_state)

    x = int(max(0, min(W - 1, x)))

    y = int(max(0, min(H - 1, y)))

    yy, xx = np.meshgrid(

        np.arange(H),

        np.arange(W),

        indexing="ij",

    )

    dist = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)

    falloff = np.clip(1.0 - dist / float(max(radius, 1)), 0.0, 1.0)

    field = np.zeros((H, W), dtype=np.float32)

    mask = dist <= radius

    field[mask] = value * falloff[mask]

    field_tensor = torch.from_numpy(field).to(state.device).unsqueeze(0)

    new_state[:, channel, :, :] = new_state[:, channel, :, :] + field_tensor

    new_state[:, channel, :, :] = torch.clamp(

        new_state[:, channel, :, :],

        config.STATE_CLAMP_MIN,

        config.STATE_CLAMP_MAX,

    )

    return new_state

def run_self_maintenance_probe(model, state, steps=None):

    """

    Проба самоподдержания.

    Система проходит несколько шагов без вмешательства.

    Измеряем, насколько хорошо она удерживает целевую топологию.

    """

    if steps is None:

        steps = config.MAINTENANCE_WINDOW

    steps = int(max(0, steps))

    was_training = model.training

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.eval()

    model.alive_mask_enabled = True

    current = state.clone()

    target_b0 = int(config.TARGET_TOPOLOGY["b0"])

    tolerance_b0 = int(config.TOPOLOGY_TOLERANCE_B0)

    checks = []

    b0_errors = []

    with torch.no_grad():

        for step in range(0, steps + 1, 10):

            if step > 0:

                current = run_steps_no_grad(model, current, steps=10)

            topo = compute_extended_topology_metrics(

                current,

                target_topology=config.TARGET_TOPOLOGY,

                mse=None,

            )

            b0_error = abs(int(topo["b0"]) - target_b0)

            checks.append(b0_error <= tolerance_b0)

            b0_errors.append(b0_error)

    persistence_fraction = 0.0

    if checks:

        persistence_fraction = float(sum(checks)) / float(len(checks))

    final_topo = compute_extended_topology_metrics(

        current,

        target_topology=config.TARGET_TOPOLOGY,

        mse=None,

    )

    final_stress = compute_stress_summary(current)

    if was_training:

        model.train()

    model.alive_mask_enabled = was_alive

    return {

        "steps": steps,

        "persistence_fraction": persistence_fraction,

        "final_b0": final_topo["b0"],

        "final_b1": final_topo["b1"],

        "final_chi": final_topo["chi"],

        "final_density": final_topo["density"],

        "final_spatial_entropy": final_topo["spatial_entropy"],

        "final_domain_wall_energy": final_topo["domain_wall_energy"],

        "final_topological_hallucination_raw": final_topo["topological_hallucination_raw"],

        "final_stress_mean": final_stress["mean"],

        "final_stress_max": final_stress["max"],

        "b0_errors": b0_errors,

    }

def apply_aging_noise(state, noise_std=None, generator=None):

    """

    Малый шум старения.

    Шум добавляется только в скрытые каналы из AGING_NOISE_CHANNELS.

    Каналы 0, 1 и стресс-канал не шумятся напрямую.

    [Rev.7]: поддержка детерминированного генератора.

    """

    if noise_std is None:

        noise_std = config.AGING_NOISE_STD

    if noise_std <= 0:

        return state.clone()

    noisy = state.clone()

    for channel in config.AGING_NOISE_CHANNELS:

        channel = int(channel)

        if 0 <= channel < noisy.shape[1]:

            if generator is not None:

                noise = torch.randn(

                    noisy[:, channel, :, :].shape,

                    generator=generator,

                    device=noisy.device,

                    dtype=noisy.dtype,

                ) * float(noise_std)

            else:

                noise = torch.randn_like(noisy[:, channel, :, :]) * float(noise_std)

            noisy[:, channel, :, :] = noisy[:, channel, :, :] + noise

    noisy = torch.clamp(

        noisy,

        config.STATE_CLAMP_MIN,

        config.STATE_CLAMP_MAX,

    )

    return noisy

def run_aging_protocol(

    model,

    state,

    steps=None,

    noise_std=None,

    target=None,

    log_every=10,

    generator=None,

):

    """

    Протокол старения.

    После достижения цели система продолжает работать без обучения,

    но с малым шумом в скрытых каналах.

    Измеряем:

    - рост пространственной энтропии;

    - дрейф β₀;

    - деградацию паттерна;

    - стресс.

    [Rev.7]: пре-регистрированные пороги деградации.

    """

    if steps is None:

        steps = config.AGING_STEPS

    if noise_std is None:

        noise_std = config.AGING_NOISE_STD

    steps = int(max(0, steps))

    log_every = int(max(1, log_every))

    was_training = model.training

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.eval()

    model.alive_mask_enabled = True

    current = state.clone()

    target_b0 = int(config.TARGET_TOPOLOGY["b0"])

    with torch.no_grad():

        initial_visible = model.visible_image(current)

        if target is not None:

            target_exp = target.expand(initial_visible.shape[0], -1, -1, -1)

            initial_mse = float(torch.mean((initial_visible - target_exp) ** 2).item())

        else:

            initial_mse = None

        initial_topo = compute_extended_topology_metrics(

            current,

            target_topology=config.TARGET_TOPOLOGY,

            mse=initial_mse,

        )

        initial_stress = compute_stress_summary(current)

        history = []

        for step in range(1, steps + 1):

            current = apply_aging_noise(current, noise_std=noise_std, generator=generator)

            current = model(current)

            if step % log_every == 0 or step == steps:

                visible = model.visible_image(current)

                if target is not None:

                    target_exp = target.expand(visible.shape[0], -1, -1, -1)

                    mse = float(torch.mean((visible - target_exp) ** 2).item())

                else:

                    mse = None

                topo = compute_extended_topology_metrics(

                    current,

                    target_topology=config.TARGET_TOPOLOGY,

                    mse=mse,

                )

                stress = compute_stress_summary(current)

                history.append(

                    {

                        "step": step,

                        "mse": mse,

                        "b0": topo["b0"],

                        "b1": topo["b1"],

                        "chi": topo["chi"],

                        "density": topo["density"],

                        "spatial_entropy": topo["spatial_entropy"],

                        "domain_wall_energy": topo["domain_wall_energy"],

                        "topological_hallucination_raw": topo["topological_hallucination_raw"],

                        "stress_mean": stress["mean"],

                        "stress_max": stress["max"],

                    }

                )

    if history:

        final = history[-1]

    else:

        final = {

            "step": 0,

            "mse": initial_mse,

            "b0": initial_topo["b0"],

            "b1": initial_topo["b1"],

            "chi": initial_topo["chi"],

            "density": initial_topo["density"],

            "spatial_entropy": initial_topo["spatial_entropy"],

            "domain_wall_energy": initial_topo["domain_wall_energy"],

            "topological_hallucination_raw": initial_topo["topological_hallucination_raw"],

            "stress_mean": initial_stress["mean"],

            "stress_max": initial_stress["max"],

        }

    entropy_increase = float(final["spatial_entropy"]) - float(

        initial_topo["spatial_entropy"]

    )

    initial_b0_error = abs(int(initial_topo["b0"]) - target_b0)

    final_b0_error = abs(int(final["b0"]) - target_b0)

    b0_error_increase = final_b0_error - initial_b0_error

    # Пре-регистрированные пороги деградации.

    aging_detected = bool(

        entropy_increase >= config.AGING_DEGRADATION_THRESHOLD_ENTROPY

        or b0_error_increase >= config.AGING_DEGRADATION_THRESHOLD_B0

    )

    if was_training:

        model.train()

    model.alive_mask_enabled = was_alive

    return {

        "steps": steps,

        "noise_std": float(noise_std),

        "initial": {

            "mse": initial_mse,

            "b0": initial_topo["b0"],

            "b1": initial_topo["b1"],

            "chi": initial_topo["chi"],

            "density": initial_topo["density"],

            "spatial_entropy": initial_topo["spatial_entropy"],

            "domain_wall_energy": initial_topo["domain_wall_energy"],

            "topological_hallucination_raw": initial_topo["topological_hallucination_raw"],

            "stress_mean": initial_stress["mean"],

            "stress_max": initial_stress["max"],

        },

        "final": final,

        "history": history,

        "entropy_increase": entropy_increase,

        "b0_error_increase": b0_error_increase,

        "aging_detected": aging_detected,

    }