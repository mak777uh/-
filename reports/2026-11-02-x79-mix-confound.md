# X79: the sweep is confounded by its own construction — mixing two patterns changes the amplitude too

**Date:** 2026-11-02, 05:00 MSK. **Experiment:** X79 (weight sweep of the composite two-scale pattern).
**Preregistration:** `reports/2026-11-02-x79-mix-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x79_mix{025,075}_s171-180.json`, fields `_x79_fields/` (20 snapshots),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x79_mix.json`.

## Result

| mix weight | components | two-peak worlds | ρ₁ / ρ₂ / ρ₃ | λ | half-life |
|---|---|---|---|---|---|
| 0 (single scale, X74) | 47.7 | — | 0.507 / 0.304 / 0.198 | 0.625 | **1.47** |
| **0.25** | 41.5 | **10/10** | 0.553 / 0.174 / 0.089 | 0.401 | **0.76** |
| 0.50 (X78b) | 30.6 | 9/10 | 0.498 / 0.228 / 0.129 | 0.509 | **1.03** |
| **0.75** | 26.4 | **0/10** | 0.512 / 0.209 / 0.121 | 0.486 | **0.96** |

The registered verdict is **inconclusive**: the points are not monotone (0.76, 1.03, 0.96) and the spread is inside the noise the
preregistration declared undetectable (±0.1).

## The design error, which is the actual finding

Mixing two independent patterns does **not** only change which scale dominates. For
`G = (1−w)·G₁ + w·G₂` with independent components of unit variance, the variance of `G` is `(1−w)² + w²`, which is **minimal at
w = 0.5** and equal at 0.25 and 0.75:

| w | variance factor | amplitude factor |
|---|---|---|
| 0.25 | 0.625 | 0.79 |
| 0.50 | 0.500 | 0.71 |
| 0.75 | 0.625 | 0.79 |

So the sweep moved **two** things at once — the dominant scale and the strength of the modulation — and the two are exactly
confounded at 0.5. The non-monotonicity is what that confound predicts, and the two-peak check makes it visible: at w = 0.75 the
8.7-cell component dominates so completely that **no** world shows two peaks (0/10), i.e. that cell is effectively single-scale at a
different wavelength, not two-scale at all.

## What survives from the sweep

- The **w = 0.25** cell is the shortest-lived long-inflow world measured (0.76, against 1.47 for single scale) and it *is* genuinely
  two-peaked (10/10). That is a second independent point in the same direction as X78b, and a stronger effect than X78b's 1.03.
- The w = 0.75 cell is not a two-scale world and cannot be used in the comparison — the manipulation check caught it.

## The fix, stated before the next attempt

Renormalise after mixing: `G ← (G − ½)/σ(w) + ½`, so that every weight delivers the same modulation amplitude and only the spectral
content changes. Then the sweep is a clean one-factor design and the graded-versus-saturating question becomes answerable. That is a
two-line change in the runner, an anchor, and the same sweep.

## Honest status of the question

"Does the effect grow with the weight of the imposed second scale" is **not answered**: the design could not answer it, for a reason
that is now understood and fixable. What the series adds is a second data point in the direction of X78b (0.76 at w = 0.25, with the
two-peak check passing 10/10) and a documented confound in the composite-pattern tool that any future use of it must control.
