# X181 — The worst-heterogeneity cell, thirty fresh seeds at a uniform horizon (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X179's audit found that radius 3 at surface gap 10, `F` = 0.030 pools six seed families whose shares span **0.20 to 0.80** (2 of
10, 2 of 5, 2 of 5, 3 of 9, 4 of 5, 7 of 15) — the single number 0.41 is a compromise between a family that fuses four times in
five and one that fuses twice in ten. Every statement the block has made about "the crossing at gap 10" inherits that dispersion.
X179's own protocol names the next step: run the cell again with thirty fresh seeds and see which side the new family lands on.

A second difference between the pooled families surfaced while reading their parameters: they were run at **different horizons**
(2000, 3000 and 6000 steps). Fusion is an event in time, so a longer horizon can only raise a share. This item runs the cell at
the block's standard horizon of 2 000 steps, which is what most of the block's cells used, and records its own steps so the
comparison is exact.

## 2. Positive control fires

The control fires if, in this arm, the peak stays inside [0.05, 2.0] at every read, the component count of every run ends above
one (these are two-body runs and none of them may be counted as fused by starting fused), and the share lands inside **[0.23,
0.59]** — the pooled 0.41 widened by one Wilson half-width of a thirty-run family. Thresholds: 0.23 and 0.59, plus the two
component-count conditions. The negative control is the neighbouring cell at the same size and rate, gap 12, which X179's table
records as 0 of 10 and which this item does not re-run.

## 3. Readout exists and varies

The primary readout is the share with its Wilson interval. Secondary, where at least three runs fuse, is X170's contact-time
corridor; it must vary across runs (sd ≥ 0.02) and must not be 0 or 1 in every run.

## 4. Sensitivity arithmetic, and the prediction

Thirty seeds at radius 3, gap 10, `F` = 0.030, seeds 1211-1240, 2 000 steps. Registered **before the run**:

- **share: 0.23 to 0.59**, from the pooled 0.41 with a thirty-run Wilson half-width;
- the family's **step-1 measured radius**, which for this geometry has read 2.9-3.0 in every family so far, is recorded for each
  run so that the effective geometry can be compared with the nominal one;
- **horizon: 2 000 steps** exactly, and this is the item's own answer to the pooling question rather than a covariate.

Thirty runs separate 0.41 from 0.20 with a Wilson half-width of about 0.17, so a new family near either extreme is visible.

## 5. Refusal rule

If the share lands inside [0.23, 0.59], the item is recorded as **the cell's pooled share is reproducible by a fresh family**, and
the dispersion X179 flagged is between-family noise rather than a hidden variable; the pooled value 0.41 then stands as the cell's
share with the spread reported alongside it. If the share lands above 0.59 or below 0.23, the item is recorded as **families are
not exchangeable at this cell**, and the consequence is written plainly: every pooled share in X179's table must be quoted with
its family spread, and the cell's share is not a property of (radius, gap, rate) alone. If the peak or the component-count
control fails, the arm is not reportable and the item says so.

## 6. What would kill it

The cell sits on the steep part of the fusing range, so a fresh family could land in the middle of the interval for reasons that
have nothing to do with exchangeability — thirty runs cannot distinguish "noise" from "a hidden variable with a small effect".
The honest test of exchangeability is a second fresh family at the same cell, and if this one lands mid-interval the item will
say that the question is left open rather than answered.

## 7. Implementation notes

Runner `scripts/x181_worst_cell.py` (radius 3, gap 10, `F` = 0.030, seeds 1211-1240, 2 000 steps, field dumps every ten steps
into a gitignored directory), analysis `scripts/x181_worst_cell_analyse.py` (share with Wilson interval, the registered
interval, the measured step-1 radius, the horizon, and the comparison against the six existing families read from the X179
aggregate). Aggregate `morphogenesis/experiments/E09_pond/l1_field_x181_worst_cell.json`. Cost about fifteen minutes of CPU.
