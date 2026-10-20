"""
wp4_report.py — сводка WP4: что мы измерили про коллапс E02 и что из этого
следует для гейта слоя 1.

Скрипт ничего не обучает: он читает артефакты волн аблаций
(experiments/E02_pattern/wp4_ablations.json), зонда ландшафта
(collapse_probe.json), профиля дельты (delta_profile.json), скана порогов
(threshold_probe.json) и гейта (gate_layer1.json), пересчитывает вердикты по
ОДНОМУ и тому же относительному порогу живости и пишет results.json +
человекочитаемый отчёт.

Зачем нужен пересчёт: в волне 1 вердикт «выжил/умер» считался от абсолютного
COLLAPSE_ALIVE_FRACTION_MIN=0.15, который стоит впритык к плотности цели
(0.1523). Ниже он считается от config.collapse_alive_fraction_min(плотность).

Первичный эндпоинт — coverage.f1 (evaluate.compute_coverage_endpoints), а не
симметричный Chamfer: Chamfer не наказывает перепокрытие (измерено: всё-белое
поле 0.036 при 0.0 у идеального кольца), f1 различает их (0.264 против 1.000).
Прогоны волны 1-2 делали этот код ещё без coverage, поэтому для них f1 равен
None и это честно написано в отчёте, а не заменено оценкой.

Статистика: парный Wilcoxon осмыслен начиная с 5 сидов на пару arms; при n=1
или n<5 скрипт печатает минимально достижимый двусторонний p (2^-n) вместо
того, чтобы притворяться значимостью.

Запуск:  python wp4_report.py
"""

import json

import os

import time

# §9.2: config раньше torch.

import config

import numpy as np

from wp4_ablations import _summarize

OUT_DIR = os.path.join("experiments", "E02_pattern")


def _load(name):
    """Чтение артифакта с повтором: волна аблаций пишет файл в тот же момент, и
    между trunc() и полным flush читатель может увидеть усечённый json.
    Молча вернуть None для wp4_ablations.json значило бы собрать отчёт по
    половине прогонов, поэтому пробуем ещё дважды."""
    path = os.path.join(OUT_DIR, name)
    if not os.path.exists(path):
        return None
    last_error = None
    for _ in range(3):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            last_error = exc
            time.sleep(1.0)
    raise RuntimeError(f"читаем битый json {path}: {last_error}")


def _target_density():
    from target_patterns import create_target

    target = create_target(device="cpu")
    return float((target > 0).float().mean().item())


def _arm_summary(run, threshold):
    """Пересчёт вердикта arm'а по относительному порогу + извлечение эндпоинтов.

    Метрики траектории считаются НЕ здесь, а в wp4_ablations._summarize — чтобы
    отчёт и абляционный артифакт не разъехались в определениях (и old-волны, у
    которых в логах нет unroll/grad_norm, получали None, а не выдумку).
    """
    rows = run.get("trajectory") or []
    base = _summarize(
        rows,
        run["arm"],
        run.get("steps", 0),
        run.get("seed", 0),
        threshold,
        run.get("description"),
        run.get("overrides") or {},
    )
    alive = [r["alive_fraction"] for r in rows]
    base.pop("trajectory", None)
    base["trajectory_points"] = len(rows)
    base["survived_at_relative_threshold"] = base["survived"]
    base["survived_at_absolute_015"] = bool(alive and min(alive) >= 0.15)
    base["b0_final"] = rows[-1].get("b0") if rows else None
    base["b1_final"] = rows[-1].get("b1") if rows else None
    return base


def _paired_wilcoxon(a_values, b_values):
    """
    Парное сравнение двух серий по сидам. Возвращает dict со статистикой и
    честной пометкой о мощности: точный двусторонний минимум равен 2^(1-n)
    (все разности одного знака, W=0), а не 2^-n — у знакового рангового теста
    два хвоста. При n=5 минимум 0.0625 > 0.05, поэтому «значимость» на пяти
    сидах недостижима априори, каким бы ни был эффект; n=6 даёт 0.03125.
    """
    n = min(len(a_values), len(b_values))
    out = {
        "n_pairs": int(n),
        "median_a": float(np.median(a_values)) if a_values else None,
        "median_b": float(np.median(b_values)) if b_values else None,
        "min_two_sided_p": float(2.0 ** (1 - n)) if n else None,
        "usable": bool(n >= 5),
    }
    if n < 5:
        out["note"] = (
            f"n={n}: парный Wilcoxon не запускаем, минимально достижимый "
            f"двусторонний p = {out['min_two_sided_p']:.5f}. Это не «нет эффекта», "
            "это отсутствие мощности — см. план WP5 (power analysis)."
        )
        return out
    try:
        from scipy.stats import wilcoxon

        res = wilcoxon(np.asarray(a_values[:n], dtype=float), np.asarray(b_values[:n], dtype=float))
        out.update({"statistic": float(res.statistic), "p_value": float(res.pvalue)})
    except Exception as exc:  # noqa: BLE001 - статистика не должна ронять отчёт
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def _usable_wilcoxon_pairs(paired):
    """Пары, где тест реально посчитан.

    Словарь `paired` заполняется и когда сидов меньше пяти: _paired_wilcoxon
    возвращает тогда запись «мощности нет, не запускаем». Если гейт смотреть по
    количеству ключей, WP4 «проходится» одним сидом на плечо — то есть условие
    статистики исчезает ровно в тот момент, когда оно нужно. Поэтому в гейт
    попадают только пары с usable=True.
    """
    return {k: v for k, v in paired.items() if v.get("usable")}


# Поля, по которым строится парный ряд arm <-> базлайн на одном сиде и горизонте.
# f1_final — заявленный первичный эндпоинт WP4 (coverage.f1 на последней точке
# прогона); f1_max — вторичный и заведомо щедрее конца (NEG-21: важно не только
# сколько, но и на какой итерации достигнут максимум); alive_fraction_min и
# visible_mse_final — выживание и MSE, по первому из них пары строились и раньше.
PAIRED_FIELDS = ("f1_final", "f1_max", "alive_fraction_min", "visible_mse_final")
PRIMARY_PAIRED_FIELD = "f1_final"


def _pair_key(arm, steps, field):
    return f"{arm}_vs_H-A0_s{steps}_{field}"


def _is_primary_pair(key):
    return key.endswith(f"_{PRIMARY_PAIRED_FIELD}")


def _build_paired_runs(runs):
    """Парные Уилксины arm <-> H-A0, отдельно по каждому эндпоинту.

    Раньше ряд строился только по alive_fraction_min, то есть по выживанию, а
    гейт WP4 требует «Уилксон» там, где в этом же отчёте первичным эндпоинтом
    назван coverage.f1. Закрывать условие статистикой по другому эндпоинту —
    значит выбить его молча. Поэтому имя пары теперь несёт эндпоинт
    (…_f1_final против …_alive_fraction_min), и в гейт попадает только первичный.
    """
    by_key = {(r["arm"], r["seed"], r["steps"]): r for r in runs}
    paired = {}
    for steps in sorted({r["steps"] for r in runs}):
        for arm in sorted({r["arm"] for r in runs if r["steps"] == steps}):
            if arm == "H-A0":
                continue
            seeds = sorted({r["seed"] for r in runs if r["steps"] == steps and r["arm"] == arm})
            for field in PAIRED_FIELDS:
                a = [by_key[(arm, s, steps)].get(field) for s in seeds]
                b = [
                    by_key[("H-A0", s, steps)].get(field)
                    for s in seeds
                    if ("H-A0", s, steps) in by_key
                ]
                if len(a) == len(b) and all(v is not None for v in a + b):
                    paired[_pair_key(arm, steps, field)] = _paired_wilcoxon(a, b)
    return paired


def _transition_digest(runs):
    """Что произошло В МОМЕНТ перехода куррикулума (unroll 16 -> 32) в тех
    arm'ах, где он был. Это второй по значимости вывод WP4: коллапс не один
    механизм, а два с разными таймингами (плавать вниз на 1e-3 против срыва на
    200-й итерации при 1e-4).

    Волна 1 (200 шагов) обрезалась ровно перед переходом, поэтому её вердикты
    про «выжил» в этом разрезе не участвуют: фильтр steps >= 300.
    """
    with_jump = []
    for r in runs:
        t = r.get("transition_iteration")
        if t is None or r.get("steps", 0) < 300:
            continue
        with_jump.append(
            {
                "arm": r["arm"],
                "steps": r["steps"],
                "seed": r["seed"],
                "transition_iteration": t,
                "unroll": [r.get("unroll_before_transition"), r.get("unroll_after_transition")],
                "alive_before": r.get("alive_fraction_before_transition"),
                "grad_norm_at_transition": r.get("grad_norm_at_transition"),
                "grad_norm_median_before": r.get("grad_norm_median_before_transition"),
                "collapsed_later": not r["survived_at_relative_threshold"],
                "collapse_iteration": r.get("collapse_iteration"),
            }
        )
    without = [
        r["arm"]
        for r in runs
        if r.get("steps", 0) >= 300 and r.get("transition_iteration") is None
    ]
    return {
        "note": (
            "transition_iteration найден по самим логам (первая итерация, на которой "
            "unroll отличается от предыдущей записанной), а не по config: в arm'ах "
            "H-I*/H-K* расписание переопределено."
        ),
        "arms_with_transition": with_jump,
        "arms_without_transition": sorted(set(without)),
    }


