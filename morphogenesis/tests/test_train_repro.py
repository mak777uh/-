"""test_train_repro.py — контракт пакета независимого воспроизведения обучения.

Пакет нужен для Gate 3: прогнать обучение E02c на другом стеке и сравнить класс,
а не байты. Ошибки, которые тут ловятся:

1. в пакет не попал модуль из импортов `train.py` (тогда он не запустится на
   чужой машине, а локально всё «работает»);
2. эталонные значения выдуманы или устарели (сравнение станет бессмысленным);
3. рецепт `ARMS["R-9"]` прочитан неправильно (другой протокол под тем же именем);
4. манифест не совпадает с файлами пакета (нельзя проверить целостность).

Ни обучения, ни GPU: тесты читают репозиторий и собранный `dist/` (если он есть).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
EXPORT_PY = ROOT / "scripts" / "export_train_repro.py"
DIST = ROOT / "dist" / "e02c-train-repro"

if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load_exporter():
    spec = importlib.util.spec_from_file_location("export_train_repro_module", EXPORT_PY)
    assert spec and spec.loader, f"не удалось загрузить {EXPORT_PY}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load_exporter()


def imports_of(path: Path) -> set[str]:
    """Локальные модули, которые импортирует файл (первый уровень)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def local_modules() -> set[str]:
    return {path.stem for path in MORPH.glob("*.py")}


class TestBundleContents:
    def test_train_dependencies_are_covered(self):
        """Каждый локальный импорт учебного контура обязан быть в пакете.

        Это защита от тихого расширения зависимостей: новый модуль в импортах
        `train.py` или `e02c_replication.py` без правки `SOURCE_FILES` уронит
        тест, а не чужой запуск.
        """
        included = set(exporter.SOURCE_FILES)
        available = local_modules()
        for entry in ("train.py", "e02c_replication.py", "e02c_census.py", "e02b_morphospace.py"):
            for name in imports_of(MORPH / entry):
                if name in available:
                    assert f"{name}.py" in included, f"{entry} импортирует {name}, а его нет в пакете"

    def test_utils_files_exist(self):
        for name in exporter.UTILS_FILES:
            assert (MORPH / "utils" / name).is_file(), name

    def test_data_files_exist(self):
        for rel, _dest in exporter.DATA_FILES:
            assert (MORPH / rel).is_file(), rel


class TestRecipe:
    def test_arm_recipe_matches_source(self):
        recipe = exporter.arm_recipe(MORPH)
        assert recipe["arm"] == "R-9"
        assert recipe["description"]
        overrides = recipe["overrides"]
        assert overrides["RETENTION_SURVIVAL_WEIGHT"] == 10.0
        assert overrides["RETENTION_SURVIVAL_MODE"] == "level"
        assert overrides["LOSS_WEIGHTS"]["retention"] == 1.0
        assert overrides["LOSS_WEIGHTS"]["alive_policy"] == 2.0
        assert overrides["TRAIN_BPTT_CURRICULUM"] == [16, 16, 16]


class TestReference:
    def test_reference_comes_from_artifacts(self):
        ref = exporter.reference_metrics(ROOT, MORPH)
        assert ref["canonical_family"] == "WP4_R-9_s2000_seed42"
        assert len(ref["checkpoint_sha256"]) == 64
        assert ref["training"]["iterations_done"] == 2000
        assert ref["training"]["stop_reason"] == "max_steps"
        # loss и alive — из finish-строки журнала, а не «примерно»
        assert abs(ref["training"]["best_loss"] - 1.104736089706421) < 1e-12
        assert abs(ref["training"]["alive_fraction_final"] - 0.34686279296875) < 1e-12
        assert ref["census"]["struct_2"] == 64
        assert ref["census"]["n_starts"] == 64
        assert 0.0 <= ref["census"]["stability_fraction"] <= 1.0

    def test_reference_is_not_silently_missing(self):
        """Если эталон пропал, сборка падает, а не собирает пакет без сравнения."""
        with pytest.raises(exporter.TrainReproError):
            exporter.reference_metrics(ROOT, MORPH / "nope")


@pytest.mark.skipif(
    not (DIST / exporter.MANIFEST_NAME).is_file(),
    reason="dist/e02c-train-repro не собран — проверка целостности пакета пропущена",
)
class TestBuiltBundle:
    def test_manifest_lists_every_file_with_hash(self):
        manifest = json.loads((DIST / exporter.MANIFEST_NAME).read_text(encoding="utf-8"))
        listed = {item["path"]: item for item in manifest["files"]}
        on_disk = {
            path.relative_to(DIST).as_posix()
            for path in DIST.rglob("*")
            if path.is_file() and path.name != exporter.MANIFEST_NAME and "__pycache__" not in path.parts
        }
        assert set(listed) == on_disk
        for rel, info in listed.items():
            assert (DIST / rel).stat().st_size == info["size_bytes"], rel
            assert exporter.sha256_file(DIST / rel) == info["sha256"], rel

    def test_bundle_has_expected_entrypoints(self):
        for name in ("train.py", "e02c_replication.py", "e02c_census.py", "README.md",
                     "requirements-train.txt", "reference.json"):
            assert (DIST / name).is_file(), name
        assert (DIST / "experiments" / "E02b_morphospace" / "class_centroids_frozen.json").is_file()

    def test_readme_states_the_criterion(self):
        text = (DIST / "README.md").read_text(encoding="utf-8")
        assert "52/64" in text
        assert "0.80" in text
        assert "не доказывает" in text.lower() or "не доказывает" in text
