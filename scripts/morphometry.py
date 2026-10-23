#!/usr/bin/env python
"""Морфометрия маски живости: периметр, размерность границы, случайная маска.

Зачем: у `struct_2` дескрипторы показали, что бинарная маска совпадает с маской
живости (binary_fraction = alive_fraction = 0.531), а текстура почти константна
(soft_mean 0.7615 ± 0.0035). Значит вопрос «где хранится форма» сводится к
геометрии этой маски, а не к текстуре. Этот скрипт меряет ровно её:

1. perimeter — длина границы маски (единичные рёбра на границе, 4-связность);
2. box dimension — фрактальная размерность границы (box-counting);
3. сравнение с случайной маской той же плотности: если периметр `struct_2`
   заметно меньше случайного, форма минимизирует границу — это структурный тезис;
4. разброс периметра между стартами против разброса площади: если периметр
   стабильнее площади, форма — топологический инвариант, а не геометрический;
5. `--mode correlation` — корреляция между расстоянием в начальном шуме и в
   финальном состоянии (шум или детерминированное расхождение);
6. `--mode randmask` — инициализация случайной маской той же плотности: распадётся
   ли она или станет `struct_2`.

Чистые функции (периметр, box-dim, случайная маска) тестируются без GPU:
`tests/test_morphometry.py`. GPU нужен только для режимов с чекпоинтом.

Запуск (cwd = morphogenesis):

    python ../scripts/morphometry.py --checkpoint checkpoints/E02c_R-9_s2000_seed42_tf32 \
        --mode boundary --starts 16
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
# скрипт лежит в repo/scripts, а код стенда — в repo/morphogenesis
MORPH = os.path.join(os.path.dirname(HERE), "morphogenesis")
if MORPH not in sys.path:
    sys.path.insert(0, MORPH)

import config  # noqa: E402
import nca_core  # noqa: E402
import topology  # noqa: E402


def mask_perimeter(mask: np.ndarray) -> int:
    """Длина границы маски: число единичных рёбер между mask и не-mask.

    Считаем по 4-связности: каждое ребро, где соседи различаются, плюс рёбра на
    краю поля, если клетка живая (у поля нет «внешней» мёртвой области).
    """
    m = np.asarray(mask).astype(bool)
    if m.ndim != 2:
        raise ValueError("ожидалась 2D маска")
    total = 0
    total += int(np.sum(m[1:, :] != m[:-1, :]))          # горизонтальные рёбра
    total += int(np.sum(m[:, 1:] != m[:, :-1]))          # вертикальные рёбра
    total += int(np.sum(m[0, :])) + int(np.sum(m[-1, :]))  # верх/низ поля
    total += int(np.sum(m[:, 0])) + int(np.sum(m[:, -1]))  # лево/право поля
    return total


def boundary_pixels(mask: np.ndarray) -> np.ndarray:
    """Пиксели маски, у которых есть сосед вне маски (или край поля)."""
    m = np.asarray(mask).astype(bool)
    padded = np.pad(m, 1, constant_values=False)
    neighbours = (
        padded[:-2, 1:-1] & padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:]
    )
    # клетка внутри маски и со всех сторон маска — не граница
    return m & ~neighbours


def box_counting_dimension(points: np.ndarray, max_box: int = 32) -> float:
    """Фрактальная размерность множества точек (box-counting) по log-log наклону."""
    pts = np.asarray(points, dtype=bool)
    if not pts.any():
        return float("nan")
    n = max(pts.shape)
    sizes, counts = [], []
    size = 1
    while size <= max_box and size <= n:
        # число занятых боксов размера `size`
        occupied = 0
        for i in range(0, pts.shape[0], size):
            for j in range(0, pts.shape[1], size):
                if pts[i : i + size, j : j + size].any():
                    occupied += 1
        sizes.append(size)
        counts.append(occupied)
        size *= 2
    if len(sizes) < 2:
        return float("nan")
    x = np.log(np.array(sizes, dtype=float))
    y = np.log(np.array(counts, dtype=float))
    slope = np.polyfit(x, y, 1)[0]
    return float(-slope)


def random_mask_baseline(shape: tuple[int, int], density: float, draws: int = 200, seed: int = 0) -> dict:
    """Средний периметр и box-dim случайных масок той же плотности."""
    rng = np.random.default_rng(seed)
    perims, dims = [], []
    for _ in range(draws):
        mask = rng.random(shape) < density
        perims.append(mask_perimeter(mask))
        dims.append(box_counting_dimension(boundary_pixels(mask)))
    return {
        "draws": draws,
        "density": float(density),
        "perimeter_mean": float(np.mean(perims)),
        "perimeter_std": float(np.std(perims)),
        "box_dim_mean": float(np.nanmean(dims)),
        "box_dim_std": float(np.nanstd(dims)),
    }


def expected_random_perimeter(shape: tuple[int, int], density: float) -> float:
    """Аналитическое ожидание периметра случайной маски на решётке (4-связность).

    Каждое из внутренних рёбер различается с вероятностью 2p(1-p); рёбра на краю
    поля считаются границей, если клетка живая (вероятность p). Отсюда
    E[P] = 2*[(h-1)*w + (w-1)*h]*p*(1-p) + 2*(h+w)*p.
    """
    h, w = shape
    internal = 2 * ((h - 1) * w + (w - 1) * h) * density * (1.0 - density)
    border = 2 * (h + w) * density
    return float(internal + border)


def isoperimetric_ratio(area: float, perimeter: float) -> float:
    """4*pi*A/P^2: 1 у круга, заметно меньше у изрезанной границы."""
    if perimeter <= 0:
        return float("nan")
    return float(4.0 * np.pi * area / (perimeter ** 2))


def local_density(mask: np.ndarray) -> np.ndarray:
    """Доля живых среди 8 соседей (по всему полю, с обрезкой на краях)."""
    m = np.asarray(mask).astype(float)
    padded = np.pad(m, 1, constant_values=0.0)
    acc = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            acc += padded[1 + dy : 1 + dy + m.shape[0], 1 + dx : 1 + dx + m.shape[1]]
    return acc / 8.0


def texture_stats(state, mask: np.ndarray) -> dict:
    """Контраст видимого канала внутри маски и его связь с плотностью соседей."""
    batch = state[0] if state.dim() == 4 else state
    visible = torch.sigmoid(batch[config.VISIBLE_CHANNEL]).detach().cpu().numpy()
    inside = np.asarray(visible)[mask].reshape(-1)
    dens = local_density(mask)[mask].reshape(-1)
    if inside.size < 2 or float(np.std(dens)) == 0.0 or float(np.std(inside)) == 0.0:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(inside, dens)[0, 1])
    return {
        "visible_mean_inside": float(inside.mean()) if inside.size else float("nan"),
        "visible_std_inside": float(inside.std()) if inside.size else float("nan"),
        "visible_min_inside": float(inside.min()) if inside.size else float("nan"),
        "visible_max_inside": float(inside.max()) if inside.size else float("nan"),
        "corr_visible_local_density": corr,
    }


def _build_model(checkpoint_dir: str, device: torch.device):
    import e02b_morphospace as e02b  # noqa: PLC0415 - тяжёлый импорт только здесь

    family = os.path.basename(os.path.normpath(checkpoint_dir))
    spec = e02b.CheckpointSpec(
        id=family,
        arm="R-9",
        family=family,
        path=os.path.join(checkpoint_dir, "nca_final.pt"),
        seed=42,
        steps_trained=2000,
        sha256=None,
        alive_mask_enabled=True,
    )
    model, _ = e02b.build_model(spec, device)
    return model, spec


def mode_boundary(model, spec, starts: int, rollout_steps: int, device) -> dict:
    import e02b_morphospace as e02b  # noqa: PLC0415

    rows = []
    for seed in range(starts):
        gen = e02b.prepare_model(model, seed)
        start = nca_core.init_state(
            batch_size=1,
            channels=config.N_CHANNELS,
            grid_size=config.GRID_SIZE,
            device=device,
            generator=gen,
        )
        final_state, _points, _traj, _elapsed = e02b.rollout(model, start, rollout_steps, 100)
        mask = topology.get_binary_mask(final_state)
        area = int(mask.sum())
        perim = mask_perimeter(mask)
        dim = box_counting_dimension(boundary_pixels(mask))
        tex = texture_stats(final_state, mask)
        holes = hole_morphology(mask)
        rows.append({
            "seed": seed,
            "area": area,
            "density": area / float(mask.size),
            "perimeter": perim,
            "box_dim": dim,
            "isoperimetric": isoperimetric_ratio(area, perim),
            "holes_n": holes["n"],
            "hole_compactness_mean": holes["shape_mean"],
            "hole_compactness_std": holes["shape_std"],
            **tex,
        })
    densities = [r["density"] for r in rows]
    baseline = random_mask_baseline(
        (config.GRID_SIZE, config.GRID_SIZE), float(np.mean(densities)), draws=100
    )
    perims = [r["perimeter"] for r in rows]
    areas = [r["area"] for r in rows]
    iso = [r["isoperimetric"] for r in rows]
    exp_perim = expected_random_perimeter((config.GRID_SIZE, config.GRID_SIZE), float(np.mean(densities)))
    return {
        "family": spec.family,
        "mode": "boundary",
        "starts": starts,
        "rollout_steps": rollout_steps,
        "rows": rows,
        "summary": {
            "density_mean": float(np.mean(densities)),
            "perimeter_mean": float(np.mean(perims)),
            "perimeter_std": float(np.std(perims)),
            "area_mean": float(np.mean(areas)),
            "area_std": float(np.std(areas)),
            "box_dim_mean": float(np.nanmean([r["box_dim"] for r in rows])),
            "isoperimetric_mean": float(np.nanmean(iso)),
            "isoperimetric_std": float(np.nanstd(iso)),
            "visible_std_inside_mean": float(np.nanmean([r["visible_std_inside"] for r in rows])),
            "corr_visible_local_density_mean": float(
                np.nanmean([r["corr_visible_local_density"] for r in rows])
            ),
            "random_baseline": baseline,
            "expected_random_perimeter": exp_perim,
            "perimeter_ratio_to_random": float(np.mean(perims) / baseline["perimeter_mean"])
            if baseline["perimeter_mean"] else float("nan"),
            "perimeter_ratio_to_analytic": float(np.mean(perims) / exp_perim) if exp_perim else float("nan"),
            "perimeter_cv": float(np.std(perims) / np.mean(perims)) if np.mean(perims) else float("nan"),
            "area_cv": float(np.std(areas) / np.mean(areas)) if np.mean(areas) else float("nan"),
            "isoperimetric_cv": float(np.nanstd(iso) / np.nanmean(iso)) if np.nanmean(iso) else float("nan"),
            "holes_n_mean": float(np.mean([r["holes_n"] for r in rows])),
            "hole_compactness_mean": float(np.nanmean([r["hole_compactness_mean"] for r in rows])),
            "hole_compactness_std": float(np.nanmean([r["hole_compactness_std"] for r in rows])),
        },
    }


def mode_randmask(model, spec, starts: int, rollout_steps: int, device,
                  density_override: float | None = None) -> dict:
    """Инициализировать случайной маской плотности эталона и посмотреть исход."""
    import e02b_morphospace as e02b  # noqa: PLC0415

    # эталон: обычный старт из шума
    gen = e02b.prepare_model(model, 0)
    start = nca_core.init_state(
        batch_size=1, channels=config.N_CHANNELS, grid_size=config.GRID_SIZE,
        device=device, generator=gen,
    )
    ref_state, _p, _t, _e = e02b.rollout(model, start, rollout_steps, 100)
    ref_mask = topology.get_binary_mask(ref_state)
    density = float(ref_mask.mean())
    if density_override is not None:
        density = float(density_override)

    rng = np.random.default_rng(1234)
    rows = []
    for i in range(starts):
        mask = rng.random((config.GRID_SIZE, config.GRID_SIZE)) < density
        state = torch.zeros(
            (1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE), device=device
        )
        # ставим видимый канал в +inf (после sigmoid -> 1) там, где маска
        vis = torch.full((config.GRID_SIZE, config.GRID_SIZE), -20.0, device=device)
        vis[torch.from_numpy(mask).to(device)] = 20.0
        state[0, config.VISIBLE_CHANNEL] = vis
        state[0, config.ALIVE_CHANNEL] = vis
        final_state, _p, _t, _e = e02b.rollout(model, state, rollout_steps, 100)
        final_mask = topology.get_binary_mask(final_state)
        inter = np.logical_and(final_mask, ref_mask).sum()
        union = np.logical_or(final_mask, ref_mask).sum()
        init_topo = components_and_holes(mask)
        final_topo = components_and_holes(final_mask)
        rows.append({
            "start": i,
            "init_density": density,
            "final_density": float(final_mask.mean()),
            "iou_with_reference": float(inter / union) if union else 0.0,
            "final_perimeter": mask_perimeter(final_mask),
            "init_b0": init_topo["b0"],
            "init_b1": init_topo["b1"],
            "final_b0": final_topo["b0"],
            "final_b1": final_topo["b1"],
        })
    return {
        "family": spec.family,
        "mode": "randmask",
        "starts": starts,
        "rollout_steps": rollout_steps,
        "reference_density": density,
        "rows": rows,
        "summary": {
            "reference_perimeter": mask_perimeter(ref_mask),
            "reference_b0": int(components_and_holes(ref_mask)["b0"]),
            "reference_b1": int(components_and_holes(ref_mask)["b1"]),
            "final_perimeter_mean": float(np.mean([r["final_perimeter"] for r in rows])),
            "init_b0_mean": float(np.mean([r["init_b0"] for r in rows])),
            "final_b0_mean": float(np.mean([r["final_b0"] for r in rows])),
            "init_b1_mean": float(np.mean([r["init_b1"] for r in rows])),
            "final_b1_mean": float(np.mean([r["final_b1"] for r in rows])),
            "iou_mean": float(np.mean([r["iou_with_reference"] for r in rows])),
            "density_after_mean": float(np.mean([r["final_density"] for r in rows])),
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--checkpoint", required=True, help="каталог с nca_final.pt")
    ap.add_argument("--mode", choices=["boundary", "randmask"], default="boundary")
    ap.add_argument("--starts", type=int, default=16)
    ap.add_argument("--rollout-steps", type=int, default=2000)
    ap.add_argument("--density", type=float, default=None,
                    help="переопределить плотность случайной маски (карта бассейна)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, spec = _build_model(args.checkpoint, device)
    if args.mode == "boundary":
        payload = mode_boundary(model, spec, args.starts, args.rollout_steps, device)
    else:
        payload = mode_randmask(model, spec, args.starts, args.rollout_steps, device,
                                density_override=args.density)

    out = args.out or os.path.join(
        "experiments", "E02c_replication", f"morphometry_{spec.family}_{args.mode}.json"
    )
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"[morphometry] {out}")
    return 0



# ---------- топология и корреляции маски (перколяционная проверка) ----------

def components_and_holes(mask: np.ndarray) -> dict:
    """Число компонент тела, дырок и эйлерова характеристика chi = b0 - b1.

    Дырки считаются по дополнению с учётом края: фон, касающийся края поля, — не
    дырка, а внешняя область (иначе любая маска имела бы одну лишнюю «дырку»).
    """
    from scipy import ndimage as ndi

    m = np.asarray(mask).astype(bool)
    if not m.any():
        return {"b0": 0, "b1": 0, "chi": 0, "sizes": [], "hole_sizes": []}
    body, n_body = ndi.label(m, structure=np.ones((3, 3)))          # тело: 8-связность
    bg, n_bg = ndi.label(~m, structure=np.array([[0, 1, 0],          # фон: 4-связность,
                                                 [1, 1, 1],          # иначе дырки
                                                 [0, 1, 0]]))        # «протекают» по диагонали
    # фон, касающийся края, — внешний, а не дырка
    edge_labels = set(bg[0, :]) | set(bg[-1, :]) | set(bg[:, 0]) | set(bg[:, -1])
    edge_labels.discard(0)
    holes = int(n_bg - len(edge_labels))
    sizes = [int((body == i).sum()) for i in range(1, n_body + 1)]
    hole_sizes = [int((bg == i).sum()) for i in range(1, n_bg + 1) if i not in edge_labels]
    return {"b0": int(n_body), "b1": holes, "chi": int(n_body - holes),
            "sizes": sizes, "hole_sizes": hole_sizes}


def autocorrelation_length(mask: np.ndarray, max_lag: int | None = None) -> float:
    """Корреляционная длина ξ: где автокорреляция падает до 1/e.

    Нормированная автокорреляция индикатора: C(r) = <n(x)n(x+r)> - p^2, делённая
    на дисперсию. Для случайной маски C(r) ~ 0 при r > 0; для кластеризованной
    спадает с длиной ξ.
    """
    m = np.asarray(mask).astype(float)
    p = float(m.mean())
    if p <= 0.0 or p >= 1.0:
        return 0.0
    var = p * (1.0 - p)
    n = max_lag or min(m.shape) // 2
    values = []
    for r in range(1, n + 1):
        right = m[:, r:] * m[:, :-r]
        down = m[r:, :] * m[:-r, :]
        c = (float(right.mean()) + float(down.mean())) / 2.0
        values.append((c - p * p) / var)
    # первый лаг, где корреляция ниже 1/e
    for r, value in enumerate(values, start=1):
        if value < 1.0 / np.e:
            return float(r)
    return float(n)


def hole_size_distribution(hole_sizes: list[int]) -> dict:
    """Хвост распределения дырок: тяжёлый (перколяция) или лёгкий."""
    sizes = np.asarray(sorted(hole_sizes), dtype=float)
    if sizes.size < 5:
        return {"n": int(sizes.size), "max": int(sizes.max()) if sizes.size else 0,
                "exponent": float("nan"), "heavy_tail": False}
    # наклон хвоста в log-log по размерам (обратное ранжирование)
    ranks = np.arange(1, sizes.size + 1)[::-1]
    lo, hi = int(0.1 * sizes.size), int(0.9 * sizes.size)
    if hi - lo < 3:
        return {"n": int(sizes.size), "max": int(sizes.max()), "exponent": float("nan"),
                "heavy_tail": False}
    x = np.log(sizes[lo:hi])
    y = np.log(ranks[lo:hi])
    slope = float(np.polyfit(x, y, 1)[0])
    return {"n": int(sizes.size), "max": int(sizes.max()), "exponent": abs(slope),
            "heavy_tail": abs(slope) < 2.0}


def hole_morphology(mask: np.ndarray) -> dict:
    """Форма полостей: площадь, периметр и компактность каждой дырки.

    Компактность = 4*pi*A/P^2 (у круга → 1, у изрезанной дырки → меньше).
    Если все дырки компактны — их «вырезало правило»; широкий разброс — случайная
    пористость. Считаем по дополнению с учётом края (фон на краю — не дырка).
    """
    from scipy import ndimage as ndi

    m = np.asarray(mask).astype(bool)
    if not m.any():
        return {"holes": [], "n": 0, "shape_mean": float("nan"), "shape_std": float("nan")}
    bg, n_bg = ndi.label(~m, structure=np.array([[0, 1, 0],
                                                 [1, 1, 1],
                                                 [0, 1, 0]]))
    edge_labels = set(bg[0, :]) | set(bg[-1, :]) | set(bg[:, 0]) | set(bg[:, -1])
    edge_labels.discard(0)
    holes = []
    for label in range(1, n_bg + 1):
        if label in edge_labels:
            continue
        hole_mask = bg == label
        area = int(hole_mask.sum())
        perim = mask_perimeter(hole_mask)
        holes.append({
            "area": area,
            "perimeter": perim,
            "compactness": isoperimetric_ratio(area, perim),
        })
    shapes = [h["compactness"] for h in holes]
    return {
        "holes": holes,
        "n": len(holes),
        "shape_mean": float(np.nanmean(shapes)) if shapes else float("nan"),
        "shape_std": float(np.nanstd(shapes)) if shapes else float("nan"),
    }


def hole_radial_distribution(mask: np.ndarray, bins: int = 8, max_r: int | None = None) -> dict:
    """g(r) центров дырок: пики — регулярность, ровно около 1 — случайность."""
    from scipy import ndimage as ndi

    m = np.asarray(mask).astype(bool)
    if not m.any():
        return {"bins": [], "g": [], "n": 0}
    bg, n_bg = ndi.label(~m, structure=np.array([[0, 1, 0],
                                                 [1, 1, 1],
                                                 [0, 1, 0]]))
    edge_labels = set(bg[0, :]) | set(bg[-1, :]) | set(bg[:, 0]) | set(bg[:, -1])
    edge_labels.discard(0)
    centers = np.array(ndi.center_of_mass(~m, bg, [i for i in range(1, n_bg + 1) if i not in edge_labels]))
    if len(centers) < 3:
        return {"bins": [], "g": [], "n": int(len(centers))}
    from scipy.spatial.distance import pdist

    d = pdist(centers)
    n = len(centers)
    max_r = max_r or int(np.percentile(d, 90))
    hist, edges = np.histogram(d, bins=bins, range=(0, max_r))
    # ожидание для равномерного распределения центров в поле
    grid_area = m.size
    density = n / grid_area
    expected = []
    for i in range(bins):
        r0, r1 = edges[i], edges[i + 1]
        annulus = np.pi * (r1 ** 2 - r0 ** 2)
        expected.append(0.5 * n * (n - 1) * density * annulus)
    g = [(h / e if e > 0 else float("nan")) for h, e in zip(hist, expected)]
    return {"bins": [float((edges[i] + edges[i + 1]) / 2) for i in range(bins)],
            "g": [float(x) for x in g], "n": int(n)}


if __name__ == "__main__":
    raise SystemExit(main())
