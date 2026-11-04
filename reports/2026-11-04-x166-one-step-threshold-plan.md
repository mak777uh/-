# X166 — The contact threshold at one-step resolution (pre-registration, 04.11)

**Status:** pre-registered, not yet run. X159 left this exact instruction on the table: the 1.9-cell reading is an upper
bound because the log samples every tenth integration step and the bodies grow inside that quantum. The repair is a
one-step log, not more seeds.

## 1. Manipulation is connected

Five arms of the fusion block are re-run with `--sample-every 1` and 2 000 steps: radius 3 at gaps 8 and 9, radius 4.5 at
gap 9, radius 5.2 at gap 7, radius 6 at gap 8. Everything else is identical to X158's runs (grid 96, `F` = 0.030, `Du` =
0.16, `Dv` = 0.08, `k` = 0.06, the same heterogeneity, the same seeding and the same jitter), so the only difference between
this series and the ones in git is the sampling rate. Five seeds per arm (911-915), never used in this block.

The manipulation is connected if the one-step logs actually change what the analysis sees: the number of logged steps per
run rises tenfold (about 2 000 against about 200) and the last two-body step is the same physical moment, so the readout
must move from "one quantum wide" to "one step wide".

## 2. Positive control fires

The control is the same one the block always uses: the gap-8 arms must fuse in at least 4 of 5 runs at radius 3 and 5 of 5
at radius 6, matching X158's 5/5 and 10/10. The control fires if those shares are reproduced at the new seeds; if they are
not, the series is not comparable to the block and stops.

## 3. Readout exists and varies

The readout is the surface gap at the **last logged step with two bodies**, now at one-step resolution, in cells. It must
vary (standard deviation of at least 0.1 cells across the 25 runs) and its median must lie between 0 and 5 cells. A readout
that collapses to a single value is not a measurement.

## 4. Sensitivity arithmetic

With ten-step logging the window was 1.3 cells wide (median over 119 runs, X159). At one-step resolution the residual
window is that width divided by ten, i.e. about **0.13 cells**, which is the resolution at which the threshold becomes
statable. The predicted effect is therefore not a difference between arms but a *narrowing*: the within-run uncertainty
drops by an order of magnitude, and the between-run scatter of the threshold — which X159 could not separate from the
window — becomes visible. Twenty-five runs are enough for a median with a bootstrap interval of about 0.2 cells if the
between-run scatter stays near 0.5; if the scatter turns out to be larger, the item reports the distribution and does not
claim a threshold.

## 5. Refusal rule

Two outcomes are both acceptable and must be stated plainly. (a) If the threshold lands within 0.2 cells of the same value
across the five arms, the sentence becomes "fusion happens at a threshold of X cells, independent of size", and the
article's "about two cells" becomes a number with an interval. (b) If the per-run thresholds scatter by more than 0.5 cells
at the same nominal geometry, there is **no single threshold**: fusion is a stochastic event whose probability rises through
the window, and the article says "about two cells" as a band by right, not by resolution. The refusal rule of §3d is not
triggered by either outcome; what would trigger it is a readout that does not exist (§3).

## 6. What would kill it

A gap-8 arm that fails to fuse in 4 of 5 (the series is not comparable); a one-step log whose "last two-body step" jumps by
more than a few steps from the ten-step reading (the reconstruction is wrong); or per-run thresholds whose spread is larger
than the whole window, which would mean the body's growth rate varies more than the effect we are chasing.

## 7. Implementation notes

Runner `scripts/x166_series.py` (five arms × five seeds = 25 runs, 2 000 steps, `--sample-every 1`, CPU, about an hour).
Analysis `scripts/x166_analyse.py`, reusing the first-2→1-transition rule from X157: find the first logged step at which
the component count falls from two to one, take the previous step's surface gap, and report it per run plus the growth rate
from the last three two-body steps. Aggregate `morphogenesis/experiments/E09_pond/l1_field_x166_threshold.json`. One-step
logs are about 45 MB per run and are **not** committed; only the compact projections and the aggregate.
