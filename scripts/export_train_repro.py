"""export_train_repro.py — собрать пакет для независимого воспроизведения обучения E02c.

Зачем отдельный пакет. Portable-пакет E02b (`scripts/export_portable.py`) несёт
только **инференс**: lite-веса и перепись. Независимая проверка обучения требует
другого: кода, который обучает с нуля, и рецепта, зафиксированного в overrides.
Этот скрипт собирает такой пакет из репозитория без единой правки исходников:
файлы копируются байт-в-байт, а рядом кладутся манифест, эталонные значения и
инструкция.

Пакет самодостаточен: обучение -> чекпоинт -> перепись тем же кодом и теми же
замороженными центроидами -> сводка. Ничего доустанавливать, кроме
`requirements-train.txt`, не нужно.

Запуск (из корня репозитория):

    python scripts/export_train_repro.py --out dist/e02c-train-repro

Пакет в git не едет: `dist/` в `.gitignore`. В git едут только скрипт, тесты и
протокол.
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
MANIFEST_NAME = "train_repro_manifest.json"

# Код, без которого обучение и перепись не запускаются. Список закрытый: если
# новый модуль появится в импортах train.py, тест это поймает.
SOURCE_FILES = (
    "config.py",
    "train.py",
    "nca_core.py",
    "evaluate.py",
    "target_patterns.py",
    "topo_proxy.py",
    "topology.py",
    "wp4_ablations.py",
    "e02c_replication.py",
    "e02c_census.py",
    "e02b_morphospace.py",
)
UTILS_FILES = ("__init__.py", "logging.py", "determinism.py", "stats.py")
DATA_FILES = (
    ("experiments/E02b_morphospace/class_centroids_frozen.json", "experiments/E02b_morphospace/class_centroids_frozen.json"),
    ("experiments/E02b_morphospace/census.json", "experiments/E02b_morphospace/census.json"),
)

REQUIREMENTS_TEXT = """\
# Независимое воспроизведение обучения E02c (R-9, seed42).
# Версии — минимум для запуска; расхождение версий допустимо, но тогда
# побитового совпадения весов ждать нельзя (см. протокол).
torch>=2.6
numpy>=2.0
scipy>=1.11
tensorboard>=2.16
"""


class TrainReproError(RuntimeError):
    """Ошибка сборки: нет файла, рецепта или эталонного значения."""


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


def arm_recipe(morph_root: Path) -> dict:
    """Рецепт R-9 из `wp4_ablations.ARMS` — читается, а не переписывается.

    Импортировать `wp4_ablations` целиком нельзя: он тянет torch. Поэтому
    рецепт берётся из `ARMS["R-9"]` через AST, а если не выйдет — из зеркала в
    `census.json` (`checkpoints[].overrides`), которое писал сам прогон.
    """
    import ast

    path = morph_root / "wp4_ablations.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "ARMS" not in targets:
            continue
        try:
            arms = ast.literal_eval(node.value)
        except (ValueError, SyntaxError) as exc:  # pragma: no cover - защита от рефакторинга
            raise TrainReproError(f"не удалось прочитать ARMS из {path}: {exc}") from exc
        if "R-9" not in arms:
            raise TrainReproError("в ARMS нет плеча R-9 — рецепт изменился")
        description, overrides = arms["R-9"]
        return {"arm": "R-9", "description": description, "overrides": overrides}
    raise TrainReproError(f"в {path} не найден ARMS")


def reference_metrics(repo_root: Path, morph_root: Path) -> dict:
    """Эталон: канонический seed42 (журнал + индекс чекпоинтов + перепись).

    Только факты из файлов. Если чего-то нет — поле не выдумывается: сборка
    падает, потому что без эталона сравнение бессмысленно.
    """
    journal = morph_root / "logs" / "journal.jsonl"
    if not journal.is_file():
        raise TrainReproError(f"нет канонического журнала: {journal}")
    finish = None
    for line in journal.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("event") == "finish" and row.get("experiment") == "WP4_R-9_s2000_seed42":
            finish = row
    if finish is None:
        raise TrainReproError("в журнале нет finish для WP4_R-9_s2000_seed42")

    index = load_json(repo_root / "lab" / "checkpoints.json")
    entries = {
        item.get("family"): item
        for item in index.get("entries", [])
        if item.get("kind") == "final"
    }
    canonical = entries.get("WP4_R-9_s2000_seed42") or {}
    if not canonical.get("sha256"):
        raise TrainReproError("в lab/checkpoints.json нет sha256 для WP4_R-9_s2000_seed42")

    census_path = morph_root / "experiments" / "E02b_morphospace" / "census.json"
    census = load_json(census_path)
    rows = [r for r in census.get("runs", []) if r.get("family") == "WP4_R-9_s2000_seed42"]
    if not rows:
        raise TrainReproError("в census.json нет прогонов WP4_R-9_s2000_seed42")
    struct2 = sum(1 for r in rows if r.get("class_name") == "struct_2")
    stable = sum(
        1
        for r in rows
        if r.get("class_name") == "struct_2"
        and float(r.get("stability_last_quarter") or 0.0) >= 0.80
    )
    return {
        "canonical_family": "WP4_R-9_s2000_seed42",
        "checkpoint_sha256": canonical.get("sha256"),
        "checkpoint_bytes": canonical.get("size_bytes"),
        "training": {
            "best_loss": finish.get("best_loss"),
            "alive_fraction_final": finish.get("alive_fraction_final"),
            "iterations_done": finish.get("iterations_done"),
            "wall_time_sec": finish.get("wall_time_sec"),
            "stop_reason": finish.get("stop_reason"),
        },
        "census": {
            "n_starts": len(rows),
            "struct_2": struct2,
            "struct_2_stable": stable,
            "stability_fraction": round(stable / len(rows), 4) if rows else 0.0,
        },
        "criterion": {
            "what": "Класс воспроизведён, если struct_2 >= 52/64 и устойчивость >= 0.80 (протокол E02c_seed42_repro).",
            "bitwise_weights": "Не требуется на другом стеке; побитовое совпадение — отдельное наблюдение, а не критерий.",
        },
    }


def build_manifest(staging: Path, *, families: list[str], reference: dict, recipe: dict,
                   source: dict, environment: dict) -> dict:
    files = []
    for path in sorted(p for p in staging.rglob("*") if p.is_file()):
        rel = path.relative_to(staging).as_posix()
        if rel == MANIFEST_NAME:
            continue
        files.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "schema_version": 1,
        "kind": "train_repro_package",
        "created_at": utc_now(),
        "source": source,
        "package": {
            "families": families,
            "n_files": len(files) + 1,
            "total_bytes": sum(item["size_bytes"] for item in files),
            "recipe": recipe,
        },
        "reference": reference,
        "files": files,
        "environment": environment,
        "notes": [
            "исходники скопированы байт-в-байт; пакет не меняет ни код, ни рецепт",
            "эталон — канонический WP4_R-9_s2000_seed42: его finish-строка, sha256 и перепись",
            "критерий независимого воспроизведения — класс (52/64 и 0.80), не побитовое равенство весов",
            "пакет собран из публичного репозитория; в git он не едет (dist/ в .gitignore)",
        ],
    }


def environment_info() -> dict:
    import numpy
    import scipy
    import torch

    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "cuda": torch.version.cuda,
        "platform": sys.platform,
    }


def _readme(preview: dict) -> str:
    ref = preview["reference"]
    pkg = preview["package"]
    return f"""# E02c train-repro package — независимое воспроизведение обучения

