"""Независимая проверка exploratory-артефактов E02b.

Канонический `e02b_verify.py` проверяет census и perturbations. Здесь — те же
правила для ночных exploratory-прогонов: сводки пересчитываются из строк
артефакта, а не читаются из harness-полей. Правила вердиктов переписаны здесь
заново; если артефакт и скрипт разойдутся, verifier это поймает.

Запуск: `python e02b_verify_exploratory.py` (из корня репозитория).
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]

DEAD_ALIVE = 0.05
LIVE_SOURCE_ALIVE = 0.5
LIVE_CLASSES = {"struct_1", "struct_2", "uniform_dark", "uniform_bright"}
STRUCTURAL = {"struct_1", "struct_2"}

errors = []
warnings = []


def check(cond, msg):
    if cond:
        print("OK  ", msg)
    else:
        print("FAIL", msg)
        errors.append(msg)


def warn(cond, msg):
    if not cond:
        print("WARN", msg)
        warnings.append(msg)


def load(name):
    path = EXP / name
    if not path.exists():
        print(f"SKIP {name}: нет артефакта")
        return None
    return json.load(open(path, encoding="utf-8"))


def median(values):
    vals = sorted(values)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return float(vals[mid])
    return 0.5 * (vals[mid - 1] + vals[mid])


# ---------------------------------------------------------------- устойчивость
rob = load("cluster_robustness_exploratory.json")
if rob:
    check(rob["n_runs"] == 704, f"robustness: n_runs={rob['n_runs']}")
    check(rob["full_refit"]["ari"] == 1.0, "robustness: полный refit ARI=1.0")
    check(
        rob["full_refit"]["label_matches"] == 704,
        f"robustness: совпадений меток {rob['full_refit']['label_matches']}",
    )
    ks = {int(e["k"]): e for e in rob["k_sweep"]}
    check(set(ks) == set(range(2, 11)), f"robustness: sweep k=2..10 ({sorted(ks)})")
    for k in range(3, 9):
        check(
            ks[k]["jaccard"]["struct_2"] == 1.0,
            f"robustness: struct_2 цел при k={k} (J={ks[k]['jaccard']['struct_2']})",
        )
    check(
        min(ks[k]["jaccard"]["struct_2"] for k in ks) == rob["summary"]["struct_2_jaccard_min_over_k"],
        "robustness: summary.jaccard_min совпадает с k-sweep",
    )
    boot = rob["bootstrap_k5"]
    check(boot["n"] == 200, f"robustness: bootstrap n={boot['n']}")
    check(
        boot["jaccard_p05"]["struct_2"] == 1.0
        and rob["summary"]["struct_2_bootstrap_jaccard_p05"] == 1.0,
        "robustness: struct_2 p05 Jaccard = 1.0",
    )
    sel = rob["bootstrap_k_selection"]
    check(
        sum(sel["counts"].values()) == sel["n"] == 100,
        f"robustness: счётчики выбора k дают {sum(sel['counts'].values())} из {sel['n']}",
    )
    check(
        abs(sel["share_k5"] - sel["counts"]["5"] / sel["n"]) < 1e-12,
        f"robustness: доля k=5 = {sel['share_k5']}",
    )
    lofo = rob["leave_one_feature_out"]
    check(len(lofo) == 18, f"robustness: LOFO по {len(lofo)} признакам")
    check(
        min(e["jaccard"]["struct_2"] for e in lofo) == rob["summary"]["struct_2_lofo_jaccard_min"],
        "robustness: summary.lofo_min совпадает",
    )
    check(
        all(e["jaccard"]["struct_2"] == 1.0 for e in lofo),
        "robustness: struct_2 цел при удалении любого признака",
    )
    noise = rob["feature_noise"]
    check(
        all(e["ari_median"] == 1.0 for e in noise),
        "robustness: ARI=1.0 при шуме признаков до 10%",
    )
    check(
        min(
            min(e["jaccard_median"]["struct_2"], e["jaccard_p05"]["struct_2"])
            for e in noise
        ) == rob["summary"]["struct_2_noise_jaccard_min"],
        "robustness: summary.noise_min совпадает",
    )

# --------------------------------------------------- прямая пересадка (вперёд)
fwd = load("basin_crossinit_exploratory.json")
if fwd:
    rows = fwd["rows"]
    check(len(rows) == 64, f"прямая пересадка: {len(rows)} строк")
    per_source = Counter(r["source_class"] for r in rows)
    check(
        per_source == Counter(
            {"struct_1": 16, "uniform_dark": 16, "uniform_bright": 16, "struct_2": 16}
        ),
        f"прямая пересадка: 16 строк на каждый источник ({dict(per_source)})",
    )
    check(
        all(r["final_class"] == "struct_2" for r in rows),
        "прямая пересадка: все финалы в struct_2",
    )
    check(
        all((r["stability_last_quarter"] or 0) >= 0.99 for r in rows),
        "прямая пересадка: устойчивость последней четверти >= 0.99",
    )
    for family, expected in (
        ("WP4_R-9_s2000_seed101", "struct_1"),
        ("WP4_R-9_s2000_seed202", "uniform_dark"),
        ("WP4_R-9_s2000_seed303", "uniform_bright"),
    ):
        check(
            fwd["sources"][family]["expected_class"] == expected,
            f"прямая пересадка: метаданные источника {family} -> {expected}",
        )
    for name, group in (
        ("struct_1", [r for r in rows if r["source_class"] == "struct_1"]),
        ("uniform_dark", [r for r in rows if r["source_class"] == "uniform_dark"]),
        ("uniform_bright", [r for r in rows if r["source_class"] == "uniform_bright"]),
        ("struct_2", [r for r in rows if r["source_class"] == "struct_2"]),
    ):
        summary = fwd["summary"][name]
        check(summary["n"] == len(group), f"прямая пересадка: {name} n={len(group)}")
        check(
            summary["final_class_counts"] == dict(Counter(r["final_class"] for r in group)),
            f"прямая пересадка: {name} финальные классы сходятся",
        )
        check(
            abs(summary["return_step_median"] - median(
                [r["return_step_to_struct_2"] for r in group]
            )) < 1e-9,
            f"прямая пересадка: медиана шага возврата {name} сходится",
        )

# ------------------------------------------------- обратная пересадка (назад)
rev = load("basin_reverse_exploratory.json")
if rev:
    rows = rev["rows"]
    check(len(rows) == 48, f"обратная пересадка: {len(rows)} строк")
    for family, home_class, outcome in (
        ("WP4_R-9_s2000_seed101", "struct_1", "death"),
        ("WP4_R-9_s2000_seed202", "uniform_dark", "uniform_dark"),
        ("WP4_R-9_s2000_seed303", "uniform_bright", "uniform_bright"),
    ):
        group = [r for r in rows if r["destination_family"] == family]
        counts = Counter(r["final_class"] for r in group)
        check(len(group) == 16, f"обратная пересадка: {family} — {len(group)} строк")
        check(
            counts == Counter({outcome: 16}),
            f"обратная пересадка: {family} -> {outcome} (16/16), получено {dict(counts)}",
        )
        check(
            all((r["stability_last_quarter"] or 0) >= 0.99 for r in group),
            f"обратная пересадка: {family} устойчивость >= 0.99",
        )
        if outcome == "death":
            check(
                all(r["alive_fraction"] == 0.0 for r in group),
                f"обратная пересадка: {family} — поле мертво (alive=0)",
            )
        summary = rev["summary"][home_class]
        check(
            summary["own_class_n"] == sum(1 for r in group if r["final_class"] == home_class),
            f"обратная пересадка: сводка {home_class} own_class_n сходится",
        )

# ------------------------------------------------------- матрица переходов
matrix = load("transition_matrix_exploratory.json")
if matrix:
    rows = matrix["rows"]
    check(len(rows) == 144, f"матрица: {len(rows)} строк")
    pairs = {(r["target_family"], r["source_family"]) for r in rows}
    check(len(pairs) == 144, f"матрица: {len(pairs)} уникальных пар")
    check(sum(1 for r in rows if r["diagonal"]) == 12, "матрица: 12 диагональных пар")
    per_target = Counter(r["target_family"] for r in rows)
    check(
        len(per_target) == 12 and set(per_target.values()) == {12},
        f"матрица: по 12 строк на каждую модель ({dict(per_target)})",
    )
    conflicts = [r for r in rows if r["class_alive_conflict"]]
    check(
        len(conflicts) == len(matrix["summary"]["class_alive_conflicts"]),
        f"матрица: конфликт класс/alive = {len(conflicts)}",
    )
    for family, summary in matrix["targets"].items():
        group = [r for r in rows if r["target_family"] == family]
        live_group = [
            r for r in group
            if r["source_alive_fraction"] >= LIVE_SOURCE_ALIVE
            and r["source_state_class"] != "death"
        ]
        effective = Counter(
            "death" if r["alive_fraction"] < DEAD_ALIVE else r["final_class"]
            for r in group
        )
        live_counts = Counter(
            "death" if r["alive_fraction"] < DEAD_ALIVE else r["final_class"]
            for r in live_group
        )
        distinct = {c for c in live_counts if c in LIVE_CLASSES}
        if not live_group:
            verdict = "no_live_source"
        elif live_counts.get("death", 0) == len(live_group):
            verdict = "killer"
        elif len(distinct) == 1:
            verdict = "single_live_attractor"
        elif sum(1 for c in distinct if live_counts[c] >= 2) >= 2:
            verdict = "multi_basin_candidate"
        else:
            verdict = "mixed"
        diag = next(r for r in group if r["diagonal"])
        diag_ok = (
            diag["final_class"] == summary["home_class"]
            and (diag["stability_last_quarter"] or 0) >= 0.75
        )
        if not diag_ok:
            verdict = "diagonal_unstable"
        check(
            summary["verdict"] == verdict,
            f"матрица: вердикт {family} = {verdict}",
        )
        check(
            summary["effective_class_counts"] == dict(effective),
            f"матрица: эффективные классы {family} сходятся",
        )
        check(
            summary["live_source_final_counts"] == dict(live_counts),
            f"матрица: исходы живых источников {family} сходятся",
        )
    check(
        not matrix["summary"]["multi_basin_candidates"],
        f"матрица: кандидатов на мультистабильность нет "
        f"({matrix['summary']['multi_basin_candidates']})",
    )

# --------------------------------------------------------- мультистабильность
r11 = load("r11_bistability_exploratory.json")
if r11:
    a, b, c = r11["phase_a_own_start"], r11["phase_b_foreign"], r11["phase_c_own_final"]
    check(len(a) == 16, f"R-11 фаза A: {len(a)} строк")
    check(len(b) == 16, f"R-11 фаза B: {len(b)} строк")
    check(len(c) == 4, f"R-11 фаза C: {len(c)} строк")
    summary = r11["summary"]
    check(
        summary["phase_a_final_counts"] == dict(Counter(r["final_class"] for r in a)),
        "R-11: финальные классы фазы A сходятся",
    )
    check(
        summary["phase_b_final_counts"] == dict(Counter(r["final_class"] for r in b)),
        "R-11: финальные классы фазы B сходятся",
    )
    check(
        summary["phase_c_final_counts"] == dict(Counter(r["final_class"] for r in c)),
        "R-11: финальные классы фазы C сходятся",
    )
    check(
        summary["phase_a_matches_census"] == sum(1 for r in a if r["matches_census"]),
        "R-11: сверка с census по фаза A",
    )
    stable = [
        r for r in a + b + c
        if r["final_class"] == "struct_1"
        and r["alive_fraction"] >= DEAD_ALIVE
        and (r["stability_last_quarter"] or 0) >= 0.75
    ]
    if len(stable) >= 2:
        verdict = "bistable"
    elif any(r["had_struct_1_anywhere"] for r in a + b + c):
        verdict = "transient_only"
    else:
        verdict = "single_attractor"
    check(summary["verdict"] == verdict, f"R-11: вердикт = {verdict}")

# --------------------------------------------------- отложенные сиды, горизонт
held = load("heldout_seeds_exploratory.json")
if held:
    runs = held["runs"]
    check(len(runs) == 128, f"отложенные сиды: {len(runs)} прогонов")
    per_family = Counter(r["family"] for r in runs)
    check(
        len(per_family) == 2 and set(per_family.values()) == {64},
        f"отложенные сиды: по 64 на модель ({dict(per_family)})",
    )
    check(
        sorted({r["seed"] for r in runs}) == list(range(64, 128)),
        "отложенные сиды: сетка 64–127",
    )
    for family, group in (
        ("WP4_R-9_s2000_seed42", [r for r in runs if r["family"] == "WP4_R-9_s2000_seed42"]),
        ("WP4_R-9_s2000_seed101", [r for r in runs if r["family"] == "WP4_R-9_s2000_seed101"]),
    ):
        counts = Counter(r["class_name"] for r in group)
        expected = "struct_2" if family.endswith("42") else "struct_1"
        check(
            counts == Counter({expected: 64}),
            f"отложенные сиды: {family} -> {expected} 64/64, получено {dict(counts)}",
        )
        check(
            all((r["stability_last_quarter"] or 0) >= 0.99 for r in group),
            f"отложенные сиды: {family} устойчивость >= 0.99",
        )

horizon = load("long_horizon_exploratory.json")
if horizon:
    runs = horizon["runs"]
    check(len(runs) == 16, f"горизонт: {len(runs)} прогонов")
    check(
        all(r["final_class"] == "struct_2" for r in runs),
        "горизонт: все финалы в struct_2",
    )
    check(
        all((r["stability_last_quarter"] or 0) >= 0.99 for r in runs),
        "горизонт: устойчивость >= 0.99",
    )
    for r in runs:
        for step in (2000, 4000, 6000):
            check(
                r["class_at_step"].get(str(step), r["class_at_step"].get(step)) == "struct_2",
                f"горизонт: seed {r['seed']} на {step} шагов — struct_2",
            )
    check(
        horizon["summary"]["class_counts"] == dict(Counter(r["final_class"] for r in runs)),
        "горизонт: сводка классов сходится",
    )

print("\n=== СВОДКА ===")
print("errors", len(errors), "warnings", len(warnings))
for e in errors:
    print("ERR", e)
for w in warnings:
    print("WARN", w)
raise SystemExit(1 if errors else 0)
