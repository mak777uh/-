"""E02b, exploratory: геометрическая абляция struct_2.

Половина поля (лево/право/верх/низ) и центральные квадраты 16/32.
Вопрос: если большая часть глобального рисунка сохранена, возвращается ли
исходная фаза (IoU с прототипом), или система выбирает другую доменную текстуру?
18 прогонов (6 повреждений × 3 повтора), 2000 шагов, срезы 500/1000/2000.
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
OUT = EXP / "geometric_lesion_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
CHECK = [500, 1000, 2000]
SIZE = 64
FAMILY = "WP4_R-9_s2000_seed42"
SEED = 35
REPEATS = 3

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
spec = e02b.load_checkpoint_specs(families=[FAMILY])[0]


def binary_of(state):
    return e02b._state_arrays(state)[1]


def classify(state):
    d = e02b.describe_state(state)
    a = int(e02b.assign_to_clusters(e02b.descriptor_vector(d).reshape(1, -1), mean, std, centroids, valid)[0])
    return d, a


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
    elif name == "corner_16":
        out[:, :, :16, :16] = 0.0
    else:
        raise ValueError(name)
    return out


LESIONS = ["cut_left", "cut_right", "cut_top", "cut_bottom", "center_16", "center_32"]

final_state, model, _ = e02b._prototype_state(spec, SEED, 2000, 50, DEVICE)
proto_stress = model.stress_ema.detach().clone()
proto_binary = binary_of(final_state)
result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_geometric_lesion",
    "note": "struct_2, R-9 seed42, прототип s35; 6 повреждений × 3 повтора, 2000 шагов",
    "check_steps": CHECK,
    "device": str(DEVICE),
    "rows": [],
}
for li, name in enumerate(LESIONS):
    for rep in range(REPEATS):
        host = lesion(name, final_state)
        p_seed = 90000 + li * 100 + rep
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
        result["rows"].append({
            "lesion": name,
            "repeat": rep,
            "generator_seed": int(p_seed),
            "initial_alive": float(e02b._state_arrays(host)[0].mean()),
            "initial_binary": float(e02b._state_arrays(host)[1].mean()),
            "points": points,
            "final": points[-1],
        })
        print(f"[lesion] {name} rep={rep} -> {points[-1]['assigned_class']} IoU={points[-1]['iou']:.3f}", flush=True)
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[lesion] written {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB)", flush=True)
