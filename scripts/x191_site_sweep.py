"""x191_site_sweep.py — X191: the bridge as a dose-response in the local inflow, five sites per level, one seed per site.

X190 showed warmth thins the bridge over five distinct sites per level (radius 6 gap 9, -0.169, Mann-Whitney p = 0.016) and that
three seeds on one site are one world repeated, so the budget for the next question goes on levels rather than on clones.

Pre-registration: reports/2026-11-04-x191-site-sweep-plan.md.
Run: python scripts/x191_site_sweep.py --write
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
FIELDS = ROOT / "_hourly" / "x191_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
RADIUS, GAP = 6.0, 9.0
SEP = 2 * RADIUS + GAP
SITES_PER_LEVEL = 5
LEVELS = [0.016, 0.021, 0.026, 0.031, 0.036, 0.041]
TOLERANCE = 0.0025
SAVE_AT = "40,60,80,100,140,200,300"
SCAN = 120000

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
    jr = np.random.default_rng(int(seed) + 9187)
    return tuple(int(v) for v in jr.integers(-GRID // 4, GRID // 4 + 1, size=2))


def site_flow(seed: int) -> float:
    g, k, f = GRID, 2.0 * math.pi / SCALE, float(FLOW)
    jx, jy = jitter(seed)
    cx, cy = g / 2.0 + jx, g / 2.0 + jy

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    return f * (1 + 0.5 * (2 * min(gat(cx - SEP / 2.0, cy), gat(cx + SEP / 2.0, cy)) - 1))


def phase(key):
    """The pattern's phase class of a site: what `G`, and therefore F_local, actually depends on (period 12)."""
    return (key[0] % 12, key[1] % 12)


def pick_sites(target: float):
    """Five sites inside the target band with distinct jitters AND distinct phases.

    The first run required only distinct jitters and landed five times on one phase at F_local = 0.030, where all five ratios were
    identical (0.39916); the readout depends on the phase, so a level's site list must vary it (plan section 8).
    """
    chosen = []
    seen_sites, seen_phases = set(), set()
    for seed in range(SCAN):
        f_loc = site_flow(seed)
        if abs(f_loc - target) > TOLERANCE:
            continue
        key = jitter(seed)
        if key in seen_sites or phase(key) in seen_phases:
            continue
        seen_sites.add(key)
        seen_phases.add(phase(key))
        chosen.append((key, f_loc, seed))
        if len(chosen) >= SITES_PER_LEVEL:
            break
    return chosen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x191_site_sweep", "flow": float(FLOW), "radius": RADIUS, "gap": GAP, "sep": SEP,
             "steps": STEPS, "save_at": SAVE_AT, "sites_per_level": SITES_PER_LEVEL, "levels": LEVELS,
             "prediction": "the level means of the contact-moment bridge ratio fall monotonically in F_local (at most one inversion) "
                           "with a Spearman correlation over the 30 sites at or below -0.5; the fusion share rises (at most one "
                           "inversion) to at least 0.6 at the top level; the site-level correlation between the bridge ratio and the "
                           "outcome is negative with |rho| >= 0.5",
             "available_sites_per_level": {}, "runs": []}
    for li, target in enumerate(LEVELS):
        sites = pick_sites(target)
        index["available_sites_per_level"][f"{target:.3f}"] = len(sites)
        index.setdefault("phases_per_level", {})[f"{target:.3f}"] = [list(phase(s[0])) for s in sites]
        for si, (key, f_loc, seed) in enumerate(sites):
            tag = f"L{li}_site{si}_s{seed}"
            out = L1 / f"x191_{tag}.json"
            fdir = FIELDS / tag
            if out.exists() and out.stat().st_size > 0:
                index["runs"].append({"level_index": li, "level": target, "site": si, "jitter": list(key),
                                      "phase": list(phase(key)), "seed": seed, "status": "skipped (exists)"})
                continue
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--init-spots", f"{RADIUS:g}:{SEP:g}",
                   "--save-fields", str(fdir), "--save-fields-at", SAVE_AT]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=12000)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"level_index": li, "level": target, "site": si, "jitter": list(key),
                                  "phase": list(phase(key)), "seed": seed,
                                  "status": status, "seconds": round(time.time() - t0, 1),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x191] {tag}: {status} ({round(time.time() - t0, 1)} s, F_local {f_loc:.5f})")
    if args.write:
        (L1 / "x191_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x191] index written; sites found per level:", index["available_sites_per_level"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
