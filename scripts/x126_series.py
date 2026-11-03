"""x126_series.py — the third cell: ten worlds at F = 0.035, the identical protocol of X108.

X108 ran ten worlds at F = 0.030 and ten at F = 0.040 with dense logging (a component record at every 10 steps). The consequence chain was measured on those
two cells and differs by almost a factor of two in every readout. This series adds the cell between them with the same seeds, so the three-cell comparison is
paired by seed and the question "gradient in inflow, or step at percolation?" becomes answerable.

Protocol: byte-identical to `x108_series.py`'s COMMON except that fields are not saved — `x108_series.py` records that a field save is pure I/O and draws no
randomness, so the worlds are the same. The anchor below is what proves it: F = 0.030, seed 301, this script's flags, against the committed
`x108_f030_s301.json`, key by key.

Run:
    python scripts/x126_series.py --anchor        # one run + comparison, prints ANCHOR OK / list of differing keys
    python scripts/x126_series.py                 # ten runs, seeds 301-310
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

CELLS = {"f035": "0.035"}
ANCHOR_FLOW = "0.030"
ANCHOR_REF = L1 / "x108_f030_s301.json"

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


def run_one(flow_tag: str, seed: int, out: Path, flow: str | None = None) -> dict:
    if out.exists():
        return {"cell": flow_tag, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", flow or CELLS[flow_tag], "--seed", str(seed), "--out", str(out)]
    last = {"cell": flow_tag, "seed": seed, "status": "failed"}
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
        return {"cell": flow_tag, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def anchor() -> int:
    HOURLY.mkdir(exist_ok=True)
    out = HOURLY / "x126_anchor.json"
    if out.exists():
        print("[x126] anchor run: reusing", out.name)
    else:
        r = run_one("anchor", 301, out, flow=ANCHOR_FLOW)
        print(f"[x126] anchor run: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}")
        if r["status"] != "ok":
            return 1
    a = json.loads(out.read_text(encoding="utf-8"))
    b = json.loads(ANCHOR_REF.read_text(encoding="utf-8"))
    # the only declared difference is the two field-saving flags and their marker
    declared = {"fields_saved", "params"}   # params is compared field by field below
    diffs = [k for k in sorted(set(a) | set(b)) if k not in VOLATILE | declared and a.get(k) != b.get(k)]
    pa, pb = a.get("params", {}), b.get("params", {})
    flag_keys = {"save_fields", "save_fields_every"}
    param_diffs = [k for k in sorted(set(pa) | set(pb))
                   if k not in flag_keys and pa.get(k) != pb.get(k)]
    alone_a = sorted(set(pa) - set(pb) - flag_keys)
    alone_b = sorted(set(pb) - set(pa) - flag_keys)
    ok = (not diffs and not param_diffs and not alone_a and not alone_b
          and a.get("uid_pairs") == b.get("uid_pairs"))
    print(f"[x126] keys differing outside the declared flags: {diffs if diffs else 'none'}")
    print(f"[x126] params differing outside the flags: {param_diffs if param_diffs else 'none'}"
          f"{' (only-in-anchor ' + str(alone_a) + ')' if alone_a else ''}"
          f"{' (only-in-ref ' + str(alone_b) + ')' if alone_b else ''}")
    print(f"[x126] uid_pairs identical: {a.get('uid_pairs') == b.get('uid_pairs')}")
    print(f"[x126] declared flags: anchor save_fields={pa.get('save_fields')!r}/{pa.get('save_fields_every')!r}"
          f" vs ref {pb.get('save_fields') is not None}/{pb.get('save_fields_every')!r}")
    print("[x126] ANCHOR OK" if ok else "[x126] ANCHOR FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X126: the third cell at F = 0.035")
    ap.add_argument("--seeds", default="301-310")
    ap.add_argument("--anchor", action="store_true")
    args = ap.parse_args(argv)
    if args.anchor:
        return anchor()

    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    index = L1 / "x126_series_index.json"
    rows = []
    for flow_tag in CELLS:
        for seed in seeds:
            r = run_one(flow_tag, seed, L1 / f"x126_{flow_tag}_s{seed}.json")
            rows.append(r)
            print(f"[x126] {flow_tag} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x126_series_index", "anchor": "ANCHOR OK", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x126] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
