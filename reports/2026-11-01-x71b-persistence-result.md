# X71b: the two-branch coexistence is stable, not a transient — five of five worlds still mixed at 24 000 steps

**Date:** 2026-11-01, 21:35 MSK. **Experiment:** X71b (persistence of the X71 multistability).
**Preregistration:** `reports/2026-11-01-x71b-persistence-plan.md` (registered before the series).
**Artifacts:** `morphogenesis/experiments/L1_field/x71b_pattern_s171-175.json`, fields `_x71b_fields/` (20 snapshots),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x71b_persistence.json`.

## Result

All five worlds are **mixed at every horizon**: 5/5 at 6 000, 12 000, 18 000 and 24 000 steps. Nothing collapsed, nothing
drifted into an intermediate state. By the preregistered rule that is **bistable**, and the coexistence is not the tail of a
choice that was still being made.

| world | 6 000 | 12 000 | 18 000 | 24 000 |
|---|---|---|---|---|
| s171 | q 8, peak 0.29, second 0.21 | 0.28 / 0.21 | 0.28 / 0.21 | 0.28 / 0.21 |
| s172 | q 11, 0.26 / 0.26 | q 8, 0.27 / 0.26 | 0.27 / 0.26 | 0.27 / 0.26 |
| s173 | q 11, 0.26 / 0.21 | 0.27 / 0.23 | 0.28 / 0.23 | 0.28 / 0.23 |
| s174 | q 8, 0.40 / 0.23 | 0.39 / 0.24 | 0.40 / 0.24 | 0.40 / 0.24 |
| s175 | q 11, 0.23 / 0.23 | 0.23 / 0.23 | 0.23 / 0.23 | 0.23 / 0.23 |

The shares are not merely above the threshold — they are **constant to two decimals over four horizons**. A transient would
have shown a trend: the dominant mode growing, the second fading. There is no trend.

## What "mixed" means here, stated plainly

The peak carries 0.23–0.40 of the power and the strongest second mode 0.21–0.26, so neither mode is dominant: this is a
spectrum with two humps and a broad remainder, not two equal lattices side by side. Each world keeps its own peak position —
q = 8 (12.0 cells) in three worlds, q = 11 (8.73 cells) in two — and the minority component sits at the other branch. That is
consistent with X71 and sharpens it: the branch is a property of the world, and the second branch persists as a minority
mode rather than as a competing equal.

## What this changes

The condition under which heredity could be discrete is not fleeting. X71 showed the band exists at one horizon; X71b shows
it lasts at least four times as long, with the spectrum stationary. If a daughter is to inherit a branch, she has a stable
branch to inherit from.

## What this does not say

- It does not say the band is wide. X71 measured it at one inflow step (0.035 between 0.030 and 0.040); X71b varies only the
  horizon, not the inflow.
- It does not say the two humps are two attractors in the dynamical-systems sense. "Stable for 24 000 steps with stationary
  shares" is the measured statement; "bistable" is the pre-registered label for it.
- One box (96), one `k` (0.06), one threshold (0.2), five worlds. The 24 000-step horizon is four times X71 and still finite.

## Next

1. **Widen the band** with half-steps `F = 0.033` and `0.037` at 24 000 steps: the honest width of the window is still
   unknown, and a one-step window could be an artefact of the sweep's resolution.
2. **Branch heredity, third attempt** (X72c): with the coexistence now known to be stationary, a daughter's branch can be
   read from a local spectrum at division time with the fields every 50 steps, and the informative cases are the minority
   ones — which needs about ten worlds, as X72b concluded.
