#!/usr/bin/env python
"""Уборка локальных весов по правилу AGENTS §5a.

GitHub — тонкая память: в git едут манифесты, журнал, метрики, отчёты, а веса
(0.5 ГБ на снапшот) живут только локально. Каждая серия оставляет после себя
`nca_iter_1000.pt`, `nca_iter_2000.pt`, `nca_best.pt` и `nca_final.pt` — это
2 ГБ на клетку. За двое суток работы так набегает 17 ГБ в `checkpoints/`, и
диск кончается посреди волны.

Что удаляется по умолчанию (безопасный режим):

1. `nca_iter_*` — если рядом есть `nca_final.pt` (промежуточные снапшоты);
2. `nca_best.pt` — если рядом есть `nca_final.pt` или метрики плеча в git.

Что **не** удаляется никогда без явного флага:

- пути из `lab/checkpoints.json` (канонические final);
- `nca_final.pt` вообще (это отдельное решение владельца, §5a п.3) —
  удаление финалов закрытых плеч включается флагом `--delete-finals`.

Защиты от удаления нужного:

- файл моложе `--min-age-min` минут не трогаем (прогон мог только что писать);
- семейство, которое упоминается в командной строке живого python-процесса,
  не трогаем — кроме процессов переписи (`e02c_census.py`): перепись читает
  только `nca_final.pt` и веса не пишет;
- путь, которого нет в каталоге, просто пропускается.

Каждое удаление пишется в `lab/retention.json` (путь, семейство, размер, mtime,
что осталось, причина) и прибавляется к `freed_bytes` — иначе через день никто
не скажет, куда делись 6 ГБ.

Запуск (из корня репозитория):

    python scripts/retention_sweep.py              # только показать план
    python scripts/retention_sweep.py --apply      # удалить и записать след
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KIND_ITER = "iter"
KIND_BEST = "best"
KIND_FINAL = "final"
MIN_BYTES_DEFAULT = 50 * 1024 * 1024  # мелочь не трогаем: шум в retention
DEFAULT_MIN_AGE_MIN = 20


def free_gb(path: Path) -> float:
    usage = __import__("shutil").disk_usage(str(path))
    return round(usage.free / 1024**3, 2)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def kind_of(name: str) -> str | None:
    if name.startswith("nca_iter_"):
        return KIND_ITER
    if name == "nca_best.pt":
        return KIND_BEST
    if name == "nca_final.pt":
        return KIND_FINAL
    return None


def canonical_paths(repo: Path) -> set[str]:
    """Пути из lab/checkpoints.json: эти файлы — канон, их не трогаем."""
    path = repo / "lab" / "checkpoints.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    out = set()
    for entry in data.get("entries", []) or []:
        p = entry.get("path")
        if p:
            out.add(str(p).replace("\\", "/"))
    return out


def live_python_cmdlines() -> list[str]:
    """Командные строки живых python-процессов (без psutil)."""
    if os.name == "nt":
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
            "ForEach-Object { $_.CommandLine }",
        ]
    else:
        cmd = ["sh", "-c", "ps -eo args | grep -i python || true"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return []
    return [line.strip() for line in (res.stdout or "").splitlines() if line.strip()]


def manifests_by_family(repo: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    runs = repo / "lab" / "runs"
    if not runs.is_dir():
        return out
    for path in sorted(runs.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        family = data.get("experiment")
        if family:
            out[str(family)] = data
            out.setdefault(str(family).split("_census_")[0], data)
    return out


def blocked_families(cmdlines: list[str]) -> set[str]:
    """Семейства, которые нельзя трогать: их держит живой процесс не-переписи."""
    blocked: set[str] = set()
    for line in cmdlines:
        low = line.lower()
        if "retention_sweep" in low or "pytest" in low:
            continue
        if "e02c_census.py" in low:  # перепись читает только final
            continue
        if "morphogenesis" not in low and "train.py" not in low and "checkpoints" not in low:
            continue
        for token in line.replace("/", "\\").split():
            if "checkpoints\\" in token:
                parts = token.split("checkpoints\\")
                if len(parts) > 1:
                    blocked.add(parts[1].split("\\")[0])
    return blocked


def plan_deletions(
    repo: Path,
    min_age_min: int,
    min_bytes: int,
    delete_finals: bool,
) -> tuple[list[dict], list[dict]]:
    ckpt = repo / "morphogenesis" / "checkpoints"
    keep = canonical_paths(repo)
    blocked = blocked_families(live_python_cmdlines())
    manifests = manifests_by_family(repo)
    now = time.time()
    delete: list[dict] = []
    skip: list[dict] = []

    if not ckpt.is_dir():
        return delete, skip

    for family_dir in sorted(p for p in ckpt.iterdir() if p.is_dir()):
        family = family_dir.name
        final = family_dir / "nca_final.pt"
        has_final = final.exists()
        for path in sorted(family_dir.glob("*.pt")):
            kind = kind_of(path.name)
            if kind is None:
                continue
            rel = f"morphogenesis/checkpoints/{family}/{path.name}"
            size = path.stat().st_size
            mtime = path.stat().st_mtime
            age_min = (now - mtime) / 60

            if rel in keep:
                skip.append({"path": rel, "reason": "канонический файл из lab/checkpoints.json"})
                continue
            if size < min_bytes:
                skip.append({"path": rel, "reason": f"меньше {min_bytes // (1024*1024)} МБ, места не освободит"})
                continue
            if age_min < min_age_min:
                skip.append(
                    {"path": rel, "reason": f"свежий файл ({age_min:.0f} мин), прогон мог ещё писать"}
                )
                continue
            if family in blocked:
                skip.append({"path": rel, "reason": f"семейство занято живым прогоном ({family})"})
                continue

            if kind in (KIND_ITER, KIND_BEST):
                if not has_final:
                    skip.append({"path": rel, "reason": "нет nca_final.pt: это единственные веса семейства"})
                    continue
                reason = (
                    "промежуточный снапшот (nca_iter_*), final на месте"
                    if kind == KIND_ITER
                    else "best-снапшот при наличии final; метрики плеча в git"
                )
                delete.append(
                    {
                        "path": rel,
                        "family": family,
                        "kind": kind,
                        "size_bytes": size,
                        "mtime": datetime.fromtimestamp(mtime, timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "kept": f"morphogenesis/checkpoints/{family}/nca_final.pt",
                        "reason": reason,
                    }
                )
                continue

            # nca_final.pt: только по явному флагу и только для закрытой серии.
            if not delete_finals:
                skip.append(
                    {
                        "path": rel,
                        "reason": "final удаляется только по решению владельца (§5a п.3), нужен --delete-finals",
                    }
                )
                continue
            manifest = manifests.get(family) or {}
            status = str(manifest.get("status") or "")
            if status not in {"finished", "failed", "aborted"}:
                skip.append({"path": rel, "reason": f"нет закрытого манифеста семейства (status={status or 'нет'})"})
                continue
            delete.append(
                {
                    "path": rel,
                    "family": family,
                    "kind": KIND_FINAL,
                    "size_bytes": size,
                    "mtime": datetime.fromtimestamp(mtime, timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "kept": "манифест, журнал и метрики в git",
                    "reason": "неканонический final закрытого/замещённого плеча (§5a п.3)",
                }
            )
    return delete, skip


def append_retention(repo: Path, deleted: list[dict], skipped: list[dict]) -> Path:
    path = repo / "lab" / "retention.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema_version", 1)
    files = data.get("files") or []
    files.extend(deleted)
    data["files"] = files
    data["skipped"] = (data.get("skipped") or []) + skipped
    data["kept_canonical"] = sorted(canonical_paths(repo))
    data["errors"] = data.get("errors") or []
    data["freed_bytes"] = int(data.get("freed_bytes") or 0) + sum(
        int(entry["size_bytes"]) for entry in deleted
    )
    data["generated_at"] = _now_utc()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(REPO), help="корень репозитория")
    ap.add_argument("--apply", action="store_true", help="удалить (без флага — только план)")
    ap.add_argument("--min-age-min", type=int, default=DEFAULT_MIN_AGE_MIN)
    ap.add_argument(
        "--min-bytes",
        type=int,
        default=MIN_BYTES_DEFAULT,
        help="файлы меньше этого размера не трогаем",
    )
    ap.add_argument(
        "--delete-finals",
        action="store_true",
        help="разрешить удаление неканонических nca_final.pt закрытых плеч",
    )
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    ckpt = repo / "morphogenesis" / "checkpoints"
    before = free_gb(repo)
    delete, skip = plan_deletions(repo, args.min_age_min, args.min_bytes, args.delete_finals)

    total = sum(entry["size_bytes"] for entry in delete)
    print(f"[retention] свободно до: {before} ГБ; план: {len(delete)} файл(ов) на {total / 1024**3:.2f} ГБ")
    for entry in delete:
        print(f"  - {entry['path']} ({entry['size_bytes'] / 1024**3:.2f} ГБ) — {entry['reason']}")
    for entry in skip[:12]:
        print(f"  = {entry['path']}: {entry['reason']}")
    if len(skip) > 12:
        print(f"  = … ещё {len(skip) - 12} пропусков")

    if not args.apply:
        print("[retention] режим плана: ничего не удалено (--apply чтобы применить)")
        return 0

    removed = 0
    for entry in delete:
        path = repo / entry["path"]
        try:
            path.unlink()
            removed += 1
        except OSError as exc:
            print(f"[retention] не удалось удалить {entry['path']}: {exc}")
            entry["error"] = str(exc)
    ok = [e for e in delete if "error" not in e]
    if ok:
        append_retention(repo, ok, skip)
    after = free_gb(repo)
    print(f"[retention] удалено {removed} файл(ов), освобождено {total / 1024**3:.2f} ГБ")
    print(f"[retention] свободно после: {after} ГБ; след в lab/retention.json")
    return 0 if removed == len(delete) else 1


if __name__ == "__main__":
    raise SystemExit(main())