Собран из коммита `{preview['source']['git_commit_short']}` (dirty: {preview['source']['git_dirty']}).
Рецепт: `{pkg['recipe']['arm']}` — {pkg['recipe']['description']}

## Что внутри

| Что | Зачем |
| --- | --- |
| `config.py`, `train.py`, `nca_core.py`, `evaluate.py`, `target_patterns.py`, `topo_proxy.py`, `topology.py`, `utils/` | код обучения, байт-в-байт из репозитория |
| `wp4_ablations.py` | рецепт `ARMS["R-9"]` (overrides применяются обёрткой) |
| `e02c_replication.py` | обёртка: один сид, отдельный каталог чекпоинтов |
| `e02c_census.py`, `e02b_morphospace.py` | перепись того же чекпоинта тем же кодом |
| `experiments/E02b_morphospace/class_centroids_frozen.json` | замороженные центроиды E02b (k=5) |
| `experiments/E02b_morphospace/census.json` | каноническая перепись: источник центроидов и эталон классов |
| `reference.json` | эталонные значения канонического прогона (loss, alive, sha256, перепись) |

## Запуск

```bash
python -m pip install -r requirements-train.txt
# 1) обучение: тот же сид, тот же рецепт, 2000 шагов
python e02c_replication.py --seed 42 --steps 2000
# 2) перепись этого чекпоинта: 64 старта x 2000 шагов
python e02c_census.py --families E02c_R-9_s2000_seed42 \\
  --out experiments/E02c_replication/census_e02c_seed42repro.json \\
  --summary-out experiments/E02c_replication/summary_e02c_seed42repro.json
```

