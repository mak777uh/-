# X78 — the causal test: impose the second scale instead of finding it

**Question.** X74–X76 established that the size memory is two-valued: half-life **0.56–0.73** divisions inside the multistable band
at `F = 0.033–0.037` and **1.47–1.61** outside it at `0.030`/`0.040`. Three monotone covariates (split rate per structure, split
rate per area, size dispersion) fail to explain the difference, and what the shallow cells share is **two coexisting length
scales**. That is a description. This series makes it a manipulation.

The hetero pattern is a prescribed spatial modulation of the inflow with a wavelength fixed by `--hetero-scale`. At `F = 0.040` the
medium's own preferred pattern is 8.7 cells (X71). So:

- **matched cell:** `--hetero-scale 8.7` — the prescribed scale agrees with the medium's, one preferred scale;
- **mismatched cell:** `--hetero-scale 12.0` — the prescribed scale disagrees, so the world carries two scales (the medium's 8.7 and
  the pattern's 12.0), exactly the configuration of the multistable band, but at an inflow where the field itself is single-valued.

Prediction: the **matched** cell keeps the long memory of its inflow (half-life ≈ 1.6), the **mismatched** cell loses it (half-life
≈ 0.6–0.8, the band's value). If instead both cells look alike, "two scales" is not the cause and the U-shaped observation was about
`F` after all.

## 1. Manipulation is connected

The manipulation is `--hetero-scale`, which changes the prescribed spatial wavelength and nothing else: same inflow, same amplitude,
same seeds, same horizon. Connectedness is that the two cells must **differ** in the observable the manipulation targets — the
per-run spatial spectrum must peak at the prescribed scale in each arm (12 cells vs 8.7 cells in the field's correlation
structure). If the two arms produce the same spectrum, the manipulation did not reach the world and the series is void.

## 2. Positive control fires

The control fires if the **matched** cell reproduces the X74 benchmark for `F = 0.040`: lag-1 ∈ `[0.40, 0.60]` and half-life
`≥ 1.2` divisions. That ties the new cell to the measured curve; if the matched cell instead comes out shallow, the manipulation has
broken something else and neither arm can be read.

## 3. Readout exists and varies

Same readout as X73–X76: Spearman(ancestor peak area, descendant peak area) at lags 1–3 with 50-step logging (genealogies need
it), `λ` as the geometric mean of the two ratios, half-life `ln 0.5 / ln λ`, cross-lineage shuffle null at every lag.

## 4. Sensitivity arithmetic

Ten runs (2 arms × 5 worlds), 6000 steps, 50-step logging, no fields: measured 69–111 s per run in X74/X75, so ~15 minutes. The
X74 `0.040` cell gave ~970 lag-1 and ~887 lag-2 pairs; five worlds should reproduce that order, and the Fisher band on `λ` is about
±0.1, so a half-life difference of the predicted size (1.6 against 0.7) is far outside the noise.

## 5. Refusal rule

**Void** if the two arms' spectra do not differ (control 1) or the matched cell's lag-1 leaves `[0.40, 0.60]`.

**Supports the causal reading** if the mismatched cell's half-life is **below 1.0** and at least **1.3× shorter** than the matched
cell's.
**Refutes** it if the two half-lives differ by **less than 1.2×** (i.e. the manipulation of scale did not move memory).
Anything else is **inconclusive**, with both curves printed.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.040`, `k = 0.06` (single-valued cell, memory long: 1.61) |
| arms | `--hetero-scale 8.7` (matched) vs `12.0` (mismatched, imposes a second scale) |
| amplitude, worlds | `0.5`, five worlds each, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every **50** steps, no fields |
| artifact | `morphogenesis/experiments/L1_field/x78_{match,mismatch}_s171-175.json`, aggregate `l1_field_x78_causal.json` |

## Status

Registered 2026-11-02 03:35 MSK, before the series. Ten runs, ~15 minutes.
