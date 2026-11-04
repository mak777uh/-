# X165 — Three bodies in a row: does the pairwise crossing survive many-body contact? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

Every fusion statement in this block is a **pairwise** law: two bodies, one gap, one crossing. The medium, however, is
global — a third body changes the field in the corridor between the first two, and if the crossing is a field-bridge effect
it should move. This item seeds three bodies of radius 3 in a row with a fixed **surface** gap between neighbours, using a
new `--init-row N:R:GAP` form (the existing `--init-spots` branch is untouched and separately anchored).

Arms: N = 3, radius 3, surface gaps 8, 10 and 12 (centre separations 14, 16 and 18), five seeds each (981-985), 6 000
steps, `F` = 0.030, ten-step sampling. Gap 8 is the block's positive control (pairs fuse 5/5); gap 10 is the crossing; gap
12 should not fuse. A pairwise control is not needed because the pair data already exist, but the gap-8 arm doubles as one.

## 2. Positive control fires

At gap 8 the three bodies must all fuse into one component in at least 4 of 5 runs — the pairwise control says they should,
and if they do not, three-body contact is not a perturbation of the pair but a different regime, which is itself worth
reporting. At gap 12 fewer than half of the runs should end with a single component.

## 3. Readout exists and varies

The readout is the **number of distinct components at the end of the run** (1, 2 or 3), plus the gap between neighbours at
the last logged step with three bodies. The component count must vary across the arms (if every arm ends at 1 or every arm
at 3, the series carries no information) and the three-body gap must vary (standard deviation ≥ 0.2 cells).

## 4. Sensitivity arithmetic

A pair at a surface gap of 10 fuses in about half its runs (X158: 7/15 at gap 10, 2/15 at gap 11), so a three-body row at
gap 10 has three chances to fuse and the expected number of fusions is around 1.5 per run if the pairwise law holds
unchanged. If the third body *helps* — because the corridor between the outer pair is enriched by the middle body's
production — the gap-10 arm should fuse in more than half its runs, and the design will see it as a higher share of runs
ending in one component than the pairwise 0.47 predicts. Five seeds per arm give a share with a Wilson interval of about
±0.4, so only a large effect (share > 0.9 or < 0.1) will be distinguishable: this item screens for a big change and does
not measure a small one.

## 5. Refusal rule

If all three arms end with a single component, the row fuses regardless of the gap and the item reports "the pairwise
crossing does not survive many-body contact: three bodies bring the pattern's own length scale into play". If all three arms
end with three components, the row never fuses and the item reports the opposite. Neither is reported as "the crossing
moved by X cells" — with five seeds only the extremes are distinguishable, and saying more would be arithmetic we cannot
back.

## 6. What would kill it

A gap-10 arm that fuses in 1-3 of 5 runs, exactly as the pairwise law predicts (0.47 per pair, so 2-3 of 5 runs with any
fusion), would say the pairwise law survives many-body contact and the medium's length is additive — a clean positive for
the mechanism. A gap-8 arm that fails to fuse would say the third body *prevents* fusion, which would be a discovery about
the medium and not a nuisance.

## 7. Implementation notes

Runner `scripts/x165_series.py` (three arms × five seeds = 15 runs, about 40 minutes), analysis
`scripts/x165_analyse.py` (component count at the end, the three-body gap at the last step with three components, the
fusion share of the outer pair and of the row). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x165_three_bodies.json`.
