"""x132_series.py — X132: twenty new worlds per cell at the two extreme inflows, seeds 311-330.

Same protocol as `x108_series.py` and `x126_series.py` (dense logging every 10 steps, `--split-new-uid`, no field saving). X126's anchor already proved that
omitting the field saving is inert; this script re-runs that comparison before the twenty start, so the series is anchored against `x108_f030_s301.json` key by key.

Run:
    python scripts/x132_series.py --anchor
    python scripts/x132_series.py
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

CELLS = {"f030": "0.030", "f040": "0.040"}
ANCHOR_FLOW = "0.030"
ANCHOR_REF = L1 / "x108_f030_s301.json"
ANCHOR_OUT = HOURLY / "x132_anchor.json"

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
FLAG_KEYS = {"save_fields", "save_fields_every"}


def run_one(flow: str, seed: int, out: Path) -> dict:
    if out.exists():
        return {"cell": flow, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", flow, "--seed", str(seed), "--out", str(out)]
    last = {"cell": flow, "seed": seed, "status": "failed"}
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
        return {"cell": flow, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def anchor() -> int:
    HOURLY.mkdir(exist_ok=True)
    if not ANCHOR_OUT.exists():
        r = run_one(ANCHOR_FLOW, 301, ANCHOR_OUT)
        print(f"[x132] anchor run: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}")
        if r["status"] != "ok":
            return 1
    else:
        print("[x132] anchor run: reusing", ANCHOR_OUT.name)
    a = json.loads(ANCHOR_OUT.read_text(encoding="utf-8"))
    b = json.loads(ANCHOR_REF.read_text(encoding="utf-8"))
    diffs = [k for k in sorted(set(a) | set(b)) if k not in VOLATILE | DECLARED and a.get(k) != b.get(k)]
    pa, pb = a.get("params", {}), b.get("params", {})
    param_diffs = [k for k in sorted(set(pa) | set(pb)) if k not in FLAG_KEYS and pa.get(k) != pb.get(k)]
    ok = (not diffs and not param_diffs and a.get("uid_pairs") == b.get("uid_pairs"))
    print(f"[x132] keys differing outside the declared flags: {diffs if diffs else 'none'}")
    print(f"[x132] params differing outside the flags: {param_diffs if param_diffs else 'none'}")
    print(f"[x132] uid_pairs identical: {a.get('uid_pairs') == b.get('uid_pairs')}")
    print("[x132] ANCHOR OK" if ok else "[x132] ANCHOR FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X132: twenty new worlds per cell")
    ap.add_argument("--seeds", default="311-330")
    ap.add_argument("--anchor", action="store_true")
    args = ap.parse_args(argv)
    if args.anchor:
        return anchor()

    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    index = L1 / "x132_series_index.json"
    rows = []
    for tag, flow in CELLS.items():
        for seed in seeds:
            r = run_one(flow, seed, L1 / f"x132_{tag}_s{seed}.json")
            rows.append(r)
            print(f"[x132] {tag} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x132_series_index", "anchor": "ANCHOR OK", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x132] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
