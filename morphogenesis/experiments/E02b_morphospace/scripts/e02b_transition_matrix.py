"""E02b, exploratory: матрица пересадок между всеми 12 каноническими моделями.

Прямая и обратная пересадки проверяли R-9 seed42 против трёх моделей. Здесь
грубее, но шире: одно готовое финальное состояние каждой из 12 канонических
моделей (старт seed 0) подаётся в каждую из 12 моделей (шум цели seed 0).
144 пересадки, классы — замороженные центроиды census, без перекластеризации.

Это описательная карта, а не доказательство. Одно состояние на источник и один
сид шума цели: диагональ и резкие отличия (kill/assimilate) читаются, тонкие
различия — нет. Кандидат на мультистабильность требует отдельного повтора.
Ни обучения, ни H1–H4 здесь нет.

Правила заранее (по живым источникам: alive >= 0.5 и класс не `death`):
- все живые источники умирают -> `killer`;
- ровно один живой финальный класс -> `single_live_attractor`;
- >= 2 живых класса, каждый набран >= 2 источниками -> `multi_basin_candidate`;
- иначе -> `mixed`.
Живость исхода определяется по alive (>= 0.05), а не только по метке класса:
один выживший из 4096 клеток даёт alive 0.00024, и такой мёртвый поле может
лечь в `struct_2`. Такие расхождения помечаются флагом `class_alive_conflict`
и считаются смертью.
Диагональ считается отдельно: модель против собственного состояния. Если она
не возвращается в свой класс с устойчивостью >= 0.75, вся строка модели
помечается `diagonal_unstable` и её выводы не интерпретируются.
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
OUT = EXP / "transition_matrix_exploratory.json"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
SOURCE_SEED = 0
NOISE_SEED = 0
LIVE_CLASSES = {"struct_1", "struct_2", "uniform_dark", "uniform_bright"}
STRUCTURAL_CLASSES = {"struct_1", "struct_2"}
# Класс из центроида — не приговор: в census у класса `death` alive до 0.0208,
# а один выживший в 4096 клеток даёт alive 0.00024 и может лечь в `struct_2`.
# Поэтому «живость» исхода определяем по alive, а расхождение помечаем флагом.
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

specs = e02b.load_checkpoint_specs(include_untrained=False)
if len(specs) != 12:
    raise SystemExit(f"ожидалось 12 канонических моделей, найдено {len(specs)}")
families = [s.family for s in specs]

home = {}
for family in families:
    members = [
        r for r in census["runs"]
        if r.get("family") == family and not r.get("is_control")
    ]
    if not members:
        # H-P1 входит в 12 канонических файлов, но census считает его контролем
        # и не кластеризует; для матрицы его домашний класс берём по всем строкам.
        members = [r for r in census["runs"] if r.get("family") == family]
    if not members:
        raise SystemExit(f"в census нет прогонов {family}")
    home[family] = Counter(r["class_name"] for r in members).most_common(1)[0][0]


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


source_states = []
for family in families:
    model = load_model(family)
    try:
        e02b.prepare_model(model, SOURCE_SEED)
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
        source_states.append(
            {
                "family": family,
                "home_class": home[family],
                "state_class": label_name(cid),
                "cluster": cid,
                "state": final.detach().cpu().clone(),
                "alive_fraction": float(desc["alive_fraction"]),
                "binary_fraction": float(desc["binary_fraction"]),
                "wall_seconds": float(elapsed),
            }
        )
        print(
            f"[matrix] source {family:28s} {label_name(cid):15s} "
            f"alive={desc['alive_fraction']:.3f}",
            flush=True,
        )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def summarize(group, own_class, live_group):
    counts = Counter(r["final_class"] for r in group)
    effective = Counter(
        "death" if r["alive_fraction"] < DEAD_ALIVE else r["final_class"]
        for r in group
    )
    live_counts = Counter(
        "death" if r["alive_fraction"] < DEAD_ALIVE else r["final_class"]
        for r in live_group
    )
    structural_counts = Counter(
        r["final_class"] for r in group if r["source_state_class"] in STRUCTURAL_CLASSES
    )
    own = [r for r in group if r["final_class"] == own_class]
    own_stable = [
        r for r in own
        if r["stability_last_quarter"] is not None
        and r["stability_last_quarter"] >= 0.75
    ]
    live_distinct = {c for c in live_counts if c in LIVE_CLASSES}
    n_live = len(live_group)
    if n_live == 0:
        verdict = "no_live_source"
    elif live_counts.get("death", 0) == n_live:
        verdict = "killer"
    elif len(live_distinct) == 1:
        verdict = "single_live_attractor"
    elif sum(1 for c in live_distinct if live_counts[c] >= 2) >= 2:
        verdict = "multi_basin_candidate"
    else:
        verdict = "mixed"
    return {
        "home_class": own_class,
        "n": len(group),
        "final_class_counts": dict(counts),
        "effective_class_counts": dict(effective),
        "live_source_n": n_live,
        "live_source_final_counts": dict(live_counts),
        "death_fraction_among_live_sources": (
            live_counts.get("death", 0) / n_live if n_live else None
        ),
        "distinct_live_outcomes": sorted(live_distinct),
        "structural_source_final_counts": dict(structural_counts),
        "home_n_all_sources": len(own),
        "home_stable_fraction": (
            len(own_stable) / len(own) if own else None
        ),
        "verdict": verdict,
    }


rows = []
for target_family in families:
    model = load_model(target_family)
    try:
        for src in source_states:
            e02b.prepare_model(model, NOISE_SEED)
            final, points, traj, elapsed = e02b.rollout(
                model, src["state"].to(DEVICE), STEPS, EVERY
            )
            desc = e02b.describe_state(final)
            cid = assign(desc)
            traj_labels = e02b.assign_to_clusters(traj, mean, std, centroids, valid)
            q0 = int(np.floor(0.75 * len(traj_labels)))
            stability = (
                float((traj_labels[q0:] == cid).mean())
                if len(traj_labels)
                else None
            )
            home_cid = next(
                (int(c) for c, n in names.items() if n == home[target_family]),
                None,
            )
            return_step = next(
                (
                    q["step"]
                    for q, c in zip(points, traj_labels, strict=True)
                    if int(c) == home_cid
                ),
                None,
            )
            row = {
                "target_family": target_family,
                "target_home_class": home[target_family],
                "source_family": src["family"],
                "source_home_class": src["home_class"],
                "source_state_class": src["state_class"],
                "source_alive_fraction": src["alive_fraction"],
                "final_class": label_name(cid),
                "final_cluster": cid,
                "final_semantic": sem.get(cid, "outlier"),
                "final_alive": float(desc["alive_fraction"]),
                "outcome_alive": bool(desc["alive_fraction"] >= DEAD_ALIVE),
                "class_alive_conflict": bool(
                    (desc["alive_fraction"] < DEAD_ALIVE and label_name(cid) in STRUCTURAL_CLASSES)
                    or (desc["alive_fraction"] >= DEAD_ALIVE and label_name(cid) == "death")
                ),
                "stability_last_quarter": stability,
                "return_step_to_target_home": return_step,
                "alive_fraction": float(desc["alive_fraction"]),
                "binary_fraction": float(desc["binary_fraction"]),
                "wall_seconds": float(elapsed),
                "diagonal": src["family"] == target_family,
            }
            rows.append(row)
            print(
                f"[matrix] {target_family:28s} <- {src['family']:28s}: "
                f"{row['final_class']:15s} stable={stability:.2f} "
                f"ret={return_step}",
                flush=True,
            )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_transition_matrix",
    "note": (
        "12x12 пересадок готовых финальных состояний (источник seed 0) "
        "в 12 канонических моделях (шум цели seed 0); классы по замороженным "
        "центроидам census; описательная карта, не H1–H4 и не обучение"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "source_seed": SOURCE_SEED,
    "noise_seed": NOISE_SEED,
    "rules": {
        "live_source": "alive_fraction >= 0.5 и source_state_class != death",
        "killer": "все живые источники дают death",
        "single_live_attractor": "ровно один живой финальный класс среди живых источников",
        "multi_basin_candidate": ">= 2 живых класса, каждый >= 2 источниками",
        "mixed": "остальное",
        "diagonal": "source_family == target_family; ожидается свой класс",
    },
    "source_states": [
        {k: v for k, v in s.items() if k != "state"} for s in source_states
    ],
    "targets": {},
    "sources": {},
    "rows": rows,
}
for family in families:
    group = [r for r in rows if r["target_family"] == family]
    live_group = [
        r for r in group
        if r["source_alive_fraction"] >= 0.5
        and r["source_state_class"] != "death"
    ]
    summary = summarize(group, home[family], live_group)
    diag = next((r for r in group if r["diagonal"]), None)
    summary["diagonal"] = {
        "source_family": diag["source_family"] if diag else None,
        "final_class": diag["final_class"] if diag else None,
        "stability_last_quarter": (
            diag["stability_last_quarter"] if diag else None
        ),
        "ok": bool(
            diag
            and diag["final_class"] == home[family]
            and (diag["stability_last_quarter"] or 0) >= 0.75
        ),
    }
    if not summary["diagonal"]["ok"]:
        summary["verdict"] = "diagonal_unstable"
    result["targets"][family] = summary

for src in source_states:
    group = [r for r in rows if r["source_family"] == src["family"]]
    counts = Counter(r["final_class"] for r in group)
    result["sources"][src["family"]] = {
        "home_class": src["home_class"],
        "state_class": src["state_class"],
        "alive_fraction": src["alive_fraction"],
        "destination_counts": dict(counts),
        "n_destinations": len(group),
        "universal": len(counts) == 1,
    }

result["summary"] = {
    "n_targets": len(families),
    "n_rows": len(rows),
    "verdict_counts": dict(
        Counter(v["verdict"] for v in result["targets"].values())
    ),
    "killer_targets": [
        f for f, v in result["targets"].items() if v["verdict"] == "killer"
    ],
    "single_live_targets": [
        f for f, v in result["targets"].items()
        if v["verdict"] == "single_live_attractor"
    ],
    "multi_basin_candidates": [
        f for f, v in result["targets"].items()
        if v["verdict"] == "multi_basin_candidate"
    ],
    "diagonal_unstable_targets": [
        f for f, v in result["targets"].items()
        if v["verdict"] == "diagonal_unstable"
    ],
    "class_alive_conflicts": [
        {
            "target_family": r["target_family"],
            "source_family": r["source_family"],
            "final_class": r["final_class"],
            "alive_fraction": r["alive_fraction"],
        }
        for r in rows
        if r["class_alive_conflict"]
    ],
    "dead_alive_threshold": DEAD_ALIVE,
}
print(f"[matrix] summary {result['summary']}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[matrix] saved {OUT}", flush=True)
