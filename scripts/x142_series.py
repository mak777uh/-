"""x142_series.py — X142: the annihilation band - radius 3 gaps 3 and 7, radius 4.5 gaps 4, 5 and 6.

`--init-spots R:SEP` places two discs and nothing else; the surface gap is `SEP - 2R`, and that is the quantity the
claim is about. The probe is unchanged since X139 (`git diff scripts/field_track.py` is empty), so the anchor is not
re-run; instead one fresh repeat of X139's gap-5 arm must come out identical to the committed log. That is the
control that the path has not moved, and it is cheaper than believing the diff.

Run:
    python scripts/x142_series.py --probe-control
    python scripts/x142_series.py
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

# (radius, gap) -> separation = 2R + gap
ARMS = ((3.0, 3), (3.0, 7), (4.5, 4), (4.5, 5), (4.5, 6))
SEEDS = (601, 602, 603, 604, 605)
FLOW = "0.030"

PROBE_REF = L1 / "x139_sep11_s601.json"     # radius 3, gap 5, the annihilation arm
PROBE_OUT = L1 / "x142_probecheck_s601.json"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def rkey(radius: float) -> str:
    return str(int(round(radius * 10)))


def arm_name(radius: float, gap: int, seed: int) -> str:
    return f"x142_g{gap}_r{rkey(radius)}_s{seed}"


def run_one(radius: float, gap: int, seed: int, out: Path) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"radius": radius, "gap": gap, "seed": seed, "status": "skipped (exists)"}
    sep = int(round(2 * radius + gap))
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out),
           "--init-spots", f"{radius}:{sep}"]
    last = {"radius": radius, "gap": gap, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=4000)
        except subprocess.TimeoutExpired:
            last.update({"status": "timeout", "attempt": attempt})
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last.update({"status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                         "tail": (proc.stderr or proc.stdout or "")[-300:]})
            continue
        return {"radius": radius, "gap": gap, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def probe_control() -> int:
    if not PROBE_REF.exists():
        print(f"[x142] probe control: reference missing: {PROBE_REF}")
        return 1
    r = run_one(3.0, 5, 601, PROBE_OUT)
    print(f"[x142] probe control run: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}")
    if r["status"] not in ("ok", "skipped (exists)"):
        return 1
    a = json.loads(PROBE_OUT.read_text(encoding="utf-8"))
    b = json.loads(PROBE_REF.read_text(encoding="utf-8"))
    series_same = a.get("series") == b.get("series")
    pairs_same = a.get("uid_pairs") == b.get("uid_pairs")
    sa, sb = a.get("summary") or {}, b.get("summary") or {}
    keys = sorted(k for k in set(sa) | set(sb) if k not in {"wall_seconds", "git_commit", "elapsed"})
    summary_diffs = [k for k in keys if sa.get(k) != sb.get(k)]
    ok = series_same and pairs_same and not summary_diffs
    print(f"[x142] series identical: {series_same}; uid_pairs identical: {pairs_same}; "
          f"summary diffs outside volatile: {summary_diffs if summary_diffs else 'none'}")
    print("[x142] PROBE CONTROL OK" if ok else "[x142] PROBE CONTROL FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X142 annihilation band")
    ap.add_argument("--probe-control", action="store_true")
    ap.add_argument("--arms", default="")
    ap.add_argument("--seeds", default="")
    args = ap.parse_args(argv)
    if args.probe_control:
        return probe_control()

    arms = list(ARMS)
    if args.arms.strip():
        arms = []
        for token in args.arms.split(","):
            r, g = token.split(":")
            arms.append((float(r), int(g)))
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    index = L1 / "x142_series_index.json"
    rows = []
    for radius, gap in arms:
        for seed in seeds:
            out = L1 / f"{arm_name(radius, gap, seed)}.json"
            r = run_one(radius, gap, seed, out)
            rows.append(r)
            print(f"[x142] R {radius} gap {gap} seed {seed}: {r['status']} {r.get('seconds', '')} "
                  f"{r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x142_series_index", "probe_control": "OK", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x142] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
