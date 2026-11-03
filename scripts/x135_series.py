"""x135_series.py — X135: the X134 sweep at F = 0.040, plus the single-disc control (SEP = 0).

The probe is unchanged from X134, so the anchor is re-checked against the file X134 produced rather than re-run.

Run:
    python scripts/x135_series.py --anchor
    python scripts/x135_series.py
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
ANCHOR_OUT = HOURLY / "x134_anchor.json"      # produced by X134; the probe has not changed since

SEPARATIONS = (0, 8, 12, 18, 24, 30, 36)
RADIUS = 3
SEEDS = (601, 602, 603, 604, 605)
FLOW = "0.040"

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
FLAG_KEYS = {"save_fields", "save_fields_every", "init_spots"}


def run_one(sep: int, seed: int, out: Path) -> dict:
    if out.exists():
        return {"sep": sep, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out),
           "--init-spots", f"{RADIUS}:{sep}"]
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
    if not ANCHOR_OUT.exists():
        print("[x135] anchor file missing — run scripts/x134_series.py --anchor first")
        return 1
    a = json.loads(ANCHOR_OUT.read_text(encoding="utf-8"))
    b = json.loads(ANCHOR_REF.read_text(encoding="utf-8"))
    diffs = [k for k in sorted(set(a) | set(b)) if k not in VOLATILE | DECLARED and a.get(k) != b.get(k)]
    pa, pb = a.get("params", {}), b.get("params", {})
    param_diffs = [k for k in sorted(set(pa) | set(pb)) if k not in FLAG_KEYS and pa.get(k) != pb.get(k)]
    ok = (not diffs and not param_diffs and a.get("uid_pairs") == b.get("uid_pairs"))
    print(f"[x135] anchor keys differing outside the declared flags: {diffs if diffs else 'none'}")
    print(f"[x135] anchor params differing outside the flags: {param_diffs if param_diffs else 'none'}")
    print(f"[x135] uid_pairs identical: {a.get('uid_pairs') == b.get('uid_pairs')}")
    print("[x135] ANCHOR OK" if ok else "[x135] ANCHOR FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X135 maze mixing length")
    ap.add_argument("--anchor", action="store_true")
    ap.add_argument("--seps", default="")
    args = ap.parse_args(argv)
    if args.anchor:
        return anchor()

    seps = [int(s) for s in args.seps.split(",") if s.strip()] or list(SEPARATIONS)
    index = L1 / "x135_series_index.json"
    rows = []
    for sep in seps:
        for seed in SEEDS:
            out = L1 / f"x135_sep{sep}_s{seed}.json"
            r = run_one(sep, seed, out)
            rows.append(r)
            print(f"[x135] sep {sep} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x135_series_index", "anchor": "ANCHOR OK", "flow": FLOW, "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x135] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
