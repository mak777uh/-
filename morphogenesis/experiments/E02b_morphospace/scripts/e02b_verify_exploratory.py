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

# ------------------------------------------- повтор матрицы (с повторами)
rep = load("transition_matrix_rep_exploratory.json")
if rep:
    rows = rep["rows"]
    n_sources = len(rep["source_seeds"])
    n_noise = len(rep["noise_seeds"])
    expected_rows = 12 * n_sources * 12 * n_noise
    check(
        len(rows) == expected_rows,
        f"повтор матрицы: {len(rows)} строк (ожидалось {expected_rows})",
    )
    keys = {
        (r["target_family"], r["source_family"], r["source_seed"], r["noise_seed"])
        for r in rows
    }
    check(
        len(keys) == len(rows),
        f"повтор матрицы: {len(keys)} уникальных четвёрок из {len(rows)}",
    )
    per_pair = Counter((r["target_family"], r["source_family"]) for r in rows)
    check(
        len(per_pair) == 144 and set(per_pair.values()) == {n_sources * n_noise},
        f"повтор матрицы: по {n_sources * n_noise} выборок на каждую из 144 пар",
    )
    per_target = Counter(r["target_family"] for r in rows)
    check(
        len(per_target) == 12 and len(set(per_target.values())) == 1,
        f"повтор матрицы: по {list(per_target.values())[0]} строк на каждую модель",
    )
    conflicts = [r for r in rows if r["class_alive_conflict"]]
    check(
        len(conflicts) == len(rep["summary"]["class_alive_conflicts"]),
        f"повтор матрицы: конфликт класс/alive = {len(conflicts)}",
    )
    for family, summary in rep["targets"].items():
        group = [r for r in rows if r["target_family"] == family]
        live_group = [
            r for r in group
            if r["source_alive_fraction"] >= LIVE_SOURCE_ALIVE
            and r["source_state_class"] != "death"
        ]
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
        else:
            strong = []
            for c in distinct:
                frac = live_counts[c] / len(live_group)
                stable_pair = False
                for src_family, p in summary["live_pairs"].items():
                    if (
                        p["dominant_class"] == c
                        and (p["pair_stable_fraction"] or 0) >= 0.5
                    ):
                        stable_pair = True
                if frac >= 0.1 and stable_pair:
                    strong.append(c)
            verdict = "multi_basin_candidate" if len(strong) >= 2 else "mixed"
        diag_rows = [r for r in group if r["diagonal"]]
        diag_ok = [
            r for r in diag_rows
            if r["final_class"] == summary["home_class"]
            and (r["stability_last_quarter"] or 0) >= 0.75
        ]
        if not (diag_rows and len(diag_ok) >= 8):
            verdict = "diagonal_unstable"
        check(
            summary["verdict"] == verdict,
            f"повтор матрицы: вердикт {family} = {verdict}",
        )
        check(
            summary["live_source_final_counts"] == dict(live_counts),
            f"повтор матрицы: исходы живых источников {family} сходятся",
        )
        check(
            summary["live_source_n"] == len(live_group),
            f"повтор матрицы: живых выборок {family} = {len(live_group)}",
        )
        # пересчёт устойчивости пары из строк
        for src_family, pair in summary["pairs"].items():
            sub = [
                r for r in group
                if r["source_family"] == src_family
            ]
            counts = Counter(
                "death" if r["alive_fraction"] < DEAD_ALIVE else r["final_class"]
                for r in sub
            )
            dominant, dominant_n = counts.most_common(1)[0]
            check(
                pair["dominant_class"] == dominant
                and pair["dominant_n"] == dominant_n
                and abs(pair["pair_consistency"] - dominant_n / len(sub)) < 1e-12,
                f"повтор матрицы: пара {family} <- {src_family} доминирующий "
                f"{dominant} {dominant_n}/{len(sub)}",
            )
    check(
        not rep["summary"]["multi_basin_candidates"],
        f"повтор матрицы: кандидатов на мультистабильность нет "
        f"({rep['summary']['multi_basin_candidates']})",
    )

