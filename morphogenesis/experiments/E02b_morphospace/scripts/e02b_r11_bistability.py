"""E02b, exploratory: удерживает ли R-11 структуру, или она только транзиентна?

Матрица переходов дала один неразобранный случай: у R-11 seed42 собственное
состояние (seed 0) дало `struct_1` с устойчивостью 0.20 — то есть модель
вернулась в класс, но не удержала его. Census для R-11: 61/64 финала
`uniform_dark` и 3/64 `struct_1`, H2 — структура была транзиентной в 64/64.

Вопрос: это переходная фаза (структура есть, но уходит) или вторая устойчивая
живая ловушка? От ответа зависит утверждение «у каждой модели один живой
аттрактор».

Три фазы, все inference-only, 2000 шагов, снимок каждые 50:
- A: 16 собственных стартов с шума (сиды 0–15). Финальный класс, устойчивость
  и путь классов по снимкам; сверка с census для тех же сидов.
- B: чужие живые состояния (`struct_1`, `struct_2`, `uniform_bright`,
  `uniform_dark` — по 2 состояния) в R-11, по 2 сида шума цели.
- C: собственные финальные состояния R-11 (сиды 0, 1) обратно в R-11, по 2
  сида шума цели: удерживает ли модель свой собственный класс.

Правила заранее:
- `bistable` — в фазе B чужое `struct_1` заканчивается как `struct_1` с
  устойчивостью >= 0.75 хотя бы в 2 прогонах из 4, ИЛИ в фазе A/C собственные
  прогоны дают `struct_1` с устойчивостью >= 0.75 хотя бы в 2 прогонах;
- `transient_only` — `struct_1` встречается в траектории, но ни один прогон не
  заканчивается им с устойчивостью >= 0.75;
- `single_attractor` — `struct_1` не встречается вовсе.
Устойчивость = доля снимков последней четверти с классом финала.
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
OUT = EXP / "r11_bistability_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
TARGET = "WP4_R-11_s2000_seed42"
OWN_SEEDS = list(range(16))
FOREIGN = {
    "WP4_R-9_s2000_seed101": "struct_1",
    "WP4_R-9_s2000_seed42": "struct_2",
    "WP4_R-9_s2000_seed303": "uniform_bright",
    "WP4_R-9_s2000_seed202": "uniform_dark",
}
FOREIGN_STATE_SEEDS = [0, 1]
FOREIGN_NOISE_SEEDS = [0, 1]
STABLE_STABILITY = 0.75
DEAD_ALIVE = 0.05

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

census_class_by_seed = {
    int(r["seed"]): r["class_name"]
    for r in census["runs"]
    if r["family"] == TARGET
}


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


def classify_trajectory(traj):
    return [label_name(int(c)) for c in e02b.assign_to_clusters(traj, mean, std, centroids, valid)]


def stability_of(labels, final_label):
    if not labels:
        return None
    q0 = int(np.floor(0.75 * len(labels)))
    return float(sum(1 for x in labels[q0:] if x == final_label) / len(labels[q0:]))


def struct1_span(labels):
    """Сколько подряд снимков в хвосте траектории класс struct_1."""
    if not labels:
        return 0
    span = 0
    for x in reversed(labels):
        if x == "struct_1":
            span += 1
        else:
            break
    return span


phase_a = []
own_final_states = []
model = load_model(TARGET)
try:
    for seed in OWN_SEEDS:
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
        labels = classify_trajectory(traj)
        final_label = label_name(cid)
        row = {
            "phase": "A_own_start",
            "seed": int(seed),
            "final_class": final_label,
            "final_cluster": cid,
            "final_semantic": sem.get(cid, "outlier"),
            "stability_last_quarter": stability_of(labels, final_label),
            "struct_1_tail_span": struct1_span(labels),
            "had_struct_1_anywhere": "struct_1" in labels,
            "first_struct_1_step": next(
                (p["step"] for p, l in zip(points, labels, strict=True) if l == "struct_1"),
                None,
            ),
            "last_struct_1_step": next(
                (
                    p["step"]
                    for p, l in reversed(list(zip(points, labels, strict=True)))
                    if l == "struct_1"
                ),
                None,
            ),
            "class_path": labels,
            "alive_fraction": float(desc["alive_fraction"]),
            "binary_fraction": float(desc["binary_fraction"]),
            "census_class_same_seed": census_class_by_seed.get(int(seed)),
            "matches_census": census_class_by_seed.get(int(seed)) == final_label,
            "wall_seconds": float(elapsed),
        }
        phase_a.append(row)
        if seed in (0, 1):
            own_final_states.append(
                {"seed": int(seed), "state": final.detach().cpu().clone()}
            )
        print(
            f"[r11] A seed={seed:2d} -> {final_label:14s} "
            f"stable={row['stability_last_quarter']:.2f} "
            f"span={row['struct_1_tail_span']:2d} census={row['census_class_same_seed']}",
            flush=True,
        )
finally:
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

foreign_states = {}
for family in FOREIGN:
    model = load_model(family)
    try:
        states = []
        for seed in FOREIGN_STATE_SEEDS:
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
                    "state": final.detach().cpu().clone(),
                    "class": label_name(cid),
                    "alive_fraction": float(desc["alive_fraction"]),
                }
            )
        foreign_states[family] = states
        print(
            f"[r11] foreign {family} -> {[s['class'] for s in states]}",
            flush=True,
        )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

phase_b = []
phase_c = []
model = load_model(TARGET)
try:
    for family, states in foreign_states.items():
        for st in states:
            for noise_seed in FOREIGN_NOISE_SEEDS:
                e02b.prepare_model(model, noise_seed)
                final, points, traj, elapsed = e02b.rollout(
                    model, st["state"].to(DEVICE), STEPS, EVERY
                )
                desc = e02b.describe_state(final)
                cid = assign(desc)
                labels = classify_trajectory(traj)
                final_label = label_name(cid)
                row = {
                    "phase": "B_foreign",
                    "source_family": family,
                    "source_class": st["class"],
                    "source_seed": int(st["seed"]),
                    "noise_seed": int(noise_seed),
                    "final_class": final_label,
                    "final_cluster": cid,
                    "final_semantic": sem.get(cid, "outlier"),
                    "stability_last_quarter": stability_of(labels, final_label),
                    "struct_1_tail_span": struct1_span(labels),
                    "had_struct_1_anywhere": "struct_1" in labels,
                    "alive_fraction": float(desc["alive_fraction"]),
                    "binary_fraction": float(desc["binary_fraction"]),
                    "wall_seconds": float(elapsed),
                }
                phase_b.append(row)
                print(
                    f"[r11] B {family:24s} s{st['seed']}n{noise_seed}: "
                    f"{final_label:14s} stable={row['stability_last_quarter']:.2f}",
                    flush=True,
                )
    for st in own_final_states:
        for noise_seed in FOREIGN_NOISE_SEEDS:
            e02b.prepare_model(model, noise_seed)
            final, points, traj, elapsed = e02b.rollout(
                model, st["state"].to(DEVICE), STEPS, EVERY
            )
            desc = e02b.describe_state(final)
            cid = assign(desc)
            labels = classify_trajectory(traj)
            final_label = label_name(cid)
            row = {
                "phase": "C_own_final",
                "source_seed": int(st["seed"]),
                "noise_seed": int(noise_seed),
                "final_class": final_label,
                "final_cluster": cid,
                "final_semantic": sem.get(cid, "outlier"),
                "stability_last_quarter": stability_of(labels, final_label),
                "struct_1_tail_span": struct1_span(labels),
                "had_struct_1_anywhere": "struct_1" in labels,
                "alive_fraction": float(desc["alive_fraction"]),
                "binary_fraction": float(desc["binary_fraction"]),
                "wall_seconds": float(elapsed),
            }
            phase_c.append(row)
            print(
                f"[r11] C own s{st['seed']}n{noise_seed}: {final_label:14s} "
                f"stable={row['stability_last_quarter']:.2f}",
                flush=True,
            )
finally:
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def stable_rows(rows, cls):
    """Финал в классе cls, устойчивый и действительно живой (alive >= 0.05)."""
    return [
        r for r in rows
        if r["final_class"] == cls
        and r["alive_fraction"] >= DEAD_ALIVE
        and r["stability_last_quarter"] is not None
        and r["stability_last_quarter"] >= STABLE_STABILITY
    ]


b_struct1 = stable_rows(phase_b, "struct_1")
b_from_struct1_source = [
    r for r in b_struct1 if r.get("source_class") == "struct_1"
]
a_struct1 = stable_rows(phase_a, "struct_1")
c_struct1 = stable_rows(phase_c, "struct_1")
if len(b_from_struct1_source) >= 2 or len(a_struct1) >= 2 or len(c_struct1) >= 2:
    verdict = "bistable"
elif any(r["had_struct_1_anywhere"] for r in phase_a + phase_b + phase_c):
    verdict = "transient_only"
else:
    verdict = "single_attractor"

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_r11_bistability",
    "note": (
        "R-11 seed42: 16 собственных стартов, 16 чужих пересадок, 4 возврата "
        "собственных финалов; классы по замороженным центроидам census; "
        "описательная проверка, не H1–H4 и не обучение"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "target": TARGET,
    "decision_rule": {
        "bistable": (
            "struct_1 удерживается (устойчивость >= 0.75) минимум в 2 прогонах "
            "из чужих struct_1 или собственных стартов/финалов"
        ),
        "transient_only": "struct_1 встречается в траектории, но не удерживается",
        "single_attractor": "struct_1 не встречается",
    },
    "phase_a_own_start": phase_a,
    "phase_b_foreign": phase_b,
    "phase_c_own_final": phase_c,
    "summary": {
        "phase_a_final_counts": dict(Counter(r["final_class"] for r in phase_a)),
        "phase_a_matches_census": sum(1 for r in phase_a if r["matches_census"]),
        "phase_a_n": len(phase_a),
        "phase_a_had_struct_1_anywhere": sum(
            1 for r in phase_a if r["had_struct_1_anywhere"]
        ),
        "phase_a_stable_struct_1_n": len(a_struct1),
        "phase_b_final_counts": dict(Counter(r["final_class"] for r in phase_b)),
        "phase_b_n": len(phase_b),
        "phase_b_stable_struct_1_n": len(b_struct1),
        "phase_b_from_struct_1_source_stable_n": len(b_from_struct1_source),
        "phase_b_from_struct_1_source_counts": dict(
            Counter(
                r["final_class"]
                for r in phase_b
                if r.get("source_class") == "struct_1"
            )
        ),
        "phase_c_final_counts": dict(Counter(r["final_class"] for r in phase_c)),
        "phase_c_n": len(phase_c),
        "phase_c_stable_struct_1_n": len(c_struct1),
        "verdict": verdict,
    },
}
print(f"[r11] summary {result['summary']}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[r11] saved {OUT}", flush=True)
