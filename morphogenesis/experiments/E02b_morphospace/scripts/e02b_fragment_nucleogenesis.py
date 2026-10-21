"""E02b, exploratory: растёт ли целая форма из крошечного живого очага?

Вопрос «цифровой геометрии жизни»: умеет ли система не только ДЕРЖАТЬ форму
(это показали абляции и пересадки), но и ВЫРАСТИВАТЬ её заново из малого
зачатка? Взрослая ткань, у которой отрезали большую часть, восстанавливает
себя — это ремонт. Маленький живой очаг, из которого разрастается вся
структура, — это морфогенез, то есть самостоятельное становление формы.

Что уже известно и чего в этом прогоне нет:
- `patch_transplant`/`patch_identity`: патчи 8×8/16×16/32×32 (64–1024 клетки)
  вырастали в свой класс 30/30, но глобальный рисунок не восстанавливался.
  Горизонт был 500 шагов, моделей две, повторов по 5, размеров три.
- `transition_matrix`: остаток H-P1 в 83 живых клеток дал полную структуру
  в 3 моделях из 12 — единичное наблюдение, без повторов и без порога.

Здесь — систематическая кривая по размеру зачатка, с повторами, длинным
горизонтом и тремя моделями (две обученные + архитектурный контроль):
- размеры зачатка k = 1, 8, 32, 128, 512 живых клеток, два способа выбора
  (`scattered` — случайно разбросанные клетки, `compact` — k ближайших к
  случайной опорной клетке, то есть пространственно компактный очаг);
  определение `compact` уточнено до запуска: топологически связного куска
  живой ткани нужного размера у большинства прототипов не существует
  (у `struct_2` живая маска — 1745 компонент, крупнейшая 164 клетки);
- контроль k = 0 (полностью мёртвое поле) — обязателен: если в нём что-то
  прорастает, тест недействителен;
- 2000 шагов, срезы каждые 50, 12 повторов на каждую ячейку;
- измеряется не только класс, но и РОСТ: расширяется ли живая область от
  зачатка (ткань растёт) или поле сразу релаксирует в аттрактор (зачаток
  не влияет на исход).

Правила заранее (зафиксированы до запуска):

1. `nucleogenesis_established` (для ячейки модель × режим × k): в ≥ 11 из 12
   повторов выполняются три условия одновременно:
   а) поле живо на финале: alive_fraction ≥ 0.05 (DEAD_ALIVE);
   б) финальный класс совпадает с домашним классом модели;
   в) живая область выросла: alive_cells(2000) ≥ 0.5 · alive_cells(прототипа).
   11 из 12 — односторонний знаковый тест, p ≤ 0.00049.
2. `same_pattern_rebuilt` — то же самое, но дополнительно бинарный IoU
   финала с бинарной маской прототипа ≥ 0.5: восстановлен не только класс,
   но и тот же глобальный рисунок. Это сильнее, чем (1).
3. `minimal_seed_size` — наименьшее k, для которого выполнено (1) для данной
   модели и режима; если ни одно k не подходит — `None`.
4. Контроль k = 0 обязан дать 0 из 12 пробуждений. Если в контроле ≥ 11 из 12,
   весь блок помечается `control_failed` и выводы о пороге не делаются.
5. Рост против релаксации (описательно, не критерий): `expansion_factor` =
   alive_cells(2000) / k. Значение ≥ 10 — «рост»; значение < 3 — «релаксация
   без расширения» (зачаток не влияет на исход, поле само приходит к форме).
6. Живость исхода всегда определяется по alive, а не по метке класса.
   Расхождение (метка структурного класса при мёртвом поле) помечается
   флагом `class_alive_conflict`.

Дополнительно — перекрёстный блок: очаг чужого класса (struct_1 в seed42 и
struct_2 в seed101) при k = 32, 12 повторов. Он отвечает на вопрос, чей это
рост: своей или чужой формы.

Ни обучения, ни H1–H4 здесь нет: только измерения по уже обученным
моделям. Строки пишутся инкрементально в JSONL, чтобы прерванный прогон
не терялся.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "fragment_nucleogenesis_exploratory.json"
ROWS = EXP / "fragment_nucleogenesis_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
REPEATS = 12
DEAD_ALIVE = 0.05
SIGN_MIN = 11
IOU_MIN = 0.5
ALIVE_GROWTH_MIN = 0.5
EXPANSION_GROWTH = 10.0
EXPANSION_RELAX = 3.0

# модель, сид прототипа, ожидаемый класс, обучена ли, индекс для сидов
MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("WP4_R-9_s2000_seed101", 5, "struct_1", True, 1),
    ("untrained_current_arch", 0, "struct_1", False, 2),
]
SIZES = [1, 8, 32, 128, 512]
MODES = ["scattered", "compact"]
CONTROL_SIZE = 0

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
by_cluster = {int(c): [] for c in valid}
for r in census["runs"]:
    if r.get("is_control"):
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[int(cid)].append(e02b.descriptor_vector(r["final"]))
centroids = np.vstack([np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid])
centroids = (centroids - mean) / std
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}


def binary_of(state):
    return e02b._state_arrays(state)[1]


def classify(state):
    d = e02b.describe_state(state)
    cid = int(
        e02b.assign_to_clusters(
            e02b.descriptor_vector(d).reshape(1, -1), mean, std, centroids, valid
        )[0]
    )
    return d, cid


def iou(a, b):
    u = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / u) if u else 0.0


def build_prototype(family, proto_seed, is_trained):
    """Прототип: финальное состояние своей модели (для контроля — untrained).

    Для выученных моделей — канонический путь `e02b._prototype_state`: EMA из
    чекпоинта восстановлена, развёртка проверена повтором `run_seed`. Для
    необученного контроля — отдельная ветка с фиксированной инициализацией
    (seed 42), потому что у него нет чекпоинта.

    ВНИМАНИЕ: в первой версии скрипта четвёртое поле в MODELS читалось
    наоборот, и выученные модели собирались веткой с обнулённой
    stress_ema. Прогон 20261021T112714Z сделан с той, ошибочной версией.
    """
    spec = e02b.load_checkpoint_specs(
        families=[family], include_untrained=not is_trained
    )[0]
    if not is_trained:
        torch.manual_seed(42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(42)
        model, _ = e02b.build_model(spec, DEVICE)
        e02b.prepare_model(model, proto_seed)
        start = e02b.init_state(
            batch_size=1,
            channels=config.N_CHANNELS,
            grid_size=config.GRID_SIZE,
            device=DEVICE,
            generator=model.generator,
        )
        final, _points, _traj, _elapsed = e02b.rollout(model, start, STEPS, EVERY)
        return model, final
    final, model, _run = e02b._prototype_state(spec, proto_seed, STEPS, EVERY, DEVICE)
    return model, final


def largest_component(mask):
    """Самая большая связная компонента маски (соседство по стороне)."""
    from scipy import ndimage

    labeled, n = ndimage.label(mask)
    if n == 0:
        return mask, 0
    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0
    best = int(sizes.argmax())
    return labeled == best, int(sizes[best])


def _seed_components(mask):
    """Сколько связных кусков в очаге (4-соседство)."""
    from scipy import ndimage

    _labeled, n = ndimage.label(mask)
    return int(n)


def compact_cells(alive_mask, k, rng):
    """k пространственно компактных живых клеток.

    Связный (топологически) кусок живой ткани у большинства прототипов
    не существует: у `struct_2` (R-9 seed42) живая маска состоит из 1745
    компонент, самая большая — 164 клетки; у необученной архитектуры —
    309 компонент, самая большая — 217. Очаг размера 512 в таком случае
    просто не из чего собрать, и строка молча выпала бы из эксперимента.
    Поэтому определение уточнено ДО запуска: «компактный» очаг — это k
    ближайших к случайной опорной клетке живых клеток. Сравнение с
    `scattered` (k случайно разбросанных живых клеток) сохраняет смысл:
    различаются только пространственная укладка и связность очага.
    """
    idx = np.argwhere(alive_mask)
    if len(idx) < k:
        return None, len(idx)
    anchor = idx[rng.integers(len(idx))]
    dist = ((idx - anchor) ** 2).sum(axis=1)
    order = np.argsort(dist, kind="stable")
    pick = idx[order[:k]]
    chosen = {(int(cy), int(cx)) for cy, cx in pick}
    return chosen, len(idx)


def make_fragment(state, alive_mask, k, mode, rng):
    """Оставить k живых клеток, остальное обнулить (все каналы).

    k = 0 — полностью мёртвое поле (нулевой тензор): это контроль,
    в котором ничего живого не должно прорасти.
    """
    if k == 0:
        return torch.zeros_like(state), np.zeros_like(alive_mask)
    if mode == "compact":
        cells, available = compact_cells(alive_mask, k, rng)
        if cells is None or len(cells) < k:
            return None, available
        keep = np.zeros_like(alive_mask)
        for cy, cx in cells:
            keep[cy, cx] = True
    else:
        idx = np.argwhere(alive_mask)
        if len(idx) < k:
            return None, len(idx)
        pick = idx[rng.choice(len(idx), size=k, replace=False)]
        keep = np.zeros_like(alive_mask)
        for cy, cx in pick:
            keep[cy, cx] = True
    out = state.clone()
    out[:, :, ~keep] = 0.0
    return out, keep


def run_one(model, proto_stress, proto_alive, proto_binary, host, p_seed):
    """Одна развёртка от очага: класс, живость, IoU с прототипом, кривые."""
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    snap_class = []
    snap_alive = []
    snap_binary = []
    for step in range(1, STEPS + 1):
        with torch.no_grad():
            state = model(state)
        if step % EVERY == 0 or step == STEPS:
            d, cid = classify(state)
            snap_class.append(names.get(cid, "outlier"))
            snap_alive.append(float(d["alive_fraction"]))
            snap_binary.append(float(d["binary_fraction"]))
    d, cid = classify(state)
    final_class = names.get(cid, "outlier")
    fin_bin = binary_of(state)
    return {
        "final_class": final_class,
        "final_cluster": int(cid),
        "final_alive": float(d["alive_fraction"]),
        "final_binary": float(d["binary_fraction"]),
        "alive_cells": int(round(float(d["alive_fraction"]) * 4096)),
        "iou_vs_prototype": iou(fin_bin, proto_binary),
        "class_alive_conflict": bool(
            (d["alive_fraction"] < DEAD_ALIVE and final_class in {"struct_1", "struct_2"})
            or (d["alive_fraction"] >= DEAD_ALIVE and final_class == "death")
        ),
        "snap_class": snap_class,
        "snap_alive": snap_alive,
        "snap_binary": snap_binary,
    }


def alive_cells_from_fraction(frac, n_cells=4096):
    return int(round(frac * n_cells))


if ROWS.exists():
    with open(ROWS, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    print(f"[frag] возобновление: {len(rows)} строк уже посчитано", flush=True)
else:
    rows = []
done = {(r["model"], r["mode"], int(r["k"]), int(r["repeat"]), r["role"]) for r in rows}
fh = open(ROWS, "a", encoding="utf-8")

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_fragment_nucleogenesis",
    "note": (
        "порог по размеру зачатка: 5 размеров × 2 режима × 12 повторов × 3 модели "
        "+ контроль k=0 + перекрёстный блок; проверка роста, а не только класса; "
        "не H1–H4 и не обучение"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "repeats": REPEATS,
    "sizes": SIZES,
    "modes": MODES,
    "control_size": CONTROL_SIZE,
    "rules": {
        "nucleogenesis_established": (
            f"живо (alive >= {DEAD_ALIVE}) и домашний класс и живая область >= "
            f"{ALIVE_GROWTH_MIN} от прототипа, минимум {SIGN_MIN} из {REPEATS} повторов"
        ),
        "same_pattern_rebuilt": (
            f"то же плюс бинарный IoU с прототипом >= {IOU_MIN}"
        ),
        "minimal_seed_size": "наименьшее k с выполненным nucleogenesis_established",
        "control": "k=0 обязан дать 0 пробуждений; иначе блок помечается control_failed",
        "expansion": (
            f"expansion_factor = alive_cells(2000)/k; >= {EXPANSION_GROWTH} — рост, "
            f"< {EXPANSION_RELAX} — релаксация без расширения"
        ),
        "liveness": "исход жив, если alive >= 0.05, метка класса не определяет живость",
    },
    "models": [],
    "rows": rows,
}

for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, final_state = build_prototype(family, proto_seed, is_trained)
    try:
        proto_desc, proto_cid = classify(final_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_binary = binary_of(final_state)
        proto_alive_mask = e02b._state_arrays(final_state)[0]
        proto_alive_cells = int(proto_alive_mask.sum())
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[frag] {family} прототип seed={proto_seed} -> {proto_class} "
            f"(ожидался {expected_class}) alive_cells={proto_alive_cells} "
            f"binary={proto_binary.mean():.3f}",
            flush=True,
        )
        model_block = {
            "family": family,
            "prototype_seed": int(proto_seed),
            "prototype_class": proto_class,
            "expected_class": expected_class,
            "class_matches_expected": bool(proto_class == expected_class),
            "prototype_alive_cells": proto_alive_cells,
            "prototype_alive_fraction": float(proto_alive_mask.mean()),
            "prototype_binary_fraction": float(proto_binary.mean()),
            "prototype_alive_components": int(_seed_components(proto_alive_mask)),
            "prototype_largest_alive_component": int(
                largest_component(proto_alive_mask)[1]
            ),
            "cells": [],
        }

        for mode in MODES:
            for k in SIZES:
                key_base = (family, mode, k)
                cell_rows = []
                for rep in range(REPEATS):
                    key = (family, mode, k, rep, "own")
                    if key in done:
                        cell_rows.append(
                            next(r for r in rows if (
                                r["model"], r["mode"], int(r["k"]), int(r["repeat"]),
                                r["role"]) == key)
                        )
                        continue
                    rng = np.random.default_rng(700000 + model_idx * 10000 + k * 100 + rep)
                    host, keep = make_fragment(
                        final_state, proto_alive_mask, k, mode, rng
                    )
                    if host is None:
                        row = {
                            "model": family,
                            "mode": mode,
                            "k": int(k),
                            "repeat": int(rep),
                            "role": "own",
                            "error": "недостаточно живых клеток для очага",
                            "final_class": "error",
                            "final_alive": 0.0,
                            "final_binary": 0.0,
                            "alive_cells": 0,
                            "iou_vs_prototype": 0.0,
                            "alive_growth_ratio": 0.0,
                            "expansion_factor": 0.0,
                            "class_alive_conflict": False,
                            "seed_cells": 0,
                            "seed_components": 0,
                            "snap_class": [],
                            "snap_alive": [],
                            "snap_binary": [],
                        }
                        rows.append(row)
                        cell_rows.append(row)
                        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                        fh.flush()
                        continue
                    p_seed = 710000 + model_idx * 10000 + k * 100 + rep * 7 + (0 if mode == "scattered" else 1)
                    res = run_one(
                        model, proto_stress, proto_alive_mask, proto_binary, host, p_seed
                    )
                    row = {
                        "model": family,
                        "mode": mode,
                        "k": int(k),
                        "repeat": int(rep),
                        "role": "own",
                        "generator_seed": int(p_seed),
                        "seed_cells": int(keep.sum()),
                        "seed_components": int(_seed_components(keep)),
                        "seed_alive_fraction": float(keep.mean()),
                        "home_class": proto_class,
                        "alive_growth_ratio": (
                            res["final_alive"] / max(proto_alive_mask.mean(), 1e-9)
                        ),
                        "expansion_factor": (
                            res["final_alive"] * 4096 / float(max(int(keep.sum()), 1))
                        ),
                        **res,
                    }
                    rows.append(row)
                    cell_rows.append(row)
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    print(
                        f"[frag] {family} {mode} k={k} rep={rep} -> {res['final_class']} "
                        f"alive={res['final_alive']:.3f} iou={res['iou_vs_prototype']:.3f}",
                        flush=True,
                    )
                good = [r for r in cell_rows if "error" not in r]
                nuc = [
                    r for r in good
                    if r["final_alive"] >= DEAD_ALIVE
                    and r["final_class"] == proto_class
                    and r["alive_growth_ratio"] >= ALIVE_GROWTH_MIN
                ]
                same = [r for r in nuc if r["iou_vs_prototype"] >= IOU_MIN]
                model_block["cells"].append({
                    "mode": mode,
                    "k": int(k),
                    "n": len(good),
                    "nucleogenesis_count": len(nuc),
                    "same_pattern_count": len(same),
                    "nucleogenesis_established": bool(len(nuc) >= SIGN_MIN),
                    "same_pattern_rebuilt": bool(len(same) >= SIGN_MIN),
                    "median_iou": (
                        float(np.median([r["iou_vs_prototype"] for r in good])) if good else None
                    ),
                    "median_alive": (
                        float(np.median([r["final_alive"] for r in good])) if good else None
                    ),
                    "median_expansion": (
                        float(np.median([r["expansion_factor"] for r in good])) if good else None
                    ),
                    "class_counts": dict(Counter(r["final_class"] for r in good)),
                    "conflicts": sum(1 for r in good if r["class_alive_conflict"]),
                })

        # контроль: полностью мёртвое поле в той же модели
        control_rows = []
        for rep in range(REPEATS):
            key = (family, "scattered", CONTROL_SIZE, rep, "control")
            if key in done:
                control_rows.append(
                    next(r for r in rows if (
                        r["model"], r["mode"], int(r["k"]), int(r["repeat"]),
                        r["role"]) == key)
                )
                continue
            host, keep = make_fragment(final_state, proto_alive_mask, 0, "scattered", None)
            p_seed = 720000 + model_idx * 10000 + rep
            res = run_one(model, proto_stress, proto_alive_mask, proto_binary, host, p_seed)
            row = {
                "model": family,
                "mode": "scattered",
                "k": CONTROL_SIZE,
                "repeat": int(rep),
                "role": "control",
                "generator_seed": int(p_seed),
                "seed_cells": 0,
                "seed_alive_fraction": 0.0,
                "home_class": proto_class,
                "alive_growth_ratio": 0.0,
                "expansion_factor": 0.0,
                **res,
            }
            rows.append(row)
            control_rows.append(row)
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
        model_block["control"] = {
            "n": len(control_rows),
            "alive_count": sum(1 for r in control_rows if r["final_alive"] >= DEAD_ALIVE),
            "class_counts": dict(Counter(r["final_class"] for r in control_rows)),
        }
        result["models"].append(model_block)
        print(
            f"[frag] {family} контроль k=0: живых {model_block['control']['alive_count']}"
            f"/{REPEATS} {model_block['control']['class_counts']}",
            flush=True,
        )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ------------------------------------------------- перекрёстный блок: чужой очаг
CROSS = [
    ("WP4_R-9_s2000_seed42", 35, "WP4_R-9_s2000_seed101", 5, "struct_1", 32),
    ("WP4_R-9_s2000_seed101", 5, "WP4_R-9_s2000_seed42", 35, "struct_2", 32),
]
cross_block = []
for target_family, target_seed, src_family, src_seed, src_class, k in CROSS:
    spec_t = e02b.load_checkpoint_specs(families=[target_family], include_untrained=False)[0]
    model_t, _ = e02b.build_model(spec_t, DEVICE)
    spec_s = e02b.load_checkpoint_specs(families=[src_family], include_untrained=False)[0]
    src_state, _model_s, _run = e02b._prototype_state(spec_s, src_seed, STEPS, EVERY, DEVICE)
    src_alive = e02b._state_arrays(src_state)[0]
    src_binary = binary_of(src_state)
    try:
        home_desc, home_cid = classify(src_state)
        target_rows = []
        for rep in range(REPEATS):
            key = (target_family, "cross", k, rep, f"cross:{src_family}")
            if key in done:
                target_rows.append(
                    next(r for r in rows if (
                        r["model"], r["mode"], int(r["k"]), int(r["repeat"]),
                        r["role"]) == key)
                )
                continue
            rng = np.random.default_rng(800000 + rep)
            host, keep = make_fragment(src_state, src_alive, k, "scattered", rng)
            if host is None:
                continue
            # У целевой модели своя память о стрессе: восстанавливаем EMA из
            # её чекпоинта (как в матрице пересадок), а не из источника.
            e02b.prepare_model(model_t, 810000 + rep)
            model_t._noise_cache = {}
            model_t._noise_seq = 0
            model_t.begin_segment()
            state = host
            snap_class = []
            for step in range(1, STEPS + 1):
                with torch.no_grad():
                    state = model_t(state)
                if step % EVERY == 0 or step == STEPS:
                    _d, cid = classify(state)
                    snap_class.append(names.get(cid, "outlier"))
            d, cid = classify(state)
            final_class = names.get(cid, "outlier")
            row = {
                "model": target_family,
                "mode": "cross",
                "k": int(k),
                "repeat": int(rep),
                "role": f"cross:{src_family}",
                "source_family": src_family,
                "source_class": src_class,
                "generator_seed": int(810000 + rep),
                "seed_cells": int(keep.sum()),
                "final_class": final_class,
                "final_alive": float(d["alive_fraction"]),
                "final_binary": float(d["binary_fraction"]),
                "iou_vs_source": iou(binary_of(state), src_binary),
                "class_alive_conflict": bool(
                    d["alive_fraction"] < DEAD_ALIVE and final_class in {"struct_1", "struct_2"}
                ),
                "snap_class": snap_class,
            }
            rows.append(row)
            target_rows.append(row)
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            print(
                f"[frag] cross {target_family} <- {src_family} k={k} rep={rep} -> {final_class}",
                flush=True,
            )
        cross_block.append({
            "target": target_family,
            "source": src_family,
            "source_class": src_class,
            "k": int(k),
            "n": len(target_rows),
            "class_counts": dict(Counter(r["final_class"] for r in target_rows)),
            "alive_count": sum(1 for r in target_rows if r["final_alive"] >= DEAD_ALIVE),
            "median_iou_vs_source": (
                float(np.median([r["iou_vs_source"] for r in target_rows])) if target_rows else None
            ),
        })
    finally:
        del model_t, _model_s
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

fh.close()

# ------------------------------------------------------------------ сводка
for mb in result["models"]:
    mins = {}
    for mode in MODES:
        cands = [
            c["k"] for c in mb["cells"]
            if c["mode"] == mode and c["nucleogenesis_established"]
        ]
        mins[mode] = min(cands) if cands else None
    same_mins = {}
    for mode in MODES:
        cands = [
            c["k"] for c in mb["cells"]
            if c["mode"] == mode and c["same_pattern_rebuilt"]
        ]
        same_mins[mode] = min(cands) if cands else None
    mb["minimal_seed_size"] = mins
    mb["minimal_seed_size_same_pattern"] = same_mins
    ctrl = mb.get("control", {})
    mb["control_failed"] = bool(ctrl.get("alive_count", 0) >= SIGN_MIN)
    if mb["control_failed"]:
        mb["minimal_seed_size"] = {m: None for m in MODES}
        mb["minimal_seed_size_same_pattern"] = {m: None for m in MODES}

result["cross"] = cross_block
result["summary"] = {
    "n_rows": len(rows),
    "models": [
        {
            "family": mb["family"],
            "prototype_class": mb["prototype_class"],
            "class_matches_expected": mb["class_matches_expected"],
            "minimal_seed_size": mb["minimal_seed_size"],
            "minimal_seed_size_same_pattern": mb["minimal_seed_size_same_pattern"],
            "control_alive": mb.get("control", {}).get("alive_count"),
            "control_failed": mb["control_failed"],
        }
        for mb in result["models"]
    ],
    "cross": [
        {
            "target": c["target"],
            "source": c["source"],
            "class_counts": c["class_counts"],
            "alive_count": c["alive_count"],
        }
        for c in cross_block
    ],
    "nucleogenesis_established_cells": sum(
        1
        for mb in result["models"]
        for c in mb["cells"]
        if c["nucleogenesis_established"]
    ),
    "same_pattern_rebuilt_cells": sum(
        1
        for mb in result["models"]
        for c in mb["cells"]
        if c["same_pattern_rebuilt"]
    ),
    "total_cells": sum(len(mb["cells"]) for mb in result["models"]),
}
print(f"[frag] summary {json.dumps(result['summary'], ensure_ascii=False)}", flush=True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"[frag] saved {OUT}", flush=True)
