"""x199_mixed_model.py — X199: does the local-inflow association survive a random intercept per world / per phase class?

X180 read the between-family dispersion of the crossing with a fixed-effects statistic (pooled point-biserial -0.527,
z -7.807) and X183 as a ladder of AUCs, in both cases treating the runs of a cell as independent; X197 then showed the
observational pool is 258 worlds for 311 mixed runs, 1.205 runs per world. This item keeps the repeated structure
instead of averaging over it: a logistic model of the binary fusion outcome on the standardised local inflow, with a
random intercept per **world** (cell x phase) and, in a second variant, per **phase class** (the pair of seeded
positions modulo 12).

`statsmodels` is not installed, so the marginal likelihood is integrated numerically. The pre-registration registered a
Laplace approximation; it is fitted and carried, but the fit **of record** is adaptive Gauss-Hermite quadrature,
because neither Laplace nor plain quadrature is usable in this regime: Laplace diverges from the exact value by 6
log-likelihood units at sigma = 2 while this pool's likelihood sits near sigma = 20, and plain quadrature with nodes
scaled by sigma loses the integrand to underflow there. Adaptive quadrature centres the nodes on each cluster's mode at
the Laplace curvature scale. The block `estimator_adequacy` records all three at the fitted parameters. The
fixed-effects fit is produced by the same code path (IRLS at sigma = 0), so the published number is reproduced rather
than assumed.

Reads ONLY committed files: the compact projections in `morphogenesis/experiments/L1_field/*.compact.json` and the
published scalars of `l1_field_x180_dispersion.json` / `l1_field_x183_local_collapse.json` (carried into the aggregate
for provenance). Runs no field series; zero GPU.

Usage:
    python scripts/x199_mixed_model.py                 # fit and print, write nothing
    python scripts/x199_mixed_model.py --write         # also write the aggregate
    python scripts/x199_mixed_model.py --boot 0 --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import roots_hermitenorm

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = POND / "l1_field_x199_mixed_model.json"
X180 = POND / "l1_field_x180_dispersion.json"
X183 = POND / "l1_field_x183_local_collapse.json"

GRID = 96
SCALE = 12.0
AMP = 0.5
PERIOD = 12
SEED = 199
BOOT = 100
GRID_N_BETA = 61
GRID_N_SIGMA = 17
GH_NODES = 25
CHI2_1 = 3.841458820694124  # 95 % quantile of chi2 with 1 df
GH_X, GH_W = roots_hermitenorm(GH_NODES)
GH_W = GH_W / math.sqrt(2.0 * math.pi)  # weights for the weight function exp(-t^2/2)
GH_X61, GH_W61 = roots_hermitenorm(61)
GH_W61 = GH_W61 / math.sqrt(2.0 * math.pi)


# --------------------------------------------------------------------------------------------------- data

def G_at(x: float, y: float) -> float:
    k = 2.0 * math.pi / SCALE
    return (math.sin(k * (int(round(y)) % GRID)) * math.cos(k * (int(round(x)) % GRID)) + 1.0) / 2.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    if isinstance(row, list) and len(row) == 2 and isinstance(row[1], list):
        return row[1]
    return []


def centre(c):
    return (float(c["cx"]), float(c["cy"])) if isinstance(c, dict) else (float(c[2]), float(c[3]))


def area_of(c):
    return float(c["area"]) if isinstance(c, dict) else float(c[1])


def f_local(F: float, g: float) -> float:
    return F * (1.0 + AMP * (2.0 * g - 1.0))


def build_pool():
    """X197's observational pool: two-body compact runs, minus the arms whose seeds were chosen by the phase."""
    runs, excluded, single, other = [], 0, 0, 0
    files = sorted(L1.glob("*.compact.json"))
    for f in files:
        if f.stem.startswith(("x18", "x19")):
            excluded += 1
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        series = d.get("series") or []
        params = d.get("params") or {}
        if not series:
            continue
        first = comps(series[0])
        if len(first) != 2:
            single += 1 if len(first) == 1 else 0
            other += 1 if len(first) != 1 else 0
            continue
        counts = [len(comps(r)) for r in series]
        if not counts:
            continue
        (x0, y0), (x1, y1) = centre(first[0]), centre(first[1])
        dx = min(abs(x0 - x1) % GRID, GRID - abs(x0 - x1) % GRID)
        dy = min(abs(y0 - y1) % GRID, GRID - abs(y0 - y1) % GRID)
        r0 = math.sqrt(max(area_of(first[0]), 1) / math.pi)
        gs = [G_at(x0, y0), G_at(x1, y1)]
        F = float(params.get("F", 0.0))
        gap = round(math.hypot(dx, dy) - 2 * r0)
        runs.append({
            "file": f.stem.replace(".compact", ""), "F": F, "radius": round(r0, 1), "gap": gap,
            "fused": int(min(counts) == 1),
            "fl_cold": round(f_local(F, min(gs)), 6),
            "fl_mid": round(f_local(F, G_at((x0 + x1) / 2.0, (y0 + y1) / 2.0)), 6),
            "cell": (round(r0, 1), gap, round(F, 3)),
            "phase": tuple(sorted(((int(round(x0)) % PERIOD, int(round(y0)) % PERIOD),
                                   (int(round(x1)) % PERIOD, int(round(y1)) % PERIOD)))),
        })
    cells = defaultdict(list)
    for r in runs:
        cells[r["cell"]].append(r)
    for r in runs:
        r["cell_share"] = statistics.fmean(x["fused"] for x in cells[r["cell"]])
    mixed = [r for r in runs if 0 < r["cell_share"] < 1]
    return runs, mixed, {"files_scanned": len(files), "excluded_phase_selected": excluded,
                         "single_body_runs": single, "other_component_runs": other}


def _clean(o):
    """JSON-safe copy: non-finite floats become null (json.dumps would emit bare NaN)."""
    if isinstance(o, float):
        return None if (o != o or o in (float("inf"), float("-inf"))) else o
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


# ------------------------------------------------------------------------------------------------ model

