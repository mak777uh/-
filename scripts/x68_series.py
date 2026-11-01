"""x68_series.py — X68: the lifetime contrast under two other identity rules.

Preregistered in `reports/2026-11-01-x68-identity-rule-plan.md`. Only the observer changes: `--overlap` decides when a
component inherits its parent's uid. The dynamics must be identical to the existing 0.5 arm, and the script checks that on
the first seed before spending the rest of the GPU time.

    ov03  --overlap 0.3   loose
    ov07  --overlap 0.7   strict

both on the heterogeneous arm (amp 0.5) and the homogeneous one (amp 0.0), seeds 171-175.

Run:
    python scripts/x68_series.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
]

RULES = {"ov03": ["--overlap", "0.3"], "ov07": ["--overlap", "0.7"]}
ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(rule: str, arm: str, seed: int) -> dict:
    out = L1 / f"x68_{rule}_{arm}_s{seed}.json"
    if out.exists():
        return {"rule": rule, "arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *RULES[rule], *ARMS[arm], "--seed", str(seed), "--out", str(out)]
    last = {"rule": rule, "arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            last = {"rule": rule, "arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"rule": rule, "arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"rule": rule, "arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def dynamics_unchanged(rule: str, arm: str, seed: int) -> tuple[bool, str]:
    """The observer must not touch the field: compare series with the 0.5 arm already on disk."""
    new = L1 / f"x68_{rule}_{arm}_s{seed}.json"
    old = L1 / f"x60_{arm}_s{seed}.json"
    if not (new.exists() and old.exists()):
        return False, "files missing"
    a = [s.get("components") for s in json.loads(new.read_text(encoding="utf-8")).get("series") or []]
    b = [s.get("components") for s in json.loads(old.read_text(encoding="utf-8")).get("series") or []]
    if a == b:
        return True, "components identical to the 0.5 arm"
    return False, "components DIFFER — the flag leaked into the dynamics"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X68: identity rule sensitivity")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = [run_one("ov03", "pattern", seeds[0])]
    print(f"[x68] first run: {rows[0]}", flush=True)
    ok, msg = dynamics_unchanged("ov03", "pattern", seeds[0])
    print(f"[x68] leak check: {'PASS' if ok else 'FAIL'} — {msg}", flush=True)
    if not ok:
        return 1

    for rule in ("ov03", "ov07"):
        for seed in seeds:
            for arm in ("pattern", "homog"):
                if rule == "ov03" and seed == seeds[0] and arm == "pattern":
                    continue
                r = run_one(rule, arm, seed)
                rows.append(r)
                print(f"[x68] {rule} {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}",
                      flush=True)
                if r["status"] in ("failed", "timeout"):
                    (L1 / "x68_series_index.json").write_text(
                        json.dumps({"kind": "x68_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
                    return 1
    (L1 / "x68_series_index.json").write_text(
        json.dumps({"kind": "x68_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x68] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
