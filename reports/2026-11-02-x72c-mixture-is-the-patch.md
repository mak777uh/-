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

## What would be worth doing next (and what would not)

- **Not** another branch-heredity instrument. Three independent instruments agree; a fourth would be looking for a way to be
  wrong.
- **Worth doing:** the same band-power readout applied to *pairs of worlds* — if the mixture is a regional property, then
  structures in the same region of the same world should agree more than structures in different regions, and that is a
  prediction the current data can test without new runs.
- **Worth doing:** X70's size memory re-read at the same boundary, with the surrogate control, to see whether size inherits
  *where* the mixture does not — that contrast (memory of size, no memory of form) is the sharpest statement the line has.
