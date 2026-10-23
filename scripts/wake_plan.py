#!/usr/bin/env python
"""Когда будить ведущего: вместо «каждый час» — по состоянию работы.

Пробуждение по часам дорого и бессмысленно, когда ничего не считается. Скрипт смотрит
на реальное состояние и говорит, когда имеет смысл следующий ход:

  * RUNNING — идёт серия (есть замок или свежие артефакты): будить к ожидаемому
    финишу: остаток = ожидаемое время серии минус прошедшее;
  * JUST_FINISHED — свежие артефакты/коммиты (последние 15 минут): будить сейчас;
  * IDLE — ничего не считается и не менялось: будить через 2–3 часа, не чаще.

Запуск:
    python scripts/wake_plan.py          # рекомендация в минутах и причина
    python scripts/wake_plan.py --json   # машиночитаемо
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLISH = ROOT.parent / "_hourly" / "polish"
RUNS = ROOT / "lab" / "runs"
LOCKS = ROOT / "lab" / "locks"

# ожидаемая длительность одного прогона пруда, секунды (300 шагов на 32×32)
RUN_SECONDS = 70
DEFAULT_SERIES = 18       # типичная серия: 3 политики × 3 режима × 2 сида
SERIES_IN_PROGRESS_SHARE = 0.6


def newest_mtime(paths: list[str]) -> float | None:
    times = [os.path.getmtime(p) for p in paths if os.path.exists(p)]
    return max(times) if times else None


def git_recent_commits(minutes: int = 15) -> int:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--since", f"{minutes} minutes ago", "--oneline"],
            capture_output=True, text=True, timeout=10,
        )
        return len([line for line in out.stdout.splitlines() if line.strip()])
    except (OSError, subprocess.SubprocessError):
        return 0


STATE = ROOT.parent / "_hourly" / "wake_state.json"


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(data: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def plan() -> dict:
    locks = glob.glob(str(LOCKS / "*.lock"))
    artifacts = glob.glob(str(POLISH / "*.json")) + glob.glob(str(RUNS / "*.json"))
    last = newest_mtime(artifacts + locks)
    now = time.time()
    age_min = (now - last) / 60 if last else 1e6

    if locks:
        # серия идёт: прикидываем остаток по числу готовых артефактов
        done = len(glob.glob(str(POLISH / "*.json")))
        expected = max(DEFAULT_SERIES, done)
        remaining_runs = max(expected - done, 1)
        wake = max(2, int(remaining_runs * RUN_SECONDS * SERIES_IN_PROGRESS_SHARE / 60) + 1)
        return {"state": "running", "wake_in_min": wake,
                "why": f"замок активен, готово {done} артефактов из ~{expected}"}

    # что-то произошло с прошлого пробуждения? если нет — это не «только что», а тишина
    state = load_state()
    seen = float(state.get("last_active_mtime", 0))
    last_active = last or 0.0
    fresh = last_active > seen
    save_state({"last_active_mtime": max(last_active, seen),
                "last_check_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")})

    if fresh and age_min <= 15:
        return {"state": "just_finished", "wake_in_min": 2,
                "why": f"новая активность {age_min:.0f} мин назад (не видели раньше)"}

    if not fresh and age_min <= 15:
        return {"state": "waiting", "wake_in_min": 45,
                "why": "активность та же, что на прошлой проверке — новых результатов нет"}

    if age_min < 120:
        return {"state": "waiting", "wake_in_min": max(15, int(120 - age_min)),
                "why": f"последняя активность {age_min:.0f} мин назад, серия не идёт"}

    return {"state": "idle", "wake_in_min": 150,
            "why": f"тишина {age_min/60:.1f} ч: ничего не считается"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = plan()
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"состояние: {result['state']}")
        print(f"следующее пробуждение: через {result['wake_in_min']} мин")
        print(f"почему: {result['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
