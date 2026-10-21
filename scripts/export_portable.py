"""export_portable.py — собрать portable inference-пакет E02b без обучения.

Зачем: канонический `nca_final.pt` весит 514.5 МБ, из которых 512 МБ — пул
состояний обучения (256 состояний). Для inference и для перепроверки переписи
нужен только `model_state_dict` (0.14 МБ) плюс скаляры и metadata. Пакет
собирается из уже закрытых артефактов E02b, веса не переобучаются и не
подменяются.

Что делает:
  * читает `lab/checkpoints.json` (канон) и `lab/experiments/E02b_morphospace.json`
    (требования) и копирует ровно те семейства, что перечислены в требованиях;
  * для каждого `nca_final.pt` проверяет sha256 против индекса и metadata против
    активной спецификации, затем пишет lite-версию с теми же путями;
  * копирует исходники (`config.py`, `nca_core.py`, `topology.py`,
    `e02b_morphospace.py`, `utils/`), `census.json`, замороженные центроиды,
    `wp4_ablations.json` (оттуда берутся overrides ALIVE_WARMUP_ITERS) и
    lab-метаданные с подменённым sha256 (lite) — полный sha256 едет только в
    `portable_manifest.json`;
  * кладёт `verify_portable.py`, `LICENSE`, `README.md`,
    `requirements-inference.txt` и `portable_manifest.json`.

Запуск:
    python scripts/export_portable.py --out dist/e02b-portable
    python scripts/export_portable.py --out dist/e02b-portable \
        --families WP4_R-9_s2000_seed42,WP4_R-9_s2000_seed101

Границы: без обучения, без правок config.py, без записи в lab/, reports/ и
articles/. Пакет собирается во временный каталог и подменяет `--out` только
если там уже лежит `portable_manifest.json` (маркер прошлой сборки).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MORPH_ROOT = REPO_ROOT / "morphogenesis"

# §9.2: config обязан импортироваться раньше torch.
if str(MORPH_ROOT) not in sys.path:
    sys.path.insert(0, str(MORPH_ROOT))

import config  # noqa: E402
import torch  # noqa: E402

EXPERIMENT_ID = "E02b_morphospace"
MANIFEST_NAME = "portable_manifest.json"
SCHEMA_VERSION = 1

# Ключи lite-чекпоинта. Ровно они и ничего больше: optimizer/scheduler/pool/state
# в пакет не едут, иначе смысл lite теряется (512 МБ пула на файл).
LITE_KEYS = (
    "model_state_dict",
    "iteration",
    "seed",
    "grid_size",
    "n_channels",
    "spec_version",
    "revision",
    "stress_enabled",
    "stress_channel",
    "metadata",
)
FORBIDDEN_LITE_KEYS = (
    "optimizer_state_dict",
    "scheduler_state_dict",
    "pool_state_dict",
    "state",
)

# Исходники, без которых пакет не запускается. Список закрытый: пакет должен
# оставаться читаемым, а не тащить весь стенд.
SOURCE_FILES = (
    "config.py",
    "nca_core.py",
    "topology.py",
    "e02b_morphospace.py",
)
UTILS_FILES = ("__init__.py", "determinism.py", "logging.py", "stats.py")

REQUIREMENTS_TEXT = """\
# Зависимости portable inference-пакета E02b (без обучения).
# Проверенное окружение: Python 3.13.11, torch 2.6.0+cu124, numpy 2.5.4,
# scipy 1.18.1. CPU-сборка torch тоже подходит: forward и дескрипторы
# считаются на CPU, но smoke на CPU заметно медленнее (минуты на сид).
torch>=2.6,<3
numpy>=2.1,<3
scipy>=1.14,<2
"""


class PortableExportError(RuntimeError):
    """Ошибка сборки: отсутствует файл или metadata несовместима со спекой."""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def git_info(repo_root: Path) -> dict:
    """Коммит-источник и флаг грязи. git может отсутствовать — это не ошибка."""

    def _git(*args: str) -> str | None:
        try:
            proc = subprocess.run(
                ["git", "-C", str(repo_root), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()

    commit = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain")
    return {
        "git_commit": commit,
        "git_commit_short": commit[:12] if commit else None,
        "git_dirty": bool(status),
        "git_dirty_files": len(status.splitlines()) if status else 0,
    }


def require_files(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not Path(path).is_file()]
    if missing:
        raise PortableExportError(
            "нет обязательных файлов для portable-пакета:\n  " + "\n  ".join(missing)
        )


def load_full_checkpoint(path: Path) -> dict:
    """Прочитать канонический nca_final.pt. Не подменяет и не «чинит» его."""
    path = Path(path)
    if not path.is_file():
        raise PortableExportError(f"чекпоинт отсутствует: {path}")
    ck = torch.load(str(path), map_location="cpu", weights_only=False)
    if not isinstance(ck, dict):
        raise PortableExportError(f"{path}: чекпоинт не dict, а {type(ck).__name__}")
    return ck


def validate_full_checkpoint(ck: dict, family: str) -> None:
    """Metadata и архитектура обязаны совпадать с активной спецификацией.

    §13.5: чекпоинты разных ревизий не смешиваются. Пакет не должен молча
    уехать с чужими весами, поэтому здесь отказ, а не предупреждение.
    """
    if "model_state_dict" not in ck or not isinstance(ck["model_state_dict"], dict):
        raise PortableExportError(f"{family}: нет model_state_dict")
    metadata = ck.get("metadata")
    if not isinstance(metadata, dict) or not metadata:
        raise PortableExportError(f"{family}: нет metadata — совместимость не доказать")
    version = metadata.get("spec_version")
    if version != config.SPEC_VERSION:
        raise PortableExportError(
            f"{family}: несовместимая версия чекпоинта {version!r}; "
            f"активная спецификация {config.SPEC_VERSION} ({config.SPEC_REVISION})"
        )
    revision = metadata.get("revision")
    if revision not in (None, config.SPEC_REVISION):
        raise PortableExportError(
            f"{family}: ревизия {revision!r} != {config.SPEC_REVISION}"
        )
    if int(metadata.get("grid_size", -1)) != config.GRID_SIZE:
        raise PortableExportError(
            f"{family}: grid_size={metadata.get('grid_size')} != {config.GRID_SIZE}"
        )
    if int(metadata.get("n_channels", -1)) != config.N_CHANNELS:
        raise PortableExportError(
            f"{family}: n_channels={metadata.get('n_channels')} != {config.N_CHANNELS}"
        )
    stress_channel = ck.get("stress_channel", config.STRESS_CHANNEL)
    if int(stress_channel) != int(config.STRESS_CHANNEL):
        raise PortableExportError(
            f"{family}: stress_channel={stress_channel} != {config.STRESS_CHANNEL}"
        )
    grid_size = ck.get("grid_size", metadata.get("grid_size"))
    if grid_size is not None and int(grid_size) != config.GRID_SIZE:
        raise PortableExportError(f"{family}: grid_size в корне не {config.GRID_SIZE}")
    n_channels = ck.get("n_channels", metadata.get("n_channels"))
    if n_channels is not None and int(n_channels) != config.N_CHANNELS:
        raise PortableExportError(f"{family}: n_channels в корне не {config.N_CHANNELS}")


def make_lite_checkpoint(ck: dict) -> dict:
    """Оставить только то, что нужно inference: веса + скаляры + metadata."""
    validate_full_checkpoint(ck, str(ck.get("metadata", {}).get("experiment") or "checkpoint"))
    metadata = dict(ck["metadata"])
    seed = ck.get("seed", metadata.get("seed"))
    if seed is None:
        raise PortableExportError("чекпоинт без seed: нечем подписать lite-файл")
    lite = {
        "model_state_dict": ck["model_state_dict"],
        "iteration": int(ck.get("iteration", metadata.get("iteration", 0)) or 0),
        "seed": int(seed),
        "grid_size": int(ck.get("grid_size", config.GRID_SIZE)),
        "n_channels": int(ck.get("n_channels", config.N_CHANNELS)),
        "spec_version": str(ck.get("spec_version", metadata["spec_version"])),
        "revision": str(ck.get("revision", metadata.get("revision", config.SPEC_REVISION))),
        "stress_enabled": bool(ck.get("stress_enabled", True)),
        "stress_channel": int(ck.get("stress_channel", config.STRESS_CHANNEL)),
        "metadata": metadata,
    }
    extra = set(lite) - set(LITE_KEYS)
    if extra:
        raise PortableExportError(f"lite содержит лишние ключи: {sorted(extra)}")
    missing = set(LITE_KEYS) - set(lite)
    if missing:
        raise PortableExportError(f"lite не содержит обязательных ключей: {sorted(missing)}")
    return lite


def save_lite_checkpoint(lite: dict, path: Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(lite, str(path))
    return path.stat().st_size


def verify_lite_roundtrip(lite: dict, path: Path, family: str) -> None:
    """Перечитать lite и убедиться, что веса и metadata не потерялись.

    Побитовое равенство forward проверяется отдельно тестом
    (`tests/test_portable_export.py`); здесь — целостность сериализации.
    """
    reloaded = torch.load(str(path), map_location="cpu", weights_only=False)
    if set(reloaded) != set(LITE_KEYS):
        raise PortableExportError(f"{family}: после перечитывания ключи lite изменились")
    for key in FORBIDDEN_LITE_KEYS:
        if key in reloaded:
            raise PortableExportError(f"{family}: в lite попал запрещённый ключ {key}")
    full_sd = lite["model_state_dict"]
    lite_sd = reloaded["model_state_dict"]
    if set(full_sd) != set(lite_sd):
        raise PortableExportError(f"{family}: набор тензоров изменился при сохранении")
    for name, tensor in full_sd.items():
        if not torch.equal(tensor, lite_sd[name]):
            raise PortableExportError(f"{family}: тензор {name} изменился при сохранении")
    if reloaded["metadata"].get("spec_version") != config.SPEC_VERSION:
        raise PortableExportError(f"{family}: metadata.spec_version потеряна")


def select_families(required: list[str], families: str | None) -> tuple[list[str], bool]:
    """Отфильтровать семейства. Частичный пакет должен быть честно помечен."""
    if not families:
        return list(required), False
    wanted = [item.strip() for item in families.split(",") if item.strip()]
    unknown = [item for item in wanted if item not in required]
    if unknown:
        raise PortableExportError(
            "семейства вне требований E02b: " + ", ".join(unknown)
        )
    seen: list[str] = []
    for item in wanted:
        if item not in seen:
            seen.append(item)
    if not seen:
        raise PortableExportError("--families задан, но пуст")
    return seen, len(seen) != len(required)


def portable_index(index: dict, lite_by_family: dict[str, dict], families: list[str]) -> dict:
    """Копия lab/checkpoints.json, где sha256/size — от lite-файлов.

    Полный sha256 остаётся только в portable_manifest.json: индекс внутри пакета
    обязан описывать ровно те файлы, которые в пакете лежат.
    """
    out = json.loads(json.dumps(index))
    kept = []
    for entry in out.get("entries", []):
        family = entry.get("family")
        if family not in families:
            continue
        info = lite_by_family[family]
        entry = dict(entry)
        entry["sha256"] = info["sha256"]
        entry["size_bytes"] = info["size_bytes"]
        entry["hash_status"] = "complete"
        entry["notes"] = (
            "portable lite (model_state_dict+metadata); "
            "полный sha256 и размер — в portable_manifest.json"
        )
        kept.append(entry)
    out["entries"] = kept

    requirement = (out.get("requirements") or {}).get(EXPERIMENT_ID)
    if isinstance(requirement, dict):
        items = [item for item in requirement.get("items", []) if item.get("family") in families]
        requirement["items"] = items
        requirement["required"] = len(items)
        requirement["ready"] = len(items)
        requirement["missing"] = []
    out["portable"] = {
        "exported_at": utc_now(),
        "families": list(families),
        "kind": "lite",
        "lite_keys": list(LITE_KEYS),
        "note": "Индекс описывает файлы пакета; полный sha256 — в portable_manifest.json",
    }
    return out


def portable_descriptor(descriptor: dict, families: list[str]) -> dict:
    out = json.loads(json.dumps(descriptor))
    out["checkpoint_requirements"] = [
        item for item in out.get("checkpoint_requirements", []) if item.get("family") in families
    ]
    out["portable"] = {
        "kind": "lite_checkpoints",
        "families": list(families),
        "note": "Требования сужены до семейств, вошедших в пакет",
    }
    return out


def package_files(root: Path, exclude: tuple[str, ...] = (MANIFEST_NAME,)) -> list[dict]:
    """Все файлы пакета, кроме манифеста: путь, размер, sha256.

    `__pycache__` и `*.pyc` выкидываются явно: пакет — артефакт, а не рабочая
    копия; кеш байткода ломает детерминированную сборку и раздувает список
    файлов после первого же запуска verify внутри каталога.
    """
    root = Path(root)
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        if any(part in (".pytest_cache", ".ruff_cache", "__pycache__") for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        files.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def assert_relative_paths(manifest: dict) -> None:
    """В манифесте не должно быть абсолютных путей и Windows-слэшей.

    Пакет обязан оставаться переносимым: путь `C:\\...\\nca_final.pt` в
    манифесте — это утечка машины сборки, а не метаданные.
    """
    problems = []
    for item in manifest["files"]:
        rel = item["path"]
        if rel.startswith("/") or "\\" in rel or ":" in rel.split("/")[0]:
            problems.append(rel)
    for family, info in manifest["checkpoints"].items():
        rel = info["path"]
        if rel.startswith("/") or "\\" in rel or ":" in rel.split("/")[0]:
            problems.append(f"{family}: {rel}")
    for key, info in manifest["datasets"].items():
        rel = info["path"]
        if rel.startswith("/") or "\\" in rel or ":" in rel.split("/")[0]:
            problems.append(f"{key}: {rel}")
    if problems:
        raise PortableExportError("в манифесте абсолютные пути: " + ", ".join(problems))


def build_manifest(
    root: Path,
    *,
    families: list[str],
    partial: bool,
    omitted: list[str],
    checkpoints: dict[str, dict],
    datasets: dict[str, dict],
    source: dict,
    environment: dict,
) -> dict:
    files = package_files(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment": EXPERIMENT_ID,
        "kind": "portable_inference_package",
        "created_at": utc_now(),
        "source": source,
        "package": {
            "partial": bool(partial),
            "families": list(families),
            "omitted_families": list(omitted),
            "n_checkpoints": len(checkpoints),
            "n_files": len(files) + 1,  # + сам манифест
            "total_bytes": sum(item["size_bytes"] for item in files),
            "spec_version": config.SPEC_VERSION,
            "revision": config.SPEC_REVISION,
            "how_to_verify": "python verify_portable.py --mode smoke",
        },
        "checkpoints": checkpoints,
        "datasets": datasets,
        "files": files,
        "environment": environment,
        "notes": [
            "lite = model_state_dict + скаляры + metadata; optimizer/scheduler/pool/state удалены",
            "forward lite побитово равен полному на CPU (tests/test_portable_export.py)",
            "census.json — каноническая перепись E02b, пакет её не пересчитывает",
            "пакет не является новым экспериментом и не меняет границы E02b",
        ],
    }


def environment_info() -> dict:
    import numpy
    import scipy

    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "device": str(config.DEVICE),
        "cuda": torch.version.cuda,
    }


def _readme(manifest_preview: dict) -> str:
    source = manifest_preview["source"]
    package = manifest_preview["package"]
    families = package["families"]
    partial = package["partial"]
    lines = [
        "# Morphogenesis E02b — portable inference package",
        "",
        "Переносимый пакет для воспроизведения переписи морфопространства E02b",
        "без обучения. Содержит lite-чекпоинты (`model_state_dict` + скаляры +",
        "metadata), исходники inference-кода, каноническую перепись и замороженные",
        "центроиды классов.",
        "",
        "## Что внутри",
        "",
        "```",
        "morphogenesis/config.py, nca_core.py, topology.py, e02b_morphospace.py, utils/",
        "morphogenesis/checkpoints/<family>/nca_final.pt   # lite, ~0.15 МБ",
        "morphogenesis/experiments/E02b_morphospace/census.json",
        "morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json",
        "experiments/E02_pattern/wp4_ablations.json       # overrides ALIVE_WARMUP_ITERS",
        "lab/checkpoints.json, lab/experiments/E02b_morphospace.json",
        "verify_portable.py, portable_manifest.json",
        "LICENSE, README.md, requirements-inference.txt",
        "```",
        "",
        "Пути внутри пакета те же, что в репозитории: `e02b_morphospace.py` ищет",
        "`lab/` и `experiments/` относительно корня пакета, поэтому ничего",
        "переписывать не нужно.",
        "",
        f"Собрано из коммита `{source.get('git_commit') or 'unknown'}`",
        f"({source.get('exported_at', '')}). Спецификация {package.get('spec_version')}",
        f"({package.get('revision')}). Семейств: {len(families)}"
        + (" (частичный пакет: " + ", ".join(package.get("omitted_families", [])) + ")"
           if partial else ""),
        "",
        "## Быстрый старт",
        "",
        "```bash",
        "python -m venv .venv",
        ".venv/Scripts/python.exe -m pip install -r requirements-inference.txt  # Windows",
        "# .venv/bin/python -m pip install -r requirements-inference.txt        # Linux/macOS",
        "",
        "python verify_portable.py --mode smoke",
        "```",
        "",
        "Smoke: 2 обученные модели (R-9 seed42, R-9 seed101) и необученная",
        "архитектура × 16 сидов (0–15) × 2000 шагов. Каждый финальный дескриптор",
        "проецируется на замороженные центроиды; классы сравниваются с",
        "`census.json`. Результат — `verify_report.json` рядом с `verify_portable.py`.",
        "",
        "```bash",
        "python verify_portable.py --mode full   # 13 семейств × 64 сида × 2000 шагов",
        "```",
        "",
        "`--mode full` повторяет полный протокол (Ward + ARI против census). На",
        "RTX 3070 это ~85 минут; запускать только по явному решению, а не «на всякий",
        "случай».",
        "",
        "## Lite против полного чекпоинта",
        "",
        "Полный `nca_final.pt` — 514.5 МБ, из них 512 МБ пул состояний обучения",
        "(256 состояний). Для inference пул, оптимизатор, scheduler и `state` не",
        "нужны: lite оставляет `model_state_dict`, `iteration`, `seed`, `grid_size`,",
        "`n_channels`, `spec_version`, `revision`, `stress_enabled`, `stress_channel`,",
        "`metadata`. Побитовое равенство forward проверяется тестом",
        "`morphogenesis/tests/test_portable_export.py`; sha256 полного файла и lite",
        "лежат в `portable_manifest.json`, чтобы подмену весов было видно.",
        "",
        "## Ручная загрузка",
        "",
        "```python",
        "import os, sys",
        "sys.path.insert(0, os.path.abspath('morphogenesis'))",
        "import config                      # §9.2: config раньше torch",
        "import torch",
        "import e02b_morphospace as e02b     # запускать из корня пакета",
        "",
        "specs = e02b.load_checkpoint_specs()",
        "model, ck = e02b.build_model(specs[0], torch.device('cpu'))",
        "print(specs[0].family, ck['metadata']['spec_version'])",
        "```",
        "",
        "## Границы",
        "",
        "- Это не новый эксперимент и не проверка гипотез: пакет воспроизводит уже",
        "  закрытую перепись E02b. Числа census не переписываются.",
        "- `struct_1` — архитектурный конфаунд (совпадает с необученной сетью),",
        "  `struct_2` — кандидат на выученную морфологию. По результатам NCA нельзя",
        "  объявлять «жизнь», «сознание» или «интеллект».",
        "- Протокол и отчёт живут в репозитории (`reports/2026-10-20-e02b-plan.md`,",
        "  `reports/2026-10-20-e02b-results.md`); здесь только метаданные-указатели.",
        "",
        "## Лицензия",
        "",
        "MIT, см. `LICENSE`.",
        "",
    ]
    return "\n".join(lines)


def export(
    out: Path,
    *,
    families: str | None = None,
    repo_root: Path = REPO_ROOT,
    keep_tmp: bool = False,
) -> dict:
    """Собрать пакет. Возвращает манифест."""
    repo_root = Path(repo_root).resolve()
    morph_root = repo_root / "morphogenesis"
    out = Path(out).resolve()

    index_path = repo_root / "lab" / "checkpoints.json"
    descriptor_path = repo_root / "lab" / "experiments" / f"{EXPERIMENT_ID}.json"
    ablations_path = repo_root / "morphogenesis" / "experiments" / "E02_pattern" / "wp4_ablations.json"
    census_path = morph_root / "experiments" / EXPERIMENT_ID / "census.json"
    centroids_path = morph_root / "experiments" / EXPERIMENT_ID / "class_centroids_frozen.json"
    verifier_src = repo_root / "scripts" / "verify_portable.py"
    license_src = repo_root / "LICENSE"

    require_files(
        [
            index_path,
            descriptor_path,
            ablations_path,
            census_path,
            centroids_path,
            verifier_src,
            license_src,
            *[morph_root / name for name in SOURCE_FILES],
            *[morph_root / "utils" / name for name in UTILS_FILES],
        ]
    )

    index = load_json(index_path)
    descriptor = load_json(descriptor_path)
    frozen = load_json(centroids_path)

    required = [item["family"] for item in descriptor.get("checkpoint_requirements", [])]
    if not required:
        raise PortableExportError("дескриптор E02b не содержит checkpoint_requirements")
    wanted, partial = select_families(required, families)
    omitted = [item for item in required if item not in wanted]

    by_family = {
        entry["family"]: entry
        for entry in index.get("entries", [])
        if entry.get("kind") == "final"
    }
    missing_entries = [item for item in wanted if item not in by_family]
    if missing_entries:
        raise PortableExportError(
            "нет final-записи в lab/checkpoints.json: " + ", ".join(missing_entries)
        )

    # Проверка согласованности данных ДО записи: census и центроиды должны быть
    # той самой переписью, иначе smoke будет сравнивать с чужим результатом.
    census_sha = sha256_file(census_path)
    declared_sha = (frozen.get("source_census") or {}).get("sha256")
    if declared_sha and census_sha != declared_sha:
        raise PortableExportError(
            "census.json не совпадает с source_census.sha256 в "
            f"class_centroids_frozen.json: {census_sha} != {declared_sha}"
        )
    census = load_json(census_path)
    census_families = {run.get("family") for run in census.get("runs", [])}
    absent_in_census = [item for item in wanted if item not in census_families]
    if absent_in_census:
        raise PortableExportError(
            "в census.json нет семейств: " + ", ".join(absent_in_census)
        )

    staging = out.parent / f".{out.name}.tmp-{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    pkg_morph = staging / "morphogenesis"
    pkg_ckpt = pkg_morph / "checkpoints"
    pkg_exp = pkg_morph / "experiments" / EXPERIMENT_ID
    for path in (pkg_morph, pkg_ckpt, pkg_exp, staging / "lab" / "experiments",
                 staging / "experiments" / "E02_pattern"):
        path.mkdir(parents=True, exist_ok=True)

    checkpoints: dict[str, dict] = {}
    lite_by_family: dict[str, dict] = {}
    try:
        for family in wanted:
            entry = by_family[family]
            rel = entry["path"]
            full_path = (repo_root / rel).resolve()
            require_files([full_path])
            full_size = full_path.stat().st_size
            expected_size = entry.get("size_bytes")
            if expected_size and int(expected_size) != full_size:
                raise PortableExportError(
                    f"{family}: размер {full_size} != индекс {expected_size} — чекпоинт подменён?"
                )
            full_sha = sha256_file(full_path)
            expected_sha = entry.get("sha256")
            if expected_sha and full_sha != expected_sha:
                raise PortableExportError(
                    f"{family}: sha256 {full_sha} != индекс {expected_sha}; "
                    "подменять чекпоинт запрещено (AGENTS.md §5)"
                )
            ck = load_full_checkpoint(full_path)
            validate_full_checkpoint(ck, family)
            lite = make_lite_checkpoint(ck)
            lite_rel = f"morphogenesis/checkpoints/{family}/nca_final.pt"
            lite_path = staging / lite_rel
            lite_size = save_lite_checkpoint(lite, lite_path)
            verify_lite_roundtrip(lite, lite_path, family)
            lite_sha = sha256_file(lite_path)
            lite_by_family[family] = {"sha256": lite_sha, "size_bytes": lite_size}
            checkpoints[family] = {
                "path": lite_rel,
                "full_sha256": full_sha,
                "full_bytes": full_size,
                "lite_sha256": lite_sha,
                "lite_bytes": lite_size,
                "lite_keys": list(LITE_KEYS),
                "removed": list(FORBIDDEN_LITE_KEYS),
                "family": family,
                "seed": int(entry.get("seed", 0)),
                "arm": str(entry.get("arm") or ""),
                "steps_trained": int(entry.get("steps", 0)),
            }
            del ck, lite
            print(
                f"[export] {family}: full {full_size / 1e6:.1f} МБ -> lite "
                f"{lite_size / 1e3:.1f} КБ"
            )

        # Исходники: байт-в-байт, без правок (пакет обязан повторять код прогона).
        for name in SOURCE_FILES:
            shutil.copy2(morph_root / name, pkg_morph / name)
        (pkg_morph / "utils").mkdir(parents=True, exist_ok=True)
        for name in UTILS_FILES:
            shutil.copy2(morph_root / "utils" / name, pkg_morph / "utils" / name)

        shutil.copy2(census_path, pkg_exp / "census.json")
        shutil.copy2(centroids_path, pkg_exp / "class_centroids_frozen.json")
        shutil.copy2(ablations_path, staging / "experiments" / "E02_pattern" / "wp4_ablations.json")

        write_json(staging / "lab" / "checkpoints.json",
                   portable_index(index, lite_by_family, wanted))
        write_json(staging / "lab" / "experiments" / f"{EXPERIMENT_ID}.json",
                   portable_descriptor(descriptor, wanted))
        shutil.copy2(verifier_src, staging / "verify_portable.py")
        shutil.copy2(license_src, staging / "LICENSE")

        source = {
            **git_info(repo_root),
            "repo": "project-morphogenesis",
            "exported_at": utc_now(),
            "exporter": "scripts/export_portable.py",
        }
        datasets = {
            "census": {
                "path": f"morphogenesis/experiments/{EXPERIMENT_ID}/census.json",
                "sha256": census_sha,
                "size_bytes": census_path.stat().st_size,
                "n_runs": len(census.get("runs", [])),
            },
            "class_centroids_frozen": {
                "path": f"morphogenesis/experiments/{EXPERIMENT_ID}/class_centroids_frozen.json",
                "sha256": sha256_file(centroids_path),
                "size_bytes": centroids_path.stat().st_size,
                "k": frozen.get("k"),
                "class_names": frozen.get("class_names"),
            },
            "wp4_ablations": {
                "path": "experiments/E02_pattern/wp4_ablations.json",
                "sha256": sha256_file(ablations_path),
                "size_bytes": ablations_path.stat().st_size,
            },
        }
        environment = environment_info()
        preview = {
            "source": {**source, "exported_at": source["exported_at"]},
            "package": {
                "families": wanted,
                "partial": partial,
                "omitted_families": omitted,
                "spec_version": config.SPEC_VERSION,
                "revision": config.SPEC_REVISION,
            },
        }
        (staging / "README.md").write_text(_readme(preview), encoding="utf-8", newline="\n")
        (staging / "requirements-inference.txt").write_text(
            REQUIREMENTS_TEXT, encoding="utf-8", newline="\n"
        )

        manifest = build_manifest(
            staging,
            families=wanted,
            partial=partial,
            omitted=omitted,
            checkpoints=checkpoints,
            datasets=datasets,
            source=source,
            environment=environment,
        )
        assert_relative_paths(manifest)
        write_json(staging / MANIFEST_NAME, manifest)

        # Подмена каталога: только собственная сборка (маркер) или пустой путь.
        if out.exists():
            if not (out / MANIFEST_NAME).is_file() and any(out.iterdir()):
                raise PortableExportError(
                    f"{out} существует и не похож на прошлую сборку (нет {MANIFEST_NAME})"
                )
            shutil.rmtree(out)
        os.replace(staging, out)
    finally:
        if staging.exists() and not keep_tmp:
            shutil.rmtree(staging, ignore_errors=True)

    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="dist/e02b-portable", help="каталог пакета")
    parser.add_argument("--families", default=None, help="подмножество семейств через запятую")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="корень репозитория")
    parser.add_argument("--keep-tmp", action="store_true", help="не удалять staging при ошибке")
    args = parser.parse_args(argv)

    try:
        manifest = export(
            Path(args.out),
            families=args.families,
            repo_root=Path(args.repo_root),
            keep_tmp=bool(args.keep_tmp),
        )
    except PortableExportError as exc:
        # Ошибка сборки — это отказ, а не трейсбек: пакет нельзя «дочинить» молча.
        print(f"[export] ОШИБКА: {exc}")
        return 2
    out = Path(args.out).resolve()
    total = manifest["package"]["total_bytes"]
    print(
        f"[export] готово: {out}\n"
        f"[export] файлов={manifest['package']['n_files']} "
        f"размер={total / 1e6:.2f} МБ "
        f"семейств={len(manifest['package']['families'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
