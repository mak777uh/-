"""x112c_series.py — X112c: the same cut sweep in the maze cell (F = 0.040), next to X108's 0.20 reference.

`--threshold` is an observer parameter: it decides which pixels count as a structure, not how the field evolves. So seeds 301-310 at
0.15 and 0.25 are the SAME twenty worlds X108 measured at 0.20 with a different observer, and the comparison is paired.

Preregistered in `reports/2026-11-02-x112c-cuts-maze-plan.md`, committed before this ran.

Run:
    python scripts/x112c_series.py
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

FLOW = "0.040"
SEEDS = tuple(range(301, 311))
THRESHOLDS = ("0.15", "0.25")

BASE = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--F", FLOW, "--sample-every", "50",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def _lock(action: str, extra: list[str] | None = None) -> None:
    cmd = [PY, str(ROOT / "scripts" / "lab.py"), action, "--experiment", "X112c_cuts_maze", "--owner", "lead"]
    if extra:
        cmd += extra
    try:
        subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    except Exception as exc:
        print(f"[x112c] lock {action} failed: {exc}", flush=True)


def run_one(seed: int, thr: str) -> dict:
    # the cell tag is derived from FLOW, not typed: a copied runner that keeps the old tag writes mislabeled artifacts
    cell_tag = "f" + FLOW.replace(".", "").lstrip("0")
    tag = f"x112c_{cell_tag}_thr{thr.replace('.', '')}_s{seed}"
    assert cell_tag == "f040", cell_tag
    out = L1 / f"{tag}.json"
    if out.exists():
        return {"tag": tag, "seed": seed, "threshold": thr, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *BASE, "--threshold", thr, "--seed", str(seed), "--out", str(out)]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3000)
        ok = proc.returncode == 0
        tail = (proc.stderr or proc.stdout or "")[-200:]
    except subprocess.TimeoutExpired:
        ok, tail = False, "timeout"
    return {"tag": tag, "seed": seed, "threshold": thr, "status": "ok" if ok else "failed",
            "seconds": round(time.time() - t0, 1), "tail": tail}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X112c cut series")
    ap.add_argument("--limit", type=int, default=0, help="stop after N runs (smoke test)")
    args = ap.parse_args(argv)

    _lock("claim", ["--ttl-minutes", "150"])
    index = L1 / "x112c_series_index.json"
    rows: list[dict] = []
    try:
        for thr in THRESHOLDS:
            for seed in SEEDS:
                if args.limit and len(rows) >= args.limit:
                    print(f"[x112c] limit reached at {len(rows)} runs")
                    return 0
                r = run_one(seed, thr)
                rows.append(r)
                print(f"[x112c] {r['tag']}: {r['status']} {r.get('seconds', '')}", flush=True)
                index.write_text(json.dumps({"kind": "x112c_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8", newline="\n")
                _lock("heartbeat")
                if r["status"] == "failed":
                    return 1
    finally:
        _lock("release")
    print(f"[x112c] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
