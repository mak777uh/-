# X174 — Does the corridor at contact depend on the gap at a fixed size? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X171 made the corridor at contact a size-independent criterion, and named the confound it could not resolve: each arm sat at
its own crossing gap, so a **size** effect and a **gap** effect could not be separated. X173's arms at a fixed radius 3 are the
material that can separate them, and its gap-8 arm (ten seeds, all fused) already has dumps. This item completes that set: radius
3, `F` = 0.030, surface gaps **8, 9 and 10** — 8 and 9 fuse often enough to give contact events in every seed, 10 is the
crossing itself.

If the corridor at contact is the same at all three gaps, then neither the size nor the initial distance moves the criterion,
and it is a property of the moment of merging alone: the "criterion" survives X171's confound. If it drifts with the gap, the
criterion is a per-gap quantity and X171's rule needs the gap as a second input.

## 2. Positive control fires

The control fires if the gap-8 arm fuses **at least 8 of 10** (share ≥ 0.8) and the gap-10 arm fuses **at most 8 of 10**
(share ≤ 0.8) — i.e. the arms straddle the crossing rather than all fusing. And every arm's median corridor must read **below
the body peak** in every contact run (share 1.0), the peak must stay in [0.05, 2.0]. If the gap-8 arm fuses fewer than eight,
the world is not in the regime and the item stops.

## 3. Readout exists and varies

X170's definition, unchanged: the minimum of the field over the middle third of the segment between the two bodies' centres at
the **last sampled step with two bodies**, divided by the peak field at that step, with the component centres taken from the
log's own component list. It must vary across runs (standard deviation ≥ 0.02 over the pools) and must not be 0 or 1 in every
run.

## 4. Sensitivity arithmetic

Per arm: ten (gap 8) or fifteen (gap 9) runs and seven to fifteen contact events; the within-group spread measured at radius 3
at `F` = 0.030 is 0.036 (X170), so a difference of 0.05 between two gaps is about 1.4 pooled spreads across groups of this size
and the design resolves it; a difference of 0.02 is not resolvable and will not be claimed. The three medians and their counts are
reported so the reader can redo the arithmetic.

## 5. Refusal rule

If the three gaps' medians agree within the pooled spread, the item is recorded as **the criterion is per-contact and depends on
neither the body nor the initial distance**: X171's confound is resolved in the direction that keeps the rule. If the medians
differ by more than the pooled spread, the item is recorded as **the criterion depends on the initial gap**, X171's confound is
real, and the rule takes the gap as a second input; the direction of the drift is reported either way.

## 6. What would kill it

The gap-8 arm has only ten seeds and it is the arm where the bodies begin closest, so if the corridor at contact is a function of
*how far the bridge had to travel* rather than of the field's state, this arm is the one that would show it — and it is also the
arm with the fewest runs. The gap-9 arm carries most of the weight. A drift that appears at gap 8 only will be reported as
unresolved rather than as a trend.

## 7. Implementation notes

Runner `scripts/x174_gap_corridor.py` (radius 3, `F` = 0.030, gaps 8 and 9, seeds 1031-1040 and 1031-1045, 2 000 steps, field
dumps every ten steps into a gitignored directory), analysis `scripts/x174_gap_corridor_analyse.py` (the same contact-time
readout, with the gap-10 arm read from X170's aggregate). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x174_gap_corridor.json`. Cost about 15 minutes of CPU.
