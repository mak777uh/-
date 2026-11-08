"""Gate: the artifact must be able to reconstruct the world.

Why. On 08.11 a static review found that `config_block()` saved 37 of the 133 fields of `PondConfig`, and
that the missing ones included `grid`, `budding_cost`, `budding_mass`, `damage_rate` and `income_mode` —
the parameters that DEFINE the world. An artifact that cannot say which world it came from is not an
artifact; it is a picture.

The gate compares the fields of `PondConfig` with the keys of `config_block(PondConfig())` and fails if any
field is missing. It also fails if the block is not JSON-serialisable, because a block that cannot be
written is not saved.

Usage:
  cd morphogenesis && python ../scripts/check_config_completeness.py
  python scripts/check_config_completeness.py          # from the repository root
"""
from __future__ import annotations
import dataclasses
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MORPH = os.path.join(ROOT, "morphogenesis")


def main() -> int:
    sys.path.insert(0, MORPH)
    cwd = os.getcwd()
    try:
        os.chdir(MORPH)          # run_pond imports `config` relatively, as the project expects
        from world.pond import PondConfig  # noqa: E402
        from world.run_pond import config_block  # noqa: E402

        cfg = PondConfig()
        fields = {f.name for f in dataclasses.fields(cfg)}
        block = config_block(cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"[config] не удалось прочитать конфиг: {exc}")
        return 1
    finally:
        os.chdir(cwd)

    missing = sorted(fields - set(block))
    if missing:
        for m in missing:
            print(f"  ПРОВАЛ: поле {m} не попадает в summary.config")
        print(f"[config] проблем: {len(missing)} из {len(fields)} полей")
        return 1

    try:
        json.dumps(block)
    except TypeError as exc:
        print(f"[config] ПРОВАЛ: блок не сериализуется в JSON: {exc}")
        return 1

    print(f"[config] ok: {len(fields)} полей, все в summary.config, JSON-сериализуемо")
    return 0


if __name__ == "__main__":
    sys.exit(main())
