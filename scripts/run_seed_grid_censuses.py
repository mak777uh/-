"""Запустить переписи второй волны H-E02C-6 и собрать сетку.

Один прогон = один вызов `scripts/lab.py run` вокруг `e02c_census.py`, чтобы у
каждой клетки был замок, манифест `lab/runs/<run_id>.json` и пара start/finish
в каноническом журнале (AGENTS §6). Порядок и имена зафиксированы заранее:

    E02c_seeddec_init<init>_data<data>  ->  census_e02c_seeddec_init<init>_data<data>.json
                                            summary_e02c_seeddec_init<init>_data<data>.json

`scripts/e02c_seed_grid.py` собирает по этим именам сетку и выносит вердикт,
поэтому имя — часть протокола, а не удобство.

Скрипт идемпотентен: клетка, у которой уже есть сводка, пропускается; клетка,
у которой нет `nca_final.pt`, попадает в `waiting` и не валит весь прогон.

Проверка плана без GPU и без запусков:

    python scripts/run_seed_grid_censuses.py --dry-run

Полный прогон (ждёт, что GPU-лейн свободен):

    python scripts/run_seed_grid_censuses.py --owner lead
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02c_replication"
CHECKPOINTS = REPO / "morphogenesis" / "checkpoints"
LAB = REPO / "scripts" / "lab.py"
CENSUS = REPO / "morphogenesis" / "e02c_census.py"

# Полный дизайн критерия H-E02C-6 (reports/2026-10-22-e02c-seed-grid-plan.md).
CELLS = [(42, 101), (42, 202), (42, 303), (101, 42), (101, 202), (101, 303)]


def family(init: int, data: int) -> str:
    return f"E02c_seeddec_init{init}_data{data}"


def summary_path(init: int, data: int) -> Path:
    return EXP / f"summary_e02c_seeddec_init{init}_data{data}.json"


def census_path(init: int, data: int) -> Path:
    return EXP / f"census_e02c_seeddec_init{init}_data{data}.json"


def existing_families(summaries: Path) -> set[str]:
    """Семейства, у которых уже есть перепись — по имени семейства внутри сводки.

    Имя файла не годится: первая волна писала `summary_e02c_seeddec_A.json` и
    `_B.json`, а это клетки (42,101) и (101,42). Опознание по `stats[*].family`
    не даёт переписать уже посчитанные клетки (это стоило бы ~15 мин GPU).
    """
    found = set()
    for path in sorted(Path(summaries).glob("summary_e02c_seeddec_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for stat in (data.get("stats") or {}).values():
            name = stat.get("family")
            if name:
                found.add(str(name))
    return found


def build_plan(cells=CELLS, checkpoints: Path = CHECKPOINTS, summaries: Path = EXP) -> dict:
    """Разложить клетки на ready / waiting / complete, не запуская ничего."""
    ready, waiting, complete = [], [], []
    done_families = existing_families(summaries)
    for init, data in cells:
        fam = family(init, data)
        final = Path(checkpoints) / fam / "nca_final.pt"
        item = {"init": init, "data": data, "family": fam}
        if fam in done_families:
            complete.append(item)
        elif final.is_file():
            ready.append(item)
        else:
            item["reason"] = (
                "чекпоинт не завершён: нет nca_final.pt" if (Path(checkpoints) / fam).is_dir()
                else "чекпоинта нет"
            )
            waiting.append(item)
    return {"ready": ready, "waiting": waiting, "complete": complete}


def census_command(item: dict) -> list[str]:
    """Команда переписи одной клетки (без обёртки)."""
    fam = item["family"]
    return [
        sys.executable,
        "e02c_census.py",
        "--families",
        fam,
        "--out",
        str(census_path(item["init"], item["data"])),
        "--summary-out",
        str(summary_path(item["init"], item["data"])),
    ]


def wrapped_command(item: dict, owner: str) -> list[str]:
    """Тот же вызов, но через `lab.py run`: замок + манифест + журнал."""
    return [
        sys.executable,
        str(LAB),
        "run",
        "--experiment",
        f"{item['family']}_census",
        "--experiment-id",
        "E02c",
        "--arm",
        "R-9",
        "--seed",
        str(item["init"]),
        "--steps",
        "2000",
        "--owner",
        owner,
        "--",
        *census_command(item),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--owner", default="lead", help="метка агента для lab.py run")
    ap.add_argument("--dry-run", action="store_true", help="только показать план")
    ap.add_argument(
        "--only",
        default="",
        help="ограничить клетки, например init42_data202,init101_data303",
    )
    args = ap.parse_args(argv)

    cells = CELLS
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        cells = [(i, d) for (i, d) in CELLS if f"init{i}_data{d}" in wanted]
        if not cells:
            raise SystemExit(f"--only не совпал ни с одной клеткой из {[f'init{i}_data{d}' for i, d in CELLS]}")

    plan = build_plan(cells)
    print(f"[grid-census] ready={len(plan['ready'])} complete={len(plan['complete'])} "
          f"waiting={len(plan['waiting'])}")
    for item in plan["complete"]:
        print(f"[grid-census] готово ранее: {item['family']}")
    for item in plan["waiting"]:
        print(f"[grid-census] ждёт: {item['family']} — {item['reason']}")

    for item in plan["ready"]:
        cmd = wrapped_command(item, args.owner)
        printable = " ".join(cmd[2:] if cmd[0] == sys.executable else cmd)
        if args.dry_run:
            print(f"[grid-census] DRY {item['family']}: {printable}")
            continue
        print(f"[grid-census] запуск {item['family']}", flush=True)
        proc = subprocess.run(cmd, cwd=REPO)
        if proc.returncode != 0:
            print(f"[grid-census] {item['family']}: код {proc.returncode} — останавливаюсь", flush=True)
            return proc.returncode

    if args.dry_run:
        return 0

    # Сетка и вердикт собираются только из готовых сводок; частичная сетка даст
    # n/a_design_incomplete, а не ложный вердикт.
    grid = subprocess.run([sys.executable, str(REPO / "scripts" / "e02c_seed_grid.py")], cwd=REPO)
    payload = json.loads((EXP / "seed_grid.json").read_text(encoding="utf-8"))
    verdict = payload.get("verdict") or {}
    print(f"[grid-census] вердикт: {verdict.get('verdict')} "
          f"missing={verdict.get('missing_cells')}")
    return grid.returncode


if __name__ == "__main__":
    raise SystemExit(main())
