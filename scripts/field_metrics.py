"""field_metrics.py — the measurement code the field line's analyses share.

Why a module. Twelve analysis scripts each carried their own copy of the same three pieces: the angular readout (`q'` and the
symmetry `s`), the per-world half-life from lag correlations, and the partial Spearman. Two of them carried the same defect as well —
a cell was globbed by a single filename prefix, so a cell that is made of two series (X85's eight worlds plus X87's twelve) was
silently read as twelve. `cell_files()` exists so that a cell is described by its **list of prefixes**, which is what the design says
it is.

Nothing here changes a number: the functions are the same arithmetic that was in the scripts, gathered so that the next fix happens
once.

Usage:
    from field_metrics import angular, cell_files, half_life, partial_spearman
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FORCING_Q = 8          # per-axis wavenumber of the 12.0-cell checkerboard; its diagonal is at q*sqrt(2) = 11.3
LAGS = (1, 2, 3)


def cell_files(series, flow: float) -> list[Path]:
    """Every run artifact of one cell, given its series prefixes and its inflow.

    `series` is a prefix or a sequence of prefixes: ('x85', 'x87') for a lattice cell made of both. The flow becomes the three-digit
    tag used in the filenames (`f025`). A cell is a design, not a filename, so this is the only place that decides which files belong
    to it.
    """
    prefixes = (series,) if isinstance(series, str) else tuple(series)
    tag = f"f{int(round(float(flow) * 1000)):03d}"
    return sorted(p for pre in prefixes for p in L1.glob(f"{pre}_{tag}_pattern_s*.json"))


def _power_at(spec: np.ndarray, n: int, ky: int, kx: int, rad: int = 1) -> float:
    total = 0.0
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            total += float(spec[(ky + dy) % n, (kx + dx) % n])
    return total


def angular(v: np.ndarray, forcing_q: int = FORCING_Q, q_max: int = 14) -> dict:
    """Axis-aligned period `q'` and symmetry `s = P_diag/(P_diag+P_axis)` of one field.

    A radial profile cannot separate the forcing line from the morphology (they share a radial bin at |k| = q*sqrt(2)); this reads the
    two by orientation instead. A dead or uniform field returns Nones rather than a number made of numerical noise.
    """
    v = np.asarray(v)
    n = v.shape[0]
    std = float(v.std())
    if std < 0.01:
        return {"q_axis": None, "symmetry": None, "field_std": round(std, 4)}
    spec = np.abs(np.fft.fft2(v - v.mean())) ** 2
    p_diag = sum(_power_at(spec, n, sy * forcing_q, sx * forcing_q) for sy in (1, -1) for sx in (1, -1))
    best_q, best_val = 0, -1.0
    for q in range(4, q_max + 1):
        val = _power_at(spec, n, q, 0) + _power_at(spec, n, 0, q)
        if val > best_val:
            best_q, best_val = q, val
    sym = p_diag / (p_diag + best_val) if (p_diag + best_val) > 0 else None
    return {"q_axis": best_q or None, "symmetry": round(sym, 3) if sym is not None else None, "field_std": round(std, 4)}


def half_life(rhos) -> dict:
    """Per-world lambda and half-life from the lag-1..3 correlations; unfittable when a ratio is not positive."""
    rs = list(rhos)
    if len(rs) != 3 or any(r is None for r in rs):
        return {"lambda": None, "half_life": None, "fittable": False}
    ratios = [x / y for x, y in ((rs[1], rs[0]), (rs[2], rs[1])) if x is not None and y is not None and x > 0 and y > 0]
    if not ratios:
        return {"lambda": None, "half_life": None, "fittable": False}
    lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    return {"lambda": lam, "half_life": math.log(0.5) / math.log(lam) if 0 < lam < 1 else None, "fittable": True}


def partial_spearman(x, y, z) -> float | None:
    """Rank partial correlation of x and y controlling z; None when the sign of a denominator is indeterminate."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from x72c_analyse import spearman  # local import: keeps this module free of import cycles at module load

    rxy, rxz, ryz = spearman(x, y), spearman(x, z), spearman(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = (1 - rxz ** 2) * (1 - ryz ** 2)
    return round((rxy - rxz * ryz) / math.sqrt(den), 3) if den > 0 else None