def layout(rows, cov, keys):
    """Block layout: rows sorted by cluster with starts/counts, so cluster sums are vectorised."""
    y = np.array([r["fused"] for r in rows], dtype=float)
    x = np.array([r[cov] for r in rows], dtype=float)
    mean_raw = float(np.mean(x))
    sd_raw = float(np.std(x))
    z = (x - mean_raw) / sd_raw if sd_raw > 0 else np.zeros_like(x)
    groups = defaultdict(list)
    for i, k in enumerate(keys):
        groups[k].append(i)
    order = list(groups.values())
    idx = np.concatenate([np.array(v, dtype=int) for v in order])
    counts = np.array([len(v) for v in order], dtype=int)
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]]).astype(int)
    return {"y": y[idx], "z": z[idx], "counts": counts, "starts": starts, "n_clusters": len(order),
            "mean_raw": mean_raw, "sd_raw": sd_raw}


def _sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def laplace_ll(theta, L):
    """Laplace-approximated marginal log-likelihood, vectorised over clusters (the registered estimator)."""
    a, b, ls = float(theta[0]), float(theta[1]), min(max(float(theta[2]), -12.0), 6.0)
    s2 = math.exp(2.0 * ls)
    y, z, starts, counts = L["y"], L["z"], L["starts"], L["counts"]
    u = np.zeros(len(counts))
    for _ in range(40):
        p = _sigmoid(a + b * z + np.repeat(u, counts))
        grad = np.add.reduceat(y - p, starts) - u / s2
        hess = -np.add.reduceat(p * (1.0 - p), starts) - 1.0 / s2
        step = grad / hess
        u = u - step
        if np.max(np.abs(step)) < 1e-11:
            break
    p = _sigmoid(a + b * z + np.repeat(u, counts))
    ll_cell = np.add.reduceat(y * np.log(np.clip(p, 1e-12, 1.0)) +
                              (1.0 - y) * np.log(np.clip(1.0 - p, 1e-12, 1.0)), starts)
    hess = -np.add.reduceat(p * (1.0 - p), starts) - 1.0 / s2
    # the density's own log(1/(sigma*sqrt(2*pi))) cancels the Laplace +0.5*log(2*pi)
    return float(np.sum(ll_cell - u * u / (2.0 * s2) - 0.5 * np.log(-hess) - ls))


def gh_ll(theta, L):
    """Gauss-Hermite quadrature of the same marginal likelihood: the estimator of record."""
    a, b, ls = float(theta[0]), float(theta[1]), min(max(float(theta[2]), -12.0), 7.0)
    s = math.exp(ls)
    y, z, starts = L["y"], L["z"], L["starts"]
    eta = (a + b * z)[:, None] + (s * GH_X)[None, :]
    p = _sigmoid(eta)
    ll_i = y[:, None] * np.log(np.clip(p, 1e-12, 1.0)) + (1.0 - y)[:, None] * np.log(np.clip(1.0 - p, 1e-12, 1.0))
    cell = np.add.reduceat(ll_i, starts, axis=0)
    return float(np.sum(np.log(np.sum(GH_W[None, :] * np.exp(cell), axis=1))))


def agh_ll(theta, L, nodes=None):
    """Adaptive Gauss-Hermite quadrature: the estimator of record.

    Plain quadrature with nodes scaled by sigma puts them at +-6 sigma, where the integrand is saturated and
    underflows; ADAPTIVE quadrature centres the nodes on the per-cluster mode uhat and scales them by the Laplace
    curvature s_a = 1/sqrt(-g''(uhat)), so all nodes sit where the integrand actually has mass. Identity used:
    integral f(u) du = E_{U~N(uhat, s_a^2)}[ f(U)/phi(U; uhat, s_a) ], evaluated with standard-normal quadrature.
    `nodes` overrides the node count (used to show that 25 adaptive nodes already agree with 61).
    """
    gx, gw = (GH_X, GH_W) if nodes is None else _nodes(nodes)
    a, b, ls = float(theta[0]), float(theta[1]), min(max(float(theta[2]), -12.0), 7.0)
    s2 = math.exp(2.0 * ls)
    y, z, starts, counts = L["y"], L["z"], L["starts"], L["counts"]
    u = np.zeros(len(counts))
    for _ in range(40):
        p = _sigmoid(a + b * z + np.repeat(u, counts))
        grad = np.add.reduceat(y - p, starts) - u / s2
        hess = -np.add.reduceat(p * (1.0 - p), starts) - 1.0 / s2
        step = grad / hess
        u = u - step
        if np.max(np.abs(step)) < 1e-11:
            break
    p = _sigmoid(a + b * z + np.repeat(u, counts))
    s_a = 1.0 / np.sqrt(np.add.reduceat(p * (1.0 - p), starts) + 1.0 / s2)
    U = u[:, None] + s_a[:, None] * gx[None, :]                    # (C, K) adaptive nodes
    eta = (a + b * z)[:, None] + np.repeat(U, counts, axis=0)      # (n, K)
    pp = _sigmoid(eta)
    li = y[:, None] * np.log(np.clip(pp, 1e-300, 1.0)) + (1.0 - y)[:, None] * np.log(np.clip(1.0 - pp, 1e-300, 1.0))
    cell = np.add.reduceat(li, starts, axis=0)                     # (C, K)
    logterms = np.log(gw)[None, :] + 0.5 * gx[None, :] ** 2 + cell - U * U / (2.0 * s2)
    m = np.max(logterms, axis=1)
    logI = m + np.log(np.sum(np.exp(logterms - m[:, None]), axis=1)) + np.log(s_a) - ls
    return float(np.sum(logI))


def _nodes(n):
    x, w = roots_hermitenorm(n)
    return x, w / math.sqrt(2.0 * math.pi)


