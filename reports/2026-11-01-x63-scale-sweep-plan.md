# X63 — is the resonance at the pattern scale, or just a monotone scale effect?

1 November 2026, 09:32. Preregistration before the run.

X62 predicted a monotone decline of turnover with correlation length and measured a maximum in the middle instead: 308
divisions at scale 12 against 20 at scale 4 and 175 at scale 24. The post-hoc reading was **resonance** — turnover peaks
when the environment varies on the pattern's own scale (12 units). Three points are enough for a hypothesis and not enough
for a curve.

This run adds four scales, at fixed amplitude 0.5 and the same five seeds: **6, 8, 16, 32**. Together with the existing
12 that makes five points spanning a factor of eight around the pattern wavelength.

**Prediction, written before the data.** If the resonance is real, the profile is a peak near 12:

- at least one of {8, 16} lands **within a factor of two of 308** (i.e. ≥ 154),
- both extremes, 6 and 32, stay **below 154**,
- and the peak is not at an endpoint.

If instead the counts fall monotonically from 6 to 32, or rise monotonically, the resonance reading is wrong and X62's
curve is a monotone scale effect that happens to have a maximum at the one point measured twice.

## 1. Manipulation is connected

Same machinery, one number (`--hetero-scale`). The three anchors already exist: 4 → 20, 12 → 308, 24 → 175 divisions, all
at amplitude 0.5 with seeds 171–175. The new arms sit between and beyond them, so any deviation from the anchors is
visible immediately.

## 2. Positive control fires

- **Control arm:** scale 12 is not re-run (it is the anchor), but the *pipeline* is: the scale-8 and scale-16 arms must
  produce series that differ from each other and from the anchors. If all four new arms produce identical series, the flag
  is not reaching the world.

## 3. Readout exists and varies

- **Readouts:** `selection.splits`, `parent_child_pairs`, `s_mean_last`; spectral entropy at t = 6000.
- **Observed range:** 4 to 311 splits across arms; a factor of eight in correlation length spans the predicted profile with
  room on both sides.

## 4. Sensitivity arithmetic

Five seeds per arm, no p-values. The criterion is a **shape**: one interior point ≥ 154, both endpoints < 154. With the
known 12 = 308 as the peak candidate, this is a test of whether the profile has interior structure at all, not an estimate
of the peak location. If the profile turns out monotone, the resonance reading dies; if it has an interior maximum
elsewhere, the reading survives with a corrected peak.

## 5. Refusal rule

Worthless, not negative, if:

1. any arm produces a dead field (median components 0);
2. all four arms give the same splits within seed noise (the flag does not reach the world);
3. the values fall outside 0–1000 divisions per run, the range spanned by every configuration measured so far.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, amplitude 0.5, `beta = 0.2`, `freq_dep = 1`, mutation 0.15 |
| arms | correlation length **6, 8, 16, 32** (anchors 4, 12, 24 already on disk) |
| seeds | 171–175, paired |
| fields | saved at t = 6000 only (the spectral question is secondary here) |
| criterion | §4 |
| artifacts | `morphogenesis/experiments/L1_field/x63_s{06,08,16,32}_s*.json` |

## Status

- [x] connected (same machinery; three anchors already measured)
- [x] positive control fires (arms must differ from each other and from the anchors)
- [x] readout exists and varies (4–311 splits; factor-8 span)
- [x] sensitivity computed (shape criterion: interior ≥ 154, endpoints < 154)
- [x] refusal rule written (three conditions)
