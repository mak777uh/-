"""X160: does an external signal hold diversity through a mortality buffer?

Three arms at equal realised tempo: a constant, the real microphone recording, and its IAAFT surrogate
(same length, same mean, same standard deviation, phase destroyed). The stream drives a leaky scalar m
(`--memory-tau`) which modulates the per-step death probability (`--mortality-gain`). Every arm is
normalised to zero mean and unit standard deviation, so the *mean* of m is the same in all three and only
its structure differs.

Usage:
    python scripts/x160_series.py --probe                 # 3 arms x 3 seeds x tau 300, prints the readouts
    python scripts/x160_series.py --write                 # the full 3 x 20 x 3 grid
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MO = ROOT / "morphogenesis"
OUT = MO / "experiments" / "E09_pond" / "x160_memory"
STREAMS = {
    "const": None,
    "real": ROOT / "lab" / "streams" / "mic-2026-10-28.json",
    "surrogate": ROOT / "lab" / "streams" / "mic_iaaft-2026-10-29.json",
}
ARMS = ("const", "real", "surrogate")
TAUS = (300, 1000, 3000)
SEEDS = tuple(range(801, 821))
STEPS = 1800
GRID = 32
INCOME = 0.030
UPDATE_COST = 0.03
GAIN = 0.02


def normalised_stream(path: Path) -> list[float]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    vals = [float(v) for v in (raw.get("values") if isinstance(raw, dict) else raw)]
    mean = statistics.fmean(vals)
    sd = statistics.pstdev(vals) or 1.0
    return [(v - mean) / sd for v in vals]


def run_one(arm: str, tau: int, seed: int, tag: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"x160_{arm}_t{tau}_s{seed}{tag}.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    cmd = [
        sys.executable, "world/run_pond.py",
        "--steps", str(STEPS), "--grid", str(GRID), "--seed", str(seed),
        "--income", str(INCOME), "--update-cost", str(UPDATE_COST),
        "--start-cells", "4", "--device", "cpu",
        "--memory-tau", str(tau), "--mortality-gain", str(GAIN),
        "--out", str(out),
    ]
    stream = STREAMS[arm]
    if stream is not None:
        cache = OUT / f"_stream_{arm}.json"
        if not cache.exists():
            cache.write_text(json.dumps({"values": normalised_stream(stream)}), encoding="utf-8")
        cmd += ["--memory-stream", str(cache)]
    proc = subprocess.run(cmd, cwd=str(MO), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"{arm}/{tau}/{seed}: {proc.stderr[-600:]}")
    return json.loads(out.read_text(encoding="utf-8"))


def readouts(art: dict) -> dict:
    s = art.get("summary", {})
    return {
        "pop_time": s.get("pop_time"),
        "lineages_with_data": s.get("lineages_with_data"),
        "effective_lineages": s.get("effective_lineages"),
        "deaths": s.get("deaths"),
        "killed_by_memory": s.get("killed_by_memory"),
        "alive_final": (art.get("series") or [{}])[-1].get("alive") if art.get("series") else None,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--taus", default="")
    args = ap.parse_args(argv)

    seeds = tuple(int(s) for s in args.seeds.split(",") if s.strip()) or (SEEDS if args.write else SEEDS[:3])
    taus = tuple(int(t) for t in args.taus.split(",") if t.strip()) or (TAUS if args.write else (300,))
    tag = "_probe" if args.probe else ""

    rows: list[dict] = []
    for tau in taus:
        for arm in ARMS:
            for seed in seeds:
                art = run_one(arm, tau, seed, tag)
                r = readouts(art)
                r.update({"arm": arm, "tau": tau, "seed": seed})
                rows.append(r)

    print(f"[x160] runs {len(rows)}; gain {GAIN}, steps {STEPS}, tau {taus}")
    for tau in taus:
        for arm in ARMS:
            sub = [r for r in rows if r["arm"] == arm and r["tau"] == tau]
            pt = [r["pop_time"] for r in sub if r["pop_time"] is not None]
            lw = [r["lineages_with_data"] for r in sub if r["lineages_with_data"] is not None]
            km = [r["killed_by_memory"] for r in sub if r["killed_by_memory"] is not None]
            print(f"  tau {tau:5d} {arm:9s} n={len(sub):2d} pop_time med "
                  f"{statistics.median(pt) if pt else float('nan'):7.1f}  lineages med "
                  f"{statistics.median(lw) if lw else float('nan'):5.1f}  killed med "
                  f"{statistics.median(km) if km else float('nan'):8.1f}")

    if args.write:
        agg = OUT / "x160_memory.json"
        agg.write_text(json.dumps({"gain": GAIN, "steps": STEPS, "grid": GRID, "income": INCOME,
                                   "update_cost": UPDATE_COST, "taus": list(taus), "rows": rows},
                                  ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[x160] aggregate: {agg.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