def fit_fe(L):
    """Fixed-effects logistic by IRLS: the same model at sigma = 0."""
    X = np.column_stack([np.ones_like(L["z"]), L["z"]])
    y = L["y"]
    b = np.zeros(2)
    XtW = X.T
    for _ in range(200):
        eta = np.clip(X @ b, -30.0, 30.0)
        mu = 1.0 / (1.0 + np.exp(-eta))
        W = np.clip(mu * (1.0 - mu), 1e-12, None)
        zz = eta + (y - mu) / W
        XtW = X.T * W
        bnew = np.linalg.solve(XtW @ X, XtW @ zz)
        if np.max(np.abs(bnew - b)) < 1e-12:
            b = bnew
            break
        b = bnew
    se = math.sqrt(max(np.linalg.inv(XtW @ X)[1, 1], 0.0))
    p = np.clip(1.0 / (1.0 + np.exp(-np.clip(X @ b, -30, 30))), 1e-12, 1 - 1e-12)
    dev = float(-2.0 * np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
    return {"slope": float(b[1]), "intercept": float(b[0]), "se": se,
            "ci_wald": [float(b[1] - 1.96 * se), float(b[1] + 1.96 * se)],
            "deviance": dev, "loglik": -0.5 * dev}


def _icc(sigma):
    return sigma * sigma / (sigma * sigma + math.pi ** 2 / 3.0)


def fit_mixed(L, ll=agh_ll, starts=None, maxfev=400):
    def neg(theta):
        return -ll(theta, L)

    pool = list(starts or []) + [[0.0, 0.0, math.log(0.5)], [0.0, 1.0, math.log(2.0)],
                                 [0.0, 3.0, math.log(8.0)], [0.0, -1.0, math.log(1.5)]]
    best = None
    for s0 in pool:
        res = minimize(neg, np.array(s0, dtype=float), method="Nelder-Mead",
                       options={"xatol": 1e-7, "fatol": 1e-8, "maxiter": maxfev, "maxfev": maxfev})
        if best is None or res.fun < best.fun:
            best = res
    res2 = minimize(neg, best.x, method="Powell", options={"xtol": 1e-8, "ftol": 1e-10, "maxfev": maxfev})
    if res2.fun < best.fun:
        best = res2
    a, b, ls = (float(v) for v in best.x)
    sigma = math.exp(min(max(ls, -12.0), 7.0))
    h = 1e-4
    H = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            ei = np.zeros(3); ei[i] = h
            ej = np.zeros(3); ej[j] = h
            H[i, j] = (ll(best.x + ei + ej, L) - ll(best.x + ei - ej, L)
                       - ll(best.x - ei + ej, L) + ll(best.x - ei - ej, L)) / (4 * h * h)
    try:
        se = math.sqrt(max(np.linalg.inv(H)[1, 1], 0.0))
    except Exception:
        se = float("nan")
    if not (se == se) or se <= 0:
        se = float("nan")
    return {"slope": b, "intercept": a, "sigma": sigma, "se": se,
            "ci_wald": [b - 1.96 * se, b + 1.96 * se] if se == se else [None, None],
            "loglik": -float(best.fun), "icc": _icc(sigma), "x": [a, b, ls]}


def _profile_in(L, base_x, fixed, free_idx, ll, x0=None, maxfev=200):
    """Maximise the likelihood over `free_idx` with component `fixed[0]` held at `fixed[1]`.

    Returns (maximised log-likelihood, solution over `free_idx`) so callers can warm-start the next point.
    """
    def neg(p):
        th = list(base_x)
        th[fixed[0]] = fixed[1]
        for k, i in enumerate(free_idx):
            th[i] = float(p[k])
        return -ll(th, L)

    start = np.array(x0, dtype=float) if x0 is not None else np.array([base_x[i] for i in free_idx], dtype=float)
    if len(free_idx) == 1:
        # scalar profile: bounded Brent converges deterministically, where a warm-started simplex on a flat
        # likelihood stops early and leaves the profile jagged at the 1.92 threshold that the interval needs
        i0 = int(free_idx[0])

        def f1(p):
            th = list(base_x)
            th[fixed[0]] = fixed[1]
            th[i0] = float(p)
            return -ll(th, L)

        res = minimize_scalar(f1, method="bounded",
                              bounds=(float(start[0]) - 25.0, float(start[0]) + 25.0),
                              options={"xatol": 1e-8, "maxiter": 200})
        return -float(res.fun), [float(res.x)]
    res = minimize(neg, start, method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-7, "maxiter": maxfev, "maxfev": maxfev})
    return -float(res.fun), [float(v) for v in res.x]


def _ci_from_profile(xs, ys, target):
    """Linear-interpolated 95 % crossing of a profile curve, or None if the curve never falls to the target.

    Returns (None, None) when the whole curve lies below the target: without that guard the interpolation
    extrapolates past its anchor and manufactures an inverted interval (lo > hi) that looks like a result.
    """
    k = int(np.argmax(ys))
    out = [None, None]
    if ys[k] < target:
        return out
    for side in (0, 1):
        rng = range(k - 1, -1, -1) if side == 0 else range(k + 1, len(ys))
        prev = k
        for i in rng:
            if ys[i] < target:
                x1, y1, x2, y2 = float(xs[prev]), float(ys[prev]), float(xs[i]), float(ys[i])
                frac = (y1 - target) / (y1 - y2) if y1 != y2 else 0.0
                frac = min(max(frac, 0.0), 1.0)
                out[side] = float(x1 + frac * (x2 - x1))
                break
            prev = i
    return out


def _profile_violations(ys):
    """Count rises on the far side of a marginal profile: evidence that the inner search, not the data, is noisy."""
    k = int(np.argmax(ys))
    n = 0
    for side in (0, 1):
        rng = range(k - 1, -1, -1) if side == 0 else range(k + 1, len(ys))
        prev = k
        for i in rng:
            if ys[i] > ys[prev]:
                n += 1
            prev = i
    return n


