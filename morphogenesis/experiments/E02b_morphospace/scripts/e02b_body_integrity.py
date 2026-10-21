"""E02b, exploratory E06: прочность тела — сколько живых клеток можно убить.

Мы выяснили, что `struct_2` — это одно связное тело, а `struct_1` — россыпь
из ~24 крошечных островков (`geometry_of_form_exploratory.json`). Пока это
различие внешнее: два рисунка. Чтобы различие стало содержательным, у формы
должна быть измеримая **прочность**: сколько живых клеток можно убить на
месте, и ткань всё ещё удержит ту же форму.

Вопрос: у выученной формы (`struct_2`, R-9 seed42) прочность выше, чем у
архитектурного конфаунда (`struct_1` у R-9 seed101 и у необученной сети)?
Если да — обучение дало не только другую картинку, а более устойчивую ткань.
Если нет — различие между формами остаётся чисто внешним, и говорить о
«лучшей ткани» рано.

Дизайн (зафиксирован до запуска):

- три модели: R-9 seed42 (`struct_2`), R-9 seed101 (`struct_1`) и необученная
  архитектура (контроль: она тоже даёт `struct_1` 64/64);
- семь долей p = 0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0;
- 12 повторов на каждую ячейку, 2000 шагов;
- исходная точка — финальное состояние своей модели (прототип), как в
  геометрической абляции;
- повреждение: у случайно выбранных живых клеток обнуляются каналы
  0 (visible) и 1 (alive) — клетка «убита на месте»; скрытые каналы 2..15
  остаются нетронутыми (внутреннее состояние клетки сохраняется);
- p = 1.0 — полностью мёртвое поле, встроенный контроль на «мёртвое не
  возрождается».

Правила заранее (зафиксированы до запуска):

1. **Выживание**: поле живо (`alive_fraction ≥ 0.05`) И финальный класс
   совпадает с домашним классом модели.
2. **Прочность на доле p** установлена, если выживание в ≥ 11 из 12
   повторов И медианная живая доля финала ≥ 0.5 × живой доли прототипа.
3. **Прочность модели T** = наибольшая p, для которой условие 2 выполнено
   (если ни одна p не подходит, T = 0.0).
4. **Целостность тела**: медианный `alive_b0` среди выживших повторов
   (число связных живых островов). Для `struct_2` ожидается 1, для `struct_1`
   около 20.
5. **Вердикт «превосходство struct_2»**: T(struct_2) строго больше T у обоих
   конфаундов И медианный `alive_b0` у `struct_2` при его T равен 1 (тело
   осталось одним куском).
6. **Вердикт «прочность архитектурная»**: T у всех трёх моделей совпадает.
7. **Индекс ремонта**: медианный бинарный IoU финала с неповреждённым
   прототипом на каждой доле. Это отдельная ось: выживание в классе и
   восстановление именно того же рисунка — не одно и то же.

Ни обучения, ни H1–H4 здесь нет.
"""
import json
import sys
from collections import Counter
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
OUT = EXP / "body_integrity_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
CHECK = [500, 1000, 2000]
SIZE = 64
REPEATS = 12
DEAD_ALIVE = 0.05
SIGN_MIN = 11
ALIVE_KEEP_MIN = 0.5

# модель, сид прототипа, ожидаемый класс, признак «обучена»
MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("WP4_R-9_s2000_seed101", 5, "struct_1", True, 1),
    ("untrained_current_arch", 0, "struct_1", False, 2),
]

FRACTIONS = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]

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


def kill_cells(state, fraction, rng):
    """Убить на месте долю живых клеток: каналы 0 (visible) и 1 (alive).

    Скрытые каналы 2..15 не трогаем — внутреннее состояние клетки остаётся.
    Значение −10.0 вместо 0.0, чтобы «мёртвая клетка» была мёртвой
    однозначно: expit(0) = 0.5 ровно на пороге alive.
    """
    out = state.clone()
    alive = e02b._state_arrays(state)[0]
    idx = np.argwhere(alive)
    if idx.size == 0:
        return out, 0, 0
    n_kill = int(round(fraction * idx.shape[0]))
    n_kill = min(max(n_kill, 0), idx.shape[0])
    if n_kill == 0:
        return out, 0, int(idx.shape[0])
    pick = rng.choice(idx.shape[0], size=n_kill, replace=False)
    sel = idx[pick]
    out[0, config.VISIBLE_CHANNEL, sel[:, 0], sel[:, 1]] = -10.0
    out[0, config.ALIVE_CHANNEL, sel[:, 0], sel[:, 1]] = -10.0
    return out, n_kill, int(idx.shape[0])


def build_prototype(family, proto_seed, is_untrained):
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
    "kind": "exploratory_body_integrity",
    "note": (
        "прочность тела: доля живых клеток, убитых на месте; 7 долей × 12 "
        "повторов × 3 модели = 252 прогона; сравнение прочности выученной "
        "формы с архитектурным конфаундом; не H3"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "check_steps": CHECK,
    "repeats": REPEATS,
    "fractions": FRACTIONS,
    "rules": {
        "survival": (
            f"поле живо (alive >= {DEAD_ALIVE}) и финальный класс равен "
            "домашнему классу модели"
        ),
        "tolerance_at_p": (
            f"выживание в >= {SIGN_MIN} из {REPEATS} повторов и медианная "
            f"живая доля финала >= {ALIVE_KEEP_MIN} × живой доли прототипа"
        ),
        "tolerance": "наибольшая доля p, для которой выполнено условие выше",
        "body_integrity": "медианный alive_b0 среди выживших повторов",
        "verdict_superior": (
            "T(struct_2) строго больше T у обоих конфаундов И медианный "
            "alive_b0 struct_2 при его T равен 1"
        ),
        "verdict_architectural": "T у всех трёх моделей совпадает",
        "repair_index": "медианный бинарный IoU финала с неповреждённым прототипом",
    },
    "models": [],
}

