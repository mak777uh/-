"""E02b, exploratory: переносятся ли struct_2 и struct_1 на отложенные сиды шума?

Перепись E02b использовала сиды 0–63. Здесь те же два чекпоинта (R-9 seed42 и
R-9 seed101) прогоняются на сидах 64–127: другие начальные поля и другая
последовательность шагового шума. Классы назначаются по замороженным
центроидам census, без перекластеризации.

Правило заранее: struct_2 считается перенесённым, если ≥52/64 (81.25%) финалов
попадают в struct_2 и ≥80% из них устойчивы на последней четверти. 32–51 —
частичный перенос; <32 — класс привязан к сидам переписи. Для struct_1 то же
правило с порогом 52/64. Это exploratory-проверка, а не повторная проверка H1:
H1 остаётся на предзарегистрированных сидах 0–63.
"""
import json
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
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "heldout_seeds_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
SEEDS = list(range(64, 128))
TARGET = {
    "WP4_R-9_s2000_seed42": "struct_2",
    "WP4_R-9_s2000_seed101": "struct_1",
}

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
sem = {int(c): str(s) for c, s in zip(valid, cl["semantic"], strict=True)}

# Центроиды восстанавливаются так же, как в остальных exploratory-скриптах:
# среднее z-векторов выученных членов класса; контроли не участвуют.
by_cluster = {int(c): [] for c in valid}
for r in census["runs"]:
    if r.get("is_control"):
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[cid].append(e02b.descriptor_vector(r["final"]))
centroids = np.vstack([np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid])
centroids = (centroids - mean) / std

baseline = {}
for family in TARGET:
    counts = Counter(r["class_name"] for r in census["runs"] if r["family"] == family)
    baseline[family] = dict(counts)

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_heldout_seeds",
    "note": "сиды 64–127, те же чекпоинты; классы по замороженным центроидам census, без перекластеризации",
    "seeds": SEEDS,
    "steps": 2000,
    "snapshot_every": 50,
    "device": str(DEVICE),
    "targets": TARGET,
    "decision_rule": {
        "supported": ">=52/64 финалов в целевом классе и >=80% из них устойчивы на последней четверти",
        "partial": "32–51/64 в целевом классе",
        "failed": "<32/64 в целевом классе",
    },
    "census_baseline_by_family": baseline,
    "runs": [],
    "summary": {},
}

specs = {s.family: s for s in e02b.load_checkpoint_specs(families=list(TARGET))}
for family, target in TARGET.items():
    spec = specs[family]
    model, _ck = e02b.build_model(spec, DEVICE)
    e02b.remember_stress_ema_start(model)
    rows = []
    for seed in SEEDS:
        run = e02b.run_seed(model, spec, seed, 2000, 50, DEVICE)
        desc = run["final"]
        assigned = int(
            e02b.assign_to_clusters(
                e02b.descriptor_vector(desc).reshape(1, -1), mean, std, centroids, valid
            )[0]
        )
        traj_labels = e02b.assign_to_clusters(run["traj_features"], mean, std, centroids, valid)
        final_label = int(traj_labels[-1]) if len(traj_labels) else -1
        q0 = int(np.floor(0.75 * len(traj_labels)))
        tail = traj_labels[q0:]
        stability = float((tail == final_label).mean()) if len(tail) else 0.0
        row = {
            "family": family,
            "seed": int(seed),
            "cluster": int(assigned),
            "class_name": names.get(assigned, "outlier"),
            "semantic": sem.get(assigned, e02b._cluster_semantic(desc)),
            "final_traj_cluster": final_label,
            "stability_last_quarter": stability,
            "settle_step": run["settle_step"],
            "dynamics": run["dynamics"],
            "final": desc,
            "trajectory": run["trajectory"],
            "wall_seconds": run["wall_seconds"],
        }
        rows.append(row)
        result["runs"].append(row)
        print(
            f"[heldout] {family} seed={seed} -> {row['class_name']} "
            f"stab={stability:.2f} alive={desc['alive_fraction']:.3f}",
            flush=True,
        )
    counts = Counter(r["class_name"] for r in rows)
    target_rows = [r for r in rows if r["class_name"] == target]
    alive_all = [r["final"]["alive_fraction"] for r in rows]
    alive_target = [r["final"]["alive_fraction"] for r in target_rows]
    stable_target = [r["stability_last_quarter"] for r in target_rows]
    fraction = len(target_rows) / len(rows)
    stable_fraction = (
        sum(1 for s in stable_target if s >= 0.8) / len(target_rows) if target_rows else 0.0
    )
    if len(target_rows) >= 52 and stable_fraction >= 0.8:
        status = "supported"
    elif len(target_rows) >= 32:
        status = "partial"
    else:
        status = "failed"
    result["summary"][family] = {
        "target": target,
        "n": len(rows),
        "class_counts": dict(counts),
        "target_n": len(target_rows),
        "target_fraction": float(fraction),
        "target_stable_fraction": float(stable_fraction),
        "target_alive_median": float(median(alive_target)) if alive_target else None,
        "alive_median": float(median(alive_all)),
        "status": status,
    }
    print(
        f"[heldout] {family}: {dict(counts)} target={target} "
        f"{len(target_rows)}/{len(rows)} stable={stable_fraction:.3f} -> {status}",
        flush=True,
    )
    del model
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[heldout] written {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)", flush=True)
