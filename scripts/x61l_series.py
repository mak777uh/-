"""x61l_series.py — X61-long: is the late concentration selection starting, or a drift?

Preregistered in `reports/2026-11-01-x61-long-horizon-plan.md`. Same world as the `a50` arm of X59, four times the
horizon: 24 000 steps, five seeds, fields at 6000 / 12000 / 18000 / 24000.

The run is only comparable if its first 6000 steps reproduce `x59_a50_s171` exactly, so the script checks the first seven
snapshots of seed 171 against that file and refuses to continue on a mismatch.

Run:
    python scripts/x61l_series.py
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
FIELDS = L1 / "x61l_fields"

COMMON = [
    "--steps", "24000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "6000,12000,18000,24000",
]


def run_one(seed: int) -> dict:
    out = L1 / f"x61l_a50_s{seed}.json"
    if out.exists():
        return {"seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--seed", str(seed), "--save-fields", str(FIELDS), "--out", str(out)]
    last = {"seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1800)
        except subprocess.TimeoutExpired:
            last = {"seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"seed": seed, "status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                    "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt}
    return last


def prefix_matches() -> tuple[bool, str]:
    a = L1 / "x61l_a50_s171.json"
    b = L1 / "x59_a50_s171.json"
    if not (a.exists() and b.exists()):
        return False, "files missing"
    sa = json.loads(a.read_text(encoding="utf-8")).get("series") or []
    sb = json.loads(b.read_text(encoding="utf-8")).get("series") or []
    head = sa[: len(sb)]
    if head == sb:
        return True, f"first {len(sb)} snapshots identical to x59_a50_s171"
    return False, "prefix DIFFERS from x59_a50_s171"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X61-long: 24000 steps")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = [run_one(seeds[0])]
    print(f"[x61l] seed {seeds[0]}: {rows[0]['status']} {rows[0].get('seconds', '')}", flush=True)
    ok, msg = prefix_matches()
    print(f"[x61l] anchor: {'PASS' if ok else 'FAIL'} — {msg}", flush=True)
    if not ok:
        return 1
    for seed in seeds[1:]:
        r = run_one(seed)
        rows.append(r)
        print(f"[x61l] seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x61l_series_index.json").write_text(
                json.dumps({"kind": "x61l_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x61l_series_index.json").write_text(
        json.dumps({"kind": "x61l_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x61l] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