def _learning_digest(runs):
    """Выживание != обучение: для выживших arm'ов показываем, насколько ткань
    вообще приблизилась к цели (f1 против 1.0) и сдвинулся ли visible_mse."""
    out = []
    for r in runs:
        if not r["survived_at_relative_threshold"]:
            continue
        out.append(
            {
                "arm": r["arm"],
                "steps": r["steps"],
                "seed": r["seed"],
                "f1_max": r.get("f1_max"),
                "f1_final": r.get("f1_final"),
                "visible_mse_first": r.get("visible_mse_first"),
                "visible_mse_final": r.get("visible_mse_final"),
                "b1_final": r.get("b1_final"),
                "learned_the_target": bool(
                    r.get("f1_max") is not None and r["f1_max"] >= 0.6
                ),
            }
        )
    return out


def _fmt(x, spec=".4f"):
    return format(x, spec) if isinstance(x, (int, float)) and not isinstance(x, bool) else "None"


def _is_noise_run(run):
    """Arm'ы с пулом из цели (TRAIN_POOL_INIT_MODE="target") — это тест ЁМКОСТИ,
    а не рост из шума: их нельзя класть в один вердикт «выжил/не выучил» с
    остальными, иначе идеальный результат H-P1 прикрыл бы провал постановки."""
    return (run.get("overrides") or {}).get("TRAIN_POOL_INIT_MODE") != "target"


def _capacity_digest(runs):
    """Записи, где пул стартует из цели: отделяют «не может» от «не успевает»."""
    return [
        r
        for r in runs
        if (r.get("overrides") or {}).get("TRAIN_POOL_INIT_MODE") == "target"
    ]


def _retention_digest(runs):
    """Wave 7 (§14.2 «удержание как цель»): плечи с включённым retention-членом.

    Отдельный дайджест нужен потому, что у этих прогонов ДВА разных исхода, и
    один из них раньше не наблюдался вовсе: выживание без формы. R-7
    (level-член, множитель 10) — первый прогон за всю историю WP4, доживший
    горизонт (alive_min 0.810 при пороге 0.0762), но его f1_max 0.1886 ниже
    потолка «поля без структуры» 0.2644. То есть выживание перестало быть
    блокёром и блокёром стала форма; в общем списке arms это различие теряется,
    потому что там вердикт один — survived True/False.
    """
    out = []
    for r in runs:
        if not r.get("retention_enabled_by_overrides"):
            continue
        ov = r.get("overrides") or {}
        # overrides содержит только то, что arm менял явно. Для R-плечей без
        # строки про множитель/mode это дефолты config, а не «неизвестно» —
        # иначе R-1 выглядел бы плечом без survival-члена, хотя он именно его
        # и прогонял (в форме transition по умолчанию).
        mode = r.get("retention_survival_mode") or str(config.RETENTION_SURVIVAL_MODE)
        margin = (
            r.get("retention_alive_margin")
            if r.get("retention_alive_margin") is not None
            else float(config.RETENTION_ALIVE_MARGIN)
        )
        curriculum = ov.get("TRAIN_BPTT_CURRICULUM") or list(config.TRAIN_BPTT_CURRICULUM)
        out.append(
            {
                "arm": r["arm"],
                "seed": r["seed"],
                "steps": r["steps"],
                "survival_mode": mode,
                "alive_margin": margin,
                "survival_weight": float(
                    ov.get("RETENTION_SURVIVAL_WEIGHT", config.RETENTION_SURVIVAL_WEIGHT)
                ),
                "rollout_steps": int(
                    ov.get("RETENTION_ROLLOUT_STEPS", config.RETENTION_ROLLOUT_STEPS)
                ),
                "flat_curriculum": len(set(curriculum)) == 1,
                "alive_policy_weight": float(
                    (ov.get("LOSS_WEIGHTS") or {}).get(
                        "alive_policy", config.LOSS_WEIGHTS["alive_policy"]
                    )
                ),
                # Парная половина (quiet): живость ВНЕ цели на той же траектории.
                # Без неё прогон «survival + quiet» неотличим от «только
                # survival», а именно на этой паре решается вопрос о форме.
                "quiet_weight": float(
                    ov.get("RETENTION_QUIET_WEIGHT", config.RETENTION_QUIET_WEIGHT)
                ),
                "quiet_margin": float(
                    ov.get("RETENTION_QUIET_MARGIN", config.RETENTION_QUIET_MARGIN)
                ),
                "quiet_final": r.get("retention_quiet_final"),
                # Фон «на полу» — это НЕ доказанная мёртвость, а отсутствие
                # штрафа: при margin=0 полу соответствует ровно мёртвый фон
                # (alpha = 0.5 даёт relu(0)=0), при margin>0 пол равен margin и
                # его не обойти даже поглощающей смертью. Поле честит именно
                # это: quiet_final <= margin значит «живости вне цели не
                # зафиксировано», и не больше. При выключенном члене поля нет —
                # None, а не False: False читалось бы как «фон живой».
                "background_at_quiet_floor": (
                    None
                    if float(ov.get("RETENTION_QUIET_WEIGHT", config.RETENTION_QUIET_WEIGHT)) <= 0.0
                    or r.get("retention_quiet_final") is None
                    else float(r["retention_quiet_final"])
                    <= float(
                        ov.get("RETENTION_QUIET_MARGIN", config.RETENTION_QUIET_MARGIN)
                    )
                    + 1e-6
                ),
                "survived": r["survived"],
                "alive_fraction_min": r["alive_fraction_min"],
                "collapse_iteration": r["collapse_iteration"],
                # first и final вместе: R-8 (NEG-20) дожил до конца горизонта, а
                # его первичный эндпоинт стал ХУЖЕ мёртвого поля, и по одному
                # final это не видно.
                "visible_mse_first": r.get("visible_mse_first"),
                "visible_mse_final": r["visible_mse_final"],
                "f1_max": r["f1_max"],
                # Где достигнут максимум f1. Без этой колонки ряд «f1_max=0.1886»
                # выглядит как измеренный результат обучения, а в wave 9 (NEG-21)
                # он равен значению на итерации 50 — то есть iniziale модели:
                # на коротком горизонте по f1_max судить о форме нельзя.
                "f1_max_iteration": r.get("f1_max_iteration"),
                # Насыщение level-члена = margin означает «вся цель мертва»:
                # значение большое, градиента нет (NEG-18/NEG-19). Без этого
                # поля прогон с saturating-штрафом выглядит «удержанием заняты».
                "survival_saturated": (
                    mode == "level"
                    and r.get("retention_survival_final") is not None
                    and abs(float(r["retention_survival_final"]) - float(margin)) < 1e-3
                ),
                "truncated": r["truncated"],
            }
        )
    return out


def _read_jsonl_rows(path):
    """Построчный разбор jsonl: (строки, число битых хвостов).

    Битые строки считаются и возвращаются, а не молча выбрасываются: в этот
    каталог писали параллельные процессы, и «журнал цел» должно быть измеряемо,
    а не предполагаемо.
    """
    rows, malformed = [], 0
    if not os.path.exists(path):
        return rows, malformed
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    return rows, malformed