# ------------------------------------------ повтор геометрической абляции
lesion_rep = load("geometric_lesion_rep_exploratory.json")
if lesion_rep:
    models = lesion_rep["models"]
    check(len(models) == 3, f"абляция-повтор: {len(models)} моделей")
    for entry in models:
        rows = entry["rows"]
        check(len(rows) == 72, f"абляция-повтор {entry['family']}: {len(rows)} строк")
        per_lesion = Counter(r["lesion"] for r in rows)
        check(
            len(per_lesion) == 6 and set(per_lesion.values()) == {12},
            f"абляция-повтор {entry['family']}: по 12 на каждое из 6 повреждений",
        )
        for name, stats in entry["by_lesion"].items():
            group = [r for r in rows if r["lesion"] == name]
            ious = sorted(r["final"]["iou"] for r in group)
            mid = len(ious) // 2
            expect = (
                float(ious[mid])
                if len(ious) % 2
                else 0.5 * (float(ious[mid - 1]) + float(ious[mid]))
            )
            check(
                abs(stats["iou_median"] - expect) < 1e-9,
                f"абляция-повтор {entry['family']}/{name}: медиана IoU сходится",
            )
            retained = sum(
                1 for r in group
                if r["final"]["assigned_class"] == entry["prototype_class"]
                and r["final"]["alive_fraction"] >= DEAD_ALIVE
            )
            check(
                stats["class_retained_n"] == retained,
                f"абляция-повтор {entry['family']}/{name}: сохранение класса сходится",
            )
        for axis_name, axis in entry["axes"].items():
            left, right = axis_name.split("_vs_")
            left_iou = {
                r["repeat"]: r["final"]["iou"] for r in rows if r["lesion"] == left
            }
            right_iou = {
                r["repeat"]: r["final"]["iou"] for r in rows if r["lesion"] == right
            }
            diffs = [
                left_iou[k] - right_iou[k]
                for k in sorted(set(left_iou) & set(right_iou))
            ]
            same_sign = max(sum(1 for d in diffs if d > 0), sum(1 for d in diffs if d < 0))
            mean_diff = sum(diffs) / len(diffs) if diffs else 0.0
            established = bool(same_sign >= 11 and abs(mean_diff) >= 0.05)
            check(
                axis["asymmetry_established"] == established,
                f"абляция-повтор {entry['family']}/{axis_name}: "
                f"асимметрия установлена = {established}",
            )
            check(
                axis["same_sign_n"] == same_sign
                and abs(axis["mean_diff_left_minus_right"] - mean_diff) < 1e-9,
                f"абляция-повтор {entry['family']}/{axis_name}: статистика оси сходится",
            )

# ------------------------------------------- нуклеогенез из живого очага
frag = load("fragment_nucleogenesis_exploratory.json")
if frag:
    models = frag["models"]
    rows = frag["rows"]
    check(len(models) == 3, f"очаг: {len(models)} модели")
    check(
        len(rows) == 3 * (2 * 5 * 12 + 12) + 2 * 12,
        f"очаг: {len(rows)} строк (3*(2*5*12+12) + 2*12)",
    )
    for entry in models:
        family = entry["family"]
        own = [r for r in rows if r["model"] == family and r["role"] == "own"]
        ctrl = [r for r in rows if r["model"] == family and r["role"] == "control"]
        check(len(ctrl) == 12, f"очаг {family}: контроль {len(ctrl)} строк")
        check(
            all(r["k"] == 0 for r in ctrl),
            f"очаг {family}: контроль — только k=0",
        )
        check(
            all(r["seed_cells"] == 0 for r in ctrl),
            f"очаг {family}: в контроле очаг пустой",
        )
        ctrl_alive = sum(1 for r in ctrl if r["final_alive"] >= DEAD_ALIVE)
        check(
            entry["control"]["alive_count"] == ctrl_alive,
            f"очаг {family}: контроль живых {ctrl_alive} сходится",
        )
        check(
            entry["control_failed"] == (ctrl_alive >= 11),
            f"очаг {family}: флаг control_failed корректен",
        )
        if ctrl_alive >= 11:
            warn(
                False,
                f"очаг {family}: контроль k=0 дал живых {ctrl_alive}/12 — тест недействителен",
            )
        per_cell = Counter((r["mode"], r["k"]) for r in own)
        check(
            len(per_cell) == 10 and set(per_cell.values()) == {12},
            f"очаг {family}: 10 ячеек (2 режима × 5 размеров) по 12 повторов",
        )
        broken = [r for r in own if r.get("error")]
        check(
            not broken,
            f"очаг {family}: очаг собрать не удалось в {len(broken)} строках",
        )
        for cell in entry["cells"]:
            group = [
                r for r in own
                if r["mode"] == cell["mode"] and r["k"] == cell["k"]
            ]
            check(
                len(group) == 12,
                f"очаг {family}/{cell['mode']}/k={cell['k']}: {len(group)} повторов",
            )
            nuc = [
                r for r in group
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == entry["prototype_class"]
                and r["alive_growth_ratio"] >= 0.5
            ]
            same = [r for r in nuc if r["iou_vs_prototype"] >= 0.5]
            check(
                cell["nucleogenesis_count"] == len(nuc),
                f"очаг {family}/{cell['mode']}/k={cell['k']}: "
                f"нуклеогенез {len(nuc)} сходится",
            )
            check(
                cell["same_pattern_count"] == len(same),
                f"очаг {family}/{cell['mode']}/k={cell['k']}: "
                f"тот же рисунок {len(same)} сходится",
            )
            check(
                cell["nucleogenesis_established"] == (len(nuc) >= 11),
                f"очаг {family}/{cell['mode']}/k={cell['k']}: флаг нуклеогенеза корректен",
            )
            check(
                cell["same_pattern_rebuilt"] == (len(same) >= 11),
                f"очаг {family}/{cell['mode']}/k={cell['k']}: флаг рисунка корректен",
            )
            check(
                cell["class_counts"] == dict(Counter(r["final_class"] for r in group)),
                f"очаг {family}/{cell['mode']}/k={cell['k']}: счётчики классов сходятся",
            )
        # порог по размеру пересчитывается из ячеек
        for mode in ("scattered", "compact"):
            cands = [
                c["k"] for c in entry["cells"]
                if c["mode"] == mode and c["nucleogenesis_established"]
            ]
            expect = min(cands) if cands else None
            check(
                entry["minimal_seed_size"][mode] == expect,
                f"очаг {family}/{mode}: минимальный зачаток {expect} сходится",
            )
            cands_same = [
                c["k"] for c in entry["cells"]
                if c["mode"] == mode and c["same_pattern_rebuilt"]
            ]
            expect_same = min(cands_same) if cands_same else None
            check(
                entry["minimal_seed_size_same_pattern"][mode] == expect_same,
                f"очаг {family}/{mode}: минимальный зачаток с рисунком {expect_same} сходится",
            )
    cross = frag.get("cross", [])
    check(len(cross) == 2, f"очаг: перекрёстный блок — {len(cross)} пары")
    for cb in cross:
        group = [
            r for r in rows
            if r["role"] == f"cross:{cb['source']}" and r["model"] == cb["target"]
        ]
        check(
            len(group) == 12,
            f"очаг cross {cb['target']}<-{cb['source']}: {len(group)} повторов",
        )
        check(
            cb["class_counts"] == dict(Counter(r["final_class"] for r in group)),
            f"очаг cross {cb['target']}<-{cb['source']}: счётчики классов сходятся",
        )

