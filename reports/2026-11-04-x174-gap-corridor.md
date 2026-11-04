# X174 — The corridor at contact depends on the gap, and on how marginal the arm is (04.11)

**Question.** X171 made the corridor at contact a size-independent criterion and named its own confound: each arm sat at its own
crossing gap, so a size effect and a gap effect could not be separated. This item separates them at a fixed size — radius 3,
`F` = 0.030, surface gaps 8, 9 and 10 — and then asked what the three cells have in common.

Pre-registration: [`2026-11-04-x174-gap-corridor-plan.md`](2026-11-04-x174-gap-corridor-plan.md). Gaps 8 (ten seeds, 1031-1040)
and 9 (fifteen seeds, 1031-1045) measured here; gap 10 is X170's arm, same rate, same size, same readout.

## Result: 0.37, 0.41, 0.48 — the fraction is not constant

| gap | fusion share | contact events | corridor / peak, median | spread |
|---|---|---|---|---|
| 8 | 1.00 | 10 of 10 | **0.367** | 0.044 |
| 9 | 0.80 | 12 of 15 | **0.411** | 0.060 |
| 10 | 0.47 | 7 of 15 | **0.479** | 0.036 |

The difference between the extreme gaps is **0.11** against a pooled within-gap spread of **0.059**, so the pre-registered
refusal rule fires in its negative direction: **the criterion depends on the initial gap**. X171's confound was real, and its
"size-independent criterion" was a statement about three cells that happened to have similar shares, not about a constant of the
medium.

## And the variable behind both is the share

Put the eight arm-cells this block has measured on one plot — three gaps at one size, two sizes at two gaps, three rates at one
gap — and order them by their **fusion share**, the arm's probability of fusing at all:

| arm | share | corridor at contact | measured by |
|---|---|---|---|
| radius 3, gap 8, `F` = 0.030 | 1.00 | 0.367 | here |
| radius 3, gap 9, `F` = 0.030 | 0.80 | 0.411 | here |
| radius 3, gap 10, `F` = 0.036 | 0.67 | 0.392 | X170 |
| radius 3, gap 10, `F` = 0.030 | 0.47 | 0.479 | X170 |
| radius 6, gap 9, `F` = 0.030 | 0.47 | 0.470 | X171 |
| radius 3, gap 10, `F` = 0.026 | 0.27 | 0.516 | X170 |
| radius 4.5, gap 10, `F` = 0.030 | 0.27 | 0.492 | X171 |

The relation is monotone decreasing — Pearson **−0.95**, Spearman **−0.88** over the eight cells — and it explains both of the
earlier results at once: X171's three sizes agree because their shares agree (0.27-0.47 over three cells whose corridors span
0.47-0.49), and X170's rate ladder is the same relation read along a different axis.

**The sign of this relation is expected; its size is the finding.** The corridor is measured on the runs that fused, and the
share is the fraction of runs that fused: an arm close to its crossing fuses only in its luckiest runs, and those are the ones
where the bridge got further before the merge, so a negative slope is what selection predicts. What is not automatic is the
scale: across a share range from 1.0 to 0.27 the corridor moves by 0.15, i.e. **the bridge's state at the moment of merging is a
band from about 0.37 to 0.52 of the body peak**, and the position inside the band is set by how marginal the pair is rather than
by a property of the medium alone.

## What this does to the two earlier claims

X171's claim is **narrowed, not withdrawn**: at the same gap the corridor is flat in body size (radius 3 and 4.5 both read 0.48
and 0.49 at gap 10, and radius 6 reads 0.47 at gap 9 where radius 3 reads 0.41 — a 0.06 difference that is about one spread and
in the direction the share predicts, because radius 6 at gap 9 has share 0.47 against radius 3's 0.80). What X171 established is
therefore "no size effect larger than the gap effect", not "a constant fraction at every size".

X170's claim is **unchanged**: the crossing moves with the source, and now that movement has a common currency — the source
changes the share, and the share sets where in the band the merge happens.

## Limits

Every cell rests on 4 to 12 contact events, and the eight cells are not independent: three of them come from one aggregate, two
share a seeds family, and the relation is a selection effect by construction, so its *sign* was never in doubt and only its
slope is evidence. Eight cells cannot distinguish a line from a curve, and the highest-share cell (share 1.00) has no scatter to
speak of — an arm where every run fuses cannot tell us what selection would do at an even easier gap.

## What would kill it

A ninth cell chosen **before** the run, whose corridor lands far from the curve's prediction. The natural cell is an interior
point of the (gap, size) plane that exists in neither family: radius 4.5 at gap 9, predicted by interpolation to have a share of
about 0.6 and a corridor of 0.42-0.46 (X175). If it lands there the relation is a curve with a shape; if it lands
systematically outside, the eight-cell ordering was an artefact of mixing families.

## Next hypotheses

1. **Test the curve at an interior point** — radius 4.5 at gap 9, one arm, prediction registered before the run (X175).
2. **Separate selection from mechanism.** In the selection reading the slope comes from *which* runs fuse; a run that barely
   fuses should be one whose bridge grew unusually far, and that is checkable: among the runs of one marginal arm, the corridor at
   contact should correlate with how late in the run the merge happened, and with the pair's initial luck (jitter).
3. **The band as the physically meaningful object.** Instead of a threshold, the claim may be that a merge requires the bridge to
   be within 0.37-0.52 of the peak, and below that range the pair fuses early because nothing stops it. That is a weaker claim
   than X171's, and it may be the true one.
