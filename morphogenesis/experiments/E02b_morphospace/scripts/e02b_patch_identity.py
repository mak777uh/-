"""E02b, exploratory: восстанавливает ли малый патч глобальный рисунок?

Продолжение patch_transplant_exploratory.json: там класс совпадал, но не
проверялась побитовая/геометрическая идентичность. Здесь для патчей 8/16/32
(индекс 0) сравниваем финал с прототипом: IoU, agreement, профиль строк,
положение светлой полосы struct_2. Фигуры — prototype/final/XOR.
"""
import json
import os
import sys
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
OUT = EXP / "patch_identity_exploratory.json"
FIGDIR = REPO / "reports" / "figures"
DEVICE = e02b._device_from_arg("auto")
STEPS = 500
EVERY = 25
SIZES = [8, 16, 32]
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


def arrays(state):
    alive, binary, _v, _s, _a = e02b._state_arrays(state)
    return alive, binary


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


def low_rows(binary, frac=0.05):
    profile = binary.mean(axis=1)
    rows = np.nonzero(profile < frac)[0]
    return {
        "min_row": int(np.argmin(profile)),
        "min_value": float(profile.min()),
        "n_low_rows": int(len(rows)),
        "low_rows": [int(x) for x in rows],
    }


def compare(final_binary, proto_binary):
    inter = np.logical_and(final_binary, proto_binary).sum()
    union = np.logical_or(final_binary, proto_binary).sum()
    return {
        "iou": float(inter / union) if union else 1.0,
        "agreement": float((final_binary == proto_binary).mean()),
        "final_low": low_rows(final_binary),
        "proto_low": low_rows(proto_binary),
        "row_profile_corr": float(np.corrcoef(final_binary.mean(axis=1), proto_binary.mean(axis=1))[0, 1])
        if final_binary.std() and proto_binary.std() else None,
        "final_binary_fraction": float(final_binary.mean()),
        "proto_binary_fraction": float(proto_binary.mean()),
    }


def save_compare_figure(proto_binary, final_binary, title, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    axes[0].imshow(proto_binary, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("prototype")
    axes[1].imshow(final_binary, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("regrown from patch")
    axes[2].imshow(proto_binary ^ final_binary, cmap="magma", vmin=0, vmax=1)
    axes[2].set_title("XOR")
    for ax in axes:
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_patch_identity",
    "note": "патч index=0; 500 шагов; сравнение с прототипом по бинарной маске",
    "steps": STEPS,
    "sizes": SIZES,
    "device": str(DEVICE),
    "rows": [],
    "figures": [],
}

for class_name, proto in PROTO.items():
    spec = specs[proto["family"]]
    final_state, model, _repro = e02b._prototype_state(spec, int(proto["seed"]), 2000, 50, DEVICE)
    proto_stress = model.stress_ema.detach().clone()
    proto_alive, proto_binary = arrays(final_state)
    centers = choose_centers(proto_binary, max(SIZES), 5)
    cy, cx = centers[0]
    for size in SIZES:
        top = cy - size // 2
        left = cx - size // 2
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
        final, points, traj, elapsed = e02b.rollout(model, host, STEPS, EVERY)
        desc = e02b.describe_state(final)
        assigned = int(e02b.assign_to_clusters(e02b.descriptor_vector(desc).reshape(1, -1), mean, std, centroids, valid)[0])
        final_alive, final_binary = arrays(final)
        cmp = compare(final_binary, proto_binary)
        title = f"{class_name}: patch {size}px -> {name_by_label.get(assigned, 'outlier')} ({STEPS} steps)"
        fig_path = os.path.join(FIGDIR, f"e02b_patch_identity_{class_name}_s{size}.png")
        save_compare_figure(proto_binary, final_binary, title, fig_path)
        row = {
            "class": class_name,
            "size": int(size),
            "center": [int(cy), int(cx)],
            "patch_top_left": [int(top), int(left)],
            "generator_seed": int(p_seed),
            "assigned_class": name_by_label.get(assigned, "outlier"),
            "descriptor": desc,
            "compare": cmp,
            "final_alive_fraction": float(final_alive.mean()),
            "figure": fig_path,
            "wall_seconds": float(elapsed),
        }
        result["rows"].append(row)
        result["figures"].append(fig_path)
        print(
            f"[identity] {class_name} s={size} -> {row['assigned_class']} "
            f"IoU={cmp['iou']:.3f} agree={cmp['agreement']:.3f} "
            f"band={cmp['final_low']['low_rows']} proto_band={cmp['proto_low']['low_rows']}",
            flush=True,
        )
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[identity] written {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB)", flush=True)