# ------------------------------------------- память формы: видимое или скрытое
chan_art = load("channel_memory_exploratory.json")
if chan_art:
    models = chan_art["models"]
    rows = chan_art["rows"]
    check(len(models) == 3, f"каналы: {len(models)} модели")
    check(len(rows) == 3 * 4 * 12, f"каналы: {len(rows)} строк (3*4*12)")
    for entry in models:
        family = entry["family"]
        group_all = [r for r in rows if r["model"] == family]
        per_cond = Counter(r["condition"] for r in group_all)
        check(
            len(per_cond) == 4 and set(per_cond.values()) == {12},
            f"каналы {family}: 4 условия по 12 повторов",
        )
        for cell in entry["conditions"]:
            cond = cell["condition"]
            group = [r for r in group_all if r["condition"] == cond]
            check(
                len(group) == 12,
                f"каналы {family}/{cond}: {len(group)} повторов",
            )
            alive_n = sum(1 for r in group if r["final_alive"] >= DEAD_ALIVE)
            class_n = sum(
                1
                for r in group
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == entry["prototype_class"]
            )
            pattern_n = sum(
                1
                for r in group
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == entry["prototype_class"]
                and r["iou_exact"] >= 0.5
            )
            phase_n = sum(
                1
                for r in group
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == entry["prototype_class"]
                and r["iou_shifted"] >= 0.5
            )
            orient_n = sum(
                1
                for r in group
                if r["final_alive"] >= DEAD_ALIVE
                and r["final_class"] == entry["prototype_class"]
                and r["iou_dihedral"] >= 0.5
            )
            check(cell["alive_n"] == alive_n, f"каналы {family}/{cond}: живых сходится")
            check(
                cell["class_recovered_n"] == class_n,
                f"каналы {family}/{cond}: класс восстановлен {class_n} сходится",
            )
            check(
                cell["same_pattern_n"] == pattern_n,
                f"каналы {family}/{cond}: тот же рисунок {pattern_n} сходится",
            )
            check(
                cell["same_phase_n"] == phase_n,
                f"каналы {family}/{cond}: та же фаза {phase_n} сходится",
            )
            check(
                cell["same_orientation_n"] == orient_n,
                f"каналы {family}/{cond}: та же ориентация {orient_n} сходится",
            )
            check(
                cell["class_recovered_established"] == (class_n >= 11),
                f"каналы {family}/{cond}: флаг класса корректен",
            )
            check(
                cell["same_pattern_established"] == (pattern_n >= 11),
                f"каналы {family}/{cond}: флаг рисунка корректен",
            )
            check(
                cell["same_phase_established"] == (phase_n >= 11),
                f"каналы {family}/{cond}: флаг фазы корректен",
            )
            check(
                cell["same_orientation_established"] == (orient_n >= 11),
                f"каналы {family}/{cond}: флаг ориентации корректен",
            )
            check(
                cell["class_counts"] == dict(Counter(r["final_class"] for r in group)),
                f"каналы {family}/{cond}: счётчики классов сходятся",
            )
        by_cond = {c["condition"]: c for c in entry["conditions"]}
        check(
            entry["control_ok"] == by_cond["none"]["class_recovered_established"],
            f"каналы {family}: флаг контроля корректен",
        )
        check(
            entry["visible_zeroed_recovers"]
            == by_cond["visible_zeroed"]["same_pattern_established"],
            f"каналы {family}: флаг visible_zeroed корректен",
        )
        check(
            entry["hidden_zeroed_recovers"]
            == by_cond["hidden_zeroed"]["same_pattern_established"],
            f"каналы {family}: флаг hidden_zeroed корректен",
        )
        check(
            entry["hidden_shuffled_recovers"]
            == by_cond["hidden_shuffled"]["same_pattern_established"],
            f"каналы {family}: флаг hidden_shuffled корректен",
        )
        check(
            entry["memory_in_hidden_channels"]
            == (
                by_cond["visible_zeroed"]["same_pattern_established"]
                and not by_cond["hidden_zeroed"]["same_pattern_established"]
            ),
            f"каналы {family}: флаг памяти в скрытых корректен",
        )
        check(
            entry["rederivable_from_visible"]
            == by_cond["hidden_zeroed"]["same_pattern_established"],
            f"каналы {family}: флаг выводимости из видимого корректен",
        )
        check(
            entry["hidden_layout_matters"]
            == (
                by_cond["none"]["same_pattern_established"]
                and not by_cond["hidden_shuffled"]["same_pattern_established"]
            ),
            f"каналы {family}: флаг укладки скрытого корректен",
        )
        # alive-канал не трогаем никогда — иначе тест был бы тривиальным
        check(
            chan_art["channels"]["alive"] == 1
            and chan_art["channels"]["visible"] == 0,
            "каналы: раскладка каналов верна (visible=0, alive=1)",
        )

