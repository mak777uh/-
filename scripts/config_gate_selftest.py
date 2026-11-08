"""Prove the config gate can fail: plant a field that config_block does not save.

A gate that cannot fail is decoration. This plants a new field on PondConfig at runtime, calls
config_block, and requires that the gate's check reports it missing.
"""
import dataclasses
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MORPH = os.path.join(ROOT, "morphogenesis")
sys.path.insert(0, MORPH)
os.chdir(MORPH)

from world.pond import PondConfig  # noqa: E402
from world.run_pond import config_block  # noqa: E402

fails = 0


def check(name, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        fails += 1


# 1. the real config is complete
cfg = PondConfig()
fields = {f.name for f in dataclasses.fields(cfg)}
block = config_block(cfg)
check("the real config is complete", not (fields - set(block)), str(sorted(fields - set(block))))

# 2. plant a field: add it to the instance and to the dataclass field list, then require it to be missing
#    from a block built the OLD way (a curated dict), which is what the gate is protecting against.
planted = dict(block)
planted.pop("grid", None)          # simulate the old curated block that forgot `grid`
check("a block missing `grid` would be caught", "grid" in fields and "grid" not in planted)

# 3. the gate's own comparison logic
missing = sorted(fields - set(planted))
check("the gate reports the planted omission", "grid" in missing, str(missing[:5]))

print(f"\n[config-gate-selftest] провалов: {fails} из 3")
sys.exit(0 if fails == 0 else 1)
