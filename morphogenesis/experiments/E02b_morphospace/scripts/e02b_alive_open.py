"""E02b alive-open: несёт ли тело форму, или тело — только гейт живости.

Протокол зафиксирован до запуска: `reports/2026-10-22-alive-open-plan.md`.
Здесь только исполнение.

Условия (по 12 повторов, 2000 шагов, 2 модели):
    none        — прототип не тронут (контроль самовоспроизводимости рисунка)
    alive_open  — канал alive = +8.0 во всех клетках (sigmoid(8) > 0.5),
                  видимый и скрытые каналы не тронуты

Метрики: body_iou (маска финала против маски прототипа), texture_iou
(visible > 0.5), класс по замороженным центроидам, alive_fraction.

Критерий: контроль none обязан держать рисунок (>= 11/12), иначе модель
исключается; при alive_open body_iou < 0.5 в >= 11/12 → тело несёт геометрию
(H-CH-6 подтверждена), >= 0.5 → тело выводится заново (опровергнута).
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
OUT = EXP / "alive_open_exploratory.json"
ROWS = EXP / "alive_open_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
REPEATS = 12
DEAD_ALIVE = 0.05
IOU_MIN = 0.5
SIGN_MIN = 11
ALIVE_OPEN_VALUE = 8.0

VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL

MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("untrained_current_arch", 0, "struct_1", False, 1),
]
CONDITIONS = ["none", "alive_open"]

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


def arrays(state):
    """alive, binary, visible — те же массивы, что в e02b._state_arrays."""
    alive, binary, visible, _b0, _b1 = e02b._state_arrays(state)
    return np.asarray(alive), np.asarray(binary), np.asarray(visible)


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


def build_prototype(family, proto_seed, is_trained):
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
        final, _p, _t, _e = e02b.rollout(model, start, STEPS, EVERY)
        return model, final
    final, model, _run = e02b._prototype_state(spec, proto_seed, STEPS, EVERY, DEVICE)
    return model, final


def apply_condition(proto_state, condition):
    out = proto_state.clone()
    if condition == "none":
        return out
    if condition == "alive_open":
        out[:, ALIV] = ALIVE_OPEN_VALUE
        return out
    raise ValueError(condition)


def run_rollout(model, proto_stress, host, p_seed):
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    for _ in range(STEPS):
        with torch.no_grad():
            state = model(state)
    desc, cid = classify(state)
    alive, binary, visible = arrays(state)
    return desc, cid, alive, binary, visible


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_alive_open",
    "protocol": "reports/2026-10-22-alive-open-plan.md",
    "note": (
        "alive_open: канал живости открыт во всех клетках (+8.0), visible и "
        "hidden не тронуты; вопрос — вернётся ли тело. Контроль none."
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "repeats": REPEATS,
    "rules": {
        "same_pattern": f"IoU >= {IOU_MIN}",
        "significance": f">= {SIGN_MIN} из {REPEATS}",
        "alive": f"alive_fraction >= {DEAD_ALIVE}",
        "criterion": (
            "H-CH-6 подтверждена, если при alive_open body_iou < 0.5 в >= 11/12 "
            "у struct_2 и контроль none держит тело (>= 11/12)"
        ),
    },
    "models": [],
}

for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, proto_state = build_prototype(family, proto_seed, is_trained)
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_alive, proto_binary, proto_visible = arrays(proto_state)
        proto_visible_mask = proto_visible > 0.5
        proto_stress = model.stress_ema.detach().clone()
        entry = {
            "family": family,
            "proto_seed": proto_seed,
            "expected_class": expected_class,
            "proto_class": proto_class,
            "proto_alive_fraction": round(float(proto_alive.mean()), 4),
            "proto_body_pixels": int(np.asarray(proto_binary).sum()),
            "conditions": {},
        }
        print(
            f"[alive-open] {family}: прототип {proto_class} (ожидался {expected_class}), "
            f"тело {entry['proto_body_pixels']} клеток",
            flush=True,
        )
        for cond_idx, cond in enumerate(CONDITIONS):
            rows = []
            for rep in range(REPEATS):
                host = apply_condition(proto_state, cond)
                p_seed = 700000 + model_idx * 10000 + cond_idx * 100 + rep
                desc, cid, alive, binary, visible = run_rollout(
                    model, proto_stress, host, p_seed
                )
                row = {
                    "section": "alive_open",
                    "family": family,
                    "condition": cond,
                    "rep": rep,
                    "p_seed": p_seed,
                    "final_class": names.get(cid, "outlier"),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "body_iou": iou(binary, proto_binary),
                    "texture_iou": iou(visible > 0.5, proto_visible_mask),
                }
                row["body_returned"] = bool(row["body_iou"] >= IOU_MIN)
                row["texture_returned"] = bool(row["texture_iou"] >= IOU_MIN)
                row["class_alive_conflict"] = bool(
                    row["final_class"] == "struct_2" and row["alive_fraction"] < DEAD_ALIVE
                )
                emit(row)
                rows.append(row)
            entry["conditions"][cond] = {
                "n": len(rows),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "texture_returned": sum(1 for r in rows if r["texture_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
                "mean_texture_iou": round(
                    float(np.mean([r["texture_iou"] for r in rows])), 4
                ),
                "class_alive_conflicts": sum(1 for r in rows if r["class_alive_conflict"]),
            }
            st = entry["conditions"][cond]
            print(
                f"[alive-open] {family} {cond:10s} тело {st['body_returned']}/{REPEATS} "
                f"(IoU {st['mean_body_iou']:.3f}), текстура {st['texture_returned']}/{REPEATS} "
                f"(IoU {st['mean_texture_iou']:.3f}), классы {st['classes']}",
                flush=True,
            )
        result["models"].append(entry)
    finally:
        del model

# --- вердикт по протоколу -----------------------------------------------------
struct2 = next(
    (m for m in result["models"] if m["family"] == "WP4_R-9_s2000_seed42"), None
)
verdict = {"applicable": False, "reason": "нет модели struct_2"}
if struct2:
    none_st = struct2["conditions"]["none"]
    open_st = struct2["conditions"]["alive_open"]
    gate_ok = none_st["body_returned"] >= SIGN_MIN
    if not gate_ok:
        verdict = {
            "applicable": False,
            "reason": f"контроль none держит тело {none_st['body_returned']}/{REPEATS} — интерпретация выключена",
        }
    elif open_st["body_returned"] >= SIGN_MIN:
        verdict = {
            "applicable": True,
            "verdict": "refuted_body_rederived",
            "reason": (
                f"при alive_open тело возвращается {open_st['body_returned']}/{REPEATS} — "
                "геометрия тела не является отдельной памятью"
            ),
        }
    elif (REPEATS - open_st["body_returned"]) >= SIGN_MIN:
        verdict = {
            "applicable": True,
            "verdict": "confirmed_body_carries_geometry",
            "reason": (
                f"при alive_open тело возвращается лишь {open_st['body_returned']}/{REPEATS} — "
                "открытый гейт не восстанавливает исходное тело"
            ),
        }
    else:
        verdict = {
            "applicable": True,
            "verdict": "inconclusive",
            "reason": (
                f"промежуточный результат: тело вернулось {open_st['body_returned']}/{REPEATS}"
            ),
        }
result["verdict"] = verdict
result["finished_at"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[alive-open] вердикт: {verdict}", flush=True)
print(f"[alive-open] записан {OUT}", flush=True)
