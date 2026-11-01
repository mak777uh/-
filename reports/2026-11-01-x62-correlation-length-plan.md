# X62 — the other axis: does the correlation length of the inflow control turnover?

1 November 2026, 09:05. Preregistration before the run.

X59 established that turnover is a **dose-response in the amplitude** of the inflow: divisions 308 → 79 → 21 as amplitude
falls 0.5 → 0.25 → 0.1, with the spectrum sharpening in the same order. Amplitude is one axis. The other, never varied in
this line, is the **correlation length** of the inflow field — how far apart two points have to be before their inflow
differs.

The question matters because of the sentence the night produced: *heterogeneity buys turnover at the cost of
organisation*. If true, turnover should track the **density of boundaries** in the inflow, not just its amplitude. The
pattern wavelength of this world is 12 units, so the interesting comparison is a correlation length far below it, at it,
and far above it.

**Prediction, written before the data.** Divisions ordered **scale 4 > scale 12 > scale 24**, with the extremes separated
by at least a factor of two, at matched amplitude 0.5. The spectrum should sharpen as the correlation length grows: at
scale 24 the field has patches large enough to hold the 12-unit pattern, so its entropy should be the lowest of the three.

## 1. Manipulation is connected

The same machinery with one number changed (`--hetero-scale`). The endpoints are already measured: scale 12 gives 308
divisions and a broadband spectrum (entropy 2.27) at amplitude 0.5. Scale is not a label — it changes the spatial
correlation of `F_eff`, which the world reads every step.

## 2. Positive control fires

- **Control arm:** scale 12, the configuration behind the 308-division measurement.
- **Fires if:** the new scale-12 runs land in the same range (median splits above 150). If they do not, the series is not
  measuring the world the prediction was written for.

## 3. Readout exists and varies

- **Readouts:** `selection.splits`, `parent_child_pairs`, `s_mean_last`; spectral entropy and peak share from the saved
  fields at t = 6000.
- **Observed range:** splits 4 to 311 across existing arms; entropy 1.52 to 2.34. Both vary by more than the predicted
  effect.

## 4. Sensitivity arithmetic

Five seeds per scale, paired by seed. Criterion: medians ordered as predicted, the extreme pair separated by a factor of
at least **2**, at least **4 of 5** seeds agreeing on that pair, and entropy at scale 24 below entropy at scale 4. No
p-values: with five correlated trajectories a test would overstate precision.

## 5. Refusal rule

Worthless, not negative, if:

1. the scale-12 arm fails the positive control (median splits below 150);
2. any arm produces a dead field (median components 0);
3. the three arms' splits fall outside the range already spanned by known configurations (4 to 311), which would mean the
   readout is not a function of the manipulation.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, amplitude 0.5, `beta = 0.2`, `freq_dep = 1`, mutation 0.15, `eps = 0` |
| arms | correlation length **4**, **12**, **24** (units = cells at this grid) |
| seeds | 171–175, paired |
| fields | saved at t = 2000, 4000, 6000 |
| criterion | §4 |
| artifacts | `morphogenesis/experiments/L1_field/x62_s{04,12,24}_s*.json`, `x62_fields/` |

## Status

- [x] connected (same machinery, one number; scale-12 endpoint already measured)
- [x] positive control fires (scale 12: 308 splits, entropy 2.27)
- [x] readout exists and varies (splits 4–311, entropy 1.52–2.34)
- [x] sensitivity computed (paired, factor-2, 4/5 sign rule, entropy ordering)
- [x] refusal rule written (three conditions)