# ------------------------------------------ транзиторные классы на карте
transient_art = load("transient_class_analysis_exploratory.json")
if transient_art:
    census_path = EXP / "census.json"
    if census_path.exists():
        census = json.load(open(census_path, encoding="utf-8"))
        cruns = census["runs"]
        check(
            transient_art["n_runs"] == len(cruns),
            f"транзитор: прогонов {transient_art['n_runs']} (перепись {len(cruns)})",
        )
        classes = list(transient_art["per_class"].keys())
        for cls in classes:
            pc = transient_art["per_class"][cls]
            with_cls = sorted(
                {
                    r["family"]
                    for r in cruns
                    if cls in (r.get("trajectory_class") or [])
                }
            )
            check(
                pc["families_with_class"] == len(with_cls),
                f"транзитор {cls}: семейств {len(with_cls)} сходится",
            )
            check(
                sorted(pc["family_list"]) == with_cls,
                f"транзитор {cls}: список семейств сходится",
            )
            transient_only = sorted(
                f
                for f in with_cls
                if not any(
                    r["family"] == f and r["class_name"] == cls for r in cruns
                )
            )
            check(
                sorted(pc["transient_only_families"]) == transient_only,
                f"транзитор {cls}: только транзиторные семейства сходятся",
            )
            check(
                pc["exclusive"] == (len(with_cls) == 1 and not transient_only),
                f"транзитор {cls}: флаг эксклюзивности корректен",
            )
        exclusive = transient_art["summary"]["exclusive_classes"]
        exclusive_structural = [c for c in exclusive if c.startswith("struct_")]
        check(
            exclusive_structural == ["struct_2"],
            f"транзитор: эксклюзивный СТРУКТУРНЫЙ класс — {exclusive_structural} "
            f"(весь эксклюзивный набор: {exclusive})",
        )
        check(
            "struct_1" not in exclusive and transient_art["per_class"]["struct_1"][
                "universal"
            ],
            "транзитор: struct_1 универсален (общий, не специфичный)",
        )
        check(
            transient_art["summary"]["struct_2_families"]
            == ["WP4_R-9_s2000_seed42"],
            "транзитор: struct_2 принадлежит ровно одному семейству",
        )
        check(
            transient_art["summary"]["struct_2_transient_only_families"] == [],
            "транзитор: struct_2 нигде не встречается только транзиторно",
        )

