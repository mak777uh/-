"""test_census_include_families.py — reference-семейства в переписи E02c.

Зачем: на чужом железе (Colab) основная задача — проверить перенос известных
сидов (`WP4_*`), а не репликация E02c. `discover_specs` берёт такие семейства
через `include_families` с `arm="REF"`:

- они считаются тем же кодом и той же замороженной проекцией;
- **не** попадают в список, по которому считается вердикт H-R1/R2/R3;
- E02c-имена через include не дублируются (их берёт `--families`), и загрузчик
  для них не вызывается.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
CENSUS_PY = MORPH / "e02c_census.py"

if str(MORPH) not in sys.path:
    sys.path.insert(0, str(MORPH))


def load_module():
    spec = importlib.util.spec_from_file_location("e02c_census_include", CENSUS_PY)
    assert spec and spec.loader, f"не удалось загрузить {CENSUS_PY}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def census(tmp_path, monkeypatch):
    module = load_module()
    root = tmp_path / "checkpoints"
    fam = root / "E02c_R-9_s2000_seed7"
    fam.mkdir(parents=True)
    (fam / "nca_final.pt").write_bytes(b"fake")
    monkeypatch.setattr(module, "CHECKPOINT_ROOT", str(root))
    monkeypatch.setattr(module, "sha256_file", lambda path: "b" * 64)
    return module


def fake_spec(module, family, seed):
    return module.e02b.CheckpointSpec(
        id=family,
        arm="R-9",
        family=family,
        path=f"/fake/{family}/nca_final.pt",
        seed=seed,
        steps_trained=2000,
        sha256="0" * 64,
        alive_mask_enabled=True,
        overrides={},
        overrides_source="test",
        kind="final",
        note="test",
    )


def patch_loader(module, monkeypatch, calls=None):
    def fake_load(families=None, include_untrained=False):
        name = (families or [None])[0]
        if calls is not None:
            calls.append(name)
        # контроль seed42 и reference seed101 «есть», прочие — нет
        if name in ("WP4_R-9_s2000_seed42", "WP4_R-9_s2000_seed101"):
            seed = 42 if name.endswith("seed42") else 101
            return [fake_spec(module, name, seed)]
        raise SystemExit(f"нет чекпоинта {name}")

    monkeypatch.setattr(module.e02b, "load_checkpoint_specs", fake_load)


def test_reference_families_get_ref_arm(census, monkeypatch):
    patch_loader(census, monkeypatch)
    specs = census.discover_specs(
        families=["E02c_R-9_s2000_seed7"],
        include_families=["WP4_R-9_s2000_seed101"],
    )
    arms = {s.family: s.arm for s in specs}
    assert arms["E02c_R-9_s2000_seed7"] == "R-9"
    assert arms["WP4_R-9_s2000_seed101"] == "REF"
    assert arms["WP4_R-9_s2000_seed42"] == "H-P1"
    assert arms["untrained_current_arch"] == "untrained"


def test_e02c_family_is_not_duplicated_via_include(census, monkeypatch):
    calls = []
    patch_loader(census, monkeypatch, calls)
    specs = census.discover_specs(
        families=["E02c_R-9_s2000_seed7"],
        include_families=["E02c_R-9_s2000_seed7"],
    )
    assert [s.family for s in specs if s.arm == "REF"] == []
    assert "E02c_R-9_s2000_seed7" not in calls, "E02c-имя не должно идти в загрузчик"
    assert len([s for s in specs if s.family == "E02c_R-9_s2000_seed7"]) == 1


def test_missing_reference_family_is_skipped(census, monkeypatch):
    patch_loader(census, monkeypatch)
    specs = census.discover_specs(
        families=["E02c_R-9_s2000_seed7"],
        include_families=["WP4_R-9_s2000_seed142"],
    )
    assert [s.family for s in specs if s.arm == "REF"] == []
    assert any(s.family == "E02c_R-9_s2000_seed7" for s in specs)


def test_reference_does_not_enter_verdict_families(census, monkeypatch):
    patch_loader(census, monkeypatch)
    specs = census.discover_specs(
        families=["E02c_R-9_s2000_seed7"],
        include_families=["WP4_R-9_s2000_seed101"],
    )
    verdict_families = [s.family for s in specs if s.arm == "R-9"]
    assert verdict_families == ["E02c_R-9_s2000_seed7"]
    verdict, applicable = census.census_verdict([], len(verdict_families))
    assert verdict == "n/a_partial_census"
    assert applicable is False


def test_missing_control_requires_flag(census, monkeypatch):
    def no_control(families=None, include_untrained=False):
        raise SystemExit("нет контроля")

    monkeypatch.setattr(census.e02b, "load_checkpoint_specs", no_control)
    with pytest.raises(SystemExit):
        census.discover_specs(families=["E02c_R-9_s2000_seed7"])
    specs = census.discover_specs(
        families=["E02c_R-9_s2000_seed7"], allow_missing_control=True
    )
    assert [s.arm for s in specs] == ["R-9", "untrained"]
