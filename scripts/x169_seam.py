"""x169_seam.py — X169: sample the field around a fusing pair, to look for a seam.

Arm A (pair): radius 3, surface gap 8, i.e. --init-spots 3:14, three seeds.
Arm B (control): a single body from the default seed in the same world, three seeds.
Both: 1 500 steps, components every 10 steps, the field dumped every 10 steps into a gitignored directory.

Pre-registration: reports/2026-11-04-x169-seam-plan.md.
Run: python scripts/x169_seam.py --write
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
FIELDS = ROOT / "_hourly" / "x169_fields"

SEEDS = (991, 992, 993)
STEPS = 1500
FLOW = "0.030"
SEP = 14

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
    "--save-fields-every", "10", "--save-fields-at", "10",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x169_seam", "steps": STEPS, "flow": FLOW, "sep": SEP, "seeds": list(SEEDS),
             "fields_dir": str(FIELDS.relative_to(ROOT)), "runs": []}
    for arm, extra in (("pair", ["--init-spots", f"3:{SEP}"]), ("single", [])):
        for seed in SEEDS:
            out = L1 / f"x169_{arm}_s{seed}.json"
            fdir = FIELDS / f"{arm}_s{seed}"
            if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
                index["runs"].append({"arm": arm, "seed": seed, "status": "skipped (exists)"})
                print(f"[x169] {arm} s{seed}: skipped")
                continue
            fdir.mkdir(parents=True, exist_ok=True)
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--save-fields", str(fdir), *extra]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=5000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            n_npy = len(list(fdir.glob("*.npy")))
            index["runs"].append({"arm": arm, "seed": seed, "status": status, "seconds": dt, "dumps": n_npy,
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x169] {arm} s{seed}: {status} {dt} dumps {n_npy}")
    if args.write:
        (L1 / "x169_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x169] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
