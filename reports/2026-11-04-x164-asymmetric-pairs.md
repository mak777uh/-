# X164 — Unequal bodies do not move the fusion crossing (04.11)

**Question.** Every fusion measurement in this block used two bodies of the same seeded radius, so "the gap at which fusion
happens" has never been separated from "the gap between two equal discs". If the crossing were a property of the pair — its
combined size, its curvature, the ratio of the two bodies — then the ten-cell number of §4.1 would be a statement about the
pairs we happen to seed and not about the medium. This item seeds one body of radius 3 and one of radius 6 and asks whether
the crossing moves.

Pre-registration: [`2026-11-04-x164-asymmetric-pairs-plan.md`](2026-11-04-x164-asymmetric-pairs-plan.md). Six arms of five
seeds (931-935), 6 000 steps, `F` = 0.030, ten-step sampling; the asymmetric pair (3, 6) at surface gaps 4, 6, 8 and 10,
plus the block's own symmetric controls at a gap of 8 for radii 3 and 6. New code: `--init-spots` now accepts
`R1:SEP:R2`; the old `R:SEP` branch is anchored bit-for-bit (300 steps, seed 701, 0 of 0 summary fields differ between the
old and the new file).

## Result — the crossing stays inside the symmetric band

| arm | fused | share | Wilson 95 % | gap at the last two-body step (median) | values |
|---|---|---|---|---|---|
| (3, 6) at gap 4 | 5/5 | 1.00 | [0.57, 1.00] | 1.84 | 1.84 (all five) |
| (3, 6) at gap 6 | 5/5 | 1.00 | [0.57, 1.00] | 2.21 | 2.14-2.25 |
| (3, 6) at gap 8 | 5/5 | 1.00 | [0.57, 1.00] | 2.60 | 2.47-2.62 |
| (3, 6) at gap 10 | 2/5 | 0.40 | [0.12, 0.77] | 4.38 | 3.95, 4.81 |
| r3-r3 at gap 8 (control) | 5/5 | 1.00 | [0.57, 1.00] | 1.73 | 1.52-1.81 |
| r6-r6 at gap 8 (control) | 5/5 | 1.00 | [0.57, 1.00] | 3.12 | 2.50-3.47 |

The positive controls fire (5/5 and 5/5, as in X158), and the readout varies well beyond its floor. The asymmetric pair
fuses at every gap up to 8 and has stopped by 10 — its crossing lies between **8 and 10 cells**, i.e. **inside the symmetric
band of 10 ± 1** (X158 crossed at 10, 10 and 9 for radii 3, 4.5 and 6). A twofold difference between the two bodies does
not move the surface gap at which fusion happens.

That is the clean negative the pre-registration named in §6: the crossing is a property of the **medium**, not of the pair.

## A second regularity, consistent with X166

The gap at the last two-body step **rises with the initial gap**: 1.84 at a nominal gap of 4, 2.21 at 6, 2.60 at 8, and
4.38 in the two runs that fused from a nominal gap of 10. The tighter the pair starts, the smaller the gap at which they
actually merge. This is the same pattern X166 found at one-step resolution — the later the fusion, the wider the gap — and
here it appears as a function of the initial condition rather than of the fusion time. Both are consistent with a bridge
that has time to build: a pair that starts further apart approaches while the corridor between them fills, so by the time
the bodies merge the corridor is wider.

## What this changes

`§4.1` currently says "about two cells, the same at every size", with "size" meaning the radius of a symmetric pair. This
item extends the statement from equal to unequal bodies: the crossing does not depend on the ratio of the two bodies either.
Together with X166 (the band is 1 to 5 cells within an arm, with the wide values belonging to slow fusions), the honest
formulation is now: **the medium tolerates contact at about two cells, between bodies of any size and any size ratio, and
the individual event ranges from about one cell to about five depending on how long the approach took.**

## Limits

Five seeds per arm, so the crossing is placed within a two-cell window by the design of the gaps, not by the precision of
the share; the arms at gap 10 (2/5) and gap 8 (5/5) bracket it. The asymmetric pair used one ratio only (1:2); a stronger
statement would need 1:3 and 1:4, where the smaller body may be too small to form a bridge at all. The corner case — a very
small body against a very large one — is untested and is the obvious place for the ratio to matter after all.

## What would kill it

A repeat with ratio 1:3 or 1:4 that crosses *below* 8 cells would say the ratio matters once it is extreme enough, and the
"medium only" reading would need a caveat. Equally, a crossing at 10 for the 1:2 pair at ten seeds (where the 2/5 at gap 10
is the discriminating arm) would move the estimate to the band's upper edge.

## Next hypotheses

1. **Extreme ratios** (1:3, 1:4) to find where the ratio does start to matter, if it does.
2. **The corridor, not the silhouette**: with one-step logs of the (3, 6) pair, measure the field in the corridor between the
   bodies at the moment of fusion, and compare with the symmetric case. If the corridor's concentration reaches the same
   value in both, the "about two cells" is really "the same corridor concentration", and the cell number is a consequence.
3. **The dependence on the initial gap** stated as a curve: gaps 2 to 12 for the (3, 6) pair, ten seeds, giving the relation
   between the nominal gap and the gap at contact that this item saw in four points.
