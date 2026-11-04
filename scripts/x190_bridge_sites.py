"""x190_bridge_sites.py — X190: the bridge with the sample made of SITES, not seeds.

X189's manipulation IS the lattice site: its radius-6 arm compared two distinct cold sites against one warm and its radius-3 arm
one replicated site per level, so three seeds were not three independent worlds. X190 fixes the sample: it enumerates the sites
the seed map can produce, keeps five distinct sites per level whose `F_local` is inside the level band, and runs three seeds per
site. The readout is X189's contact-moment bridge ratio, unchanged.

Pre-registration: reports/2026-11-04-x190-bridge-sites-plan.md.
Run: python scripts/x190_bridge_sites.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x190_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
SITES_PER_LEVEL = 5
SEEDS_PER_SITE = 3
SAVE_AT = "40,60,80,100,140,200,300"
ARMS = [("r6_g9", 6.0, 9.0), ("r3_g10", 3.0, 10.0)]
LEVELS = {"cold": 0.017, "warm": 0.030}
TOLERANCE = 0.0025
SCAN = 60000

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def jitter(seed: int):
    g = GRID
    jr = np.random.default_rng(int(seed) + 9187)
    return tuple(int(v) for v in jr.integers(-g // 4, g // 4 + 1, size=2))


def site_flow(seed: int, sep: float) -> float:
    """F_local at the colder of the two discs for this seed's site, same arithmetic as X187 and X189."""
    g, k, f = GRID, 2.0 * math.pi / SCALE, float(FLOW)
    jx, jy = jitter(seed)
    cx, cy = g / 2.0 + jx, g / 2.0 + jy

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    return f * (1 + 0.5 * (2 * min(gat(cx - sep / 2.0, cy), gat(cx + sep / 2.0, cy)) - 1))


def pick_sites(sep: float, target: float):
    """Five distinct sites inside the level band, three seeds each, in seed order."""
    per_site: dict[tuple[int, int], list[int]] = {}
    chosen: list[tuple[tuple[int, int], float, list[int]]] = []
    for seed in range(SCAN):
        f_loc = site_flow(seed, sep)
        if abs(f_loc - target) > TOLERANCE:
            continue
        key = jitter(seed)
        bucket = per_site.setdefault(key, [])
        if len(bucket) < SEEDS_PER_SITE:
            bucket.append(seed)
        if len(bucket) == SEEDS_PER_SITE and key not in [c[0] for c in chosen]:
            chosen.append((key, f_loc, list(bucket)))
            if len(chosen) >= SITES_PER_LEVEL:
                break
    return chosen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x190_bridge_sites", "flow": float(FLOW), "steps": STEPS, "save_at": SAVE_AT,
             "sites_per_level": SITES_PER_LEVEL, "seeds_per_site": SEEDS_PER_SITE,
             "prediction": "radius 6 gap 9: the warm level's contact-moment bridge ratio is at least 0.05 lower than the cold "
                           "level's, now over five distinct sites per level; the mean within-site spread is at least 0.02",
             "arms": {}, "runs": []}
    for name, rad, gap in ARMS:
        sep = 2 * rad + gap
        arm = {"radius": rad, "gap": gap, "sep": sep, "levels": {}}
        for lvl, tgt in LEVELS.items():
            sites = pick_sites(sep, tgt)
            arm["levels"][lvl] = {"sites": [{"jitter": list(s[0]), "f_local": round(s[1], 5), "seeds": s[2]}
                                            for s in sites]}
            for si, (key, f_loc, seeds) in enumerate(sites):
                for seed in seeds:
                    tag = f"{name}_{lvl}_site{si}_s{seed}"
                    out = L1 / f"x190_{tag}.json"
                    fdir = FIELDS / tag
                    if out.exists() and out.stat().st_size > 0:
                        index["runs"].append({"arm": name, "level": lvl, "site": si, "seed": seed,
                                              "jitter": list(key), "status": "skipped (exists)"})
                        continue
                    cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                           "--out", str(out), "--init-spots", f"{rad:g}:{sep:g}",
                           "--save-fields", str(fdir), "--save-fields-at", SAVE_AT]
                    t0 = time.time()
                    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                                       errors="replace", timeout=12000)
                    status = "ok" if p.returncode == 0 else "failed"
                    index["runs"].append({"arm": name, "level": lvl, "site": si, "seed": seed, "jitter": list(key),
                                          "status": status, "seconds": round(time.time() - t0, 1),
                                          **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
                    print(f"[x190] {tag}: {status} ({round(time.time() - t0, 1)} s, F_local {f_loc:.5f})")
        index["arms"][name] = arm
    if args.write:
        (L1 / "x190_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x190] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
