"""

target_patterns.py — Создание целевых паттернов.

[v5.5-EXP FINAL Rev.7]

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