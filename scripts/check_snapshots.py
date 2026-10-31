"""check_snapshots.py — снимки лабораторного состояния обязаны совпадать с диском.

Зачем. 31.10 `lab/checkpoints.json` утверждал `ready: 12, missing: []`, а на диске из двенадцати канонических весов
лежал **один**. Гейты этого не видели: снимок проверялся сам собой. Ошибку нашёл случай — при измерении занятого
места. Класс ошибки: **снимок обещает то, чего нет**.

Здесь проверяются две вещи, обе машинно:

1. **чекпоинты**: для каждого требования `requirements.<exp>` пересчитывается, какие файлы реально существуют, и
   сравнивается с заявленным `ready` / `missing`;
2. **замки и прогоны**: каждый `active_runs` в `lab/state.json` обязан иметь живой замок или манифест со статусом
   `running`; каждый замок `lab/locks/*.lock` — живой процесс владельца или честно просроченный.

Запуск:
    python scripts/check_snapshots.py            # отчёт
    python scripts/check_snapshots.py --ci       # падение при расхождении
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _paths(root: Path) -> dict:
    lab = root / "lab"
    return {"state": lab / "state.json", "checkpoints": lab / "checkpoints.json",
            "locks": lab / "locks", "runs": lab / "runs"}


def check_checkpoints(root: Path) -> list[str]:
    problems: list[str] = []
    p = _paths(root)["checkpoints"]
    if not p.is_file():
        return ["нет lab/checkpoints.json"]
    data = json.loads(p.read_text(encoding="utf-8"))
    for exp, req in (data.get("requirements") or {}).items():
        items = req.get("items") or []
        if not items:
            continue
        real_ready = [it for it in items if it.get("path") and (root / it["path"]).is_file()]
        declared = req.get("ready")
        if declared is not None and int(declared) != len(real_ready):
            problems.append(
                f"checkpoints.{exp}: заявлено ready={declared}, на диске {len(real_ready)} из {len(items)} — "
                f"снимок обещает то, чего нет (пересоберите: python scripts/lab.py state)"
            )
        declared_missing = len(req.get("missing") or [])
        real_missing = len(items) - len(real_ready)
        if declared is not None and declared_missing != real_missing:
            problems.append(
                f"checkpoints.{exp}: заявлено missing={declared_missing}, реально отсутствует {real_missing}"
            )
    return problems


def check_state_locks(root: Path) -> list[str]:
    problems: list[str] = []
    paths = _paths(root)
    if not paths["state"].is_file():
        return ["нет lab/state.json"]
    state = json.loads(paths["state"].read_text(encoding="utf-8"))
    locks = {p.stem for p in paths["locks"].glob("*.lock")} if paths["locks"].is_dir() else set()
    active = state.get("active_runs") or []
    for run_id in active:
        if run_id in locks:
            continue
        manifest = paths["runs"] / f"{run_id}.json"
        if manifest.is_file():
            status = json.loads(manifest.read_text(encoding="utf-8")).get("status")
            if status == "running":
                continue
        problems.append(f"state.active_runs: {run_id} числится активным, но нет ни замка, ни манифеста running")
    for lock in sorted(locks):
        if lock in active:
            continue
        manifest = paths["runs"] / f"{lock}.json"
        if manifest.is_file():
            status = json.loads(manifest.read_text(encoding="utf-8")).get("status")
            if status == "running":
                problems.append(f"locks: есть замок {lock}.lock и манифест running, но в state.active_runs его нет")
                continue
        problems.append(f"locks: замок {lock}.lock без записи в state.active_runs (мусор или потерянный прогон)")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="снимки против диска")
    ap.add_argument("--ci", action="store_true")
    ap.add_argument("--root", default=None, help="корень репозитория (по умолчанию — этот)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else ROOT
    problems = check_checkpoints(root) + check_state_locks(root)
    for msg in problems:
        print("  ВНИМАНИЕ:", msg)
    if problems:
        print(f"[snapshots] расхождений: {len(problems)}")
        return 1 if args.ci else 0
    print("[snapshots] снимки совпадают с диском")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
