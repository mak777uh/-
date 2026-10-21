"""E02b, exploratory: повтор матрицы пересадок 12×12 с повторами.

Первая матрица (`transition_matrix_exploratory.json`) взяла по одному
финальному состоянию на источник и один сид шума цели: 144 пересадки.
Вердикты («killer», «single_live_attractor») описывали модель, но не
отделяли устойчивое состояние от удачного единичного прогона — по одной
выборке это различить нельзя.

Здесь та же матрица, но с повторами: по 3 готовых финальных состояния
на источник (старты seed 0, 1, 2) и по 3 сида шума цели (0, 1, 2).
Итого 36 источников × 12 целей × 3 шума = 1296 пересадок, по 9 выборок
на каждую пару (цель, семейство источника). Это в 9 раз больше работы
предыдущего прогона (~3.5 ч на CUDA) и даёт частоты вместо единичных
наблюдений.

Правила заранее (зафиксированы до запуска):

1. Живой источник: `alive_fraction >= 0.5` и класс источника ≠ `death`.
2. Живость исхода определяется по `alive >= 0.05` (DEAD_ALIVE), а не по
   метке класса. Расхождение помечается флагом `class_alive_conflict`
   и считается смертью.
3. Пара (цель, семейство источника), n = 9:
   - `dominant_class` — эффективный класс с наибольшим счётчиком;
   - `pair_consistency` — доля выборок в `dominant_class`;
   - `pair_stable_fraction` — среди выборок `dominant_class` доля со
     `stability_last_quarter >= 0.75`.
4. Устойчивая пара: `pair_consistency >= 0.8`. Ниже — «лотерея», а не
   устойчивое состояние.
5. Вердикт модели считается по 54 живым выборкам (6 живых семейств × 9):
   - `killer` — все живые выборки мертвы;
   - `single_live_attractor` — ровно один живой класс среди живых выборок;
   - `multi_basin_candidate` — ≥2 живых класса, каждый ≥ 10% живых
     выборок (≥6 из 54) и `pair_stable_fraction` своего класса ≥ 0.5;
   - `mixed` — иначе.
6. Диагональ (цель против собственных состояний) считается отдельно:
   если модель возвращается в свой класс с устойчивостью ≥ 0.75 менее
   чем в 8 из 9, вся строка модели помечается `diagonal_unstable` и её
   выводы не интерпретируются.

Ни обучения, ни H1–H4 здесь нет: только повторно измеренные переходы
между уже обученными моделями. Строки пишутся инкрементально в JSONL,
чтобы прерванный прогон не терялся.
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
OUT = EXP / "transition_matrix_rep_exploratory.json"
ROWS = EXP / "transition_matrix_rep_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
SOURCE_SEEDS = [0, 1, 2]
NOISE_SEEDS = [0, 1, 2]
LIVE_CLASSES = {"struct_1", "struct_2", "uniform_dark", "uniform_bright"}
STRUCTURAL_CLASSES = {"struct_1", "struct_2"}
DEAD_ALIVE = 0.05
LIVE_SOURCE_ALIVE = 0.5
PAIR_CONSISTENCY_STABLE = 0.8
PAIR_STABILITY_STABLE = 0.75
MULTI_BASIN_MIN_FRACTION = 0.1
MULTI_BASIN_MIN_PAIR_STABLE = 0.5
DIAGONAL_MIN_OK = 8
DIAGONAL_TOTAL = len(SOURCE_SEEDS) * len(NOISE_SEEDS)

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
        # H-P1 входит в 12 канонических файлов, но census считает его контролем.
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


def effective_class(row):
    """Живой класс или смерть — решение по alive, а не по метке."""
    return row["final_class"] if row["alive_fraction"] >= DEAD_ALIVE else "death"


# ---------------------------------------------------------------- источники
source_states = []
for family in families:
    model = load_model(family)
    try:
        for seed in SOURCE_SEEDS:
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
            source_states.append(
                {
                    "family": family,
                    "home_class": home[family],
                    "source_seed": int(seed),
                    "state_class": label_name(cid),
                    "cluster": cid,
                    "state": final.detach().cpu().clone(),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "binary_fraction": float(desc["binary_fraction"]),
                    "wall_seconds": float(elapsed),
                }
            )
            print(
                f"[rep] source {family:28s} seed{seed} {label_name(cid):15s} "
                f"alive={desc['alive_fraction']:.3f}",
                flush=True,
            )
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ------------------------------------------------------------------- пересадки
done = set()
rows = []
if ROWS.exists():
    with open(ROWS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows.append(row)
            done.add((row["target_family"], row["source_family"], row["source_seed"], row["noise_seed"]))
    print(f"[rep] возобновление: {len(rows)} строк уже посчитано", flush=True)

fh = open(ROWS, "a", encoding="utf-8")
try:
    for target_family in families:
        model = load_model(target_family)
        try:
            home_cid = next(
                (int(c) for c, n in names.items() if n == home[target_family]), None
            )
            for src in source_states:
                for noise_seed in NOISE_SEEDS:
                    key = (
                        target_family,
                        src["family"],
                        src["source_seed"],
                        noise_seed,
                    )
                    if key in done:
                        continue
                    e02b.prepare_model(model, noise_seed)
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
                        "source_seed": src["source_seed"],
                        "source_state_class": src["state_class"],
                        "source_alive_fraction": src["alive_fraction"],
                        "noise_seed": int(noise_seed),
                        "final_class": label_name(cid),
                        "final_cluster": cid,
                        "final_semantic": sem.get(cid, "outlier"),
                        "final_alive": float(desc["alive_fraction"]),
                        "outcome_alive": bool(desc["alive_fraction"] >= DEAD_ALIVE),
                        "class_alive_conflict": bool(
                            (
                                desc["alive_fraction"] < DEAD_ALIVE
                                and label_name(cid) in STRUCTURAL_CLASSES
                            )
                            or (
                                desc["alive_fraction"] >= DEAD_ALIVE
                                and label_name(cid) == "death"
                            )
                        ),
                        "stability_last_quarter": stability,
                        "return_step_to_target_home": return_step,
                        "alive_fraction": float(desc["alive_fraction"]),
                        "binary_fraction": float(desc["binary_fraction"]),
                        "wall_seconds": float(elapsed),
                        "diagonal": src["family"] == target_family,
                    }
                    rows.append(row)
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    print(
                        f"[rep] {target_family:28s} <- {src['family']:28s} "
                        f"s{src['source_seed']}/n{noise_seed}: "
                        f"{row['final_class']:15s} stable={stability:.2f}",
                        flush=True,
                    )
        finally:
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
finally:
    fh.close()


# ------------------------------------------------------------------ сводка
def summarize_pairs(group):
    """По парам (цель, семейство источника): доминирующий класс и устойчивость."""
    pairs = {}
    by_source = {}
    for r in group:
        by_source.setdefault(r["source_family"], []).append(r)
    for src_family, src_rows in by_source.items():
        counts = Counter(effective_class(r) for r in src_rows)
        dominant, dominant_n = counts.most_common(1)[0]
        own = [r for r in src_rows if effective_class(r) == dominant]
        stable_own = [
            r for r in own
            if r["stability_last_quarter"] is not None
            and r["stability_last_quarter"] >= PAIR_STABILITY_STABLE
        ]
        pairs[src_family] = {
            "n": len(src_rows),
            "effective_counts": dict(counts),
            "dominant_class": dominant,
            "dominant_n": dominant_n,
            "pair_consistency": dominant_n / len(src_rows),
            "pair_stable_fraction": len(stable_own) / len(own) if own else None,
            "pair_is_stable": bool(
                dominant_n / len(src_rows) >= PAIR_CONSISTENCY_STABLE
            ),
            "source_alive_fraction": src_rows[0]["source_alive_fraction"],
            "source_state_class": src_rows[0]["source_state_class"],
        }
    return pairs


targets = {}
for family in families:
    group = [r for r in rows if r["target_family"] == family]
    if not group:
        continue
    pairs = summarize_pairs(group)
    live_pairs = {
        s: p for s, p in pairs.items()
        if p["source_alive_fraction"] >= LIVE_SOURCE_ALIVE
        and p["source_state_class"] != "death"
    }
    live_rows = [
        r for r in group
        if r["source_alive_fraction"] >= LIVE_SOURCE_ALIVE
        and r["source_state_class"] != "death"
    ]
    live_counts = Counter(effective_class(r) for r in live_rows)
    live_distinct = {c for c in live_counts if c in LIVE_CLASSES}
    n_live = len(live_rows)
    if n_live == 0:
        verdict = "no_live_source"
    elif live_counts.get("death", 0) == n_live:
        verdict = "killer"
    elif len(live_distinct) == 1:
        verdict = "single_live_attractor"
    else:
        strong = [
            c for c in live_distinct
            if live_counts[c] / n_live >= MULTI_BASIN_MIN_FRACTION
            and any(
                p["dominant_class"] == c
                and (p["pair_stable_fraction"] or 0) >= MULTI_BASIN_MIN_PAIR_STABLE
                for p in live_pairs.values()
            )
        ]
        verdict = "multi_basin_candidate" if len(strong) >= 2 else "mixed"
    diag_rows = [r for r in group if r["diagonal"]]
    diag_ok = [
        r for r in diag_rows
        if r["final_class"] == home[family]
        and r["stability_last_quarter"] is not None
        and r["stability_last_quarter"] >= PAIR_STABILITY_STABLE
    ]
    diag = {
        "n": len(diag_rows),
        "ok_n": len(diag_ok),
        "final_classes": dict(Counter(r["final_class"] for r in diag_rows)),
        "ok": bool(diag_rows and len(diag_ok) >= DIAGONAL_MIN_OK),
    }
    if not diag["ok"]:
        verdict = "diagonal_unstable"
    targets[family] = {
        "home_class": home[family],
        "n": len(group),
        "live_source_n": n_live,
        "live_source_final_counts": dict(live_counts),
        "death_fraction_among_live_sources": (
            live_counts.get("death", 0) / n_live if n_live else None
        ),
        "distinct_live_outcomes": sorted(live_distinct),
        "pairs": pairs,
        "live_pairs": live_pairs,
        "n_unstable_live_pairs": sum(
            1 for p in live_pairs.values() if not p["pair_is_stable"]
        ),
        "diagonal": diag,
        "verdict": verdict,
    }

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_transition_matrix_replication",
    "note": (
        "повтор матрицы 12x12 с 3 состояниями на источник и 3 сидами шума цели; "
        "1296 пересадок, по 9 на пару; классы по замороженным центроидам census; "
        "описательная карта, не H1–H4 и не обучение"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "snapshot_every": EVERY,
    "source_seeds": SOURCE_SEEDS,
    "noise_seeds": NOISE_SEEDS,
    "rules": {
        "live_source": f"alive_fraction >= {LIVE_SOURCE_ALIVE} и класс источника != death",
        "dead_alive": f"alive_fraction < {DEAD_ALIVE} считается смертью",
        "pair_consistency_stable": PAIR_CONSISTENCY_STABLE,
        "pair_stability_stable": PAIR_STABILITY_STABLE,
        "multi_basin": (
            f">= 2 живых класса, каждый >= {MULTI_BASIN_MIN_FRACTION} живых выборок "
            f"и pair_stable_fraction >= {MULTI_BASIN_MIN_PAIR_STABLE}"
        ),
        "diagonal": f"модель возвращается в свой класс в >= {DIAGONAL_MIN_OK} из {DIAGONAL_TOTAL}",
    },
    "source_states": [
        {k: v for k, v in s.items() if k != "state"} for s in source_states
    ],
    "rows": rows,
    "targets": targets,
    "summary": {
        "n_rows": len(rows),
        "n_targets": len(targets),
        "verdict_counts": dict(
            Counter(v["verdict"] for v in targets.values())
        ),
        "killer_targets": [
            f for f, v in targets.items() if v["verdict"] == "killer"
        ],
        "single_live_targets": [
            f for f, v in targets.items() if v["verdict"] == "single_live_attractor"
        ],
        "multi_basin_candidates": [
            f for f, v in targets.items() if v["verdict"] == "multi_basin_candidate"
        ],
        "diagonal_unstable_targets": [
            f for f, v in targets.items() if v["verdict"] == "diagonal_unstable"
        ],
        "unstable_live_pairs": [
            {
                "target_family": f,
                "source_family": s,
                "pair_consistency": p["pair_consistency"],
                "dominant_class": p["dominant_class"],
            }
            for f, v in targets.items()
            for s, p in v["live_pairs"].items()
            if not p["pair_is_stable"]
        ],
        "class_alive_conflicts": [
            {
                "target_family": r["target_family"],
                "source_family": r["source_family"],
                "source_seed": r["source_seed"],
                "noise_seed": r["noise_seed"],
                "final_class": r["final_class"],
                "alive_fraction": r["alive_fraction"],
            }
            for r in rows
            if r["class_alive_conflict"]
        ],
        "dead_alive_threshold": DEAD_ALIVE,
    },
}
print(f"[rep] summary {result['summary']}", flush=True)

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[rep] saved {OUT}", flush=True)