# ------------------------------------------ generic-класс: расстояния в z-пространстве
generic_art = load("generic_class_distance_exploratory.json")
if generic_art:
    import numpy as _np

    census_path = EXP / "census.json"
    if census_path.exists():
        import sys as _sys

        # EXP = <repo>/morphogenesis/experiments/E02b_morphospace,
        # EXP.parents[1] = <repo>/morphogenesis — там лежит e02b_morphospace.py
        _sys.path.insert(0, str(EXP.parents[1]))
        import e02b_morphospace as e02b  # noqa: E402

        census = json.load(open(census_path, encoding="utf-8"))
        cl = census["clustering"]
        _mean = _np.asarray(cl["scaler_mean"])
        _std = _np.asarray(cl["scaler_std"])
        _valid = cl["labels_valid"]
        _names = {int(c): str(n) for c, n in zip(_valid, cl["class_names"], strict=True)}

        def _z(vec):
            return (_np.asarray(vec, dtype=_np.float64) - _mean) / _std

        _by = {int(c): [] for c in _valid}
        _ctrl = {}
        for _r in census["runs"]:
            _v = _z(e02b.descriptor_vector(_r["final"]))
            if _r.get("is_control"):
                _ctrl.setdefault(str(_r.get("family")), []).append(_v)
                continue
            _cid = int(_r["cluster"])
            if _cid in _by:
                _by[_cid].append(_v)
        _cent = _np.vstack([_np.asarray(_by[int(c)]).mean(axis=0) for c in _valid])
        _classes = [_names[int(c)] for c in _valid]
        _unt = _np.vstack(_ctrl["untrained_current_arch"])
        for _cname in ("struct_1", "struct_2"):
            _i = _classes.index(_cname)
            _own = float(_np.linalg.norm(_unt - _cent[_i], axis=1).mean())
            _spread = float(
                _np.linalg.norm(_np.vstack(_by[int(_valid[_i])]) - _cent[_i], axis=1).mean()
            )
            _stored = generic_art["classes"][_cname]
            check(
                abs(_stored[f"distance_to_untrained_current_arch"] - _own) < 1e-6,
                f"generic: {_cname} — расстояние от облака необученной сходится ({_own:.3f})",
            )
            check(
                abs(_stored["within_class_spread"] - _spread) < 1e-6,
                f"generic: {_cname} — внутриклассовый разброс сходится ({_spread:.3f})",
            )
            _verdict = "generic" if _own <= 2.0 * _spread else "learned"
            check(
                _stored["generic_verdict"]["verdict"] == _verdict,
                f"generic: {_cname} — вердикт {_verdict}",
            )
        check(
            generic_art["summary"]["generic_structural_classes"] == ["struct_1"],
            "generic: struct_1 — единственный generic-класс",
        )
        check(
            generic_art["summary"]["learned_structural_classes"] == ["struct_2"],
            "generic: struct_2 — единственный выученный структурный класс",
        )
    else:
        warn(False, "generic: нет census.json для независимого пересчёта")

# ------------------------------------------ геометрия формы: независимый пересчёт
geom_art = load("geometry_of_form_exploratory.json")
if geom_art:
    import numpy as _np

    census_path = EXP / "census.json"
    if census_path.exists():
        census = json.load(open(census_path, encoding="utf-8"))
        gruns = census["runs"]

        def _gvals(rows, axis):
            return _np.asarray(
                [float(r["final"].get(axis, 0.0)) for r in rows], dtype=_np.float64
            )

        def _gprof(rows):
            return _np.asarray(
                [r["final"].get("radial_profile") or [] for r in rows], dtype=_np.float64
            )

        def _separated(a, b):
            if a.size == 0 or b.size == 0:
                return False
            return bool(a.max() < b.min() or b.max() < a.min())

        def _verdict(n):
            if n >= 3:
                return "geometrically_distinct"
            if n >= 1:
                return "partially_distinct"
            return "not_distinct"

        _untrained = "untrained_current_arch"
        _gdefs = {
            "struct_2": [r for r in gruns if r["class_name"] == "struct_2"],
            "struct_1": [r for r in gruns if r["class_name"] == "struct_1"],
            "uniform_dark": [r for r in gruns if r["class_name"] == "uniform_dark"],
            "struct_1_untrained": [
                r
                for r in gruns
                if r["class_name"] == "struct_1" and r["family"] == _untrained
            ],
            "struct_1_learned": [
                r
                for r in gruns
                if r["class_name"] == "struct_1" and not r.get("is_control")
            ],
        }
        _gcontrasts = {
            "C1_struct2_vs_struct1": ("struct_2", "struct_1"),
            "C2_struct2_vs_uniform_dark": ("struct_2", "uniform_dark"),
            "C3_struct1_untrained_vs_learned": (
                "struct_1_untrained",
                "struct_1_learned",
            ),
            "C4_struct2_vs_struct1_untrained": ("struct_2", "struct_1_untrained"),
        }
        _axes_a = geom_art["rules"]["axes_A"]
        _axes_b = geom_art["rules"]["axes_B"]
        _axes_strict = geom_art["rules"]["axes_A_strict"]
        for _cname, (_ga, _gb) in _gcontrasts.items():
            _ca = geom_art["contrasts"][_cname]
            _ra, _rb = _gdefs[_ga], _gdefs[_gb]
            check(
                _ca["n_a"] == len(_ra) and _ca["n_b"] == len(_rb),
                f"геометрия {_cname}: размеры групп сходятся",
            )
            _sep_a = []
            for _ax in _axes_a:
                if _separated(_gvals(_ra, _ax), _gvals(_rb, _ax)):
                    _sep_a.append(_ax)
            _sep_b = []
            for _ax in _axes_b:
                if _separated(_gvals(_ra, _ax), _gvals(_rb, _ax)):
                    _sep_b.append(_ax)
            _pa, _pb = _gprof(_ra), _gprof(_rb)
            if _pa.size and _pb.size:
                _ma, _mb = _pa.mean(axis=0), _pb.mean(axis=0)
                _ok = bool(
                    (
                        0.5 * _np.abs(_pa - _ma).sum(axis=1)
                        < 0.5 * _np.abs(_pa - _mb).sum(axis=1)
                    ).all()
                    and (
                        0.5 * _np.abs(_pb - _mb).sum(axis=1)
                        < 0.5 * _np.abs(_pb - _ma).sum(axis=1)
                    ).all()
                )
            else:
                _ok = False
            if _ok:
                _sep_b.append("radial_profile")
            check(
                sorted(_ca["separated_A"]) == sorted(_sep_a),
                f"геометрия {_cname}: разделённые оси уровня A сходятся "
                f"({len(_sep_a)})",
            )
            check(
                sorted(_ca["separated_B"]) == sorted(_sep_b),
                f"геометрия {_cname}: разделённые оси уровня B сходятся "
                f"({len(_sep_b)})",
            )
            check(
                _ca["verdict_A"] == _verdict(len(_sep_a)),
                f"геометрия {_cname}: вердикт A = {_verdict(len(_sep_a))}",
            )
            _sep_strict = [
                _ax for _ax in _axes_strict if _ax in set(_sep_a) | set(_sep_b)
            ]
            check(
                _ca["n_separated_A_strict"] == len(_sep_strict),
                f"геометрия {_cname}: строгий набор разделён ({len(_sep_strict)})",
            )
            check(
                _ca["verdict_A_strict"] == _verdict(len(_sep_strict)),
                f"геометрия {_cname}: строгий вердикт = {_verdict(len(_sep_strict))}",
            )
        # Ключевые содержательные утверждения, которые должны быть верны.
        _c4 = geom_art["contrasts"]["C4_struct2_vs_struct1_untrained"]
        _c3 = geom_art["contrasts"]["C3_struct1_untrained_vs_learned"]
        check(
            _c4["verdict_A_strict"] == "geometrically_distinct",
            "геометрия: struct_2 геометрически отличен от struct_1 необученной сети",
        )
        check(
            _c3["verdict_A_strict"] == "not_distinct",
            "геометрия: struct_1 выученных и необученной сетей геометрически совпадают",
        )
        _gp = geom_art["group_profiles"]
        check(
            _gp["struct_2"]["median_alive_b0"] == 1,
            "геометрия: struct_2 — одно связное тело (alive_b0 = 1)",
        )
        check(
            _gp["struct_1"]["median_alive_b0"] > 10,
            f"геометрия: struct_1 — россыпь "
            f"(alive_b0 = {_gp['struct_1']['median_alive_b0']:.0f})",
        )
        check(
            _gp["struct_2"]["median_outer_occupancy"]
            > _gp["struct_1"]["median_outer_occupancy"],
            "геометрия: у struct_2 масса плотнее у края, чем у struct_1",
        )
    else:
        warn(False, "геометрия: нет census.json для независимого пересчёта")

