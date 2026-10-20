"""E02b, exploratory: держится ли struct_2 за пределами 2000 шагов?

Перепись останавливалась на 2000 шагах, а большинство прогонов struct_2
классифицированы как drift с малой дельтой. Здесь 16 стартов R-9 seed42 идут
6000 шагов; класс назначается замороженными центроидами census на каждом
снимке. Проверяется, аттрактор это или медленный транзиент.

Правило заранее: persistent, если ≥14/16 финалов остаются struct_2 и ≥80% из них
устойчивы на последней четверти (шаги 4550–6000). 8–13 — partial; <8 — transient.
Дополнительно сверяется класс на шаге 2000 с census для тех же сидов.
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
OUT = EXP / "long_horizon_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
FAMILY = "WP4_R-9_s2000_seed42"
TARGET = "struct_2"
SEEDS = list(range(16))
STEPS = 6000
EVERY = 50

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

census_class = {
    int(r["seed"]): str(r["class_name"])
    for r in census["runs"]
    if r["family"] == FAMILY and int(r["seed"]) in SEEDS
}

spec = e02b.load_checkpoint_specs(families=[FAMILY])[0]
model, _ck = e02b.build_model(spec, DEVICE)
e02b.remember_stress_ema_start(model)

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_long_horizon",
    "note": "16 сидов × 6000 шагов; struct_2; замороженные центроиды census",
    "family": FAMILY,
    "target": TARGET,
    "seeds": SEEDS,
    "steps": STEPS,
    "snapshot_every": EVERY,
    "device": str(DEVICE),
    "decision_rule": {
        "persistent": ">=14/16 финалов в struct_2 и >=80% из них устойчивы на 4550–6000",
        "partial": "8–13/16 в struct_2",
        "transient": "<8/16 в struct_2",
    },
    "census_class_at_2000": {str(k): v for k, v in census_class.items()},
    "runs": [],
}

for seed in SEEDS:
    run = e02b.run_seed(model, spec, seed, STEPS, EVERY, DEVICE)
    labels = e02b.assign_to_clusters(run["traj_features"], mean, std, centroids, valid)
    points = run["trajectory"]
    final_label = int(labels[-1]) if len(labels) else -1
    q0 = int(np.floor(0.75 * len(labels)))
    tail = labels[q0:]
    stability = float((tail == final_label).mean()) if len(tail) else 0.0
    at = {}
    for step in (2000, 4000, 6000):
        idx = (step // EVERY) - 1
        if 0 <= idx < len(labels):
            at[str(step)] = names.get(int(labels[idx]), "outlier")
    check = at.get("2000") == census_class.get(seed)
    row = {
        "seed": int(seed),
        "final_class": names.get(final_label, "outlier"),
        "final_semantic": sem.get(final_label, "outlier"),
        "final_cluster": final_label,
        "stability_last_quarter": stability,
        "class_at_step": at,
        "census_class_at_2000": census_class.get(seed),
        "match_census_at_2000": bool(check),
        "settle_step": run["settle_step"],
        "dynamics": run["dynamics"],
        "final": run["final"],
        "trajectory": points,
        "wall_seconds": run["wall_seconds"],
    }
    result["runs"].append(row)
    print(
        f"[long] seed={seed} -> {row['final_class']} at={at} "
        f"stab={stability:.2f} match2000={check}",
        flush=True,
    )

target_rows = [r for r in result["runs"] if r["final_class"] == TARGET]
stable_target = [r["stability_last_quarter"] for r in target_rows]
stable_fraction = (
    sum(1 for s in stable_target if s >= 0.8) / len(target_rows) if target_rows else 0.0
)
if len(target_rows) >= 14 and stable_fraction >= 0.8:
    status = "persistent"
elif len(target_rows) >= 8:
    status = "partial"
else:
    status = "transient"
result["summary"] = {
    "n": len(result["runs"]),
    "class_counts": dict(Counter(r["final_class"] for r in result["runs"])),
    "target_n": len(target_rows),
    "target_stable_fraction": float(stable_fraction),
    "alive_median": float(median(r["final"]["alive_fraction"] for r in result["runs"])),
    "match_census_at_2000": sum(r["match_census_at_2000"] for r in result["runs"]),
    "status": status,
}
print(f"[long] summary {result['summary']}", flush=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[long] written {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)", flush=True)
