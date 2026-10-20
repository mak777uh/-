"""E02b, exploratory: восстанавливается ли необученная архитектура после ампутации?

Канонический untrained-контроль в census — одна несидированная инициализация.
Здесь три детерминированные инициализации (init seed 42/43/44): 64 старта × 2000
шагов, проекция на классы census, затем ампутация 20% (все каналы) для трёх
прототипов, попавших в struct_1. Это проверка архитектурного конфаунда, не H3.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
MORPH = HERE.parents[3]
sys.path.insert(0, str(MORPH))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "untrained_recovery_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
INIT_SEEDS = [42, 43, 44]
STARTS = list(range(64))

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
# census.json не сохраняет centroids_z (артефакт пишет только scaler/labels).
# Восстанавливаем центроиды как средние z-векторов членов класса — так же, как
# их считает fit_clusters; контроли в подгонке не участвуют.
by_cluster = {int(c): [] for c in valid}
for r in census["runs"]:
    if r.get("is_control"):
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[cid].append(e02b.descriptor_vector(r["final"]))
centroids = np.vstack(
    [np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid]
)
centroids = (centroids - mean) / std
name_by_label = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
sem_by_label = {int(c): str(s) for c, s in zip(valid, cl["semantic"], strict=True)}

spec = e02b.load_checkpoint_specs(families=["untrained_current_arch"])[0]
print(f"[untrained] device={DEVICE} init_seeds={INIT_SEEDS}", flush=True)

def build_untrained(init_seed):
    torch.manual_seed(int(init_seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(init_seed))
    model, _ = e02b.build_model(spec, DEVICE)
    return model


def run_final(model, seed):
    e02b.prepare_model(model, seed)
    start = e02b.init_state(
        batch_size=1,
        channels=config.N_CHANNELS,
        grid_size=config.GRID_SIZE,
        device=DEVICE,
        generator=model.generator,
    )
    final, points, traj, elapsed = e02b.rollout(model, start, 2000, 50)
    desc = e02b.describe_state(final)
    assigned = int(
        e02b.assign_to_clusters(
            e02b.descriptor_vector(desc).reshape(1, -1), mean, std, centroids, valid
        )[0]
    )
    return final, points, desc, assigned, elapsed


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_untrained_recovery",
    "note": "три сидированные инициализации необученной архитектуры; проверка архитектурного конфаунда struct_1; не H3",
    "init_seeds": INIT_SEEDS,
    "device": str(DEVICE),
    "runs": [],
    "recovery": [],
}
for init_seed in INIT_SEEDS:
    model = build_untrained(init_seed)
    cls = Counter()
    alive = []
    for seed in STARTS:
        final, points, desc, assigned, elapsed = run_final(model, seed)
        cls[name_by_label.get(assigned, "outlier")] += 1
        alive.append(desc["alive_fraction"])
        result["runs"].append(
            {
                "init_seed": int(init_seed),
                "seed": int(seed),
                "assigned_cluster": int(assigned),
                "assigned_class": name_by_label.get(assigned, "outlier"),
                "assigned_semantic": sem_by_label.get(assigned, "outlier"),
                "alive_fraction": float(desc["alive_fraction"]),
                "binary_fraction": float(desc["binary_fraction"]),
                "b0": int(desc["b0"]),
                "b1": int(desc["b1"]),
                "wall_seconds": float(elapsed),
            }
        )
        print(
            f"[untrained] init={init_seed} start={seed} -> {name_by_label.get(assigned, 'outlier')} "
            f"alive={desc['alive_fraction']:.3f} bin={desc['binary_fraction']:.3f}",
            flush=True,
        )
    print(
        f"[untrained] init={init_seed} classes={dict(cls)} alive_med={median(alive):.3f}",
        flush=True,
    )
    result.setdefault("class_distribution", {})[str(init_seed)] = dict(cls)
    # Три прототипа: первые старты, попавшие в struct_1.
    proto_seeds = [
        r["seed"] for r in result["runs"] if r["init_seed"] == init_seed and r["assigned_cluster"] == 1
    ][:3]
    if not proto_seeds:
        print(f"[untrained] init={init_seed}: нет struct_1, ампутация пропущена", flush=True)
        continue
    for p_i, seed in enumerate(proto_seeds):
        final, points, desc, assigned, _ = run_final(model, seed)
        proto_stress = model.stress_ema.detach().clone()
        for rep in range(5):
            p_seed = 40000 + init_seed * 100 + p_i * 10 + rep
            gen = config.create_deterministic_generator(p_seed)
            model.set_generator(gen)
            model.stress_ema.copy_(proto_stress)
            model._noise_cache = {}
            model._noise_seq = 0
            model.begin_segment()
            state, meta = e02b._clone_perturbed_state(
                final, {"kind": "amputation", "fraction": 0.2}, gen, DEVICE
            )
            f2, p2, traj2, elapsed2 = e02b.rollout(model, state, 500, 25)
            d2 = e02b.describe_state(f2)
            a2 = int(
                e02b.assign_to_clusters(
                    e02b.descriptor_vector(d2).reshape(1, -1), mean, std, centroids, valid
                )[0]
            )
            labels2 = e02b.assign_to_clusters(traj2, mean, std, centroids, valid)
            return_step = next(
                (q["step"] for q, c in zip(p2, labels2, strict=True) if int(c) == 1),
                None,
            )
            result["recovery"].append(
                {
                    "init_seed": int(init_seed),
                    "prototype_seed": int(seed),
                    "repeat": int(rep),
                    "meta": meta,
                    "assigned_cluster": int(a2),
                    "assigned_class": name_by_label.get(a2, "outlier"),
                    "returned_same_class": bool(a2 == 1),
                    "return_step": return_step,
                    "final": d2,
                    "wall_seconds": float(elapsed2),
                }
            )
            print(
                f"[untrained] init={init_seed} proto={seed} rep={rep} -> "
                f"{name_by_label.get(a2, 'outlier')} same={a2 == 1} return={return_step}",
                flush=True,
            )
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[untrained] written {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB)", flush=True)
