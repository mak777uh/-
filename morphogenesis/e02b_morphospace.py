"""e02b_morphospace.py — перепись морфопространства без обучения (E02b).

Что делает:
  * берёт канонические nca_final.pt из lab/checkpoints.json;
  * для каждого чекпоинта запускает 64 детерминированных старта из шума
    (seed 0…63) на 2000 шагов, без градиента и без обучения;
  * считает морфологические и динамические дескрипторы;
  * кластеризует финальные морфологии (Ward + проверка DBSCAN);
  * выбирает прототипы классов и проверяет возмущения (ампутация, шум,
    разрез, пересадка, мёртвое поле).

Это диагностика, а не обучение. Веса не меняются, config.py не трогается.
Pilot (8 сидов × 500 шагов) — только замер времени; гипотезы по нему не
проверяются и в отчёт как проверка не попадают.

Запуск:
  python e02b_morphospace.py --pilot
  python e02b_morphospace.py --steps 2000 --seeds 0-63
  python e02b_morphospace.py --seeds 0-1 --steps 10 --allow-missing  # smoke
"""

import argparse
import json
import os
import shutil
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# §9.2: config обязан импортироваться раньше torch.
import config

import numpy as np
import torch
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.ndimage import label as ndi_label
from scipy.ndimage import shift as ndi_shift
from scipy.special import expit
from scipy.spatial.distance import pdist, squareform

from nca_core import NeuralCellularAutomaton, init_state
from topology import count_connected_components, count_holes
from utils.determinism import randn as _randn
from utils.determinism import randperm as _randperm

EXPERIMENT_ID = "E02b_morphospace"
# Артефакты привязаны к морфогенезису, а не к cwd: lab.py запускает команду из
# morphogenesis/, но прямой запуск из корня не должен писать census.json в
# чужое место.
_MORPH_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(_MORPH_ROOT, "experiments", EXPERIMENT_ID, "census.json")
PILOT_OUT = os.path.join(_MORPH_ROOT, "experiments", EXPERIMENT_ID, "pilot.json")
PERTURBATIONS_OUT = os.path.join(_MORPH_ROOT, "experiments", EXPERIMENT_ID, "perturbations.json")
FIGURES_DIR = os.path.join(os.path.dirname(_MORPH_ROOT), "reports", "figures")

# Признаки для кластеризации. Все они либо инвариантны к сдвигу (доли,
# топология, bbox, радиальный профиль от центроида), либо к повороту
# (симметрия берётся максимумом по поворотам/отражениям), либо к обоим.
# Сырые координаты центроида в кластеризацию НЕ входят: они измеряют положение,
# а не геометрию, и сделали бы «кольцо слева» отдельным классом от «кольца справа».
CLUSTER_FEATURES = (
    "alive_fraction",
    "binary_fraction",
    "bright_fraction",
    "soft_mean",
    "entropy",
    "log1p_b0",
    "log1p_b1",
    "chi",
    "bbox_fill",
    "largest_component_fraction",
    "radial_var",
    "radial_peak_bin",
    "radial_center_occupancy",
    "symmetry_rot_centered",
    "symmetry_reflect_centered",
    "autocorr_lag1",
    "autocorr_lag4",
    "edge_fraction",
)

COMPACT_KEYS = (
    "step",
    "alive_fraction",
    "binary_fraction",
    "bright_fraction",
    "bbox_fill",
    "b0",
    "b1",
    "radial_peak_bin",
    "radial_var",
    "entropy",
    "delta_per_step",
)

# Допуски для «цикла» и «стабилизации». Они не подбираются по результату:
# это грубые границы, отделяющие шум с точностью 1e-2 от смены морфологии.
CYCLE_TOL = {
    "alive_fraction": 0.01,
    "binary_fraction": 0.01,
    "b0": 0,
    "b1": 0,
    "radial_peak_bin": 0,
    "entropy": 0.01,
}


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path: str) -> str:
    """Путь из lab/checkpoints.json (от корня repo) или локальный (от cwd)."""
    if os.path.isabs(path):
        return path
    local = os.path.abspath(path)
    if os.path.exists(local):
        return local
    return os.path.join(_repo_root(), path.replace("/", os.sep))


