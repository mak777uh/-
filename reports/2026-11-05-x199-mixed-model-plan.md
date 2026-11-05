# X199 — a mixed-effects check of the local-inflow reading (05.11) — pre-registration

**Status:** pre-registration, written before any fit. No run of the field series is part of this item: it is an
analysis of committed aggregates and committed compact slices only, zero GPU. The plan is registered here and the
fit is produced by `scripts/x199_mixed_model.py --write` after this file exists.

## Question

X180 (`morphogenesis/experiments/E09_pond/l1_field_x180_dispersion.json`) reads the between-family dispersion of
the crossing with a **fixed-effects** statistic: over the 321 non-saturated runs the pooled point-biserial of
fusion on the midpoint phase is **−0.527**, the mean over cells is **−0.552** and the two-proportion z between the
bottom and top midpoint-G quartiles is **−7.807**; only 1 of 17 cells has its fusing runs at the higher midpoint G.
X183 (`l1_field_x183_local_collapse.json`) reads the same pool as a ladder of AUCs, in which every within-level AUC
of the nominal rate is exactly **0.500** while the local readings separate the levels (F_local_min 0.8656 overall,
0.8951 within).

Both are stored scalars with no run-level data in the aggregate, and both treat the runs of a cell as independent.
X197 (`l1_field_x197_deviance_worlds.json`) then showed that this pool is **258 worlds for 311 mixed runs — 1.205
runs per world**, so about a fifth of the mixed rows are repeats, and that a deviance drop of 20.7 over runs falls
to 14.3 over worlds, i.e. inside X186's own bar of 20.

**The question of this item.** Does the local-inflow association survive when the repeated structure is kept
rather than averaged over: is the slope of fusion on the local inflow still non-zero, and how much of the outcome's
variation is **between** worlds rather than between runs? Two random effects are registered, in the article's own
vocabulary (`articles/030-…md` §4): a **world** is a phase *together with* the arm's geometry, and a **phase class**
is the pair of seeded positions modulo the stripe period of 12 cells, pooled over geometries. Variant A puts a
random intercept on the world; variant B puts one on the phase class.

This is the falsifier `articles/030-…md` §7 item 9 registers: *if a cell's families stop disagreeing once the site
is treated as a random effect, §5.7's between-family noise is the whole story.*

## 1. Manipulation is connected (analysis analogue)

No manipulation is applied; the covariate is read from the committed projection. The analogue of item 1 is that the
covariate **exists and varies** in the committed data, which is checked before the fit:

- `G` is the medium's fixed pattern `G(x,y) = (sin(2·pi·y/12)·cos(2·pi·x/12) + 1)/2`, evaluated at the rounded
  centre of a body exactly as X180 (midpoint) and X183/X197 (colder body) evaluate it;
- the local inflow is `F_local = F·(1 + 0.5·(2G − 1))`, i.e. `F·2G` at `amp = 0.5`;
- observed range in the primary sample: `F_local_min` **0.0130 – 0.0375** (sd 0.0058), `F_local_mid`
  **0.0150 – 0.0516** (sd 0.0076).
- **Registered design fact, checked before the fit:** because `G` has period 12 and the phase is the pair of
  positions modulo 12, `F_local_min` is a deterministic function of (cell, phase) = the world, so it is
  **exactly constant within every multi-run world** (reconnaissance: within-world sd = 0.000000 in all 47
  multi-run worlds). The world-model slope is therefore a **between-world** slope; a within-world slope does not
  exist in this design and is not claimed. `F_local_mid` varies within 4 of the 47 worlds, by at most 0.0113.

## 2. Positive control fires

The association this item re-tests is already published, so the control is a **reproduction**, declared before the
fit at its published sign and order of magnitude:

- control arm: the fixed-effects logistic fit of fusion on the standardised local inflow over the primary sample;
- expected effect: **positive** for `F_local_min` (X183: F_local_min is the best local reading, AUC 0.8656;
  article §5.7: "the informative site is the colder body") and **negative** for `F_local_mid` (X180: pooled
  point-biserial −0.527);
