"""E02b, exploratory: обратная пересадка `struct_2` в чужие модели.

Прямая проверка (basin_crossinit) показала: R-9 seed42 переводит готовые
`struct_1`, `uniform_dark` и `uniform_bright` в `struct_2` (48/48). Здесь
обратное направление: готовые состояния `struct_2` (seed42, сиды 0–3)
подаются в R-9 seed101, seed202 и seed303, по 4 состояния × 4 сида шума цели.

Вопрос: у каждой ли модели один живой аттрактор, или чужие модели способны
удерживать `struct_2`? Классы — замороженные центроиды census; перекластеризации
нет. Это exploratory, не H1–H4 и не обучение.

Правило заранее: для каждой destination-модели ≥12/16 финалов в её собственном
классе и ≥80% устойчивы — «own attractor»; 4–11 — «mixed»; <4 — «struct_2
удерживается/другое».
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
OUT = EXP / "basin_reverse_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
STATE_SEEDS = [0, 1, 2, 3]
NOISE_SEEDS = [0, 1, 2, 3]
SOURCE_FAMILY = "WP4_R-9_s2000_seed42"
DESTINATIONS = {
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


def load_model(family):
    spec = e02b.load_checkpoint_specs(families=[family], include_untrained=False)[0]
    model, _ = e02b.build_model(spec, DEVICE)
    return model


def generate_source_states():
    model = load_model(SOURCE_FAMILY)
    states = []
    try:
        for seed in STATE_SEEDS:
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
                }
            )
            print(
                f"[reverse] source struct_2 seed={seed} -> {label_name(cid)} "
                f"alive={desc['alive_fraction']:.3f}",
                flush=True,
            )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return states


source_states = generate_source_states()
rows = []
for family, expected in DESTINATIONS.items():
    expected_cid = next(
        (int(c) for c, n in names.items() if n == expected), None
    )
    if expected_cid is None:
        raise SystemExit(f"в census нет класса {expected}")
    model = load_model(family)
    try:
        for src in source_states:
            for noise_seed in NOISE_SEEDS:
                e02b.prepare_model(model, noise_seed)
                final, points, traj, elapsed = e02b.rollout(
                    model, src["state"].to(DEVICE), STEPS, EVERY
                )
                desc = e02b.describe_state(final)
                cid = assign(desc)
                traj_labels = e02b.assign_to_clusters(
                    traj, mean, std, centroids, valid
                )
                q0 = int(np.floor(0.75 * len(traj_labels)))
                stability = (
                    float((traj_labels[q0:] == cid).mean())
                    if len(traj_labels)
                    else None
                )
                return_step = next(
                    (
                        q["step"]
                        for q, c in zip(points, traj_labels, strict=True)
                        if int(c) == expected_cid
                    ),
                    None,
                )
                row = {
                    "destination_family": family,
                    "destination_expected": expected,
                    "state_seed": int(src["seed"]),
                    "noise_seed": int(noise_seed),
                    "final_class": label_name(cid),
                    "final_cluster": cid,
                    "final_semantic": sem.get(cid, "outlier"),
                    "stability_last_quarter": stability,
                    "return_step_to_expected": return_step,
                    "alive_fraction": float(desc["alive_fraction"]),
                    "binary_fraction": float(desc["binary_fraction"]),
                    "wall_seconds": float(elapsed),
                }
                rows.append(row)
                print(
                    f"[reverse] {expected:15s} s{src['seed']}->n{noise_seed}: "
                    f"{row['final_class']:15s} stable={stability:.2f} "
                    f"ret={return_step}",
                    flush=True,
                )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def summarize(group, own_class):
    counts = Counter(r["final_class"] for r in group)
    in_own = [r for r in group if r["final_class"] == own_class]
    stable = [
        r for r in in_own
        if r["stability_last_quarter"] is not None
        and r["stability_last_quarter"] >= 0.8
    ]
    returns = [
        r["return_step_to_expected"] for r in in_own
        if r["return_step_to_expected"] is not None
    ]
    alive = [r["alive_fraction"] for r in group]
    if len(in_own) >= 12 and len(stable) >= 0.8 * len(in_own):
        verdict = "own_attractor"
    elif len(in_own) >= 4:
        verdict = "mixed"
    else:
        verdict = "struct_2_or_other"
    return {
        "n": len(group),
        "final_class_counts": dict(counts),
        "own_class_n": len(in_own),
        "own_class_stable_n": len(stable),
        "own_class_stable_fraction": (len(stable) / len(in_own)) if in_own else None,
        "return_step_median": float(np.median(returns)) if returns else None,
        "alive_median": float(np.median(alive)),
        "verdict": verdict,
    }


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_basin_reverse",
    "note": (
        "обратная пересадка готовых struct_2 в R-9 seed101/202/303; "
        "классы по замороженным центроидам census; не обучение и не H1–H4"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "source_family": SOURCE_FAMILY,
    "state_seeds": STATE_SEEDS,
    "noise_seeds": NOISE_SEEDS,
    "source_states": [
        {k: v for k, v in s.items() if k != "state"} for s in source_states
    ],
    "rows": rows,
    "summary": {},
}
for family, expected in DESTINATIONS.items():
    group = [r for r in rows if r["destination_family"] == family]
    result["summary"][expected] = summarize(group, expected)
    print(f"[reverse] summary {expected}: {result['summary'][expected]}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[reverse] saved {OUT}", flush=True)
