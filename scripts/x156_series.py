"""x156_series.py — X156: twenty runs with the field-measured shape observer.

Two habitats (`F` = 0.030 spots, `F` = 0.040 connected) x ten seeds (801-810), 6 000 steps, sampled every ten steps, with
`--shape-log`. The observer is a pure function of the field, so the anchor (a reference run with and without the flag) is
bit-identical in every field except the two new keys.

    python scripts/x156_series.py [--cell f030|f040] [--steps 6000] [--device cpu]
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
INDEX = L1 / "x156_series_index.json"

CELLS = {
    "f030": {"name": "x156_shape_f030", "F": "0.030", "seeds": tuple(range(801, 811))},
    "f040": {"name": "x156_shape_f040", "F": "0.040", "seeds": tuple(range(801, 811))},
}

COMMON = [
    "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter", "--shape-log",
]


def run_one(cell: dict, seed: int, steps: int, device: str, out: Path) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--steps", str(steps), "--device", device,
           "--F", cell["F"], "--seed", str(seed), "--out", str(out)]
    last = {"seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=6000)
        except subprocess.TimeoutExpired:
            last = {"seed": seed, "status": "timeout", "attempt": attempt}
            continue
        elapsed = time.time() - t0
        if proc.returncode != 0:
            last = {"seed": seed, "status": "failed", "attempt": attempt, "seconds": round(elapsed, 1),
                    "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"seed": seed, "status": "ok", "seconds": round(elapsed, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X156 shape-heredity series")
    ap.add_argument("--cell", default="", help="f030 or f040 (default: both)")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args(argv)
    keys = [args.cell] if args.cell else list(CELLS)
    rows = json.loads(INDEX.read_text(encoding="utf-8"))["rows"] if INDEX.exists() else []
    for key in keys:
        cell = CELLS[key]
        for seed in cell["seeds"]:
            out = L1 / f"{cell['name']}_s{seed}.json"
            r = run_one(cell, seed, args.steps, args.device, out)
            r.update({"cell": key, "F": cell["F"], "steps": args.steps, "device": args.device})
            rows = [row for row in rows if not (row["cell"] == key and row["seed"] == seed)] + [r]
            rows.sort(key=lambda row: (row["cell"], row["seed"]))
            INDEX.write_text(json.dumps({"kind": "x156_series_index", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"[x156] {key} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                return 1
    ok = sum(1 for row in rows if row["status"] in ("ok", "skipped (exists)"))
    print(f"[x156] done: {ok} runs available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
