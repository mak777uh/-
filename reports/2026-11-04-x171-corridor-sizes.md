# X171 — The corridor at contact is the same at every body size (04.11)

**Question.** X170 turned the crossing from a measured length into a candidate rule: two bodies become one when the field
between them reaches some fraction of the body peak, and the crossing in cells is wherever that fraction is reached. A rule of
that kind must hold at every size. If it only holds at radius 3, it is a description of one arm.

Pre-registration: [`2026-11-04-x171-corridor-sizes-plan.md`](2026-11-04-x171-corridor-sizes-plan.md). Two new arms at the
reference rate `F` = 0.030, each at its own crossing gap: radius 4.5 at surface gap 10 and radius 6 at surface gap 9, fifteen
seeds each (971-985), 2 000 steps, the field dumped every ten steps; the radius-3 arm is X170's, with the same definition.

## Result: 0.48, 0.49, 0.47

| radius | crossing gap | contact events | corridor / peak, median | spread |
|---|---|---|---|---|
| 3 | 10 | 7 of 15 | **0.479** | 0.036 |
| 4.5 | 10 | 4 of 15 | **0.492** | 0.022 |
| 6 | 9 | 7 of 15 | **0.470** | 0.026 |

The difference between the extreme sizes is **0.02** against a pooled within-group spread of **0.040** — the pre-registered
refusal rule fires in the direction that makes the rule real: **the corridor at contact is a size-independent criterion**. A
merge happens at a roughly constant fraction of the body peak regardless of how big the bodies are, at a fixed rate.

All controls held: the peak stayed inside [0.05, 2.0] in every read, the corridor read below the peak in every contact run
(share 1.0), the readout varies (sd 0.040 across the pool), and each arm sits at its own crossing with a fusion share inside
[0.2, 0.8] (0.467, 0.267, 0.467).

## What this makes of X170's description

It makes it a rule with two measured inputs and one measured output:

1. the **fraction** at which a merge happens — 0.47-0.49 of the body peak at `F` = 0.030, flat in size (this item);
2. the **dependence of that fraction on the source** — 0.52 / 0.48 / 0.39 at `F` = 0.026 / 0.030 / 0.036 (X170);
3. the crossing in cells (10 ± 1 across three sizes, X158) is then *where the bridge reaches that fraction*, not an
   independent constant.

The two relations are consistent: a warmer medium builds the bridge faster and more strongly, so the merge happens while the
bridge is less built (lower fraction) and the bodies can be further apart when it does (larger crossing gap). This is the first
sentence in this line that has the form of a mechanism rather than a measurement, and it is testable in exactly one more way —
by predicting the crossing rather than measuring it (next hypotheses below).

## Limits

Contact events are 7, 4 and 7, so each median rests on a handful of runs; the spread is small but the counts are thin. The
radius-4.5 arm fuses only 4 of 15 at its crossing gap, just above the pre-registered floor of 0.2, so its median is the weakest
of the three. And the confound the pre-registration named is real and unresolved: each arm sits at its own crossing gap, so a
size effect and a gap effect cannot be separated by this design — the result says the three *cells* read the same, not that the
corridor is flat over gaps at a fixed size. Separating them needs an arm at a non-crossing gap, where the corridor at contact is
only definable for the subset that still fuses.

## What would kill it

A single arm at another size whose corridor at contact sits outside [0.42, 0.54]; or the same measurement at a fixed size but a
non-crossing gap, if the corridor there reads systematically different — that would show the "criterion" is a per-cell artefact
of the confound. Both are cheap: the first is fifteen runs, the second is already implied by X173's arms.

## Next hypotheses

1. **Predict the crossing instead of measuring it.** With the fraction at 0.47 and the bridge's growth rate known, the crossing
   gap for an unrun size should be computable; the test is a size whose crossing was never run (radius 5.2, where the old
   interpolations disagreed) and a prediction stated before the arm.
2. **Separate size from gap.** Three arms at a fixed radius 3 and gaps 8, 9 and 10, all of which fuse often enough to have
   contact events, would say whether the corridor drifts with the gap at fixed size — the confound this item could not touch.
3. **The fraction is a function of the rate alone.** If 0.47 at `F` = 0.030 is one point on a curve, the same three-size
   measurement at `F` = 0.036 should read about 0.39 at every size; that is a prediction the size-independence claim makes and
   can be checked with thirty runs.
