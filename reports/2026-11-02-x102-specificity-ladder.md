# X102 — the specificity is definition-bound too, but the *containment* is not

**Plan:** [`2026-11-02-x102-specificity-plan.md`](2026-11-02-x102-specificity-plan.md) (registered 20:20 MSK, before the
analysis). **Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x102_specificity_ladder.json`.
Analysis of X100's stored snapshots; no GPU, no new runs.

## What was asked

X91 measured not the *level* of size heredity but its **specificity**: a daughter follows her own parent far more than
the nearest non-ancestor (gap 0.26–0.41). X101 then showed the level is definition-bound — 0.531 / 0.384 for the
excursion set at `v > 0.20`, 0.300 / 0.174 for a drainage basin, 0.176 / 0.058 for the core at half the local maximum.

X102 asks the question that decides how to describe this medium: **does the gap survive the weaker definition?** If it
does, "a daughter resembles her mother more than her neighbours" is a statement about the medium. If it collapses too,
even the specificity belongs to the excursion-set definition.

## Numbers

Same daughters under both definitions, ten worlds per inflow:

| inflow | definition | ρ(parent, daughter) | ρ(stranger, daughter) | **gap** |
|---|---|---|---|---|
| 0.030 | excursion set, `v > 0.20` | 0.531 | 0.219 | **0.312** |
| 0.030 | basin by steepest ascent | 0.308 | 0.291 | **0.017** |
| 0.040 | excursion set, `v > 0.20` | 0.384 | 0.169 | **0.215** |
| 0.040 | basin by steepest ascent | 0.153 | 0.163 | **−0.010** |

Basin pairs: 1 882 at 0.030 and 956 at 0.040; basin coverage 0.93 and 0.839; 2 024 and 1 139 ancestor-daughter pairs.
The positive control fired at both inflows (X91's gap reproduced: +0.312, +0.215), so the pairing and the stranger
lookup are X91's.

**Registered rule fired:** the gap falls by 0.295 and 0.225, both past the declared 0.15 resolution —
*"specificity is definition-bound too"*. At `F = 0.040` the basin gap is not merely small, it is zero to two decimals.

## The degeneracy question, and why the answer is not an artefact

A collapse like this has an obvious mechanical explanation: if the nearest non-ancestor almost always sat inside the
daughter's own drainage basin, the basin area could not separate them by construction, and the null would be a property
of the geometry rather than of heredity. So the analysis was extended with a containment count, in the frame where each
candidate peaks:

| inflow | parent shares the daughter's basin | stranger shares the daughter's basin | ratio |
|---|---|---|---|
| 0.030 | 0.398 | 0.132 | 3.0× |
| 0.040 | 0.187 | 0.081 | 2.3× |

The basin readout **had room**: ancestry is visible in the topography — a mother's peak site is inside the daughter's
drainage basin two to three times as often as a stranger's — and yet the *area* of that basin carries no heredity at
either inflow. The collapse is therefore not a degeneracy of the control. The basin's extent is simply the wrong
quantity; the basin's *identity* is not.

**A first attempt got these two numbers wrong and must be recorded:** labels from `basins()` are assigned per frame, so
comparing a parent's label in the snapshot where the parent peaks with the daughter's label in the snapshot where the
daughter peaks is meaningless. That version reported 0.07 / 0.13 and would have supported the opposite reading (the
parent no more often inside than the stranger). Corrected to same-frame containment: 0.398 / 0.132 and 0.187 / 0.081.
Neither number was published before the correction; the rule earned is part of `docs/design-checks.md` below.

## Reading

The ladder from X101 and the gap from X102 are the same statement seen twice:

| what is inherited | level | specificity (gap) |
|---|---|---|
| how far the excursion spreads (fixed cut 0.20) | 0.531 / 0.384 | **0.312 / 0.215** |
| the drainage region's area | 0.300 / 0.174 | **0.017 / −0.010** |
| the core at half the local maximum | 0.176 / 0.058 | not measured |

Level and specificity fall together, and they fall to nothing at the last step that stops being an excursion set. What
the medium passes from mother to daughter is therefore **an extensive property of a fixed-density region** — how much of
the field is drawn above a fixed level around her — and not the topography that region sits in. A mother leaves her
daughter a *skirt of a certain width*, not a *valley of a certain size*.

This is a strong statement about the medium and it is falsifiable in one obvious way: if heredity were a property of the
topography, a position-within-the-basin design (does a daughter's fate depend on where in the mother's basin she starts,
centre versus rim?) should beat the area. That is registered as the next analysis, not run here.

## Caveats

- Ten worlds per inflow (X100's runs). `F = 0.040` basin coverage is 0.839, close to the preregistered floor of 0.80;
  the 0.040 basin numbers are the weaker half of the result.
- The stranger is the nearest non-ancestor by centroid at the daughter's first appearance (X73's rule), not a
  size-matched control. X92/X93 showed that area–lifetime is not null across strangers, which is exactly why the
  reported quantity is a **difference** of two correlations on the same daughters, not an absolute fraction.
- Both definitions measure the same snapshots, so the comparison is paired and world-to-world variation cancels; the
  remaining dependence is that both readouts use the same twenty worlds as X101.
- The basin area still depends on the saved frames (one per logged step); a daughter whose peak falls between frames is
  measured at a neighbour.

## Design rules earned (added to `docs/design-checks.md`)

1. **Label-valued quantities are per frame.** A topological label (basin id, component id) may only be compared with
   another label computed from the same frame. Anything else silently compares numbering schemes.
2. **A collapse needs a degeneracy check before interpretation.** State how often the control falls in the same
   structure as the subject; if it nearly always does, the readout is void by construction, not by result.

## Next hypotheses

- **X103 (analysis, registered):** position within the mother's basin. If the daughter's fate depends on where in the
  basin she sits rather than on the basin's area, heredity is topographic after all and this reading is refuted.
- **X104 (needs runs):** the gap at a *second* cut (0.15 or 0.25). If the gap is an excursion-set quantity, it should
  move with the cut the way the level does (X99) — the same factor-of-three sensitivity, in the specificity.
- **Held:** X94 (memory minimum), X95 (trickle above 0.050), X97 (sibling second generation) — each only if
  load-bearing; X96 waits on the owner (a second diffusive species is a new world rule).

доска: принято 0, отклонено 0, отложено 0.
