# X84 — the medium has one period and two symmetries: X71's "two wavelengths" was a radial binning artefact

**Date:** 2026-11-02, 04:35 MSK. **Reads:** `_x71_fields` (35 worlds), `_x71b_fields` (20 snapshots), `_x71c_fields` (10 worlds),
`_x82_fields` (control worlds). **No new runs.** Registered plan: `reports/2026-11-02-x84-angular-plan.md` (deviation from it is
stated at the end). **Corrects:** §10eq, §10ev, claims 291 and 295.

## The measurement error

Every spectral number in this line — X71's modes, X78b's two-peak check, X79's and X80's shares — comes from a **radial** profile:
power binned by `|k|` alone. The forcing pattern is a checkerboard, `G = (sin(qy)·cos(qx) + 1)/2`, whose power sits at the four
**diagonal** wavevectors `(±q, ±q)`. For the 12-cell pattern `q = 8`, so the forcing line is at `|k| = q√2 = 11.3`, radial bin **11**.

A stripe morphology of period 8.7 cells sits at `(±11, 0)` and `(0, ±11)`, `|k| = 11.0` — radial bin **11** as well. Two different
things share one bin, and one of them is the forcing itself. X71's "modes at 12.0 and 8.73 cells" were read as bins 8 and 11.

A control world makes it explicit (X82's single-scale cell, no imposed second scale): its four largest Fourier peaks are the
**diagonals at `|k| = 11.3`** (power 63 123 and 57 209) and its next four are the **axis-aligned peaks at `|k| = 8.0`**
(35 612 and 35 431). One period of structure, two orientations of power, and a radial profile with peaks at both bins.

## The measurement that separates them

From the same fields, per world:

- `P_diag` — power at the four prescribed diagonals `(±8, ±8)`;
- `q'` — the axis-aligned wavenumber of maximum power, `(q', 0)` and `(0, q')`, searched in `q' ∈ [4, 14]`;
- symmetry `s = P_diag / (P_diag + P_axis)`.

`q'` is a **period** (wavelength `96/q'` cells); `s` is a **symmetry mix** (1 = checkerboard locked to the forcing, 0 = stripes).

## Result: one period, a symmetry that follows the inflow

Thirty-five X71 pattern worlds, five per inflow:

| `F` | `q'` per world | wavelength, cells | symmetry `s`, median | `s` range |
|---|---|---|---|---|
| 0.025 | 6, 8, 8, 7, 8 | 16.0–12.0 | 0.381 | 0.352–0.598 |
| 0.030 | 8, 8, 9, 9, 8 | 12.0–10.7 | 0.516 | 0.462–0.739 |
| 0.035 | 8, 7, 8, 7, 8 | 12.0–13.7 | **0.777** | 0.643–0.811 |
| 0.040 | 8, 7, 7, 7, 7 | 13.7–12.0 | 0.919 | 0.918–0.948 |
| 0.045 | 8, 7, 7, 7, 7 | 13.7–12.0 | 0.925 | 0.913–0.955 |
| 0.050 | 8, 7, 7, 7, 7 | 13.7–12.0 | 0.924 | 0.908–0.944 |
| 0.055 | 8, 8, 5, 7, 8 | 19.2–12.0 | 0.888 | 0.770–0.934 |

- **The period never splits.** `q'` takes values 5–9 across the 35 forced worlds, i.e. 10.7–19.2 cells, and **never 11** — the value
  that would be needed for an 8.7-cell branch. The morphology has one preferred scale, ~12 cells, throughout. The **unforced** arm
  agrees on the period: `q' = 7–10` (9.6–13.7 cells) at `F = 0.025–0.050`, with the caveat that its `F = 0.055` worlds are **dead**
  (field std 0.0, no morphology to measure) and its `F = 0.050` worlds are weak (std 0.035 against ~0.10 elsewhere), so the top of
  that column is a decay, not a second scale.
- **The symmetry varies strongly and smoothly with inflow.** `s` rises from 0.38 at `F = 0.025` to a plateau of 0.92 at
  `F = 0.040–0.050`, then falls slightly at 0.055. Spearman(`s`, `F`) over the 35 forced worlds = **0.687**.
- **Without forcing the symmetry is low and falls with inflow** (`homog` arm: 0.23 at 0.025, 0.10 at 0.030, 0.18 at 0.035, 0.05 at
  0.040, 0.02 at 0.045, 0.20 at 0.050) — a residual diagonal of a few per cent, not a line. Forcing is what raises `s`, and the range
  0.35–0.95 is the response to it.
- **The radial "mode" is the symmetry.** Spearman(`s`, X71's recorded radial `q_peak`) = **0.778**: worlds whose largest radial peak
  is bin 11 are worlds locked to the forcing diagonals, not worlds with a shorter wavelength.
- **X71b's stationarity is the forcing's stationarity.** At `F = 0.035` the symmetry is 0.777 at t = 6000 and 0.775 at t = 24 000 —
  flat to three decimals over four snapshots. A stationary line plus a stationary pattern is stationary by construction; the claim
  that "two modes coexist and persist" is not supported by that flatness.
- **X71c's "band width" is the width of the crossover.** At `F = 0.033` `s = 0.663` (0.576–0.781), at 0.037 `s = 0.901`
  (0.794–0.949). A continuous ramp in `s` passes any threshold at some inflow, so "the band is 0.002 wide at cut 0.2 but wide at cut
  0.15" is exactly what a smooth ramp does. The earlier finding ("the width is a property of the cut") was the first symptom.
- **Without forcing, `s` is near zero.** The `homog` arm (no pattern in `G`) gives `s = 0.02–0.23` with `q' = 7–10` across inflows:
  stripes at the same period, no diagonal line, and the line's share decreases as inflow rises. Forcing is what raises `s`, and the
  range 0.35–0.95 is the response to it.

## What this does to the earlier claims

1. **"The medium is multistable between 12.0 and 8.73 cells at `F = 0.035`" — refuted.** There is one period. What alternates between
   worlds is the **symmetry** of the pattern at that period, and the alternation is a smooth function of inflow, not a bistability.
2. **"Two-branch coexistence is stable over 24 000 steps" — not supported.** The measured quantity that was flat is the fraction of
   power on the forcing diagonals, and it is flat because the forcing is fixed.
3. **"The half-life is two-valued inside and outside the band" (§10fa)** — the band was this crossover, so the two levels are the two
   ends of a symmetry ramp, not two attractors. The number stands as a measurement; its interpretation changes.
4. **X78b/X79/X80's two-scale manipulations** varied the **forcing line**, not the number of morphological scales. That is why the
   weights moved almost nothing in the field: the forcing line moves as prescribed, the morphology does not follow it.
5. **X82's "realised share"** is essentially `1 − s`-like: it measures how power divides between the forcing diagonals and the
   structure band. Its transfer function is a statement about symmetry, not about reach to a second scale.

## What replaces the old picture

A single-parameter description of this medium in this box: **one period (~12 cells, set by the medium), and a symmetry coordinate
`s ∈ [0,1]` set by how strongly the inflow pattern is locked into the structure, rising from ~0.4 at `F = 0.025` to a plateau ~0.92
at `F ≥ 0.040`.** "Two preferred scales" was a reading of the same fact in radial coordinates, where a checkerboard's diagonal and a
stripe's axis land in the same bin.

For the question of life in a digital medium this is a cleaner handle than a "multistable band": the environment can impose
**orientation** at a fixed scale, and cannot impose scale at all. Whether orientation is what carries memory is now a direct
question — and the readout for it (`s`, per world) already exists on stored fields.

## Deviation from the registered plan, stated

X84 was registered as fifteen new worlds. While preparing it I found that X71, X71b and X71c had already saved their fields
(65 snapshots), so the registered readout was applied to **those** fields instead of new runs — a larger sample (35 worlds plus
four horizons plus two edge cells) than the plan's 15. The registered control ("the `F = 0.030` cell must reproduce X74's `rho1` band")
is **not applicable** because no new worlds were generated; instead the instrument was validated in three ways: the control world's
angular peaks match the prescribed forcing wavevectors exactly, the `homog` arm returns `s ≈ 0.15` with no forcing, and the X82
control worlds (independent seeds, same configuration) give `s = 0.61–0.64` against X71's 0.46–0.74 — consistent.

доска: принято 0, отклонено 0, отложено 0.
