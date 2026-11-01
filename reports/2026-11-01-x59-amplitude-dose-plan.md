# X59 — dose-response: does transmission follow the amplitude of the inflow?

1 November 2026, 07:50. Preregistration before the run.

The sentence from
[`2026-11-01-transmission-tracks-the-field.md`](2026-11-01-transmission-tracks-the-field.md) says transmission tracks the
*geometry* of the field rather than the strength of selection on the trait. The sharpest cheap test is a **dose**: keep
every trait parameter fixed and vary only the amplitude of the inflow modulation.

At amplitude 0.5 the heterogeneous world is broadband and produces ~311 splits; at amplitude 0.0 it selects a 12-unit
wavelength and produces 17.5. If transmission follows geometry, the counts should fall monotonically as the amplitude
falls, and the spectrum should sharpen as it does.

**Prediction, written before the data.** Median splits: `amp 0.5` > `amp 0.25` > `amp 0.1`, with the extremes separated
by at least a factor of two, and the spectral entropy at physical time 6000 falling in the same order (more amplitude,
broader spectrum).

## 1. Manipulation is connected

Amplitude changes the world observably: at 0.5 the field is broadband (peak share 0.24, entropy 2.23 at grid 96), at 0.0 it
selects q = 8 (peak 0.45, entropy 1.52). The manipulation is the same inflow machinery with one number changed.

## 2. Positive control fires

- **Control arm:** `amp 0.5`, the configuration already measured — `e6p_survfd` median **311** splits over ten seeds.
- **Fires if:** the new `amp 0.5` runs land in the same range (median above 100). If they do not, the pipeline no longer
  reproduces the world the sentence was written about, and nothing else in the series can be read.

## 3. Readout exists and varies

- **Readouts:** `selection.splits`, `selection.parent_child_pairs`, `selection.s_mean_last`, plus the spectral entropy
  from the saved fields.
- **Observed range across existing arms:** 4 to 311 splits, so the readout varies by two orders of magnitude and a
  monotone trend would be visible without statistics.

## 4. Sensitivity arithmetic

Five seeds per amplitude. The three amplitudes are compared **pairwise by seed** (same seeds everywhere), so the relevant
quantity is the per-seed difference, not the between-seed spread. Criterion: medians strictly ordered
(`amp 0.5 > amp 0.25 > amp 0.1`), the extreme pair separated by a factor of at least **2**, and at least **4 of 5** seeds
agreeing on that extreme pair. Spectral entropy ordered in the same direction at t = 6000.

## 5. Refusal rule

Worthless, not negative, if:

1. the `amp 0.5` arm fails the positive control (median splits below 100);
2. any amplitude produces a dead field (median components 0) — then the run measures the death of the world, not
   transmission;
3. the two intermediate amplitudes fall outside the range spanned by the known endpoints (17.5 to 311) — which would mean
   the readout is not a function of the manipulation.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, `Du = 0.16`, `Dv = 0.08`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15, `eps = 0`, hetero scale 12 |
| arms | `amp 0.5`, `amp 0.25`, `amp 0.1` |
| seeds | 171–175 (five), paired |
| fields | saved at t = 2000, 4000, 6000 for the spectral check |
| criterion | §4 |
| artifacts | `morphogenesis/experiments/L1_field/x59_<arm>_s*.json`, `x59_fields/`, `x59_series_index.json` |

## Status

- [x] connected (0.5 broadband, 0.0 selective; same machinery, one number)
- [x] positive control fires (existing `amp 0.5`: 311 splits, ten seeds)
- [x] readout exists and varies (4 to 311 across arms)
- [x] sensitivity computed (paired by seed, factor-2 separation, 4/5 sign rule)
- [x] refusal rule written (three conditions)
