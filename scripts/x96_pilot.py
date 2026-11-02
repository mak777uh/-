"""x96_pilot.py — X96: the second diffusive species (owner-approved 02.11).

Step 1 is the anchor: with `--second-species` absent, seed 291 at F = 0.030 must reproduce the committed `x100_f030_s291.json`
bit-for-bit (`series` and `uid_pairs`). A flag that changes the off-path is not a flag, and the anchor is checked against an
artifact in git rather than against a fresh run.

Step 2 is the pilot: one cell (F = 0.030), one seed (401), `Dw` in {0.08, 0.16, 0.32} x `gamma` in {0.5, 1.5}, plus the w-off
control. Each run saves the field at step 6000 so the wavelength readout (`field_metrics.angular`) can be taken from it.

Plan: reports/2026-11-02-x96-second-species-plan.md.

    python scripts/x96_pilot.py --anchor       # only the anchor
    python scripts/x96_pilot.py                # anchor, then the pilot
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
FIELDS = L1 / "_x96_fields"
REFERENCE = L1 / "x100_f030_s291.json"

BASE = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]

SETTINGS = [("dw008_g05", "0.08", "0.5"), ("dw008_g15", "0.08", "1.5"),
            ("dw016_g05", "0.16", "0.5"), ("dw016_g15", "0.16", "1.5"),
            ("dw032_g05", "0.32", "0.5"), ("dw032_g15", "0.32", "1.5")]

# X96b: the first pass collapsed the field (gamma 0.5 cuts the autocatalysis by a third inside a structure), so this sweep keeps the
# pattern alive: gamma 0.05-0.20 instead of 0.5-1.5, same three diffusion lengths.
MILD = [("dw008_g005", "0.08", "0.05"), ("dw008_g01", "0.08", "0.10"), ("dw008_g02", "0.08", "0.20"),
        ("dw016_g005", "0.16", "0.05"), ("dw016_g01", "0.16", "0.10"), ("dw016_g02", "0.16", "0.20"),
        ("dw032_g005", "0.32", "0.05"), ("dw032_g01", "0.32", "0.10"), ("dw032_g02", "0.32", "0.20")]


def run(cmd: list[str], timeout: int = 3000) -> tuple[bool, str, float]:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    tail = (proc.stderr or proc.stdout or "")[-300:]
    return proc.returncode == 0, tail, time.time() - t0


def anchor() -> bool:
    out = ROOT / "_hourly" / "x96_anchor_v2.json"
    cmd = [PY, str(TRACK), *BASE, "--F", "0.030", "--seed", "291", "--out", str(out)]
    ok, tail, dt = run(cmd)
    if not ok:
        print(f"[x96] anchor run FAILED {dt:.0f}s {tail}")
        return False
    new = json.loads(out.read_text(encoding="utf-8"))
    ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
    same_series = new.get("series") == ref.get("series")
    same_pairs = new.get("uid_pairs") == ref.get("uid_pairs")
    print(f"[x96] anchor: series identical={same_series} uid_pairs identical={same_pairs} ({dt:.0f}s)")
    if not (same_series and same_pairs):
        diff = [k for k in new.keys() if k in ("series", "uid_pairs") and new.get(k) != ref.get(k)]
        print(f"[x96] ANCHOR FAILED in {diff}; the flag changes the off-path — do not run the pilot")
        return False
    return True


def pilot(mild: bool = False) -> int:
    fields = (L1 / "_x96b_fields") if mild else FIELDS
    prefix = "x96bpilot" if mild else "x96pilot"
    settings = MILD if mild else SETTINGS
    fields.mkdir(parents=True, exist_ok=True)
    rows = []
    todo = [("w_off", None, None)] + settings
    for tag, dw, gamma in todo:
        out = L1 / f"{prefix}_{tag}.json"
        if out.exists():
            rows.append({"tag": tag, "status": "skipped (exists)"})
            print(f"[{prefix}] {tag}: skipped")
            continue
        cmd = [PY, str(TRACK), *BASE, "--F", "0.030", "--seed", "401", "--out", str(out),
               "--save-fields", str(fields), "--save-fields-at", "6000"]
        if dw is not None:
            cmd += ["--second-species", "--Dw", dw, "--gamma", gamma, "--beta-w", "0.05"]
        ok, tail, dt = run(cmd)
        status = "ok" if ok else "failed"
        rows.append({"tag": tag, "Dw": dw, "gamma": gamma, "status": status, "seconds": round(dt, 1), "tail": tail})
        print(f"[{prefix}] {tag}: {status} {dt:.0f}s {tail}")
        (L1 / f"{prefix}_index.json").write_text(
            json.dumps({"kind": f"{prefix}_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        if not ok:
            return 1
    print(f"[{prefix}] pilot done: {len(rows)} runs")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X96 second-species pilot")
    ap.add_argument("--anchor", action="store_true", help="only check the anchor")
    ap.add_argument("--mild", action="store_true", help="X96b: the mild sweep (gamma 0.05-0.20)")
    ap.add_argument("--skip-anchor", action="store_true", help="the anchor already passed in this session")
    args = ap.parse_args(argv)
    if not args.skip_anchor and not anchor():
        return 1
    if args.anchor:
        return 0
    return pilot(mild=args.mild)


if __name__ == "__main__":
    raise SystemExit(main())
