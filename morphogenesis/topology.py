"""

topology.py — Вычисление топологических инвариантов.

ТОЛЬКО МОНИТОРИНГ. Никаких дифференцируемых прокси.

[v5.5-EXP FINAL] Rev.7

Ключевые требования:

- двойственная связность: 8 для foreground, 4 для background/дырок;

- единая бинарная маска: (α > 0.5) AND (visible > 0.5);

- border-aware count_holes через компоненты фона с 4-связностью;

- вычисление симметричного Chamfer для обнаружения геометрических галлюцинаций;

- все вычисления на CPU.

"""

import math

import numpy as np

import torch

from scipy.ndimage import label, distance_transform_edt

import config

# === ДВОЙСТВЕННАЯ СВЯЗНОСТЬ ===

def _get_structure_8():

    """8-связность для переднего плана."""

    return np.ones((3, 3), dtype=int)

def _get_structure_4():

    """4-связность для фона / дырок."""

    return np.array(

        [

            [0, 1, 0],

            [1, 1, 1],

            [0, 1, 0],

        ],

        dtype=int,

    )

def _get_structure(connectivity=None):

    """

    Совместимая обёртка.

    По умолчанию 8-связность (для переднего плана).

    """

    if connectivity is None:

        connectivity = config.CONNECTIVITY

    if connectivity == 1:

        return _get_structure_4()

    return _get_structure_8()

# === ЕДИНАЯ БИНАРНАЯ МАСКА ===

def get_binary_mask(state, threshold=None):

    """

    ПРАВИЛО: единый source of truth для бинаризации.

    binary_mask = (sigmoid(alpha) > ALIVE_THRESHOLD) AND (sigmoid(visible) > BINARY_THRESHOLD)

    Принимает 4D состояние (B, C, H, W) или 3D (C, H, W).

    Возвращает 2D numpy bool mask (H, W) для первого батча.

    """

    if threshold is None:

        threshold = config.BINARY_THRESHOLD

    if isinstance(state, torch.Tensor):

        s = state.detach().cpu()

    else:

        s = torch.as_tensor(np.asarray(state))

    # Приводим к (B, C, H, W).

    if s.dim() == 2:

        raise ValueError("get_binary_mask ожидает состояние с каналами, а не 2D картинку.")

    if s.dim() == 3:

        s = s.unsqueeze(0)

    if s.dim() != 4:

        raise ValueError(f"Некорректная размерность состояния: {s.dim()}")

    alpha = torch.sigmoid(s[0, config.ALIVE_CHANNEL, :, :])

    visible = s[0, config.VISIBLE_CHANNEL, :, :]

    if config.USE_SIGMOID_VISIBLE:

        visible = torch.sigmoid(visible)

    mask = (alpha > config.ALIVE_THRESHOLD) & (visible > threshold)

    return mask.numpy().astype(np.uint8)

def tensor_to_binary(image_tensor, threshold=None):

    """

    Совместимость: бинаризация одиночного изображения.

    Для топологии лучше использовать get_binary_mask(state).

    """

    if threshold is None:

        threshold = config.BINARY_THRESHOLD

    if isinstance(image_tensor, torch.Tensor):

        img = image_tensor.detach().cpu().numpy()

    else:

        img = np.asarray(image_tensor)

    while img.ndim > 2:

        img = img[0]

    return img > threshold

def tensor_to_float_image(image_tensor):

    """

    Возвращает 2D float-изображение в [0, 1].

    """

    if isinstance(image_tensor, torch.Tensor):

        img = image_tensor.detach().cpu().numpy()

    else:

        img = np.asarray(image_tensor)

    while img.ndim > 2:

        img = img[0]

    img = np.asarray(img, dtype=np.float32)

    img = np.clip(img, 0.0, 1.0)

    return img

def remove_small_clusters(binary_mask, min_size=None):

    if min_size is None:

        min_size = config.MIN_CLUSTER_SIZE

    structure = _get_structure_8()

    labeled_array, n_components = label(

        binary_mask.astype(np.int32),

        structure=structure,

    )

    cleaned = np.zeros_like(binary_mask, dtype=bool)

    for i in range(1, n_components + 1):

        cluster = labeled_array == i

        if cluster.sum() >= min_size:

            cleaned = cleaned | cluster

    return cleaned

def count_connected_components(binary_mask, connectivity=None):

    """

    β₀: число компонент переднего плана.

    Всегда 8-связность для переднего плана.

    """

    structure = _get_structure_8()

    _, n_components = label(

        binary_mask.astype(np.int32),

        structure=structure,

    )

    return n_components

