#!/usr/bin/env python3
"""lab.py — машинный control plane лаборатории Morphogenesis.

Запускать из корня репозитория:

    python scripts/lab.py status
    python scripts/lab.py validate
    python scripts/lab.py checkpoints
    python scripts/lab.py journal-import
    python scripts/lab.py state

Скрипт намеренно не импортирует torch и config: он должен работать быстро,
на свежем клоне и без GPU. Тяжёлые эксперименты запускаются через `run`,
который берёт замок и пишет манифест.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
MORPH = ROOT / "morphogenesis"
REGISTRY = LAB / "registry.json"
STATE = LAB / "state.json"
CHECKPOINTS = LAB / "checkpoints.json"
DESCRIPTOR = LAB / "experiments" / "E02b_morphospace.json"
RUNS = LAB / "runs"
LOCKS = LAB / "locks"
LOGS_ARCHIVE = LAB / "logs"
JOURNAL = MORPH / "logs" / "journal.jsonl"
CHECKPOINT_DIR = MORPH / "checkpoints"

STATUSES = {"planned", "running", "closed", "blocked", "not_run"}
KINDS = {"experiment", "diagnostic", "gate", "series"}
HYPOTHESIS_STATUSES = {"planned", "running", "confirmed", "rejected", "blocked"}
LOOP_STAGES = ("sources", "review", "hypothesis", "test", "writeup", "sources_next")
RUN_STATUSES = {"claimed", "running", "finished", "failed", "aborted", "superseded"}
EVENTS = {"start", "finish", "error", "checkpoint", "run_start", "run_finish"}
LEVELS = {"debug", "info", "warn", "warning", "error"}
REQUIRED_LAB_FILES = [
    ROOT / "AGENTS.md",
    LAB / "README.md",
    REGISTRY,
    STATE,
    CHECKPOINTS,
    DESCRIPTOR,
]

WP4_RE = re.compile(r"^WP4_(?P<arm>.+?)_s(?P<steps>\d+)_seed(?P<seed>\d+)$")
GATE_RE = re.compile(r"^gate_layer1_s(?P<steps>\d+)_seed(?P<seed>\d+)$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return cleaned or "run"


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return path.as_posix()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return rows, [f"нет файла {rel(path)}"]
    with path.open("r", encoding="utf-8") as fh:
        for number, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel(path)}:{number}: {exc}")
                continue
            if not isinstance(row, dict):
                errors.append(f"{rel(path)}:{number}: строка не объект")
                continue
            rows.append(row)
    return rows, errors


def git_tracked() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            stderr=subprocess.DEVNULL,
        )
        return [part for part in out.decode("utf-8", "replace").split("\0") if part]
    except (OSError, subprocess.CalledProcessError):
        return []


def git_info() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        status = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return {"commit": commit or None, "dirty": bool(status.strip())}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def disk_info() -> dict[str, Any]:
    usage = shutil.disk_usage(ROOT)
    gb = 1024 ** 3
    return {
        "total_gb": round(usage.total / gb, 2),
        "free_gb": round(usage.free / gb, 2),
        "used_gb": round(usage.used / gb, 2),
    }


def checkpoint_bytes() -> int:
    total = 0
    if not CHECKPOINT_DIR.exists():
        return 0
    for path in CHECKPOINT_DIR.rglob("*.pt"):
        try:
            total += path.stat().st_size
        except OSError:
            pass
    return total


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_fields(experiment: str) -> dict[str, Any]:
    match = WP4_RE.match(experiment)
    if match:
        return {
            "experiment_id": "WP4",
            "arm": match.group("arm"),
            "seed": int(match.group("seed")),
            "steps": int(match.group("steps")),
        }
    match = GATE_RE.match(experiment)
    if match:
        return {
            "experiment_id": "GATE_L1",
            "arm": "gate_layer1",
            "seed": int(match.group("seed")),
            "steps": int(match.group("steps")),
        }
    return {"experiment_id": None, "arm": None, "seed": None, "steps": None}


def make_run_id(start_ts: str | None, experiment: str, used: set[str]) -> str:
    parsed = parse_ts(start_ts)
    stamp = parsed.strftime("%Y%m%dT%H%M%SZ") if parsed else re.sub(r"[^0-9A-Za-z]+", "", start_ts or "")[:16]
    base = f"{stamp or 'unknown'}-{slug(experiment)}"
    candidate = base
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    used.add(candidate)
    return candidate


def load_registry() -> dict[str, Any]:
    return read_json(REGISTRY)


def load_descriptor() -> dict[str, Any] | None:
    if not DESCRIPTOR.exists():
        return None
    return read_json(DESCRIPTOR)


def load_state() -> dict[str, Any] | None:
    if not STATE.exists():
        return None
    return read_json(STATE)


# ---------------------------------------------------------------------------
# Checkpoints
# ---------------------------------------------------------------------------


def _parse_checkpoint_dir(name: str) -> dict[str, Any] | None:
    match = WP4_RE.match(name)
    if match:
        return {
            "experiment_id": "WP4",
            "arm": match.group("arm"),
            "seed": int(match.group("seed")),
            "steps": int(match.group("steps")),
        }
    match = GATE_RE.match(name)
    if match:
        return {
            "experiment_id": "GATE_L1",
            "arm": "gate_layer1",
            "seed": int(match.group("seed")),
            "steps": int(match.group("steps")),
        }
    return None


def _parse_kind(filename: str) -> tuple[str, int | None]:
    if filename == "nca_best.pt":
        return "best", None
    if filename == "nca_final.pt":
        return "final", None
    match = re.match(r"^nca_iter_(\d+)\.pt$", filename)
    if match:
        return "iter", int(match.group(1))
    return "other", None


def scan_checkpoints(hash_canonical: bool = False) -> dict[str, Any]:
    descriptor = load_descriptor() or {}
    requirements_by_family: dict[str, str] = {}
    for item in descriptor.get("checkpoint_requirements", []):
        requirements_by_family[item["family"]] = item["file"]

    entries: list[dict[str, Any]] = []
    if CHECKPOINT_DIR.exists():
        for directory in sorted(CHECKPOINT_DIR.iterdir(), key=lambda p: p.name):
            if not directory.is_dir() or directory.name == "E02_seed0_stress1":
                continue
            fields = _parse_checkpoint_dir(directory.name)
            if fields is None:
                continue
            for path in sorted(directory.glob("*.pt"), key=lambda p: p.name):
                kind, iteration = _parse_kind(path.name)
                required_file = requirements_by_family.get(directory.name)
                canonical = bool(required_file and required_file == path.name)
                sha = None
                hash_status = "pending" if canonical else "not_required"
                if hash_canonical and canonical:
                    sha = sha256_file(path)
                    hash_status = "complete"
                try:
                    size_bytes = path.stat().st_size
                    mtime = dt.datetime.fromtimestamp(
                        path.stat().st_mtime, tz=dt.timezone.utc
                    ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                except OSError:
                    size_bytes = 0
                    mtime = None
                entries.append(
                    {
                        "family": directory.name,
                        "experiment_id": fields["experiment_id"],
                        "arm": fields["arm"],
                        "seed": fields["seed"],
                        "steps": fields["steps"],
                        "kind": kind,
                        "iteration": iteration,
                        "path": rel(path),
                        "size_bytes": size_bytes,
                        "mtime": mtime,
                        "sha256": sha,
                        "hash_status": hash_status,
                        "canonical_for": ["E02b_morphospace"] if canonical else [],
                        "notes": (
                            "hash не посчитан"
                            if hash_status == "pending"
                            else ("канонический файл не требуется для E02b" if not canonical else "")
                        ),
                    }
                )

    required_items: list[dict[str, Any]] = []
    missing: list[str] = []
    for family, filename in requirements_by_family.items():
        match = next(
            (
                entry
                for entry in entries
                if entry["family"] == family and Path(entry["path"]).name == filename
            ),
            None,
        )
        item = {
            "family": family,
            "file": filename,
            "ready": match is not None,
            "path": match["path"] if match else None,
        }
        required_items.append(item)
        if match is None:
            missing.append(f"{family}/{filename}")

    virtual = []
    untrained = descriptor.get("checkpoint_policy", {}).get("untrained_control")
    if untrained:
        virtual.append(
            {
                "id": untrained.get("id", "untrained"),
                "kind": untrained.get("kind", "runtime"),
                "note": untrained.get("note", ""),
                "canonical_for": ["E02b_morphospace"],
            }
        )

    payload = {
        "schema_version": 1,
        "generated_at": now_utc(),
        "root": rel(CHECKPOINT_DIR),
        "entries": entries,
        "requirements": {
            "E02b_morphospace": {
                "required": len(required_items),
                "ready": sum(1 for item in required_items if item["ready"]),
                "missing": missing,
                "items": required_items,
            }
        },
        "virtual": virtual,
    }
    write_json_atomic(CHECKPOINTS, payload)
    return payload


# ---------------------------------------------------------------------------
# Runs from journal
# ---------------------------------------------------------------------------


def _finish_metrics(row: dict[str, Any]) -> dict[str, Any]:
    metrics = {}
    for key in (
        "best_loss",
        "alive_fraction_final",
        "iterations_done",
        "wall_time_sec",
        "sim_steps_accumulated",
        "nan_count",
    ):
        if key in row:
            metrics[key] = row[key]
    return metrics


def _manifest_from_pair(
    start: dict[str, Any],
    finish: dict[str, Any] | None,
    status: str,
    used: set[str],
) -> dict[str, Any]:
    experiment = start.get("experiment") or "unknown"
    fields = run_fields(experiment)
    run_id = make_run_id(start.get("ts"), experiment, used)
    log_candidate = MORPH / "logs" / f"{experiment}_log.jsonl"
    return {
        "schema_version": 1,
        "run_id": run_id,
        "experiment": experiment,
        "experiment_id": fields["experiment_id"],
        "arm": fields["arm"],
        "seed": start.get("seed", fields["seed"]),
        "steps": start.get("total_steps", fields["steps"]),
        "status": status,
        "provenance": "journal-reconstructed",
        "source": rel(JOURNAL),
        "started_at": start.get("ts"),
        "finished_at": finish.get("ts") if finish else None,
        "git_commit": None,
        "git_dirty": None,
        "command": None,
        "cwd": "morphogenesis",
        "owner": None,
        "environment": {
            "device": start.get("device"),
            "spec_version": start.get("spec_version"),
            "revision": start.get("revision"),
            "batch_size": start.get("batch_size"),
            "pool_init_mode": start.get("pool_init_mode"),
        },
        "checkpoint_in": None,
        "outputs": {},
        "metrics": _finish_metrics(finish or {}),
        "stop_reason": (finish or {}).get("stop_reason"),
        "exit_code": None,
        "log_path": rel(log_candidate) if log_candidate.exists() else None,
        "notes": "Восстановлено из журнала: git-коммит, команда, входной чекпоинт и хеши не сохранялись.",
    }


def _status_from_finish(row: dict[str, Any]) -> str:
    if row.get("event") == "error":
        return "failed"
    stop_reason = str(row.get("stop_reason") or "").lower()
    if stop_reason in {"aborted", "cancelled", "interrupted", "keyboard_interrupt"}:
        return "aborted"
    if stop_reason in {"nan", "oom", "out_of_memory", "error", "exception"}:
        return "failed"
    return "finished"


def import_journal() -> dict[str, int]:
    rows, errors = read_jsonl(JOURNAL)
    if errors:
        raise SystemExit("Журнал не читается:\n  " + "\n  ".join(errors))

    open_by_experiment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pairs: list[tuple[dict[str, Any], dict[str, Any] | None, str]] = []
    for row in rows:
        event = row.get("event")
        experiment = row.get("experiment")
        if event in ("start", "run_start") and experiment:
            open_by_experiment[experiment].append(row)
        elif event in ("finish", "run_finish", "error") and experiment:
            if open_by_experiment[experiment]:
                start = open_by_experiment[experiment].pop(0)
                pairs.append((start, row, _status_from_finish(row)))
            else:
                pairs.append((row, None, "failed"))

    for _experiment, starts in open_by_experiment.items():
        for index, start in enumerate(starts):
            age_hours = 10 ** 6
            parsed = parse_ts(start.get("ts"))
            if parsed is not None:
                age_hours = (dt.datetime.now(dt.timezone.utc) - parsed).total_seconds() / 3600
            is_last = index == len(starts) - 1
            status = "running" if is_last and age_hours < 6 else "aborted"
            pairs.append((start, None, status))

    used: set[str] = set()
    written = 0
    skipped = 0
    RUNS.mkdir(parents=True, exist_ok=True)
    for start, finish, status in pairs:
        manifest = _manifest_from_pair(start, finish, status, used)
        target = RUNS / f"{manifest['run_id']}.json"
        if target.exists():
            existing = read_json(target)
            if existing.get("provenance") != "journal-reconstructed":
                skipped += 1
                continue
        write_json_atomic(target, manifest)
        written += 1
    return {"rows": len(rows), "written": written, "skipped": skipped}


# ---------------------------------------------------------------------------
# Logs archive (GitHub-friendly)
# ---------------------------------------------------------------------------


def archive_logs(dry_run: bool = False) -> dict[str, Any]:
    """Копирует завершённые per-run JSONL в lab/logs/ и пишет index.json.

    TensorBoard, stdout-логи обёртки и per-run JSONL активных прогонов не
    архивируются: первые два нечитаемы в git, последние ещё дописываются.
    """
    runs_by_experiment: dict[str, dict[str, Any]] = {}
    for path in sorted(RUNS.glob("*.json")):
        try:
            manifest = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        experiment = manifest.get("experiment")
        if not experiment:
            continue
        previous = runs_by_experiment.get(experiment)
        if previous is None or (manifest.get("started_at") or "") >= (
            previous.get("started_at") or ""
        ):
            runs_by_experiment[experiment] = manifest

    files = []
    copied = 0
    skipped = 0
    for source in sorted((MORPH / "logs").glob("*_log.jsonl")):
        experiment = source.name[: -len("_log.jsonl")]
        manifest = runs_by_experiment.get(experiment) or {}
        status = manifest.get("status") or "legacy"
        if status in {"claimed", "running"}:
            skipped += 1
            continue
        target = LOGS_ARCHIVE / source.name
        if not dry_run:
            LOGS_ARCHIVE.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied += 1
        files.append(
            {
                "path": rel(target),
                "source": rel(source),
                "experiment": experiment,
                "run_id": manifest.get("run_id"),
                "run_status": status,
                "size_bytes": source.stat().st_size,
                "mtime": dt.datetime.fromtimestamp(
                    source.stat().st_mtime, tz=dt.timezone.utc
                )
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "sha256": sha256_file(source),
            }
        )

    payload = {
        "schema_version": 1,
        "generated_at": now_utc(),
        "policy": "Только завершённые per-run JSONL; TensorBoard, stdout обёртки и активные прогоны не архивируются.",
        "files": files,
        "total_bytes": sum(item["size_bytes"] for item in files),
        "copied": copied,
        "skipped_active": skipped,
        "dry_run": dry_run,
    }
    if not dry_run:
        write_json_atomic(LOGS_ARCHIVE / "index.json", payload)
    return payload


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


def build_state() -> dict[str, Any]:
    registry = load_registry()
    checkpoints = read_json(CHECKPOINTS)
    runs = []
    for path in sorted(RUNS.glob("*.json")):
        try:
            runs.append(read_json(path))
        except (OSError, json.JSONDecodeError):
            continue

    active = sorted(
        [run for run in runs if run.get("status") in {"claimed", "running"}],
        key=lambda run: run.get("started_at") or "",
    )
    experiment_counts = Counter(item.get("status") for item in registry.get("experiments", []))
    run_counts = Counter(run.get("status") for run in runs)
    requirement = checkpoints.get("requirements", {}).get(
        "E02b_morphospace", {"required": 0, "ready": 0, "missing": []}
    )
    hashes_pending = sum(
        1
        for entry in checkpoints.get("entries", [])
        if entry.get("canonical_for") and entry.get("hash_status") == "pending"
    )
    disk = disk_info()
    disk["checkpoints_gb"] = round(checkpoint_bytes() / (1024 ** 3), 2)

    blockers = list(registry.get("program", {}).get("blockers", []))
    if requirement.get("missing"):
        blockers.append(
            "E02b checkpoint preflight: не хватает " + ", ".join(requirement["missing"])
        )
    if disk["free_gb"] < 2.0:
        blockers.append(f"Мало места на диске: свободно {disk['free_gb']} ГБ.")

    next_steps = list(registry.get("program", {}).get("next", []))
    if hashes_pending:
        next_steps.append(
            "После закрытия активных прогонов заполнить sha256 канонических чекпоинтов: "
            "python scripts/lab.py checkpoints --hash-canonical"
        )

    locks = []
    if LOCKS.exists():
        for path in sorted(LOCKS.glob("*.lock")):
            try:
                locks.append(read_json(path))
            except (OSError, json.JSONDecodeError):
                continue

    state = {
        "schema_version": 1,
        "generated_at": now_utc(),
        "phase": registry.get("program", {}).get("phase", "UNKNOWN"),
        "status_note": registry.get("program", {}).get("status_note", ""),
        "active_runs": [
            {
                "run_id": run.get("run_id"),
                "experiment": run.get("experiment"),
                "arm": run.get("arm"),
                "seed": run.get("seed"),
                "status": run.get("status"),
                "started_at": run.get("started_at"),
                "owner": run.get("owner"),
            }
            for run in active
        ],
        "locks": locks,
        "counts": {
            "experiments": dict(experiment_counts),
            "runs": dict(run_counts),
            "run_manifests": len(runs),
        },
        "checkpoints": {
            "e02b": {
                "required": requirement.get("required", 0),
                "ready": requirement.get("ready", 0),
                "missing": requirement.get("missing", []),
            },
            "hashes_pending": hashes_pending,
            "files_indexed": len(checkpoints.get("entries", [])),
        },
        "disk": disk,
        "blockers": blockers,
        "next": next_steps,
        "decisions_needed": list(registry.get("program", {}).get("decisions_needed", [])),
        "sources": [rel(REGISTRY), rel(CHECKPOINTS), rel(RUNS), rel(JOURNAL)],
    }
    write_json_atomic(STATE, state)
    return state


# ---------------------------------------------------------------------------
# Claim / run
# ---------------------------------------------------------------------------


def _lock_path(experiment: str) -> Path:
    return LOCKS / f"{slug(experiment)}.lock"


def _read_lock(path: Path) -> dict[str, Any] | None:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def claim(experiment: str, owner: str, run_id: str | None, ttl_minutes: int, steal_stale: bool) -> dict[str, Any]:
    LOCKS.mkdir(parents=True, exist_ok=True)
    path = _lock_path(experiment)
    if path.exists():
        existing = _read_lock(path) or {}
        heartbeat = parse_ts(existing.get("heartbeat_at") or existing.get("started_at"))
        age_minutes = 10 ** 9
        if heartbeat is not None:
            age_minutes = (dt.datetime.now(dt.timezone.utc) - heartbeat).total_seconds() / 60
        if steal_stale and age_minutes > ttl_minutes:
            path.unlink(missing_ok=True)
        else:
            raise SystemExit(
                "Эксперимент уже занят:\n"
                + json.dumps(existing, ensure_ascii=False, indent=2)
                + f"\nЗамок: {rel(path)} (возраст {age_minutes:.1f} мин, ttl {ttl_minutes} мин)"
            )

    if run_id is None:
        run_id = make_run_id(now_utc(), experiment, set())
    if not RUN_ID_RE.match(run_id):
        raise SystemExit("run_id содержит недопустимые символы: " + run_id)

    payload = {
        "run_id": run_id,
        "experiment": experiment,
        "owner": owner,
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "started_at": now_utc(),
        "heartbeat_at": now_utc(),
        "ttl_minutes": ttl_minutes,
    }
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError as exc:
        raise SystemExit(f"Гонка за замок: {rel(path)}") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return payload


def release(experiment: str, run_id: str | None) -> None:
    path = _lock_path(experiment)
    if not path.exists():
        print(f"Замка нет: {rel(path)}")
        return
    existing = _read_lock(path) or {}
    if run_id and existing.get("run_id") != run_id:
        raise SystemExit(
            f"Замок принадлежит run_id={existing.get('run_id')!r}, а не {run_id!r}; "
            "не удаляю чужой замок."
        )
    path.unlink(missing_ok=True)
    print(f"Замок снят: {rel(path)}")


def heartbeat(experiment: str, run_id: str | None) -> None:
    path = _lock_path(experiment)
    existing = _read_lock(path)
    if existing is None:
        raise SystemExit(f"Замка нет: {rel(path)}")
    if run_id and existing.get("run_id") != run_id:
        raise SystemExit("run_id не совпадает с замком; heartbeat отклонён.")
    existing["heartbeat_at"] = now_utc()
    write_json_atomic(path, existing)
    print(json.dumps(existing, ensure_ascii=False, indent=2))


def _environment() -> dict[str, Any]:
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": package_version("torch"),
        "numpy": package_version("numpy"),
        "device": None,
    }
    for key in ("CUBLAS_WORKSPACE_CONFIG", "PYTHONHASHSEED"):
        if key in os.environ:
            env[key] = os.environ[key]
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        ).strip()
        if out:
            env["device"] = out.splitlines()[0]
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return env


def run_command(args: argparse.Namespace) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("Нужна команда после `--`, например: ... run ... -- python train.py ...")
    if command[0] in {"python", "python3"}:
        command[0] = sys.executable

    lock = claim(args.experiment, args.owner, args.run_id, args.ttl_minutes, False)
    run_id = lock["run_id"]
    manifest_path = RUNS / f"{run_id}.json"
    log_path = MORPH / "logs" / f"{run_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    git = git_info()
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "experiment": args.experiment,
        "experiment_id": args.experiment_id,
        "arm": args.arm,
        "seed": args.seed,
        "steps": args.steps,
        "status": "running",
        "provenance": "runner",
        "source": rel(JOURNAL),
        "started_at": now_utc(),
        "finished_at": None,
        "git_commit": git["commit"],
        "git_dirty": git["dirty"],
        "command": command,
        "cwd": "morphogenesis",
        "owner": args.owner,
        "environment": _environment(),
        "checkpoint_in": (
            {"path": rel(Path(args.checkpoint_in)), "sha256": None}
            if args.checkpoint_in
            else None
        ),
        "outputs": {"declared": args.output or [], "log": rel(log_path)},
        "metrics": {},
        "stop_reason": None,
        "exit_code": None,
        "log_path": rel(log_path),
        "notes": args.note or "",
    }
    write_json_atomic(manifest_path, manifest)
    print(f"[lab] run_id={run_id}")
    print(f"[lab] manifest={rel(manifest_path)}")
    print(f"[lab] log={rel(log_path)}")
    print(f"[lab] cwd={MORPH}")
    print("[lab] " + " ".join(command), flush=True)

    return_code = 1
    try:
        with log_path.open("w", encoding="utf-8", newline="\n") as log_fh:
            process = subprocess.Popen(
                command,
                cwd=MORPH,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="")
                log_fh.write(line)
                log_fh.flush()
            return_code = process.wait()
        manifest["finished_at"] = now_utc()
        manifest["exit_code"] = return_code
        manifest["status"] = "finished" if return_code == 0 else "failed"
        manifest["stop_reason"] = f"exit_{return_code}"
        write_json_atomic(manifest_path, manifest)
        return return_code
    except KeyboardInterrupt:
        try:
            process.terminate()
            process.wait(timeout=10)
        except Exception:
            pass
        manifest["finished_at"] = now_utc()
        manifest["exit_code"] = 130
        manifest["status"] = "aborted"
        manifest["stop_reason"] = "keyboard_interrupt"
        write_json_atomic(manifest_path, manifest)
        return 130
    except Exception as exc:
        manifest["finished_at"] = now_utc()
        manifest["exit_code"] = return_code
        manifest["status"] = "failed"
        manifest["stop_reason"] = "exception"
        manifest["notes"] = (manifest.get("notes") or "") + f"\n{type(exc).__name__}: {exc}"
        write_json_atomic(manifest_path, manifest)
        raise
    finally:
        release(args.experiment, run_id)
        build_state()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _check_hypotheses(items: Any, where: str) -> list[str]:
    """Проверить список гипотез: у каждой есть id, утверждение, критерий и статус."""
    errors: list[str] = []
    if not isinstance(items, list) or not items:
        return [f"{where}: пусто — нужна хотя бы одна гипотеза со способом проверки"]
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            errors.append(f"{where}: элемент не объект")
            continue
        hid = str(item.get("id") or "")
        if not hid:
            errors.append(f"{where}: гипотеза без id")
        elif hid in seen:
            errors.append(f"{where}: повтор id={hid}")
        else:
            seen.add(hid)
        for key in ("statement", "test"):
            if not str(item.get(key) or "").strip():
                errors.append(f"{where}[{hid or '?'}]: пустое поле {key}")
        if item.get("status") not in HYPOTHESIS_STATUSES:
            errors.append(
                f"{where}[{hid or '?'}]: недопустимый status={item.get('status')!r}; "
                f"допустимо {sorted(HYPOTHESIS_STATUSES)}"
            )
    return errors


def _check_loop(program: dict[str, Any]) -> list[str]:
    """Проверить, что научный цикл описан: шесть стадий и очередь гипотез."""
    errors: list[str] = []
    loop = program.get("loop")
    if not isinstance(loop, list) or not loop:
        return ["registry.program.loop отсутствует или пуст: описан цикл научной работы"]
    stages: list[str] = []
    for item in loop:
        if not isinstance(item, dict):
            errors.append("registry.program.loop: элемент не объект")
            continue
        stage = str(item.get("stage") or "")
        if not stage:
            errors.append("registry.program.loop: стадия без stage")
        stages.append(stage)
        for key in ("title", "where", "output"):
            if not str(item.get(key) or "").strip():
                errors.append(f"registry.program.loop[{stage or '?'}]: пустое поле {key}")
    if len(stages) != len(set(stages)):
        errors.append("registry.program.loop: стадии повторяются")
    missing = [stage for stage in LOOP_STAGES if stage not in stages]
    if missing:
        errors.append(
            "registry.program.loop: нет обязательных стадий цикла: " + ", ".join(missing)
        )
    errors.extend(_check_hypotheses(program.get("next_hypotheses"), "registry.program.next_hypotheses"))
    return errors


def validate(ci: bool, strict: bool) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, Any] = {}

    for path in REQUIRED_LAB_FILES:
        if not path.exists():
            errors.append(f"нет обязательного файла: {rel(path)}")

    registry: dict[str, Any] = {}
    state: dict[str, Any] = {}
    checkpoints: dict[str, Any] = {}
    descriptor: dict[str, Any] | None = None

    try:
        registry = load_registry()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"registry.json: {exc}")
    try:
        state = load_state() or {}
        if not state:
            errors.append("state.json отсутствует или пуст")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"state.json: {exc}")
    try:
        checkpoints = read_json(CHECKPOINTS)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"checkpoints.json: {exc}")
    try:
        descriptor = load_descriptor()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"descriptor: {exc}")

    if registry:
        if registry.get("schema_version") != 1:
            errors.append("registry.schema_version должен быть 1")
        program = registry.get("program", {})
        for key in ("name", "phase", "status_note", "blockers", "next", "decisions_needed"):
            if key not in program:
                errors.append(f"registry.program.{key} отсутствует")
        errors.extend(_check_loop(program))
        experiments = registry.get("experiments", [])
        if not isinstance(experiments, list) or not experiments:
            errors.append("registry.experiments пуст или не список")
        seen: set[str] = set()
        for item in experiments if isinstance(experiments, list) else []:
            exp_id = item.get("id")
            if not exp_id:
                errors.append("experiment без id")
                continue
            if exp_id in seen:
                errors.append(f"duplicate experiment id: {exp_id}")
            seen.add(exp_id)
            if item.get("status") not in STATUSES:
                errors.append(f"{exp_id}: недопустимый status={item.get('status')!r}")
            if item.get("kind") not in KINDS:
                errors.append(f"{exp_id}: недопустимый kind={item.get('kind')!r}")
            for key in ("plan", "report", "article", "descriptor"):
                value = item.get(key)
                if value and not (ROOT / value).exists():
                    errors.append(f"{exp_id}.{key} не существует: {value}")
            root = item.get("artifact_root")
            if root and not (ROOT / root).exists() and item.get("status") not in {"planned", "not_run"}:
                warnings.append(f"{exp_id}.artifact_root пока нет: {root}")
            # Научный цикл (AGENTS.md §3a): написанная статья обязана заканчиваться
            # следующими гипотезами — иначе результат не закрыт.
            if item.get("article"):
                errors.extend(
                    _check_hypotheses(
                        item.get("next_hypotheses"), f"{exp_id}.next_hypotheses"
                    )
                )
        counts["experiments"] = len(experiments if isinstance(experiments, list) else [])

    if state:
        for key in (
            "schema_version",
            "generated_at",
            "phase",
            "active_runs",
            "counts",
            "checkpoints",
            "disk",
            "blockers",
            "next",
            "decisions_needed",
        ):
            if key not in state:
                errors.append(f"state.{key} отсутствует")
        if registry and state.get("phase") != registry.get("program", {}).get("phase"):
            errors.append("state.json устарел: phase не совпадает с registry.program.phase; запусти `lab.py state`")
        counts["active_runs"] = len(state.get("active_runs", []))

    if checkpoints:
        for entry in checkpoints.get("entries", []):
            path_value = entry.get("path")
            if path_value and not ci and not (ROOT / path_value).exists():
                warnings.append(f"checkpoint отсутствует: {path_value}")
        requirement = checkpoints.get("requirements", {}).get("E02b_morphospace", {})
        missing = requirement.get("missing", [])
        if missing:
            message = "E02b checkpoint preflight: не хватает " + ", ".join(missing)
            (errors if strict else warnings).append(message)
        if state and requirement:
            state_missing = state.get("checkpoints", {}).get("e02b", {}).get("missing", [])
            if set(state_missing) != set(missing):
                errors.append("state.checkpoints.e02b.missing не совпадает с checkpoints.json; запусти `lab.py state`")
        counts["checkpoint_files"] = len(checkpoints.get("entries", []))

    if descriptor:
        if descriptor.get("id") != "E02b_morphospace":
            errors.append("descriptor.id должен быть E02b_morphospace")
        protocol = descriptor.get("protocol")
        if protocol and not (ROOT / protocol).exists():
            errors.append(f"descriptor.protocol не существует: {protocol}")
        required = descriptor.get("checkpoint_requirements", [])
        counts["e02b_checkpoint_requirements"] = len(required)

    run_files = sorted(RUNS.glob("*.json"))
    run_ids: set[str] = set()
    for path in run_files:
        try:
            manifest = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel(path)}: {exc}")
            continue
        run_id = manifest.get("run_id")
        if not run_id:
            errors.append(f"{rel(path)}: нет run_id")
            continue
        if run_id in run_ids:
            errors.append(f"duplicate run_id: {run_id}")
        run_ids.add(run_id)
        if path.stem != run_id:
            errors.append(f"{rel(path)}: имя файла не совпадает с run_id={run_id}")
        if manifest.get("status") not in RUN_STATUSES:
            errors.append(f"{rel(path)}: недопустимый status={manifest.get('status')!r}")
        for key in ("experiment", "started_at", "provenance"):
            if not manifest.get(key):
                errors.append(f"{rel(path)}: нет {key}")
    counts["runs"] = len(run_files)

    journal_rows, journal_errors = read_jsonl(JOURNAL)
    errors.extend(journal_errors)
    for index, row in enumerate(journal_rows, start=1):
        if row.get("event") not in EVENTS:
            errors.append(f"journal строка {index}: недопустимый event={row.get('event')!r}")
        for key in ("ts", "experiment", "level"):
            if not row.get(key):
                errors.append(f"journal строка {index}: нет {key}")
        if row.get("level") not in LEVELS:
            errors.append(f"journal строка {index}: недопустимый level={row.get('level')!r}")
    counts["journal_rows"] = len(journal_rows)

    tracked = git_tracked()
    if tracked:
        bad_pyc = [path for path in tracked if path.endswith((".pyc", ".pyo"))]
        bad_weights = [path for path in tracked if path.endswith((".pt", ".pth", ".ckpt"))]
        bad_logs = [
            path
            for path in tracked
            if path.startswith("morphogenesis/logs/") and path != rel(JOURNAL)
        ]
        if bad_pyc:
            errors.append(f"в git отслеживаются .pyc: {len(bad_pyc)} файлов")
        if bad_weights:
            errors.append(f"в git отслеживаются веса: {len(bad_weights)} файлов")
        if bad_logs:
            errors.append(f"в git отслеживаются runtime-логи: {len(bad_logs)} файлов")
        counts["tracked_files"] = len(tracked)

    return errors, warnings, counts


def print_validation(errors: list[str], warnings: list[str], counts: dict[str, Any], as_json: bool) -> int:
    ok = not errors
    if as_json:
        print(
            json.dumps(
                {"ok": ok, "errors": errors, "warnings": warnings, "counts": counts},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if errors:
            print("ОШИБКИ:")
            for error in errors:
                print("  - " + error)
        if warnings:
            print("ПРЕДУПРЕЖДЕНИЯ:")
            for warning in warnings:
                print("  - " + warning)
        if not errors and not warnings:
            print("lab: контракт в порядке.")
        else:
            print("lab: " + ("провал" if errors else "есть предупреждения") + ".")
        if counts:
            print("counts: " + json.dumps(counts, ensure_ascii=False))
    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Status / CLI
# ---------------------------------------------------------------------------


def status(as_json: bool, refresh: bool) -> int:
    state = build_state() if refresh or not STATE.exists() else load_state()
    if state is None:
        raise SystemExit("state.json отсутствует; запусти `python scripts/lab.py state`")
    if as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    print(f"phase: {state.get('phase')}")
    print(f"status: {state.get('status_note')}")
    active = state.get("active_runs", [])
    print(f"active runs: {len(active)}")
    for run in active:
        print(
            "  - {run_id} | {experiment} | arm={arm} seed={seed} | {status} | {started_at}".format(
                **{key: run.get(key) for key in ("run_id", "experiment", "arm", "seed", "status", "started_at")}
            )
        )
    cp = state.get("checkpoints", {}).get("e02b", {})
    print(f"E02b checkpoints: {cp.get('ready', 0)}/{cp.get('required', 0)} ready")
    for missing in cp.get("missing", []):
        print("  missing: " + missing)
    disk = state.get("disk", {})
    print(
        f"disk: free {disk.get('free_gb')} GB; checkpoints {disk.get('checkpoints_gb')} GB; "
        f"canonical hashes pending {state.get('checkpoints', {}).get('hashes_pending', 0)}"
    )
    if state.get("blockers"):
        print("blockers:")
        for blocker in state["blockers"]:
            print("  - " + blocker)
    if state.get("next"):
        print("next:")
        for item in state["next"]:
            print("  - " + item)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Машинный control plane Morphogenesis")
    sub = parser.add_subparsers(dest="action", required=True)

    p_status = sub.add_parser("status", help="показать state.json")
    p_status.add_argument("--json", action="store_true")
    p_status.add_argument("--refresh", action="store_true")

    p_validate = sub.add_parser("validate", help="проверить контракт")
    p_validate.add_argument("--ci", action="store_true", help="не требовать локальные веса")
    p_validate.add_argument("--strict", action="store_true", help="считать предупреждения ошибками")
    p_validate.add_argument("--json", action="store_true")

    p_checkpoints = sub.add_parser("checkpoints", help="пересканировать веса")
    p_checkpoints.add_argument("--hash-canonical", action="store_true", help="посчитать sha256 канонических файлов")
    p_checkpoints.add_argument("--json", action="store_true")

    p_journal = sub.add_parser("journal-import", help="пересобрать lab/runs из журнала")
    p_journal.add_argument("--json", action="store_true")

    p_logs = sub.add_parser("logs-archive", help="архивировать per-run JSONL в lab/logs")
    p_logs.add_argument("--dry-run", action="store_true")
    p_logs.add_argument("--json", action="store_true")

    sub.add_parser("state", help="пересобрать state.json")

    p_claim = sub.add_parser("claim", help="занять эксперимент")
    p_claim.add_argument("--experiment", required=True)
    p_claim.add_argument("--owner", default=os.environ.get("USERNAME") or os.environ.get("USER") or "unknown")
    p_claim.add_argument("--run-id")
    p_claim.add_argument("--ttl-minutes", type=int, default=480)
    p_claim.add_argument("--steal-stale", action="store_true")

    p_release = sub.add_parser("release", help="снять замок")
    p_release.add_argument("--experiment", required=True)
    p_release.add_argument("--run-id")

    p_heartbeat = sub.add_parser("heartbeat", help="обновить heartbeat замка")
    p_heartbeat.add_argument("--experiment", required=True)
    p_heartbeat.add_argument("--run-id")

    p_run = sub.add_parser("run", help="запустить команду под замком и манифестом")
    p_run.add_argument("--experiment", required=True)
    p_run.add_argument("--experiment-id")
    p_run.add_argument("--arm")
    p_run.add_argument("--seed", type=int)
    p_run.add_argument("--steps", type=int)
    p_run.add_argument("--owner", default=os.environ.get("USERNAME") or os.environ.get("USER") or "unknown")
    p_run.add_argument("--run-id")
    p_run.add_argument("--ttl-minutes", type=int, default=480)
    p_run.add_argument("--checkpoint-in")
    p_run.add_argument("--output", action="append")
    p_run.add_argument("--note")
    p_run.add_argument("command", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    if args.action == "status":
        return status(args.json, args.refresh)
    if args.action == "validate":
        errors, warnings, counts = validate(args.ci, args.strict)
        return print_validation(errors, warnings, counts, args.json)
    if args.action == "checkpoints":
        payload = scan_checkpoints(hash_canonical=args.hash_canonical)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(
                f"checkpoints: {len(payload['entries'])} файлов; "
                f"E02b ready {payload['requirements']['E02b_morphospace']['ready']}"
                f"/{payload['requirements']['E02b_morphospace']['required']}"
            )
            for missing in payload["requirements"]["E02b_morphospace"]["missing"]:
                print("  missing: " + missing)
        build_state()
        return 0
    if args.action == "journal-import":
        result = import_journal()
        build_state()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(
                f"journal: строк {result['rows']}; манифестов записано {result['written']}; "
                f"пропущено {result['skipped']}"
            )
        return 0
    if args.action == "logs-archive":
        payload = archive_logs(dry_run=args.dry_run)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(
                f"logs: файлов {len(payload['files'])}; "
                f"скопировано {payload['copied']}; "
                f"активных пропущено {payload['skipped_active']}; "
                f"объём {payload['total_bytes'] / 1024 ** 2:.2f} МБ"
                + (" (dry-run)" if payload["dry_run"] else "")
            )
        return 0
    if args.action == "state":
        print(json.dumps(build_state(), ensure_ascii=False, indent=2))
        return 0
    if args.action == "claim":
        payload = claim(args.experiment, args.owner, args.run_id, args.ttl_minutes, args.steal_stale)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        build_state()
        return 0
    if args.action == "release":
        release(args.experiment, args.run_id)
        build_state()
        return 0
    if args.action == "heartbeat":
        heartbeat(args.experiment, args.run_id)
        return 0
    if args.action == "run":
        return run_command(args)
    raise SystemExit("неизвестная команда")


if __name__ == "__main__":
    raise SystemExit(main())