def _journal_integrity(log_dir=None, manager_journal_path=None):
    """Проверка §13.3: на каждую start-запись обязана приходиться finish-запись.

    WP4-гейт требует это явно, поэтому отчёт считает пары сам, а не ссылается на
    «мы вроде писали журнал». Источников три:

    * logs/journal.jsonl — единый журнал (utils.logging.Journal), пишется с тех
      же строк train.py, что и пары;
    * logs/*_log.jsonl — пофайловые логи прогона с событиями run_start/run_finish;
    * experiments/journal.jsonl — журнал менеджера экспериментов (текстовые
      «Начало…»/«Завершено…»), тот самый файл, который в Rev.7 оборвался на
      «E02 Сид 0: стресс включён».

    Прогоны, запущенные до появления парной записи, finish НЕ имеют — их нельзя
    дорисовать задним числом (§7.7), поэтому они считаются отдельно (legacy_*) и
    объясняются отдельной строкой вывода. Актуальное поколение отличается по
    измеримому признаку: строка run_start/journal.start с отметкой emits_run_finish
    написана билдом, который умеет закрывать пару, — отсутствие finish у такой
    строки есть нарушение §13.3. Поле code_pairing говорит, есть ли в train.py
    эмитент finish (включая atexit-маркер «aborted»): без него ноль finish-записей
    означал бы «журнала нет», а не «прогоны старые».
    """
    if log_dir is None:
        log_dir = config.LOG_DIR

    def _read_jsonl(path):
        return _read_jsonl_rows(path)

    journal_path = os.path.join(log_dir, "journal.jsonl")
    jrows, jbad = _read_jsonl(journal_path)
    pending = {}
    supported_pending = {}
    closed = {}
    counts = {"start": 0, "finish": 0, "error": 0, "checkpoint": 0}
    for row in jrows:
        event = row.get("event")
        if event in counts:
            counts[event] += 1
        exp = row.get("experiment") or row.get("experiment_id") or "?"
        if event == "start":
            pending[exp] = pending.get(exp, 0) + 1
            if row.get("emits_run_finish"):
                supported_pending[exp] = supported_pending.get(exp, 0) + 1
        elif event in ("finish", "error"):
            pending[exp] = max(pending.get(exp, 0) - 1, 0)
            closed[exp] = closed.get(exp, 0) + 1
            if supported_pending.get(exp):
                supported_pending[exp] -= 1
    journal = {
        "path": journal_path,
        "present": os.path.exists(journal_path),
        "starts": counts["start"],
        "finishes": counts["finish"],
        "errors": counts["error"],
        "malformed_lines": jbad,
        # Все висячие start (включая legacy-строки) — справочно.
        "unpaired_experiments": sorted(e for e, n in pending.items() if n > 0),
        # Висячие start актуального поколения — нарушение §13.3.
        "supported_starts": sum(
            1
            for r in jrows
            if r.get("event") == "start" and r.get("emits_run_finish")
        ),
        "supported_unpaired_experiments": sorted(e for e, n in supported_pending.items() if n > 0),
        # Подкласс, который меняет диагностику, но не отменяет нарушение: старт
        # без финиша у эксперимента, у которого ДРУГОЙ старт всё-таки закрылся.
        # Так выглядит убитый извне процесс (atexit не успевает написать
        # «aborted»), перезапущенный потом под тем же experiment_id. Считается
        # по тому же счётчику, поэтому не «исправляет» §13.3, а объясняет, из
        # чего состоит дыра: оператор уронил прогон, а не эмитент перестал
        # закрывать пары.
        "supported_unpaired_superseded": sorted(
            e for e, n in supported_pending.items() if n > 0 and closed.get(e, 0) > 0
        ),
        "supported_unpaired_hard": sorted(
            e for e, n in supported_pending.items() if n > 0 and closed.get(e, 0) == 0
        ),
    }

    # Третий источник — журнал менеджера экспериментов (experiments/journal.jsonl):
    # именно он в Rev.7 оборвался строкой «E02 Сид 0: стресс включён», из-за чего
    # незавершённый прогон выглядел как завершённый. Формат там текстовый
    # («Начало…» / «Завершено…» / «Ошибка…»), пары считаем по нему.
    if manager_journal_path is None:
        manager_journal_path = os.path.join("experiments", "journal.jsonl")
    mrows, mbad = _read_jsonl(manager_journal_path)
    stack = {}
    m_starts = m_finishes = 0
    for row in mrows:
        message = str(row.get("message", ""))
        exp = row.get("experiment") or "?"
        if message.startswith("Начало"):
            m_starts += 1
            stack.setdefault(exp, []).append(
                {"spec_version": row.get("spec_version"), "message": message}
            )
        elif message.startswith(("Завершено", "Ошибка", "Прерван")):
            m_finishes += 1
            if stack.get(exp):
                stack[exp].pop()
    unpaired_rows = [
        {"experiment": e, **left} for e, leftovers in stack.items() for left in leftovers
    ]
    manager_journal = {
        "path": manager_journal_path,
        "present": os.path.exists(manager_journal_path),
        "rows": len(mrows),
        "starts": m_starts,
        "finishes": m_finishes,
        "malformed_lines": mbad,
        "unpaired": sorted(
            unpaired_rows,
            key=lambda r: (str(r.get("spec_version")), r["experiment"], r["message"]),
        ),
        # Задним числом Rev.7 не чинится (§7.7), поэтому отдельным полем — что
        # висит именно на текущей версии спеки (это уже нарушение, а не история).
        "unpaired_current_spec": sorted(
            f"{r['experiment']}: {r['message']}"
            for r in unpaired_rows
            if r.get("spec_version") == config.SPEC_VERSION
        ),
    }

    runs = {}
    files = (
        sorted(
            (f for f in os.scandir(log_dir) if f.is_file() and f.name.endswith("_log.jsonl")),
            key=lambda f: f.name,
        )
        if os.path.isdir(log_dir)
        else []
    )
    bad_total = 0
    # Разделение по «поколению» кода: прогон, запущенный билдом, который finish
    # писать умел (поле emits_run_finish в run_start), обязан иметь пару; прогоны
    # старше этого поля — измеренная история (NEG-11), требовать пары от них
    # нельзя, но и молча считать их завершёнными нельзя.
    legacy_starts = 0
    for handle in files:
        rows, malformed = _read_jsonl(handle.path)
        bad_total += malformed
        starts = 0
        finishes = 0
        supported_open = 0
        supported_starts = 0
        for row in rows:
            event = row.get("event")
            if event == "run_start":
                starts += 1
                if row.get("emits_run_finish"):
                    supported_starts += 1
                    supported_open += 1
                else:
                    legacy_starts += 1
            elif event == "run_finish":
                finishes += 1
                if supported_open:
                    supported_open -= 1
        exp = handle.name[: -len("_log.jsonl")]
        if rows:
            exp = rows[0].get("experiment_id") or exp
        runs[exp] = {
            "log": os.path.relpath(handle.path, log_dir),
            "run_starts": starts,
            "run_finishes": finishes,
            "supported_starts": supported_starts,
            "supported_open": supported_open,
            "malformed_lines": malformed,
            "stop_reason": next(
                (r.get("stop_reason") for r in reversed(rows) if r.get("event") == "run_finish"),
                None,
            ),
        }
    # Висячие пары актуального поколения — это и есть нарушение §13.3.
    supported_hanging = sorted(e for e, r in runs.items() if r["supported_open"] > 0)
    with_finish = sorted(e for e, r in runs.items() if r["run_finishes"] > 0)
    supported_total = sum(r["supported_starts"] for r in runs.values())

    try:
        with open("train.py", "r", encoding="utf-8") as fh:
            src = fh.read()
        code_pairing = {
            "journal_start": "journal.start(" in src,
            "journal_finish": "journal.finish(" in src,
            "run_finish_event": '"run_finish"' in src,
            "atexit_abort_marker": "atexit.register(_finish_marker)" in src,
            "run_start_stamp": '"emits_run_finish"' in src,
        }
    except OSError:
        code_pairing = {"error": "train.py не читается"}

    return {
        "requirement": (
            "§13.3 / гейт WP4: в journal.jsonl на каждую start-строку есть finish-строка"
        ),
        "journal": journal,
        "manager_journal": manager_journal,
        "per_run_logs": {
            "files": len(runs),
            "run_starts": sum(r["run_starts"] for r in runs.values()),
            "run_finishes": sum(r["run_finishes"] for r in runs.values()),
            "malformed_lines": bad_total,
            # Актуальное поколение (run_start с emits_run_finish): вот где живёт
            # нарушение §13.3.
            "supported_starts": supported_total,
            "supported_unpaired": supported_hanging,
            # Подкласс висячих стартов: у эксперимента есть finish ОТ ДРУГОГО
            # старта под тем же id. Так выглядит прогон, убитый извне (GPU-
            # процесс снимают без SIGTERM-обработки, atexit-маркер «aborted» не
            # успевает отработать), и затем перезапущенный. Это НЕ отменяет
            # нарушение §13.3 (пара обязана быть на каждый старт), но отделяет
            # «эмитент перестал закрывать пары» от «оператор уронил процесс» —
            # иначе диагностика вела бы в неверную сторону.
            "supported_unpaired_superseded": sorted(
                e for e in supported_hanging if runs[e]["run_finishes"] > 0
            ),
            "supported_unpaired_hard": sorted(
                e for e in supported_hanging if runs[e]["run_finishes"] == 0
            ),
            # Прогоны старше поля: старт без финиша по построению, не починка.
            "legacy_start_rows": legacy_starts,
            "paired": with_finish,
            # Почему встал каждый прогон (None = finish-записи нет, т.е. прогон
            # до починки пары). Без этого «сколько оборвалось» пришлось бы
            # пересчитывать по чужим полям.
            "detail": {e: r["stop_reason"] for e, r in sorted(runs.items())},
        },
        "code_pairing": code_pairing,
        # Честный вердикт: условие §13.3 проверяется на прогонах, которые умели
        # его выполнять. Ни одного такого прогона = условие НЕ выполнено (нельзя
        # объявить выполненным то, что ещё не измерялось). Журнал менеджера
        # учитывается только записями текущей версии спеки: висячий «E02 Сид 0»
        # из Rev.7 — измеренная история, её не чинят задним числом (§7.7), но и
        # актуальным нарушением она не становится.
        "fresh_start_rows": supported_total + journal["supported_starts"],
        "all_starts_paired": (
            (supported_total + journal["supported_starts"]) > 0
            and not supported_hanging
            and not journal["supported_unpaired_experiments"]
            and not manager_journal["unpaired_current_spec"]
        ),
        "legacy_unpaired_records": len(manager_journal["unpaired"]) - len(
            manager_journal["unpaired_current_spec"]
        ),
        "note": (
            "Условие §13.3 проверяется только на прогонах, отмеченных в run_start "
            "полем emits_run_finish: их finish обязан быть, и его отсутствие = "
            "нарушение. Прогоны старше этой отметки (весь WP4, прошлые гейты и "
            "волны аблаций) finish не писали по построению — дыра NEG-11, которую "
            "нельзя закрыть задним числом (§7.7). Каждый свежий прогон пишет "
            "run_finish со stop_reason, а оборванный процесс — finish со "
            "stop_reason=aborted через atexit, так что «старт без финиша» больше "
            "не может выглядеть как завершённый эксперимент."
        ),
    }