Обучение пишет `checkpoints/E02c_R-9_s2000_seed42/nca_final.pt` и пару
`start`/`finish` в `logs/journal.jsonl`; перепись пишет сводку и тоже пару
`start`/`finish`.

## Критерий (записан до запуска)

- **reproduced:** `struct_2` не менее чем в **52/64** стартов и
  устойчивость последней четверти **>= 0.80**.
- **not reproduced:** меньше 52/64. Класс, в который ушёл прогон, фиксируется как
  есть; порог не двигается и повторов «до успеха» не будет.
- Побитовое совпадение весов **не** требуется: на другом стеке порядок операций
  и версии torch другие. Если веса всё же совпадут — это отдельное наблюдение.

Эталон локального прогона: `{ref['canonical_family']}`, `best_loss` =
`{ref['training']['best_loss']}`, `alive_fraction_final` =
`{ref['training']['alive_fraction_final']}`, sha256 =
`{ref['checkpoint_sha256']}`, перепись `struct_2` {ref['census']['struct_2']}/
{ref['census']['n_starts']} (устойчивость {ref['census']['stability_fraction']}).

## Что этот запуск не доказывает

Не доказывает, что класс — свойство рецепта R-9: это проверено в E02c (0/3).
Не доказывает уникальность seed42. Не даёт права говорить «жизнь», «сознание»,
«интеллект»; допустимая рамка — наблюдаемый класс поведения и его границы.
"""


def export(out: Path, *, repo_root: Path = REPO_ROOT, keep_tmp: bool = False) -> dict:
    out = Path(out)
    morph_root = Path(repo_root) / "morphogenesis"
    staging = out.with_name(out.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    missing = [
        str(path)
        for path in (
            *[morph_root / name for name in SOURCE_FILES],
            *[morph_root / "utils" / name for name in UTILS_FILES],
            *[morph_root / rel for rel, _ in DATA_FILES],
        )
        if not path.is_file()
    ]
    if missing:
        raise TrainReproError("нет файлов для пакета: " + ", ".join(missing))

    try:
        for name in SOURCE_FILES:
            shutil.copy2(morph_root / name, staging / name)
        (staging / "utils").mkdir(parents=True, exist_ok=True)
        for name in UTILS_FILES:
            shutil.copy2(morph_root / "utils" / name, staging / "utils" / name)
        for rel, dest in DATA_FILES:
            target = staging / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(morph_root / rel, target)

        recipe = arm_recipe(morph_root)
        reference = reference_metrics(repo_root, morph_root)
        source = {
            **git_info(repo_root),
            "repo": "project-morphogenesis",
            "exported_at": utc_now(),
            "exporter": "scripts/export_train_repro.py",
        }
        (staging / "README.md").write_text(
            _readme({"source": source, "package": {"recipe": recipe}, "reference": reference}),
            encoding="utf-8",
            newline="\n",
        )
        (staging / "requirements-train.txt").write_text(REQUIREMENTS_TEXT, encoding="utf-8", newline="\n")
        write_json(staging / "reference.json", reference)

        manifest = build_manifest(
            staging,
            families=["E02c_R-9_s2000_seed42"],
            reference=reference,
            recipe=recipe,
            source=source,
            environment=environment_info(),
        )
        write_json(staging / MANIFEST_NAME, manifest)

        if out.exists():
            if not (out / MANIFEST_NAME).is_file() and any(out.iterdir()):
                raise TrainReproError(
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
    parser.add_argument("--out", default="dist/e02c-train-repro", help="каталог пакета")
    parser.add_argument("--keep-tmp", action="store_true", help="не удалять staging при ошибке")
    args = parser.parse_args(argv)
    try:
        manifest = export(Path(args.out), keep_tmp=bool(args.keep_tmp))
    except TrainReproError as exc:
        print(f"[train-repro] ОШИБКА: {exc}", file=sys.stderr)
        return 2
    print(
        f"[train-repro] готово: {args.out} "
        f"({manifest['package']['n_files']} файлов, {manifest['package']['total_bytes'] / 1e6:.1f} МБ)"
    )
    print(f"[train-repro] эталон: best_loss={manifest['reference']['training']['best_loss']}, "
          f"struct_2={manifest['reference']['census']['struct_2']}/{manifest['reference']['census']['n_starts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
