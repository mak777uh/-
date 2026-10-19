"""

target_patterns.py — Создание целевых паттернов.

[v5.6-EXP FINAL Rev.11]

Совместимость:

- По умолчанию функции возвращают только тензор маски.

- Если нужен целевой топологический вектор, вызвать с return_topology=True.

Каждая цель имеет явный целевой топологический вектор:

    TARGET_TOPOLOGY = {"b0": int, "b1": int, "chi": int}

"""

import math

import numpy as np

import torch

import config

def topology_for_circles(n_circles):

    """

    Топологический вектор для n изолированных дисков.

    """

    n = int(n_circles)

    return {

        "b0": n,

        "b1": 0,

        "chi": n,

    }

def topology_for_ring():

    """

    Топологический вектор для одного кольца.

    """

    return {

        "b0": 1,

        "b1": 1,

        "chi": 0,

    }

def topology_for_grid(n_rows, n_cols):

    """

    Топологический вектор для прямоугольной сетки изолированных квадратов.

    """

    n = int(n_rows) * int(n_cols)

    return {

        "b0": n,

        "b1": 0,

        "chi": n,

    }

def topology_for_pattern(name):

    """

    Топологический вектор цели по её имени (§12.5.2: у каждой цели он известен).

    Берётся из реестра config.TARGET_PATTERN_TOPOLOGY — единственного источника,

    чтобы описание цели в отчёте не могло разойтись с самой маской.

    """

    if name not in config.TARGET_PATTERN_TOPOLOGY:

        raise KeyError(

            f"Неизвестная цель {name!r}; доступны: "

            f"{sorted(config.TARGET_PATTERN_TOPOLOGY)}"

        )

    return dict(config.TARGET_PATTERN_TOPOLOGY[name])

def create_target_circles(

    grid_size=config.GRID_SIZE,

    n_circles=config.TARGET_COMPONENTS,

    radius=8,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Создаёт целевую маску из n кругов.

    Если n=1 — круг в центре.

    Если n>1 — круги равномерно по окружности.

    """

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    centers = []

    if n_circles == 1:

        centers.append((grid_size // 2, grid_size // 2))

    else:

        for i in range(n_circles):

            angle = 2 * math.pi * i / n_circles

            cx = int(grid_size / 2 + (grid_size / 4) * math.cos(angle))

            cy = int(grid_size / 2 + (grid_size / 4) * math.sin(angle))

            centers.append((cx, cy))

    yy, xx = np.meshgrid(

        np.arange(grid_size),

        np.arange(grid_size),

        indexing="ij",

    )

    for cx, cy in centers:

        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)

        target[dist <= radius] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, topology_for_circles(n_circles)

    return tensor

def create_target_ring(

    grid_size=config.GRID_SIZE,

    radius=20,

    thickness=5,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Создаёт целевую маску в виде кольца.

    """

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    center = grid_size // 2

    yy, xx = np.meshgrid(

        np.arange(grid_size),

        np.arange(grid_size),

        indexing="ij",

    )

    dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2)

    target[np.abs(dist - radius) <= thickness / 2] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, topology_for_ring()

    return tensor

