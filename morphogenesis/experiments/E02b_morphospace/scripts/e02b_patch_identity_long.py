"""E02b, exploratory: сходятся ли патчи к глобальному рисунку к 2000 шагам?

Патч 8/16/32 (index 0) в мёртвом поле; IoU с прототипом на 500/1000/2000.
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
OUT = EXP / "patch_identity_long_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
SIZES = [8, 16, 32]
CHECK = [500, 1000, 2000]
PROTO = {
    "struct_1": {"family": "WP4_R-9_s2000_seed101", "seed": 5, "cluster": 1},
    "struct_2": {"family": "WP4_R-9_s2000_seed42", "seed": 35, "cluster": 5},
}
census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
specs = {s.family: s for s in e02b.load_checkpoint_specs(families=[p["family"] for p in PROTO.values()])}
rng = np.random.default_rng(20261021)


def binary_of(state):
    return e02b._state_arrays(state)[1]


def choose_centers(binary, size, n):
    h, w = binary.shape
    half = size // 2
    ys, xs = np.nonzero(binary)
    ok = (ys >= half) & (ys < h - half) & (xs >= half) & (xs < w - half)
    ys, xs = ys[ok], xs[ok]
    idx = rng.choice(len(ys), size=min(n, len(ys)), replace=False)
    return [(int(ys[i]), int(xs[i])) for i in idx]


def iou(a, b):
    u = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / u) if u else 1.0


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_patch_identity_long",
    "note": "patch index 0; IoU с прототипом на 500/1000/2000 шагах",
    "check_steps": CHECK,
    "device": str(DEVICE),
    "rows": [],
}
for class_name, proto in PROTO.items():
    spec = specs[proto["family"]]
    final_state, model, _ = e02b._prototype_state(spec, int(proto["seed"]), 2000, 50, DEVICE)
    proto_stress = model.stress_ema.detach().clone()
    proto_binary = binary_of(final_state)
    centers = choose_centers(proto_binary, max(SIZES), 5)
    cy, cx = centers[0]
    for size in SIZES:
        top, left = cy - size // 2, cx - size // 2
        patch = final_state[:, :, top:top + size, left:left + size].clone()
        host = torch.zeros_like(final_state)
        host[:, :, (64 - size) // 2:(64 - size) // 2 + size,
             (64 - size) // 2:(64 - size) // 2 + size] = patch
        p_seed = 70000 + int(proto["seed"]) * 100 + size * 10 + 0
        gen = config.create_deterministic_generator(p_seed)
        model.set_generator(gen)
        model.stress_ema.copy_(proto_stress)
        model._noise_cache = {}
        model._noise_seq = 0
        model.begin_segment()
        state = host
        points = []
        for step in range(1, 2001):
            with torch.no_grad():
                state = model(state)
            if step in CHECK:
                b = binary_of(state)
                points.append({"step": step, "iou": iou(b, proto_binary), "binary_fraction": float(b.mean())})
        # Финальная классификация по пересобранным центроидам.
        by_cluster = {int(c): [] for c in valid}
        for r in census["runs"]:
            if r.get("is_control"):
                continue
            cid = int(r["cluster"])
            if cid in by_cluster:
                by_cluster[cid].append(e02b.descriptor_vector(r["final"]))
        cent = np.vstack([np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid])
        cent = (cent - mean) / std
        desc = e02b.describe_state(state)
        assigned = int(e02b.assign_to_clusters(e02b.descriptor_vector(desc).reshape(1, -1), mean, std, cent, valid)[0])
        result["rows"].append({
            "class": class_name,
            "size": int(size),
            "center": [int(cy), int(cx)],
            "generator_seed": int(p_seed),
            "assigned_class": {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}.get(assigned, "outlier"),
            "final": desc,
            "points": points,
        })
        print(f"[long] {class_name} s={size} -> {result['rows'][-1]['assigned_class']} {points}", flush=True)
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[long] written {OUT}", flush=True)
