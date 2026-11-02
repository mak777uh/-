# X80: dip or slope — the sweep cannot say, because the ruler changes its answer when you change how you average

**Date:** 2026-11-02, 06:40 MSK. **Experiment:** X80 (amplitude-normalised weight sweep at `F = 0.030`).
**Preregistration:** `reports/2026-11-02-x80-dip-plan.md` (written 05:15, series 05:20-06:10).
**Artifacts:** `morphogenesis/experiments/L1_field/x80_w{025,05,075}_s171-175.json` (15 runs), fields `_x80_fields/` (15 snapshots
at 6000), aggregate `morphogenesis/experiments/E09_pond/l1_field_x80_dip.json`.

## Result

Five jittered worlds per cell, 6000 steps, 50-step logging, field saved at 6000. All three cells are patterned and powered
(27-39 components, 665-981 lag-1 ancestor-descendant pairs).

| cell | components | two-peak worlds | rho1 / rho2 / rho3 | lambda | half-life, pooled | half-life, per-world median (range) |
|---|---|---|---|---|---|---|
| w = 0.25 (mostly 12.0 cells) | 38.7 | **5/5** | 0.509 / 0.214 / 0.101 | 0.445 | 0.86 | **1.04** (0.34-1.83) |
| w = 0.50 (equal parts) | 29.4 | **5/5** | **0.391** / 0.137 / 0.121 | 0.556 | 1.18 | **0.52** (0.29-4.03) |
| w = 0.75 (mostly 8.7 cells) | 27.1 | **0/5** | 0.499 / 0.216 / 0.164 | 0.573 | 1.25 | **1.16** (0.57-1.63) |
| single scale at 0.030 (X74) | 47.7 | - | 0.507 / 0.304 / 0.198 | 0.625 | 1.47 | 1.26 (1.21-2.44) |

The registered rule **fires "slope"** (`0.86 < 1.18 < 1.25`, monotone, spread 0.39 >= 0.20). I am not accepting that verdict, and
the reason is inside the preregistration, not after it.

## Why the registered verdict does not stand

Two of the plan's own gate conditions failed at once:

1. **The positive control did not fire.** The plan required both wings above 1.0 so that the wings could serve as single-scale
   references. `w = 0.25` came out at 0.86. The wings are not single-scale-like; they are already mixed.
2. **The middle cell is not uniquely the most two-peaked.** It ties with `w = 0.25` (5/5 against 5/5), and `w = 0.75` carries
   **no** two-peak world at all. So the sweep did not produce three degrees of mixedness. It produced **mixed, mixed, one
   single scale at 8.7 cells** — the endpoint is a different wavelength, which is exactly the failure the plan's void clause was
   meant to catch and did not, because it asked for "highest", and a tie passed.

Under those two failures, "slope in `w`" is a slope between two mixture cells and a single-scale cell, i.e. it is not the
"dominant scale" reading the plan defined. What the pooled numbers do support: **both mixture cells are shorter-lived than the
single-scale reference at the same inflow** (0.86 and 1.18 against 1.47), in the same direction as X78b (1.03) and X79 (0.76 at
w = 0.25). That is a third and fourth data point for "an imposed second scale shortens memory", and no ordering between the
mixture cells.

## The second finding, which is larger: the half-life is aggregation-dependent

The preregistered statistic fits `lambda` to the ratios of the **pooled** pair pool, then `half = ln0.5/ln(lambda)`. Pooling
pairs across worlds is not the same as averaging worlds, and the two disagree — in X80 they disagree in **sign**:

| reading | w = 0.25 | w = 0.50 | w = 0.75 | shape |
|---|---|---|---|---|
| pooled rho1 | 0.509 | **0.391** | 0.499 | dip |
| pooled half-life | 0.86 | 1.18 | 1.25 | slope |
| per-world median half-life | 1.04 | **0.52** | 1.16 | dip |

