"""x155_ablation.py — the mutation-off arm of X155, plus its anchor.

Three runs at `F = 0.030`, the exact command of `scripts/x108_series.py` with one flag changed at a time:

1. anchor, mutation 0.15, seed 301 — must reproduce `x108_f030_s301.json` key-by-key, because the arm's whole
   value is that the mutation flag is the only difference;
2. `--mutation 0.0`, seed 301;
3. `--mutation 0.0`, seed 302.

Plan: reports/2026-11-03-x155-heredity-plan.md

Run:
    python scripts/x155_ablation.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x108_fields"
REFERENCE = L1 / "x108_f030_s301.json"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--save-fields", str(FIELDS), "--save-fields-every", "10",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
    "--F", "0.030",
]

ARMS = [
    {"tag": "anchor", "seed": 301, "mutation": "0.15"},
    {"tag": "nomut", "seed": 301, "mutation": "0.0"},
    {"tag": "nomut", "seed": 302, "mutation": "0.0"},
]


def compare_anchor() -> dict:
    ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
    new = json.loads((L1 / "x155_anchor_f030_s301.json").read_text(encoding="utf-8"))
    diffs = []
    for key in ("uid_pairs", "size_pairs", "uid_outcomes"):
        if ref.get(key) != new.get(key):
            diffs.append(key)
    if len(ref.get("series") or []) != len(new.get("series") or []):
        diffs.append("series_length")
    else:
        for a, b in zip(ref["series"], new["series"]):
            for key in ("step", "components", "s_mean", "components_log"):
                if a.get(key) != b.get(key):
                    diffs.append(f"series[{a.get('step')}].{key}")
                    break
            if diffs:
                break
    return {"identical": not diffs, "diffs": diffs[:8],
            "uid_pairs": len(new.get("uid_pairs") or []),
            "inheritability_r": (new.get("selection") or {}).get("inheritability_r")}


def main() -> int:
    index = L1 / "x155_ablation_index.json"
    rows = []
    for arm in ARMS:
        out = L1 / f"x155_{arm['tag']}_f030_s{arm['seed']}.json"
        if out.exists():
            rows.append({**arm, "status": "skipped (exists)"})
            continue
        cmd = [PY, str(TRACK), *COMMON, "--seed", str(arm["seed"]), "--mutation", arm["mutation"], "--out", str(out)]
        t0 = time.time()
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3000)
        row = {**arm, "status": "ok" if proc.returncode == 0 else "failed",
               "seconds": round(time.time() - t0, 1)}
        if proc.returncode != 0:
            row["tail"] = (proc.stderr or proc.stdout or "")[-300:]
        else:
            payload = json.loads(out.read_text(encoding="utf-8"))
            row["inheritability_r"] = (payload.get("selection") or {}).get("inheritability_r")
            row["splits"] = (payload.get("selection") or {}).get("splits")
        rows.append(row)
        index.write_text(json.dumps({"kind": "x155_ablation_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
        print(f"[x155] {arm['tag']} seed {arm['seed']} mutation {arm['mutation']}: {row['status']} "
              f"{row.get('seconds')} r={row.get('inheritability_r')}", flush=True)
        if row["status"] == "failed":
            return 1
    anchor = compare_anchor()
    rows.append({"anchor_check": anchor})
    index.write_text(json.dumps({"kind": "x155_ablation_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
    print("[x155] anchor identical:", anchor["identical"], anchor.get("diffs"), flush=True)
    return 0 if anchor["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