def count_holes(binary_mask, connectivity=None):

    """

    β₁: число дырок через компоненты фона с 4-связностью.

    Border-aware: вычитаем ВСЕ компоненты фона, касающиеся границы.

    ПРАВИЛО 24: фон для дырок — 4-связность.

    """

    binary_mask = binary_mask.astype(np.uint8)

    background = 1 - binary_mask

    structure_4 = _get_structure_4()

    labeled_bg, num_bg = label(background.astype(np.int32), structure=structure_4)

    if num_bg == 0:

        return 0

    border_labels = set()

    border_labels.update(labeled_bg[0, :].tolist())

    border_labels.update(labeled_bg[-1, :].tolist())

    border_labels.update(labeled_bg[:, 0].tolist())

    border_labels.update(labeled_bg[:, -1].tolist())

    border_labels.discard(0)

    holes = num_bg - len(border_labels)

    return max(holes, 0)

def compute_euler_characteristic(binary_mask):

    b0 = count_connected_components(binary_mask)

    b1 = count_holes(binary_mask)

    return b0 - b1

def compute_topology_metrics(image_tensor, clean=True):

    """

    Совместимая базовая функция.

    Принимает либо изображение, либо состояние. Если передано состояние

    с каналами, использует единую маску.

    """

    if isinstance(image_tensor, torch.Tensor) and image_tensor.dim() >= 3 and image_tensor.shape[-3] == config.N_CHANNELS:

        binary = get_binary_mask(image_tensor).astype(bool)

    else:

        binary = tensor_to_binary(image_tensor)

    if clean:

        binary = remove_small_clusters(binary)

    b0 = count_connected_components(binary)

    b1 = count_holes(binary)

    chi = b0 - b1

    density = float(binary.mean())

    if isinstance(image_tensor, torch.Tensor):

        mean_intensity = float(image_tensor.detach().cpu().numpy().mean())

    else:

        mean_intensity = float(np.asarray(image_tensor).mean())

    return {

        "b0": b0,

        "b1": b1,

        "chi": chi,

        "density": density,

        "mean_intensity": mean_intensity,

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

def _perimeter_estimate(binary_mask):

    """

    Грубая оценка периметра / доменных стенок.

    Используется 4-соседняя связность для периметра.

    """

    if binary_mask.sum() == 0:

        return 0.0

    padded = np.pad(

        binary_mask.astype(np.int8),

        pad_width=1,

        mode="constant",

        constant_values=0,

    )

    center = padded[1:-1, 1:-1]

    neighbors = (

        padded[:-2, 1:-1].astype(np.int8)

        + padded[2:, 1:-1].astype(np.int8)

        + padded[1:-1, :-2].astype(np.int8)

        + padded[1:-1, 2:].astype(np.int8)

    )

    transitions = np.logical_and(center == 1, neighbors == 0).sum()

    return float(transitions)

def _spatial_entropy(float_image, bins=16):

    """Нормированная пространственная энтропия видимого изображения."""

    if float_image.size == 0:

        return 0.0

    hist, _ = np.histogram(

        float_image.ravel(),

        bins=bins,

        range=(0.0, 1.0),

    )

    total = hist.sum()

    if total == 0:

        return 0.0

    p = hist.astype(np.float32) / float(total)

    entropy = -np.sum(p * np.log(p + 1e-12))

    entropy = entropy / np.log(bins)

    return float(entropy)

def compute_extended_topology_metrics(

    state_or_image,

    target_topology=None,

    mse=None,

    symmetric_chamfer_error=None,

    clean=True,

):

    """

    Расширенные топологические метрики для v5.5.

    Вход:

    - предпочтительно 4D состояние (B, C, H, W), чтобы использовать

      единую бинарную маску (α>0.5) AND (visible>0.5);

    - допускается 2D/3D изображение (совместимость).

    Возвращает сырые флаги галлюцинаций без гистерезиса.

    Гистерезис применяется в вызывающем коде (когнитивный цикл / train).

    """

    # Определяем, передано ли полное состояние.

    is_state = False

    if isinstance(state_or_image, torch.Tensor):

        if state_or_image.dim() >= 3:

            # (C,H,W) или (B,C,H,W) с C == N_CHANNELS

            c_dim = state_or_image.shape[-3]

            if c_dim == config.N_CHANNELS:

                is_state = True

    if is_state:

        binary_raw = get_binary_mask(state_or_image).astype(bool)

        # Для энтропии используем видимый канал.

        if isinstance(state_or_image, torch.Tensor):

            vis = state_or_image.detach().cpu()

        else:

            vis = torch.as_tensor(np.asarray(state_or_image))

        if vis.dim() == 3:

            vis = vis.unsqueeze(0)

        visible = vis[0, config.VISIBLE_CHANNEL]

        if config.USE_SIGMOID_VISIBLE:

            visible = torch.sigmoid(visible)

        float_image = visible.numpy().astype(np.float32)

        float_image = np.clip(float_image, 0.0, 1.0)

    else:

        binary_raw = tensor_to_binary(state_or_image)

        float_image = tensor_to_float_image(state_or_image)

    structure_8 = _get_structure_8()

    # Сырые кластеры для оценки мелких фрагментов.

    labeled_raw, n_raw = label(binary_raw.astype(np.int32), structure=structure_8)

    small_cluster_count = 0

    largest_cluster_size = 0

    if n_raw > 0:

        sizes = np.bincount(labeled_raw.ravel())[1:]

        if sizes.size > 0:

            small_cluster_count = int(np.sum(sizes < config.MIN_CLUSTER_SIZE))

            largest_cluster_size = int(np.max(sizes))

    binary = binary_raw

    if clean:

        binary = remove_small_clusters(binary_raw)

    b0 = count_connected_components(binary)

    b1 = count_holes(binary)

    chi = b0 - b1

    density = float(binary.mean())

    mean_intensity = float(float_image.mean())

    largest_cluster_fraction = 0.0

    if binary.size > 0:

        largest_cluster_fraction = float(largest_cluster_size) / float(binary.size)

    perimeter_estimate = _perimeter_estimate(binary)

    domain_wall_energy = 0.0

    if binary.size > 0 and perimeter_estimate > 0:

        domain_wall_energy = float(perimeter_estimate) / float(binary.size)

    compactness = 0.0

    area = float(binary.sum())

    if area > 0 and perimeter_estimate > 0:

        compactness = (4.0 * np.pi * area) / (perimeter_estimate * perimeter_estimate)

        compactness = float(np.clip(compactness, 0.0, 1.0))

    hole_area_total = 0

    largest_hole_area = 0

    if binary.sum() > 0:

        background = 1 - binary.astype(np.uint8)

        structure_4 = _get_structure_4()

        labeled_bg, num_bg = label(background.astype(np.int32), structure=structure_4)

        border_labels = set()

        border_labels.update(labeled_bg[0, :].tolist())

        border_labels.update(labeled_bg[-1, :].tolist())

        border_labels.update(labeled_bg[:, 0].tolist())

        border_labels.update(labeled_bg[:, -1].tolist())

        border_labels.discard(0)

        interior_bg = [i for i in range(1, num_bg + 1) if i not in border_labels]

        if interior_bg:

            hole_sizes = [int((labeled_bg == i).sum()) for i in interior_bg]

            hole_area_total = int(sum(hole_sizes))

            largest_hole_area = int(max(hole_sizes))

    spatial_entropy = _spatial_entropy(float_image)

    # === Сырые флаги галлюцинаций (без гистерезиса). ===

    topological_hallucination_raw = False

    if target_topology is not None and mse is not None:

        target_b0 = int(target_topology.get("b0", config.TARGET_TOPOLOGY["b0"]))

        target_b1 = int(target_topology.get("b1", config.TARGET_TOPOLOGY["b1"]))

        hallucination_by_b0 = abs(b0 - target_b0) > config.TOPOLOGY_TOLERANCE_B0

        hallucination_by_b1 = abs(b1 - target_b1) > config.TOPOLOGY_TOLERANCE_B1

        topological_hallucination_raw = bool(

            mse < config.MSE_HALLUCINATION_THRESHOLD

            and (hallucination_by_b0 or hallucination_by_b1)

        )

    geometric_hallucination_raw = False

    if symmetric_chamfer_error is not None:

        geometric_hallucination_raw = bool(

            symmetric_chamfer_error > config.SYMMETRIC_CHAMFER_HALLUCINATION_THRESHOLD

        )

    return {

        "b0": b0,

        "b1": b1,

        "chi": chi,

        "density": density,

        "mean_intensity": mean_intensity,

        "largest_cluster_fraction": largest_cluster_fraction,

        "small_cluster_count": small_cluster_count,

        "perimeter_estimate": perimeter_estimate,

        "compactness": compactness,

        "hole_area_total": hole_area_total,

        "largest_hole_area": largest_hole_area,

        "spatial_entropy": spatial_entropy,

        "domain_wall_energy": domain_wall_energy,

        "topological_hallucination_raw": topological_hallucination_raw,

        "geometric_hallucination_raw": geometric_hallucination_raw,

        # Совместимость со старым полем (сырое значение).

        "topological_hallucination": topological_hallucination_raw,

        "geometric_hallucination": geometric_hallucination_raw,

    }

def topology_loss_monitoring(current_metrics, target_b0=config.TARGET_COMPONENTS):

    """Для мониторинга (НЕ для обучения)."""

    return float((current_metrics["b0"] - target_b0) ** 2)
