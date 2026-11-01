# X63: the resonance was my own post-hoc reading, and it did not survive

1 November 2026, 10:00. Twenty runs, four new correlation lengths. Preregistration:
[`2026-11-01-x63-scale-sweep-plan.md`](2026-11-01-x63-scale-sweep-plan.md), committed before the run.

An hour ago X62's prediction failed and I read the three points as a **resonance**: turnover maximal when the environment
varies on the pattern's own scale. That reading was labelled post-hoc. This run was built to test it, with the shape fixed
in advance — and it does not confirm it.

## The profile

| correlation length | divisions (median) | range across seeds |
|---|---|---|
| 4 | 20 | 6 – 267 |
| 6 | 34 | 8 – 260 |
| 8 | 33 | 11 – 139 |
| **12** | **308** | **87 – 554** |
| 16 | 63 | 53 – 244 |
| 24 | 175 | 131 – 182 |
| 32 | 113 | 19 – 164 |

**Pre-declared criterion: unclear.** The resonance required at least one of {8, 16} within a factor of two of 308 (≥ 154)
and both ends below 154. The ends *are* below the bar, but neither 8 (33) nor 16 (63) comes close to it, and the profile
is not monotone either. Three of the four pre-declared outcomes were possible and the answer is the fourth: the shape is
erratic.

## What that means

**The resonance reading is withdrawn.** It was mine, made from three points after the fact, and the fourth and fifth points
do not support it. What remains is a weaker and more honest statement: the three original scales gave 20, 308 and 175, and
adding four more makes the sequence 20, 34, 33, 308, 63, 175, 113 — a set with no describable shape.

**The reason is visible in the ranges.** Within the scale-12 arm the divisions run from 87 to 554 across five seeds; at
scale 4, from 6 to 267. The between-seed spread of this readout is roughly tenfold, larger than any difference between
neighbouring scales. Five seeds cannot resolve a profile when one seed dominates its arm, and the 308 that anchored the
whole story is a median of a distribution whose upper half is a single seed.

That also weakens the X59 dose-response in a way worth stating: its ordering held in 5 of 5 seeds, which is stronger
evidence than a median, but the underlying spread is the same large one.

## What the line should do differently

The divisions counter is a **heavy-tailed** readout: a few runs with a burst of splitting carry the arm. Two options, and
the second is better:

1. more seeds — the honest sample size for this spread is in the tens, not five;
2. a **rate** statistic that is less dominated by bursts — divisions per component per 1000 steps, or the fraction of
   seeds above a fixed threshold — computable from the **existing** artifacts without a new run.

Until then, no shape claim about correlation length should be made, including my own from an hour ago.

## What stands

- The X59 amplitude ordering (308 → 79 → 21, 5/5 seeds) is still the strongest evidence in this thread, and it is
  consistent in sign across every seed.
- The spectrum findings are untouched: they are seed-averaged and their differences are large.
- Only the *shape of the correlation-length profile* is withdrawn.

## Artifacts

`morphogenesis/experiments/L1_field/x63_{s06,s08,s16,s32}_s{171..175}.json`, fields at t = 6000 in `x63_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x63_profile.json` (which includes the X62 anchors), scripts
`scripts/x63_series.py`, `scripts/x63_analyse.py`.