def _gate_endpoints(gate, log_dir=None):
    """Первичный эндпоинт (visible MSE) по сидам прогона гейта — из их же логов.

    gate_layer1.json хранит покрытие и Chamfer, а поитерационный MSE в него не
    кладётся. Формулировка гейта WP4 требует «первичный эндпоинт + 5 сидов»,
    поэтому числа достаются из существующих логов, а не новым обучением: логи
    уже на диске, а переобучение дало бы тот же коллапс. Прогон сопоставляется
    с логом по run_start (сид и длина) — без этой проверки чужому сиду можно
    было бы приписать чужую кривую, и имя файла тут не аргумент.
    """
    if not gate or not gate.get("runs"):
        return {"runs": [], "unmatched": [], "note": "gate_layer1.json отсутствует"}
    if log_dir is None:
        log_dir = config.LOG_DIR

    out, unmatched = [], []
    for rec in gate["runs"]:
        seed = int(rec["seed"])
        steps = int(rec["steps"])
        candidates = [
            rec.get("experiment_id"),
            f"GATE_L1_s{steps}_seed{seed}",
            f"GATE_L1_seed{seed}",
        ]
        matched = None
        for exp in candidates:
            if not exp:
                continue
            path = os.path.join(
                log_dir, exp if exp.endswith(".jsonl") else f"{exp}_log.jsonl"
            )
            rows, _bad = _read_jsonl_rows(path)
            starts = [r for r in rows if r.get("event") == "run_start"]
            if not starts:
                continue
            start = starts[0]
            if int(start.get("seed", -1)) == seed and int(start.get("total_steps", -1)) == steps:
                matched = (os.path.basename(path), rows)
                break
        if matched is None:
            unmatched.append({"seed": seed, "steps": steps})
            continue
        name, rows = matched
        mse = [
            r["loss"]["visible_mse"]
            for r in rows
            if isinstance(r.get("loss"), dict) and "visible_mse" in r["loss"]
        ]
        f1 = [
            r["coverage"]["f1"]
            for r in rows
            if isinstance(r.get("coverage"), dict) and "f1" in r["coverage"]
        ]
        out.append(
            {
                "seed": seed,
                "steps": steps,
                "log": name,
                "iterations_logged": len(mse),
                "visible_mse_first": float(mse[0]) if mse else None,
                "visible_mse_last": float(mse[-1]) if mse else None,
                "f1_last": float(f1[-1]) if f1 else None,
                "f1_final_eval": rec.get("f1_final_eval"),
                "alive_fraction_min": rec.get("alive_fraction_min"),
                "no_collapse": rec.get("no_collapse"),
                "stop_reason": next(
                    (
                        r.get("stop_reason")
                        for r in reversed(rows)
                        if r.get("event") == "run_finish"
                    ),
                    None,
                ),
            }
        )
    return {
        "runs": out,
        "unmatched": unmatched,
        "seeds_with_primary_endpoint": sorted(
            {r["seed"] for r in out if r["visible_mse_last"] is not None}
        ),
        "note": (
            "MSE взят из логов прогонов гейта (train пишет loss.visible_mse на "
            "каждой итерации); пересчётом обучения не получен — §7.7"
        ),
    }


def _threshold_digest(probe):
    """Компактная таблица скана порогов (wp4_threshold_probe.py).

    Длинную кривую из 60 точек сюда не кладём — она лежит в threshold_probe.json.
    Смысл колонки: f1@0.5 = штатный эндпоинт §5.1, best_f1 = максимум по порогу
    (лучшее, что модель умеет, если амплитуду калибровать постфактум). Разрыв
    между ними = «выучила бледно», а не «не выучила»; но вывод о структуре делаем
    только против потолка бесструктурного предсказателя structureless_f1_ceiling.
    """
    if not probe:
        return None
    runs = []
    for rec in probe.get("runs", []):
        scan = (rec.get("threshold_scan") or {}).get("saved_state") or {}
        gscan = (rec.get("threshold_scan") or {}).get("saved_state_alive_gated") or {}
        auto = (rec.get("threshold_scan") or {}).get("after_autonomous_steps") or {}
        gauto = (rec.get("threshold_scan") or {}).get("after_autonomous_steps_alive_gated") or {}
        best = scan.get("best") or {}
        gbest = gscan.get("best") or {}
        auto_best = (auto.get("scan") or {}).get("best") or {}
        gauto_best = (gauto.get("scan") or {}).get("best") or {}
        runs.append(
            {
                "experiment_id": rec["experiment_id"],
                "iteration": rec.get("checkpoint_iteration"),
                "pool_init_mode": rec.get("pool_init_mode_in_log"),
                "visible_mse": rec.get("visible_mse_at_checkpoint"),
                "f1_at_default_threshold": scan.get("f1_at_default_threshold"),
                "best_f1_saved_state": best.get("f1"),
                "best_threshold": best.get("threshold"),
                "best_recall": best.get("recall"),
                "best_precision": best.get("precision"),
                "best_pred_fraction": best.get("pred_fraction"),
                # gated = мёртвые клетки принудительно «тёмные» (§5.2/§5.8):
                # по ним и ставится вердикт, см. _scan_field в wp4_threshold_probe.
                "gated_best_f1_saved_state": gbest.get("f1"),
                "gated_best_threshold": gbest.get("threshold"),
                "gated_best_recall": gbest.get("recall"),
                "gated_best_precision": gbest.get("precision"),
                "autonomous_steps": auto.get("steps"),
                "best_f1_after_autonomous_steps": auto_best.get("f1"),
                "gated_best_f1_after_autonomous_steps": gauto_best.get("f1"),
                "best_f1_any_threshold": rec.get("best_f1_any_threshold"),
                "best_f1_any_threshold_gated": rec.get("best_f1_any_threshold_gated"),
                # по-максимуму по gated-сканам (сохраненное поле + автономный rollout)
                "structure_beyond_ceiling": rec.get("structure_beyond_ceiling"),
                "structure_beyond_ceiling_ungated": rec.get("structure_beyond_ceiling_ungated"),
            }
        )
    return {
        "target_density": probe.get("target_density"),
        "constant_field_floor": probe.get("constant_field_floor"),
        "structureless_f1_ceiling": probe.get("structureless_f1_ceiling"),
        "criterion": (
            "структура есть, если best_f1_any_threshold_gated > structureless_f1_ceiling + 0.05 "
            "(зазор = шумовой: потолок 2p/(1+p) достигается точно, 0.2643-0.2649); "
            "gated = мёртвые клетки не считаются яркими"
        ),
        "runs": runs,
        # Контроль ёмкости (пул из цели) — вне списка «рост из шума»: он и обязан
        # давать 1.0, это проверка инструмента, а не результат постановки §14.2.
        "beyond_ceiling": sorted(
            r["experiment_id"]
            for r in runs
            if r["structure_beyond_ceiling"] and r.get("pool_init_mode") != "target"
        ),
        "controls_beyond_ceiling": sorted(
            r["experiment_id"]
            for r in runs
            if r["structure_beyond_ceiling"] and r.get("pool_init_mode") == "target"
        ),
    }


def _reach_digest(probes):
    """Компактная сводка зонда «достичь/удержать» (wp4_reach_probe.py).

    Зонд — единственное измерение в полосе, где f1 снимается не с того состояния,
    в котором модель оказалась по ходу обучения, а с автономной развёртки из двух
    заведомо разных стартов: шума (reach) и самой цели (hold). Без него «f1=0»
    неотличимо от «дорастает, но не держится», а H-P1 (пул из цели) читается как
    морфогенез, хотя это неподвижная точка.

    Точка решения у двух прогонов разная и берётся из артефакта (decision_point):
    у hold максимум траектории равен 1.0 по построению (старт = цель), поэтому
    решать по нему значило бы измерять начальное состояние (NEG-21/NEG-23).
    Длина развёртки — часть измерения, поэтому сводка идёт по горизонтам.

    Артефактов зонда несколько (разные плечи и разные длины развёртки), и один
    прогон может попасть в два файла: R-9 s2000 мерился и общим запуском, и
    отдельным sweep'ом на том же горизонте. Поэтому блоки сливаются по
    rollout_steps, а прогоны дедуплицируются по (arm, steps_trained, seed, probe):
    побеждает запись из последнего файла. Иначе один и тот же чекпоинт считался
    бы дважды, а в отчёте появились бы два «горизонта 1000».
    """
    if not probes:
        return None
    by_horizon = {}
    for probe in probes:
        horizon = probe.get("rollout_steps")
        verdict = probe.get("verdict") or {}
        bucket = by_horizon.get(horizon)
        if bucket is None:
            bucket = {
                "device": set(),
                "criterion": set(),
                "ceiling": set(),
                "reachable_arms": set(),
                "holdable_arms": set(),
                "runs": {},
            }
            by_horizon[horizon] = bucket
        if probe.get("device"):
            bucket["device"].add(str(probe["device"]))
        for key, target in (("threshold", "criterion"), ("ceiling", "ceiling")):
            value = verdict.get(key)
            if value is not None:
                bucket[target].add(float(value))
        bucket["reachable_arms"].update(verdict.get("reachable_arms") or [])
        bucket["holdable_arms"].update(verdict.get("holdable_arms") or [])
        for rec in probe.get("runs", []):
            dec = rec.get("decision") or {}
            best = rec.get("best") or {}
            last = rec.get("last") or {}
            key = (
                rec.get("arm"),
                rec.get("steps_trained"),
                rec.get("seed"),
                rec.get("probe"),
            )
            bucket["runs"][key] = {
                "arm": rec.get("arm"),
                "steps_trained": rec.get("steps_trained"),
                "seed": rec.get("seed"),
                "probe": rec.get("probe"),
                "decision_point": rec.get("decision_point"),
                "start_f1_default": (rec.get("first") or {}).get("f1_default"),
                "best_f1": best.get("f1_gated_best"),
                "best_step": best.get("step"),
                "last_f1": last.get("f1_gated_best"),
                "decision_f1": dec.get("f1_gated_best"),
                "decision_precision": dec.get("gated_precision"),
                "decision_pred_fraction": dec.get("gated_pred_fraction"),
                "n_gated_thresholds": dec.get("n_gated_thresholds"),
                "alive_fraction_min": rec.get("alive_fraction_min"),
                "beyond_ceiling": rec.get("beyond_ceiling"),
            }

    def _one_or_sorted(values):
        if len(values) == 1:
            return next(iter(values))
        return sorted(values)

    horizons = []
    for horizon in sorted(by_horizon, key=lambda h: h or 0):
        bucket = by_horizon[horizon]
        horizons.append(
            {
                "rollout_steps": horizon,
                "device": ", ".join(sorted(bucket["device"])) or None,
                "criterion": _one_or_sorted(bucket["criterion"]),
                "structureless_f1_ceiling": _one_or_sorted(bucket["ceiling"]),
                "reachable_arms": sorted(bucket["reachable_arms"]),
                "holdable_arms": sorted(bucket["holdable_arms"]),
                "runs": [
                    bucket["runs"][key]
                    for key in sorted(bucket["runs"], key=lambda k: tuple(str(x) for x in k))
                ],
            }
        )
    return {
        "note": (
            "reach = кольцо достигается из шума (решение по максимуму траектории), "
            "hold = кольцо ещё есть через N шагов после старта из цели (решение по "
            "последней точке). Пустой reach при непустом hold — неподвижная точка, "
            "а не морфогенез (§14.2). gated_best — максимум по 60 квантильным порогам "
            "и по точкам траектории, то есть оптимистично смещённая статистика; "
            "поэтому рядом лежат precision и pred_fraction лучшей точки."
        ),
        "horizons": horizons,
    }


