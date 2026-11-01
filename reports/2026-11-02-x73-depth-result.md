# X73: the size memory decays by about 0.4 per division and is still detectable at the third generation

**Date:** 2026-11-02, 01:05 MSK. **Experiment:** X73 (re-analysis of genealogies already in git; no new runs).
**Preregistration:** `reports/2026-11-02-x73-depth-plan.md`.
**Artifacts:** `morphogenesis/experiments/E09_pond/l1_field_x73_depth.json`; sources `x72c_pattern_s171-180.json`
(primary) and `x70r_pattern_s171-175.json` (replication).

## Result

Spearman(ancestor peak area, descendant peak area) along the genealogy, by number of divisions between them:

| lag | X72c: pairs | X72c: ρ | X72c: shuffle p95 | X70r: pairs | X70r: ρ | X70r: shuffle p95 |
|---|---|---|---|---|---|---|
| 1 (mother–daughter) | 2 140 | **0.475** | 0.033 | 1 034 | **0.512** | 0.055 |
| 2 (grandmother) | 1 968 | **0.204** | 0.037 | 975 | **0.239** | 0.052 |
| 3 (great-grandmother) | 1 776 | **0.072** | 0.040 | 917 | **0.121** | 0.055 |

Register-side controls: at lag 1 the nearest **non-ancestor** gives 0.069 (X72c) and 0.090 (X70r), i.e. the parent's 0.475 and
0.512 are parent-specific, reproducing X70. The registered verdict is **depth ≥ 2** (pooled lag-2 ρ = 0.204 ≥ 0.15, above the
shuffled p95 = 0.037, and ≥ 0.15 in 7 of 10 worlds).

But the interesting number is the shape, not the verdict: the correlation decays by a factor of **0.43** from lag 1 to 2 and
by **0.35** from 2 to 3 — a geometric decay of roughly **0.4 per division**, i.e. a **half-life of about 0.7–0.8 divisions**.
The replication dataset gives the same shape (0.512 → 0.239 → 0.121, factors 0.47 and 0.51), which is why the curve is reported
rather than a single significance claim.

At lag 3 the correlation is small (0.072) but **still above the cross-lineage null** (0.040), and with 1 776 pairs the Fisher
band is about ±0.05, so the residual is real — just barely. Read together with lag 2, the honest statement is: the memory is
one generation deep in practice and measurable three generations deep in principle, decaying exponentially.

## Why the decay is the result

A single-lag measurement can only say "there is a memory". The decay rate says **what kind** of memory: an exponentially
forgetting state, not a copying rule. A copying rule (a genotype) would give a flat curve — 0.45, 0.45, 0.45 — because the
daughter gets the parent's value and the granddaughter gets it again. What we see is what a medium does when each structure is
pulled toward its own preferred scale at every division: the parent's deviation is halved, then quartered, then gone.

That distinction matters for the wider question. "Conditions for life" require some heritable state that survives long enough
for selection to act on it; this medium provides a state with a half-life of less than one generation, which is enough to make
a daughter resemble her mother and not enough to make a lineage accumulate anything.

## Limitations, stated before they are asked

- **Survival bias:** a structure can only have a grand-daughter if it survived two divisions, so lag-2 pairs come from
  structures that lived longer, and longer-lived structures are the larger ones — the decay may be slightly **flattened** by
  this, not steepened.
- **Peak area is a lifetime maximum**, not an instantaneous size, so the ancestor's value may come from after the descendant was
  born. That is a property of the measure inherited from X70 and applies equally at every lag, so it does not bias the slope
  between lags, only the absolute level.
- **One inflow** (`F = 0.035`), one box (96), one threshold (0.2). The half-life is a property of *this* medium point.
- The lag-3 residual (0.072 against 0.040) is the weakest number in the table; treating it as "memory at three generations"
  would be over-reading, and the report does not do that.

## What follows

- The decay rate gives a **falsifiable prediction for any other medium point**: at a different inflow the half-life should
  scale with how strongly the field pulls structures to its preferred size. That is measurable with the data we already have
  across the X71 sweep, if those worlds had \(k\)-generation chains — they do not, so it is a new run if we want it.
- For the "conditions for life" thread the quantitative form is now: **memory half-life ≈ 0.75 division at `F = 0.035`**,
  against a required lifetime for cumulative selection of many generations. The gap is a factor of ten, and it is now a number
  rather than an impression.