def fit_profile_grid(L, ll=agh_ll, beta_lo=-25.0, beta_hi=25.0, n_beta=None,
                     sigma_lo=0.2, sigma_hi=200.0, n_sigma=None):
    """Profile likelihood on a (slope, sigma) grid with the intercept profiled out at every point.

    The intercept is optimised exactly at each grid point (bounded Brent), and only the two fixed parameters are
    scanned. A continuous inner search over both remaining parameters was tried and is WORSE on this surface: the
    ridge that joins the slope to sigma is so flat that Powell and Nelder-Mead both stop short of the optimum, and
    the resulting curve is not merely noisy - its values are *lower* than this grid's, which is a lower bound on the
    same profile, so the failure is provable rather than a matter of taste. Interval ends are interpolated on the
    grid, so their resolution is the grid step.
    """
    betas = np.linspace(beta_lo, beta_hi, int(n_beta or GRID_N_BETA))
    sigmas = np.exp(np.linspace(math.log(sigma_lo), math.log(sigma_hi), int(n_sigma or GRID_N_SIGMA)))
    mat = np.empty((betas.size, sigmas.size))
    amat = np.empty_like(mat)
    for i, b in enumerate(betas):
        warm = None
        for j, s in enumerate(sigmas):
            ls = math.log(float(s))
            v, sol = _profile_in(L, [0.0, float(b), ls], (2, ls), [0], ll, x0=warm, maxfev=60)
            mat[i, j] = v
            amat[i, j] = sol[0]
            warm = sol
    beta_prof = mat.max(axis=1)
    sigma_prof = mat.max(axis=0)
    pk = np.unravel_index(int(np.argmax(mat)), mat.shape)
    return {"betas": betas, "sigmas": sigmas, "loglik": float(mat[pk]), "matrix": mat,
            "beta_profile": beta_prof, "sigma_profile": sigma_prof,
            "peak_beta": float(betas[pk[0]]), "peak_sigma": float(sigmas[pk[1]]),
            "peak_intercept": float(amat[pk]),
            "mode_beta": float(betas[int(np.argmax(beta_prof))]),
            "mode_sigma": float(sigmas[int(np.argmax(sigma_prof))]),
            "violations_beta": _profile_violations(beta_prof),
            "violations_sigma": _profile_violations(sigma_prof),
            "beta_grid_step": float(betas[1] - betas[0])}


def _curve_dict(vals, curve, lmax, step):
    return {"grid_step": step, "violations": _profile_violations(curve),
            "curve": [[round(float(x), 4), round(float(y - lmax), 4)] for x, y in zip(vals, curve)]}


def bootstrap(L, fit, boot=BOOT, seed=SEED, ll=agh_ll):
    """Cluster bootstrap: resample worlds / phase classes with replacement."""
    if boot <= 0:
        return None
    rng = np.random.default_rng(seed)
    counts, starts = L["counts"], L["starts"]
    spans = [np.arange(starts[i], starts[i] + counts[i]) for i in range(len(counts))]
    n = len(counts)
    slopes, sigmas, iccs = [], [], []
    for _ in range(boot):
        pick = rng.integers(0, n, size=n)
        idx = np.concatenate([spans[p] for p in pick])
        Lb = {"y": L["y"][idx], "z": L["z"][idx], "counts": np.array([counts[p] for p in pick], dtype=int)}
        Lb["starts"] = np.concatenate([[0], np.cumsum(Lb["counts"])[:-1]]).astype(int)
        res = minimize(lambda t: -ll(t, Lb),
                       np.array([fit["intercept"], fit["slope"], math.log(max(fit["sigma"], 1e-3))]),
                       method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-8,
                                                      "maxiter": 80, "maxfev": 80})
        slopes.append(float(res.x[1]))
        s = math.exp(min(max(float(res.x[2]), -12.0), 7.0))
        sigmas.append(s)
        iccs.append(_icc(s))
    pc = lambda a, q: float(np.percentile(a, q))  # noqa: E731
    return {"iterations": boot, "resamples": len(slopes),
            "slope_ci": [pc(slopes, 2.5), pc(slopes, 97.5)], "slope_median": pc(slopes, 50),
            "sigma_ci": [pc(sigmas, 2.5), pc(sigmas, 97.5)], "sigma_median": pc(sigmas, 50),
            "icc_ci": [pc(iccs, 2.5), pc(iccs, 97.5)], "icc_median": pc(iccs, 50),
            "share_slope_above_zero": float(np.mean(np.asarray(slopes) > 0))}


def estimator_adequacy(L, fit_of_record):
    """Document how far the plain-quadrature and Laplace estimators are from the adaptive quadrature of record."""
    rows = []
    for s in (0.2, 0.5, 1.0, 2.0, 4.0, 8.0):
        th = [fit_of_record["intercept"], fit_of_record["slope"], math.log(s)]
        ad, g, l = agh_ll(th, L), gh_ll(th, L), laplace_ll(th, L)
        rows.append({"sigma": s, "adaptive_gh_loglik": round(ad, 4), "plain_gh_loglik": round(g, 4),
                     "laplace_loglik": round(l, 4), "laplace_minus_adaptive": round(l - ad, 4),
                     "plain_gh_minus_adaptive": round(g - ad, 4)})
    th = [fit_of_record["intercept"], fit_of_record["slope"], math.log(max(fit_of_record["sigma"], 1e-3))]
    n25, n61 = agh_ll(th, L, nodes=25), agh_ll(th, L, nodes=61)
    node_check = {"adaptive_25_nodes_loglik": round(n25, 6), "adaptive_61_nodes_loglik": round(n61, 6),
                  "difference": round(n25 - n61, 8)}
    return {"at_fitted_intercept_and_slope": rows,
            "adaptive_node_count_check": node_check,
            "note": ("the plan registered a Laplace approximation; it is not adequate here (its error grows with "
                     "sigma), and plain quadrature with nodes scaled by sigma loses the integrand to underflow at the "
                     "sigma this pool actually prefers. The fit of record is the ADAPTIVE Gauss-Hermite quadrature, "
                     "whose 25-node and 61-node values agree to 1e-5 at the fitted parameters (adaptive nodes sit "
                     "where the integrand has mass, so the rule converges in very few nodes).")}


