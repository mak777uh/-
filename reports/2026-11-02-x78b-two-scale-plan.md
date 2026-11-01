# X78b — impose two scales where the world is robust: composite pattern at `F = 0.030`

**Why a second attempt.** X78 tried to impose a second preferred scale by prescribing the hetero wavelength at `F = 0.040`, and the
matched arm degenerated to a single-component world: `--hetero-scale` sets the wavelength of an inflow *modulation*, and at that
inflow any strong modulation pushes the field out of the patterned regime. The runner therefore gained a **composite pattern**:
`--hetero-scale2` with `--hetero-mix2` sums two wavelengths into one `G` (off by default; anchored bit-for-bit with the flags off
on `x78_mismatch_s171`).

Pilots of the composite show the same collapse at `0.040` (1.0–1.3 components at amp 0.5, 0.25 and 0.15) but a **robust world at
`0.030`**: 30.9 components and 146 division pairs at amp 0.5, 23.9 and 118 at amp 0.25. So the causal test moves to the inflow
where both scales can coexist without killing the field.

**Prediction.** `0.030` is a long-memory cell (half-life 1.47, X74). Imposing a second scale there should shorten memory toward the
band's value (0.56–0.73) if the two-scale reading is right. If memory stays at 1.4–1.5, the reading is refuted and the two-level
pattern of §10fa must be about something else.

## 1. Manipulation is connected

The manipulation is the composite `G`. Connectedness is that the world must (a) remain patterned — at least 10 components per
world on average and at least 600 lag-1 pairs pooled — and (b) actually carry **two spectral peaks**: with fields saved at step
6000, the radial spectrum of each world must have local maxima near q ≈ 8 (12.0 cells) and q ≈ 11 (8.7 cells), separated by at
least 2 bins. If only one peak appears, the composite did not reach the world and the series is void.

## 2. Positive control fires

The control fires if the **single-scale** reference for this inflow is reproduced by this protocol: the `0.030` cell of X74 gave
lag-1 = 0.507 and half-life 1.47 with the same seeds and horizon. The reference is cited, not re-run; what is checked is that the
composite arm's lag-1 lies in `[0.30, 0.70]` (a patterned world's range) and its shuffle p95 is at most 0.10.

## 3. Readout exists and varies

Same depth readout as X73–X76 (Spearman of ancestor on descendant peak area at lags 1–3, `λ`, half-life), plus the two-peak check
of §1 from the saved fields.

## 4. Sensitivity arithmetic

Ten worlds, 6000 steps, 50-step logging, fields at 6000 only: measured 103–112 s per run in X74 → ~20 minutes. The X74 `0.030` cell
gave 1 166 / 1 091 / 1 037 pairs at lags 1–3; the composite pilot gave 146 pairs in one world, so ten worlds should give ≈1 400 and
the Fisher band on `λ` ≈ ±0.1 — a shift from 1.47 to 0.7 is far outside it.

## 5. Refusal rule

**Void** if the world collapses (fewer than 10 components on average), if fewer than 600 lag-1 pairs appear, or if the two-peak
check fails.

**Supports the causal reading** if the composite cell's half-life is **below 1.0** and at least **1.3× shorter** than the
single-scale 1.47.
**Refutes it** if the half-life is **above 1.3**.
Anything else is **inconclusive**, with the curve and the spectra printed.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.030`, `k = 0.06` (long-memory cell, 1.47) |
| pattern | composite `G` = 0.5·G(12.0) + 0.5·G(8.7), amp 0.5 — two imposed scales |
| worlds | 10, `--init-jitter`, seeds 171–180 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every **50** steps; fields at 6000 (`_x78b_fields/`) for the two-peak check |
| artifact | `morphogenesis/experiments/L1_field/x78b_two_scale_s171-180.json`, aggregate `l1_field_x78b_causal.json` |

## Status

Registered 2026-11-02 04:05 MSK, before the series. Runner change anchored: with `--hetero-scale2` absent, `x78_mismatch_s171`
reproduces bit-for-bit (`series`, `uid_pairs`, `uid_outcomes` identical). Ten runs, ~20 minutes.
