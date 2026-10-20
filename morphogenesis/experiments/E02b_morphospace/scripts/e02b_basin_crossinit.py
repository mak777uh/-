"""E02b, exploratory: что делает dynamics R-9 seed42 с чужими готовыми классами?

До сих пор `struct_2` проверялся на устойчивость (ампутация, шум, малый патч,
длинный горизонт), но не на **бассейн**: если подать на вход модели готовое
состояние другого класса, останется ли оно собой или придёт в `struct_2`?

Дизайн: 3 источника × 4 сида (0–3) × 4 сида шума цели (0–3) = 48 пересадок,
плюс самопересадка `struct_2` 4×4 = 16 как контроль. Источники — финальные
состояния канонических чекпоинтов R-9 seed101 (`struct_1`), seed202
(`uniform_dark`), seed303 (`uniform_bright`). Цель — R-9 seed42.

Классы назначаются замороженными центроидами census; перекластеризации нет.
Правило заранее: для каждого источника ≥12/16 финалов в `struct_2` и ≥80%
устойчивы — «сходится»; 4–11 — «смешанно»; <4 — «остаётся своим/другим».
Это exploratory-проверка бассейна, не H1–H4 и не обучение.
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
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "basin_crossinit_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
SOURCE_SEEDS = [0, 1, 2, 3]
TARGET_SEEDS = [0, 1, 2, 3]
TARGET_FAMILY = "WP4_R-9_s2000_seed42"
SOURCES = {
    "WP4_R-9_s2000_seed101": "struct_1",
    "WP4_R-9_s2000_seed202": "uniform_dark",
    "WP4_R-9_s2000_seed303": "uniform_bright",
}

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
sem = {int(c): str(s) for c, s in zip(valid, cl["semantic"], strict=True)}
by_cluster = {int(c): [] for c in valid}
for r in census["runs"]:
    if r.get("is_control"):
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[cid].append(e02b.descriptor_vector(r["final"]))
centroids = np.vstack([np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid])
centroids = (centroids - mean) / std


def assign(desc):
    return int(
        e02b.assign_to_clusters(
            e02b.descriptor_vector(desc).reshape(1, -1), mean, std, centroids, valid
        )[0]
    )


def label_name(cid):
    return names.get(int(cid), "outlier")


def generate_states(family, seeds):
    """Финальные состояния чекпоинта на заданных сидах (по одному, без батча)."""
    spec = e02b.load_checkpoint_specs(families=[family], include_untrained=False)[0]
    model, _ = e02b.build_model(spec, DEVICE)
    states = []
    try:
        for seed in seeds:
            e02b.prepare_model(model, seed)
            start = e02b.init_state(
                batch_size=1,
                channels=e02b.config.N_CHANNELS,
                grid_size=e02b.config.GRID_SIZE,
                device=DEVICE,
                generator=model.generator,
            )
            final, points, traj, elapsed = e02b.rollout(model, start, STEPS, EVERY)
            desc = e02b.describe_state(final)
            cid = assign(desc)
            states.append(
                {
                    "seed": int(seed),
                    "state": final.detach().clone(),
                    "class": label_name(cid),
                    "cluster": cid,
                    "alive_fraction": float(desc["alive_fraction"]),
                    "binary_fraction": float(desc["binary_fraction"]),
                    "wall_seconds": float(elapsed),
                }
            )
            print(
                f"[basin] source {family} seed={seed} -> {label_name(cid)} "
                f"alive={desc['alive_fraction']:.3f}",
                flush=True,
            )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return states


# Источники считаются по одному, на CPU остаются только 4 состояния.
source_states = {family: generate_states(family, SOURCE_SEEDS) for family in SOURCES}
self_states = generate_states(TARGET_FAMILY, SOURCE_SEEDS)

# Целевая модель загружается один раз; перед каждой пересадкой prepare_model
# сбрасывает генератор, stress EMA и кэш шума, но не само начальное состояние.
target_spec = e02b.load_checkpoint_specs(
    families=[TARGET_FAMILY], include_untrained=False
)[0]
target, _ = e02b.build_model(target_spec, DEVICE)
rows = []

# return_step ищется по имени struct_2, поэтому нужен его cluster id.
STRUCT2_ID = next(
    (int(c) for c, n in names.items() if n == "struct_2"), None
)
if STRUCT2_ID is None:
    raise SystemExit("в census нет struct_2")


def run_transplant(source_family, source_class, state, source_seed, target_seed):
    e02b.prepare_model(target, target_seed)
    start = state.to(DEVICE)
    final, points, traj, elapsed = e02b.rollout(target, start, STEPS, EVERY)
    final_desc = e02b.describe_state(final)
    final_cid = assign(final_desc)
    traj_labels = e02b.assign_to_clusters(traj, mean, std, centroids, valid)
    q0 = int(np.floor(0.75 * len(traj_labels)))
    stability = float((traj_labels[q0:] == final_cid).mean()) if len(traj_labels) else None
    return_step = next(
        (
            q["step"]
            for q, c in zip(points, traj_labels, strict=True)
            if int(c) == STRUCT2_ID
        ),
        None,
    )
    row = {
        "source_family": source_family,
        "source_class": source_class,
        "source_seed": int(source_seed),
        "target_seed": int(target_seed),
        "final_class": label_name(final_cid),
        "final_cluster": final_cid,
        "final_semantic": sem.get(final_cid, "outlier"),
        "stability_last_quarter": stability,
        "return_step_to_struct_2": return_step,
        "alive_fraction": float(final_desc["alive_fraction"]),
        "binary_fraction": float(final_desc["binary_fraction"]),
        "wall_seconds": float(elapsed),
    }
    rows.append(row)
    print(
        f"[basin] {source_class:15s} s{source_seed}->t{target_seed}: "
        f"{row['final_class']:15s} stable={stability:.2f} ret={return_step}",
        flush=True,
    )
    return row


try:
    for family, expected in SOURCES.items():
        for src in source_states[family]:
            for target_seed in TARGET_SEEDS:
                run_transplant(
                    family, expected, src["state"], src["seed"], target_seed
                )
    for src in self_states:
        for target_seed in TARGET_SEEDS:
            run_transplant(
                TARGET_FAMILY, "struct_2", src["state"], src["seed"], target_seed
            )
finally:
    del target
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def summarize(rows_for_source):
    counts = Counter(r["final_class"] for r in rows_for_source)
    n = len(rows_for_source)
    in_target = [r for r in rows_for_source if r["final_class"] == "struct_2"]
    stable = [
        r for r in in_target
        if r["stability_last_quarter"] is not None and r["stability_last_quarter"] >= 0.8
    ]
    returns = [r["return_step_to_struct_2"] for r in in_target if r["return_step_to_struct_2"] is not None]
    alive = [r["alive_fraction"] for r in rows_for_source]
    if len(in_target) >= 12 and len(stable) >= 0.8 * len(in_target):
        verdict = "converges"
    elif len(in_target) >= 4:
        verdict = "mixed"
    else:
        verdict = "retains_source_or_other"
    return {
        "n": n,
        "final_class_counts": dict(counts),
        "struct_2_n": len(in_target),
        "struct_2_stable_n": len(stable),
        "struct_2_stable_fraction": (len(stable) / len(in_target)) if in_target else None,
        "return_step_median": float(np.median(returns)) if returns else None,
        "alive_median": float(np.median(alive)),
        "verdict": verdict,
    }


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_basin_crossinit",
    "note": (
        "пересадка готовых финальных состояний других классов в dynamics R-9 seed42; "
        "классы по замороженным центроидам census; не обучение и не H1–H4"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "target_family": TARGET_FAMILY,
    "source_seeds": SOURCE_SEEDS,
    "target_noise_seeds": TARGET_SEEDS,
    "sources": {
        family: {
            "expected_class": expected,
            "states": [{k: v for k, v in s.items() if k != "state"} for s in states],
        }
        for family, states in source_states.items()
    },
    "rows": rows,
    "summary": {},
}
groups = {}
for family, expected in SOURCES.items():
    groups[expected] = [r for r in rows if r["source_family"] == family]
groups["struct_2"] = [r for r in rows if r["source_family"] == TARGET_FAMILY]
for name, group in groups.items():
    result["summary"][name] = summarize(group)
    print(f"[basin] summary {name}: {result['summary'][name]}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[basin] saved {OUT}", flush=True)
