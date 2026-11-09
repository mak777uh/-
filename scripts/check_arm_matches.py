"""Gate: the arm a run says it ran must be the arm it actually ran.

Why. Twice on 08.11 a field was silently overwritten after it had been set, and both times the result looked
plausible:

  * E18 - the "no record" arm set plastic_eta = 0.0, which made `_plastic_mobility` return immediately, so the
    arm took NO ACTIONS AT ALL and the readout was undefined;
  * E19 - the profile set plastic_gate = "random", then the command-line default overwrote it with "pred", so
    the two acting arms were the SAME ARM (identical move counts) and the difference was exactly zero.

Neither was caught by any gate, because no gate compared what the artifact says against what the artifact
contains. This one does.

The rule. A run's artifact carries a `config` block. For every field the run DECLARED as its manipulation (the
manifest's `arm` or the profile's `fields_set`), the value in the config must match the value the run intended.
This script reads a manifest that names the arms and checks each artifact against it.

Usage:
  python scripts/check_arm_matches.py --manifest lab/experiments/E19.json
  python scripts/check_arm_matches.py --dir morphogenesis/experiments/E19 --field plastic_gate --expect random
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_config(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:  # noqa: BLE001
        return None
    summary = d.get("summary") or {}
    return summary.get("config") or None


def check_dir(directory: str, field: str, expect: str, arm_filter: str | None) -> int:
    """Every artifact whose name contains `arm_filter` must carry `field == expect`."""
    pattern = f"*{arm_filter}*.json" if arm_filter else "*.json"
    files = sorted(glob.glob(os.path.join(directory, pattern)))
    if not files:
        print(f"[arm] no artifacts matching {pattern} in {directory}")
        return 1
    bad = []
    for p in files:
        cfg = read_config(p)
        if cfg is None:
            bad.append((os.path.basename(p), "no config block"))
            continue
        got = cfg.get(field)
        if str(got) != str(expect):
            bad.append((os.path.basename(p), f"{field} = {got!r}, expected {expect!r}"))
    if bad:
        for name, why in bad[:10]:
            print(f"  ПРОВАЛ {name}: {why}")
        print(f"[arm] {len(bad)} of {len(files)} artifacts do not carry the arm they claim")
        return 1
    print(f"[arm] ok: {len(files)} artifacts carry {field} = {expect!r}")
    return 0


def check_manifest(path: str) -> int:
    """A manifest may name, per arm, the fields that define it. Check each named field against the artifacts."""
    try:
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"[arm] cannot read manifest: {exc}")
        return 1
    arms = m.get("arms") or {}
    if not arms:
        print(f"[arm] manifest {os.path.basename(path)} names no arms; nothing to check")
        return 0
    directory = m.get("artifacts_dir")
    if not directory:
        print("[arm] manifest names no artifacts_dir")
        return 1
    full = directory if os.path.isabs(directory) else os.path.join(ROOT, directory)
    fails = 0
    for arm_name, spec in arms.items():
        expect_fields = spec.get("expect") or {}
        if not expect_fields:
            continue
        files = sorted(glob.glob(os.path.join(full, f"*{arm_name}*.json")))
        if not files:
            print(f"  ПРОВАЛ {arm_name}: no artifacts")
            fails += 1
            continue
        for p in files:
            cfg = read_config(p)
            if cfg is None:
                print(f"  ПРОВАЛ {os.path.basename(p)}: no config block")
                fails += 1
                continue
            for field, want in expect_fields.items():
                got = cfg.get(field)
                if str(got) != str(want):
                    print(f"  ПРОВАЛ {os.path.basename(p)}: {field} = {got!r}, expected {want!r}")
                    fails += 1
    if fails:
        print(f"[arm] {fails} mismatches between the arm a run claims and the arm it ran")
        return 1
    print(f"[arm] ok: every artifact carries the fields its arm declares")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--dir")
    ap.add_argument("--field")
    ap.add_argument("--expect")
    ap.add_argument("--arm", default=None)
    args = ap.parse_args(argv)

    if args.manifest:
        return check_manifest(args.manifest)
    if args.dir and args.field is not None and args.expect is not None:
        return check_dir(args.dir, args.field, args.expect, args.arm)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
