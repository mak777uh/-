"""test_retention_sweep.py — уборка весов не должна уносить нужное.

Правило AGENTS §5a: локально живут только канонические `nca_final.pt`, остальное
(iter, best) — расходник, но удалять его можно только когда рядом есть final и
метрики уже в git. Тест держит три границы: канонический путь не трогается,
свежий файл не трогается, а каждое удаление попадает в `lab/retention.json`
вместе с `freed_bytes`.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import retention_sweep  # noqa: E402


def make_family(root: Path, family: str, *, final_mb: int = 1, extra=("nca_iter_1000.pt", "nca_best.pt")) -> Path:
    family_dir = root / "morphogenesis" / "checkpoints" / family
    family_dir.mkdir(parents=True)
    for name in ("nca_final.pt", *extra):
        path = family_dir / name
        path.write_bytes(b"0" * (final_mb * 1024 * 1024))
        old = time.time() - 7200
        os.utime(path, (old, old))
    return family_dir


def read_retention(root: Path) -> dict:
    return json.loads((root / "lab" / "retention.json").read_text(encoding="utf-8"))


def test_sweep_removes_iter_and_best_keeps_final(tmp_path):
    make_family(tmp_path, "E02c_demo_seed1")
    code = retention_sweep.main(
        ["--repo", str(tmp_path), "--apply", "--min-age-min", "0", "--min-bytes", "0"]
    )
    assert code == 0
    family = tmp_path / "morphogenesis" / "checkpoints" / "E02c_demo_seed1"
    assert (family / "nca_final.pt").exists()
    assert not (family / "nca_iter_1000.pt").exists()
    assert not (family / "nca_best.pt").exists()
    data = read_retention(tmp_path)
    assert len(data["files"]) == 2
    assert data["freed_bytes"] == sum(entry["size_bytes"] for entry in data["files"])
    assert data["errors"] == []


def test_canonical_final_is_never_deleted(tmp_path):
    family_dir = make_family(tmp_path, "WP4_R-9_s2000_seed42", extra=())
    canonical = "morphogenesis/checkpoints/WP4_R-9_s2000_seed42/nca_final.pt"
    (tmp_path / "lab").mkdir()
    (tmp_path / "lab" / "checkpoints.json").write_text(
        json.dumps({"entries": [{"path": canonical}]}), encoding="utf-8"
    )
    code = retention_sweep.main(
        [
            "--repo",
            str(tmp_path),
            "--apply",
            "--min-age-min",
            "0",
            "--min-bytes",
            "0",
            "--delete-finals",
        ]
    )
    assert code == 0
    assert (family_dir / "nca_final.pt").exists(), "канонический final удалён быть не должен"


def test_fresh_file_is_skipped(tmp_path):
    make_family(tmp_path, "E02c_fresh_seed2")
    family = tmp_path / "morphogenesis" / "checkpoints" / "E02c_fresh_seed2"
    now = time.time()
    for path in family.glob("*.pt"):
        os.utime(path, (now, now))
    code = retention_sweep.main(
        ["--repo", str(tmp_path), "--apply", "--min-age-min", "60", "--min-bytes", "0"]
    )
    assert code == 0
    assert (family / "nca_iter_1000.pt").exists()
    data = read_retention(tmp_path) if (tmp_path / "lab" / "retention.json").exists() else {}
    assert not data.get("files")


def test_iter_without_final_is_kept(tmp_path):
    family_dir = tmp_path / "morphogenesis" / "checkpoints" / "E02c_only_iter_seed3"
    family_dir.mkdir(parents=True)
    path = family_dir / "nca_iter_1000.pt"
    path.write_bytes(b"0" * (1024 * 1024))
    old = time.time() - 7200
    os.utime(path, (old, old))
    code = retention_sweep.main(
        ["--repo", str(tmp_path), "--apply", "--min-age-min", "0", "--min-bytes", "0"]
    )
    assert code == 0
    assert path.exists(), "без final iter — единственные веса семейства, удалять нельзя"


def test_dry_run_deletes_nothing(tmp_path):
    make_family(tmp_path, "E02c_dry_seed4")
    family = tmp_path / "morphogenesis" / "checkpoints" / "E02c_dry_seed4"
    code = retention_sweep.main(["--repo", str(tmp_path), "--min-age-min", "0", "--min-bytes", "0"])
    assert code == 0
    assert (family / "nca_iter_1000.pt").exists()
    assert not (tmp_path / "lab" / "retention.json").exists()
