#!/usr/bin/env python
"""farm_reader.py — читать результаты фермы GitHub Actions.

Зачем (26.10): ферма пишет результаты коммитом в `analysis/`, но **читать их было нечем**:
никто не делал `git pull`, никто не проверял, что задача вообще отработала, и «нет
результатов» было неотличимо от «ферма не запускалась». Владелец спросил — и оказалось,
что за всё время ферма не оставила ни одного коммита.

Что делает:
  1) `--pull` — забирает коммиты фермы из origin (по умолчанию не делает, чтобы не мешать);
  2) сводка по всем задачам: kind, вердикт, ключевые числа, провенанс (`script_commit`);
  3) статусы прогонов из `analysis/farm-status.json` — включая упавшие;
  4) помечает проблемы: задачи без результата, результаты с устаревшим `script_commit`,
     вердикты «недостаточно данных», прогоны со статусом failure;
  5) пишет человекочитаемый `reports/farm-latest.md`.

Запуск:
    python scripts/farm_reader.py            # только прочитать
    python scripts/farm_reader.py --pull     # сначала git pull --rebase
    python scripts/farm_reader.py --strict   # код 1 при найденных проблемах (для цикла)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "analysis"
QUEUE = ROOT / "lab" / "analysis-queue.json"
REPORT = ROOT / "reports" / "farm-latest.md"
STATUS = ANALYSIS / "farm-status.json"

KEY_FIELDS = {
    "proportion": ("p", "wilson95", "bootstrap95", "n"),
    "rho_drop_whale": ("median_rho_full", "median_rho_without_whale", "verdict"),
    "recompute_i": ("I_obs_median", "I_null_95_median", "I_ratio_median", "above_null_k"),
    "power_lines": ("eps", "trait_sigma", "note"),
}


def git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def load_queue() -> dict:
    if not QUEUE.exists():
        return {"tasks": []}
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="чтение результатов фермы")
    ap.add_argument("--pull", action="store_true", help="сначала git pull --rebase")
    ap.add_argument("--strict", action="store_true", help="код 1 при проблемах")
    ap.add_argument("--quiet", action="store_true", help="только короткий итог")
    args = ap.parse_args(argv)

    if args.pull:
        if git(["status", "--porcelain"]):
            print("[farm] рабочая копия грязная — pull не делаю (сначала коммит)")
        else:
            out = git(["pull", "--rebase", "--quiet"])
            print("[farm] pull:", out or "ок")

    q = load_queue()
    by_id = {t["id"]: t for t in q.get("tasks", [])}
    results, problems = [], []

    # статусы прогонов
    runs = []
    if STATUS.exists():
        try:
            runs = json.loads(STATUS.read_text(encoding="utf-8")).get("runs", [])
        except Exception as exc:
            problems.append(f"farm-status.json не читается: {exc}")

    for f in sorted(ANALYSIS.glob("*.json")):
        if f.name in ("provenance-legacy.json", "farm-status.json"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{f.name}: не читается ({exc})")
            continue
        res = d.get("result") or {}
        kind = d.get("kind") or ""
        entry = {
            "file": f.name, "task": d.get("task"), "kind": kind,
            "question": d.get("question", ""),
            "numbers": {k: res.get(k) for k in KEY_FIELDS.get(kind, ()) if k in res},
            "verdict": res.get("verdict", ""),
            "script_commit": d.get("script_commit"),
            "script_dirty": d.get("script_dirty"),
            "mtime": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        }
        if "недостаточно данных" in str(entry["verdict"]):
            problems.append(f"{f.name}: вердикт «недостаточно данных» — задача посчитана, вывод не получен")
        if entry["script_dirty"] is True:
            problems.append(f"{f.name}: посчитано изменённым скриптом (script_dirty) — провенанс неполный")
        if not entry["script_commit"] and entry["kind"]:
            problems.append(f"{f.name}: нет script_commit — результат старого формата, связь с кодом только по карте")
        results.append(entry)

    # задачи из очереди без результата
    done_files = {r["task"] for r in results}
    missing = [t["id"] for t in q.get("tasks", []) if t.get("status") == "pending" and t["id"] not in done_files]

    if not args.quiet:
        print(f"[farm] результатов: {len(results)}; задач в очереди: {len(q.get('tasks', []))}; "
              f"прогонов в статусе: {len(runs)}")
        for r in results:
            line = f"  {str(r['task'])[:32]:34s} {r['kind']:16s} {r['mtime']}"
            if r["numbers"]:
                line += "  " + ", ".join(f"{k}={v}" for k, v in list(r["numbers"].items())[:3])
            print(line)
        if runs:
            last = runs[-1]
            print(f"[farm] последний прогон: {last.get('result')} ({last.get('at')}) "
                  f"задачи={len(last.get('planned') or [])}")
            for run in runs[-3:]:
                if str(run.get("result")) != "success":
                    problems.append(f"прогон {run.get('run_id')} завершился «{run.get('result')}» — смотреть {run.get('url')}")
        else:
            problems.append("farm-status.json отсутствует: ферма ни разу не отработала (или пишет только при успехе)")
        if missing:
            problems.append(f"в очереди pending без результата: {', '.join(missing[:6])}")

    for p in problems:
        print(f"[farm] ВНИМАНИЕ: {p}")

    # человекочитаемый отчёт
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Ферма CPU-задач: последние результаты", "",
             f"Обновлено: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC. "
             "Источник — `morphogenesis/experiments/E09_pond/analysis/`.", "",
             "| задача | вид | вердикт | ключевые числа | провенанс |", "|---|---|---|---|---|"]
    for r in results:
        nums = ", ".join(f"{k}={v}" for k, v in r["numbers"].items())
        lines.append(f"| `{r['task']}` | {r['kind']} | {r['verdict'] or '—'} | {nums or '—'} | "
                     f"{r['script_commit'] or 'нет'}{' (dirty)' if r['script_dirty'] else ''} |")
    if problems:
        lines += ["", "## Проблемы", ""] + [f"- {p}" for p in problems]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    if not args.quiet:
        print(f"[farm] отчёт: {REPORT.relative_to(ROOT)}")

    return 1 if (args.strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