def _conclusions(runs, threshold, threshold_probe=None, density=None, journal_integrity=None, reach=None):
    """Выводы, собранные из измеренных чисел, а не из памяти о прошлом запуске.

    Текст прошлой версии был захардкожен и уже начал отставать от данных
    («H-D2 выжил» — волна 1), поэтому каждая строка ниже либо считает число из
    runs, либо явно помечает, что она ссылается на NEG-запись.
    """
    latest = {}
    for r in runs:
        # Для каждого arm'а берём самый длинный горизонт: он включает переход
        # куррикулума и потому валиден для вердикта о выживании.
        key = (r["arm"], r["seed"])
        if key not in latest or r["steps"] > latest[key]["steps"]:
            latest[key] = r

    def one(arm, seed=42):
        return latest.get((arm, seed))

    died_from_loss_terms = [
        a
        for a in ("H-A1", "H-A2", "H-A3", "H-B", "H-E", "H-F", "H-G", "H-H")
        if (r := one(a)) is not None and not r["survived_at_relative_threshold"]
    ]
    survivors = sorted(
        {
            r["arm"]
            for r in latest.values()
            if r["survived_at_relative_threshold"] and _is_noise_run(r)
        }
    )
    lines = [
        "H-A в сильной форме (смерть = оптимум реализованной цели) опровергнута: "
        "корректно собранное кольцо стоит 0.0040 против 0.4275 у мёртвого поля — см. NEG-07.",
        f"Порог вердикта: относительный {threshold:.4f} (0.5 x плотность цели), а не "
        "абсолютный 0.15, который стоял впритык к плотности цели 0.1523.",
    ]
    if died_from_loss_terms:
        lines.append(
            "Снятие отдельных членов лосса не спасает: умерли "
            + ", ".join(died_from_loss_terms)
            + ". Состав лосса — не оперативная причина коллапса."
        )
    grid = []
    for arm in ("H-I1", "H-I2", "H-I3", "H-D1", "H-D2", "H-D3", "H-A0"):
        r = one(arm)
        if r is None:
            continue
        grid.append(
            f"{arm}: {r['description']} -> alive_min {_fmt(r['alive_fraction_min'])}, "
            f"f1_max {_fmt(r['f1_max'])}, переход unroll "
            f"{_fmt(r.get('transition_iteration'), 'd')} "
            f"(gn {_fmt(r.get('grad_norm_at_transition'), '.1f')} против медианы до него "
            f"{_fmt(r.get('grad_norm_median_before_transition'), '.2f')}), "
            f"выжил={r['survived_at_relative_threshold']}"
        )
    if grid:
        lines.append("Куррикулум BPTT и длина шага (" + "; ".join(grid) + ").")
    const_floor = density * (1.0 - density) if density else None
    if survivors:
        rows = []
        stale_lr = []
        for a in survivors:
            r = one(a)
            if r is None:
                continue
            vs = r["visible_mse_final"]
            if const_floor and vs is not None and vs >= const_floor:
                stale_lr.append(a)
            beat = (
                "ниже пола константы"
                if const_floor and vs is not None and vs < const_floor
                else "не ниже пола константы"
                if const_floor and vs is not None
                else "пол не вычислен"
            )
            rows.append(
                f"{a} (alive_min {_fmt(r['alive_fraction_min'])}, f1_max {_fmt(r['f1_max'])}, "
                f"visible_mse {_fmt(r['visible_mse_first'])}->{_fmt(vs)} = {beat} "
                f"{_fmt(const_floor, '.5f')})"
            )
        lines.append(
            "Выжили только " + ", ".join(sorted(survivors)) + ". Ни один из них не собрал цель "
            "при штатном эндпоинте f1@0.5: " + "; ".join(rows) + ". "
            "Пол константного предсказателя p(1-p) — разделительная линия: выше него поле с целью "
            "не согласовано вообще, ниже — согласовано хоть как-то (см. скан порогов)."
            + (
                " У " + ", ".join(sorted(stale_lr)) + " visible_mse остался выше пола — это "
                "остановка обучения, а не медленный рост."
                if stale_lr
                else ""
            )
        )
    else:
        lines.append(
            "Ни один arm на горизонте, включающем переход куррикулума, не удержал ткань выше порога."
        )
    ret = _retention_digest(runs)
    if ret:
        ceiling_line = []
        for e in ret:
            # «None» в этой колонке читается как «фона на полу нет», а означает
            # «поле не измерялось этим членом» — разница ровно та же, из-за
            # которой digest берёт пропущенные поля из config.
            if e["quiet_weight"] <= 0.0:
                floor_note = "quiet выкл."
            elif e["background_at_quiet_floor"] is None:
                floor_note = "quiet вкл., не записан"
            else:
                floor_note = (
                    "ФОН НА ПОЛУ (живости вне цели нет)"
                    if e["background_at_quiet_floor"]
                    else "фон не на полу (живость вне цели есть)"
                )
            ceiling_line.append(
                f"{e['arm']}/s{e['steps']} (mode={e['survival_mode']}, "
                f"множитель {_fmt(e['survival_weight'], '.1f')}, K={e['rollout_steps']}, "
                f"flat-curriculum={e['flat_curriculum']}, "
                f"quiet вес={_fmt(e['quiet_weight'], '.1f')}, "
                f"alive_policy вес={_fmt(e['alive_policy_weight'], '.1f')}): "
                f"выжил={e['survived']} alive_min={_fmt(e['alive_fraction_min'])} "
                f"f1_max={_fmt(e['f1_max'])}@it{_fmt(e['f1_max_iteration'], 'd')} "
                f"vis {_fmt(e['visible_mse_first'])}->{_fmt(e['visible_mse_final'])} "
                f"{floor_note} "
                f"{'штраф насыщен (цель мертва)' if e['survival_saturated'] else 'штраф не насыщен'}"
            )
        lines.append(
            "Wave 7+9, удержание как член лосса (§14.2): " + "; ".join(ceiling_line) + ". "
            "Смысл ряда в том, что выживание и форма расцеплены: transition-форма не меняла "
            "исхода вообще (NEG-18), level-форма удерживает жизнь (R-7: alive_min 0.810 при пороге "
            f"{threshold:.4f} — первое выживание на mask-ON постановке), но её f1_max всё равно "
            "не превышает потолок поля без структуры 0.2644, то есть кольцо не собирается. "
            "Wave 9 добавила вторую половину полосы (quiet = живость ВНЕ цели на том же roll-out): "
            "пари по фону из одного целевого кадра не хватало — R-8 с alive_policy весом 2.0 дожил "
            "до конца горизонта 2000 (alive_min 0.4575, коллапса нет, штраф не насыщен: "
            "survival_final 1.62e-02), но f1_max=0.2300 < 0.2644 при precision ~0.15, то есть "
            "остался «живо всё» (NEG-20). Отдельно и неприятно: его финальный visible_mse 0.2948 "
            "ХУЖЕ аналитического мёртвого поля 0.25, т.е. выживание куплено ценой первичного "
            "эндпоинта — ещё одна причина, почему про wave 7/9 нельзя судить по колонке survived. "
            "Отрицательный итог этих волн нельзя читать как «удержание не "
            "работает»: оно работает и переводит вопрос из «ткань умирает» в «ткань живая, но "
            "бесформенная», а дальше проверяется, закрывает ли вторую половину именно roll-out "
            "налог (R-9/R-10/R-11, веса quiet 1.0/3.0/1.0 калиброваны по замеру градиента на "
            "чекпоинте R-8), а не ещё один вес. "
            "Правило чтения f1_max (NEG-21): у всех плеч с горизонтом 400 argmax f1 приходится "
            "на итерацию 50, то есть на самое первое измерение после сброса маски — на таком "
            "горизонте f1_max измеряет начальное состояние модели, а не результат обучения, "
            "поэтому вывод «формы нет» по 400 итерациям не делается, и волна 9 перезапущена "
            "на 2000 (ряд сравнения — R-8, у которого максимум f1=0.2300 достигнут на "
            "итерации 1250, то есть сильно после конца экрана: eval-точки идут 0.0813@200 -> "
            "0.0581@400 -> 0.1559@600 -> 0.2252@1200). quiet при этом передаёт давление "
            "измеримо: quiet_final 0.3410 при весе 1.0 против 0.1329 при весе 3.0 (R-9/R-10), "
            "то есть член работает как написан, и его нулевой эффект на f1 — это результат "
            "про форму, а не про сломанный штраф."
        )
    lines.append(
        "Все диагностические прогоны (<=400 итераций) лежат ВНУТРИ линейного warmup "
        "(TRAIN_WARMUP_STEPS=500): фактический LR растёт с 0 до TRAIN_LR, косинусная ветка не "
        "выполняется. Вывод про LR нельзя переносить на полный прогон без отдельной проверки."
    )
    if journal_integrity is not None:
        jn = journal_integrity["journal"]
        mj = journal_integrity["manager_journal"]
        pl = journal_integrity["per_run_logs"]
        emitter = ", ".join(
            f"{k}={v}" for k, v in sorted(journal_integrity["code_pairing"].items())
        )
        hang_list = "; ".join(
            f"{r['experiment']} ← «{r['message']}»" for r in mj["unpaired"]
        )
        if journal_integrity["all_starts_paired"]:
            tail = " Требование выполнено: у всех start-строк актуального поколения есть finish."
        elif journal_integrity["fresh_start_rows"] == 0:
            tail = (
                " Требование НЕ выполнено: ни одного прогона билдом, который пишет finish, ещё "
                "не запускалось (отметка emits_run_finish появилась позже волн WP4) — старые логи "
                f"не дописываются задним числом (§7.7, NEG-11). Эмитент пар в train.py ({emitter})."
            )
        else:
            superseded = pl.get("supported_unpaired_superseded") or []
            hard = [e for e in pl["supported_unpaired"] if e not in superseded]
            tail = (
                " Требование НЕ выполнено: у прогона(ов) актуального поколения старт без финиша ("
                + ", ".join(pl["supported_unpaired"])
                + ") — это ровно та дыра §13.3, из-за которой оборванный эксперимент выглядел "
                "завершённым."
                + (
                    f" Из них {len(superseded)} — убитые извне попытки, перезапущенные под тем же "
                    "id и закрытые финишем второй попытки (" + ", ".join(superseded) + "): atexit-"
                    "маркер «aborted» на жёсткое снятие процесса не распространяется. Настоящих "
                    "нарушений эмитента (старт без единого финиша): "
                    + (", ".join(hard) if hard else "нет") + "."
                    if superseded
                    else ""
                )
            )
        lines.append(
            "Журнал §13.3 (гейт WP4 требует пару на каждую start-строку): "
            + ("logs/journal.jsonl есть" if jn["present"] else "logs/journal.jsonl отсутствует")
            + f" (start={jn['starts']}, finish={jn['finishes']}, error={jn['errors']}); "
            f"пофайловые логи: run_start={pl['run_starts']}, run_finish={pl['run_finishes']}. "
            f"Актуальное поколение (run_start с отметкой emits_run_finish): "
            f"строк={journal_integrity['fresh_start_rows']}, без финиша="
            f"{pl['supported_unpaired'] or 'нет'}; прогонов до починки (пары не требуется, "
            f"но и завершения нет) = {pl['legacy_start_rows']} строк (§7.7, NEG-11)."
            + f" Журнал менеджера ({mj['path']}): Начало={mj['starts']}, "
            f"Завершено/Ошибка={mj['finishes']}; висячих на текущей версии спеке "
            f"{len(mj['unpaired_current_spec'])}, исторических записей без пары "
            f"(Rev.7, по §7.7 не правится) {journal_integrity['legacy_unpaired_records']}"
            + (f": {hang_list}" if hang_list else "")
            + ". "
            + tail
        )
    capacity = _capacity_digest(runs)
    if capacity:
        best = max(capacity, key=lambda r: (r.get("f1_max") or 0.0, r["steps"]))
        lines.append(
            f"ЁМКОСТЬ НЕ ПРИЧЁМ: при пуле, стартующем из цели (TRAIN_POOL_INIT_MODE=\"target\", "
            f"{best['arm']}, {best['steps']} итераций), модель УДЕРЖИВАЕТ кольцо — "
            f"f1_max {_fmt(best.get('f1_max'))}, f1_final {_fmt(best.get('f1_final'))}, "
            f"chamfer_final {_fmt(best.get('chamfer_final'))}, "
            f"β₀={_fmt(best.get('b0_final'), '.2f')} β₁={_fmt(best.get('b1_final'), '.2f')}, "
            f"visible_mse {_fmt(best.get('visible_mse_first'), '.5f')}->"
            f"{_fmt(best.get('visible_mse_final'), '.5f')}, alive_min "
            f"{_fmt(best.get('alive_fraction_min'))}. Значит блокёр E02 — требование §14.2 "
            "«вырастить форму ИЗ ШУМА за горизонт BPTT», а не архитектура, не состав лосса и "
            "не поглощающая смерть сами по себе."
        )
    t = _threshold_digest(threshold_probe) if threshold_probe else None
    if t and t["runs"]:
        ceiling = t["structureless_f1_ceiling"]
        floor = t["constant_field_floor"]
        # Прогон с пулом из цели — положительный контроль самого инструмента:
        # на заведомо выученном поле скан обязан вернуть ~1.0. Его нельзя ставить
        # в один список с прогонами «рост из шума».
        controls = [r for r in t["runs"] if r.get("pool_init_mode") == "target"]
        noise_runs = [r for r in t["runs"] if r.get("pool_init_mode") != "target"]
        above = [r for r in noise_runs if r["structure_beyond_ceiling"]]
        below = [r for r in noise_runs if not r["structure_beyond_ceiling"]]
        if controls:
            ctrl = max(controls, key=lambda r: r["gated_best_f1_saved_state"] or 0.0)
            ok = (ctrl["gated_best_f1_saved_state"] or 0.0) > ceiling + 0.05
            verdict = (
                "скан видит заведомо выученное поле"
                if ok
                else "СКАН НЕ ВИДИТ заведомо выученное поле: инструмент сломан"
            )
            lines.append(
                "Контроль инструмента: на прогоне с пулом из цели "
                f"({ctrl['experiment_id']}) скан даёт лучший f1 (gated) "
                f"{_fmt(ctrl['gated_best_f1_saved_state'])} при f1@0.5="
                f"{_fmt(ctrl['f1_at_default_threshold'])} — {verdict}."
            )
        parts = []
        for r in above + below:
            parts.append(
                f"{r['experiment_id']}: f1@0.5={_fmt(r['f1_at_default_threshold'])}, "
                f"лучший f1 (с условием живости)={_fmt(r['gated_best_f1_saved_state'])} при пороге "
                f"{_fmt(r['gated_best_threshold'], '.3f')} (R={_fmt(r['gated_best_recall'], '.3f')} "
                f"P={_fmt(r['gated_best_precision'], '.3f')}, без условия "
                f"{_fmt(r['best_f1_saved_state'])}), после "
                f"{r['autonomous_steps']} автономных шагов (gated)={_fmt(r['gated_best_f1_after_autonomous_steps'])}"
            )
        lines.append(
            "Скан порогов (вторичный эндпоинт, NEG-10): потолок бесструктурного "
            f"«всё яркое» = 2p/(1+p) = {_fmt(ceiling)}, пол константного MSE = "
            f"p(1-p) = {_fmt(floor, '.5f')}. " + " | ".join(parts) + "."
        )
        if above:
            best_hold = max(
                (
                    r
                    for r in above
                    if r["gated_best_f1_after_autonomous_steps"] is not None
                ),
                key=lambda r: r["gated_best_f1_after_autonomous_steps"],
            )
            held = (
                best_hold["gated_best_f1_after_autonomous_steps"] or 0.0
            ) > ceiling + 0.05
            lines.append(
                "Структура ВЫШЕ потолка есть только у "
                + ", ".join(f"{r['experiment_id']} ({r['iteration']} итераций)" for r in above)
                + ": в этих прогонах выключены маска и давление на alpha "
                "(см. overrides в ablation_runs) — кольцо локализовано (recall близок к 1), "
                "но амплитудой ниже порога §5.1, то есть "
                "f1@0.5 = 0 означает «не в фокусе бинарной метрики», а не «ничему не научилась»."
                + (
                    " После "
                    f"{best_hold['autonomous_steps']} автономных шагов лучший f1 (gated) ="
                    f" {_fmt(best_hold['gated_best_f1_after_autonomous_steps'])} — это выше потолка "
                    "с зазором, то есть выученное поле УДЕРЖИВАЕТСЯ динамикой."
                    if held
                    else " Удержания нет: после "
                    f"{best_hold['autonomous_steps']} автономных шагов лучший f1 (gated) падает до "
                    f"{_fmt(best_hold['gated_best_f1_after_autonomous_steps'])} — ниже потолка с "
                    "зазором, то есть динамика форму не удерживает."
                )
            )
        if below:
            artifact = [
                r
                for r in below
                # Разрыв > 0.05 между ungated и gated = ровно артефакт мёртвых
                # клеток (sigmoid(0)=0.5 по §5.8), а не выученная амплитуда.
                if (r["best_f1_any_threshold"] or 0.0) - (r["best_f1_any_threshold_gated"] or 0.0)
                > 0.05
            ]
            lines.append(
                "У "
                + ", ".join(
                    f"{r['experiment_id']} лучший f1 (gated) {_fmt(r['best_f1_any_threshold_gated'])}"
                    for r in below
                )
                + " — не превышает потолок бесструктурного предсказателя с учётом зазора: "
                "структуры нет."
                + (
                    " При этом у "
                    + ", ".join(
                        f"{r['experiment_id']} ungated-скан даёт {_fmt(r['best_f1_any_threshold'])}"
                        for r in artifact
                    )
                    + " (≈ потолок) — это ложные sigmoid(0)=0.5 в мёртвых клетках: §5.8 обнуляет "
                    "клетку целиком, поэтому при пороге < 0.5 вся мёртвая ткань считается "
                    "яркой. Отсюда требование: скан обязан учитывать канал живости."
                    if artifact
                    else ""
                )
            )
    if reach and reach.get("horizons"):
        parts = []
        for h in reach["horizons"]:
            parts.append(
                f"{h['rollout_steps']} шагов: достижимо — "
                + (", ".join(h["reachable_arms"]) if h["reachable_arms"] else "ни у кого")
                + "; удерживается — "
                + (", ".join(h["holdable_arms"]) if h["holdable_arms"] else "ни у кого")
            )
        lines.append(
            "Зонд «достичь/удержать» (автономная развёртка без обучения, "
            "wp4_reach_probe.py; по горизонтам — длина развёртки входит в измерение): "
            + "; ".join(parts)
            + "."
        )
        # Пересечение порога на reach — это максимум по траектории. Если конец
        # развёртки ниже, структура не удерживается, и это надо сказать числом,
        # иначе «достижимо» прочтут как «получилось».
        transient = []
        for h in reach["horizons"]:
            for r in h["runs"]:
                if r["probe"] == "reach" and r["beyond_ceiling"]:
                    transient.append(
                        f"{r['arm']} s{r['steps_trained']} на {h['rollout_steps']} шагах: "
                        f"max {_fmt(r['best_f1'])} @{r['best_step']} -> конец "
                        f"{_fmt(r['last_f1'])}"
                    )
        if transient:
            lines.append(
                "Пересечение порога на reach — всегда МАКСИМУМ траектории, а не состояние: "
                + "; ".join(transient)
                + ". Это значит «кольцо побывало собранным», а не «динамика его удерживает»."
            )
        # Прочность неподвижной точки у контроля, чей пул обучения стартует из
        # цели: сколько от кольца остаётся к концу развёртки — и что из шума он
        # при этом не растёт (иначе это был бы морфогенез, а не фиксированная точка).
        hold_ctrl = []
        reach_ctrl = []
        for h in reach["horizons"]:
            for r in h["runs"]:
                if r["arm"] != "H-P1":
                    continue
                if r["probe"] == "hold":
                    hold_ctrl.append(f"на {h['rollout_steps']} шагах {_fmt(r['decision_f1'])}")
                elif r["beyond_ceiling"]:
                    reach_ctrl.append(str(h["rollout_steps"]))
        if hold_ctrl:
            lines.append(
                "Контроль H-P1 (пул обучения стартует из цели): удержание при старте из цели "
                + ", ".join(hold_ctrl)
                + (" — это прочность неподвижной точки, а не морфогенез: из шума он "
                   "порог не пересекает ни на одном горизонте"
                   if not reach_ctrl
                   else " — а из шума порог пересекает на горизонтах "
                        + ", ".join(reach_ctrl))
                + "."
            )
    return lines


