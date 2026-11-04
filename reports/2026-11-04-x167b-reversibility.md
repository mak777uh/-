# X167b — A merge is reversible in place, and that is all this design can say (04.11)

**Question.** X167 found that merged bodies divide again, into products at the parents' positions with 0.87 of the parents'
combined area — and immediately ran into the confound that an elongated blob split at its ends produces the same geometry.
This item was pre-registered to settle it with a matched comparison.

Pre-registration: [`2026-11-04-x167b-reversibility-plan.md`](2026-11-04-x167b-reversibility-plan.md). Arm (a), merged: the
eight fusions in the X158 compacts, followed to their next division. Arm (b), single: ten fresh runs from a single droplet
(3 000 steps, the same world, seeds 951-960), giving a single body's own growth phase — the pre-registered "time from one
division to the next".

## Result

| quantity | merged (n = 8) | single (n = 10) |
|---|---|---|
| divided again within the log | 8/8 | 10/10 |
| steps from the referent to the next division (median) | **25** | **40** |
| products' area / the parents' combined area (median) | 0.867 | — |
| products' distance from the parents' old centres (median) | 1.25 cells | — |

The two medians differ by 1.12 standard deviations, and both are only two to four logged steps on a grid that samples every
ten steps. So the honest statement is the narrow one:

**A merged body divides again, promptly and in place, with products that carry the parents' combined area at the parents'
positions. That is what "reversible" means at the level of the tracking rule — and it is not evidence that the merged body
is anything other than a blob of the summed area.**

The pre-registered refusal rule fired: the arms overlap, so the item records "the merge carries nothing" as far as this
design can see, and the identity language leaves the fusion work unless the field says otherwise.

## What went wrong in the measurement, twice, and is recorded rather than hidden

1. **Arm (b) was degenerate at first.** It was defined as "time from reaching the merged area to the next division", but a
   single body only reaches that area immediately after its own division, so no run divided inside the window and the arm
   produced ten empty values. Replaced with the growth phase (division to division), which is what the pre-registration's
   §3 meant all along.
2. **Divisions are not always 1→2.** The runs reach 45 components with only one strict 1→2 transition, because splits
   happen as 1→3 and 2→3; counting only strict transitions gave "0 of 10 divided". Counting every increase in the component
   count fixed it.

Both are the same class of fault as the X160 incident: a readout that silently reports an absence. The difference is that
here the absence was visible — ten empty values in an arm that should divide — and was chased down instead of reported.

## Limits — and they are the whole point

The comparison cannot separate the readings, because both arms divide within two to four sampled steps and the sampling is
coarser than the difference. A decisive version needs (a) one-step logs, so that the time to division is measured at the
resolution at which it varies, and (b) the seam test from the field: for a body that divides after a fusion, does the
division line coincide with the old waist between the parents? Only the field can answer "is this the same object", and this
item's own conclusion is that components cannot.

## What this changes

The fusion block's §4k.3 language about a merged body becoming "a new object" is not supported by anything in the
component-level data, and this item says so explicitly. The measurement that would support it is the seam, and it is now the
only thing worth running here.

## What would kill it

A seam result: if division lines after a fusion cluster near the old waist, then the merge preserved structure and the
"blob" reading is wrong — the very next item would overturn this one. Equally, one-step logs showing the merged body
dividing at half the wait of a matched single body would do it.

## Next hypotheses

1. **The seam, from the field** (one run with field dumps, one-step sampling, the old waist measured): the only remaining
   discriminator.
2. **One-step division timing** for both arms, which turns a 1.1-sigma difference into a measured one or drops it.
3. **A third arm**: a single body seeded *elongated* along the same axis rather than circular, to test whether elongation
   alone reproduces the fused body's prompt division.
