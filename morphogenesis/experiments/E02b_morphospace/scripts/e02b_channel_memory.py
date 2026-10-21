"""E02b E04: где живёт форма — в видимой текстуре или в скрытых каналах?

Вопрос: когда ткань «помнит» свою форму, память лежит в том, что видно
(канал 0), или в том, что не видно, но хранится внутри клеток (скрытые
каналы)? Это разные утверждения, и сейчас в репозитории нет ни одного
измерения, которое их разделяло.

Каналы (фиксированы в config.py):
  0 VISIBLE  — то, что «видно»;
  1 ALIVE    — канал живости, из него считается alive = expit(alpha) > 0.5;
  2..15      — невидимые каналы (включая STRESS = 15); в тексте ниже — HIDDEN.

Важно: alive считается ИМЕННО из канала 1, поэтому канал 1 нельзя обнулять
— поле погибло бы тривиально, и тест ничего не сказал бы о памяти.

Условия (повреждение наносится по каналам прототипа своей модели):
  1. `none`            — контроль: прототип не тронут;
  2. `visible_zeroed`  — канал 0 обнулён, скрытое состояние цело;
  3. `hidden_zeroed`   — каналы 2..15 обнулены, видимая текстура цела;
  4. `hidden_shuffled` — видимая текстура цела, значения скрытых каналов
     переставлены случайным образом по позициям (гистограмма каждого канала
     сохраняется, пространственная связь — нет).

Правила заранее (зафиксированы до запуска):

1. Живость исхода всегда определяется по alive (≥ DEAD_ALIVE = 0.05), а не
   по метке класса. Расхождение помечается флагом `class_alive_conflict`.
2. «Класс восстановлен» для (модель, условие): доля повторов, у которых
   финальный класс совпал с домашним классом модели И поле живо.
   «Порог» — не менее SIGN_MIN = 11 из 12 повторов (односторонний знаковый
   тест, p ≤ 0.00049).
3. «Тот же рисунок» (`same_pattern`): бинарный IoU финала с бинарной маской
   прототипа ≥ IOU_MIN = 0.5.
4. «Та же фаза» (`same_phase`): IoU ≥ 0.5 после сдвига финала на любые
   смещения в диапазоне ±SHIFT_MAX пикселей. Отделяет «тот же рисунок, но
   сдвинутый» от «другого рисунка».
5. «Та же ориентация» (`same_orientation`): IoU ≥ 0.5 после поворота и
   отражения финала (группа диэдра D4, 8 преобразований). Отделяет «тот же
   рисунок в другой ориентации» от «другого рисунка».
6. Интерпретация (описательная, не критерий):
   - `visible_zeroed` восстанавливает тот же рисунок → видимая текстура НЕ
     нужна, значит память формы лежит в скрытом состоянии;
   - `hidden_zeroed` восстанавливает тот же рисунок → скрытое состояние НЕ
     нужно, значит форма выводится заново по видимой текстуре;
   - `hidden_shuffled` ломается там, где `none` держится → важна
     пространственная укладка скрытого состояния, а не только его наличие.
7. Контроль `none` обязан оставаться в домашнем классе: если прототип сам
   по себе распадается, все остальные условия неинтерпретируемы.

Модели: R-9 seed42 (struct_2, выученная форма), R-9 seed101 (struct_1,
та же форма, что и у необученной архитектуры) и необученная архитектура
(контроль «generic»). 4 условия × 12 повторов × 3 модели = 144 развёртки.

Ни обучения, ни H1–H4 здесь нет: только измерения по уже обученным моделям.
Строки пишутся инкрементально в JSONL, чтобы прерванный прогон не терялся.
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
OUT = EXP / "channel_memory_exploratory.json"
ROWS = EXP / "channel_memory_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
REPEATS = 12
DEAD_ALIVE = 0.05
SIGN_MIN = 11
IOU_MIN = 0.5
SHIFT_MAX = 4
VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL
HIDDEN = [c for c in range(config.N_CHANNELS) if c not in (VIS, ALIV)]

# модель, сид прототипа, ожидаемый класс, ОБУЧЕНА ЛИ (True), индекс для сидов
MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("WP4_R-9_s2000_seed101", 5, "struct_1", True, 1),
    ("untrained_current_arch", 0, "struct_1", False, 2),
]
CONDITIONS = ["none", "visible_zeroed", "hidden_zeroed", "hidden_shuffled"]

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


def shift_iou(a, b, max_shift):
    """Лучший IoU по целочисленным сдвигам a относительно b (±max_shift)."""
    best = 0.0
    h, w = b.shape
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            shifted = np.zeros_like(b)
            ys0, ys1 = max(0, dy), min(h, h + dy)
            xs0, xs1 = max(0, dx), min(w, w + dx)
            sy0, sy1 = max(0, -dy), min(h, h - dy)
            sx0, sx1 = max(0, -dx), min(w, w - dx)
            shifted[ys0:ys1, xs0:xs1] = a[sy0:sy1, sx0:sx1]
            best = max(best, iou(shifted, b))
    return best


def dihedral_masks(a):
    """8 преобразований группы D4: 4 поворота × (с отражением и без)."""
    out = []
    cur = a
    for _ in range(4):
        out.append(cur)
        out.append(np.fliplr(cur))
        cur = np.rot90(cur)
    return out


def dihedral_iou(a, b):
    return max(iou(m, b) for m in dihedral_masks(a))


def build_prototype(family, proto_seed, is_trained):
    """Прототип: финальное состояние своей модели (для контроля — untrained)."""
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


def apply_condition(state, condition, rng):
    """Нанести повреждение по каналам. alive-канал (1) не трогаем никогда."""
    out = state.clone()
    if condition == "none":
        return out
    if condition == "visible_zeroed":
        out[:, VIS] = 0.0
        return out
    if condition == "hidden_zeroed":
        for c in HIDDEN:
            out[:, c] = 0.0
        return out
    if condition == "hidden_shuffled":
        for c in HIDDEN:
            arr = out[0, c].detach().cpu().numpy()
            perm = rng.permutation(arr.size)
            shuffled = arr.reshape(-1)[perm].reshape(arr.shape)
            out[0, c] = torch.from_numpy(shuffled).to(
                device=out.device, dtype=out.dtype
            )
        return out
    raise ValueError(f"неизвестное условие {condition}")


def run_one(model, proto_stress, proto_binary, host, p_seed):
    """Одна развёртка: класс, живость, IoU (прямой, со сдвигом, с поворотом)."""
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    snap_class = []
    snap_alive = []
    for step in range(1, STEPS + 1):
        with torch.no_grad():
            state = model(state)
        if step % EVERY == 0 or step == STEPS:
            d, cid = classify(state)
            snap_class.append(names.get(cid, "outlier"))
            snap_alive.append(float(d["alive_fraction"]))
    d, cid = classify(state)
    final_class = names.get(cid, "outlier")
    fin_bin = binary_of(state)
    iou_exact = iou(fin_bin, proto_binary)
    return {
        "final_class": final_class,
        "final_cluster": int(cid),
        "final_alive": float(d["alive_fraction"]),
        "final_binary": float(d["binary_fraction"]),
        "alive_cells": int(round(float(d["alive_fraction"]) * 4096)),
        "iou_exact": iou_exact,
        "iou_shifted": shift_iou(fin_bin, proto_binary, SHIFT_MAX),
        "iou_dihedral": dihedral_iou(fin_bin, proto_binary),
        "class_alive_conflict": bool(
            (d["alive_fraction"] < DEAD_ALIVE and final_class in {"struct_1", "struct_2"})
            or (d["alive_fraction"] >= DEAD_ALIVE and final_class == "death")
        ),
        "snap_class": snap_class,
        "snap_alive": snap_alive,
    }


if ROWS.exists():
    with open(ROWS, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    print(f"[chan] возобновление: {len(rows)} строк уже посчитано", flush=True)
else:
    rows = []
done = {(r["model"], r["condition"], int(r["repeat"])) for r in rows}
fh = open(ROWS, "a", encoding="utf-8")

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_channel_memory",
    "note": (
        "где живёт форма: видимая текстура или скрытые каналы; "
        "4 условия × 12 повторов × 3 модели = 144 развёртки; "
        "не H1–H4 и не обучение"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "repeats": REPEATS,
    "conditions": CONDITIONS,
    "channels": {
        "visible": VIS,
        "alive": ALIV,
        "hidden": HIDDEN,
        "stress": config.STRESS_CHANNEL,
    },
    "rules": {
        "alive_rule": f"исход жив, если alive >= {DEAD_ALIVE}; метка класса не определяет живость",
        "class_recovered": f">= {SIGN_MIN} из {REPEATS} повторов: домашний класс и поле живо",
        "same_pattern": f"бинарный IoU с прототипом >= {IOU_MIN}",
        "same_phase": (
            f"бинарный IoU >= {IOU_MIN} при сдвиге до ±{SHIFT_MAX} пикселей"
        ),
        "same_orientation": (
            f"бинарный IoU >= {IOU_MIN} при повороте/отражении (группа D4)"
        ),
        "alive_channel_kept": (
            "канал 1 (alive) не обнуляется никогда: alive считается из него, "
            "иначе тест был бы тривиальным"
        ),
    },
    "models": [],
    "rows": rows,
}

for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, final_state = build_prototype(family, proto_seed, is_trained)
    try:
        _proto_desc, proto_cid = classify(final_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_binary = binary_of(final_state)
        proto_alive = e02b._state_arrays(final_state)[0]
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[chan] {family} прототип seed={proto_seed} -> {proto_class} "
            f"(ожидался {expected_class}) alive={int(proto_alive.sum())} "
            f"binary={proto_binary.mean():.3f}",
            flush=True,
        )
        model_block = {
            "family": family,
            "prototype_seed": int(proto_seed),
            "prototype_class": proto_class,
            "expected_class": expected_class,
            "class_matches_expected": bool(proto_class == expected_class),
            "prototype_alive_cells": int(proto_alive.sum()),
            "prototype_binary_fraction": float(proto_binary.mean()),
            "conditions": [],
        }

        for condition in CONDITIONS:
            cell_rows = []
            for rep in range(REPEATS):
                key = (family, condition, rep)
                if key in done:
                    cell_rows.append(
                        next(
                            r
                            for r in rows
                            if (
                                r["model"],
                                r["condition"],
                                int(r["repeat"]),
                            ) == key
                        )
                    )
                    continue
                p_seed = 830000 + model_idx * 10000 + rep
                rng = np.random.default_rng(840000 + model_idx * 10000 + rep)
                host = apply_condition(final_state, condition, rng)
                res = run_one(model, proto_stress, proto_binary, host, p_seed)
                row = {
                    "model": family,
                    "condition": condition,
                    "repeat": int(rep),
                    "generator_seed": int(p_seed),
                    "home_class": proto_class,
                    **res,
                }
                rows.append(row)
                cell_rows.append(row)
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
            n = len(cell_rows)
            alive_n = sum(1 for r in cell_rows if r["final_alive"] >= DEAD_ALIVE)
            class_n = sum(
                1
                for r in cell_rows
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == proto_class
            )
            pattern_n = sum(
                1
                for r in cell_rows
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == proto_class
                and r["iou_exact"] >= IOU_MIN
            )
            phase_n = sum(
                1
                for r in cell_rows
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == proto_class
                and r["iou_shifted"] >= IOU_MIN
            )
            orient_n = sum(
                1
                for r in cell_rows
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == proto_class
                and r["iou_dihedral"] >= IOU_MIN
            )
            ious = sorted(r["iou_exact"] for r in cell_rows)
            mid = len(ious) // 2
            median_iou = (
                float(ious[mid])
                if len(ious) % 2
                else 0.5 * (float(ious[mid - 1]) + float(ious[mid]))
            )
            model_block["conditions"].append({
                "condition": condition,
                "n": n,
                "alive_n": alive_n,
                "class_recovered_n": class_n,
                "same_pattern_n": pattern_n,
                "same_phase_n": phase_n,
                "same_orientation_n": orient_n,
                "class_recovered_established": bool(class_n >= SIGN_MIN),
                "same_pattern_established": bool(pattern_n >= SIGN_MIN),
                "same_phase_established": bool(phase_n >= SIGN_MIN),
                "same_orientation_established": bool(orient_n >= SIGN_MIN),
                "median_iou_exact": median_iou,
                "class_counts": dict(Counter(r["final_class"] for r in cell_rows)),
                "conflicts": sum(1 for r in cell_rows if r["class_alive_conflict"]),
            })
            print(
                f"[chan] {family}/{condition}: класс {class_n}/{n}, "
                f"тот же рисунок {pattern_n}/{n}, та же фаза {phase_n}/{n}, "
                f"та же ориентация {orient_n}/{n}",
                flush=True,
            )

        by_cond = {c["condition"]: c for c in model_block["conditions"]}
        control_ok = by_cond["none"]["class_recovered_established"]
        model_block["control_ok"] = bool(control_ok)
        model_block["visible_zeroed_recovers"] = bool(
            by_cond["visible_zeroed"]["same_pattern_established"]
        )
        model_block["hidden_zeroed_recovers"] = bool(
            by_cond["hidden_zeroed"]["same_pattern_established"]
        )
        model_block["hidden_shuffled_recovers"] = bool(
            by_cond["hidden_shuffled"]["same_pattern_established"]
        )
        model_block["memory_in_hidden_channels"] = bool(
            by_cond["visible_zeroed"]["same_pattern_established"]
            and not by_cond["hidden_zeroed"]["same_pattern_established"]
        )
        model_block["rederivable_from_visible"] = bool(
            by_cond["hidden_zeroed"]["same_pattern_established"]
        )
        model_block["hidden_layout_matters"] = bool(
            by_cond["none"]["same_pattern_established"]
            and not by_cond["hidden_shuffled"]["same_pattern_established"]
        )
        result["models"].append(model_block)
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

result["summary"] = {
    "n_rows": len(rows),
    "models": {
        m["family"]: {
            "prototype_class": m["prototype_class"],
            "class_matches_expected": m["class_matches_expected"],
            "control_ok": m["control_ok"],
            "visible_zeroed_recovers": m["visible_zeroed_recovers"],
            "hidden_zeroed_recovers": m["hidden_zeroed_recovers"],
            "hidden_shuffled_recovers": m["hidden_shuffled_recovers"],
            "memory_in_hidden_channels": m["memory_in_hidden_channels"],
            "rederivable_from_visible": m["rederivable_from_visible"],
            "hidden_layout_matters": m["hidden_layout_matters"],
            "by_condition": {
                c["condition"]: {
                    "class_recovered_n": c["class_recovered_n"],
                    "same_pattern_n": c["same_pattern_n"],
                    "same_phase_n": c["same_phase_n"],
                    "same_orientation_n": c["same_orientation_n"],
                    "median_iou_exact": c["median_iou_exact"],
                    "class_counts": c["class_counts"],
                }
                for c in m["conditions"]
            },
        }
        for m in result["models"]
    },
    "same_pattern_cells_established": sum(
        1
        for m in result["models"]
        for c in m["conditions"]
        if c["same_pattern_established"]
    ),
    "total_cells": sum(len(m["conditions"]) for m in result["models"]),
}

OUT.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
fh.close()
print(f"[chan] записан {OUT}", flush=True)
