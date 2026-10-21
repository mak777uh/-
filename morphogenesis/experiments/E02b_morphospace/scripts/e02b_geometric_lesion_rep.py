"""E02b, exploratory: повтор геометрической абляции с достаточной мощностью.

Первая абляция (`geometric_lesion_exploratory.json`) сделана на одном
чекпоинте (R-9 seed42, `struct_2`) с 3 повторами на повреждение. По таким
данным асимметрия «левая половина хуже правой» (IoU 0.43–0.81 против
0.74–0.84) не отличима от шума: три повтора не дают знаковой мощности.

Здесь тот же протокол, но:
- 12 повторов на каждое повреждение вместо 3;
- три модели вместо одной: R-9 seed42 (`struct_2`), R-9 seed101 (`struct_1`)
  и необученная архитектура (контроль: она тоже даёт `struct_1` 64/64);
- те же 6 повреждений, 2000 шагов, срезы 500/1000/2000.

Вопрос: различаются ли половины поля систематически, и — главное — чей это
свойство: класса, чекпоинта или самой архитектуры. Если асимметрия есть и у
необученной модели, она архитектурная, а не выученная.

Правила заранее (зафиксированы до запуска):

1. Асимметрия оси считается УСТАНОВЛЕННОЙ, если оба условия выполнены:
   - знак парной разности IoU одинаков минимум в 11 из 12 повторов
     (односторонний знаковый тест, p ≤ 0.00049);
   - модуль средней разности IoU ≥ 0.05.
   Иначе — «не установлена».
2. Ось: cut_left против cut_right, cut_top против cut_bottom. Обе половины
   равны по площади, поэтому сравнение парное и справедливое.
3. Сохранение класса считается по финальному классу (после проверки, что поле
   живо: alive ≥ 0.05).
4. Прототип: для обученных — тот же прототип, что в первой абляции (R-9
   seed42, старт seed 35); для R-9 seed101 — старт seed 5; для необученной
   архитектуры — инициализация 42, старт seed 0. Класс прототипа проверяется
   и пишется в артефакт: если он не ожидаемый, модель исключается из
   проверки асимметрии (но не из отчёта).

Ни обучения, ни H1–H4 здесь нет.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
MORPH = HERE.parents[3]
sys.path.insert(0, str(MORPH))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "geometric_lesion_rep_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
CHECK = [500, 1000, 2000]
SIZE = 64
REPEATS = 12
DEAD_ALIVE = 0.05
SIGN_MIN = 11
MEAN_DIFF_MIN = 0.05

# модель, сид прототипа, ожидаемый класс, признак «обучена»
MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("WP4_R-9_s2000_seed101", 5, "struct_1", True, 1),
    ("untrained_current_arch", 0, "struct_1", False, 2),
]

LESIONS = ["cut_left", "cut_right", "cut_top", "cut_bottom", "center_16", "center_32"]
AXES = [("cut_left", "cut_right"), ("cut_top", "cut_bottom")]

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
        by_cluster[cid].append(e02b.descriptor_vector(r["final"]))
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
    return float(np.logical_and(a, b).sum() / u) if u else 1.0


def lesion(name, state):
    out = state.clone()
    if name == "cut_left":
        out[:, :, :, : SIZE // 2] = 0.0
    elif name == "cut_right":
        out[:, :, :, SIZE // 2:] = 0.0
    elif name == "cut_top":
        out[:, :, : SIZE // 2, :] = 0.0
    elif name == "cut_bottom":
        out[:, :, SIZE // 2:, :] = 0.0
    elif name == "center_16":
        a = SIZE // 2 - 8
        out[:, :, a:a + 16, a:a + 16] = 0.0
    elif name == "center_32":
        a = SIZE // 2 - 16
        out[:, :, a:a + 32, a:a + 32] = 0.0
    else:
        raise ValueError(name)
    return out


def build_prototype(family, proto_seed, is_untrained):
    """Прототип: финальное состояние своей модели перед повреждением."""
    spec = e02b.load_checkpoint_specs(
        families=[family], include_untrained=not is_untrained
    )[0]
    if is_untrained:
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
        final, _points, _traj, _elapsed = e02b.rollout(model, start, STEPS, 50)
        return model, final
    final, model, _run = e02b._prototype_state(spec, proto_seed, STEPS, 50, DEVICE)
    return model, final


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_geometric_lesion_replication",
    "note": (
        "12 повторов на повреждение, три модели (struct_2, struct_1 и "
        "необученная архитектура); 6 повреждений × 12 повторов × 3 модели = 216 "
        "прогонов; проверка асимметрии половин знаковым тестом; не H3"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "check_steps": CHECK,
    "repeats": REPEATS,
    "rules": {
        "asymmetry_established": (
            f"знак парной разности IoU одинаков в >= {SIGN_MIN} из {REPEATS} "
            f"повторов и |средняя разность| >= {MEAN_DIFF_MIN}"
        ),
        "axes": [list(a) for a in AXES],
        "class_retention": "финальный класс совпадает с классом прототипа и alive >= 0.05",
    },
    "models": [],
}

for family, proto_seed, expected_class, is_untrained, model_idx in MODELS:
    model, final_state = build_prototype(family, proto_seed, is_untrained)
    try:
        proto_desc, proto_cid = classify(final_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_binary = binary_of(final_state)
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[lesion-rep] {family} прототип seed={proto_seed} -> {proto_class} "
            f"(ожидался {expected_class})",
            flush=True,
        )
        rows = []
        for li, name in enumerate(LESIONS):
            for rep in range(REPEATS):
                host = lesion(name, final_state)
                p_seed = 90000 + model_idx * 10000 + li * 100 + rep
                gen = config.create_deterministic_generator(p_seed)
                model.set_generator(gen)
                model.stress_ema.copy_(proto_stress)
                model._noise_cache = {}
                model._noise_seq = 0
                model.begin_segment()
                state = host
                points = []
                for step in range(1, STEPS + 1):
                    with torch.no_grad():
                        state = model(state)
                    if step in CHECK:
                        desc, assigned = classify(state)
                        b = binary_of(state)
                        points.append({
                            "step": step,
                            "assigned_class": names.get(assigned, "outlier"),
                            "iou": iou(b, proto_binary),
                            "binary_fraction": float(b.mean()),
                            "alive_fraction": float(desc["alive_fraction"]),
                        })
                rows.append({
                    "lesion": name,
                    "repeat": rep,
                    "generator_seed": int(p_seed),
                    "initial_alive": float(e02b._state_arrays(host)[0].mean()),
                    "initial_binary": float(e02b._state_arrays(host)[1].mean()),
                    "points": points,
                    "final": points[-1],
                })
                print(
                    f"[lesion-rep] {family:26s} {name:11s} rep={rep:2d} -> "
                    f"{points[-1]['assigned_class']:15s} IoU={points[-1]['iou']:.3f}",
                    flush=True,
                )
        result["models"].append({
            "family": family,
            "prototype_seed": int(proto_seed),
            "expected_class": expected_class,
            "prototype_class": proto_class,
            "prototype_alive_fraction": float(proto_desc["alive_fraction"]),
            "prototype_binary_fraction": float(proto_desc["binary_fraction"]),
            "prototype_matches_expected": bool(proto_class == expected_class),
            "is_untrained": bool(is_untrained),
            "rows": rows,
        })
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def median(values):
    vals = sorted(values)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return float(vals[mid])
    return 0.5 * (float(vals[mid - 1]) + float(vals[mid]))


for entry in result["models"]:
    rows = entry["rows"]
    by_lesion = {}
    for name in LESIONS:
        group = [r for r in rows if r["lesion"] == name]
        ious = [r["final"]["iou"] for r in group]
        retained = [
            r for r in group
            if r["final"]["assigned_class"] == entry["prototype_class"]
            and r["final"]["alive_fraction"] >= DEAD_ALIVE
        ]
        by_lesion[name] = {
            "n": len(group),
            "iou_median": median(ious),
            "iou_min": min(ious),
            "iou_max": max(ious),
            "class_retained_n": len(retained),
            "class_retained_fraction": len(retained) / len(group) if group else None,
            "alive_median": median([r["final"]["alive_fraction"] for r in group]),
        }
    axes = {}
    for left, right in AXES:
        left_iou = {r["repeat"]: r["final"]["iou"] for r in rows if r["lesion"] == left}
        right_iou = {r["repeat"]: r["final"]["iou"] for r in rows if r["lesion"] == right}
        diffs = [
            left_iou[k] - right_iou[k] for k in sorted(set(left_iou) & set(right_iou))
        ]
        positive = sum(1 for d in diffs if d > 0)
        negative = sum(1 for d in diffs if d < 0)
        same_sign = max(positive, negative)
        mean_diff = sum(diffs) / len(diffs) if diffs else 0.0
        established = bool(
            same_sign >= SIGN_MIN and abs(mean_diff) >= MEAN_DIFF_MIN
        )
        axes[f"{left}_vs_{right}"] = {
            "n_pairs": len(diffs),
            "left_median": median(list(left_iou.values())),
            "right_median": median(list(right_iou.values())),
            "mean_diff_left_minus_right": mean_diff,
            "positive_n": positive,
            "negative_n": negative,
            "same_sign_n": same_sign,
            "asymmetry_established": established,
        }
    entry["by_lesion"] = by_lesion
    entry["axes"] = axes
    entry["class_retained_fraction"] = (
        sum(1 for r in rows
            if r["final"]["assigned_class"] == entry["prototype_class"]
            and r["final"]["alive_fraction"] >= DEAD_ALIVE)
        / len(rows)
        if rows else None
    )
    entry["asymmetry_established_any"] = any(
        a["asymmetry_established"] for a in axes.values()
    )

result["summary"] = {
    "n_rows": sum(len(m["rows"]) for m in result["models"]),
    "models": {
        m["family"]: {
            "prototype_class": m["prototype_class"],
            "prototype_matches_expected": m["prototype_matches_expected"],
            "class_retained_fraction": m["class_retained_fraction"],
            "asymmetry": {
                k: {
                    "mean_diff": v["mean_diff_left_minus_right"],
                    "same_sign_n": v["same_sign_n"],
                    "n_pairs": v["n_pairs"],
                    "established": v["asymmetry_established"],
                }
                for k, v in m["axes"].items()
            },
            "asymmetry_established_any": m["asymmetry_established_any"],
            "by_lesion": {
                k: {
                    "iou_median": v["iou_median"],
                    "class_retained_fraction": v["class_retained_fraction"],
                }
                for k, v in m["by_lesion"].items()
            },
        }
        for m in result["models"]
    },
}
print(f"[lesion-rep] summary {json.dumps(result['summary'], ensure_ascii=False)}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[lesion-rep] written {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB)", flush=True)
