"""x134_series.py — X136: the wall to the cell - separations 14, 16, 17; 12, 15, 18 are reused from X134b.

`--init-spots R:SEP` places two discs and nothing else. This script anchors the probe (with the flag absent the run must reproduce `x108_f030_s301.json` key by key),
then sweeps six separations at F = 0.030, five seeds each.

Run:
    python scripts/x134_series.py --anchor
    python scripts/x134_series.py
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
HOURLY = ROOT / "_hourly"
ANCHOR_REF = L1 / "x108_f030_s301.json"
ANCHOR_OUT = HOURLY / "x134b_anchor.json"

SEPARATIONS = (14, 16, 17)
RADIUS = 3
SEEDS = (601, 602, 603, 604, 605)
FLOW = "0.030"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]
VOLATILE = {"wall_seconds", "git_commit", "config", "out", "command", "elapsed", "timing"}
DECLARED = {"fields_saved", "params"}
FLAG_KEYS = {"save_fields", "save_fields_every", "init_spots"}  # declared: the new flag exists with its inert default


def run_one(sep: int, seed: int, out: Path, spots: str | None) -> dict:
    if out.exists():
        return {"sep": sep, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out)]
    if spots is not None:
        cmd += ["--init-spots", spots]
    last = {"sep": sep, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=3000)
        except subprocess.TimeoutExpired:
            last.update({"status": "timeout", "attempt": attempt})
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last.update({"status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                         "tail": (proc.stderr or proc.stdout or "")[-300:]})
            continue
        return {"sep": sep, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def anchor() -> int:
    HOURLY.mkdir(exist_ok=True)
    r = run_one(0, 301, ANCHOR_OUT, spots=None)
    print(f"[x134] anchor run: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}")
    if r["status"] not in ("ok", "skipped (exists)"):
        return 1
    a = json.loads(ANCHOR_OUT.read_text(encoding="utf-8"))
    b = json.loads(ANCHOR_REF.read_text(encoding="utf-8"))
    diffs = [k for k in sorted(set(a) | set(b)) if k not in VOLATILE | DECLARED and a.get(k) != b.get(k)]
    pa, pb = a.get("params", {}), b.get("params", {})
    param_diffs = [k for k in sorted(set(pa) | set(pb)) if k not in FLAG_KEYS and pa.get(k) != pb.get(k)]
    ok = (not diffs and not param_diffs and a.get("uid_pairs") == b.get("uid_pairs"))
    print(f"[x134] keys differing outside the declared flags: {diffs if diffs else 'none'}")
    print(f"[x134] params differing outside the flags: {param_diffs if param_diffs else 'none'}")
    print(f"[x134] uid_pairs identical: {a.get('uid_pairs') == b.get('uid_pairs')}")
    print("[x134] ANCHOR OK" if ok else "[x134] ANCHOR FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X134 mixing length")
    ap.add_argument("--anchor", action="store_true")
    ap.add_argument("--seps", default="")
    ap.add_argument("--seeds", default="")
    args = ap.parse_args(argv)
    if args.anchor:
        return anchor()

    seps = [int(s) for s in args.seps.split(",") if s.strip()] or list(SEPARATIONS)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    index = L1 / "x136_series_index.json"
    rows = []
    for sep in seps:
        for seed in seeds:
            out = L1 / f"x136_sep{sep}_s{seed}.json"
            r = run_one(sep, seed, out, spots=f"{RADIUS}:{sep}")
            rows.append(r)
            print(f"[x134] sep {sep} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x136_series_index", "anchor": "ANCHOR OK", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x134] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
