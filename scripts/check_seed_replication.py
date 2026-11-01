"""check_seed_replication.py — a seed is replication only if it changes the world.

In a world without feedback (`beta = 0`, `eps = 0`) the field does not depend on the seed: the initial blob is fixed and the
seed is consumed only by the trait channel. Five "seeds" then are one world quoted five times, and every "5/5 seeds"
statement about geometry in such an arm is one observation. This gate measures it instead of assuming it.

Method: group artifacts `L1_field/*_s<seed>.json` by name prefix, require the params to agree apart from `seed`, then hash
the `series` rows with the trait columns removed (`s_mean`, `s_sd_between`, `s_wild_fraction`, `components_log`). One
distinct hash across seeds means one world.

    python scripts/check_seed_replication.py --write    # regenerate seed_replication.json
    python scripts/check_seed_replication.py --check     # fail if the committed table disagrees with the artifacts
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "seed_replication.json"

TRAIT_KEYS = ("s_mean", "s_sd_between", "s_wild_fraction", "components_log")
SKIP_PREFIXES = ("x70d_", "x70r_", "hl1_", "n20_", "x14_", "x15_", "x16_", "x17_", "x18_", "x23_", "x48_", "x49_",
                 "x56_", "e6p_", "e6q_")


def geo_hash(doc: dict) -> str:
    rows = []
    for s in doc.get("series") or []:
        rows.append({k: v for k, v in s.items() if k not in TRAIT_KEYS})
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()[:16]


def build() -> dict:
    fams: dict[str, dict] = {}
    for path in sorted(glob.glob(str(L1 / "*_s[0-9]*.json"))):
        m = re.match(r"(.+)_s(\d+)\.json$", Path(path).name)
        if not m:
            continue
        fam, seed = m.group(1), int(m.group(2))
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not doc.get("series"):
            continue
        params = doc.get("params") or {}
        key = json.dumps({k: v for k, v in params.items() if k != "seed"}, sort_keys=True)
        f = fams.setdefault(fam, {"seeds": {}, "params": params, "param_key": key, "mixed_params": False})
        if f["param_key"] != key:
            f["mixed_params"] = True
        f["seeds"][seed] = geo_hash(doc)

    out = {}
    for fam, f in sorted(fams.items()):
        hashes = f["seeds"]
        distinct = len(set(hashes.values()))
        beta = f["params"].get("beta")
        eps = f["params"].get("eps")
        neutral = (beta in (0, 0.0, None)) and (eps in (0, 0.0, None))
        out[fam] = {
            "seeds": len(hashes),
            "distinct_geometry": distinct,
            "one_world": distinct == 1 and len(hashes) > 1,
            "neutral_world": bool(neutral),
            "mixed_params": f["mixed_params"],
            "defect": bool(distinct == 1 and len(hashes) > 1),
        }
    return {"kind": "seed_replication", "method": "sha256 of series rows without trait columns, per seed",
            "families": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="seed replication check")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    fresh = build()
    fams = fresh["families"]
    one = [k for k, v in fams.items() if v["defect"]]
    print(f"[seed-replication] families: {len(fams)}, one-world: {len(one)}")
    for k in one:
        print(f"    one world: {k} ({fams[k]['seeds']} seeds, neutral={fams[k]['neutral_world']})")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(fresh, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8", newline="\n")
        print(f"[seed-replication] written: {OUT.name}")
        return 0

    if args.check:
        if not OUT.exists():
            print("[seed-replication] FAIL: table missing, run --write")
            return 1
        old = json.loads(OUT.read_text(encoding="utf-8")).get("families", {})
        diff = sorted(set(old) ^ set(fams)) + [k for k in sorted(set(old) & set(fams)) if old[k] != fams[k]]
        if diff:
            print("[seed-replication] FAIL: table is stale for: " + ", ".join(diff[:8]))
            return 1
        print("[seed-replication] ok: table matches the artifacts")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