- threshold that counts as "fires": the fixed-effects slope's 95 % interval excludes 0 in the published direction.
- If the control does not fire, the mixed model is not interpreted (refusal rule 5).

## 3. Readout exists and varies

- readout: `fused`, = 1 when the minimum logged component count over the run is 1, exactly X197's definition;
- source field: `series[].1[].length` for the component count, `params.F` for the nominal rate,
  `series[0]` for the seeded geometry;
- observed variance in the primary sample: **135 fused of 311 runs = 0.4341**; across the 258 worlds the outcome
  is 0 in 211, 1 in ?, and mixed in the remainder (the exact split is written into the aggregate).
- the response is therefore neither constant nor saturated.

## 4. Sensitivity arithmetic (written before the criterion)

- baseline (fusion rate of the primary sample) = **0.4341** (135/311);
- between-world sd of the standardised covariate = 1.000 by construction; raw sd 0.0058 (`F_local_min`) /
  0.0076 (`F_local_mid`);
- effect worth detecting = **β = 0.40 log-odds per sd** (odds ratio 1.49);
- clusters available: **258 worlds** (47 with more than one run; sizes 1×211, 2×42, 3×4, 4×1) and
  **143 phase classes** (75 with more than one run; up to 10 runs in one class);
- design effect from 1.205 runs per world ≈ 1 + (1.205 − 1)·ρ ≤ 1.2, so the working standard error of the slope is
  ≈ 1/sqrt(258 · 0.4341 · 0.5659 · 1) · 1.1 ≈ **0.138**;
- clusters needed at α = 0.05 two-sided, power 0.8 = **≈ 258 for β = 0.40** — i.e. this pool is at the bar, and a
  true slope below ≈ 0.39/sd is not separable from zero here. The published fixed-effects slope is 0.59/sd
  (`F_local_min`), above that bar; the midpoint slope is larger and negative.

## 5. Refusal rule

This item is declared worthless, rather than negative, if any of the following holds. The outcome is then written
into the report and into the aggregate's `verdict`, with the counts that show it, and **no fit is interpreted**:

1. **No repeat runs within a world** (no world holds more than one run) → the between-world variance is not
   estimable from committed data; report the limitation instead of fitting.
2. **The fitted random-effect sd is at the boundary** (σ̂ < 1e-4) → the random effect is degenerate, the ICC is
   reported as 0 and the between-world variance is stated as not resolved above zero.
3. **The profile interval for the slope does not close** → report "interval not finite", not a number.
4. **The covariate is constant within every multi-run world** → the fit is reported, but only as a
   between-world slope; any sentence implying a within-world effect is forbidden. (This condition is **met** and
   is therefore a registered limitation of the result, declared in §1 above.)
5. **The positive control of §2 does not fire** → the mixed model is not interpreted.

## Registered model and estimator

Binary outcome `fused` per run; covariate `z = (F_local − mean)/sd` standardised over the analysis sample.

- **Variant A (world).** `logit P(fused_i) = a + b·z_i + u_{w(i)}`, `u_w ~ N(0, σ_w²)`, random intercept per
  **world = (cell, phase)**.
- **Variant B (phase class).** The same with a random intercept per **phase class = the pair of seeded positions
  modulo 12**, pooled over geometries.
- **Estimator.** `statsmodels` is not installed and `scipy` is. The marginal likelihood is integrated by a
  **Laplace approximation over the 1-D random intercept**,
  `L_w = ∫ Π_i p(y_i | a + b z_i + u) φ(u/σ)/σ du ≈ exp(g(û))·sqrt(2π)/sqrt(−g''(û))`, with `û` the mode of the
  integrand; `(a, b, log σ)` are optimised directly with `scipy.optimize.minimize` (Nelder–Mead, restarted from a
  grid). The slope's 95 % interval is a **profile-likelihood** interval (`2·ΔlogL ≤ 3.841`), with a
  **cluster bootstrap over worlds** (400 replicates, resampling clusters with replacement) reported beside it.
- **ICC** = `σ²/(σ² + π²/3)` (latent-scale logistic), i.e. the share of latent-scale variance that is between
  worlds (or between phase classes).