# ------------------------------------------ прочность тела (E06)
integrity = load("body_integrity_exploratory.json")
if integrity:
    import numpy as _np

    _models = integrity["models"]
    check(
        len(_models) == 3,
        f"прочность: {len(_models)} модели",
    )
    _fracs = integrity["fractions"]
    _repeats = integrity["repeats"]
    for _entry in _models:
        _fam = _entry["family"]
        _rows = _entry["rows"]
        check(
            len(_rows) == len(_fracs) * _repeats,
            f"прочность {_fam}: {len(_rows)} строк "
            f"(ожидалось {len(_fracs) * _repeats})",
        )
        _by = {}
        for _r in _rows:
            _by.setdefault(_r["fraction"], []).append(_r)
        check(
            sorted(_by) == sorted(_fracs),
            f"прочность {_fam}: набор долей сходится",
        )
        for _f in _fracs:
            _g = _by.get(_f, [])
            _bf = _entry["by_fraction"][str(_f)]
            _surv = [
                _r
                for _r in _g
                if _r["final"]["assigned_class"] == _entry["prototype_class"]
                and _r["final"]["alive_fraction"] >= DEAD_ALIVE
            ]
            check(
                _bf["n"] == len(_g),
                f"прочность {_fam}/p={_f}: {len(_g)} повторов",
            )
            check(
                _bf["n_survived"] == len(_surv),
                f"прочность {_fam}/p={_f}: выжило {len(_surv)} сходится",
            )
            check(
                _bf["median_alive"] == median([_r["final"]["alive_fraction"] for _r in _g]),
                f"прочность {_fam}/p={_f}: медиана alive сходится",
            )
            check(
                _bf["median_iou"] == median([_r["final"]["iou"] for _r in _g]),
                f"прочность {_fam}/p={_f}: медиана IoU сходится",
            )
            check(
                _bf["median_alive_b0_survived"]
                == median([_r["final"]["alive_b0"] for _r in _surv]),
                f"прочность {_fam}/p={_f}: медиана alive_b0 сходится",
            )
            _ma = _bf["median_alive"]
            _tol = bool(
                len(_surv) >= 11
                and _ma is not None
                and _ma >= 0.5 * _entry["prototype_alive_fraction"]
            )
            check(
                _bf["tolerance_established"] == _tol,
                f"прочность {_fam}/p={_f}: флаг прочности корректен",
            )
        _est = [f for f in _fracs if _entry["by_fraction"][str(f)]["tolerance_established"]]
        _t = max(_est) if _est else 0.0
        check(
            _entry["tolerance"] == _t,
            f"прочность {_fam}: прочность {_t} сходится",
        )
    # Вердикт пересчитывается из прочностей.
    _tols = {e["family"]: e["tolerance"] for e in _models}
    _s2 = next(e for e in _models if e["expected_class"] == "struct_2")
    _others = [e for e in _models if e["expected_class"] != "struct_2"]
    if all(abs(_tols[e["family"]] - _tols[_s2["family"]]) < 1e-9 for e in _others):
        _verdict = "tolerance_architectural"
    elif (
        all(_tols[_s2["family"]] > _tols[e["family"]] + 1e-9 for e in _others)
        and int(
            integrity["summary"]["struct_2_median_alive_b0_at_tolerance"] or 0
        )
        == 1
    ):
        _verdict = "struct_2_superior"
    else:
        _verdict = "mixed"
    check(
        integrity["summary"]["verdict"] == _verdict,
        f"прочность: вердикт {_verdict} сходится",
    )
    check(
        integrity["summary"]["tolerances"] == _tols,
        "прочность: таблица прочностей сходится",
    )
    # Содержательная проверка: при нулевом повреждении поле должно остаться живым.
    for _entry in _models:
        _g0 = [_r for _r in _entry["rows"] if _r["fraction"] == 0.0]
        _alive0 = sum(1 for _r in _g0 if _r["final"]["alive_fraction"] >= DEAD_ALIVE)
        check(
            _alive0 == len(_g0),
            f"прочность {_entry['family']}: контроль p=0 — поле живо "
            f"в {_alive0}/{len(_g0)}",
        )

