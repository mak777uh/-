# X69 — the turnover dose with fifteen seeds, and a rate instead of a count

1 November 2026, 14:46. Preregistration before the run.

X59 is the strongest evidence in the field line: divisions 308 → 79 → 21 as the inflow amplitude falls 0.5 → 0.25 → 0.1,
ordered in 5 of 5 seeds with a factor of 14.7 between the ends. X63 then showed the weakness: the same counter has a
tenfold spread between seeds inside one arm, so a median of five can be moved by a single run.

This run adds ten seeds per amplitude (176–185), giving **fifteen seeds per arm** when combined with X59's 171–175, and
it adds the readout X63 asked for: **divisions per component per 1000 steps**, computed from the same artifacts, which is
less sensitive to a single run's burst.

## Prediction, written before the data

- The ordering `0.5 > 0.25 > 0.1` holds on the **rate** as well as on the count, with the same sign agreement bar.
- With fifteen seeds the spread of the rate should be visibly narrower than the spread of the count (that is the point of
  dividing by the number of components), and the ordering should survive it.

If the ordering holds on the count but not on the rate, the count is measuring arm size rather than turnover — which would
be an important correction to X59 itself.

## 1. Manipulation is connected

Only the amplitude changes, as in X59. The three arms differ in dynamics on the same seed (X59 established that, and X62's
leak check confirmed the amplitude reaches the world).

## 2. Positive control fires

The `amp 0.5` arm must reproduce X59's magnitudes: median divisions in the hundreds. If the new seeds give a median below
100, the series is not measuring the world X59 measured and nothing else can be read.

## 3. Readout exists and varies

`selection.splits` and the derived rate `splits / mean(components) / 6` (per 1000 steps), plus `components` from the
series. Observed: count 21–308 across arms, rate 1.17–6.94 across the earlier scale arms — both vary by more than the
predicted ordering.

## 4. Sensitivity arithmetic

Fifteen seeds per arm, paired by seed where the same seed exists in all arms (it does: 171–185). Criterion: medians
strictly ordered on **both** readouts, the extreme pair separated by a factor of at least 2, and at least **12 of 15**
seeds agreeing on the extreme pair. No p-values.

## 5. Refusal rule

Worthless, not negative, if:

1. the `amp 0.5` arm's median count falls below 100 (positive control failed);
2. the rate and the count order differently — then the two readouts measure different things and the arm comparison is
   ambiguous, not negative;
3. any arm produces a dead field.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, `beta = 0.2`, `freq_dep = 1`, mutation 0.15, scale 12 |
| arms | amplitude **0.5, 0.25, 0.1** |
| seeds | **176–185** (ten new per arm; combined with 171–175 for fifteen) |
| fields | not saved (this run is about counts and rates only) |
| criterion | §4 |
| cost | 30 runs ≈ 40 min |
| artifacts | `morphogenesis/experiments/L1_field/x69_a{50,25,10}_s*.json` |

## Status

- [x] connected (amplitude reaches the dynamics; X59 and X62 established it)
- [x] positive control fires (X59 `amp 0.5`: median 308 divisions)
- [x] readout exists and varies (count 21–308, rate 1.17–6.94)
- [x] sensitivity computed (fifteen seeds, factor-2 bar, 12/15 sign rule, both readouts)
- [x] refusal rule written (three conditions)