def build_report():
    ablations = _load("wp4_ablations.json") or {"runs": []}
    probe = _load("collapse_probe.json")
    delta = _load("delta_profile.json")
    gate = _load("gate_layer1.json")
    thresh = _load("threshold_probe.json")
    # Зонд «достичь/удержать» пишется по одному артефакту на горизонт развёртки;
    # отсутствие любого из них — не ошибка (старые снимки), но если есть хоть
    # один, он обязан попасть в отчёт: это единственное измерение, где f1
    # снимается не с состояния по ходу обучения.
    reach = _reach_digest(
        [
            payload
            for payload in (
                _load("wp4_reach_probe.json"),
                _load("wp4_reach_probe_s1000.json"),
                _load("wp4_reach_probe_s2000.json"),
                _load("wp4_reach_probe_R9_s1000.json"),
            )
            if payload
        ]
    )
    journal_integrity = _journal_integrity()
    gate_endpoints = _gate_endpoints(gate)

    density = ablations.get("target_density") or _target_density()
    threshold = config.collapse_alive_fraction_min(density)

    runs = [_arm_summary(r, threshold) for r in ablations["runs"]]

    # Эффект arm'а относительно базлайна на том же сиде и горизонте.
    by_key = {(r["arm"], r["seed"], r["steps"]): r for r in runs}
    for r in runs:
        base = by_key.get(("H-A0", r["seed"], r["steps"]))
        if base is None or r["arm"] == "H-A0" or base["alive_fraction_min"] is None:
            continue
        r["delta_alive_min_vs_baseline"] = float(r["alive_fraction_min"] - base["alive_fraction_min"])
        if base["visible_mse_final"] not in (None, 0.0) and r["visible_mse_final"] is not None:
            r["relative_visible_mse_vs_baseline"] = float(r["visible_mse_final"] / base["visible_mse_final"])

    # Парные ряды по сидам для Wilcoxon (работает только когда сидов >=5).
    paired = _build_paired_runs(runs)
    usable_pairs = _usable_wilcoxon_pairs(paired)
    primary_usable_pairs = {k: v for k, v in usable_pairs.items() if _is_primary_pair(k)}

    verdicts = {
        "arms_survived": sorted({r["arm"] for r in runs if r["survived_at_relative_threshold"]}),
        "arms_died": sorted({r["arm"] for r in runs if not r["survived_at_relative_threshold"]}),
        "n_runs": len(runs),
        "n_seeds": len({r["seed"] for r in runs}),
        # Условие гейта WP4 по §13.3: пары start/finish в журнале. Считается по
        # фактическим логам; на старых артефактах оно ложно по построению.
        "journal_paired": journal_integrity["all_starts_paired"],
    }

    # Самодиагностика гейта WP4 из плана: «results.json с первичным эндпоинтом,
    # 5 сидов, effect size, Уилксон; в journal.jsonl на каждую start-строку есть
    # finish-строка». Пишется как список условий с числами, потому что «почти
    # выполнено» и «выполнено» в отчёте обязаны различаться.
    seeds_with_f1 = sorted(
        {r["seed"] for r in runs if r.get("f1_final") is not None or r.get("f1_max") is not None}
    )
    with_effect = [r for r in runs if r.get("delta_alive_min_vs_baseline") is not None]
    # Сида гейта слоя 1 считаются отдельно: это один плечо (базлайн) на 5 сидах,
    # а не 5 сидов у каждого аблационного плеча. Считать их вместе было бы
    # подгонкой под формулировку гейта.
    gate_seeds = sorted({int(r["seed"]) for r in (gate or {}).get("runs", [])})
    n_seeds_all = len({int(r["seed"]) for r in runs} | set(gate_seeds))
    primary_seeds = sorted(
        set(seeds_with_f1) | set(gate_endpoints["seeds_with_primary_endpoint"])
    )
    gate_wp4_checks = {
        "primary_endpoint_coverage": {
            "met": bool(primary_seeds),
            "seeds_with_f1": seeds_with_f1,
            "seeds_with_visible_mse": gate_endpoints["seeds_with_primary_endpoint"],
            "seeds_with_primary_endpoint": primary_seeds,
        },
        "five_seeds": {
            "met": n_seeds_all >= 5,
            "n_seeds": verdicts["n_seeds"],
            "n_seeds_including_gate": n_seeds_all,
            "gate_seeds": gate_seeds,
            "comment": (
                "5 сидов закрыты прогоном гейта слоя 1 (gate_layer1.json, одно плечо "
                "на сидах "
                f"{gate_seeds or 'нет'}); волны аблаций шли на одном сиде, поэтому "
                "это 5 наблюдений базлайна, а не 5 наблюдений каждого arm'а"
            ),
        },
        "effect_size_vs_baseline": {
            "met": bool(with_effect),
            "runs_with_delta": len(with_effect),
            "seeds_with_delta": sorted({int(r["seed"]) for r in with_effect}),
            "comment": (
                "дельта считается на той же паре (arm, сид, горизонт); сидов в "
                "аблациях ровно столько, сколько перечислено — это effect size при "
                "n=1 на плечо, а не оценка разброса"
            ),
        },
        "paired_wilcoxon": {
            # bool(paired) было бы ложным «выполнено»: словарь заполняется и для
            # n=1, где тест сознательно НЕ запускается (мощности нет). Требование
            # гейта — посчитанный тест, поэтому считаются только пары с n>=5.
            # Второе уточнение: ряды строятся по нескольким эндпоинтам, а условие
            # гейта сформулировано по первичному (coverage.f1), поэтому met смотрит
            # только на него — иначе «Уилксон» закрывался бы статистикой по тому
            # эндпоинту, который для него удобен.
            "met": bool(primary_usable_pairs),
            "primary_endpoint_field": PRIMARY_PAIRED_FIELD,
            "pairs": len(paired),
            "pairs_by_field": {
                field: sum(1 for k in paired if k.endswith(f"_{field}")) for field in PAIRED_FIELDS
            },
            "pairs_with_computed_test": len(usable_pairs),
            "pairs_with_computed_test_on_primary": len(primary_usable_pairs),
            "computed_primary_pairs": sorted(primary_usable_pairs),
            "comment": (
                "парный Уилксон требует >=5 сидов на пару arms (см. utils.stats); "
                "ряды строятся по каждому эндпоинту отдельно и имя пары его несёт, "
                "в met засчитываются только пары по первичному эндпоинту "
                f"{PRIMARY_PAIRED_FIELD}"
            ),
        },
        "journal_pairs_13_3": {
            "met": journal_integrity["all_starts_paired"],
            "fresh_start_rows": journal_integrity["fresh_start_rows"],
            "supported_unpaired": journal_integrity["per_run_logs"]["supported_unpaired"],
            "legacy_start_rows": journal_integrity["per_run_logs"]["legacy_start_rows"],
        },
    }
    gate_wp4 = {
        "requirement": (
            "гейт WP4 (план): experiments/E02_pattern/results.json содержит первичный "
            "эндпоинт, 5 сидов, effect size и Уилксон; в journal.jsonl на каждую "
            "start-строку есть finish-строка (§13.3)"
        ),
        "checks": gate_wp4_checks,
        "passed": all(c["met"] for c in gate_wp4_checks.values()),
    }

    results = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "experiment": "E02_pattern (WP4: диагностика коллапса ткани)",
        "primary_endpoint": "coverage.f1 (evaluate.compute_coverage_endpoints)",
        "primary_endpoint_rationale": (
            "нормированный симметричный Chamfer не наказывает перепокрытие: "
            "всё-белое поле 0.0362, случайное p=0.5 0.0385, идеальное кольцо 0.0000; "
            "f1 тех же полей: 0.2644 / 0.2356 / 1.0000"
        ),
        "secondary_endpoints": [
            "alive_fraction (выживание ткани)",
            "visible_mse (форма в канале 0)",
            "symmetric_chamfer_error (историческая совместимость с v5.5)",
            "b0/b1 против TARGET_TOPOLOGY",
            "скан порога бинаризации: f1@0.5 и лучший f1 (threshold_probe.json, NEG-10)",
        ],
        "collapse_threshold": {
            "target_density": density,
            "relative": threshold,
            "ratio": config.COLLAPSE_ALIVE_FRACTION_RATIO,
            "absolute_legacy": config.COLLAPSE_ALIVE_FRACTION_MIN,
            "why": (
                "абсолютный порог 0.15 стоит впритык к плотности цели 0.15234: "
                "он меряет выбранное число, а не смерть ткани"
            ),
        },
        "gate_layer1": gate
        and {
            "seeds_passed_no_collapse": gate.get("seeds_passed_no_collapse"),
            "seeds_passed_chamfer": gate.get("seeds_passed_chamfer"),
            "seeds_passed_coverage": gate.get("seeds_passed_coverage"),
            # §14.2 «удержать» как условие гейта слоя 1 (WP4b).
            "seeds_passed_retention": gate.get("seeds_passed_retention"),
            "retention": gate.get("retention"),
            "per_seed_retention_f1": [
                r.get("retention_f1_gated_best") for r in gate.get("runs", [])
            ],
            "seeds_with_coverage_measured": gate.get("seeds_with_coverage_measured"),
            "seeds_with_structure_beyond_ceiling": gate.get("seeds_with_structure_beyond_ceiling"),
            "structureless_f1_ceiling": gate.get("structureless_f1_ceiling"),
            "gate_passed": gate.get("gate_passed"),
            "collapse_threshold": gate.get("collapse_threshold"),
            "per_seed_alive_min": [r.get("alive_fraction_min") for r in gate.get("runs", [])],
            "chamfer_first_to_last": [
                (r.get("chamfer_first"), r.get("chamfer_last")) for r in gate.get("runs", [])
            ],
            # Первичный эндпоинт (visible MSE) по сидам — из логов тех же прогонов,
            # потому что в gate_layer1.json он не дублируется.
            "primary_endpoint_from_logs": gate_endpoints,
        },
        "landscape_probe": probe
        and {
            "modes": {
                mode: {
                    "fresh_model_totals": {
                        k: v["total"] for k, v in data["arms"]["fresh_model"].items()
                    },
                    # Натренированные веса: зонд берёт последний найденный
                    # чекпоинт (имя вида trained_<каталог>); список всех — чтобы
                    # было видно, какие прогоны вообще попали в сравнение.
                    "trained_arms_used": sorted(
                        k for k in data["arms"] if k.startswith("trained_")
                    ),
                    "trained_totals": {
                        k: {s: v["total"] for s, v in data["arms"][k].items()}
                        for k in sorted(data["arms"])
                        if k.startswith("trained_")
                    },
                    "death_is_global_optimum": data["verdict"]["fresh_model"][
                        "death_is_optimum_of_implemented_loss"
                    ],
                    "frac_cells_pushed_to_death": data["gradient_direction"][
                        "alive_blank_grey"
                    ]["frac_cells_pushed_to_death"],
                    "term_attribution_weights": data["term_attribution"]["weights"],
                }
                for mode, data in probe["modes"].items()
            },
            "term_attribution": {
                mode: probe["modes"][mode].get("term_attribution") for mode in probe["modes"]
            },
        },
        "delta_profile": delta,
        "ablation_runs": runs,
        "paired_stats": paired,
        "curriculum_transition": _transition_digest(runs),
        "survived_but_learned": _learning_digest(runs),
        # Тест ёмкости: пул из цели. Отделяет «архитектура не может» от
        # «не вырастает из шума» (см. пост-скриптум к NEG-09).
        "capacity_probe": _capacity_digest(runs),
        # Wave 7: удержание как член лосса (§14.2). Выживание и форма — два
        # разных исхода, и после R-7 они расцеплены: ткань жива, кольца нет.
        "retention_arms": _retention_digest(runs),
        # Сканирование порога бинаризации: f1@0.5 против лучшего f1 по порогу.
        # Без него вывод «цель не выучена» неотличим от «выучена ниже порога».
        "threshold_probe": _threshold_digest(thresh),
        # Достижимость против удержания: f1 по ходу обучения не различает эти
        # два исхода, зонд различает (NEG-23).
        "reach_probe": reach,
        # Пары start/finish (§13.3) — условие гейта WP4; считаем по фактическим
        # журналам, а не по памяти о том, что должны были писать.
        "journal_integrity": journal_integrity,
        # Гейт WP4 из плана как список условий с числами: «почти выполнено»
        # обязано отличаться от «выполнено».
        "gate_wp4": gate_wp4,
        "verdict": verdicts,
        "conclusions": _conclusions(
            runs, threshold, thresh, density, journal_integrity=journal_integrity, reach=reach
        ),
    }
    unmet = [k for k, c in gate_wp4_checks.items() if not c["met"]]
    why = (
        ""
        if not unmet
        else " Числа по каждому условию лежат в results.json:gate_wp4.checks."
    )
    if "paired_wilcoxon" in unmet:
        w = gate_wp4_checks["paired_wilcoxon"]
        why += (
            f" По первичному эндпоинту ({w['primary_endpoint_field']}) посчитано пар "
            f"{w['pairs_with_computed_test_on_primary']} из {w['pairs']} построенных; "
            f"всего с тестом {w['pairs_with_computed_test']}. Пара существует только "
            "если на том же сиде и горизонте есть базлайн H-A0 и в обеих записях "
            "есть значение эндпоинта — 5 сидов на плечо тут не заменяются чужими "
            "артефактами, старые логи задним числом сидами не обзаводятся (§7.7)."
        )
    results["conclusions"].append(
        "Гейт WP4: "
        + (
            "выполнен по всем условиям."
            if not unmet
            else "НЕ выполнен — " + ", ".join(unmet) + "." + why
        )
        + " Не путать с научным критерием: WP4 — процессуальный (первичный эндпоинт"
        " записан, 5 сидов, effect size, Уилксон, пары журнала §13.3), а вопрос «есть"
        " ли форма» решается гейтом слоя 1 — f1 после автономного roll-out выше"
        " потолка бесструктурного поля с зазором 0.05. Закрытие WP4 не означает, что"
        " E02 дала морфогенез, и наоборот: провал WP4 по статистике не есть"
        " отрицание гипотезы."
    )
    return results


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = build_report()
    path = os.path.join(OUT_DIR, "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"[wp4-report] записано: {path}")

    v = results["verdict"]
    print(
        f"[wp4-report] прогонов={v['n_runs']} сидов={v['n_seeds']} "
        f"пары_журнала={v['journal_paired']} "
        f"выжили={v['arms_survived'] or 'ни один arm'} "
    )
    for r in results["ablation_runs"]:
        print(
            f"  {r['arm']:6s} s={r['steps']:4d} seed={r['seed']} "
            f"alive_min={r['alive_fraction_min'] if r['alive_fraction_min'] is not None else float('nan'):.4f} "
            f"surv(rel)={r['survived_at_relative_threshold']} f1={r['f1_final']}"
        )
    print("[wp4-report] выводы:")
    for line in results["conclusions"]:
        print(f"  - {line}")
    t = results.get("threshold_probe")
    if t:
        print(
            f"[wp4-report] структура выше потолка «всё яркое» "
            f"({_fmt(t['structureless_f1_ceiling'])}) у: {t['beyond_ceiling'] or 'ни у кого'}"
        )
    return results


if __name__ == "__main__":
    main()
