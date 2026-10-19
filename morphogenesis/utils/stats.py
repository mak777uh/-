"""

stats.py — статистический слой (§12.1.11, §15.6).

[v5.6-EXP FINAL] Rev.11-IMPLEMENTATION-READY

Зачем: спека запрещает делать выводы (a) без power analysis, (b) без контрольной

ветки, (c) при множественных сравнениях без поправки на FDR, (d) по одному числу

вместо распределения. Здесь собраны ровно те инструменты, которыми это

проверяется; ничего «умнее» (модели, байесовские выводы) тут нет и не будет,

пока не появится эксперимент, которому это нужно.

Все функции чистые: принимают массивы чисел, возвращают dict/кортежи, ничего не

пишут на диск и не читают (кроме явных *_power_analysis helpers).

"""

import json

import math

import os

import numpy as np

from scipy import stats as sps

import config


# === Описательные статистики ===


def describe(values):
    """n / mean / median / std / min / max по конечным значениям."""
    arr = np.asarray(list(values), dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "std": None,
            "min": None,
            "max": None,
        }
    return {
        "n": int(arr.size),
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def paired_differences(a, b):
    """Попарные разности (попарность = один и тот же сид/ячейка в обеих ветках)."""
    a = np.asarray(list(a), dtype=np.float64)
    b = np.asarray(list(b), dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"Попарное сравнение требует равных длин: {a.shape} vs {b.shape}")
    keep = np.isfinite(a) & np.isfinite(b)
    return a[keep] - b[keep]


def rank_biserial(diff):
    """

    Rank-biserial correlation для попарных разностей: (R+ − R−) / (R+ + R−).

    Считаем сами, потому что scipy.wilcoxon для two-sided возвращает МЕНЬШУЮ из

    ранговых сумм и тем самым теряет знак эффекта.

    """
    diff = np.asarray(diff, dtype=np.float64)
    nonzero = diff[diff != 0]
    if nonzero.size == 0:
        return None
    ranks = sps.rankdata(np.abs(nonzero))
    r_plus = float(ranks[nonzero > 0].sum())
    r_minus = float(ranks[nonzero < 0].sum())
    total = r_plus + r_minus
    if total == 0:
        return None
    return (r_plus - r_minus) / total


def effect_size_paired(a, b):
    """

    Cohen's d_z для попарного сравнения: mean(diff) / std(diff).

    Возвращает dict с d_z и rank-biserial correlation (не требует нормальности).

    """
    diff = paired_differences(a, b)
    n = int(diff.size)
    if n == 0:
        return {"n": 0, "cohens_dz": None, "rank_biserial": None, "mean_diff": None}
    mean_diff = float(diff.mean())
    sd = float(diff.std(ddof=1)) if n > 1 else 0.0
    dz = mean_diff / sd if sd > 0 else None
    return {
        "n": n,
        "cohens_dz": dz,
        "rank_biserial": rank_biserial(diff),
        "mean_diff": mean_diff,
    }


def wilcoxon_paired(a, b, alternative="two-sided"):
    """Точный/асимптотический критерий Уилксона для попарных разностей."""
    diff = paired_differences(a, b)
    if diff.size == 0:
        raise ValueError("Нет конечных попарных наблюдений")
    nonzero = diff[diff != 0]
    if nonzero.size == 0:
        return {
            "test": "wilcoxon",
            "statistic": None,
            "p_value": 1.0,
            "n": int(diff.size),
            "n_nonzero": 0,
            "alternative": alternative,
            "note": "все разности нулевые — эффекта нет",
        }
    result = sps.wilcoxon(diff, alternative=alternative, zero_method="wilcox")
    return {
        "test": "wilcoxon",
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "n": int(diff.size),
        "n_nonzero": int(nonzero.size),
        "alternative": alternative,
    }


def bootstrap_ci(values, statistic=None, resamples=None, alpha=None, rng=None):
    """

    BCa-упрощённый (percentile) bootstrap CI для одной статистики.

    Возвращает dict(point, low, high, se, resamples).

    """
    arr = np.asarray(list(values), dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        raise ValueError("bootstrap требует >= 2 наблюдений")
    if statistic is None:
        statistic = np.mean
    if resamples is None:
        resamples = int(config.STATS_BOOTSTRAP_RESAMPLES)
    if alpha is None:
        alpha = float(config.STATS_ALPHA)
    if rng is None:
        rng = np.random.default_rng(config.SEED)
    boots = np.empty(resamples, dtype=np.float64)
    n = arr.size
    for i in range(resamples):
        idx = rng.integers(0, n, size=n)
        boots[i] = float(statistic(arr[idx]))
    lo = float(np.quantile(boots, alpha / 2.0))
    hi = float(np.quantile(boots, 1.0 - alpha / 2.0))
    return {
        "point": float(statistic(arr)),
        "low": lo,
        "high": hi,
        "se": float(boots.std(ddof=1)),
        "resamples": int(resamples),
        "level": 1.0 - alpha,
    }


# === Множественные сравнения ===


def benjamini_hochberg(p_values):
    """

    Поправка BH (§12.1.11, STATS_FDR_METHOD="benjamini-hochberg").

    Возвращает dict(adjusted, rejected, method, alpha) — rejected по сырым

    скорректированным p <= alpha.

    """
    p = np.asarray(list(p_values), dtype=np.float64)
    m = p.size
    if m == 0:
        return {"adjusted": [], "rejected": [], "method": config.STATS_FDR_METHOD, "alpha": None}
    alpha = float(config.STATS_ALPHA)
    order = np.argsort(p, kind="mergesort")  # детерминированная сортировка
    ranked = p[order]
    adj = ranked * m / (np.arange(1, m + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]  # enforcing монотонности
    adj = np.clip(adj, 0.0, 1.0)
    adjusted = np.empty(m, dtype=np.float64)
    adjusted[order] = adj
    return {
        "adjusted": [float(x) for x in adjusted],
        "rejected": [bool(x <= alpha) for x in adjusted],
        "method": config.STATS_FDR_METHOD,
        "alpha": alpha,
    }


# === Power analysis (§15.6) ===


def required_seeds_paired(effect_size, alpha=None, power=None):
    """

    Требуемое число попарных наблюдений (сидов) для эффекта d при двустороннем

    тесте. Нормальная аппроксимация парного t-теста: n = ((z_а + z_b) / d)^2.

    Спека требует Уилксон, но для расчёта мощности используется именно эта

    консервативная оценка; фактический тест — Уилксон (см. wilcoxon_paired).

    """
    if alpha is None:
        alpha = float(config.STATS_ALPHA)
    if power is None:
        power = float(config.STATS_POWER_TARGET)
    d = abs(float(effect_size))
    if not math.isfinite(d) or d <= 0:
        raise ValueError(f"effect_size должен быть конечным и > 0, получено {effect_size!r}")
    z_a = float(sps.norm.ppf(1.0 - alpha / 2.0))
    z_b = float(sps.norm.ppf(power))
    raw = ((z_a + z_b) / d) ** 2
    # +1 наблюдение на оценку дисперсии (стандартная поправка для малых выборок)
    return int(math.ceil(raw)) + 1


def power_analysis_record(
    experiment,
    control,
    treatment,
    metric_name="primary_endpoint",
    pilot_seeds=None,
    max_seeds=None,
    min_seeds=None,
):
    """

    Расчёт по пилотным данным и запись в формате §15.6.

    decision: run_main | underpowered_or_redesign | effect_too_small.

    """
    control = np.asarray(list(control), dtype=np.float64)
    treatment = np.asarray(list(treatment), dtype=np.float64)
    if pilot_seeds is None:
        pilot_seeds = int(config.STATS_PILOT_SEEDS)
    if max_seeds is None:
        max_seeds = int(config.STATS_MAX_SEEDS)
    if min_seeds is None:
        min_seeds = int(config.STATS_MIN_SEEDS)
    if control.size != treatment.size:
        raise ValueError("Пилотные ветки должны быть попарными (одинаковое число сидов)")

    diffs = paired_differences(treatment, control)
    stats = effect_size_paired(treatment, control)
    dz = stats["cohens_dz"]
    variance = float(diffs.var(ddof=1)) if diffs.size > 1 else 0.0
    effect = float(dz) if dz is not None else 0.0

    if effect == 0.0:
        required = max_seeds + 1
    else:
        required = required_seeds_paired(effect)

    if required > max_seeds:
        decision = "underpowered_or_redesign"
    elif abs(effect) < float(config.STATS_EFFECT_SIZE_MIN_INTEREST):
        # Эффект меньше минимального интересного — гонять 30 сидов бессмысленно.
        decision = "effect_too_small"
    else:
        decision = "run_main"

    return {
        "experiment": experiment,
        "metric": metric_name,
        "pilot_seeds": int(pilot_seeds),
        "observed_pilot_n": int(diffs.size),
        "effect_size": effect,
        "effect_size_kind": "cohens_dz_paired",
        "mean_diff": stats["mean_diff"],
        "rank_biserial": stats["rank_biserial"],
        "variance": variance,
        "alpha": float(config.STATS_ALPHA),
        "power_target": float(config.STATS_POWER_TARGET),
        "required_seeds": int(required),
        "min_seeds": int(min_seeds),
        "max_seeds": int(max_seeds),
        "decision": decision,
        "timestamp": _utc_iso(),
    }


def _utc_iso():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def save_power_analysis(record, path=None):
    """

    Добавляет/обновляет запись в memory/power_analysis.json (§15.6).

    Файл — dict по именам экспериментов, чтобы несколько прогонов не перезаписывали

    друг друга; старый плоский формат мигрируется автоматически.

    """
    if path is None:
        path = config.POWER_ANALYSIS_PATH
    records = _load_raw(path)
    key = record.get("experiment", "unknown")
    records[key] = record
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return path


def _load_raw(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "experiment" in data:
        return {data["experiment"]: data}
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {str(item.get("experiment", i)): item for i, item in enumerate(data)}
    return {}


def load_power_analysis(experiment, path=None):
    """Запись power analysis для конкретного эксперимента (или None)."""
    if path is None:
        path = config.POWER_ANALYSIS_PATH
    return _load_raw(path).get(experiment)


def assert_power_analysis_ready(experiment, path=None):
    """

    Гейт перед ОСНОВНЫ прогоном (§15.6, §23): без сохранённого power analysis

    основной прогон запрещён. Также запрещён underpowered-вердикт.

    """
    if not bool(getattr(config, "STATS_POWER_ANALYSIS_REQUIRED", True)):
        return None
    if path is None:
        path = config.POWER_ANALYSIS_PATH
    record = _load_raw(path).get(experiment)
    if record is None:
        raise RuntimeError(
            f"{experiment}: нет записи power analysis в {path}. "
            "Основной прогон запрещён (§15.6). Сначала прогнать пилот "
            f"({config.STATS_PILOT_SEEDS} сидов) и сохранить результат."
        )
    decision = record.get("decision")
    if decision != "run_main":
        raise RuntimeError(
            f"{experiment}: power analysis decision={decision!r} (не run_main), "
            f"required_seeds={record.get('required_seeds')} при "
            f"max_seeds={record.get('max_seeds')}. Прогон запрещён (§15.6)."
        )
    required = int(record.get("required_seeds", 0))
    seeds = max(required, int(config.STATS_MIN_SEEDS))
    if seeds > int(config.STATS_MAX_SEEDS):
        raise RuntimeError(
            f"{experiment}: требуемое число сидов {seeds} > STATS_MAX_SEEDS"
        )
    return seeds


# === Период-свип (E08; используется слоем 4, здесь только инструмент) ===


def compare_against_baseline(values, baseline_value, threshold_ratio=None):
    """Доля значений, превышающих baseline*(1+threshold_ratio), + описательная статистика."""
    arr = np.asarray(list(values), dtype=np.float64)
    if threshold_ratio is None:
        threshold_ratio = 0.2
    thr = float(baseline_value) * (1.0 + float(threshold_ratio))
    above = arr[arr > thr]
    return {
        "baseline": float(baseline_value),
        "threshold": thr,
        "n_above": int(above.size),
        "fraction_above": float(above.size / arr.size) if arr.size else 0.0,
        "summary": describe(arr),
    }
