"""test_verify_portable_package.py — проверка целостности портативного пакета.

`scripts/verify_portable_package.py` — это то, чем читатель проверяет
`dist/e02b-portable`, не доверяя тексту рукописи. Тест держит его честным:

- совпадающий пакет проходит (0 ошибок);
- подменённый байт в payload — ошибка, а не «файл на месте»;
- отсутствующий файл и лишний файл различаются (ошибка против предупреждения);
- абсолютный путь автора в текстовом файле — ошибка;
- в бинарных `.pt` шаблон путей не сканируется: случайные байты не должны
  превращаться в ложную ошибку;
- расхождение `datasets.census.source_sha256` с каноническим census — ошибка.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_portable_package.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_portable_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_package(tmp_path: Path, module, *, payload: bytes = b"census-payload") -> Path:
    pkg = tmp_path / "pkg"
    (pkg / "morphogenesis" / "experiments").mkdir(parents=True)
    readme = b"# portable package\n"  # байтами: на Windows текстовый режим меняет \n на \r\n
    (pkg / "README.md").write_bytes(readme)
    census = pkg / "morphogenesis" / "experiments" / "census.json"
    census.write_bytes(payload)
    (pkg / "morphogenesis" / "checkpoints").mkdir(parents=True)
    weights = pkg / "morphogenesis" / "checkpoints" / "lite.pt"
    weights.write_bytes(b"\x00C:\\Users\\author\\path\x00")  # бинарь с «путём» внутри

    canon = tmp_path / "canonical_census.json"
    canon.write_bytes(b"canonical")

    manifest = {
        "schema_version": 1,
        "kind": "portable_inference_package",
        "datasets": {
            "census": {
                "path": "morphogenesis/experiments/census.json",
                "sha256": sha(payload),
                "source_sha256": sha(b"canonical"),
            }
        },
        "files": [
            {"path": "README.md", "bytes": len(readme), "sha256": sha(readme)},
            {"path": "morphogenesis/experiments/census.json", "bytes": len(payload), "sha256": sha(payload)},
            {"path": "morphogenesis/checkpoints/lite.pt", "bytes": weights.stat().st_size, "sha256": sha(weights.read_bytes())},
        ],
    }
    (pkg / "portable_manifest.json").write_bytes(json.dumps(manifest).encode("utf-8"))

    module.PKG = pkg
    module.CANON_CENSUS = canon
    return pkg


def test_clean_package_passes(tmp_path, monkeypatch, capsys):
    module = load_module()
    build_package(tmp_path, module)
    assert module.main() == 0
    out = capsys.readouterr().out
    assert "ИТОГ: 0 ошибок, 0 предупреждений" in out
    assert "бинарные не сканируются: 1" in out


def test_tampered_payload_is_an_error(tmp_path, capsys):
    module = load_module()
    pkg = build_package(tmp_path, module)
    (pkg / "morphogenesis" / "experiments" / "census.json").write_bytes(b"changed")
    assert module.main() == 1
    assert "sha256 не совпал" in capsys.readouterr().out


def test_missing_file_is_an_error(tmp_path, capsys):
    module = load_module()
    pkg = build_package(tmp_path, module)
    (pkg / "README.md").unlink()
    assert module.main() == 1
    assert "нет файла: README.md" in capsys.readouterr().out


def test_extra_file_is_a_warning(tmp_path, capsys):
    module = load_module()
    pkg = build_package(tmp_path, module)
    (pkg / "stray.txt").write_text("лишний", encoding="utf-8")
    assert module.main() == 0
    out = capsys.readouterr().out
    assert "файлы вне манифеста" in out and "stray.txt" in out


def test_absolute_path_in_text_file_is_an_error(tmp_path, capsys):
    module = load_module()
    pkg = build_package(tmp_path, module)
    (pkg / "README.md").write_bytes(b"see C:\\Users\\author\\repo\n")
    assert module.main() == 1
    assert "абсолютные пути остались в: ['README.md']" in capsys.readouterr().out


def test_canonical_census_mismatch_is_an_error(tmp_path, capsys):
    module = load_module()
    build_package(tmp_path, module)
    (tmp_path / "canonical_census.json").write_bytes(b"rewritten!")
    assert module.main() == 1
    assert "source_sha256 канонического census не совпал" in capsys.readouterr().out