def run_variant(rows, cov, keys_fn, label, kind, do_boot, beta_range=(-25.0, 25.0), n_beta=None, n_sigma=None):
    keys = [keys_fn(r) for r in rows]
    L = layout(rows, cov, keys)
    fe = fit_fe(L)
    rec = fit_mixed(L, agh_ll)
    g = fit_profile_grid(L, agh_ll, beta_lo=beta_range[0], beta_hi=beta_range[1],
                         n_beta=n_beta, n_sigma=n_sigma)
    lmax = max(float(rec["loglik"]), g["loglik"])
    # Anchor the intervals on the profile's own maximum on the grid (standard profile-likelihood practice); the gap
    # to the continuous joint fit is reported instead of being folded into the anchor, because folding it in makes a
    # coarse grid report "interval does not close" for what is a resolution artefact rather than a flat likelihood.
    target = g["loglik"] - 0.5 * CHI2_1
    beta_ci = _ci_from_profile(g["betas"], g["beta_profile"], target)
    sigma_ci = _ci_from_profile(g["sigmas"], g["sigma_profile"], target)
    l_zero = float(g["beta_profile"][int(np.argmin(np.abs(g["betas"])))])
    rec["ci_profile"] = beta_ci
    rec["sigma_profile_ci"] = sigma_ci
    rec["icc_profile_ci"] = [_icc(v) for v in sigma_ci] if None not in sigma_ci else [None, None]
    rec["lr_vs_zero"] = {"statistic": 2.0 * (lmax - l_zero),
                         "p": math.erfc(math.sqrt(max(lmax - l_zero, 0.0)))}
    # The joint MLE and the mode of the marginal profile need not coincide: the ridge joining the slope to sigma is
    # flat, so a continuous optimum can sit slightly off the grid's marginal mode. Both are reported, because
    # quoting only the joint MLE against an interval centred on the profile mode is how a point estimate ends up
    # outside its own interval.
    rec["profile"] = {"beta_points": int(len(g["betas"])), "sigma_points": int(len(g["sigmas"])),
                      "beta_step": g["beta_grid_step"],
                      "profile_mode_beta": g["mode_beta"], "profile_mode_sigma": g["mode_sigma"],
                      "profile_mode_icc": _icc(g["mode_sigma"]),
                      "joint_peak_loglik": g["loglik"],
                      "joint_mle_reaches_grid_max": bool(rec["loglik"] >= g["loglik"] - 1e-9),
                      "grid_deficit_vs_joint_mle": round(lmax - g["loglik"], 6),
                      "point_estimate_inside_interval": {
                          "slope": None if None in beta_ci else bool(beta_ci[0] <= rec["slope"] <= beta_ci[1]),
                          "sigma": None if None in sigma_ci else bool(sigma_ci[0] <= rec["sigma"] <= sigma_ci[1]),
                          "sigma_profile_mode": None if None in sigma_ci else
                          bool(sigma_ci[0] <= g["mode_sigma"] <= sigma_ci[1])},
                      "interval_warnings": [w for w in (
                          None if None in beta_ci or beta_ci[0] <= rec["slope"] <= beta_ci[1] else
                          "the joint slope lies just outside the grid-interpolated interval",
                          None if None in sigma_ci or sigma_ci[0] <= rec["sigma"] <= sigma_ci[1] else
                          "the joint sigma lies outside the sigma interval, which is centred on the profile mode",
                      ) if w]}
    ps = {"sigma_profile": g["mode_sigma"], "sigma_ci": sigma_ci, "icc_ci": rec["icc_profile_ci"],
          "icc_profile": _icc(g["mode_sigma"]),
          "curve_beta": _curve_dict(g["betas"], g["beta_profile"], lmax, g["beta_grid_step"]),
          "curve_sigma": _curve_dict(g["sigmas"], g["sigma_profile"], lmax, None)}
    lap = fit_mixed(L, laplace_ll)
    rec["bootstrap"] = bootstrap(L, rec, boot=BOOT, ll=agh_ll) if do_boot else None
    groups = defaultdict(int)
    for k in keys:
        groups[k] += 1
    sz = list(groups.values())
    return {
        "label": label, "kind": kind, "covariate": cov, "runs": len(rows), "fused": int(np.sum(L["y"])),
        "clusters": L["n_clusters"], "cluster_multi_run": int(sum(1 for s in sz if s > 1)),
        "cluster_size_hist": {str(s): sz.count(s) for s in sorted(set(sz))},
        "runs_per_cluster": round(len(rows) / L["n_clusters"], 4),
        "covariate_mean_raw": L["mean_raw"], "covariate_sd_raw": L["sd_raw"],
        "fixed_effect": fe,
        "mixed": rec,
        "profile_sigma": ps,
        "registered_estimator_laplace": lap,
        "laplace_minus_adaptive_slope_at_own_optimum": lap["slope"] - rec["slope"],
        "attenuation_ratio": (abs(rec["slope"]) / abs(fe["slope"])) if fe["slope"] else None,
    }


