"""x70r_series.py — X70 with genuinely independent neutral worlds.

The dense re-logging (`x70d_series.py`) revealed a second defect while it was being analysed: in the neutral world
(`beta = 0`, `eps = 0`) the geometry does not depend on the seed at all. The initial blob is fixed and the seed only feeds
the trait channel, which has no feedback, so all five "seeds" are the same universe with different inert trait noise:
`uid_pairs`, areas and peaks are identical across seeds, only `s` differs. Every "5/5 seeds" statement about geometry in
X70 was therefore one world quoted five times.

This series keeps the same neutral world and only moves the starting blob by the seed (`--init-jitter`: centre offset and
±20 % radius), which is what replication of a world without feedback has to mean. Logging stays dense (50 steps) with field
snapshots every 200 steps so the spatial control can still be run.

Anchor: `--init-jitter` off reproduces the previous artifacts bit-for-bit (checked on seed 171 before the series).

Run:
    python scripts/x70r_series.py
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
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid",
]

# X70r: the only difference from x70d is this flag (see the module docstring) and the artifact prefix.
JITTER = ["--init-jitter"]

FIELDS = ROOT / "morphogenesis" / "experiments" / "L1_field" / "_x70r_fields"
SAVE_AT = ",".join(str(s) for s in range(200, 6001, 200))

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x70r_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *JITTER, *ARMS[arm], "--seed", str(seed), "--out", str(out),
           "--save-fields", str(FIELDS), "--save-fields-at", SAVE_AT]
    last = {"arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1800)
        except subprocess.TimeoutExpired:
            last = {"arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X70 neutral-world replication")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for seed in seeds:
        for arm in ("pattern", "homog"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x70r] {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x70r_series_index.json").write_text(
                    json.dumps({"kind": "x70r_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x70r_series_index.json").write_text(
        json.dumps({"kind": "x70r_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x70r] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
