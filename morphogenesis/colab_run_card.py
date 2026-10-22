"""Карточка прогона на чужом железе (Colab): маленький JSON для git.

Зачем: прогон в Colab не оставляет ни манифеста `lab/runs/`, ни замка — он идёт
на чужой машине. Чтобы след всё-таки был в репозитории, ноутбук пишет карточку:
окружение, коммит кода, дизайн, сводка, sha256 артефактов. Веса и census-JSON
(мегабайты) остаются на Drive, в git едет только карточка и сам ноутбук.

Использование в ноутбуке:

    from colab_run_card import build_card
    card = build_card(
        summary_path="/content/summary_colab_seed42.json",
        census_path="/content/census_colab_seed42.json",
        experiment="E02c_colab_repro_seed42",
        repo_url="https://github.com/mak777uh/-",
        design={"family": "E02c_R-9_s2000_seed42", "seeds": "0-63", "steps": 2000},
    )
    print(json.dumps(card, ensure_ascii=False, indent=1))
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import time
from typing import Any


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit(repo_dir: str | None) -> str | None:
    if not repo_dir:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def environment_card() -> dict[str, Any]:
    """Железо и стек: без этого «прогон на T4» — слова, а не данные."""
    card: dict[str, Any] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": None,
        "cuda": None,
        "gpu": None,
    }
    try:
        import torch

        card["torch"] = torch.__version__
        card["cuda"] = torch.version.cuda
        if torch.cuda.is_available():
            card["gpu"] = torch.cuda.get_device_name(0)
            card["gpu_memory_gb"] = round(
                torch.cuda.get_device_properties(0).total_memory / 1024 ** 3, 1
            )
    except Exception as exc:  # noqa: BLE001 - карточка важнее строгости
        card["torch_error"] = str(exc)
    return card


def build_card(
    summary_path: str,
    experiment: str,
    design: dict[str, Any],
    repo_dir: str | None = None,
    repo_url: str | None = None,
    census_path: str | None = None,
    out_path: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    with open(summary_path, encoding="utf-8") as fh:
        summary = json.load(fh)
    card: dict[str, Any] = {
        "schema_version": 1,
        "kind": "colab_run_card",
        "experiment": experiment,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo": {"url": repo_url, "commit": _git_commit(repo_dir)},
        "environment": environment_card(),
        "design": design,
        "result": {
            "stats": summary.get("stats"),
            "controls": summary.get("controls"),
            "verdict": summary.get("verdict"),
            "verdict_applicable": summary.get("verdict_applicable"),
            "families": summary.get("families"),
        },
        "artifacts": {
            "summary": os.path.basename(summary_path),
            "summary_sha256": sha256_file(summary_path),
        },
        "notes": notes,
    }
    if census_path and os.path.exists(census_path):
        card["artifacts"]["census"] = os.path.basename(census_path)
        card["artifacts"]["census_sha256"] = sha256_file(census_path)
        card["artifacts"]["census_bytes"] = os.path.getsize(census_path)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(card, fh, ensure_ascii=False, indent=1)
    return card
