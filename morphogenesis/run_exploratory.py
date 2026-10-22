"""run_exploratory.py — запуск exploratory-скрипта под парой start/finish в журнале.

Зачем. Exploratory-скрипты E02b (`experiments/E02b_morphospace/scripts/*.py`)
исполняют работу на уровне модуля: у них нет `main()` и нет `__main__`-блока,
поэтому они не писали пару `start`/`finish` в `logs/journal.jsonl`. Семь таких
прогонов закрылись с манифестом и stdout, но без пары в журнале
(`lab/state.json` → `blockers`). Дописывать журнал задним числом запрещено
([`AGENTS.md`](../AGENTS.md) §2), поэтому чинится **процесс**: этот лаунчер
запускает скрипт как есть через `runpy`, но оборачивает его в журнал.

Запуск (из корня репозитория, лучше через лабораторную обёртку):

    python scripts/lab.py run \\
      --experiment E02b_channel_memory --experiment-id E02b --owner lead \\
      -- .venv/Scripts/python.exe run_exploratory.py \\
         --script experiments/E02b_morphospace/scripts/e02b_channel_memory.py \\
         --experiment E02b_channel_memory --note "повтор H-CH-1"

Почему `runpy`, а не импорт: скрипты пишут артефакты на уровне модуля и ждут
`__file__`. `runpy.run_path` даёт им ровно тот же контекст, что и прямой запуск,
но под нашим `try/except`.

Ограничение: лаунчер не знает, какой артефакт считает «результатом» — он
фиксирует время, скрипт и статус. Манифест с артефактами по-прежнему пишет
`scripts/lab.py run` (`--output`), и это осознанно: журнал отвечает за пару
событий, манифест — за входы и выходы.
"""
from __future__ import annotations

import argparse
import os
import runpy
import sys
import time

import config

from utils.logging import Journal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--script", required=True, help="путь к exploratory-скрипту")
    parser.add_argument(
        "--experiment",
        required=True,
        help="имя эксперимента для журнала (совпадает с именем артефакта)",
    )
    parser.add_argument("--note", default="", help="короткая пометка, зачем запуск")
    parser.add_argument("--device", default=None, help="подсказка для журнала (cuda/cpu)")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.script):
        print(f"[exploratory] нет скрипта: {args.script}", file=sys.stderr)
        return 2

    journal = Journal(experiment=args.experiment)
    started = time.time()
    journal.start(
        script=args.script,
        note=args.note,
        device=args.device or str(config.DEVICE),
        emits_run_finish=True,
        runner="run_exploratory.py",
    )
    try:
        runpy.run_path(args.script, run_name="__main__")
    except SystemExit as exc:
        # Скрипт может завершаться `raise SystemExit(main())`: это нормальный
        # выход, а не ошибка. Раньше любой SystemExit писался в журнал как
        # error, и успешный прогон (`error: "0"`) выглядел проваленным.
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        if code == 0:
            journal.finish(stop_reason="finished", wall_seconds=round(time.time() - started, 1))
            return 0
        journal.error(exc, wall_seconds=round(time.time() - started, 1))
        return code
    except BaseException as exc:  # start без finish = оборванный прогон (§6)
        journal.error(exc, wall_seconds=round(time.time() - started, 1))
        raise
    journal.finish(stop_reason="finished", wall_seconds=round(time.time() - started, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
