"""World profiles: a named, versioned combination of config fields.

Why. `PondConfig` has 134 fields spanning five subsystems (resource 29, budget 18, reproduction 22,
behaviour 33, other 32). A run that names 134 numbers is not reproducible in practice: nobody can read it, and
two runs that differ in one field look identical in every summary. A profile is a NAME for a combination, with
a version, so an artifact can say `profile: pond-v2` and a reader can find the exact fields.

This does not replace `PondConfig`. It sits on top: `apply_profile(cfg, name)` sets the fields the profile
defines and leaves the rest at their defaults, and `profile_block(cfg, name)` records in the artifact which
profile was used and which fields it set.

The profiles below are the ones the bench has actually run. `pond-v1` is the world before 08.11 (a different
energy budget and death rule); `pond-v2` is the world after the model-integrity cycle. They are NOT
interchangeable and the artifact says which one ran.

Usage:
  from world.profiles import PROFILES, apply_profile, profile_block
"""
from __future__ import annotations

# Every profile is a dict of config fields. A field not named keeps the dataclass default, which is the
# behaviour of the old code, so a profile is a DELTA and never a full specification.
PROFILES: dict[str, dict] = {
    # the world after the model-integrity cycle of 08.11: budding conserves energy, age does not kill,
    # repair is charged only on a repair. The parameters are the ones under which the body stays alive for
    # 300 steps (scripts/world_alive_sweep.py: income 0.2, update 0.01, repair 0.005 -> 1024 alive).
    "pond-v2-alive": {
        "grid": 32,
        "resource_regen": 0.05,
        "baseline_income": 0.2,
        "income_mode": "proportional",
        "update_cost": 0.01,
        "repair_cost": 0.005,
        "damage_rate": 0.02,
        "init_resource_fill": 1.0,
        "resource_max": 1.0,
        "budding_mass": 8,
        "noise": 0.0,
        "boundary": "absorbing",
    },
    # the same world with the record switched on, for the K-readouts
    "pond-v2-record": {
        "grid": 32,
        "resource_regen": 0.05,
        "baseline_income": 0.2,
        "income_mode": "proportional",
        "update_cost": 0.01,
        "repair_cost": 0.005,
        "damage_rate": 0.02,
        "init_resource_fill": 1.0,
        "resource_max": 1.0,
        "budding_mass": 8,
        "noise": 0.0,
        "boundary": "absorbing",
        "plastic_eta": 0.05,
        "plastic_gate": "pred",
    },
    # the same, with the gate ignoring the record: the cell acts, but not on its prediction
    "pond-v2-record-random": {
        "grid": 32,
        "resource_regen": 0.05,
        "baseline_income": 0.2,
        "income_mode": "proportional",
        "update_cost": 0.01,
        "repair_cost": 0.005,
        "damage_rate": 0.02,
        "init_resource_fill": 1.0,
        "resource_max": 1.0,
        "budding_mass": 8,
        "noise": 0.0,
        "boundary": "absorbing",
        "plastic_eta": 0.05,
        "plastic_gate": "random",
    },
}

# which world version each profile belongs to. Series of different versions are not pooled.
PROFILE_VERSION = {
    "pond-v2-alive": 2,
    "pond-v2-record": 2,
    "pond-v2-record-random": 2,
}


def apply_profile(cfg, name: str):
    """Set the profile's fields on `cfg` and return the list of fields it set."""
    if name not in PROFILES:
        raise KeyError(f"unknown profile {name!r}; known: {sorted(PROFILES)}")
    setattr(cfg, "_profile_name", name)
    set_fields = []
    for k, v in PROFILES[name].items():
        if not hasattr(cfg, k):
            raise KeyError(f"profile {name!r} names a field the config does not have: {k}")
        setattr(cfg, k, v)
        set_fields.append(k)
    return set_fields


def profile_block(cfg, name: str | None) -> dict:
    """What the artifact records about the profile.

    `fields_set` is the list of fields the profile overrode, so a reader can see what the name stands for
    without opening this file; `version` is the world version, so series are not pooled across it.
    """
    if not name or name not in PROFILES:
        return {"name": name, "known": False, "version": None, "fields_set": []}
    return {
        "name": name,
        "known": True,
        "version": PROFILE_VERSION.get(name),
        "fields_set": sorted(PROFILES[name]),
        "n_fields_set": len(PROFILES[name]),
    }