for family, proto_seed, expected_class, is_untrained, model_idx in MODELS:
    model, final_state = build_prototype(family, proto_seed, is_untrained)
    try:
        proto_desc, proto_cid = classify(final_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_binary = binary_of(final_state)
        proto_alive = float(proto_desc["alive_fraction"])
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[integrity] {family} прототип seed={proto_seed} -> {proto_class} "
            f"(ожидался {expected_class}), alive={proto_alive:.3f}",
            flush=True,
        )
        rows = []
        for fi, frac in enumerate(FRACTIONS):
            for rep in range(REPEATS):
                rng = np.random.default_rng(700000 + model_idx * 10000 + fi * 100 + rep)
                host, n_killed, n_alive = kill_cells(final_state, frac, rng)
                p_seed = 95000 + model_idx * 10000 + fi * 100 + rep
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
                            "alive_b0": int(desc["alive_b0"]),
                        })
                rows.append({
                    "fraction": float(frac),
                    "repeat": rep,
                    "generator_seed": int(p_seed),
                    "damage_seed": int(700000 + model_idx * 10000 + fi * 100 + rep),
                    "alive_before": n_alive,
                    "killed": n_killed,
                    "initial_alive": float(e02b._state_arrays(host)[0].mean()),
                    "initial_binary": float(e02b._state_arrays(host)[1].mean()),
                    "points": points,
                    "final": points[-1],
                })
                print(
                    f"[integrity] {family:26s} p={frac:4.2f} rep={rep:2d} -> "
                    f"{points[-1]['assigned_class']:15s} alive={points[-1]['alive_fraction']:.3f} "
                    f"IoU={points[-1]['iou']:.3f} b0={points[-1]['alive_b0']}",
                    flush=True,
                )
        result["models"].append({
            "family": family,
            "prototype_seed": int(proto_seed),
            "expected_class": expected_class,
            "prototype_class": proto_class,
            "prototype_alive_fraction": proto_alive,
            "prototype_binary_fraction": float(proto_desc["binary_fraction"]),
            "prototype_alive_b0": int(proto_desc["alive_b0"]),
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
    by_frac = {}
    for frac in FRACTIONS:
        group = [r for r in rows if r["fraction"] == frac]
        survived = [
            r
            for r in group
            if r["final"]["assigned_class"] == entry["prototype_class"]
            and r["final"]["alive_fraction"] >= DEAD_ALIVE
        ]
        med_alive = median([r["final"]["alive_fraction"] for r in group])
        med_iou = median([r["final"]["iou"] for r in group])
        med_b0 = median([r["final"]["alive_b0"] for r in survived])
        tolerance_here = bool(
            len(survived) >= SIGN_MIN
            and med_alive is not None
            and med_alive >= ALIVE_KEEP_MIN * entry["prototype_alive_fraction"]
        )
        by_frac[str(frac)] = {
            "n": len(group),
            "n_survived": len(survived),
            "survival_fraction": float(len(survived) / len(group)) if group else None,
            "median_alive": med_alive,
            "median_iou": med_iou,
            "median_alive_b0_survived": med_b0,
            "tolerance_established": tolerance_here,
            "class_counts": dict(Counter(r["final"]["assigned_class"] for r in group)),
        }
    entry["by_fraction"] = by_frac
    established = [f for f in FRACTIONS if by_frac[str(f)]["tolerance_established"]]
    entry["tolerance"] = float(max(established)) if established else 0.0
    entry["tolerance_fractions"] = [float(f) for f in established]

tolerances = {e["family"]: e["tolerance"] for e in result["models"]}
s2 = next(e for e in result["models"] if e["expected_class"] == "struct_2")
others = [e for e in result["models"] if e["expected_class"] != "struct_2"]
s2_b0 = None
if s2["by_fraction"].get(str(s2["tolerance"])):
    s2_b0 = s2["by_fraction"][str(s2["tolerance"])]["median_alive_b0_survived"]

if all(abs(tolerances[e["family"]] - tolerances[s2["family"]]) < 1e-9 for e in others):
    verdict = "tolerance_architectural"
elif all(
    tolerances[s2["family"]] > tolerances[e["family"]] + 1e-9 for e in others
) and (s2_b0 is not None and int(s2_b0) == 1):
    verdict = "struct_2_superior"
else:
    verdict = "mixed"

result["summary"] = {
    "tolerances": tolerances,
    "struct_2_median_alive_b0_at_tolerance": s2_b0,
    "verdict": verdict,
    "per_model": {
        e["family"]: {
            "tolerance": e["tolerance"],
            "prototype_class": e["prototype_class"],
            "prototype_alive_b0": e["prototype_alive_b0"],
            "repair_index": {
                f: e["by_fraction"][f]["median_iou"] for f in e["by_fraction"]
            },
            "median_alive": {
                f: e["by_fraction"][f]["median_alive"] for f in e["by_fraction"]
            },
            "survival_fraction": {
                f: e["by_fraction"][f]["survival_fraction"] for f in e["by_fraction"]
            },
        }
        for e in result["models"]
    },
}

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[integrity] записан {OUT}", flush=True)
for e in result["models"]:
    print(
        f"[integrity] {e['family']:26s} T={e['tolerance']:.2f} "
        f"класс={e['prototype_class']} alive_b0 прототипа={e['prototype_alive_b0']}",
        flush=True,
    )
print(f"[integrity] вердикт: {verdict}", flush=True)
