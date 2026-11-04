# X167 — Does a merged body come apart? Exploratory analysis (04.11)

**Status: exploratory, not pre-registered.** This item was run as an analysis of existing logs before its
pre-registration was written, which is why its conclusions are labelled exploratory and why the confirmatory version is
queued as X167b. It is reported rather than hidden because the observation itself is worth having and because the confound
is instructive.

## What was measured

The X158 compacts (63 logs of two seeded bodies, 6 000 steps, ten-step sampling) are scanned for the first two-to-one
transition — the fusion — and the merged component is then followed to the end of the log. For each fusion the report
records whether the merged body divided again, the total area of the products relative to the parents' total, and how far
the products sit from the parents' old centres.

## Result

| quantity | value |
|---|---|
| logs scanned | 63 |
| fusions followed | 8 |
| re-divided within the log | 8 (share 1.0) |
| product area / parent area (median) | 0.867 |
| product centre offset from the nearest parent centre (median) | 1.25 cells |
| logged steps between the fusion and the end of the log (median) | 592 |

So a merged body does divide again, its products carry about 87 % of the parents' combined area, and they occupy the
parents' old positions to within about a cell and a quarter. At the level of the tracking rule the merge is **reversible**:
what fused can divide again, and the products sit where the pair was.

## The confound, stated plainly

A merged body is large and elongated along the line joining the parents, and the tracking rule splits large blobs. Products
near the parents' positions are therefore what one expects from **any** elongated blob being split along its short axis,
whether or not the merge preserved anything. This measurement cannot separate "the original pair came apart" from "a big
blob split into two halves at its ends", and the area ratio of 0.867 is compatible with both (bodies lose area as they grow
and divide).

That is not a small caveat: it means the exploratory result is compatible with the boring explanation, and the interesting
reading needs a control.

## The confirmatory design, queued as X167b

Two arms of ten seeds each: (a) a fused pair, followed after the merge; (b) a **single** body seeded with the same area as
the merged pair at the same step, followed for the same number of steps. If the re-division share and the product geometry
are the same in both arms, the merge carries nothing and the "identity" language must be dropped from the fusion work. If
the fused arm re-divides sooner, or along the old seam specifically, the merge preserves structure. The seam test needs the
field, not the components: the merged body's waist, measured from the field, is where a preserved seam would show up.

Registration: [`2026-11-04-x167b-reversibility-plan.md`](2026-11-04-x167b-reversibility-plan.md).

## Limits

Eight fusions is a small sample, and the 63 logs are those of one geometry family (gap 8 and 9 arms), so the fusion census
here is not the 201-run census of X158. The censoring matters: a fusion that happens near the end of a log cannot re-divide,
and the median of 592 remaining steps says most of these eight were early, which inflates the 8/8 share relative to a
random fusion. The item therefore reports "merges are reversible when there is time to see it" and not a rate.

## Next hypotheses

1. **X167b**, the two-arm control above — the only way to tell the readings apart.
2. **The waist from the field**: save the field for one re-dividing merged body and measure whether the division line
   coincides with the old seam. This is the direct test of "identity", and it is the reason the item exists.
3. **Censoring-aware census**: the whole X158 series (201 runs), with a Kaplan-Meier style estimate of the time from fusion
   to the next division, rather than a share among survivors.