# ------------------------------------------ замороженные центроиды классов
frozen = load("class_centroids_frozen.json")
if frozen:
    # Проверка НЕ импортирует e02b: считаем проекцию вручную, чистым питоном,
    # чтобы файл центроидов проверялся сам по себе, а не тем же кодом, который
    # его создал.
    _feats = list(frozen["features"])
    _mean = [float(v) for v in frozen["scaler_mean"]]
    _std = [float(v) for v in frozen["scaler_std"]]
    _cent = [[float(v) for v in row] for row in frozen["centroids_z"]]
    _valid = [int(v) for v in frozen["labels_valid"]]
    _names = list(frozen["class_names"])
    check(
        len(_feats) == 18,
        f"центроиды: {len(_feats)} признаков (ожидалось 18)",
    )
    check(
        len(_mean) == len(_feats) and len(_std) == len(_feats),
        "центроиды: размеры скалера совпадают с числом признаков",
    )
    check(
        all(len(row) == len(_feats) for row in _cent),
        "центроиды: размеры центроидов совпадают с числом признаков",
    )
    check(
        len(_cent) == len(_valid) == len(_names),
        "центроиды: число центроидов, меток и имён совпадает",
    )
    check(
        len(set(_valid)) == len(_valid),
        "центроиды: метки уникальны",
    )
    # Пересчёт проекции на сырых дескрипторах из census.json: у каждого
    # прогона должен получиться ровно тот класс, который записан в census.
    _census_path = EXP / "census.json"
    if _census_path.exists():
        _census = json.load(open(_census_path, encoding="utf-8"))
        _runs = _census["runs"]
        _name_by_label = {lab: nm for lab, nm in zip(_valid, _names)}
        _mismatch = []
        _checked = 0
        for _run in _runs:
            _fin = _run["final"]
            _x = [float(_fin.get(k, 0.0)) for k in _feats]
            _z = [(_x[i] - _mean[i]) / (_std[i] if _std[i] else 1.0) for i in range(len(_feats))]
            _best = None
            _bestd = None
            for _ci, _row in enumerate(_cent):
                _d = sum((_z[i] - _row[i]) ** 2 for i in range(len(_feats)))
                if _bestd is None or _d < _bestd:
                    _bestd = _d
                    _best = _ci
            _got = _name_by_label.get(_valid[_best], "outlier")
            _checked += 1
            if _got != _run.get("class_name"):
                _mismatch.append((_run.get("family"), _run.get("seed"), _got, _run.get("class_name")))
        check(
            _checked == len(_runs),
            f"центроиды: проверено {_checked} прогонов переписи",
        )
        check(
            not _mismatch,
            f"центроиды: проекция воспроизводит класс census у всех прогонов "
            f"(расхождений: {len(_mismatch)})",
        )
        if _mismatch:
            print("     первые расхождения:", _mismatch[:5])
    check(
        frozen["refit_verification"]["all_fields_match"] is True,
        "центроиды: пересборка кластеризации совпала с census.json",
    )
    check(
        frozen["k"] == 5 and frozen["sizes"] == [67, 320, 189, 64, 64],
        f"центроиды: k={frozen['k']}, размеры {frozen['sizes']}",
    )
    check(
        frozen["class_names"] == _census["clustering"]["class_names"],
        "центроиды: имена классов совпадают с census.json",
    )
    _sha = frozen["source_census"]["sha256"]
    _actual = __import__("hashlib").sha256(_census_path.read_bytes()).hexdigest()
    check(
        _sha == _actual,
        "центроиды: sha256 census.json совпадает с записанным",
    )

