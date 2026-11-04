# X167b — Does a merge preserve anything? Two-arm control (pre-registration, 04.11)

## 1. Manipulation is connected

X167 found that all eight fusions it could follow re-divided, with products at 0.867 of the parents' area and 1.25 cells
from the parents' old centres — but an elongated blob split at its ends produces exactly that geometry whether or not the
merge preserved anything. This item supplies the missing comparison.

Two arms of ten seeds. Arm (a), **fused**: two bodies of radius 3 at a surface gap of 8 (the block's positive control, which
fuses 5/5), followed for 2 000 steps after the merge. Arm (b), **single**: one body seeded at the step of the merge with the
merged body's area, followed for the same 2 000 steps from the same point in the world's development. The only difference
between the arms is whether the body at that moment is a merged pair or a single blob of the same area at the same place.

Implementation: arm (a) needs a merge detector that stops the run at the fusion and restarts it with an equivalent single
body — or, simpler and bit-identical in behaviour, one run per arm with `--init-spots` and a post-hoc pairing by area, which
the analysis does by matching each fused run to a single-body run whose initial area is within 5 %. Matching is done before
any outcome is read, and the pairs are recorded.

## 2. Positive control fires

Arm (a) must fuse in at least 4 of 5 of its runs (X158 gives 5/5 at gap 8), and arm (b) must actually reach a division in at
least 4 of 5 runs — a single body that never divides cannot be compared. If either fails, the item reports the design
failure and stops.

## 3. Readout exists and varies

The primary readout is **steps from the referent moment to the next division**, in logged steps; it must vary (standard
deviation ≥ 20 steps) and its median must be within the run length. The secondary readout is the geometry of the products:
their combined area relative to the referent body's area, and the angle of the division line relative to the old seam (the
line joining the two parents' centres). The angle is the discarding test: a preserved seam means the division line is close
to the old seam's perpendicular, a generic split means uniform angles.

## 4. Sensitivity arithmetic

In X167 the gap between the parents' centres was about 2.5 cells and the products sat 1.25 cells from the parents' centres,
i.e. at the two ends of the merged body — exactly the generic geometry. So the two readings differ not in *where* the
products are but in **when** the body divides and **along which line**. With ten seeds per arm and a between-run spread of
perhaps 100 steps, a difference of 150 steps is detectable; the seam angle needs the field, so it is measured on four runs
only, and reported as a qualitative check rather than a distribution.

## 5. Refusal rule

If the re-division times of the two arms overlap entirely and the seam angles are uniform, the item is recorded as **the
merge carries nothing** — the merged body is a blob, and the fusion work must stop using the word identity. If the fused arm
divides sooner or its division line clusters near the old seam, the merge preserves structure and that becomes a result of
its own. If the observables do not vary (§3), nothing is reported.

## 6. What would kill it

A fused arm that divides at the same time and along the same distribution of lines as a single body of the same area — that
is the negative, and it is the more likely one. A confound to guard: the merged body's area is the parents' sum, so the
matching in §1 must match areas within 5 %, not merely "both large".

## 7. Implementation notes

Runner `scripts/x167b_series.py` (two arms, ten seeds, 2 000 steps after the referent, `--sample-every 4` for the angle and
the time, field dumps for four runs only). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x167b_reversibility.json`. Cost about two hours.
