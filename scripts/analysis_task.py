#!/usr/bin/env python
"""analysis_task.py — ферма CPU-задач на GitHub Actions: берёт задачу из очереди и считает.

Зачем: у нас есть класс работы, который не требует GPU и который иначе не делается —
интервалы, перестановки, независимый пересчёт, расчёты мощности. GitHub даёт бесплатные
стандартные раннеры для публичного репозитория, 20 параллельных задач и 6 часов на задачу.

**Принципиальная граница:** очередь задач пишет человек (ведущий), а ферма только исполняет.
Ферма не придумывает анализы — иначе это ровно тот «сад расходящихся тропок», против которого
мы работаем: машина, перебирающая варианты, найдёт «эффект» где угодно.

Задачи (`lab/analysis-queue.json`, поле `kind`):
  proportion       — интервал Уилсона + bootstrap для доли k/n (простые числа из утверждений);
  rho_drop_whale   — корреляция признак↔приспособленность с крупнейшей линией и без неё;
  recompute_i      — независимый пересчёт I_obs, I_null(95 %), медиан и числа сидов выше нуля;
  power_lines      — сколько линий нужно, чтобы df ≥ 4 при частной корреляции.

Запуск:
    python scripts/analysis_task.py --list
    python scripts/analysis_task.py --run <task_id>          # считает и пишет результат
    python scripts/analysis_task.py --run <task_id> --dry    # только проверить, что задача валидна
Коды выхода: 0 — успех, 1 — ошибка, 3 — задача не найдена/не pending (не ошибка).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import inspect
import json
import math
import statistics as st
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
QUEUE = ROOT / "lab" / "analysis-queue.json"
OUTDIR = POND / "analysis"


# ---------------------------------------------------------------- утилиты
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 3:
        return float("nan")
    def rank(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    rx -= rx.mean(); ry -= ry.mean()
    den = math.sqrt(float((rx ** 2).sum()) * float((ry ** 2).sum()))
    return float((rx * ry).sum() / den) if den else float("nan")


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """ρ(x, y | z) через ранги (частная корреляция Спирмена)."""
    if min(x.size, y.size, z.size) < 4:
        return float("nan")
    def rank(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v)); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry, rz = rank(x), rank(y), rank(z)
    def resid(a, b):
        b1 = np.vstack([np.ones_like(b), b]).T
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef
    ex, ey = resid(rx, rz), resid(ry, rz)
    den = math.sqrt(float((ex ** 2).sum()) * float((ey ** 2).sum()))
    return float((ex * ey).sum() / den) if den else float("nan")


def crow(w: np.ndarray) -> float:
    """Возможность отбора I = Var(w)/mean(w)² (выборочная дисперсия, ddof=1)."""
    if w.size < 2:
        return 0.0
    m = float(w.mean())
    if m <= 0:
        return 0.0
    return float(w.var(ddof=1) / (m * m))


def i_null_95(cells: np.ndarray, rate: float, draws: int = 2000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    lam = np.maximum(rate * cells, 1e-12)
    vals = np.empty(draws)
    for i in range(draws):
        vals[i] = crow(rng.poisson(lam).astype(float) / np.maximum(cells, 1))
    return float(np.percentile(vals, 95))


def load_summary(path: Path) -> dict:
    return (json.loads(path.read_text(encoding="utf-8")) or {}).get("summary") or {}


def lineages(summary: dict, min_cells: int = 1, min_spores: int = 0) -> dict:
    cells = {k[1:]: float(v) for k, v in (summary.get("type_counts") or {}).items()}
    spores = {k: float((summary.get("lineage_spores") or {}).get(k, 0)) for k in cells}
    # ВНИМАНИЕ: type_traits ключуется как "T<id>", а type_counts/lineage_* — как "<id>".
    # Ровно эта разница ключей уже стоила нам ложного «признак не влияет» (B-061, 25.10),
    # поэтому смотрим оба варианта, а не только один.
    raw_traits = summary.get("type_traits") or {}
    traits = {k: float(raw_traits.get(f"T{k}", raw_traits.get(k, 0.0))) for k in cells}
    steps = {k: float((summary.get("lineage_cell_steps") or {}).get(k, 0)) for k in cells}
    keep = [k for k in cells if cells[k] >= min_cells and spores[k] >= min_spores]
    return {"keys": keep, "cells": cells, "spores": spores, "traits": traits, "steps": steps}


# ---------------------------------------------------------------- задачи
def task_proportion(spec: dict) -> dict:
    k, n = int(spec["k"]), int(spec["n"])
    if not (0 <= k <= n) or n <= 0:
        raise ValueError(f"некорректная доля: k={k}, n={n}")
    lo, hi = wilson(k, n)
    rng = np.random.default_rng(int(spec.get("seed", 0)))
    draws = int(spec.get("bootstrap", 10000))
    if k in (0, n):
        boot = (0.0 if k == 0 else 1.0, 0.0 if k == 0 else 1.0)
        note = "граница диапазона: bootstrap вырожден, использовать Уилсона"
    else:
        samples = rng.binomial(n, k / n, draws) / n
        boot = (float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))
        note = ""
    return {
        "k": k, "n": n, "p": round(k / n, 4),
        "wilson95": [round(lo, 4), round(hi, 4)],
        "bootstrap95": [round(boot[0], 4), round(boot[1], 4)],
        "bootstrap_draws": draws, "note": note,
    }


def task_rho_drop_whale(spec: dict) -> dict:
    pattern = spec.get("glob") or "w2bud3/w2bud3_cell_seed*.json"
    min_cells = int(spec.get("min_cells", 5))
    rows = []
    for f in sorted(POND.glob(pattern)):
        s = load_summary(f)
        L = lineages(s, min_cells=min_cells, min_spores=1)
        keys = L["keys"]
        if len(keys) < 3:
            continue
        cells = np.array([L["cells"][k] for k in keys])
        spores = np.array([L["spores"][k] for k in keys])
        traits = np.array([L["traits"][k] for k in keys])
        steps = np.array([L["steps"][k] for k in keys])
        w = spores / np.maximum(cells, 1)
        full = spearman(traits, w)
        top = int(np.argmax(cells))
        mask = np.ones(len(keys), bool); mask[top] = False
        drop = spearman(traits[mask], w[mask]) if mask.sum() >= 3 else float("nan")
        energy_map = s.get("energy_per_cell_time_by_lineage") or {}
        if energy_map:
            energy = np.array([float(energy_map.get(k, 0.0)) for k in keys])
            rho_partial = partial_spearman(traits, steps, energy)
        else:
            rho_partial = float("nan")
        rows.append({"file": f.name, "lines": len(keys), "rho_full": round(full, 4),
                     "rho_without_whale": round(drop, 4), "rho_partial": round(rho_partial, 4),
                     "whale_share": round(float(cells[top] / cells.sum()), 4)})
    if not rows:
        raise ValueError(f"нет данных по маске {pattern}")
    def med(key):
        vals = [r[key] for r in rows if isinstance(r[key], (int, float)) and not math.isnan(r[key])]
        return round(st.median(vals), 4) if vals else None
    return {
        "runs": len(rows), "min_cells": min_cells,
        "median_rho_full": med("rho_full"),
        "median_rho_without_whale": med("rho_without_whale"),
        "median_rho_partial": med("rho_partial"),
        "sign_full_k": sum(1 for r in rows if r["rho_full"] < 0),
        "sign_without_whale_k": sum(1 for r in rows if r["rho_without_whale"] < 0),
        "median_whale_share": med("whale_share"),
        "rows": rows,
        "verdict": _whale_verdict(med("rho_full"), med("rho_without_whale")),
    }


def task_recompute_i(spec: dict) -> dict:
    pattern = spec.get("glob") or "w2bud3/w2bud3_cell_seed*.json"
    min_cells = int(spec.get("min_cells", 5))
    draws = int(spec.get("draws", 2000))
    obs, nulls, ratios, above, lines = [], [], [], 0, []
    for i, f in enumerate(sorted(POND.glob(pattern))):
        s = load_summary(f)
        L = lineages(s, min_cells=min_cells, min_spores=1)
        keys = L["keys"]
        lines.append(len(keys))
        if len(keys) < 2:
            continue
        cells = np.array([L["cells"][k] for k in keys])
        spores = np.array([L["spores"][k] for k in keys])
        w = spores / np.maximum(cells, 1)
        i_obs = crow(w)
        rate = float(spores.sum() / max(cells.sum(), 1e-12))
        i_null = i_null_95(cells, rate, draws=draws, seed=i)
        obs.append(i_obs); nulls.append(i_null)
        if i_null > 0:
            ratios.append(i_obs / i_null)
        above += 1 if i_obs > i_null else 0
    if not obs:
        raise ValueError(f"нет данных по маске {pattern}")
    return {
        "runs": len(lines), "min_cells": min_cells, "null_draws": draws,
        "I_obs_median": round(st.median(obs), 4),
        "I_null_95_median": round(st.median(nulls), 4),
        "I_ratio_median": round(st.median(ratios), 3) if ratios else None,
        "I_ratio_of_medians": round(st.median(obs) / st.median(nulls), 3) if st.median(nulls) > 0 else None,
        "above_null_k": above,
        "lines_median": round(float(np.median(lines)), 2),
    }


def task_power_lines(spec: dict) -> dict:
    """Сколько линий нужно, чтобы df = n − 3 ≥ 4 (то есть n ≥ 7) при данной связи признака."""
    betas = [float(b) for b in (spec.get("betas") or [0.001, 0.002, 0.005])]
    ns = [int(n) for n in (spec.get("ns") or [4, 5, 6, 7, 8, 10, 12])]
    eps = float(spec.get("eps", 4.0))
    sigma = float(spec.get("trait_sigma", 0.05))
    reps = int(spec.get("reps", 400))
    rng = np.random.default_rng(int(spec.get("seed", 0)))
    out = []
    for n in ns:
        row = {"lines": n, "df": n - 3}
        for beta in betas:
            hits = 0
            for _ in range(reps):
                trait = rng.normal(0, sigma, n)
                rate = np.exp(np.clip(beta * (trait - trait.mean()) * eps / max(sigma, 1e-9), -20, 20))
                cells = np.maximum(rng.poisson(30 / np.maximum(rate, 1e-9) * 1.0), 3).astype(float)
                spores = rng.poisson(cells * rate * 0.05 + 1e-9).astype(float)
                w = spores / np.maximum(cells, 1)
                rho = spearman(trait, w)
                hits += 1 if (not math.isnan(rho) and abs(rho) >= 0.5) else 0
            row[f"beta_{beta}"] = round(hits / reps, 3)
        out.append(row)
    return {"eps": eps, "trait_sigma": sigma, "reps": reps,
            "note": "доля симуляций, где |ρ| ≥ 0.5 — порог манипуляционной проверки",
            "grid": out}






def _git(args: list[str]) -> str:
    """Короткий вызов git; при недоступности возвращает пустую строку."""
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20)
        return out.stdout.strip()
    except Exception:
        return ""

def _whale_verdict(full, drop) -> str:
    """Вердикт про крупнейшую линию. Отсутствие данных — не «эффект пропал»,
    и «0.5 против 0.0» — не «знак не изменился»: сравнивать надо и величину."""
    if full is None or drop is None:
        return "недостаточно данных: корреляция не вычислима (меньше трёх линий или нет признака)"
    if abs(drop) < 0.2 and abs(full) >= 0.3:
        return (f"связь держится на крупнейшей линии: ρ {full:+.3f} → {drop:+.3f} без неё "
                f"(|ρ| < 0.2) — это не популяционная статистика")
    if (full < 0) != (drop < 0):
        return f"знак МЕНЯЕТСЯ без крупнейшей линии ({full:+.3f} → {drop:+.3f}) — эффект может быть её свойством"
    return f"знак устойчив к исключению крупнейшей линии ({full:+.3f} → {drop:+.3f})"

TASKS = {
    "proportion": task_proportion,
    "rho_drop_whale": task_rho_drop_whale,
    "recompute_i": task_recompute_i,
    "power_lines": task_power_lines,
}


# ---------------------------------------------------------------- исполнение
def load_queue() -> dict:
    if not QUEUE.exists():
        return {"tasks": []}
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def save_queue(q: dict) -> None:
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_task(task: dict) -> Path:
    kind = task.get("kind")
    if kind not in TASKS:
        raise ValueError(f"неизвестный kind: {kind}")
    result = TASKS[kind](task.get("spec") or {})
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"{task['id']}.json"
    payload = {
        "kind": kind,
        "task": task["id"],
        "question": task.get("question", ""),
        "spec": task.get("spec") or {},
        "result": result,
        # Провенанс. Урок 26.10: хеш «сырых байт файла» зависит от перевода строк
        # (рабочая копия Windows — CRLF, блоб в git — LF), поэтому один и тот же код
        # давал разные хеши, и связать результат с коммитом было нельзя без догадки.
        # Теперь пишем то, что не зависит от платформы: коммит и признак «файл грязный».
        "git_commit": _git(["rev-parse", "--short", "HEAD"]),
        "script_dirty": bool(_git(["status", "--porcelain", "scripts/analysis_task.py"])),
        # Хеш именно той функции, которая считала: иначе любая правка скрипта
        # «переписывает» провенанс всех старых результатов (замечание библиотекаря 26.10).
        "task_fn_sha256": hashlib.sha256(inspect.getsource(TASKS[kind]).encode()).hexdigest()[:16],
        "script_sha256_eol_dependent": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16],
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="ферма CPU-задач (GitHub Actions)")
    ap.add_argument("--list", action="store_true", help="показать очередь")
    ap.add_argument("--pending", action="store_true", help="напечатать id pending-задач (для matrix)")
    ap.add_argument("--run", metavar="ID", help="выполнить задачу")
    ap.add_argument("--limit", type=int, default=0, help="сколько pending печатать")
    ap.add_argument("--dry", action="store_true", help="не писать результат")
    ap.add_argument("--mark-done", action="store_true", help="пометить выполненной (по умолчанию да)")
    args = ap.parse_args(argv)

    q = load_queue()
    tasks = q.get("tasks", [])

    if args.list:
        for t in tasks:
            print(f"{t['id']:28s} {t.get('status', '?'):10s} {t.get('kind', '?'):16s} {t.get('question', '')[:60]}")
        return 0

    if args.pending:
        ids = [t["id"] for t in tasks if t.get("status") == "pending"]
        if args.limit:
            ids = ids[: args.limit]
        print(json.dumps(ids))
        return 0

    if not args.run:
        ap.print_help()
        return 0

    task = next((t for t in tasks if t["id"] == args.run), None)
    if not task:
        print(f"[analysis] задача {args.run} не найдена")
        return 3
    if task.get("status") not in ("pending", "running"):
        print(f"[analysis] задача {args.run} в статусе {task.get('status')} — пропускаю")
        return 3

    if args.dry:
        kind = task.get("kind")
        print(f"[analysis] задача {args.run}: kind={kind}, spec={json.dumps(task.get('spec') or {}, ensure_ascii=False)[:120]}")
        return 0 if kind in TASKS else 1

    out = run_task(task)
    if args.mark_done:
        task["status"] = "done"
        save_queue(q)
    print(f"[analysis] {args.run}: готово → {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
