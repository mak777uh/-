# X59: transmission obeys the amplitude of the inflow, fifteen-fold

1 November 2026, 07:55. Fifteen runs, three amplitudes, five paired seeds. Preregistration:
[`2026-11-01-x59-amplitude-dose-plan.md`](2026-11-01-x59-amplitude-dose-plan.md), committed before the run.

## Result

Everything is fixed except one number — the amplitude of the inflow modulation. The trait channel, the mutation, the
seeds, the grid, the duration are identical across the three arms.

| amplitude | divisions per run | parent–child pairs | `r` | mean composition | spectral entropy at t = 6000 | peak mode |
|---|---|---|---|---|---|---|
| 0.50 | **308** | 682 | 0.97 | 1.89 | 2.27 / 2.48 | q = 1, share 0.25 |
| 0.25 | **79** | 167 | 0.89 | 1.28 | 2.25 / 2.48 | q = 8, share 0.19 |
| 0.10 | **21** | 43 | 0.80 | 1.07 | **1.75 / 2.48** | **q = 8, share 0.39** |

**All four pre-declared conditions hold.** The medians are strictly ordered, the extreme pair differs by a factor of
**14.7** against a bar of 2, **5 of 5 seeds** agree on that pair, and the spectral entropy falls in the same order.

The positive control also held on its own terms: the `amp 0.5` arm reproduced the 311-split configuration of `e6p_survfd`
(308 against 311), so the series is measuring the world the sentence was written about.

## What it establishes

The sentence from this morning now has a dose:

> **Transmission tracks the geometry of the field, and it does so monotonically.** Smoothing the inflow from 0.5 to 0.1 —
> touching nothing else — cuts divisions fifteen-fold and sharpens the spectrum from broadband (entropy 2.27, no dominant
> mode) to a selected wavelength at q = 8 (entropy 1.75, peak share 0.39).

The middle amplitude is the interesting one: it already peaks at q = 8 but weakly (0.19) with entropy still 2.25. Selection
of a wavelength and suppression of transmission happen **together along the same axis**, not as two separate effects with a
threshold between them.

Composition drift follows the same ordering (1.89 → 1.28 → 1.07), which is the E6p/E6q pattern again: the strongest trait
drift lives in the most fragmented world.

## What it does not establish

- Amplitude also changes how much area the field occupies, so the dose is not a pure geometry knob; the matched-occupancy
  control of X60 has not been repeated here.
- Five seeds per arm: the argument is the ordering and the 5/5 sign agreement, not a test.
- Divisions count events under the overlap rule, not verified lineages.

## Artifacts

`morphogenesis/experiments/L1_field/x59_{a50,a25,a10}_s{171..175}.json`, fields in `x59_fields/` (45 arrays), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x59_dose.json`. Scripts: `scripts/x59_series.py`, `scripts/x59_analyse.py`.

## Next

The axis now has three points; the natural fourth is the endpoint already on disk (amplitude 0.0, 17.5 divisions). With it
the curve is four points spanning 308 → 17.5 and can be read as a response curve rather than three arms — which is a
comparison of existing artifacts, not a new run.
