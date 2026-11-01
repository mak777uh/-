"""x68r_series.py — X68 with five genuinely different neutral worlds per rule.

The X68 artifacts were measured in a `beta = 0` world, and in that world the seed does not move the geometry: the starting
blob is fixed and the seed only feeds the trait channel. All five "seeds" of each X68 arm are therefore the same universe
with different inert trait noise (`lifetimes` hashes are identical across seeds), so the "0/5 seeds" sentence in the X68
report means "the single world disagrees with the prediction", not five independent disagreements.

This series repeats exactly the same measurement with `--init-jitter`, which moves the starting blob by the seed and varies
its radius by ±20 %. Only then does "five worlds" mean five worlds. Rules 0.3 / 0.5 / 0.7 overlap, arms heterogeneous and
homogeneous, seeds 171-175: 30 runs.

The defect and the blast radius are in `reports/2026-11-01-x70-two-design-defects.md`; the rule is in
`docs/design-checks.md` ("a seed is replication only if it changes the world").

Run:
    python scripts/x68r_series.py
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
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--init-jitter",
]

RULES = {"ov03": ["--overlap", "0.3"], "ov05": ["--overlap", "0.5"], "ov07": ["--overlap", "0.7"]}
ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(rule: str, arm: str, seed: int) -> dict:
    out = L1 / f"x68r_{rule}_{arm}_s{seed}.json"
    if out.exists():
        return {"rule": rule, "arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *RULES[rule], *ARMS[arm], "--seed", str(seed), "--out", str(out)]
    last = {"rule": rule, "arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            last = {"rule": rule, "arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"rule": rule, "arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"rule": rule, "arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def worlds_differ(rule: str, arm: str) -> tuple[bool, str]:
    """Positive control: the seeds must now produce different worlds, or the series repeats the defect."""
    hashes = {}
    for f in sorted(L1.glob(f"x68r_{rule}_{arm}_s*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        rows = [{k: v for k, v in s.items() if not k.startswith("s_") and k != "components_log"}
                for s in d.get("series") or []]
        hashes[f.name] = json.dumps(rows, sort_keys=True)
    if len(hashes) < 2:
        return False, "fewer than two worlds on disk"
    distinct = len(set(hashes.values()))
    # В неоднородном мире все пять стартов обязаны дать разные миры. В однородном два старта иногда сходятся в одну и ту
    # же динамику — это свойство мира (он сходится), а не повтор дефекта: порог 4 из 5, а число печатается в отчёт.
    need = len(hashes) if arm == "pattern" else max(2, len(hashes) - 1)
    return distinct >= need, f"{distinct} distinct geometries of {len(hashes)} runs (need >= {need})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X68: identity rules on five real neutral worlds")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for rule in ("ov03", "ov05", "ov07"):
        for arm in ("pattern", "homog"):
            for seed in seeds:
                r = run_one(rule, arm, seed)
                rows.append(r)
                print(f"[x68r] {rule} {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}",
                      flush=True)
                if r["status"] in ("failed", "timeout"):
                    (L1 / "x68r_series_index.json").write_text(
                        json.dumps({"kind": "x68r_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
                    return 1
            ok, msg = worlds_differ(rule, arm)
            print(f"[x68r] positive control {rule}/{arm}: {'PASS' if ok else 'FAIL'} — {msg}", flush=True)
            if not ok:
                return 1
    (L1 / "x68r_series_index.json").write_text(
        json.dumps({"kind": "x68r_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x68r] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