- **Fixed-effects comparison**: the same logistic model with σ = 0, fitted by IRLS, with a Wald interval and its
  binomial deviance, so the fixed-effects number this item re-tests is reproduced in the same code path.

## Criteria (pass/fail, registered before the fit)

| # | criterion | passes if |
|---|---|---|
| C1 | the association survives the world random effect (`F_local_min`) | slope > 0 and its 95 % profile interval excludes 0 |
| C2 | the site carries the dispersion | ICC_world ≥ 0.50 |
| C3 | the clustering does not materially attenuate the slope | \|b_world\| / \|b_FE\| ≥ 0.70 |
| C4 | the phase-class variant behaves as the world variant | σ_phase > 0.001 and its slope's interval excludes 0 |
| C5 | the published midpoint reading is reproduced | slope on `F_local_mid` < 0, interval excludes 0 (in both variants) |

## What would refute it, and what the outcome means

- The falsifier stands (the dispersion is **not** only between-family noise) if C1 passes and C3 passes: the
  association survives clustering and the slope is not an artefact of treating repeated runs as independent.
- The falsifier falls (the dispersion **is** the site, and §5.7's "between-family noise" is the whole story) if
  the slope's interval covers 0 in the world model while the fixed-effects fit excludes it — i.e. the association
  was carried by between-world differences that the random intercept absorbs.
- A large ICC with a surviving slope means the site explains much of the outcome **and** the local inflow still
  has a between-world gradient: both statements, not one.
- **Refuted by construction:** if a later item runs two seeds at the same (cell, phase) — a true clone pair — and
  they disagree, then the "world" unit is wrong and this item's clusters are not clusters. Nothing here can see
  that, because within-world replication exists in only 47 of 258 worlds.

## Design summary

| element | value |
|---|---|
| world and settings | committed `L1_field/*.compact.json`, hetero_amp 0.5, hetero_scale 12, grid 96 |
| arms | none — analysis of existing projections |
| window | series[0] geometry + `min` component count over all logged steps |
| readout | `fused` ∈ {0,1}, base rate 0.4341 |
| seeds | 311 runs in 11 mixed cells (primary); 742 runs in 57 cells (secondary) |
| criterion | C1–C5 above |

## Dataset and exact inclusion rule

1. universe: all `morphogenesis/experiments/L1_field/*.compact.json`;
2. **exclude** files whose stem starts with `x18` or `x19` (X197's guard: those seeds were chosen *by* the inflow
   or the phase in X182/X184/X187 and later arms, so using them to measure the inflow's effect would be circular);
   excluded = 1219 of 2224;
3. **keep** runs whose `series[0]` has **exactly two** components (the two-body crossing table's unit); 742 runs;
   one-component controls (248) and three-component rows are dropped, as in X179;
4. cell = (radius = round(√(area₀/π), 1), gap = round(|centre separation| − 2·radius₀), F = round(F, 3));
   phase = the two bodies' rounded positions modulo 12, sorted; world = (cell, phase);
5. **primary sample** = the runs of the **mixed cells**, i.e. cells whose pooled fusion share is strictly between 0
   and 1 — 311 runs in 11 cells, 258 worlds (X197's own pool, so the two items are comparable);
   **secondary sample** = all 742 two-body runs (57 cells, 593 worlds);
6. covariates, both computed per run from the committed geometry: `F_local_min = F·(1+0.5(2·min(G₀,G₁)−1))`
   (**primary**, X183's best local reading) and `F_local_mid = F·(1+0.5(2·G(midpoint)−1))` (**secondary**,
   X180's own covariate, whose published number is −0.527).

## Status

- [x] 1. connected (covariate exists and varies; range and within-world constancy checked)
- [x] 2. positive control declared (published sign, interval excluding 0 as the bar)
- [x] 3. readout exists and varies (0.4341, 135/311)
- [x] 4. sensitivity computed (β = 0.40/sd at ≈ 258 clusters, power 0.8)
- [x] 5. refusal rule written (5 conditions)

**Registered before the fit.**
