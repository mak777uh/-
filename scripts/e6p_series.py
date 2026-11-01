"""e6p_series.py — E6p: three selection regimes in the field, artifacts inside git.

Preregistered in `reports/2026-11-01-e6p-selection-regimes-plan.md`. The question was already asked twice (`E6c`, `E6d`,
§10bx–§10bz), but those artifacts lived in `_hourly/` and no longer exist, so the claims have no evidence in the
repository. This series re-asks it in one design, with three arms and ten paired seeds, and puts the files where they can
be checked.

    ctrl     --beta 0.0 --freq-dep 0.0     composition cannot affect decay; any drift is mutation plus inflow
    surv     --beta 0.2 --freq-dep 0.0     survival channel, no frequency dependence (the E6d regime)
    survfd   --beta 0.2 --freq-dep 1.0     frequency-dependent survival (the E6e regime, and the X60 regime)

Anchor: `survfd` seed 171 has exactly the X60 parameter set, so its run must reproduce
`morphogenesis/experiments/L1_field/x60_pattern_s171.json` bit-for-bit. The script checks that automatically and refuses
to continue if the anchor fails.

Run:
    python scripts/e6p_series.py --limit 1     # anchor only
    python scripts/e6p_series.py               # the series
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
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06",
    "--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json",
    "--hetero-scale", "12.0", "--sample-every", "1000", "--threshold", "0.2",
    "--eps", "0.0", "--bin-width", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
]

ARMS = {
    "ctrl": ["--beta", "0.0", "--freq-dep", "0.0"],
    "surv": ["--beta", "0.2", "--freq-dep", "0.0"],
    "survfd": ["--beta", "0.2", "--freq-dep", "1.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"e6p_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed), "--out", str(out)]
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


def anchor_ok() -> tuple[bool, str]:
    """survfd/171 must equal the X60 run of the same parameters."""
    a = L1 / "e6p_survfd_s171.json"
    b = L1 / "x60_pattern_s171.json"
    if not (a.exists() and b.exists()):
        return False, "anchor files missing"
    sa = json.loads(a.read_text(encoding="utf-8")).get("series")
    sb = json.loads(b.read_text(encoding="utf-8")).get("series")
    if sa == sb:
        return True, "series identical to x60_pattern_s171"
    return False, "series DIFFER from x60_pattern_s171"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E6p series: three selection regimes")
    ap.add_argument("--seeds", default="171-180")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    if args.limit:
        seeds = seeds[: args.limit]

    rows = []
    # anchor first: one run of survfd on seed 171, then compare
    rows.append(run_one("survfd", seeds[0]))
    ok, msg = anchor_ok()
    print(f"[e6p] anchor: {'PASS' if ok else 'FAIL'} — {msg}", flush=True)
    if not ok:
        print("[e6p] anchor failed, series not run", flush=True)
        return 1

    for seed in seeds:
        for arm in ("ctrl", "surv", "survfd"):
            if seed == seeds[0] and arm == "survfd":
                continue
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[e6p] {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "e6p_series_index.json").write_text(
                    json.dumps({"kind": "e6p_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "e6p_series_index.json").write_text(
        json.dumps({"kind": "e6p_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[e6p] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