def create_target_grid(

    grid_size=config.GRID_SIZE,

    n_rows=3,

    n_cols=3,

    cell_size=5,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Создаёт целевую маску в виде прямоугольной сетки изолированных квадратов.

    """

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    spacing_x = grid_size // (n_cols + 1)

    spacing_y = grid_size // (n_rows + 1)

    for i in range(n_rows):

        for j in range(n_cols):

            cx = spacing_x * (j + 1)

            cy = spacing_y * (i + 1)

            x0 = max(0, cx - cell_size)

            x1 = min(grid_size, cx + cell_size)

            y0 = max(0, cy - cell_size)

            y1 = min(grid_size, cy + cell_size)

            target[y0:y1, x0:x1] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, topology_for_grid(n_rows, n_cols)

    return tensor

def _mesh(grid_size):

    """Координатная сетка (yy, xx) — один и тот же порядок во всех целях."""

    return np.meshgrid(np.arange(grid_size), np.arange(grid_size), indexing="ij")

def create_target_disk(

    grid_size=config.GRID_SIZE,

    radius=10,

    center=None,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Диск: β₀ = 1, β₁ = 0, χ = 1 (§12.5.1). Самая простая нетривиальная цель.

    """

    yy, xx = _mesh(grid_size)

    cy, cx = center if center is not None else (grid_size // 2, grid_size // 2)

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    target[np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) <= float(radius)] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, {"b0": 1, "b1": 0, "chi": 1}

    return tensor

def create_target_two_components(

    grid_size=config.GRID_SIZE,

    radius=8,

    gap=6,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Два раздельных диска: β₀ = 2, β₁ = 0, χ = 2 (§12.5.1).

    Цель проверяет именно β₀ — «схлопывание» двух компонент в одну для

    Chamfer почти невидимо.

    """

    yy, xx = _mesh(grid_size)

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    cy = grid_size // 2

    offset = (radius + gap // 2)

    for cx in (cy - offset, cy + offset):

        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)

        target[dist <= radius] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, {"b0": 2, "b1": 0, "chi": 2}

    return tensor

def create_target_boundary_ring(

    grid_size=config.GRID_SIZE,

    position=None,

    axis=None,

    radius=None,

    thickness=None,

    device=config.DEVICE,

    return_topology=False,

):

    """

    Кольцо, ЦЕНТР которого лежит на границе щелевых контактов (§12.5.4, E09).

    Требования спеки выполняются геометрически:

    - кольцо пересекает границу (радиус больше половины толщины любой половины);

    - левая и правая половины по отдельности — разомкнутые дуги, β₁ = 0;

    - β₁ = 1 возникает только при глобальной сборке.

    """

    position = int(config.GAP_JUNCTION_POSITION if position is None else position)

    axis = str(config.GAP_JUNCTION_AXIS if axis is None else axis)

    radius = float(config.GAP_JUNCTION_TARGET_RADIUS if radius is None else radius)

    thickness = float(

        config.GAP_JUNCTION_TARGET_THICKNESS if thickness is None else thickness

    )

    if axis not in ("x", "y"):

        raise ValueError(f"axis должен быть 'x' или 'y', получено {axis!r}")

    yy, xx = _mesh(grid_size)

    # Центр на границе и посередине перпендикулярной координаты.

    if axis == "x":

        cy, cx = grid_size // 2, position

    else:

        cy, cx = position, grid_size // 2

    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)

    target = np.zeros((grid_size, grid_size), dtype=np.float32)

    target[np.abs(dist - radius) <= thickness / 2.0] = 1.0

    tensor = torch.from_numpy(target).unsqueeze(0).unsqueeze(0).to(device)

    if return_topology:

        return tensor, topology_for_pattern("boundary_ring")

    return tensor

# Каталог целей §12.5: имя -> строитель.

TARGET_BUILDERS = {

    "ring": lambda gs, dev: create_target_ring(grid_size=gs, device=dev),

    "disk": lambda gs, dev: create_target_disk(grid_size=gs, device=dev),

    "two_components": lambda gs, dev: create_target_two_components(grid_size=gs, device=dev),

    "boundary_ring": lambda gs, dev: create_target_boundary_ring(grid_size=gs, device=dev),

    "three_circles": lambda gs, dev: create_target_circles(

        grid_size=gs, n_circles=config.TARGET_COMPONENTS, device=dev

    ),

}

def create_target(name=None, grid_size=config.GRID_SIZE, device=config.DEVICE, return_topology=False):

    """

    Единая точка создания активной цели (§12.5). Имя берётся из

    config.TARGET_PATTERN, если не передано, — поэтому train.py, эксперименты и

    когнитивный цикл физически строят ОДНУ и ту же цель.

    """

    key = str(config.TARGET_PATTERN if name is None else name)

    if key not in TARGET_BUILDERS:

        raise KeyError(

            f"Неизвестная цель {key!r}; каталог: {sorted(TARGET_BUILDERS)}"

        )

    tensor = TARGET_BUILDERS[key](grid_size, device)

    if return_topology:

        return tensor, topology_for_pattern(key)

    return tensor