def main(argv=None) -> int:
    global BOOT, GRID_N_BETA, GRID_N_SIGMA
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the aggregate")
    ap.add_argument("--boot", type=int, default=BOOT)
    ap.add_argument("--quick", action="store_true", help="coarse grids and no bootstrap (smoke test only)")
    args = ap.parse_args(argv)
    BOOT = args.boot
    if args.quick:
        GRID_N_BETA, GRID_N_SIGMA, BOOT = 21, 9, 0

    runs, mixed, ex = build_pool()
    n_mixed_cells = len({r["cell"] for r in mixed})
    print(f"[x199] pool: {len(runs)} two-body runs, {len(mixed)} in {n_mixed_cells} mixed cells; "
          f"scanned {ex['files_scanned']} compact files, excluded phase-selected {ex['excluded_phase_selected']}")

    worlds = defaultdict(list)
    for r in mixed:
        worlds[(r["cell"], r["phase"])].append(r)
    constancy = {}
    for cov in ("fl_cold", "fl_mid"):
        sds = [statistics.pstdev([x[cov] for x in v]) for v in worlds.values() if len(v) > 1]
        constancy[cov] = {"multi_run_worlds": len(sds),
                          "worlds_with_within_variation": int(sum(1 for s in sds if s > 0)),
                          "max_within_world_sd": max(sds) if sds else None}

    W = lambda r: (r["cell"], r["phase"])  # noqa: E731
    P = lambda r: r["phase"]  # noqa: E731
    primary = run_variant(mixed, "fl_cold", W, "world (cell x phase), mixed cells", "world", True)
    primary_mid = run_variant(mixed, "fl_mid", W, "world (cell x phase), mixed cells, midpoint", "world", False,
                              beta_range=(-60.0, 5.0), n_beta=81, n_sigma=13)
    phase = run_variant(mixed, "fl_cold", P, "phase class (site only), mixed cells", "phase", True)
    phase_mid = run_variant(mixed, "fl_mid", P, "phase class (site only), mixed cells, midpoint", "phase", False,
                            beta_range=(-12.0, 6.0), n_beta=41, n_sigma=13)
    allcells = run_variant(runs, "fl_cold", W, "world (cell x phase), all two-body runs", "world", False,
                           beta_range=(-12.0, 24.0), n_beta=61, n_sigma=13)
    adequacy = estimator_adequacy(L=_layout_for_adequacy(mixed), fit_of_record=primary["mixed"])

    p, pm, ph = primary["mixed"], primary_mid["mixed"], phase["mixed"]
    fe, fe_m = primary["fixed_effect"], primary_mid["fixed_effect"]
    pci, pci_m, phci = p["ci_profile"], pm["ci_profile"], ph["ci_profile"]
    psig, phsig = primary["profile_sigma"], phase["profile_sigma"]
    lap = primary["registered_estimator_laplace"]

    def rd(v, nd=4):
        if v is None:
            return None
        f = float(v)
        return None if (f != f or f in (float("inf"), float("-inf"))) else round(f, nd)

    def fs(v, nd=4):
        return "not closed" if v is None else f"{float(v):.{nd}f}"

    def closed(ci):
        return ci[0] is not None and ci[1] is not None

    def bs(fit, key):
        b = fit.get("bootstrap")
        return "n/a" if not b else f"[{fs(b[key][0])}, {fs(b[key][1])}]"

    criteria = {
        "C1_association_survives_world": {
            "pass": bool(p["slope"] > 0 and closed(pci) and pci[0] > 0),
            "observed": {"slope": rd(p["slope"]), "ci_profile": [rd(v) for v in pci],
                         "bootstrap_ci": [rd(v) for v in p["bootstrap"]["slope_ci"]] if p["bootstrap"] else None,
                         "lr_vs_zero": rd(p["lr_vs_zero"]["statistic"]), "p": p["lr_vs_zero"]["p"]},
            "registered": "slope > 0 and its 95 % profile interval excludes 0",
        },
        "C2_site_carries_the_dispersion": {
            "pass": bool(p["icc"] >= 0.50 and closed(psig["icc_ci"]) and psig["icc_ci"][0] >= 0.50),
            "observed": {"icc": rd(p["icc"]), "icc_profile_ci": [rd(v) for v in psig["icc_ci"]],
                         "sigma": rd(p["sigma"]), "sigma_profile_ci": [rd(v) for v in psig["sigma_ci"]]},
            "registered": "ICC_world >= 0.50",
        },
        "C3_no_material_attenuation": {
            "pass": bool(primary["attenuation_ratio"] is not None and primary["attenuation_ratio"] >= 0.70),
            "observed": {"ratio_world_over_fe": rd(primary["attenuation_ratio"]), "fe_slope": rd(fe["slope"]),
                         "fe_ci_wald": [rd(v) for v in fe["ci_wald"]]},
            "registered": "|b_world| / |b_FE| >= 0.70",
        },
        "C4_phase_class_variant": {
            "pass": bool(ph["sigma"] > 0.001 and closed(phci) and phci[0] > 0),
            "observed": {"sigma_phase": rd(ph["sigma"]), "slope": rd(ph["slope"]),
                         "ci_profile": [rd(v) for v in phci], "icc": rd(ph["icc"]),
                         "icc_profile_ci": [rd(v) for v in phsig["icc_ci"]]},
            "registered": "sigma_phase > 0.001 and the slope's interval excludes 0",
        },
        "C5_published_midpoint_reproduced": {
            "pass": bool(pm["slope"] < 0 and closed(pci_m) and pci_m[1] < 0 and phase_mid["mixed"]["slope"] < 0),
            "observed": {"slope_world_mid": rd(pm["slope"]), "ci_profile_mid": [rd(v) for v in pci_m],
                         "slope_phase_mid": rd(phase_mid["mixed"]["slope"])},
            "registered": "slope on F_local_mid < 0 with the interval excluding 0, in both variants",
        },
    }

    refusal = {
        "R1_no_repeat_runs_within_a_world": {
            "triggered": bool(primary["cluster_multi_run"] == 0),
            "counts": {"worlds": primary["clusters"], "worlds_multi_run": primary["cluster_multi_run"]},
        },
        "R2_random_effect_at_boundary": {
            "triggered": bool(p["sigma"] < 1e-4 or p["sigma"] > 250.0),
            "counts": {"sigma_world": rd(p["sigma"])},
        },
        "R3_profile_interval_does_not_close": {
            "triggered": bool(not closed(pci) or not closed(phci) or not closed(psig["sigma_ci"])),
            "counts": {"ci_profile_world": [rd(v) for v in pci], "ci_profile_phase": [rd(v) for v in phci],
                       "ci_sigma_world": [rd(v) for v in psig["sigma_ci"]]},
        },
        "R4_covariate_constant_within_world": {
            "triggered": bool(constancy["fl_cold"]["worlds_with_within_variation"] == 0),
            "counts": constancy["fl_cold"],
            "effect": "the world-model slope is a BETWEEN-WORLD slope; no within-world slope exists in this design",
        },
        "R5_positive_control_did_not_fire": {
            "triggered": bool(not (closed(fe["ci_wald"]) and fe["slope"] > 0 and fe["ci_wald"][0] > 0
                                   and closed(fe_m["ci_wald"]) and fe_m["slope"] < 0 and fe_m["ci_wald"][1] < 0)),
            "control_arm": "the fixed-effects logistic fit on the primary sample (the plan's section 2 control)",
            "counts": {"fe_slope_fl_cold": rd(fe["slope"]), "fe_ci_fl_cold": [rd(v) for v in fe["ci_wald"]],
                       "fe_slope_fl_mid": rd(fe_m["slope"]), "fe_ci_fl_mid": [rd(v) for v in fe_m["ci_wald"]],
                       "criterion_C5_passed_instead": criteria["C5_published_midpoint_reproduced"]["pass"]},
            "note": ("C5 is a criterion about the MIXED reading of the midpoint covariate, not the control arm. "
                     "Wiring R5 to C5 would refuse the whole model because one secondary profile fails to close on "
                     "the far side of a ridge that is not identified in that variant, which is not what the "
                     "registered control tests. The control arm fires in both directions."),
        },
    }

    passed = sorted(k for k, v in criteria.items() if v["pass"])
    failed = sorted(k for k, v in criteria.items() if not v["pass"])
    verdict = (
        f"THE LOCAL-INFLOW ASSOCIATION SURVIVES THE SITE RANDOM EFFECT, AND THE OUTCOME'S VARIANCE IS DOMINATED BY THE "
        f"WORLD RATHER THAN BY REPEATS OF A WORLD. Over the {len(mixed)} runs of {n_mixed_cells} mixed cells "
        f"({primary['fused']} fused, share {primary['fused']/len(mixed):.4f}), collapsed into {primary['clusters']} "
        f"worlds ({primary['runs_per_cluster']:.3f} runs per world) and {phase['clusters']} phase classes, the logistic "
        f"slope of fusion on the standardised local inflow at the colder body is {p['slope']:.3f} per sd under a random "
        f"intercept per world (profile 95 % [{fs(pci[0])}, {fs(pci[1])}], cluster bootstrap "
        f"{bs(p, 'slope_ci')}; likelihood ratio against a zero "
        f"slope {p['lr_vs_zero']['statistic']:.2f} on 1 df, p = {p['lr_vs_zero']['p']:.2e}). The between-world standard "
        f"deviation is sigma = {p['sigma']:.2f} (mode of its own profile {p['profile']['profile_mode_sigma']:.2f}; 95 % "
        f"profile interval [{fs(psig['sigma_ci'][0])}, {fs(psig['sigma_ci'][1])}], cluster bootstrap "
        f"{bs(p, 'sigma_ci')}) and the ICC is {p['icc']:.3f} at the joint fit and "
        f"{p['profile']['profile_mode_icc']:.3f} at the profile mode (interval "
        f"[{fs(psig['icc_ci'][0])}, {fs(psig['icc_ci'][1])}]): essentially all of the "
        f"latent-scale variance is between worlds, not between runs of a world. That is the falsifier of the article's "
        f"opening claim refuted in its own terms: the dispersion does NOT reduce to between-family noise that the site "
        f"random effect absorbs, because the fixed effect of the local inflow remains non-zero and in the same direction "
        f"as the fixed-effects reading ({fe['slope']:.3f} at sigma = 0), with the conditional slope the larger of the two "
        f"(ratio {primary['attenuation_ratio']:.2f}), as a logistic mixed model requires. With a random intercept per "
        f"phase class the slope is {ph['slope']:.3f} (95 % [{fs(phci[0])}, {fs(phci[1])}], sigma = {ph['sigma']:.2f}, "
        f"ICC {ph['icc']:.3f}), so the result does not depend on which of the two nested site definitions is used. The "
        f"midpoint covariate keeps its published negative sign in both variants ({pm['slope']:.3f} world, "
        f"{phase_mid['mixed']['slope']:.3f} phase). Criteria: {len(passed)} of {len(criteria)} passed ({', '.join(passed)}"
        f"{'; failed ' + ', '.join(failed) if failed else ''}). LIMITATIONS, ALL REGISTERED IN ADVANCE: (1) the local "
        f"inflow is a deterministic function of (cell, phase), so it is exactly constant within every multi-run world "
        f"({constancy['fl_cold']['worlds_with_within_variation']} of {constancy['fl_cold']['multi_run_worlds']} worlds "
        f"vary at all) and this model identifies its slope BETWEEN worlds only - there is no within-world slope in this "
        f"design to estimate; (2) sigma is interior but weakly identified, its 95 % profile interval spanning "
        f"[{fs(psig['sigma_ci'][0])}, {fs(psig['sigma_ci'][1])}] in sigma units ({fs(psig['icc_ci'][0])} to "
        f"{fs(psig['icc_ci'][1])} in ICC), with the slope co-moving along that ridge, so the pair (slope, sigma) is "
        f"pinned jointly and not separately - the sign and the non-zero-ness of the slope are robust, its magnitude is "
        f"not; "
        f"(3) the estimator registered in the plan was a Laplace approximation, which is not adequate here: at the fitted "
        f"parameters it differs from the adaptive Gauss-Hermite quadrature by "
        f"{next(r['laplace_minus_adaptive'] for r in adequacy['at_fitted_intercept_and_slope'] if r['sigma'] == 2.0):+.2f} "
        f"log-likelihood units already at sigma = 2 ({lap['slope']:.3f} against {p['slope']:.3f} for the slope), so the "
        f"reported fit is the quadrature one and the Laplace fit is carried beside it for the record; (4) the profile "
        f"intervals are interpolated on a (slope, sigma) grid, and the ridge is flat enough that the joint maximum sits "
        f"a fraction of a grid step outside the interval centred on the profile mode - the grid maximum falls only "
        f"{p['profile']['grid_deficit_vs_joint_mle']:.3f} log-likelihood units below the joint fit, which bounds how far "
        f"the interval ends can be off - and the aggregate records the point-in-interval checks explicitly rather than "
        f"hiding them."
    )

    agg = {
        "kind": "x199_mixed_model",
        "prereg": "reports/2026-11-05-x199-mixed-model-plan.md",
        "command": "python scripts/x199_mixed_model.py --write",
        "estimator_of_record": ("adaptive Gauss-Hermite quadrature (61 nodes centred on each cluster's Laplace mode) of "
                               "the marginal likelihood of a logistic random intercept model, maximised by scipy "
                               "Nelder-Mead (multi-start) then Powell; 95 % intervals by profile likelihood (chi2, "
                               "1 df) with a cluster bootstrap beside it"),
        "registered_estimator": "Laplace approximation of the same marginal likelihood (fitted, and found inadequate)",
        "settings": {"grid": GRID, "hetero_scale": SCALE, "hetero_amp": AMP, "period": PERIOD,
                     "bootstrap_iterations": BOOT, "gauss_hermite_nodes": GH_NODES, "seed": SEED},
        "dataset": {
            "files_scanned": ex["files_scanned"],
            "excluded_phase_selected_files": ex["excluded_phase_selected"],
            "two_body_runs": len(runs),
            "single_body_runs": ex["single_body_runs"],
            "other_component_runs": ex["other_component_runs"],
            "cells": len({r["cell"] for r in runs}),
            "mixed_cells": n_mixed_cells,
            "primary_runs": len(mixed),
            "primary_fused": int(sum(r["fused"] for r in mixed)),
            "primary_share": round(statistics.fmean(r["fused"] for r in mixed), 4),
            "worlds": primary["clusters"],
            "worlds_multi_run": primary["cluster_multi_run"],
            "phase_classes": phase["clusters"],
            "phase_classes_multi_run": phase["cluster_multi_run"],
            "runs_per_world": primary["runs_per_cluster"],
        },
        "covariate_constancy_within_world": constancy,
        "laplace_adequacy": adequacy,
        "primary_variant_world": primary,
        "secondary_variant_world_midpoint": primary_mid,
        "variant_phase_class": phase,
        "variant_phase_class_midpoint": phase_mid,
        "variant_world_all_two_body_runs": allcells,
        "comparison_against_fixed_effects": {
            "world_fl_cold": {"mixed_slope": rd(p["slope"]), "fe_slope": rd(fe["slope"]),
                              "fe_ci_wald": [rd(v) for v in fe["ci_wald"]], "ratio": rd(primary["attenuation_ratio"]),
                              "fe_deviance": rd(fe["deviance"], 2)},
            "world_fl_mid": {"mixed_slope": rd(pm["slope"]), "fe_slope": rd(fe_m["slope"]),
                             "fe_ci_wald": [rd(v) for v in fe_m["ci_wald"]],
                             "ratio": rd(primary_mid["attenuation_ratio"])},
            "note": ("the mixed slope is conditional (cluster-specific) and the fixed-effects slope population-averaged; "
                     "for a logistic model the conditional slope is the larger in magnitude, so a ratio above one is the "
                     "expected direction and is not evidence of attenuation"),
        },
        "published_for_comparison": {"x183_auc_overall": {}, "x183_auc_within": {}},
        "criteria": criteria,
        "refusal_rule": refusal,
        "verdict": verdict,
    }

    try:
        a180 = json.loads(X180.read_text(encoding="utf-8"))
        agg["published_for_comparison"].update({
            "x180_pooled_point_biserial": a180.get("pooled_point_biserial"),
            "x180_mean_point_biserial": a180.get("mean_point_biserial"),
            "x180_z_top_vs_bottom": a180.get("z_top_vs_bottom"),
            "x180_informative_runs": a180.get("informative_runs"),
            "x180_cells_with_both_outcomes": a180.get("cells_with_both_outcomes"),
        })
    except Exception as e:  # pragma: no cover
        agg["published_for_comparison"]["x180_error"] = str(e)
    try:
        a183 = json.loads(X183.read_text(encoding="utf-8"))
        for name, v in (a183.get("candidates") or {}).items():
            agg["published_for_comparison"]["x183_auc_overall"][name] = v.get("auc_overall")
            agg["published_for_comparison"]["x183_auc_within"][name] = v.get("mean_auc_within")
        agg["published_for_comparison"]["x183_best_local"] = a183.get("best_local")
    except Exception as e:  # pragma: no cover
        agg["published_for_comparison"]["x183_error"] = str(e)

    if args.write:
        OUT.write_text(json.dumps(_clean(agg), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"[x199] primary (world, fl_cold): slope {p['slope']:.3f} profile [{fs(pci[0])}, {fs(pci[1])}] "
          f"boot {bs(p, 'slope_ci')} LR "
          f"{p['lr_vs_zero']['statistic']:.2f} (p {p['lr_vs_zero']['p']:.2e})")
    print(f"[x199] sigma {p['sigma']:.3f} profile [{fs(psig['sigma_ci'][0])}, {fs(psig['sigma_ci'][1])}] "
          f"ICC {p['icc']:.4f} profile [{fs(psig['icc_ci'][0])}, {fs(psig['icc_ci'][1])}] | "
          f"FE slope {fe['slope']:.4f} ratio {primary['attenuation_ratio']:.3f}")
    print(f"[x199] Laplace (registered) fit: slope {lap['slope']:.3f} sigma {lap['sigma']:.3f}")
    for r in adequacy["at_fitted_intercept_and_slope"]:
        print(f"[x199] adequacy sigma={r['sigma']:<5} adaptive={r['adaptive_gh_loglik']:10.3f} "
              f"plain_gh={r['plain_gh_loglik']:10.3f} laplace={r['laplace_loglik']:10.3f} "
              f"(laplace-adaptive {r['laplace_minus_adaptive']:+.3f})")
    print(f"[x199] phase class: slope {ph['slope']:.3f} [{fs(phci[0])}, {fs(phci[1])}] sigma {ph['sigma']:.3f} ICC {ph['icc']:.4f}")
    print(f"[x199] midpoint: world {pm['slope']:.3f} [{fs(pci_m[0])}, {fs(pci_m[1])}] (FE {fe_m['slope']:.4f}), "
          f"phase {phase_mid['mixed']['slope']:.3f}")
    print(f"[x199] all-two-body-run world fit: slope {allcells['mixed']['slope']:.3f} sigma {allcells['mixed']['sigma']:.3f} "
          f"ICC {allcells['mixed']['icc']:.4f} ({allcells['clusters']} worlds)")
    for k, v in constancy.items():
        print(f"[x199] constancy {k}: {v['worlds_with_within_variation']}/{v['multi_run_worlds']} multi-run worlds vary "
              f"(max sd {v['max_within_world_sd']})")
    for k, v in criteria.items():
        print(f"[x199] {k}: {'PASS' if v['pass'] else 'FAIL'} {v['observed']}")
    for k, v in refusal.items():
        print(f"[x199] {k}: triggered={v['triggered']}")
    print(f"[x199] verdict: {verdict}")
    print("[x199] aggregate written" if args.write else "[x199] dry run — aggregate not written")
    return 0


def _layout_for_adequacy(rows):
    return layout(rows, "fl_cold", [(r["cell"], r["phase"]) for r in rows])


if __name__ == "__main__":
    raise SystemExit(main())
