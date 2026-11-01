"""x58_analyse.py — the same measurement on a 128 grid: β₀, β₁, wavelength, normalised count.

Reads `morphogenesis/experiments/L1_field/x60_<arm>_s<seed>.json` and the arrays in `x60_fields/`, and answers the three
questions the preregistration fixed (`reports/2026-11-01-x60-fields-and-masks-plan.md`):

1. **Topology.** Is the fragmented field a scatter of spots (β₀ high, β₁ low) or a single labyrinth that the threshold
   tears apart (β₁ high)? β₁ is obtained from the Euler characteristic with the identity β₁ = β₀ − χ, valid for a 2-D
   binary image when β₂ = 0.
2. **Scale.** Does the contrast survive normalisation by the observed wavelength, `N·λ²/A`, where λ = 2π/q_peak from the
   radial structure factor of `v`?
3. **Share.** Does one structure dominate the thresholded area, or is the area spread over many pieces?

Conventions, stated because they decide the numbers:
- foreground = `v ≥ threshold` (default 0.2, the value used everywhere in the line);
- components: **4-connectivity with periodic wrap** (the same `label()` the runner uses);
- Euler characteristic: bit-quad formula on the wrapped mask,
  χ = (n₁ − n₃ − 2·n_diag)/4, which is exact for 4-connected foreground;
- the background is therefore 8-connected by construction; on a torus this is the standard pairing;
- λ is in **grid cells**, so `N·λ²/A` is dimensionless with `A = 96²`.

Run:
    python scripts/x58_analyse.py --write
    python scripts/x58_analyse.py --selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x58_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x58_betti.json"
THRESHOLD = 0.2
SNAPSHOTS = (4000, 8000, 12000)   # = physical time 2000/4000/6000 at dt = 0.5

sys.path.insert(0, str(ROOT / "scripts"))
from field_track import label  # noqa: E402  (та же функция, что в прогоне — не вторая реализация)


def drop_small(mask: np.ndarray, min_cells: int) -> np.ndarray:
    """Убрать компоненты меньше min_cells — ровно то, что делает прогон (--min-cells, по умолчанию 5)."""
    if min_cells <= 1:
        return mask
    lab, n = label(mask)
    for cid in range(1, n + 1):
        if int((lab == cid).sum()) < min_cells:
            mask = mask & (lab != cid)
    return mask


def beta0(mask: np.ndarray) -> int:
    _lab, n = label(mask.astype(bool))
    return int(n)


def euler(mask: np.ndarray) -> float:
    """χ of a periodic binary image, bit-quad formula (4-connected foreground)."""
    m = mask.astype(np.int8)
    a = m
    b = np.roll(m, -1, axis=1)
    c = np.roll(m, -1, axis=0)
    d = np.roll(np.roll(m, -1, axis=0), -1, axis=1)
    tot = a + b + c + d
    n1 = int((tot == 1).sum())
    n3 = int((tot == 3).sum())
    diag = int(((a == 1) & (d == 1) & (b == 0) & (c == 0)).sum() + ((b == 1) & (c == 1) & (a == 0) & (d == 0)).sum())
    return (n1 - n3 - 2 * diag) / 4.0


def structure_factor(v: np.ndarray) -> tuple[float, float]:
    """(q_peak, peak/median-tail ratio) from the radial power spectrum of v."""
    f = np.fft.fft2(v - v.mean())
    p = (np.abs(f) ** 2).astype(np.float64)
    ky = np.fft.fftfreq(v.shape[0]) * v.shape[0]
    kx = np.fft.fftfreq(v.shape[1]) * v.shape[1]
    ky, kx = np.meshgrid(ky, kx, indexing="ij")
    r = np.sqrt(ky ** 2 + kx ** 2)
    rbin = np.round(r).astype(int)
    prof = {}
    for rad in range(1, int(rbin.max()) + 1):
        sel = rbin == rad
        if sel.any():
            prof[rad] = float(p[sel].mean())
    if not prof:
        return 0.0, 0.0
    q = max(prof, key=prof.get)
    vals = sorted(prof.values())
    tail = vals[: max(1, len(vals) // 2)]
    ratio = prof[q] / (st.median(tail) if st.median(tail) > 0 else 1.0)
    return float(q), float(ratio)


def largest_share(mask: np.ndarray) -> float:
    lab, n = label(mask.astype(bool))
    if n == 0:
        return 0.0
    sizes = [int((lab == i).sum()) for i in range(1, n + 1)]
    return max(sizes) / sum(sizes)


def _occ(mask: np.ndarray, min_cells: int) -> float:
    return float(drop_small(mask, min_cells).mean())


def _threshold_for_occupancy(v: np.ndarray, target: float, min_cells: int) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(25):
        mid = (lo + hi) / 2
        if _occ(v > mid, min_cells) < target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def threshold_sweep() -> list[dict]:
    """β₁ при разных порогах: дырки — свойство поля или порога? Бесплатно, массивы уже на диске."""
    out = []
    for th in (0.15, 0.20, 0.25, 0.30):
        for t in SNAPSHOTS:
            diffs = []
            for seed in range(171, 176):
                fp = FIELDS / f"x58_pattern_s{seed}_t{t}.npy"
                fh = FIELDS / f"x58_homog_s{seed}_t{t}.npy"
                if not (fp.exists() and fh.exists()):
                    continue
                mc = 5
                mp = drop_small(np.load(fp).astype(np.float64) > th, mc)
                mh = drop_small(np.load(fh).astype(np.float64) > th, mc)
                diffs.append((beta0(mp) - euler(mp)) - (beta0(mh) - euler(mh)))
            if diffs:
                out.append({"threshold": th, "t": t, "n": len(diffs),
                            "median_diff_beta1": round(st.median(diffs), 2),
                            "seeds_positive": sum(1 for d in diffs if d > 0)})
    return out


def spectrum_by_arm() -> list[dict]:
    """Радиальный спектр, усреднённый по сидам: q — номер моды, lambda = N/q клеток."""
    out = []
    for t in SNAPSHOTS:
        for arm in ("pattern", "homog"):
            ps = []
            for seed in range(171, 176):
                f = FIELDS / f"x58_{arm}_s{seed}_t{t}.npy"
                if not f.exists():
                    continue
                v = np.load(f).astype(np.float64)
                fft = np.fft.fft2(v - v.mean())
                ps.append(np.abs(fft) ** 2)
            if not ps:
                continue
            p = np.mean(ps, axis=0)
            n = p.shape[0]
            k = np.fft.fftfreq(n) * n
            ky, kx = np.meshgrid(k, k, indexing="ij")
            r = np.round(np.sqrt(ky ** 2 + kx ** 2)).astype(int)
            prof = {rad: float(p[r == rad].mean()) for rad in range(1, int(r.max()) + 1) if (r == rad).any()}
            q = max(prof, key=prof.get)
            top = [rad for rad, _ in sorted(prof.items(), key=lambda kv: -kv[1])[:3]]
            # Доли мощности по модам 1..12 и энтропия: "есть ли выделенная длина волны" — это
            # концентрация спектра, а не номер пика. Пик на q=1 бывает и у широкого спектра.
            low = {rad: prof[rad] for rad in sorted(prof) if rad <= 12}
            tot = sum(prof.values()) or 1.0
            shares = {rad: round(v / tot, 3) for rad, v in low.items()}
            ent = -sum((v / tot) * math.log(v / tot) for v in low.values() if v > 0)
            out.append({"t": t, "arm": arm, "n_seeds": len(ps), "q_peak": q,
                        "lambda_cells": round(n / q, 2), "top3_modes": top,
                        "peak_share": shares.get(q),
                        "power_share_q1_12": shares,
                        "spectral_entropy": round(ent, 3),
                        "entropy_max_ln12": round(math.log(12), 3)})
    return out


def matched_occupancy() -> list[dict]:
    """Вторичный контроль (объявлен ПОСЛЕ данных): сравнить β₁ при равной занятой площади.

    Без него возражение простое: «дыр больше, потому что материала больше». Здесь у неоднородного
    прогона подбирается порог, дающий ту же занятую площадь, что у однородного при 0.2, и β₁
    сравнивается при равной площади.
    """
    out = []
    for t in SNAPSHOTS:
        diffs, rows = [], []
        for seed in range(171, 176):
            fp = FIELDS / f"x58_pattern_s{seed}_t{t}.npy"
            fh = FIELDS / f"x58_homog_s{seed}_t{t}.npy"
            if not (fp.exists() and fh.exists()):
                continue
            vp = np.load(fp).astype(np.float64)
            vh = np.load(fh).astype(np.float64)
            _jl = L1 / f"x58_pattern_s{seed}.json"
            if not _jl.exists():
                continue
            mc = int((json.loads(_jl.read_text(encoding='utf-8')).get("params") or {}).get("min_cells") or 1)
            qh = _occ(vh > THRESHOLD, mc)
            thp = _threshold_for_occupancy(vp, qh, mc)
            mp = drop_small(vp > thp, mc)
            mh = drop_small(vh > THRESHOLD, mc)
            b0p, b1p = beta0(mp), beta0(mp) - euler(mp)
            b0h, b1h = beta0(mh), beta0(mh) - euler(mh)
            diffs.append(b1p - b1h)
            rows.append({"seed": seed, "occupancy_matched": round(qh, 3), "threshold_pattern": round(thp, 4),
                         "beta0_pattern": b0p, "beta1_pattern": int(round(b1p)),
                         "beta0_homog": b0h, "beta1_homog": int(round(b1h))})
        if diffs:
            out.append({"t": t, "n": len(diffs), "median_diff_beta1": round(st.median(diffs), 2),
                        "seeds_positive": sum(1 for d in diffs if d > 0), "rows": rows})
    return out


def collect() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(str(L1 / "x60_*.json"))):
        name = os.path.basename(path)
        if not name.startswith(("x60_pattern_", "x60_homog_")):
            continue
        arm = "pattern" if name.startswith("x60_pattern_") else "homog"
        seed = int(name.rsplit("_s", 1)[1].split(".")[0])
        meta = json.loads(Path(path).read_text(encoding="utf-8"))
        for t in SNAPSHOTS:
            f = FIELDS / f"x58_{arm}_s{seed}_t{t}.npy"
            if not f.exists():
                continue
            v = np.load(f).astype(np.float64)
            mask = v > THRESHOLD   # строгое >, как в самом прогоне (vn > threshold)
            mask = drop_small(mask, int((meta.get("params") or {}).get("min_cells") or 1))
            b0 = beta0(mask)
            chi = euler(mask)
            b1 = b0 - chi
            q, ratio = structure_factor(v)
            lam = (v.shape[0] / q) if q else 0.0   # q — номер моды: lambda = N/q клеток
            area = mask.size
            by_step = {s["step"]: s for s in meta.get("series") or []}
            comp_json = (by_step.get(t) or {}).get("components")
            rows.append({
                "arm": arm, "seed": seed, "t": t,
                "components_json": comp_json,
                "match": (b0 == comp_json) if comp_json is not None else None,
                "beta0": b0, "beta1": int(round(b1)), "chi": round(chi, 2),
                "occupied": round(float(mask.mean()), 4),
                "largest_share": round(largest_share(mask), 3),
                "q_peak": q, "peak_ratio": round(ratio, 2),
                "lambda": round(lam, 2),
                "n_norm": round(b0 * lam * lam / area, 4) if lam else None,
            })
    return rows


def summarise(rows: list[dict]) -> dict:
    out = {}
    for t in SNAPSHOTS:
        cell = {}
        for arm in ("pattern", "homog"):
            sub = [r for r in rows if r["t"] == t and r["arm"] == arm]
            if not sub:
                continue
            cell[arm] = {k: round(st.median([r[k] for r in sub if r[k] is not None]), 3)
                         for k in ("beta0", "beta1", "largest_share", "lambda", "n_norm")}
            cell[arm]["n"] = len(sub)
        if "pattern" in cell and "homog" in cell:
            paired = {}
            for k in ("beta0", "beta1", "largest_share", "n_norm"):
                d = []
                seeds = sorted({r["seed"] for r in rows if r["t"] == t})
                for s in seeds:
                    a = next((r[k] for r in rows if r["t"] == t and r["seed"] == s and r["arm"] == "pattern"), None)
                    b = next((r[k] for r in rows if r["t"] == t and r["seed"] == s and r["arm"] == "homog"), None)
                    if a is not None and b is not None:
                        d.append(a - b)
                if d:
                    paired[k] = {"median_diff": round(st.median(d), 3),
                                 "seeds_positive": sum(1 for x in d if x > 0), "n": len(d)}
            cell["contrast"] = paired
        out[str(t)] = cell
    return out


def selftest() -> int:
    ok = True
    one = np.zeros((16, 16), dtype=bool)
    one[8, 8] = True
    ring = np.zeros((16, 16), dtype=bool)
    ring[6:10, 6:10] = True
    ring[7:9, 7:9] = False
    two = np.zeros((16, 16), dtype=bool)
    two[3, 3] = two[12, 12] = True
    cases = [(one, 1, 0, 1.0), (ring, 1, 1, 0.0), (two, 2, 0, 2.0)]
    for img, b0, b1, chi in cases:
        got_b0, got_chi = beta0(img), euler(img)
        got_b1 = got_b0 - got_chi
        good = (got_b0 == b0 and got_b1 == b1 and abs(got_chi - chi) < 1e-9)
        ok &= good
        print(f"  {'ok ' if good else 'FAIL'} beta0={got_b0} (want {b0}) beta1={got_b1} (want {b1}) chi={got_chi} (want {chi})")
    # период: две точки на противоположных краях — одна компонента через wrap
    wrap = np.zeros((16, 16), dtype=bool)
    wrap[0, 0] = wrap[15, 0] = True   # вертикальные соседи через шов
    good = beta0(wrap) == 1
    ok &= good
    print(f"  {'ok ' if good else 'FAIL'} wrap-connectivity: beta0={beta0(wrap)} (want 1)")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X60 analysis: topology, scale, share")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        print("[betti] selftest")
        return selftest()
    rows = collect()
    if not rows:
        print("[betti] no runs yet — nothing to analyse")
        return 0
    data = {
        "kind": "l1_field_x58_betti",
        "experiment": "X58-lite",
        "command": "python scripts/x58_analyse.py --write",
        "prereg": "reports/2026-11-01-x58-lite-grid128-plan.md",
        "design": {"threshold": THRESHOLD, "connectivity": "4 (periodic wrap)",
                   "euler": "bit-quad, chi = (n1 - n3 - 2*ndiag)/4",
                   "snapshots": list(SNAPSHOTS), "grid": 128, "dx": 0.75},
        "rows": rows,
        "summary": summarise(rows),
        "matched_occupancy": matched_occupancy(),   # вторичный контроль, см. docstring
        "spectrum_seed_mean": spectrum_by_arm(),      # популяционный спектр: на одном срезе шумно
        "threshold_sweep": threshold_sweep(),         # порог 0.15-0.30, тот же вопрос без нового прогона
        "not_claimed": [
            "λ is in grid cells; comparability across grids requires the X58 scaling, not assumed here",
            "β₁ = β₀ − χ assumes β₂ = 0, true for a binary 2-D image but not for a thick 3-D shell",
            "the 8/10 sign rule of the prereg is applied to the contrast block, not to individual rows",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[betti] written: {OUT.name}")
    for t, cell in data["summary"].items():
        line = f"  t={t}: "
        for arm in ("pattern", "homog"):
            if arm in cell:
                c = cell[arm]
                line += f"{arm} beta0={c['beta0']:.1f} beta1={c['beta1']:.1f} share={c['largest_share']:.3f} lam={c['lambda']:.2f} | "
        if "contrast" in cell:
            c = cell["contrast"]
            line += " d_beta0=%+.1f (%d/%d) d_beta1=%+.1f (%d/%d)" % (
                c["beta0"]["median_diff"], c["beta0"]["seeds_positive"], c["beta0"]["n"],
                c["beta1"]["median_diff"], c["beta1"]["seeds_positive"], c["beta1"]["n"])
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