def _parse_seeds(spec: str) -> List[int]:
    """'0-63' / '0,2,4' / '7' -> список сидов без дублей, порядок сохраняется."""
    out: List[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            lo, hi = int(a), int(b)
            if hi < lo:
                raise ValueError(f"пустой диапазон сидов: {chunk}")
            out.extend(range(lo, hi + 1))
        else:
            out.append(int(chunk))
    seen = set()
    unique = []
    for seed in out:
        if seed not in seen:
            seen.add(seed)
            unique.append(seed)
    return unique


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class CheckpointSpec:
    id: str
    arm: str
    family: str
    path: Optional[str]
    seed: int
    steps_trained: int
    sha256: Optional[str]
    alive_mask_enabled: bool
    overrides: dict = field(default_factory=dict)
    overrides_source: str = "default_config"
    kind: str = "final"
    note: str = ""


def _load_wp4_overrides() -> Dict[Tuple[str, int, int], dict]:
    path = _resolve(os.path.join("experiments", "E02_pattern", "wp4_ablations.json"))
    if not os.path.exists(path):
        return {}
    data = _load_json(path)
    out = {}
    for run in data.get("runs", []):
        out[(str(run.get("arm")), int(run.get("steps", 0)), int(run.get("seed", 0)) )] = (
            run.get("overrides") or {}
        )
    return out


def _alive_mask_from_overrides(overrides: dict, steps_trained: int) -> bool:
    if not overrides:
        return bool(int(config.ALIVE_WARMUP_ITERS) <= int(steps_trained))
    warmup = int(overrides.get("ALIVE_WARMUP_ITERS", config.ALIVE_WARMUP_ITERS))
    return bool(warmup <= int(steps_trained))


def load_checkpoint_specs(
    families: Optional[Sequence[str]] = None,
    include_untrained: bool = True,
    allow_missing: bool = False,
) -> List[CheckpointSpec]:
    """Собрать спецификации из experiment-дескриптора и индекса чекпоинтов.

    Дескриптор задаёт ПОРЯДОК и требования; индекс — путь, seed и sha256.
    Отсутствующий файл нельзя подменить «похожим» (AGENTS.md §5): для полного
    прогона это ошибка, для smoke — только с --allow-missing.
    """
    exp_path = _resolve(os.path.join("lab", "experiments", f"{EXPERIMENT_ID}.json"))
    index_path = _resolve(os.path.join("lab", "checkpoints.json"))
    exp = _load_json(exp_path)
    index = _load_json(index_path)
    by_family = {e["family"]: e for e in index.get("entries", []) if e.get("kind") == "final"}

    required = [item["family"] for item in exp.get("checkpoint_requirements", [])]
    if families:
        wanted = set(families)
        required = [f for f in required if f in wanted]
    overrides_by_key = _load_wp4_overrides()
    specs: List[CheckpointSpec] = []
    missing: List[str] = []
    for family in required:
        entry = by_family.get(family)
        if entry is None:
            missing.append(f"{family}: нет final-записи в lab/checkpoints.json")
            continue
        path = _resolve(entry["path"])
        if not os.path.exists(path):
            missing.append(f"{family}: файл отсутствует ({entry['path']})")
            continue
        arm = str(entry.get("arm") or family.split("_")[1])
        seed = int(entry.get("seed", 42))
        steps = int(entry.get("steps", 2000))
        ov = overrides_by_key.get((arm, steps, seed), {})
        specs.append(
            CheckpointSpec(
                id=family,
                arm=arm,
                family=family,
                path=path,
                seed=seed,
                steps_trained=steps,
                sha256=entry.get("sha256"),
                alive_mask_enabled=_alive_mask_from_overrides(ov, steps),
                overrides=ov,
                overrides_source="wp4_ablations.json" if ov else "default_config",
                kind="final",
            )
        )
    if missing and not allow_missing:
        raise SystemExit(
            "[e02b] неполный канон чекпоинтов; полный прогон запрещён:\n  "
            + "\n  ".join(missing)
        )
    for msg in missing:
        print(f"[e02b] ВНИМАНИЕ: {msg} (allow_missing)")

    if include_untrained and (not families or "untrained_current_arch" in families):
        specs.append(
            CheckpointSpec(
                id="untrained_current_arch",
                arm="untrained",
                family="untrained_current_arch",
                path=None,
                seed=42,
                steps_trained=0,
                sha256=None,
                alive_mask_enabled=True,
                overrides={},
                overrides_source="runtime",
                kind="runtime",
                note="свежая инициализация той же архитектуры, без загрузки весов",
            )
        )
    return specs


def build_model(spec: CheckpointSpec, device: torch.device) -> Tuple[NeuralCellularAutomaton, Optional[dict]]:
    """Загрузить веса на CPU и перенести на устройство.

    Чекпоинт целиком (оптимизатор, пул) остаётся на CPU: на GPU нужна только
    модель, иначе 539-МБ файл на каждый из 13 чекпоинтов съест память впустую.
    """
    model = NeuralCellularAutomaton(channels=config.N_CHANNELS)
    ck = None
    if spec.path:
        ck = torch.load(spec.path, map_location="cpu", weights_only=False)
        config.assert_checkpoint_compatible(
            ck, allow_missing_metadata=True, context=f"e02b({spec.id})"
        )
        model.load_state_dict(ck["model_state_dict"])
    model.alive_mask_enabled = bool(spec.alive_mask_enabled)
    model.to(device)
    model.eval()
    return model, ck


def prepare_model(model: NeuralCellularAutomaton, seed: int) -> torch.Generator:
    """Сбросить всё, что делает старт зависимым от порядка сидов.

    stress_ema — глобальный буфер модели, а не часть начального состояния.
    Если его не восстановить, сид 1 начнёт с EMA, накопленной сидом 0, и 64
    старта перестанут быть независимыми. Сохраняем значение, пришедшее из
    чекпоинта (или ноль у необученной модели), и восстанавливаем перед каждым
    стартом — так же, как это делает wp4_reach_probe (он вообще не трогает EMA).
    """
    gen = config.create_deterministic_generator(seed)
    model.set_generator(gen)
    if hasattr(model, "_e02b_stress_ema_start"):
        model.stress_ema.copy_(model._e02b_stress_ema_start)
    else:
        model.stress_ema.zero_()
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    return gen


def remember_stress_ema_start(model: NeuralCellularAutomaton) -> None:
    model._e02b_stress_ema_start = model.stress_ema.detach().clone()


def _state_arrays(state: torch.Tensor) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Один перенос GPU→CPU, затем все маски по каноническим правилам.

    binary = (sigmoid(alpha) > ALIVE_THRESHOLD) & (sigmoid(visible) > BINARY_THRESHOLD)
    совпадает с topology.get_binary_mask; тест сверяет это на случайном состоянии.
    """
    arr = state[0].detach().cpu().numpy().astype(np.float32, copy=False)
    visible = arr[config.VISIBLE_CHANNEL]
    alpha = arr[config.ALIVE_CHANNEL]
    stress = arr[config.STRESS_CHANNEL]
    if config.USE_SIGMOID_VISIBLE:
        visible_soft = expit(visible)
    else:
        visible_soft = np.clip(visible, 0.0, 1.0)
    alive = expit(alpha) > float(config.ALIVE_THRESHOLD)
    binary = alive & (visible_soft > float(config.BINARY_THRESHOLD))
    return alive, binary, visible_soft, stress, alpha


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    union = np.logical_or(a, b).sum()
    if union == 0:
        return 0.0
    return float(np.logical_and(a, b).sum() / union)


def _center_mask(mask: np.ndarray) -> np.ndarray:
    """Сдвинуть маску центроидом в центр без wrap-артефактов."""
    if not mask.any():
        return mask
    ys, xs = np.nonzero(mask)
    cy, cx = float(ys.mean()), float(xs.mean())
    h, w = mask.shape
    dy, dx = (h - 1) / 2.0 - cy, (w - 1) / 2.0 - cx
    shifted = ndi_shift(
        mask.astype(np.float32),
        shift=(dy, dx),
        order=0,
        mode="constant",
        cval=0.0,
        prefilter=False,
    )
    return shifted > 0.5


def _symmetry_scores(mask: np.ndarray) -> Tuple[float, float]:
    if not mask.any():
        return 0.0, 0.0
    rot = max(_iou(mask, np.rot90(mask, k)) for k in (1, 2, 3))
    flips = (np.fliplr(mask), np.flipud(mask), mask.T, np.flipud(mask.T))
    reflect = max(_iou(mask, other) for other in flips)
    return float(rot), float(reflect)


def _radial_profile(mask: np.ndarray, bins: int = 8) -> Tuple[np.ndarray, int, float, float, float]:
    """Профиль заполнения по радиусу от центроида.

    Возвращает (profile, peak_bin, center_occupancy, outer_occupancy, var).
    Кольцо даёт высокий outer/peak_bin ближе к краю, пятно — высокий center.
    """
    h, w = mask.shape
    if mask.any():
        ys, xs = np.nonzero(mask)
        cy, cx = float(ys.mean()), float(xs.mean())
    else:
        cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    yy, xx = np.indices(mask.shape)
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    # Нормируем на радиус САМОЙ маски, а не на угол сетки: иначе кольцо радиуса
    # 20 из 64 попадает в средние бины, а «outer» всегда ноль, и профиль
    # перестаёт различать кольцо и пятно (проверено тестом).
    max_r = float(r[mask].max()) if mask.any() else float(r.max())
    if max_r <= 0:
        max_r = 1.0
    bin_idx = np.minimum((r / max_r * bins).astype(np.int32), bins - 1)
    # Пиксели ЗА радиусом маски не принадлежат ни одному бину. Раньше они
    # клиппились в последний бин и разбавляли его фоном: у диска outer падал до
    # 0.02, а radial_var становился больше, чем у кольца. Это делало дескриптор
    # не тем, чем он называется.
    inside = r <= max_r + 1e-9
    flat_bins = bin_idx[inside].ravel()
    flat_mask = mask[inside].ravel().astype(np.float32)
    counts = np.bincount(flat_bins, minlength=bins).astype(np.float32)
    sums = np.bincount(flat_bins, weights=flat_mask, minlength=bins)
    profile = sums / np.maximum(counts, 1.0)
    if mask.any():
        peak_bin = int(np.argmax(profile))
    else:
        peak_bin = -1
    return profile, peak_bin, float(profile[0]), float(profile[-1]), float(np.var(profile))


def _autocorr1d(x: np.ndarray, lag: int) -> float:
    if x.size <= lag or x.size == 0:
        return 0.0
    xm = x - float(x.mean())
    denom = float((xm * xm).mean())
    if denom <= 1e-12:
        return 0.0
    num = float((xm[:-lag, :] * xm[lag:, :]).mean())
    num2 = float((xm[:, :-lag] * xm[:, lag:]).mean())
    return float((num + num2) / (2.0 * denom))


def _intensity_entropy(image: np.ndarray, bins: int = 16) -> float:
    hist, _ = np.histogram(image.ravel(), bins=bins, range=(0.0, 1.0))
    total = hist.sum()
    if total <= 0:
        return 0.0
    p = hist.astype(np.float32) / float(total)
    return float(-np.sum(p * np.log(p + 1e-12)) / np.log(bins))


def describe_state(state: torch.Tensor) -> dict:
    """Полный дескриптор одной точки развёртки (без target/f1)."""
    alive, binary, visible_soft, stress, _alpha = _state_arrays(state)
    h, w = binary.shape
    n = float(h * w)
    pixels = int(binary.sum())
    alive_pixels = int(alive.sum())
    b0 = int(count_connected_components(binary))
    b1 = int(count_holes(binary))
    alive_b0 = int(count_connected_components(alive.astype(np.uint8)))

    if pixels:
        ys, xs = np.nonzero(binary)
        y0, y1 = int(ys.min()), int(ys.max())
        x0, x1 = int(xs.min()), int(xs.max())
        bbox_area = float((y1 - y0 + 1) * (x1 - x0 + 1))
        bbox_fill = float(pixels / bbox_area)
        largest = 0
        labeled, n_comp = ndi_label(binary.astype(np.int32), structure=np.ones((3, 3), dtype=int))
        if n_comp:
            largest = int(np.bincount(labeled.ravel())[1:].max())
        largest_fraction = float(largest / n)
        centroid_y = float(ys.mean() / max(h - 1, 1))
        centroid_x = float(xs.mean() / max(w - 1, 1))
        edge = int(binary[0, :].sum() + binary[-1, :].sum() + binary[:, 0].sum() + binary[:, -1].sum())
        edge_fraction = float(edge / max(pixels, 1))
    else:
        bbox_fill = 0.0
        largest_fraction = 0.0
        centroid_y = 0.5
        centroid_x = 0.5
        edge_fraction = 0.0

    centered = _center_mask(binary)
    sym_rot, sym_reflect = _symmetry_scores(centered)
    profile, peak_bin, center_occ, outer_occ, radial_var = _radial_profile(binary)
    bright = visible_soft > 0.5
    bright_fraction = float(bright.mean())
    bright_alive_fraction = float((bright & alive).sum() / max(alive_pixels, 1))

    return {
        "alive_fraction": float(alive_pixels / n),
        "binary_fraction": float(pixels / n),
        "bright_fraction": bright_fraction,
        "bright_alive_fraction": bright_alive_fraction,
        "soft_mean": float(visible_soft.mean()),
        "soft_std": float(visible_soft.std()),
        "entropy": _intensity_entropy(visible_soft),
        "b0": b0,
        "b1": b1,
        "chi": int(b0 - b1),
        "log1p_b0": float(np.log1p(b0)),
        "log1p_b1": float(np.log1p(b1)),
        "alive_b0": alive_b0,
        "n_pixels": int(pixels),
        "bbox_fill": bbox_fill,
        "largest_component_fraction": largest_fraction,
        "centroid_x": centroid_x,
        "centroid_y": centroid_y,
        "radial_profile": [float(v) for v in profile],
        "radial_peak_bin": int(peak_bin),
        "radial_center_occupancy": center_occ,
        "radial_outer_occupancy": outer_occ,
        "radial_var": radial_var,
        "symmetry_rot_centered": sym_rot,
        "symmetry_reflect_centered": sym_reflect,
        "autocorr_lag1": _autocorr1d(visible_soft, 1),
        "autocorr_lag2": _autocorr1d(visible_soft, 2),
        "autocorr_lag4": _autocorr1d(visible_soft, 4),
        "autocorr_lag8": _autocorr1d(visible_soft, 8),
        "edge_fraction": edge_fraction,
        "stress_mean": float(stress.mean()),
        "stress_max": float(stress.max()),
    }


def descriptor_vector(desc: dict) -> np.ndarray:
    return np.asarray([float(desc.get(k, 0.0)) for k in CLUSTER_FEATURES], dtype=np.float64)


def compact_point(desc: dict, step: int, delta_per_step: Optional[float]) -> dict:
    point = {k: desc.get(k) for k in COMPACT_KEYS}
    point["step"] = int(step)
    point["delta_per_step"] = delta_per_step
    return point


def classify_dynamics(points: Sequence[dict], every: int) -> dict:
    """Неподвижная точка / цикл / дрейф по снимкам, без претензии на хаос."""
    deltas = [p.get("delta_per_step") for p in points if p.get("delta_per_step") is not None]
    last = deltas[-3:] if len(deltas) >= 3 else deltas
    fixed = bool(last) and max(last) < 1e-4
    if fixed:
        # Даже при почти нулевой дельте проверим, что морфология не прыгает.
        tail = points[-3:] if len(points) >= 3 else points
        fixed = all(
            abs(p["alive_fraction"] - tail[-1]["alive_fraction"]) < 1e-4
            and abs(p["binary_fraction"] - tail[-1]["binary_fraction"]) < 1e-4
            and p["b0"] == tail[-1]["b0"]
            and p["b1"] == tail[-1]["b1"]
            for p in tail
        )
    if fixed:
        return {
            "class": "fixed",
            "cycle_lag_snapshots": None,
            "period_steps": None,
            "amplitude_alive_fraction": None,
            "amplitude_binary_fraction": None,
        }

    for lag in range(2, min(9, len(points) + 1)):
        ok = True
        for i in range(len(points) - lag):
            a, b = points[i], points[i + lag]
            for key, tol in CYCLE_TOL.items():
                if abs(float(a[key]) - float(b[key])) > tol:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            tail = points[-max(lag + 1, 2):]
            return {
                "class": "cycle",
                "cycle_lag_snapshots": int(lag),
                "period_steps": int(lag * every),
                "amplitude_alive_fraction": float(
                    max(p["alive_fraction"] for p in tail) - min(p["alive_fraction"] for p in tail)
                ),
                "amplitude_binary_fraction": float(
                    max(p["binary_fraction"] for p in tail) - min(p["binary_fraction"] for p in tail)
                ),
            }
    return {
        "class": "drift",
        "cycle_lag_snapshots": None,
        "period_steps": None,
        "amplitude_alive_fraction": None,
        "amplitude_binary_fraction": None,
    }


def settle_step(points: Sequence[dict]) -> Optional[int]:
    """Первый снимок, после которого компактный дескриптор не меняется."""
    if not points:
        return None
    final = points[-1]
    stable_from = len(points) - 1
    for i in range(len(points) - 2, -1, -1):
        p = points[i]
        same = (
            abs(p["alive_fraction"] - final["alive_fraction"]) <= 0.01
            and abs(p["binary_fraction"] - final["binary_fraction"]) <= 0.01
            and p["b0"] == final["b0"]
            and p["b1"] == final["b1"]
            and p["radial_peak_bin"] == final["radial_peak_bin"]
        )
        if same:
            stable_from = i
        else:
            break
    return int(points[stable_from]["step"])


def rollout(
    model: NeuralCellularAutomaton,
    state: torch.Tensor,
    steps: int,
    every: int,
) -> Tuple[torch.Tensor, List[dict], np.ndarray, float]:
    """Автономная развёртка. Возвращает final_state, compact points, traj features, время."""
    points: List[dict] = []
    features: List[np.ndarray] = []
    prev_state = None
    prev_step = 0
    t0 = time.perf_counter()
    for step in range(1, int(steps) + 1):
        with torch.no_grad():
            state = model(state)
        if step % every == 0 or step == steps:
            desc = describe_state(state)
            if prev_state is None:
                delta_per_step = None
            else:
                gap = step - prev_step
                delta_per_step = float(
                    (state - prev_state).abs().mean().item() / max(gap, 1)
                )
            points.append(compact_point(desc, step, delta_per_step))
            features.append(descriptor_vector(desc))
            prev_state = state.detach().clone()
            prev_step = step
    elapsed = time.perf_counter() - t0
    traj = np.vstack(features) if features else np.zeros((0, len(CLUSTER_FEATURES)))
    return state, points, traj, float(elapsed)


def run_seed(
    model: NeuralCellularAutomaton,
    spec: CheckpointSpec,
    seed: int,
    steps: int,
    every: int,
    device: torch.device,
) -> dict:
    gen = prepare_model(model, seed)
    start = init_state(
        batch_size=1,
        channels=config.N_CHANNELS,
        grid_size=config.GRID_SIZE,
        device=device,
        generator=gen,
    )
    final_state, points, traj, elapsed = rollout(model, start, steps, every)
    final_desc = describe_state(final_state)
    return {
        "family": spec.family,
        "arm": spec.arm,
        "seed": int(seed),
        "steps": int(steps),
        "snapshot_every": int(every),
        "is_control": bool(spec.arm in ("H-P1", "untrained")),
        "control_role": (
            "positive_control_h_p1" if spec.arm == "H-P1"
            else "untrained_architecture" if spec.arm == "untrained"
            else None
        ),
        "alive_mask_enabled": bool(spec.alive_mask_enabled),
        "overrides_source": spec.overrides_source,
        "final": final_desc,
        "trajectory": points,
        "traj_features": traj,
        "dynamics": classify_dynamics(points, every),
        "settle_step": settle_step(points),
        "wall_seconds": elapsed,
    }


def _cluster_semantic(median: dict) -> str:
    if median["alive_fraction"] < 0.01:
        return "death"
    if median["binary_fraction"] < 0.01:
        return "uniform_dark"
    if median["binary_fraction"] > 0.95:
        return "uniform_bright"
    return "structured"


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    n = len(X)
    if n < 2:
        return 0.0
    D = squareform(pdist(X))
    unique = np.unique(labels)
    if len(unique) < 2:
        return 0.0
    scores = []
    for i in range(n):
        own = labels == labels[i]
        own[i] = False
        if own.sum() == 0:
            scores.append(0.0)
            continue
        a = float(D[i, own].mean())
        b = float("inf")
        for c in unique:
            if c == labels[i]:
                continue
            other = labels == c
            if other.any():
                b = min(b, float(D[i, other].mean()))
        if b == float("inf"):
            scores.append(0.0)
        else:
            denom = max(a, b)
            scores.append(0.0 if denom <= 0 else (b - a) / denom)
    return float(np.mean(scores))


def _adjusted_rand(labels_a: np.ndarray, labels_b: np.ndarray) -> float:
    """ARI без sklearn; метки -1 считаются обычной меткой."""
    a = np.asarray(labels_a)
    b = np.asarray(labels_b)
    if len(a) != len(b) or len(a) < 2:
        return 0.0
    ua, ia = np.unique(a, return_inverse=True)
    ub, ib = np.unique(b, return_inverse=True)
    table = np.zeros((len(ua), len(ub)), dtype=np.float64)
    np.add.at(table, (ia, ib), 1.0)
    def comb2(x):
        return float((x * (x - 1.0) / 2.0).sum())
    sum_comb = comb2(table)
    sum_a = comb2(table.sum(axis=1))
    sum_b = comb2(table.sum(axis=0))
    total = len(a)
    expected = sum_a * sum_b / (total * (total - 1.0) / 2.0)
    max_index = 0.5 * (sum_a + sum_b)
    denom = max_index - expected
    if abs(denom) < 1e-12:
        return 0.0
    return float((sum_comb - expected) / denom)


def _dbscan(X: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    n = len(X)
    labels = np.full(n, -1, dtype=int)
    visited = np.zeros(n, dtype=bool)
    if n == 0:
        return labels
    D = squareform(pdist(X))
    cluster = 0
    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        neighbors = np.where(D[i] <= eps)[0]
        if len(neighbors) < min_samples:
            continue
        labels[i] = cluster
        seeds = list(neighbors)
        in_seeds = set(seeds)
        cursor = 0
        while cursor < len(seeds):
            q = int(seeds[cursor])
            cursor += 1
            if not visited[q]:
                visited[q] = True
                qn = np.where(D[q] <= eps)[0]
                if len(qn) >= min_samples:
                    for item in qn:
                        if int(item) not in in_seeds:
                            in_seeds.add(int(item))
                            seeds.append(int(item))
            if labels[q] == -1:
                labels[q] = cluster
        cluster += 1
    return labels


def _dbscan_check(X: np.ndarray, max_k: int) -> dict:
    n = len(X)
    if n < 10:
        return {"status": "too_few_points", "n_points": n}
    kth = np.partition(squareform(pdist(X)), 4, axis=1)[:, 4]
    base = float(np.percentile(kth, 90))
    if base <= 0:
        base = 0.5
    best = None
    for factor in (0.8, 1.0, 1.25, 1.6, 2.0):
        labels = _dbscan(X, eps=base * factor, min_samples=5)
        labels_set = set(int(v) for v in labels if v >= 0)
        noise = int((labels < 0).sum())
        cand = {
            "eps": float(base * factor),
            "min_samples": 5,
            "n_clusters": len(labels_set),
            "noise": noise,
            "noise_fraction": float(noise / n),
            "labels": labels,
        }
        if best is None:
            best = cand
        # Предпочитаем 2..max_k кластеров и минимум шума; при равенстве — больше классов.
        def score(c):
            in_range = 2 <= c["n_clusters"] <= max_k
            return (int(in_range), -c["noise_fraction"], c["n_clusters"])
        if score(cand) > score(best):
            best = cand
    best.pop("labels", None)
    return best


def fit_clusters(
    runs: Sequence[dict],
    min_size: int = 5,
    max_k: int = 10,
) -> dict:
    """Ward по финальным дескрипторам + silhouette + проверка DBSCAN."""
    if not runs:
        raise ValueError("fit_clusters: нет прогонов")
    X = np.vstack([descriptor_vector(r["final"]) for r in runs])
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std < 1e-9] = 1.0
    Xz = (X - mean) / std
    n = len(Xz)
    if n == 1:
        labels = np.zeros(1, dtype=int)
        return {
            "features": list(CLUSTER_FEATURES),
            "scaler_mean": mean.tolist(),
            "scaler_std": std.tolist(),
            "linkage": "ward",
            "k": 1,
            "silhouette": None,
            "labels": labels,
            "sizes": [1],
            "outliers": 0,
            "centroids_z": Xz.mean(axis=0, keepdims=True),
            "medians": [runs[0]["final"]],
            "semantic": ["structured" if runs[0]["final"]["alive_fraction"] >= 0.01 else "death"],
            "dbscan": {"status": "too_few_points", "n_points": n},
        }
    Z = linkage(Xz, method="ward")
    candidates = []
    for k in range(2, min(max_k, n - 1) + 1):
        labels = fcluster(Z, k, criterion="maxclust").astype(int)
        sizes = np.bincount(labels)[1:] if labels.min() >= 0 else np.bincount(labels)
        # fcluster нумерует с 1; bincount без нуля.
        sizes = np.bincount(labels)[1:]
        if sizes.size == 0 or int(sizes.min()) < min_size:
            continue
        sil = _silhouette(Xz, labels)
        candidates.append({"k": int(k), "labels": labels, "sizes": sizes, "silhouette": float(sil)})
    if candidates:
        best = max(candidates, key=lambda c: c["silhouette"])
        labels = best["labels"]
        k = best["k"]
        silhouette = best["silhouette"]
    else:
        # Нет k, где все классы ≥ min_size: берём k=2 и честно помечаем
        # маленький класс выбросом (-1), а не раздуваем его до «класса».
        labels = fcluster(Z, 2, criterion="maxclust").astype(int)
        sizes_raw = np.bincount(labels)
        small = [i for i in range(1, len(sizes_raw)) if sizes_raw[i] < min_size]
        for i in small:
            labels[labels == i] = -1
        k = len(set(int(v) for v in labels if v >= 0))
        silhouette = None
    valid_labels = sorted(set(int(v) for v in labels if v >= 0))
    centroids = []
    medians = []
    semantic = []
    for cid in valid_labels:
        mask = labels == cid
        centroids.append(Xz[mask].mean(axis=0))
        med = {
            key: float(np.median([runs[i]["final"][key] for i in np.where(mask)[0]]))
            for key in runs[0]["final"]
            if isinstance(runs[0]["final"][key], (int, float))
        }
        medians.append(med)
        semantic.append(_cluster_semantic(med))
    names = []
    structured_i = 0
    for sem in semantic:
        if sem == "structured":
            structured_i += 1
            names.append(f"struct_{structured_i}")
        else:
            names.append(sem)
    dbscan = _dbscan_check(Xz, max_k)
    if "labels" in dbscan:
        # labels уже убраны; сюда не попадём, оставлено для явности контракта.
        pass
    dbscan_labels = _dbscan(
        Xz,
        eps=float(dbscan.get("eps", 0.0)),
        min_samples=int(dbscan.get("min_samples", 5)),
    ) if dbscan.get("eps") else np.full(n, -1)
    dbscan["ari_vs_ward"] = _adjusted_rand(labels, dbscan_labels)
    return {
        "features": list(CLUSTER_FEATURES),
        "scaler_mean": mean.tolist(),
        "scaler_std": std.tolist(),
        "linkage": "ward",
        "k": int(k),
        "silhouette": silhouette,
        "labels": labels,
        "labels_valid": valid_labels,
        "sizes": [int((labels == c).sum()) for c in valid_labels],
        "outliers": int((labels < 0).sum()),
        "centroids_z": np.vstack(centroids) if centroids else np.zeros((0, len(CLUSTER_FEATURES))),
        "medians": medians,
        "semantic": semantic,
        "class_names": names,
        "dbscan": dbscan,
    }


def assign_to_clusters(
    features: np.ndarray,
    scaler_mean: np.ndarray,
    scaler_std: np.ndarray,
    centroids_z: np.ndarray,
    labels_valid: Sequence[int],
) -> np.ndarray:
    if features.size == 0 or centroids_z.size == 0:
        return np.full(len(features), -1, dtype=int)
    z = (features - scaler_mean) / scaler_std
    d = ((z[:, None, :] - centroids_z[None, :, :]) ** 2).sum(axis=2)
    idx = d.argmin(axis=1)
    return np.asarray([int(labels_valid[i]) for i in idx], dtype=int)


def _apply_clustering(
    runs: List[dict],
    clustering: dict,
    fit_indices: Optional[Sequence[int]] = None,
) -> None:
    labels = clustering["labels"]
    valid = clustering["labels_valid"]
    class_names = clustering["class_names"]
    centroids = np.vstack(clustering["centroids_z"]) if clustering["centroids_z"].size else np.zeros((0, len(CLUSTER_FEATURES)))
    scaler_mean = np.asarray(clustering["scaler_mean"])
    scaler_std = np.asarray(clustering["scaler_std"])
    name_by_label = {int(c): str(name) for c, name in zip(valid, class_names, strict=True)}
    semantic_by_label = {int(c): str(sem) for c, sem in zip(valid, clustering["semantic"], strict=True)}
    if fit_indices is None:
        fit_indices = list(range(len(runs)))
    # Ward обучается на выученных динамиках; контроли только проецируются на
    # найденные центроиды и не получают собственный «класс».
    label_by_index = {int(idx): int(labels[k]) for k, idx in enumerate(fit_indices)}
    for i, run in enumerate(runs):
        if i in label_by_index:
            label = label_by_index[i]
        else:
            vec = descriptor_vector(run["final"]).reshape(1, -1)
            label = int(assign_to_clusters(vec, scaler_mean, scaler_std, centroids, valid)[0])
        run["cluster"] = int(label)
        run["class_name"] = name_by_label.get(int(label), "outlier")
        run["semantic"] = semantic_by_label.get(int(label), _cluster_semantic(run["final"]))
        traj_labels = assign_to_clusters(
            run["traj_features"], scaler_mean, scaler_std, centroids, valid
        )
        run["trajectory_cluster"] = [int(v) for v in traj_labels]
        run["trajectory_class"] = [
            name_by_label.get(int(v), "outlier") for v in traj_labels
        ]
        final_label = int(traj_labels[-1]) if len(traj_labels) else -1
        # Устойчивость на последней четверти: доля снимков с финальным классом.
        n = len(traj_labels)
        q0 = int(np.floor(0.75 * n))
        tail = traj_labels[q0:]
        run["stability_last_quarter"] = (
            float((tail == final_label).mean()) if len(tail) else 0.0
        )
        stable_from = None
        for j in range(n - 1, -1, -1):
            if int(traj_labels[j]) == final_label:
                stable_from = int(run["trajectory"][j]["step"])
            else:
                break
        run["class_stable_from_step"] = stable_from
        # Финальный Ward-класс и ближайший центроид могут расходиться у выброса;
        # это фиксируется отдельно, а не замазывается.
        run["nearest_cluster"] = int(final_label)
        run["is_outlier"] = bool(int(label) < 0)
        # Полные дескрипторы снимков в JSON не едут: только компактная траектория.
        run.pop("traj_features", None)


def evaluate_h1(runs: Sequence[dict], families: Sequence[str]) -> dict:
    """H1: нетривиальный класс, воспроизводимый в ≥80% из 64 стартов.

    Контроли (H-P1 и необученная модель) исключены по полю is_control, а не по
    строке family: family H-P1 выглядит как WP4_H-P1_s2000_seed42, и сравнение
    с "H-P1" молча оставило бы контроль в знаменателе.
    """
    eval_runs = [r for r in runs if not r.get("is_control")]
    eval_families = [f for f in families if any(r["family"] == f for r in eval_runs)]
    total = len(eval_runs)
    death_uniform = sum(1 for r in eval_runs if r["semantic"] in ("death", "uniform_dark", "uniform_bright"))
    candidates = []
    struct_max = {}
    for family in eval_families:
        group = [r for r in eval_runs if r["family"] == family]
        if not group:
            continue
        for cid in sorted(set(r["cluster"] for r in group if r["cluster"] >= 0)):
            members = [r for r in group if r["cluster"] == cid]
            sem = members[0]["semantic"]
            if sem != "structured":
                continue
            frac = len(members) / len(group)
            stable = sum(1 for r in members if r["stability_last_quarter"] >= 0.8) / len(members)
            # Пункт (б) протокола: класс должен жить в диапазоне 0.05–0.80.
            # Проверяем медиану по членам: это свойство класса, а не выброса.
            alive_median = float(
                np.median([float(r.get("final", {}).get("alive_fraction", 0.0)) for r in members])
            )
            struct_max[family] = max(struct_max.get(family, 0.0), frac)
            if frac >= 0.8 and stable >= 0.8 and 0.05 <= alive_median <= 0.80:
                candidates.append(
                    {
                        "family": family,
                        "cluster": int(cid),
                        "class_name": members[0]["class_name"],
                        "fraction_of_starts": float(frac),
                        "stable_fraction": float(stable),
                        "alive_fraction_median": alive_median,
                        "n_starts": len(members),
                    }
                )
    refuted = bool(
        total > 0
        and (
            death_uniform / total >= 0.95
            or (struct_max and max(struct_max.values()) < 0.5)
            or not struct_max
        )
    )
    return {
        "hypothesis": "H1: есть нетривиальное структурное многообразие",
        "evaluated_runs": total,
        "death_or_uniform_fraction": float(death_uniform / total) if total else None,
        "candidates": candidates,
        "supported": bool(candidates),
        "refuted": refuted,
        "struct_max_fraction_by_family": {k: float(v) for k, v in sorted(struct_max.items())},
        "note": "H-P1 и необученный контроль исключены из кандидатов: это контроли.",
    }


def evaluate_h2(runs: Sequence[dict], structural_labels: Sequence[int]) -> dict:
    r11 = [r for r in runs if r["family"].startswith("WP4_R-11") or r["arm"] == "R-11"]
    if not r11:
        return {"hypothesis": "H2: структура R-11 транзиентна", "status": "not_run", "reason": "нет R-11"}
    structural = set(int(v) for v in structural_labels)
    final_death = sum(1 for r in r11 if r["semantic"] in ("death", "uniform_dark", "uniform_bright"))
    any_struct = sum(1 for r in r11 if any(v in structural for v in r.get("trajectory_cluster", [])))
    transient = sum(
        1
        for r in r11
        if r["semantic"] in ("death", "uniform_dark", "uniform_bright")
        and any(v in structural for v in r.get("trajectory_cluster", []))
    )
    n = len(r11)
    frac_final_death = final_death / n
    frac_any_struct = any_struct / n
    frac_transient = transient / n
    if frac_final_death >= 0.8 and frac_any_struct >= 0.5:
        status = "supported"
    elif frac_final_death <= 0.2:
        status = "refuted"
    else:
        status = "mixed"
    return {
        "hypothesis": "H2: структура R-11 транзиентна",
        "status": status,
        "n_starts": n,
        "final_death_or_uniform_fraction": float(frac_final_death),
        "any_structural_snapshot_fraction": float(frac_any_struct),
        "transient_structural_fraction": float(frac_transient),
        "note": "опровержение — если последняя точка структурна у ≥80% стартов",
    }


def _select_prototypes(runs: Sequence[dict], clustering: dict, max_per_class: int = 3) -> List[dict]:
    centroids = np.asarray(clustering["centroids_z"])
    mean = np.asarray(clustering["scaler_mean"])
    std = np.asarray(clustering["scaler_std"])
    prototypes = []
    for cid, sem, name in zip(clustering["labels_valid"], clustering["semantic"], clustering["class_names"], strict=True):
        if sem != "structured":
            continue
        # Контроли могут попасть в тот же Ward-кластер, но прототип и H3 —
        # про выученную динамику, поэтому они в члены класса не входят.
        members = [r for r in runs if r["cluster"] == int(cid) and not r.get("is_control")]
        if len(members) < 5:
            continue
        X = np.vstack([descriptor_vector(r["final"]) for r in members])
        Z = (X - mean) / std
        c = centroids[clustering["labels_valid"].index(int(cid))]
        d = ((Z - c) ** 2).sum(axis=1)
        order = np.argsort(d)
        picks = [order[0]]
        if len(order) > 2:
            picks.extend([order[len(order) // 2], order[2 * len(order) // 3]])
        for rank, idx in enumerate(picks[:max_per_class]):
            run = members[int(idx)]
            prototypes.append(
                {
                    "class": int(cid),
                    "class_name": str(name),
                    "semantic": sem,
                    "family": run["family"],
                    "arm": run["arm"],
                    "seed": int(run["seed"]),
                    "steps": int(run["steps"]),
                    "prototype_rank": rank,
                    "distance_to_centroid": float(d[int(idx)]),
                    "cluster": int(cid),
                }
            )
    return prototypes


def _clone_perturbed_state(
    state: torch.Tensor,
    perturbation: dict,
    gen: torch.Generator,
    device: torch.device,
) -> Tuple[torch.Tensor, dict]:
    out = state.clone()
    meta = {"kind": perturbation["kind"]}
    if perturbation["kind"] == "amputation":
        frac = float(perturbation["fraction"])
        alpha = out[0, config.ALIVE_CHANNEL]
        alive = (torch.sigmoid(alpha) > config.ALIVE_THRESHOLD).flatten()
        idx = torch.nonzero(alive, as_tuple=False).flatten()
        n = int(round(frac * idx.numel()))
        n = min(max(n, 1), idx.numel()) if idx.numel() else 0
        if n:
            pick = _randperm(idx.numel(), generator=gen, device="cpu")[:n].to(idx.device)
            chosen = idx[pick]
            flat = out.view(1, config.N_CHANNELS, -1)
            flat[0, :, chosen] = 0.0
        meta.update(
            {
                "fraction": frac,
                "cells": int(n),
                "live_cells": int(idx.numel()),
                "zeroed": "all_channels",
            }
        )
    elif perturbation["kind"] == "noise":
        sigma = float(perturbation["sigma"])
        noise = _randn(tuple(out.shape), generator=gen, device=device)
        out = out + sigma * noise
        meta.update({"sigma": sigma})
    elif perturbation["kind"] == "cut_half":
        w = out.shape[-1]
        out[:, :, :, : w // 2] = 0.0
        meta.update({"axis": "x", "cut": int(w // 2)})
    elif perturbation["kind"] == "transplant":
        # Патч берётся по bbox бинарной маски прототипа; если маски нет,
        # пересадка не определена и пропускается.
        alive, binary, _, _, _ = _state_arrays(state)
        if not binary.any():
            meta.update({"skipped": True, "reason": "нет бинарной маски для патча"})
            out.zero_()
        else:
            ys, xs = np.nonzero(binary)
            y0, y1 = int(ys.min()), int(ys.max())
            x0, x1 = int(xs.min()), int(xs.max())
            pad = 2
            y0, y1 = max(0, y0 - pad), min(out.shape[-2] - 1, y1 + pad)
            x0, x1 = max(0, x0 - pad), min(out.shape[-1] - 1, x1 + pad)
            patch = state[:, :, y0 : y1 + 1, x0 : x1 + 1].clone()
            ph, pw = patch.shape[-2:]
            out.zero_()
            dy = (out.shape[-2] - ph) // 2
            dx = (out.shape[-1] - pw) // 2
            out[:, :, dy : dy + ph, dx : dx + pw] = patch
            meta.update({"bbox": [x0, y0, x1, y1], "patch_shape": [ph, pw]})
    elif perturbation["kind"] == "dead_control":
        out.zero_()
        meta.update({"field": "zeros"})
    else:
        raise ValueError(f"неизвестное возмущение: {perturbation['kind']}")
    return out, meta


def _prototype_state(
    spec: CheckpointSpec,
    seed: int,
    steps: int,
    every: int,
    device: torch.device,
) -> Tuple[torch.Tensor, NeuralCellularAutomaton, dict]:
    model, _ck = build_model(spec, device)
    remember_stress_ema_start(model)
    run = run_seed(model, spec, seed, steps, every, device)
    # Восстановить финальное состояние нельзя из дескрипторов; повторяем
    # развёртку и убеждаемся, что она воспроизводит финальный дескриптор.
    gen = prepare_model(model, seed)
    start = init_state(
        batch_size=1,
        channels=config.N_CHANNELS,
        grid_size=config.GRID_SIZE,
        device=device,
        generator=gen,
    )
    final_state, _points, _traj, _elapsed = rollout(model, start, steps, every)
    desc = describe_state(final_state)
    if abs(desc["alive_fraction"] - run["final"]["alive_fraction"]) > 1e-5:
        raise RuntimeError(
            f"прототип не воспроизвёлся: {spec.id} seed={seed} "
            f"alive {desc['alive_fraction']} != {run['final']['alive_fraction']}"
        )
    return final_state, model, {"seed": seed, "reproduced": True}


def _save_prototype_figure(state: torch.Tensor, title: str, path: str) -> Optional[str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    alive, binary, visible, _, _ = _state_arrays(state)
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    axes[0].imshow(visible, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("visible")
    axes[1].imshow(binary, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("binary (alive & visible)")
    axes[2].imshow(alive, cmap="gray", vmin=0, vmax=1)
    axes[2].set_title("alive")
    for ax in axes:
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def run_perturbations(
    specs: Sequence[CheckpointSpec],
    prototypes: Sequence[dict],
    clustering: dict,
    census_runs: Sequence[dict],
    steps: int = 500,
    every: int = 25,
    repeats: int = 5,
    device: torch.device = torch.device("cpu"),
) -> dict:
    by_family = {s.family: s for s in specs}
    mean = np.asarray(clustering["scaler_mean"])
    std = np.asarray(clustering["scaler_std"])
    centroids = np.asarray(clustering["centroids_z"])
    valid = clustering["labels_valid"]
    name_by_label = {int(c): str(n) for c, n in zip(valid, clustering["class_names"], strict=True)}
    sem_by_label = {int(c): str(s) for c, s in zip(valid, clustering["semantic"], strict=True)}
    outcomes = []
    prototype_rows = []
    figures = []
    for p_idx, proto in enumerate(prototypes):
        spec = by_family[proto["family"]]
        final_state, model, repro = _prototype_state(
            spec, int(proto["seed"]), int(proto["steps"]), int(proto["steps"] // 40 or 50), device
        )
        proto_stress = model.stress_ema.detach().clone()
        # Для фигуры и пересадки нужен именно финальный state; повторная
        # развёртка уже дала его.
        fig_path = os.path.join(
            FIGURES_DIR,
            f"e02b_{proto['class_name']}_{proto['family']}_s{proto['seed']}.png",
        )
        try:
            saved = _save_prototype_figure(final_state, f"{proto['class_name']} / {proto['family']} / s{proto['seed']}", fig_path)
            if saved:
                figures.append(saved)
        except Exception as exc:  # noqa: BLE001 - фигура не должна ронять перепись
            print(f"[e02b] фигура не сохранена: {exc}")
        prototype_rows.append({**proto, **repro, "figure": fig_path if os.path.exists(fig_path) else None})

        perturbation_specs = []
        for frac in (0.10, 0.20):
            for rep in range(repeats):
                perturbation_specs.append(
                    {"kind": "amputation", "fraction": frac, "repeat": rep}
                )
        for rep in range(repeats):
            perturbation_specs.append({"kind": "noise", "sigma": 0.1, "repeat": rep})
        for rep in range(repeats):
            perturbation_specs.append({"kind": "cut_half", "repeat": rep})
        for rep in range(repeats):
            perturbation_specs.append({"kind": "transplant", "repeat": rep})
        for rep in range(repeats):
            perturbation_specs.append({"kind": "dead_control", "repeat": rep})

        for rep_idx, perturbation in enumerate(perturbation_specs):
            seed = 10000 + p_idx * 1000 + rep_idx
            gen = config.create_deterministic_generator(seed)
            model.set_generator(gen)
            model.stress_ema.copy_(proto_stress)
            model._noise_cache = {}
            model._noise_seq = 0
            model.begin_segment()
            state, meta = _clone_perturbed_state(final_state, perturbation, gen, device)
            if meta.get("skipped"):
                outcomes.append(
                    {
                        "class": proto["class_name"],
                        "prototype_seed": proto["seed"],
                        "family": proto["family"],
                        "perturbation": perturbation["kind"],
                        "repeat": int(perturbation.get("repeat", 0)),
                        "skipped": True,
                        "reason": meta.get("reason"),
                    }
                )
                continue
            final, points, traj, elapsed = rollout(model, state, steps, every)
            desc = describe_state(final)
            vec = descriptor_vector(desc).reshape(1, -1)
            assigned = int(assign_to_clusters(vec, mean, std, centroids, valid)[0])
            same = bool(assigned == int(proto["cluster"]))
            outcomes.append(
                {
                    "class": proto["class_name"],
                    "cluster": int(proto["cluster"]),
                    "prototype_seed": int(proto["seed"]),
                    "family": proto["family"],
                    "perturbation": perturbation["kind"],
                    "fraction": perturbation.get("fraction"),
                    "sigma": perturbation.get("sigma"),
                    "repeat": int(perturbation.get("repeat", 0)),
                    "meta": meta,
                    "final": desc,
                    "assigned_cluster": assigned,
                    "assigned_class": name_by_label.get(assigned, "outlier"),
                    "assigned_semantic": sem_by_label.get(assigned, _cluster_semantic(desc)),
                    "returned_same_class": same,
                    "return_step": next(
                        (p["step"] for p, c in zip(points, assign_to_clusters(traj, mean, std, centroids, valid), strict=True)
                         if int(c) == int(proto["cluster"])),
                        None,
                    ),
                    "trajectory": points,
                    "wall_seconds": elapsed,
                }
            )
    # H3 считается только по 20% ампутации, как записано в протоколе.
    h3 = {}
    for proto in prototype_rows:
        cid = int(proto["cluster"])
        rows = [
            o for o in outcomes
            if o.get("cluster") == cid and o.get("perturbation") == "amputation"
            and abs(float(o.get("fraction", 0.0)) - 0.20) < 1e-9
        ]
        if not rows:
            continue
        rec = sum(1 for o in rows if o.get("returned_same_class")) / len(rows)
        h3.setdefault(str(cid), {"class": proto["class_name"], "n": len(rows), "recovery_fraction": rec})
    if h3:
        max_rec = max(v["recovery_fraction"] for v in h3.values())
        h3_summary = {
            "hypothesis": "H3: ни один класс не восстанавливается после ампутации 20%",
            "by_class": h3,
            "max_recovery_fraction": float(max_rec),
            "supported": bool(max_rec < 0.5),
            "refuted": bool(max_rec >= 0.5),
        }
    else:
        h3_summary = {
            "hypothesis": "H3: ни один класс не восстанавливается после ампутации 20%",
            "status": "not_testable",
            "reason": "нет структурных прототипов",
        }
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "prototypes": prototype_rows,
        "outcomes": outcomes,
        "h3": h3_summary,
        "figures": figures,
        "steps": int(steps),
        "every": int(every),
    }


def _outcome(census_h1: dict, h2: dict, h3: dict, runs: Sequence[dict], structural_labels: Sequence[int]) -> dict:
    # Вердикт — про выученные динамики. H-P1 и необученная модель остаются в
    # переписи как контроли, но не могут ни создать «богатую карту», ни
    # разбавить знаменатель death/uniform.
    analysis = [r for r in runs if not r.get("is_control")]
    structural = set(int(v) for v in structural_labels)
    struct_runs = [r for r in analysis if r["semantic"] == "structured"]
    death_uniform = sum(1 for r in analysis if r["semantic"] in ("death", "uniform_dark", "uniform_bright"))
    total = len(analysis)
    n_struct_classes = len(structural)
    max_repro = max(census_h1.get("struct_max_fraction_by_family", {}).values(), default=0.0)
    max_recovery = h3.get("max_recovery_fraction") if h3.get("by_class") else None
    if total and death_uniform / total >= 0.95:
        outcome = "empty_map"
        reason = "≥95% прогонов — смерть или однородное поле"
    elif max_recovery is not None and max_recovery >= 0.5 and n_struct_classes >= 2 and max_repro >= 0.8:
        outcome = "rich_map"
        reason = "≥2 структурных класса, ≥80% воспроизводимость, ≥1 класс восстановился ≥50%"
    elif max_repro >= 0.8 and max_recovery is not None and max_recovery < 0.2:
        outcome = "geometry_without_life"
        reason = "классы устойчивы, но восстановление <20%"
    else:
        outcome = "mixed"
        reason = "описать классы и ограничения без агрегированного вердикта"
    return {
        "outcome": outcome,
        "reason": reason,
        "n_runs": int(total),
        "n_structural_classes": int(n_struct_classes),
        "n_structural_runs": len(struct_runs),
        "death_or_uniform_fraction": float(death_uniform / total) if total else None,
        "max_reproducibility": float(max_repro),
        "max_recovery_20pct": max_recovery,
    }


def _preflight(specs: Sequence[CheckpointSpec], full_protocol: bool, allow_missing: bool) -> None:
    if not full_protocol:
        return
    missing_hashes = [s.id for s in specs if s.path and not s.sha256]
    if missing_hashes:
        raise SystemExit(
            "[e02b] у канонических файлов не заполнен sha256: "
            + ", ".join(missing_hashes)
        )
    free = shutil.disk_usage(os.getcwd()).free / (1024 ** 3)
    if free < 2.0:
        raise SystemExit(f"[e02b] свободно {free:.2f} ГБ < 2 ГБ — полный прогон запрещён")
    if not allow_missing and len([s for s in specs if s.path]) < 12:
        raise SystemExit(
            f"[e02b] в каноне {len([s for s in specs if s.path])}/12 файлов; "
            "полный прогон запрещён"
        )


def _device_from_arg(value: str) -> torch.device:
    if value == "auto":
        return torch.device(config.DEVICE)
    return torch.device(value)


def run_census(
    specs: Sequence[CheckpointSpec],
    seeds: Sequence[int],
    steps: int,
    every: int,
    device: torch.device,
    pilot: bool = False,
) -> dict:
    started = time.time()
    runs: List[dict] = []
    timings = []
    for spec in specs:
        t0 = time.time()
        model, ck = build_model(spec, device)
        remember_stress_ema_start(model)
        spec_runs = []
        for seed in seeds:
            run = run_seed(model, spec, seed, steps, every, device)
            spec_runs.append(run)
            runs.append(run)
        elapsed = time.time() - t0
        timings.append(
            {
                "family": spec.family,
                "n_seeds": len(seeds),
                "seconds": float(elapsed),
                "seconds_per_seed": float(elapsed / max(len(seeds), 1)),
                "checkpoint_steps": spec.steps_trained,
                "path": spec.path,
                "sha256": spec.sha256,
            }
        )
        print(
            f"[e02b] {spec.family}: {len(seeds)} сидов × {steps} шагов за {elapsed:.1f} с "
            f"({elapsed / max(len(seeds), 1):.2f} с/сид), устройство={device}"
        )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
    total_seconds = time.time() - started
    payload = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "pilot": bool(pilot),
        "hypotheses_evaluated": False,
        "device": str(device),
        "seeds": [int(s) for s in seeds],
        "steps": int(steps),
        "snapshot_every": int(every),
        "checkpoints": [
            {
                "family": s.family,
                "arm": s.arm,
                "path": s.path,
                "sha256": s.sha256,
                "kind": s.kind,
                "seed": s.seed,
                "steps_trained": s.steps_trained,
                "alive_mask_enabled": s.alive_mask_enabled,
                "overrides": s.overrides,
                "overrides_source": s.overrides_source,
            }
            for s in specs
        ],
        "timings": timings,
        "total_seconds": float(total_seconds),
        "runs": [],
    }
    if pilot:
        for r in runs:
            payload["runs"].append(
                {
                    "family": r["family"],
                    "seed": r["seed"],
                    "is_control": r.get("is_control", False),
                    "control_role": r.get("control_role"),
                    "final": r["final"],
                    "trajectory": r["trajectory"],
                    "dynamics": r["dynamics"],
                    "settle_step": r["settle_step"],
                    "alive_mask_enabled": r["alive_mask_enabled"],
                    "wall_seconds": r["wall_seconds"],
                }
            )
        payload["note"] = (
            "Pilot только для времени и smoke; гипотезы H1–H4 по нему не проверяются. "
            "Официальная перепись — 64 сида × 2000 шагов."
        )
        return payload

    full_protocol = (
        len(seeds) == 64 and list(seeds) == list(range(64)) and steps == 2000 and every == 50
    )
    payload["full_protocol"] = bool(full_protocol)
    if len(runs) >= 2:
        # Ward учится только на выученных динамиках: положительный контроль
        # (H-P1) и необученная архитектура не должны задавать форму классов.
        # Они проецируются на найденные центроиды после кластеризации.
        fit_indices = [i for i, r in enumerate(runs) if not r.get("is_control")]
        if len(fit_indices) < 2:
            fit_indices = list(range(len(runs)))
        clustering = fit_clusters([runs[i] for i in fit_indices], min_size=5, max_k=10)
        _apply_clustering(runs, clustering, fit_indices)
        structural_labels = [
            int(c)
            for c, sem in zip(clustering["labels_valid"], clustering["semantic"], strict=True)
            if sem == "structured"
            and sum(1 for r in runs if r["cluster"] == int(c) and not r.get("is_control")) >= 5
        ]
        families = [s.family for s in specs]
        h1 = evaluate_h1(runs, families)
        h2 = evaluate_h2(runs, structural_labels)
        # Смоук на 2–3 сидах — это предпросмотр, а не проверка H1–H4: протокол
        # фиксирует 64 старта × 2000 шагов. Флаг не даёт принять preview за итог.
        payload["hypotheses_evaluated"] = bool(full_protocol)
        if not full_protocol:
            payload["hypotheses_note"] = (
                "preview: не 64 сида × 2000 шагов; H1–H4 не считаются проверенными"
            )
        payload["clustering"] = {
            "features": clustering["features"],
            "scaler_mean": clustering["scaler_mean"],
            "scaler_std": clustering["scaler_std"],
            "linkage": clustering["linkage"],
            "k": clustering["k"],
            "silhouette": clustering["silhouette"],
            "sizes": clustering["sizes"],
            "outliers": clustering["outliers"],
            "labels_valid": clustering["labels_valid"],
            "class_names": clustering["class_names"],
            "semantic": clustering["semantic"],
            "medians": clustering["medians"],
            "dbscan": clustering["dbscan"],
        }
        payload["hypotheses"] = {"H1": h1, "H2": h2}
        payload["structural_labels"] = structural_labels
        payload["prototypes"] = _select_prototypes(runs, clustering)
        payload["outcome_preliminary"] = _outcome(h1, h2, {"status": "not_run"}, runs, structural_labels)
    else:
        payload["clustering"] = None
        payload["hypotheses"] = {"H1": {"status": "not_testable"}, "H2": {"status": "not_testable"}}
        payload["structural_labels"] = []
        payload["prototypes"] = []
        payload["outcome_preliminary"] = {"outcome": "mixed", "reason": "меньше двух прогонов"}
    for r in runs:
        payload["runs"].append(
            {
                "family": r["family"],
                "arm": r["arm"],
                "seed": r["seed"],
                "is_control": r.get("is_control", False),
                "control_role": r.get("control_role"),
                "final": r["final"],
                "trajectory": r["trajectory"],
                "dynamics": r["dynamics"],
                "settle_step": r["settle_step"],
                "cluster": r.get("cluster"),
                "class_name": r.get("class_name"),
                "semantic": r.get("semantic"),
                "nearest_cluster": r.get("nearest_cluster"),
                "is_outlier": r.get("is_outlier"),
                "stability_last_quarter": r.get("stability_last_quarter"),
                "class_stable_from_step": r.get("class_stable_from_step"),
                "trajectory_cluster": r.get("trajectory_cluster"),
                "trajectory_class": r.get("trajectory_class"),
                "alive_mask_enabled": r["alive_mask_enabled"],
                "wall_seconds": r["wall_seconds"],
            }
        )
    payload["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return payload, clustering if len(runs) >= 2 else None


def main(argv: Optional[Sequence[str]] = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pilot", action="store_true", help="8 сидов × 500 шагов, только замер времени")
    ap.add_argument("--seeds", default=None, help="например 0-63 или 0,1,2 (по умолчанию 0-63)")
    ap.add_argument("--steps", type=int, default=None, help="по умолчанию 2000 (pilot: 500)")
    ap.add_argument("--every", type=int, default=50, help="снимок каждые N шагов")
    ap.add_argument("--families", default="", help="фильтр семейств через запятую")
    ap.add_argument("--device", default="auto", help="auto|cuda|cpu")
    ap.add_argument("--out", default=None, help="путь census.json/pilot.json")
    ap.add_argument("--allow-missing", action="store_true", help="smoke без полного канона")
    ap.add_argument("--no-untrained", action="store_true", help="не добавлять необученный контроль")
    ap.add_argument("--no-perturbations", action="store_true", help="только перепись, без батареи")
    args = ap.parse_args(argv)

    if args.pilot:
        seeds = [0, 1, 2, 3, 4, 5, 6, 7]
        steps = 500
        out_path = args.out or PILOT_OUT
        pilot = True
    else:
        seeds = _parse_seeds(args.seeds or "0-63")
        steps = int(args.steps or 2000)
        out_path = args.out or DEFAULT_OUT
        pilot = False
    families = [x.strip() for x in args.families.split(",") if x.strip()]
    specs = load_checkpoint_specs(
        families=families or None,
        include_untrained=not args.no_untrained,
        allow_missing=bool(args.allow_missing),
    )
    if not specs:
        raise SystemExit("[e02b] нет ни одного чекпоинта под фильтр")
    device = _device_from_arg(args.device)
    full_protocol = (
        not pilot and len(seeds) == 64 and list(seeds) == list(range(64))
        and steps == 2000 and args.every == 50
    )
    _preflight(specs, full_protocol=full_protocol, allow_missing=bool(args.allow_missing))
    print(
        f"[e02b] чекпоинтов={len(specs)} сидов={len(seeds)} шагов={steps} "
        f"каждые={args.every} устройство={device} pilot={pilot}"
    )
    result = run_census(specs, seeds, steps, args.every, device, pilot=pilot)
    if pilot:
        payload = result
        clustering = None
    else:
        payload, clustering = result
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"[e02b] записано: {out_path} ({os.path.getsize(out_path) / 1e6:.1f} МБ)")
    if not pilot and clustering is not None and not args.no_perturbations:
        prototypes = payload.get("prototypes", [])
        if prototypes:
            print(f"[e02b] прототипов={len(prototypes)}; батарея возмущений 500 шагов")
            pert = run_perturbations(
                specs,
                prototypes,
                clustering,
                payload["runs"],
                steps=500,
                every=25,
                repeats=5,
                device=device,
            )
            pert_path = os.path.join(os.path.dirname(out_path), "perturbations.json")
            with open(pert_path, "w", encoding="utf-8") as fh:
                json.dump(pert, fh, ensure_ascii=False, indent=2)
            print(f"[e02b] возмущения записаны: {pert_path}")
            payload["perturbations_path"] = pert_path
            payload["hypotheses"]["H3"] = pert["h3"]
            payload["outcome"] = _outcome(
                payload["hypotheses"]["H1"],
                payload["hypotheses"]["H2"],
                pert["h3"],
                payload["runs"],
                payload["structural_labels"],
            )
            payload["hypotheses"]["H4"] = {
                "status": "not_run",
                "reason": "требует отдельной сетки вариантов локального правила; "
                          "по плану проверяется только после H1–H3 и не подменяется переписью",
            }
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
        else:
            payload["hypotheses"]["H3"] = {
                "status": "not_testable",
                "reason": "нет структурных классов ≥5 прогонов",
            }
            payload["outcome"] = payload.get("outcome_preliminary")
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
    elif not pilot:
        payload["outcome"] = payload.get("outcome_preliminary")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


if __name__ == "__main__":
    main()
