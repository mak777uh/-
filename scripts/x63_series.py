"""x63_series.py — X63: four more correlation lengths, to turn X62's three points into a profile.

Preregistered in `reports/2026-11-01-x63-scale-sweep-plan.md`. Amplitude fixed at 0.5, seeds 171-175, scales 6, 8, 16, 32.
The anchors (4 -> 20, 12 -> 308, 24 -> 175 divisions) are already on disk, so this run only fills the gaps around the
suspected resonance at the pattern wavelength.

Run:
    python scripts/x63_series.py
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
FIELDS = L1 / "x63_fields"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "6000",
]

ARMS = {
    "s06": ["--hetero-scale", "6.0"],
    "s08": ["--hetero-scale", "8.0"],
    "s16": ["--hetero-scale", "16.0"],
    "s32": ["--hetero-scale", "32.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x63_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed),
           "--save-fields", str(FIELDS), "--out", str(out)]
    last = {"arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            last = {"arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X63: scale sweep")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        for arm in ("s06", "s08", "s16", "s32"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x63] {arm} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x63_series_index.json").write_text(
                    json.dumps({"kind": "x63_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x63_series_index.json").write_text(
        json.dumps({"kind": "x63_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x63] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
