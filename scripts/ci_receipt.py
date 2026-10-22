#!/usr/bin/env python
"""Квитанция воспроизведения: чем именно проверялся репозиторий.

Зачем: «у нас всё воспроизводится» — утверждение, которое проверяется машиной, а
не обещанием. Скрипт собирает маленький JSON: коммит, ОС, версии Python/torch,
результаты пересчёта чисел E02c и вердикт сетки. Этот файл CI кладёт артефактом,
и его можно приложить к статье или показать рецензенту.

Ничего не меняет в репозитории и не требует GPU. Если какая-то проверка не
проходит — квитанция всё равно пишется (с `ok: false`), чтобы падение было видно
не только в логе, а в артефакте.

Запуск (из корня репозитория):

    python scripts/ci_receipt.py            # пишет reproduction_receipt.json
    python scripts/ci_receipt.py --check    # ещё и падает, если проверки красные
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reproduction_receipt.json"


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # noqa: BLE001
        return 1, f"{type(exc).__name__}: {exc}"
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    return proc.returncode, tail[0][:400]


def _git(*args: str) -> str:
    code, out = _run(["git", *args])
    return out if code == 0 else ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="падать, если проверки красные")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)

    checks: dict[str, dict] = {}
    plan = {
        "lab_contract": [sys.executable, "scripts/lab.py", "validate", "--ci"],
        "e02c_numbers": [sys.executable, "scripts/verify_e02c_numbers.py"],
        "e02c_seed_grid": [sys.executable, "scripts/e02c_seed_grid.py"],
    }
    for name, cmd in plan.items():
        code, tail = _run(cmd)
        checks[name] = {"ok": code == 0, "exit_code": code, "tail": tail}

    try:
        import torch  # noqa: PLC0415 - нужен только здесь

        torch_version = str(torch.__version__)
    except Exception:  # noqa: BLE001
        torch_version = "not installed"

    payload = {
        "kind": "reproduction_receipt",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": os.environ.get("GITHUB_SHA") or _git("rev-parse", "HEAD"),
        "branch": os.environ.get("GITHUB_REF_NAME") or _git("rev-parse", "--abbrev-ref", "HEAD"),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "run_url": (
            f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
            f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
            if os.environ.get("GITHUB_RUN_ID")
            else ""
        ),
        "environment": {
            "os": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "torch": torch_version,
            "runner": "github-actions" if os.environ.get("GITHUB_ACTIONS") else "local",
        },
        "checks": checks,
        "ok": all(item["ok"] for item in checks.values()),
        "notes": (
            "GPU-опыты (TF32, обучения) сюда не входят: у бесплатных раннеров нет GPU. "
            "Квитанция подтверждает, что контракт лаборатории, арифметика отчётов E02c "
            "и вердикт замороженного критерия воспроизводятся из артефактов в git."
        ),
    }

    out = Path(args.out)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["ok"], "checks": {k: v["ok"] for k, v in checks.items()}},
                     ensure_ascii=False))
    print(f"[receipt] {out}")
    if args.check and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
