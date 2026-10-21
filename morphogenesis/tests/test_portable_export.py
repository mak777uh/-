"""test_portable_export.py — контракт portable inference-пакета E02b.

Что проверяем (и что легко сделать неправильно):

1. lite-чекпоинт содержит ТОЛЬКО `model_state_dict` + скаляры + metadata:
   optimizer/scheduler/pool/state не должны просочиться, иначе «lite» весит
   как полный файл;
2. forward lite-модели побитово равен forward полной модели на CPU — иначе
   пакет не воспроизводит census, а просто «похож»;
3. metadata проверяется, а не принимается на веру: чужая spec_version или
   grid_size — отказ (§13.5 нельзя смешивать веса разных ревизий);
4. `portable_manifest.json` перечисляет каждый файл пакета со sha256;
5. индекс пакета описывает lite-файлы (полный sha256 — только в манифесте).

Интеграционные тесты с реальным 539-МБ чекпоинтом и с собранным `dist/`
помечены skipif: на чистом клоне (без весов и без сборки) они пропускаются,
а не падают. CWD фиксирует conftest.py (morphogenesis/).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))

import config  # noqa: E402  (§9.2: config раньше torch)
from nca_core import NeuralCellularAutomaton, init_state  # noqa: E402

EXPORT_PY = ROOT / "scripts" / "export_portable.py"
REAL_CHECKPOINT = (
    ROOT / "morphogenesis" / "checkpoints" / "WP4_R-9_s2000_seed42" / "nca_final.pt"
)
INDEX_PATH = ROOT / "lab" / "checkpoints.json"


def canonical_families() -> list[str]:
    """Семейства E02b, для которых канонический nca_final.pt реально лежит на диске."""
    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    families = []
    items = index.get("requirements", {}).get("E02b_morphospace", {}).get("items", [])
    for item in items:
        family = item.get("family")
        if family and (ROOT / item.get("path", "")).is_file():
            families.append(family)
    return families


REAL_FAMILIES = canonical_families()
DIST = ROOT / "dist" / "e02b-portable"
# Манифест не описывает сам себя, а отчёты проверки и __pycache__ появляются
# после сборки — это след запуска, а не содержимое пакета.
GENERATED = {"verify_report.json", "verify_census.json", "portable_manifest.json"}


def load_exporter():
    spec = importlib.util.spec_from_file_location("export_portable_module", EXPORT_PY)
    assert spec and spec.loader, f"не удалось загрузить {EXPORT_PY}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load_exporter()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def full_checkpoint_like(seed: int = 7, iteration: int = 3) -> dict:
    """Полный чекпоинт в миниатюре: те же ключи, но пул/state — заглушки."""
    model = NeuralCellularAutomaton(channels=config.N_CHANNELS)
    return {
        "iteration": iteration,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": {"state": {}, "param_groups": [{"lr": 1e-3}]},
        "scheduler_state_dict": {"last_epoch": iteration},
        "pool_state_dict": {
            "states": torch.zeros(2, config.N_CHANNELS, 4, 4),
            "ages": torch.zeros(2),
        },
        "state": torch.zeros(1, config.N_CHANNELS, 4, 4),
        "loss": 0.5,
        "seed": seed,
        "grid_size": config.GRID_SIZE,
        "n_channels": config.N_CHANNELS,
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "stress_enabled": True,
        "stress_channel": config.STRESS_CHANNEL,
        "metadata": config.get_checkpoint_metadata(
            seed=seed, experiment_id="TEST_ONLY", iteration=iteration
        ),
    }


def model_from_state(state_dict: dict) -> NeuralCellularAutomaton:
    model = NeuralCellularAutomaton(channels=config.N_CHANNELS)
    model.load_state_dict(state_dict)
    model.alive_mask_enabled = True
    model.eval()
    return model


def rollout(model: NeuralCellularAutomaton, steps: int = 12, seed: int = 11) -> torch.Tensor:
    """Детерминированная развёртка на CPU: тот же протокол, что в e02b.run_seed."""
    generator = config.create_deterministic_generator(seed)
    model.set_generator(generator)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = init_state(
        batch_size=1,
        channels=config.N_CHANNELS,
        grid_size=config.GRID_SIZE,
        device=torch.device("cpu"),
        generator=generator,
    )
    with torch.no_grad():
        for _ in range(int(steps)):
            state = model(state)
    return state


class TestLiteContract:
    def test_lite_has_only_allowed_keys(self):
        ck = full_checkpoint_like()
        lite = exporter.make_lite_checkpoint(ck)
        assert set(lite) == set(exporter.LITE_KEYS)
        assert not set(lite) & set(exporter.FORBIDDEN_LITE_KEYS)
        assert lite["metadata"] == ck["metadata"]
        assert lite["seed"] == 7
        assert lite["iteration"] == 3
        assert lite["spec_version"] == config.SPEC_VERSION
        assert lite["stress_channel"] == config.STRESS_CHANNEL

    def test_lite_saves_small_and_roundtrips(self, tmp_path):
        ck = full_checkpoint_like()
        lite = exporter.make_lite_checkpoint(ck)
        path = tmp_path / "lite.pt"
        size = exporter.save_lite_checkpoint(lite, path)
        assert size == path.stat().st_size
        # Полный файл — сотни МБ; lite обязан быть на три порядка меньше.
        assert size < 1_000_000
        exporter.verify_lite_roundtrip(lite, path, "TEST_ONLY")
        reloaded = torch.load(str(path), map_location="cpu", weights_only=False)
        assert set(reloaded) == set(exporter.LITE_KEYS)
        assert reloaded["metadata"]["spec_version"] == config.SPEC_VERSION

    def test_lite_forward_is_bitwise_equal_on_cpu(self, tmp_path):
        ck = full_checkpoint_like()
        lite = exporter.make_lite_checkpoint(ck)
        path = tmp_path / "lite.pt"
        exporter.save_lite_checkpoint(lite, path)

        full_model = model_from_state(ck["model_state_dict"])
        lite_model = model_from_state(
            torch.load(str(path), map_location="cpu", weights_only=False)["model_state_dict"]
        )
        state_full = rollout(full_model)
        state_lite = rollout(lite_model)
        assert torch.equal(state_full, state_lite)
        assert float((state_full - state_lite).abs().max()) == 0.0


class TestValidation:
    def test_rejects_incompatible_spec_version(self):
        ck = full_checkpoint_like()
        ck["metadata"] = dict(ck["metadata"], spec_version="v5.5-EXP FINAL")
        with pytest.raises(exporter.PortableExportError, match="несовместимая версия"):
            exporter.validate_full_checkpoint(ck, "TEST_ONLY")

    def test_rejects_wrong_grid_size(self):
        ck = full_checkpoint_like()
        ck["metadata"] = dict(ck["metadata"], grid_size=config.GRID_SIZE // 2)
        with pytest.raises(exporter.PortableExportError, match="grid_size"):
            exporter.validate_full_checkpoint(ck, "TEST_ONLY")

    def test_rejects_missing_model_state(self):
        ck = full_checkpoint_like()
        ck.pop("model_state_dict")
        with pytest.raises(exporter.PortableExportError, match="model_state_dict"):
            exporter.validate_full_checkpoint(ck, "TEST_ONLY")

    def test_rejects_missing_metadata(self):
        ck = full_checkpoint_like()
        ck["metadata"] = {}
        with pytest.raises(exporter.PortableExportError, match="metadata"):
            exporter.validate_full_checkpoint(ck, "TEST_ONLY")


class TestManifestAndIndex:
    def test_manifest_lists_every_file(self, tmp_path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
        (tmp_path / "sub" / "b.bin").write_bytes(b"\x00\x01\x02")
        manifest = exporter.build_manifest(
            tmp_path,
            families=["F1"],
            partial=False,
            omitted=[],
            checkpoints={},
            datasets={},
            source={"git_commit": "deadbeef"},
            environment={"python": "test"},
        )
        paths = [item["path"] for item in manifest["files"]]
        assert paths == ["a.txt", "sub/b.bin"]
        assert manifest["files"][0]["sha256"] == sha256(tmp_path / "a.txt")
        assert manifest["files"][1]["size_bytes"] == 3
        assert manifest["package"]["n_files"] == len(paths) + 1
        assert manifest["package"]["total_bytes"] == sum(
            item["size_bytes"] for item in manifest["files"]
        )
        assert "portable_manifest.json" not in paths
        assert manifest["source"]["git_commit"] == "deadbeef"
        assert manifest["package"]["families"] == ["F1"]

    def test_index_describes_lite_files(self):
        index = {
            "entries": [
                {
                    "family": "F1",
                    "path": "morphogenesis/checkpoints/F1/nca_final.pt",
                    "sha256": "full-sha",
                    "size_bytes": 539495742,
                    "kind": "final",
                },
                {
                    "family": "F2",
                    "path": "morphogenesis/checkpoints/F2/nca_final.pt",
                    "sha256": "full-sha-2",
                    "size_bytes": 539495742,
                    "kind": "final",
                },
            ],
            "requirements": {
                exporter.EXPERIMENT_ID: {
                    "required": 2,
                    "ready": 2,
                    "missing": [],
                    "items": [{"family": "F1"}, {"family": "F2"}],
                }
            },
        }
        lite = {
            "F1": {"sha256": "lite-sha", "size_bytes": 152602},
            "F2": {"sha256": "lite-sha-2", "size_bytes": 152602},
        }
        portable = exporter.portable_index(index, lite, ["F1", "F2"])
        for entry in portable["entries"]:
            assert entry["sha256"] == f"lite-sha{'-2' if entry['family'] == 'F2' else ''}"
            assert entry["size_bytes"] == 152602
            assert "full-sha" not in entry["sha256"]
        requirement = portable["requirements"][exporter.EXPERIMENT_ID]
        assert requirement["required"] == requirement["ready"] == 2
        assert portable["portable"]["kind"] == "lite"
        # Исходный индекс не мутирует: пакет — копия, а не правка канона.
        assert index["entries"][0]["sha256"] == "full-sha"

    def test_descriptor_is_narrowed_to_exported_families(self):
        descriptor = {
            "checkpoint_requirements": [
                {"family": "F1", "file": "nca_final.pt"},
                {"family": "F2", "file": "nca_final.pt"},
            ],
            "status": "closed",
        }
        narrowed = exporter.portable_descriptor(descriptor, ["F2"])
        assert [item["family"] for item in narrowed["checkpoint_requirements"]] == ["F2"]
        assert narrowed["status"] == "closed"
        assert descriptor["checkpoint_requirements"][0]["family"] == "F1"


class TestMissingFiles:
    def test_require_files_reports_all_missing(self, tmp_path):
        missing_a = tmp_path / "a.pt"
        missing_b = tmp_path / "nested" / "b.pt"
        with pytest.raises(exporter.PortableExportError) as excinfo:
            exporter.require_files([missing_a, missing_b])
        message = str(excinfo.value)
        assert str(missing_a) in message
        assert str(missing_b) in message

    def test_select_families_rejects_unknown(self):
        with pytest.raises(exporter.PortableExportError, match="вне требований"):
            exporter.select_families(["F1", "F2"], "F3")

    def test_select_families_marks_partial(self):
        assert exporter.select_families(["F1", "F2"], None) == (["F1", "F2"], False)
        assert exporter.select_families(["F1", "F2"], "F2") == (["F2"], True)


@pytest.mark.skipif(
    not REAL_CHECKPOINT.is_file(),
    reason="нет канонического nca_final.pt — интеграционный тест пропущен",
)
class TestRealCheckpoint:
    def test_real_lite_is_small_and_bitwise_equal(self, tmp_path):
        ck = exporter.load_full_checkpoint(REAL_CHECKPOINT)
        exporter.validate_full_checkpoint(ck, "WP4_R-9_s2000_seed42")
        lite = exporter.make_lite_checkpoint(ck)
        path = tmp_path / "nca_final.pt"
        size = exporter.save_lite_checkpoint(lite, path)
        assert size < 1_000_000
        assert set(lite) == set(exporter.LITE_KEYS)

        full_model = model_from_state(ck["model_state_dict"])
        lite_model = model_from_state(
            torch.load(str(path), map_location="cpu", weights_only=False)["model_state_dict"]
        )
        with torch.no_grad():
            assert torch.equal(rollout(full_model, steps=5), rollout(lite_model, steps=5))


@pytest.mark.skipif(
    len(REAL_FAMILIES) < 3,
    reason="меньше трёх канонических чекпоинтов — проверка архитектур пропущена",
)
class TestAllCanonicalCheckpoints:
    def test_every_family_has_bitwise_lite_forward(self, tmp_path):
        """Все семейства (12 на рабочей машине) дают побитово тот же forward.

        Одного семейства мало: H-A0, R-9, R-11 и H-P1 — разные плечи, и ошибка
        сериализации может проявиться только на части state_dict (например, на
        замороженных слоях или на stress-буфере).
        """
        checked: list[str] = []
        for family in REAL_FAMILIES:
            source = ROOT / "morphogenesis" / "checkpoints" / family / "nca_final.pt"
            ck = exporter.load_full_checkpoint(source)
            exporter.validate_full_checkpoint(ck, family)
            lite = exporter.make_lite_checkpoint(ck)
            path = tmp_path / f"{family}.pt"
            size = exporter.save_lite_checkpoint(lite, path)
            assert size < 1024**2, family
            assert set(lite) == set(exporter.LITE_KEYS)

            full_model = model_from_state(ck["model_state_dict"])
            lite_model = model_from_state(
                torch.load(str(path), map_location="cpu", weights_only=False)["model_state_dict"]
            )
            with torch.no_grad():
                state_full = rollout(full_model, steps=3)
                state_lite = rollout(lite_model, steps=3)
            assert torch.equal(state_full, state_lite), f"{family}: forward разошёлся"
            checked.append(family)
            del ck, lite, full_model, lite_model, state_full, state_lite

        assert len(checked) == len(REAL_FAMILIES)
        assert len({family.split("_s2000")[0] for family in checked}) >= 3


@pytest.mark.skipif(
    not (DIST / "portable_manifest.json").is_file(),
    reason="dist/e02b-portable не собран — интеграционный тест пакета пропущен",
)
class TestBuiltPackage:
    def test_manifest_matches_package_files(self):
        manifest = json.loads((DIST / "portable_manifest.json").read_text(encoding="utf-8"))
        assert manifest["package"]["partial"] is False
        assert len(manifest["package"]["families"]) == 12
        assert manifest["package"]["total_bytes"] <= 30 * 1024**2
        listed = {item["path"]: item for item in manifest["files"]}
        on_disk = {
            path.relative_to(DIST).as_posix()
            for path in DIST.rglob("*")
            if path.is_file()
            and path.name not in GENERATED
            and "__pycache__" not in path.parts
        }
        assert set(listed) == on_disk
        for rel, info in listed.items():
            assert (DIST / rel).stat().st_size == info["size_bytes"]
            assert sha256(DIST / rel) == info["sha256"], rel

    def test_lite_checkpoints_are_lite_and_index_is_consistent(self):
        manifest = json.loads((DIST / "portable_manifest.json").read_text(encoding="utf-8"))
        index = json.loads((DIST / "lab" / "checkpoints.json").read_text(encoding="utf-8"))
        by_family = {item["family"]: item for item in index["entries"]}
        assert set(by_family) == set(manifest["checkpoints"])
        for family, info in manifest["checkpoints"].items():
            lite_path = DIST / info["path"]
            assert lite_path.is_file()
            assert lite_path.stat().st_size == info["lite_bytes"]
            assert sha256(lite_path) == info["lite_sha256"]
            ck = torch.load(str(lite_path), map_location="cpu", weights_only=False)
            assert set(ck) == set(exporter.LITE_KEYS)
            assert not set(ck) & set(exporter.FORBIDDEN_LITE_KEYS)
            assert ck["metadata"]["spec_version"] == config.SPEC_VERSION
            # Индекс пакета обязан ссылаться на lite, а полный sha — только в манифесте.
            assert by_family[family]["sha256"] == info["lite_sha256"]
            assert by_family[family]["sha256"] != info["full_sha256"]
            assert len(info["full_sha256"]) == 64
            assert info["full_bytes"] > 500 * 1024**2
            assert info["lite_bytes"] < 1024**2

    def test_manifest_has_no_absolute_or_windows_paths(self):
        manifest = json.loads((DIST / "portable_manifest.json").read_text(encoding="utf-8"))
        paths = [item["path"] for item in manifest["files"]]
        paths += [info["path"] for info in manifest["checkpoints"].values()]
        paths += [info["path"] for info in manifest["datasets"].values()]
        for rel in paths:
            assert not rel.startswith("/"), rel
            assert "\\" not in rel, rel
            assert ":" not in rel.split("/")[0], rel

    def test_manifest_records_source_and_environment(self):
        manifest = json.loads((DIST / "portable_manifest.json").read_text(encoding="utf-8"))
        source = manifest["source"]
        assert source["exporter"] == "scripts/export_portable.py"
        assert source["exported_at"].endswith("Z")
        assert isinstance(source["git_dirty"], bool)
        assert len(source["git_commit"]) == 40
        environment = manifest["environment"]
        assert environment["python"] and environment["torch"]
        assert manifest["package"]["n_checkpoints"] == 12
        assert manifest["package"]["n_files"] == len(manifest["files"]) + 1

    def test_dataset_checksums_match_manifest(self):
        manifest = json.loads((DIST / "portable_manifest.json").read_text(encoding="utf-8"))
        datasets = manifest["datasets"]
        for key in ("census", "class_centroids_frozen", "wp4_ablations"):
            info = datasets[key]
            path = DIST / info["path"]
            assert path.is_file(), key
            assert sha256(path) == info["sha256"], key
        assert datasets["census"]["n_runs"] == 832
        assert datasets["class_centroids_frozen"]["k"] == 5
