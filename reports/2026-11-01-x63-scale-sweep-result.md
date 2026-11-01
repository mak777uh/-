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

## Addendum, 10:05 — a rate statistic, computed from the same files

If the counter is heavy-tailed, a rate per structure should be steadier than a raw count. Computed from the existing
artifacts, no new runs: divisions per component per 1000 steps, where the component count is the mean over the run's seven
snapshots.

| scale | splits | mean components | per component / 1000 steps | share of seeds above 150 |
|---|---|---|---|---|
| 4 | 20 | 2.14 | 1.46 | 0.2 |
| 6 | 34 | 2.43 | 2.13 | 0.2 |
| 8 | 33 | 3.86 | 1.17 | 0.0 |
| **12** | **308** | 5.43 | **6.94** | **0.8** |
| 16 | 63 | 7.71 | 1.23 | 0.2 |
| **24** | **175** | 4.86 | **4.93** | **0.6** |
| 32 | 113 | 3.29 | 2.90 | 0.2 |

**The verdict does not change.** The rate has the same shape as the count, so the profile is not an artefact of arm size,
and it still has no monotone or single-peaked form: two arms stand out, five do not.

**One observation, explicitly *not* a claim.** The two elevated arms are at 12 and 24 — the pattern wavelength and twice it.
The low arms are at 4, 6, 8, 16 and 32, none of which is a multiple. That would read as a resonance at *integer multiples*
of the pattern scale, and it is exactly the kind of post-hoc pattern I withdrew twenty minutes ago on the strength of two
extra points. It is recorded here as a hypothesis for a pre-registered test (scales 12, 24 against 18 and 36, many more
seeds), not as a finding.
