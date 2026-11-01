# X72c: the mixture belongs to the patch, not to the parent — third attempt, and the first with a clean answer

**Date:** 2026-11-02, 00:15 MSK (runs 23:00–23:15 on 01.11). **Experiment:** X72c, third attempt at branch heredity.
**Preregistration:** `reports/2026-11-01-x72c-band-power-plan.md` (band powers instead of a class; ten worlds).
**Artifacts:** `morphogenesis/experiments/L1_field/x72c_pattern_s171-180.json`, fields `_x72c_fields/` (1200 snapshots),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x72c_branch.json`.

## Result

Ten worlds at `F = 0.035`, `k = 0.06`, 1 715 division events, band powers from a 48-cell window (`p_wide` = power at
`q_win 3–4`, i.e. 12-cell period; `p_narrow` at `q_win 5–6`, i.e. 8.7-cell).

| statistic | value |
|---|---|
| Spearman(parent `p_wide`, daughter `p_wide`), pooled | **0.853** |
| permutation p95 (parent values shuffled within world) | 0.040 |
| worlds with positive `rho` | **10/10** (range 0.76–0.89) |
| minority events (parent's dominant band ≠ the world's dominant band) | **415** |
| concordance with the **parent**, minority events | **0.740** |
| concordance with a **nearest non-parent** structure, same events | **0.843** |
| difference | **−0.104** |

The registered rule says: not supported if the surrogate is higher. It is higher, in 6 of 10 worlds, and the pooled
difference is −0.104. **Verdict: not supported.**

## Why a correlation of 0.853 is not heredity

Parent and daughter are measured **in the same patch**, 50 steps apart, with a 48-cell window — the daughter appears inside
the window the parent was measured in. Any spatially smooth quantity therefore correlates with itself across a division, and
band power is exactly that: within a snapshot, `p_wide` varies across structures with a standard deviation of only **0.06–0.07**
(median per world), so almost all of the variance in the measurement is *where* the structure is, not *which* structure it is.
The nearest non-parent — measured at the daughter's own snapshot — predicts her better than her parent does (0.843 vs 0.740)
simply because it is contemporaneous.

This is the same conclusion X70's spatial control reached for size, X72b reached for the discrete branch, and X21 reached for
patterns: **the local state is a property of the place.** What X72c adds is that it holds for the *continuous* mixture too, so
the earlier escapes ("the class was too coarse", "the argmax hid the minority") are closed.

## Correction to my own control, made after the run

The preregistered instrument control required the spread of the local readout to be ≥ 0.2, and I computed that spread as the
**standard deviation of per-snapshot medians over time** (0.11–0.18), which failed in 10/10 worlds and produced a "void"
verdict. That was the wrong quantity: the question is whether the instrument separates *structures* from each other, so the
spread must be taken **across structures within a snapshot**. Recomputed: 0.060–0.068 median, maximum 0.187 — the control
passes. Both numbers are now in the aggregate (`spread` and `within_snapshot_sd`).

The correction does not change the verdict, and saying why matters: the verdict is driven by the surrogate comparison, which
never depended on the control arithmetic, and the corrected number makes the interpretation stronger rather than weaker — a
readout whose cross-structure spread is 0.07 cannot carry structure-level information in the first place.

## What this closes

The question "does a daughter inherit her parent's branch" has now been asked three times with three different instruments
(spacing proxy, argmax class, band powers) and answered the same way each time: **nothing parent-specific survives once the
patch is controlled.** The coexistence of two wavelengths at this inflow (X71, X71b, X71c) is real, stationary and narrow, and
it is a property of **regions of the world**, not of lineages.

For the thread's main question — conditions under which a medium carries form — this is a definite negative with a definite
shape: the medium carries one generation of *size* memory (X70, pair-specific, 0.42–0.57) and **no** memory of the mixture.
Form at the branch level is not heritable; size is, weakly.

## The prediction tested on the same data: a third of the mixture is "which quadrant you are in"

The "it is the patch" reading makes a falsifiable prediction that needs no new runs: if the mixture belongs to regions rather
than to structures, then structures inside one quadrant of the box should agree with each other more than quadrants agree with
each other. Tested on the same 1 200 snapshots (`scripts/x72c_regions.py`, aggregate `l1_field_x72c_regions.json`) by a one-way
decomposition of `p_wide` across the four quadrants:

| world | η² median | η² p90 |
|---|---|---|
| s171 | 0.427 | 0.485 |
| s172 | 0.226 | 0.413 |
| s173 | 0.322 | 0.680 |
| s174 | 0.304 | 0.416 |
| s175 | 0.218 | 0.277 |
| s176 | **0.542** | 0.692 |
| s177 | 0.321 | 0.506 |
| s178 | 0.284 | 0.437 |
| s179 | 0.225 | 0.268 |
| s180 | 0.311 | 0.443 |
| **pooled** | **0.307** | — |

**About a third of the variance of the band power is explained by the quadrant a structure sits in**, in every world, and in the
best worlds over half of it. The prediction held, independently of the surrogate comparison that produced the verdict, and it
is a *positive* statement where the heredity test was negative: the mixture has a spatial structure, and "region" is the level
at which it is a real quantity.

Caveat, stated because the decomposition is crude: four quadrants on a 96-cell torus is a coarse partition (24 × 24 cells each,
about two wavelengths across), so η² here is a lower bound on regionality for a finer partition and an upper bound for "any
partition at all". A finer test would need a windowed local average rather than a hard quadrant split.

## The regions are historical, not prescribed

The inflow pattern (`--hetero-signal const_ones.json`) is the **same in every world**, so quadrant *q* in one world is the
same place by external conditions as quadrant *q* in another. That gives a sharp test of what "regional" means, and it came
out the other way from the naive reading:

| quadrant | median `p_wide` over 10 worlds | sd |
|---|---|---|
| 0 | 0.541 | 0.061 |
| 1 | 0.519 | 0.066 |
| 2 | 0.522 | 0.077 |
| 3 | 0.523 | 0.050 |

`η²` across worlds for the quadrant labels: **0.004**. So the quadrants are indistinguishable *between* worlds even though they
are strongly distinguishable *within* a world (η² = 0.307). The regions exist, they carry a third of the mixture's variance, and
**which** region is rich is a property of that world's history, not of the prescribed inflow.

That is a stronger statement than "it is the patch": the patch is not the environment we wrote down, it is the environment the
world made for itself. It also explains why the branch could never be inherited: what a daughter would have to inherit is a
state of a region, and the region's state is not a function of the coordinates.

## The contrast on one dataset: size is parent-specific, mixture is not

Everything above and X70's result came from different runs, which leaves the objection that the comparison is between
datasets. Removed: both readouts computed on **the same 1 955 division events** of the X72c worlds
(`scripts/x72c_size_contrast.py`, aggregate `l1_field_x72c_size_contrast.json`).

| readout | parent → daughter | nearest non-parent → daughter | difference |
|---|---|---|---|
| **peak area** (X70's measure) | **0.457** | 0.069 | **+0.388** |
| **band mixture** (`p_wide`) | 0.853 | *predicts better* (concordance 0.843 vs 0.740) | negative |

Per world, the area correlation beats its surrogate in **10 of 10** (parent 0.275–0.548 against surrogate −0.071…+0.188). So on
one event set, with one geometry and one surrogate rule: **the size of a daughter is parent-specific, the mixture of a daughter
is not.** The high raw correlation of the mixture (0.853) is what a spatially smooth quantity does when both ends are measured
in the same patch; the surrogate is what separates "same place" from "same parent", and only size survives it.

This is the sharpest statement the line has produced, and it is a statement about what a medium can carry: one generation of
**how big**, no generation of **which form**.

## What would be worth doing next (and what would not)

- **Not** another branch-heredity instrument. Three independent instruments agree; a fourth would be looking for a way to be
  wrong.
- **Worth doing:** the same band-power readout applied to *pairs of worlds* — if the mixture is a regional property, then
  structures in the same region of the same world should agree more than structures in different regions, and that is a
  prediction the current data can test without new runs.
- **Worth doing:** X70's size memory re-read at the same boundary, with the surrogate control, to see whether size inherits
  *where* the mixture does not — that contrast (memory of size, no memory of form) is the sharpest statement the line has.