The mechanism is visible in the numbers: when a cell's lag-1 correlation drops but its lag-2/lag-3 do not drop as fast, the ratio
`rho2/rho1` **rises**, so `lambda` rises and the fitted half-life gets *longer* even though the memory starts lower. Half-life is
a ratio statistic; it cannot be read as a level. Pooled and per-world differ because the pooled `rho1` is one number for the
whole cell, while the per-world median asks a different question: what does a typical world do.

Per-world fits are also unstable at this size. At `w = 0.50` the five worlds give 0.29, 0.50, 2.43, 0.52, 4.03 — one world
carries a near-zero lag-2 and drags `lambda` to 0.84. A cell of 100-150 pairs per world is not enough to fit a two-ratio decay.

## Audit of the same statistic on the earlier cells

Recomputed from the stored per-world correlations, nothing else changed:

| cell | pooled half-life (as published) | per-world median | per-world range | worlds fittable |
|---|---|---|---|---|
| X74 F = 0.030 | 1.47 | 1.26 | 1.21-2.44 | 5/5 |
| X74 F = 0.035 | 0.73 | 0.92 | 0.27-3.09 | 10/10 |
| X74 F = 0.040 | 1.61 | 1.82 | 0.82-2.10 | 5/5 |
| X76 F = 0.033 | 0.57 | 0.66 | 0.43-1.86 | **7/10** |
| X79 w = 0.25 | 0.76 | 0.64 | 0.42-1.86 | 9/10 |
| X79 w = 0.75 | 0.96 | 0.89 | 0.21-3.36 | 10/10 |
| X78b 0.030 two-scale | 1.03 | not stored | - | - |

Consequences for what we already wrote:

- **The direction of the multistable band survives.** Outside the band 1.26 and 1.82, inside 0.66 and 0.92 — the ordering is
  the same under both aggregations.
- **The size of the effect does not.** Pooled gives 2.01x (0.030/0.035) and 2.58x (0.030/0.033); per-world medians give 1.37x
  and 1.91x. The phrase "two-valued, 2.1-2.5x" in §10fa and claim 295 is a **pooled** number and must be quoted as such.
- **One cell cannot be fitted per world at all.** At `F = 0.033` three of ten worlds have a lag-2 or lag-3 correlation at or
  below zero, so their `lambda` does not exist; the published 0.57 is fitted from the pooled pool that includes them.

## What I now think is true

1. An imposed second scale shortens memory at `F = 0.030`: four cells across three series (0.86, 1.18, 1.03, 0.76) against
   1.47 for a single scale. The four are not mutually ordered, and the two-peak check says they are not the same kind of world.
2. **Mixedness, as this composite can produce it, is not separable from wavelength dominance with three weights.** At equal
   weights the two peaks coexist; at 0.75 the small scale wins outright. The next design must prescribe the **share** of the
   second spectral peak at a fixed dominant, not mix two patterns and hope.
3. The half-life as implemented is a **ratio**, so "how long memory lasts" and "how fast it decays" can move in opposite
   directions. Every half-life in X74/X76/X78b/X79/X80 is pooled. Any claim built on it carries an aggregation assumption that
   was never stated before today.
4. Two of our gates are too weak and are now known to be: the two-peak check passes on a tie, and the positive control can fail
   without voiding the series (the plan mentioned the consequence but the refusal rule did not encode it).

## What must change before the next run (registered in §10ff)

- Report **`rho1` as the primary level** and the half-life as a **secondary** derived quantity, with the per-world median and
  its range always printed beside the pooled value.
- Fit `lambda` **per world** and aggregate by median; declare a cell unfittable if fewer than 7 of 10 worlds yield a positive
  decay.
- Replace the mixture with a **prescribed spectrum**: dominant at q = 8, second peak at q = 11 with share swept 0 / 0.5 / 1.0 of
  the dominant power, phases random, then amplitude-normalised. The manipulation check is the **measured** power share from the
  saved field, not a peak count.
- Void if any cell's measured share deviates from the prescribed share by more than 0.15, or if the two-peak check is a tie.

## доска литературы

принято 0, отклонено 0, отложено 0 — this result is a measurement-geometry finding; nothing on the board bears on it.