# ------------------------------------------------- происхождение чекпоинтов
prov = load("checkpoint_provenance_exploratory.json")
if prov:
    import hashlib
    import re

    REPO = HERE.parents[4]
    rows = prov["checkpoints"]
    check(
        len(rows) == 12,
        f"происхождение: чекпоинтов в артефакте {len(rows)} (ожидалось 12)",
    )
    # Хеш весов попарно различный: значит это 12 разных обучений, а не
    # один файл, скопированный 12 раз.
    _wh = [r["weights_sha256"] for r in rows]
    check(
        len(set(_wh)) == len(_wh),
        f"происхождение: различных наборов весов {len(set(_wh))}/{len(_wh)}",
    )
    # Метаданные проговаривают то же, что и имя семейства.
    _meta_bad = []
    for r in rows:
        m = re.match(r"^WP4_(?P<arm>.+?)_s(?P<steps>\d+)_seed(?P<seed>\d+)$", r["family"])
        if not m:
            _meta_bad.append((r["family"], "имя семьи не разобрано"))
            continue
        if r["payload_seed"] != int(m.group("seed")):
            _meta_bad.append((r["family"], f"seed {r['payload_seed']}"))
        if r["payload_iteration"] != int(m.group("steps")):
            _meta_bad.append((r["family"], f"iteration {r['payload_iteration']}"))
        if r["metadata_experiment"] != r["family"]:
            _meta_bad.append((r["family"], f"experiment {r['metadata_experiment']}"))
        if r["metadata_spec_version"] != r["payload_spec_version"]:
            _meta_bad.append((r["family"], "spec_version"))
    check(
        not _meta_bad,
        f"происхождение: метаданные согласованы с именем семейства "
        f"(расхождений: {len(_meta_bad)})",
    )
    if _meta_bad:
        print("     первые расхождения:", _meta_bad[:5])
    # Группы одинакового лосса пересчитываются из строк.
    _groups = {}
    for r in rows:
        _groups.setdefault(f"{r['payload_loss']:.17g}", []).append(r["family"])
    _groups = {k: sorted(v) for k, v in sorted(_groups.items())}
    _artifact_groups = {k: v["families"] for k, v in prov["loss_groups"].items()}
    check(
        _groups == _artifact_groups,
        f"происхождение: группы одинакового лосса пересчитаны и совпали "
        f"({len(_groups)} групп)",
    )
    # Байт-хеш файлов пересчитывается независимо (hashlib, без torch).
    _index_path = REPO / "lab" / "checkpoints.json"
    _index = json.load(open(_index_path, encoding="utf-8")) if _index_path.exists() else {}
    _index_sha = {
        e["path"]: e.get("sha256")
        for e in _index.get("entries", [])
        if "E02b_morphospace" in (e.get("canonical_for") or [])
    }
    _missing = []
    _bad_hash = []
    _bad_index = []
    for r in rows:
        _path = REPO / r["path"]
        if not _path.exists():
            _missing.append(r["path"])
            continue
        _h = hashlib.sha256()
        with _path.open("rb") as _fh:
            for _chunk in iter(lambda: _fh.read(1 << 20), b""):
                _h.update(_chunk)
        if _h.hexdigest() != r["file_sha256"]:
            _bad_hash.append(r["family"])
        if _index_sha.get(r["path"]) != r["file_sha256"]:
            _bad_index.append(r["family"])
    if _missing:
        warn(
            False,
            f"происхождение: на диске нет {len(_missing)} канонических чекпоинтов — "
            "проверка байт-хешей пропущена (веса в git не входят)",
        )
    else:
        check(
            not _bad_hash,
            f"происхождение: байт-хеш каждого файла пересчитан и совпал "
            f"(расхождений: {len(_bad_hash)})",
        )
        check(
            not _bad_index,
            f"происхождение: хеши совпадают с lab/checkpoints.json "
            f"(расхождений: {len(_bad_index)})",
        )
    check(
        prov["summary"]["file_integrity_ok"] is True
        and prov["summary"]["metadata_consistent"] is True
        and prov["summary"]["weights_pairwise_distinct"] is True
        and not prov["summary"]["issues"],
        "происхождение: сводка артефакта без замечаний",
    )

print("\n=== СВОДКА ===")
print("errors", len(errors), "warnings", len(warnings))
for e in errors:
    print("ERR", e)
for w in warnings:
    print("WARN", w)
raise SystemExit(1 if errors else 0)
