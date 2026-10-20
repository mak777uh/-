"""E02b, exploratory: растёт ли малый патч структуры в мёртвом поле?

Почему: в perturbations.json «transplant» копировал bbox патча, а bbox обоих
структурных классов — всё поле 64×64. Тест не отвечал на вопрос о росте из
фрагмента. Здесь патчи 8×8 / 16×16 / 32×32 из финального состояния прототипа
помещаются в нулевое поле; 500 шагов, 5 детерминированных позиций на размер.

Это exploratory-проверка, не H3 и не новая предзарегистрированная гипотеза.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
MORPH = HERE.parents[3]
REPO = HERE.parents[4]
sys.path.insert(0, str(MORPH))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "patch_transplant_exploratory.json"
FIGDIR = REPO / "reports" / "figures"
DEVICE = e02b._device_from_arg("auto")
STEPS = 500
EVERY = 25
SIZES = [8, 16, 32]
N_PATCHES = 5
PROTO = {
    "struct_1": {"family": "WP4_R-9_s2000_seed101", "seed": 5, "cluster": 1},
    "struct_2": {"family": "WP4_R-9_s2000_seed42", "seed": 35, "cluster": 5},
}

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
name_by_label = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}

specs = {s.family: s for s in e02b.load_checkpoint_specs(families=[p["family"] for p in PROTO.values()])}
rng = np.random.default_rng(20261021)


def classify(state):
    d = e02b.describe_state(state)
    a = int(e02b.assign_to_clusters(e02b.descriptor_vector(d).reshape(1, -1), mean, std, centroids, valid)[0])
    return d, a


def patch_metrics(state, top, left, size):
    alive, binary, _visible, _stress, _alpha = e02b._state_arrays(state)
    h, w = binary.shape
    mask = np.zeros((h, w), dtype=bool)
    mask[top:top + size, left:left + size] = True
    outside = ~mask
    patch_cells = float(mask.sum())
    outside_cells = float(outside.sum())
    return {
        "patch_alive_fraction": float(alive[mask].mean()) if patch_cells else 0.0,
        "patch_binary_fraction": float(binary[mask].mean()) if patch_cells else 0.0,
        "alive_outside_patch": float(alive[outside].sum() / outside_cells) if outside_cells else 0.0,
        "binary_outside_patch": float(binary[outside].sum() / outside_cells) if outside_cells else 0.0,
        "n_binary_outside_patch": int(binary[outside].sum()),
    }


def choose_centers(binary, size, n):
    h, w = binary.shape
    half = size // 2
    ys, xs = np.nonzero(binary)
    ok = (ys >= half) & (ys < h - half) & (xs >= half) & (xs < w - half)
    ys, xs = ys[ok], xs[ok]
    if len(ys) == 0:
        ys = np.array([h // 2])
        xs = np.array([w // 2])
    idx = rng.choice(len(ys), size=min(n, len(ys)), replace=False)
    return [(int(ys[i]), int(xs[i])) for i in idx]


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_patch_transplant",
    "note": "малые патчи 8/16/32 в нулевое поле; не H3, не переписывает протокол",
    "steps": STEPS,
    "every": EVERY,
    "sizes": SIZES,
    "device": str(DEVICE),
    "runs": [],
    "controls": [],
    "figures": [],
}

for class_name, proto in PROTO.items():
    spec = specs[proto["family"]]
    print(f"[patch] {class_name}: воспроизвожу прототип {proto['family']} seed={proto['seed']}", flush=True)
    final_state, model, repro = e02b._prototype_state(
        spec, int(proto["seed"]), 2000, 50, DEVICE
    )
    proto_stress = model.stress_ema.detach().clone()
    alive, binary, _v, _s, _a = e02b._state_arrays(final_state)
    print(
        f"[patch] {class_name}: alive={alive.mean():.3f} binary={binary.mean():.3f} "
        f"b0={e02b.count_connected_components(binary)} b1={e02b.count_holes(binary)}",
        flush=True,
    )
    # Один общий набор центров (по самому большому патчу), вложенные размеры.
    centers = choose_centers(binary, max(SIZES), N_PATCHES)
    for size in SIZES:
        for k, (cy, cx) in enumerate(centers):
            top = cy - size // 2
            left = cx - size // 2
            patch = final_state[:, :, top:top + size, left:left + size].clone()
            host = torch.zeros_like(final_state)
            host[:, :, (64 - size) // 2:(64 - size) // 2 + size,
                 (64 - size) // 2:(64 - size) // 2 + size] = patch
            p_seed = 70000 + int(proto["seed"]) * 100 + size * 10 + k
            gen = config.create_deterministic_generator(p_seed)
            model.set_generator(gen)
            model.stress_ema.copy_(proto_stress)
            model._noise_cache = {}
            model._noise_seq = 0
            model.begin_segment()
            m0 = patch_metrics(host, (64 - size) // 2, (64 - size) // 2, size)
            f, points, traj, elapsed = e02b.rollout(model, host, STEPS, EVERY)
            desc, assigned = classify(f)
            labels = e02b.assign_to_clusters(traj, mean, std, centroids, valid)
            first = next((p["step"] for p, c in zip(points, labels, strict=True) if int(c) == int(proto["cluster"])), None)
            m1 = patch_metrics(f, (64 - size) // 2, (64 - size) // 2, size)
            result["runs"].append({
                "class": class_name,
                "family": proto["family"],
                "prototype_seed": int(proto["seed"]),
                "size": int(size),
                "patch_index": int(k),
                "center": [int(cy), int(cx)],
                "generator_seed": int(p_seed),
                "proto_reproduced": bool(repro.get("reproduced")),
                "initial": m0,
                "final": desc,
                "final_metrics": m1,
                "assigned_cluster": int(assigned),
                "assigned_class": name_by_label.get(assigned, "outlier"),
                "returned_same_class": bool(assigned == int(proto["cluster"])),
                "return_step": first,
                "trajectory": points,
                "wall_seconds": float(elapsed),
            })
            print(
                f"[patch] {class_name} s={size} k={k} -> {name_by_label.get(assigned, 'outlier')} "
                f"same={assigned == int(proto['cluster'])} alive={desc['alive_fraction']:.3f} "
                f"bin={desc['binary_fraction']:.3f} out_bin={m1['binary_outside_patch']:.3f}",
                flush=True,
            )
    # Референс: весь финал в мёртвое поле (эквивалент вырожденной пересадки).
    p_seed = 79000 + int(proto["seed"])
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    f, points, traj, elapsed = e02b.rollout(model, final_state.clone(), STEPS, EVERY)
    desc, assigned = classify(f)
    result["controls"].append({
        "kind": "full_state",
        "class": class_name,
        "assigned_cluster": int(assigned),
        "assigned_class": name_by_label.get(assigned, "outlier"),
        "returned_same_class": bool(assigned == int(proto["cluster"])),
        "final": desc,
        "wall_seconds": float(elapsed),
    })
    result.setdefault("class_summary", {})[class_name] = {
        "n": sum(1 for r in result["runs"] if r["class"] == class_name),
        "proto_alive": float(alive.mean()),
        "proto_binary": float(binary.mean()),
        "centers": [[int(y), int(x)] for y, x in centers],
    }
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

# Контроль: нулевой патч 16×16 в нулевом поле и пустое поле.
for name, size in (("zero_patch", 16), ("empty_field", 0)):
    host = torch.zeros(1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=DEVICE)
    model, _ = e02b.build_model(specs[PROTO["struct_1"]["family"]], DEVICE)
    gen = config.create_deterministic_generator(80000 + size)
    model.set_generator(gen)
    model.stress_ema.zero_()
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    f, points, traj, elapsed = e02b.rollout(model, host, STEPS, EVERY)
    desc, assigned = classify(f)
    result["controls"].append({
        "kind": name,
        "size": int(size),
        "assigned_cluster": int(assigned),
        "assigned_class": name_by_label.get(assigned, "outlier"),
        "final": desc,
        "wall_seconds": float(elapsed),
    })
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

# Сводка по размерам и классам.
summary = {}
for class_name in PROTO:
    for size in SIZES:
        rows = [r for r in result["runs"] if r["class"] == class_name and r["size"] == size]
        summary[f"{class_name}_s{size}"] = {
            "n": len(rows),
            "same_class": sum(r["returned_same_class"] for r in rows),
            "alive_med": float(np.median([r["final"]["alive_fraction"] for r in rows])),
            "binary_med": float(np.median([r["final"]["binary_fraction"] for r in rows])),
            "outside_binary_med": float(np.median([r["final_metrics"]["binary_outside_patch"] for r in rows])),
            "outside_binary_max": float(max(r["final_metrics"]["binary_outside_patch"] for r in rows)),
            "return_step_med": (
                float(np.median([r["return_step"] for r in rows if r["return_step"] is not None]))
                if any(r["return_step"] is not None for r in rows) else None
            ),
        }
result["summary"] = summary

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[patch] written {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB)", flush=True)
print(json.dumps(summary, ensure_ascii=False, indent=1), flush=True)
