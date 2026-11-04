# X172 — A prediction at a rate not yet run (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X170 measured, at surface gap 10, how the fusion share and the corridor at contact move with the inflow: shares 4/15, 7/15 and
10/15 at `F` = 0.026, 0.030 and 0.036, and corridor 0.516, 0.479 and 0.392 of the body peak. Both ladders are monotone and both
were fitted to three points. That is a description; a description becomes a law only when it predicts a cell it was not fitted
to.

This item runs an **unrun rate between the two measured neighbours**: `F` = 0.033, halfway between 0.030 and 0.036, surface gap
10, radius 3, **twenty seeds**. Nothing else changes.

## 2. Positive control fires

The control fires if the gap-8 arm at `F` = 0.033, five seeds, fuses **5/5** — the threshold is a share of 1.0 — so that the
world is demonstrably alive and in the same regime at this rate. If it does not, the rate is outside the regime and the item
stops.

## 3. Readout exists and varies

Two readouts, both already defined: the **fusion share** (min component count == 1 at least once, over twenty runs) and the
**corridor at contact** (minimum over the middle third of the segment between the two bodies' centres at the last two-body step,
over the peak field), the latter on the runs that fuse. The corridor must vary (standard deviation ≥ 0.02) and must read below
the peak in at least 80 % of contact runs.

## 4. Sensitivity arithmetic, and the prediction

Two predictions are registered **before the run**, from linear interpolation between the two measured neighbours:

- **share:** interpolating between 7/15 = 0.467 at 0.030 and 10/15 = 0.667 at 0.036 gives **0.567** at 0.033. The 95 % Wilson
  interval for 12 of 20 is [0.36, 0.75], so the prediction is stated as "**between 9 and 15 of 20**".
- **corridor:** interpolating between 0.479 and 0.392 gives **0.436**. With about eight contact events and a within-group spread
  of 0.04, the prediction is stated as "**0.436 ± 0.08**", i.e. inside [0.36, 0.52].

The item is a prediction test, so its verdict is written against these two intervals rather than against a difference: a miss on
either is a failure of the interpolation, and both are reported.

## 5. Refusal rule

If both predictions land inside their intervals, the item is recorded as **the dependence is smooth and quantitative**, and the
fusion line has a calibrated relation between the source and the crossing rather than an anecdote. If the share lands inside but
the corridor does not (or the reverse), the item is recorded as **a partial miss**, names which relation is not linear, and the
ladder gets a third point to fit rather than an interpolation. If both miss, the dependence is not monotone in the range and
X170's direction survives without its magnitude.

## 6. What would kill it

Both predictions are interpolations between adjacent rates, so they can be right for the wrong reason: the world's dependence on
`F` need not be linear in this range, and twenty seeds give a share interval 0.39 wide. A miss would therefore not refute X170,
only the linear reading of it. Conversely a hit confirms only that the two endpoints interpolate — which is still more than the
three-point ladder had.

## 7. Implementation notes

Runner `scripts/x172_forecast.py` (gap 10 at `F` = 0.033, twenty seeds 986-1005, plus five gap-8 controls, field dumps every ten
steps into a gitignored directory), analysis `scripts/x172_forecast_analyse.py` (the two readouts against their registered
intervals, plus the neighbour values read from X170's aggregate). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x172_forecast.json`. Cost about 15 minutes of CPU.
