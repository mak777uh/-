# X84 — re-read X71's "two branches" with an angular spectrum: one period with two symmetries, or two wavelengths?

**Why.** Every spectral number in the field line (X71's modes, X78b's two-peak check, X79's and X80's shares) comes from a
**radial** profile: power binned by `|k|` alone. The forcing pattern is a checkerboard, `G = (sin(qy)·cos(qx) + 1)/2`, whose power sits
at the four **diagonal** wavevectors `(±q, ±q)` — for the 12-cell pattern, `|k| = q√2 = 11.3`, i.e. radial bin 11. A stripe
morphology of period 8.7 cells sits at `(±11, 0)` and `(0, ±11)`, `|k| = 11.0` — radial bin 11 as well. **Two different things share
one bin**, and one of them is the forcing itself.

A control world (no imposed second scale) shows this directly: its largest Fourier peaks are the four **diagonals at `|k| = 11.3`**
(power 63 123 and 57 209) and the four **axis-aligned peaks at `|k| = 8.0`** (35 612 and 35 431) — the checkerboard forcing line and
the 12-cell stripes. Its radial profile therefore has a peak at bin 8 *and* a peak at bin 11 in a world with **one** imposed
wavelength. X71 read its two branches as 12.0 and 8.73 cells from exactly those two bins.

So the question that decides the headline multistability claim: at `F = 0.035`, do worlds differ in the **wavelength of their
morphology** (axis-aligned peak at two different periods), or in the **symmetry** of a pattern at one period (how much of the power
is locked to the forcing diagonals rather than to the axis-aligned stripes)?

## 1. Manipulation is connected

Three inflows — `F = 0.030` (X71's single-branch cell, X74's long-memory reference), `0.035` (X71's multistable cell) and `0.040` —
five jittered worlds each, same flags as X71 so the worlds are comparable. Connectedness is checked by the field: the forcing line must
be present in every world at the **prescribed** wavevectors `(±8, ±8)`, because a world that lost the modulation is not a test.

## 2. Positive control fires (numeric)

The `F = 0.030` cell is a re-run of X74's single-scale reference. **The control fires if** its pooled lag-1 correlation lies in
**[0.45, 0.56]** and its pooled half-life in **[1.30, 1.70]** divisions (X74: 0.507 and 1.47). If not, the worlds are not comparable
with the earlier series and the re-read is void.

## 3. Readout exists and varies

Per world, from the saved field at 6000:

- **forcing line** `P_diag = Σ P(k)` over the four wavevectors `(±8, ±8)` within ±1;
- **morphology** `q'` = the axis-aligned wavenumber of maximum power with the other component within ±2, searched in `q' ∈ [4, 14]`;
  `P_axis` is the power at `(±q', 0)` and `(0, ±q')` within ±1;
- **symmetry** `s = P_diag / (P_diag + P_axis)`;
- the depth readout as usual (`rho1`, per-world `lambda`).

Morphological wavelength is `96 / q'` cells. The two readings are now separable: `q'` is a period, `s` is a symmetry mix.

## 4. Sensitivity arithmetic

`q'` is an integer wavenumber, so the resolution is one bin: a split between 12.0 and 8.7 cells is 8 against 11, **three bins** — far
above resolution. `s` is a power ratio with world-to-world spread ~0.1–0.15 (three X80 cells, five worlds each: 0.43–0.70), so five
worlds per cell resolve a difference of 0.2 in the median. Cost: 15 runs at ~110 s ≈ **28 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a world has <10 components, <400 lag-1 pairs, no saved field, or if fewer than 4 of 5 worlds in a cell show the forcing
line at the prescribed wavevectors; also void if the §2 control misses its band.

**Two wavelengths** (X71's reading survives) if the axis-aligned `q'` at `F = 0.035` forms two clusters at least **two bins** apart,
each holding at least two of the five worlds.

**One period, two symmetries** (X71's reading does not survive) if all five worlds at `F = 0.035` share a `q'` cluster (spread ≤ 1 bin)
while the symmetry `s` varies by **>= 0.20** between worlds.

**Inconclusive** otherwise, printed in full.

Whatever the outcome, the write-up states the radial bin of the forcing line explicitly, so that no later reader re-derives a
wavelength from `|k| = q√2` a second time.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.030`, `0.035`, `0.040`, `k = 0.06` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5` (as X71) |
| worlds | 5 per cell, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every 50 steps; field at 6000 |
| artifact | `morphogenesis/experiments/L1_field/x84_f{030,035,040}_s171-175.json`, aggregate `l1_field_x84_angular.json` |

## Checklist before the series

- [x] connected (forcing line must appear at the prescribed wavevectors)
- [x] positive control fires (numeric band, §2)
- [x] readout exists and varies (`q'` integer, `s` continuous; both already measured on control fields)
- [x] sensitivity computed (§4)
- [x] refusal rule written, with the failure mode "two things in one radial bin" named

## Status

Registered 2026-11-02 08:05 MSK, before the series. Fifteen runs, ~28 minutes. Runs after X82 frees the lane.

доска: принято 0, отклонено 0, отложено 0.
